import copy
from src.logging import *
from src.solver.flow_generator import *
from z3 import *


class trace2flows:
    def __init__(self, cg_vec):
        self.graph = cg_vec.pop(0)
        self.dags = cg_vec
        self.solver = Solver()
        self.edge_z3var_list = []
        self.edge_variables_3D_dict = {}
        self.node_variables_2D_dict = {}
        self.root_variables_2D_dict = {}
        self.solutions = []
        self.is_monolithic = None
        self.max_sol = self.graph.get_max_solutions()

        #@ start generating flow specificatons.
        model_table = self.find_reduced_model()
        print('return model table size is ', len(model_table))
        exit()
        # self.generate_monolithic_solutions()
    #@ ---------------------------------------

    def reset(self):
        self.solver = Solver()
        self.edge_z3var_list = []
        self.edge_variables_3D_dict = {}
        self.node_variables_2D_dict = {}
        self.root_variables_2D_dict = {}
        self.solutions = []

    def generate_split_solutions(self):
        dagID = 'a'
        self.is_monolithic = False
        for dag in self.dags:
            self.create_vars_and_edge_constraints(dag, dagID)
            dagID = chr(ord(dagID) + 1)

        self.create_unified_constraints()
        self.solve()


    def generate_monolithic_solutions(self):
        ranking = 100
        while True:
            log('@%s:%d: using ranking threshold = %d\n' % (whoami(), line_numb(), ranking), INFO)
           
            self.reset()

            print(self.solver)
            # self.create_vars_and_edge_constraints(self.graph, graphID)
            self.create_constraints(ranking)

            # solve and generate solutions.
            model_count = self.solve()
            if model_count > 0:
                log('@%s:%d: models of consistent binary sequences found = %d\n' % (whoami(), line_numb(), model_count), INFO)
                break
            ranking -= 10


    def create_vars_and_edge_constraints(self, graph, graphID):
        nodes = graph.get_nodes()
        edge_vars = {}
        node_vars = {}
        root_vars = {}

        log('node --> edge constraints ======== \n', DEBUG)
        self.create_vars_and_outgoing_edge_constraints(graph, graphID, nodes, edge_vars, node_vars, root_vars)
        log('edge --> node constraints ======== \n', DEBUG)
        self.create_incoming_edge_constraints(graphID, nodes, edge_vars, node_vars)

        self.edge_variables_3D_dict[graphID] = edge_vars
        self.node_variables_2D_dict[graphID] = node_vars
        self.root_variables_2D_dict[graphID] = root_vars

    
    # Possibly need to make this function for monolithic, this is the dag version
    def create_constraints(self, ranking_threshold=100):
        nodes = self.graph.get_nodes()
        edges = self.graph.get_edges().values()

        for node in nodes.values():
            node_z3var = node.get_z3var()
            node_support = node.get_support()
            if node_support == 0: continue
            self.solver.add(node_z3var == node_support)
            log(str(node_z3var) + ' == ' + str(node_support) + '\n', DEBUG)
            
            #@ adding constraints on node and its outgoing edges
            #@--------------------------------------------------
            #@ constraints on outgoing edges of a node may cause the CSP to be UNSAT if 
            #@ the node is the source of simultaneous multiple destnations, eg, a cache-write message  
            #@ can trigger memory-write and cache-invalidate at the same time. 
            #@ -------------------------------------------------- 
            outgoing_edges = node.get_outgoing_edges() if not self.graph.is_terminal(node) else []
            node_edge_vars = []
            for edge in outgoing_edges:
                edge_support = edge.get_support()
                edge_ranking = edge.get_ranking()
                edge_z3var = edge.get_z3var()
                #@ only consider edges with ranking higher than the threshold
                if edge_ranking >= ranking_threshold:
                    node_edge_vars.append(edge_z3var)
                # log(str(0)+' <= '+str(edge_int_var)+ ' <= ' + str(edge_support), DEBUG)

            #@------------------------  
            sum_z3vars = None
            s = ''
            for edge_var in node_edge_vars:
                if sum_z3vars is None:
                    sum_z3vars = edge_var
                    s = str(edge_var) 
                else:
                    sum_z3vars += edge_var
                    s = s + ' + ' + str(edge_var) 
            # if sum_z3vars != None:
            #     self.solver.add(node_z3var == sum_z3vars)
            #     log(str(node_z3var) + " == " + str(s) + '\n', DEBUG)
            #@----------------------------

            # adding constraints on node and its incoming edges
            incoming_edges = node.get_incoming_edges() if not self.graph.is_root(node) else []
            node_edge_vars = []
            for edge in incoming_edges:
                edge_support = edge.get_support()
                edge_z3var = edge.get_z3var()
                # self.solver.add(edge_int_var <= edge_support, edge_int_var >= 0)
                node_edge_vars.append(edge_z3var)
                # log(str(0)+' <= '+str(edge_int_var)+ ' <= ' + str(edge_support), DEBUG)
                
            sum_z3vars = None
            s = ''
            for edge_var in node_edge_vars:
                if sum_z3vars is None:
                    sum_z3vars = edge_var
                    s = str(edge_var) 
                else:
                    sum_z3vars += edge_var
                    s = s + ' + ' + str(edge_var) 

            if sum_z3vars != None:
                self.solver.add(node_z3var == sum_z3vars)
                log(str(node_z3var) + " == " + str(s) + '\n', DEBUG)

        # adding constraints on edge support
        for edge in edges:
            edge_z3var = edge.get_z3var()
            self.edge_z3var_list.append(edge_z3var)
            edge_support = edge.get_support()
            self.solver.add(edge_z3var <= edge_support, edge_z3var >= 0)
            log(str(0)+' <= '+str(edge_z3var)+ ' <= ' + str(edge_support) + '\n', DEBUG)
            # if edge.get_id() == '0_26':
            #     self.solver.add(edge_z3var == 0)
            # if  edge.get_id() == '0_25':
            #     self.solver.add(edge_z3var > 0)
    #------------------------------------------------------------------


    # Possibly need to make this function for monolithic, this is the dag version
    def create_vars_and_outgoing_edge_constraints(self, graph, graphID, nodes, edge_vars, node_vars, root_vars):
        for origin in nodes.values():
            nodeID = graphID + str(origin)
            node_int_var = Int(nodeID)

            if graph.is_root(origin) or self.is_monolithic:
                self.solver.add(node_int_var == origin.get_support())
                log(str(node_int_var) + " == " + str(origin.get_support())+'\n', DEBUG)
            else:
                self.solver.add(node_int_var <= origin.get_support(), node_int_var >= 0)
                log("0 <= " + str(node_int_var) + " <= " + str(origin.get_support)+'\n', DEBUG)

            node_vars[nodeID] = node_int_var
            if graph.is_root(origin):
                root_vars[nodeID] = node_int_var
            
            edges = origin.get_edges().values()
            if edges:
                node_edge_vars = {}
                for edge in edges:
                    edge_support = edge.get_edge_support()
                    edgeID = graphID + str(edge)
                    edge_int_var = Int(edgeID)
                    self.solver.add(edge_int_var <= edge_support, edge_int_var >= 0)
                    node_edge_vars[edgeID] = edge_int_var
                    log(str(0)+' <= '+str(edge_int_var)+ ' <= ' + str(edge_support), DEBUG)
                
                sum_int_vars = None
                s = ''
                for edge_var in node_edge_vars.values():
                    if sum_int_vars is None:
                        sum_int_vars = edge_var
                        s = str(edge_var) 
                    else:
                        sum_int_vars += edge_var
                        s = s + ' + ' + str(edge_var) 

                edge_vars[nodeID] = node_edge_vars
                # self.solver.add(node_vars[nodeID] == sum_int_vars)
                # print(node_vars[nodeID], " == ", s) if self.DEBUG else None

                # Manual test of using terminal messages to resolve UNSAT situation                
                # if nodeID=="x25" or nodeID=="x26" or nodeID=="x29" or nodeID=="x32" or nodeID=="x35" or nodeID=="x36" or nodeID=="x37" or nodeID=="x40" or nodeID=="x41" or nodeID=="x43":
                if self.graph.is_terminal(origin):
                    log('skip terminal nodes ' + str(nodeID)+'\n', DEBUG)
                else:
                    self.solver.add(node_vars[nodeID] == sum_int_vars)
                    log(str(node_vars[nodeID]) + " == " + str(s), DEBUG)
        
    

    def create_incoming_edge_constraints(self, graphID, nodes, edge_vars, node_vars):
        for destination in nodes.values():
            sum_int_vars = None
            destinationID = graphID + str(destination)
            s=''
            
            for origin in nodes.values():

                if origin == destination:
                    continue

                edgeID = str(origin) + '_' + str(destination)
                edges = origin.get_edges()

                if not edges.keys().__contains__(edgeID):
                    continue

                originID = graphID + str(origin)

                edge_var = edge_vars[originID][graphID + edgeID]
                if sum_int_vars is None:
                    sum_int_vars = edge_var
                    s = str(edge_var) #if self.DEBUG else None
                else:
                    sum_int_vars += edge_var   #edge_vars[originID][graphID + edgeID]
                    s = s + ' + ' + str(edge_var) #if self.DEBUG else None


            if sum_int_vars is not None:
                self.solver.add(node_vars[destinationID] == sum_int_vars)
                log(str(node_vars[destinationID]) + " == " + str(s), DEBUG) 

            # if self.solver.check() == unsat:
            #     print("*** UNSAT ***")
            #     exit()

    def create_unified_constraints(self):
        log(" unified node constraints ========", DEBUG) 
        self.create_unified_node_constraints()
        log(" unified edge constraints ========", DEBUG)
        self.create_unified_edge_constraints()

    def create_unified_node_constraints(self):

        for node in self.graph.get_nodes().values():

            if self.graph.is_root(node):
                continue

            sum_int_vars = None

            for dag_key in self.node_variables_2D_dict:
                nodeID = dag_key + str(node)

                if sum_int_vars is None:
                    sum_int_vars = self.node_variables_2D_dict[dag_key][nodeID]
                else:
                    sum_int_vars += self.node_variables_2D_dict[dag_key][nodeID]

            if sum_int_vars is not None:
                self.solver.add(sum_int_vars == node.get_support())
                log(str(sum_int_vars) + " == " + str(node.get_support()), DEBUG) 

    def create_unified_edge_constraints(self):
        for edge in self.graph.get_edges().values():

            sum_int_vars = None

            # if self.graph.is_root(edge.get_origin()):
            #     continue

            for dag_key in self.edge_variables_3D_dict:
                nodeID = dag_key + str(edge.get_origin())

                if not self.edge_variables_3D_dict[dag_key].keys().__contains__(nodeID):
                    continue

                edgeID = dag_key + str(edge)

                if not self.edge_variables_3D_dict[dag_key][nodeID].keys().__contains__(edgeID):
                    continue

                if sum_int_vars is None:
                    sum_int_vars = self.edge_variables_3D_dict[dag_key][nodeID][edgeID]
                else:
                    sum_int_vars += self.edge_variables_3D_dict[dag_key][nodeID][edgeID]

            if sum_int_vars is not None and str(sum_int_vars).__contains__('+'):
                self.solver.add(sum_int_vars <= edge.get_edge_support(), 0 <= sum_int_vars)
                log(str(sum_int_vars) + " <= " + edge.get_edge_support() + " 0 <= " + str(sum_int_vars), DEBUG) 


    def solve(self):
        sol_count = 0
        if self.solver.check() == unsat:
            print('The constraints encoded are not satisfiable.')
            # for x in self.solver.assertions():
            #    print(repr(x))
            return sol_count

        edge_vars = {}

        for dag_key in self.edge_variables_3D_dict:
            for node_key in self.edge_variables_3D_dict[dag_key]:
                for edge_var_key in self.edge_variables_3D_dict[dag_key][node_key]:
                    edge_vars[edge_var_key] = self.edge_variables_3D_dict[dag_key][node_key][edge_var_key]

        solution_edge_vars = copy.copy(edge_vars)

        # old_m = self.solver.model()
        # self.solutions.append(old_m)
        #
        # self.solver.add(Or(
        #     [old_m[edge_var] != edge_var for edge_var in edge_vars.values()]))

        while self.solver.check() == sat:
            # sol_count += 1
            # if sol_count > self.max_sol:
            #     break
            model = self.solver.model()
            self.add_solution(model)
            log('@%s:%d: print a model of consistent binary sequences\n' % (whoami(), line_numb()), INFO)
            # log2file('bin-seq-model.txt', self.z3model2str(model), INFO)
            log(self.z3model2str(model), INFO)
            log('@trace2flows:363: call flow-generator to extract flow specifications\n', INFO)
            flow_gen = flow_generator(self.graph, model)

            #@ -----------------------------
            #@ flow_spec directed solving
            #@ if extracting flow specs fails, repeat solving after adding constraints excluding
            #@ certain edges
            log('@trace2flows:371: adding node-cover/noncycle constraints returned from flow-generator', DEBUG)
            node_cover_constraint_list = flow_gen.get_node_cover_constraints()
            for c in node_cover_constraint_list:
                print(c)
                self.solver.add(c)

            noncycle_constraint_list = flow_gen.get_noncycle_constraints()
            for c in noncycle_constraint_list:
                # print(c)
                self.solver.add(c)
            #@---------------------


            #@ if previous solution leads to flow specs, repeat solving by enforcing some 
            #@ zero-edges to be non-zero
            # flow_spec = flow_gen.get_flow_spec()
            # print(flow_spec)
            edges = self.graph.get_edges().values()
            new_constr = False
            for edge in edges:
                edge_z3var = edge.get_z3var()
                new_constr = Or(new_constr, And(model[edge_z3var] > 0, edge_z3var == 0))
            # new_constr = constr if new_constr is None else Or(new_constr, constr)
            new_constr = simplify(new_constr)
            self.solver.add(new_constr) 
            log('@%s:%d: next iteration\n' % (whoami(), line_numb()), INFO, True)
            #@-------------------------------------
    
        print(sol_count)
        return sol_count

            #self.solutions.append(m)
            # self.add_solution(m)
            #print(m) if self.DEBUG==True else None

            # self.solver.add(Or(
            #     [And(old_m[edge_var] == m[edge_var], edge_var > 0) for edge_var in edge_vars.values()]))

            # for edge_var in solution_edge_vars.values():
            #     if old_m[edge_var] is not m[edge_var]:
            #         print(edge_var, old_m[edge_var], m[edge_var])
            #         edge_vars.pop(str(edge_var), None)

            # for edge_var in solution_edge_vars.values():
            #     if old_m[edge_var] is m[edge_var]:
            #         print(edge_var, old_m[edge_var], m[edge_var])
            #         edge_vars.pop(str(edge_var), None)

            #
            # if not edge_vars:
            #     break

            # self.solver.add(
            #     Or(And([If(old_m[edge_var] == m[edge_var], edge_var != old_m[edge_var], edge_var == 0) for edge_var in
            #             edge_vars.values()])))

            # self.solver.add(
            #     Or([And(m[edge_var] > 0, edge_var == 0) for edge_var in edge_vars.values()]))

            # self.solver.add(
            #     And([If(m[edge_var] == 0, edge_var > 0, edge_var != m[edge_var]) for edge_var in edge_vars.values()]))

            # #@ creating new constraints by setting some non-zero edge to 0
            # edges = self.graph.get_edges().values()
            # new_constr = False
            # for edge in edges:
            #     edge_z3var = edge.get_z3var()
            #     new_constr = Or(new_constr, And(m[edge_z3var] > 0, edge_z3var == 0))
            # constr = simplify(new_constr)
            # self.solver.add(constr)

            # #@ creating new constraints by setting some zero edge to be non-0
            # edges = self.graph.get_edges().values()
            # new_constr = False
            # for edge in edges:
            #     edge_z3var = edge.get_z3var()
            #     new_constr = Or(new_constr, And(m[edge_z3var] == 0, edge_z3var > 0))
            # constr = simplify(new_constr)
            # self.solver.add(constr)
                
            # for dag_key in self.edge_variables_3D_dict:
            #     filtered_edge_vars = list(filter(lambda x: str(x)[0] == dag_key, edge_vars.values()))
            #     self.solver.add(
            #         Or([And(edge_var != m[edge_var]) for edge_var in filtered_edge_vars]))

            # for dag_key in self.edge_variables_3D_dict:
            #     filtered_edge_vars = list(filter(lambda x: str(x)[0] == dag_key, edge_vars.values()))
            #     self.solver.add(
            #         Or([And(edge_var != m[edge_var], m[edge_var] == 0) if m[edge_var] is not 0
            #         else And(edge_var != m[edge_var], m[edge_var] == 0) for edge_var in filtered_edge_vars]))

            # for dag_key in self.edge_variables_3D_dict:
            #     filtered_edge_vars = list(filter(lambda x: str(x)[0] == dag_key, edge_vars.values()))
            #     self.solver.add(Or([And(old_m[edge_var] == m[edge_var], edge_var != m[edge_var])
            #                         for edge_var in filtered_edge_vars]))

        # for i, solution in enumerate(self.solutions):
        #     print()
        #     print('Solution ' + str(i + 1))
        #     print()
        #     char_id = 'a'
        #     for edge_var in solution_edge_vars.values():
        #         if char_id != str(edge_var)[0]:
        #             char_id = str(edge_var)[0]
        #             print()
        #          str(solution[edge_var]) != '0':
        #             print(str(edge_var) + ' with edge support of ' + str(solution[edge_var]))
        # END


    def find_reduced_model(self):
        #@ add CG constraints into the solver
        self.create_constraints(0)

        model_table = {}
        edges = self.graph.get_edges().values()
        edge_z3var_list = []
        for edge in edges:
            edge_z3var_list.append(edge.get_z3var())

        reduced_model_size = 1000000
        while self.solver.check() == sat:
            if len(model_table) > 200:
                break
            model = self.solver.model()
            if self.z3model_signature(model) not in model_table:
                model_table[self.z3model_signature(model)] = model
                new_model_size = self.model_size(model, edge_z3var_list);
                if new_model_size < reduced_model_size:
                    reduced_model_size = new_model_size
                print(len(model_table), ' ', self.z3model_signature(model), ' ', self.model_size(model, edge_z3var_list))
                log('@%s:%d: print a model of consistent binary sequences\n' % (whoami(), line_numb()), INFO)
                log(self.z3model2str(model), INFO)

            #@--- start a new scope and recrusively find a reduce model
            self.solver.push()
            new_constr = False
            for edge_z3var in edge_z3var_list:
                if model[edge_z3var]==0:
                    self.solver.add(edge_z3var==0)
            self.reduce_model_recursive(model, edge_z3var_list, model_table, 0)
            self.solver.pop()
            #@--- end of the scope

            new_constr = False
            for edge_z3var in edge_z3var_list:
                new_constr = Or(new_constr, And(model[edge_z3var] > 0, edge_z3var == 0))
            # new_constr = constr if new_constr is None else Or(new_constr, constr)
            new_constr = simplify(new_constr)
            self.solver.add(new_constr) 
            log('@%s:%d: next iteration\n' % (whoami(), line_numb()), INFO, False)
            #@-------------------------------------
        
        print('Size of smallest model: ', reduced_model_size)
        return model_table


    def reduce_model_recursive(self, model, edge_z3var_list, model_table, level):
        if len(model_table) > 1000:
            return
        redm = model
        for edge_z3var in edge_z3var_list:
            if model[edge_z3var].as_long() > 0:
                self.solver.push()
                self.solver.add(edge_z3var==0)
                if self.solver.check() == sat:
                    redm = self.solver.model()
                    if self.z3model_signature(redm) not in model_table:
                        # print(self.z3model_signature(redm), ' ', self.model_size(redm, edge_z3var_list))
                        model_table[self.z3model_signature(redm)] = redm
                        redm = self.reduce_model_recursive(redm, edge_z3var_list, model_table, level+1)
                self.solver.pop()
        return

    
    def add_solution(self, solution):
        red = True
        for old_m in self.solutions:
            for var in solution:
                if (solution[var].as_long() == 0 and old_m[var].as_long() >0) or (solution[var].as_long() > 0 and old_m[var].as_long()==0):
                    red = False
                    break
            if red == False:
                break

        if not len(self.solutions) or red == False:
            self.solutions.append(solution)
        else:
            print('Found a redundant solution...')
            #exit()

    def get_new_model(self):
                edges = self.graph.get_edges().values()
                new_constr = None
                for edge in edges:
                    edge_z3var = edge.get_z3var()
                    constr = And(m[edge_z3var] == 0, edge_z3var > 0)
                    new_constr = constr if new_constr is None else Or(new_constr, constr)
                new_constr = simplify(new_constr)
                self.solver.add(new_constr) 

    def get_solutions(self):
        return self.solutions

    def print_z3model(self, m):
        for node in self.graph.get_nodes().values():
            node_z3var = node.get_
            z3var()
            if m[node_z3var].as_long() != 0:
                print(node_z3var, '=', m[node_z3var], ' ', end=' ')
        print()

        for edge_z3var in self.edge_z3var_list:
            if m[edge_z3var].as_long() != 0:
                print(edge_z3var, '=', m[edge_z3var], ' ', end=' ')
        print()

    def z3model2str(self, m):
        s = '#Node supports -->\n'
        for node in self.graph.get_nodes().values():
            node_z3var = node.get_z3var()
            if m[node_z3var] is None: continue
            if m[node_z3var].as_long() != 0:
                s += str(node_z3var) + ' ' + str(m[node_z3var]) + '\n'
        s += '\n\n'
        s += '#Edge supports -->\n'

        for edge_z3var in self.edge_z3var_list:
            if m[edge_z3var] is None: continue
            if m[edge_z3var].as_long() != 0:
                vars = str(edge_z3var).split('_')
                s += vars[0] + ' ' + vars[1] + ' ' + str(m[edge_z3var]) + '\n'
        s += '\n'
        return s

    
    def z3model_signature(self, m):
        s = ''
        for edge_z3var in self.edge_z3var_list:
            if m[edge_z3var].as_long() != 0:
                s += str(edge_z3var) + ' '
        return s


    def model_size(self, model, edge_z3var_list):
        cnt = 0
        for edge_z3var in edge_z3var_list:
            if model[edge_z3var].as_long() > 0:   cnt += 1
        return cnt
