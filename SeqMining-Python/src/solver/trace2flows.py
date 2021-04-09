import copy

from z3 import *
from src.logging import *
from src.solver.flow_generator import *
import pulp as pl
from src.visualization.state_diagram.draw_graph import Planter


class trace2flows:
    def __init__(self, cg_vec):
        self.graph = cg_vec.pop(0)
        self.dags = cg_vec
        self.solver = Solver()
        self.pulp_solver = pl.LpProblem('minimum_solution', pl.LpMinimize)
        self.edge_z3var_list = []
        self.edge_variables_3D_dict = {}
        self.node_variables_2D_dict = {}
        self.root_variables_2D_dict = {}
        self.solutions = []
        self.is_monolithic = None
        self.max_sol = self.graph.get_max_solutions()

        # #@ start generating flow specificatons.
        # model_table = self.find_reduced_model()
        # print('return model table size is ', len(model_table))
        # exit()
    #@ ---------------------------------------

    def reset(self):
        self.solver = Solver()
        self.edge_z3var_list = []
        self.edge_variables_3D_dict = {}
        self.node_variables_2D_dict = {}
        self.root_variables_2D_dict = {}
        self.solutions = []
        self.pulp_solver.variables().clear()
        self.pulp_solver.constraints.clear()

    def find_minimum_solution(self):
        self.create_constraints(0)
        status = self.pulp_solver.solve()
        print(pl.LpStatus[status])

        nodes = self.graph.get_nodes()
        edges = self.graph.get_edges().values()

        # Solution for Node Supports
        for node in nodes:
            print(node.get_symbol_index() + ' = ' + str(pl.value(node.get_pulp_var())))

        for edge in edges:
            print(edge.get_id() + ' = ' + str(pl.value(edge.get_pulp_var())))

    
    # Possibly need to make this function for monolithic, this is the dag version
    def create_constraints(self, ranking_threshold=100):
        nodes = self.graph.get_nodes()
        edges = self.graph.get_edges().values()

        for node in nodes.values():
            ## create constraint for each node
            node_z3var = node.get_z3var()
            node_support = node.get_support()
            if node_support == 0: continue
            self.solver.add(node_z3var == node_support)
            log(str(node_z3var) + ' == ' + str(node_support) + '\n', DEBUG)
            self.create_outgoing_edge_constraints(node)
            self.create_incoming_edge_constraints(node)
            
        #@ adding constraints on edge support
        for edge in edges:
            edge_z3var = edge.get_z3var()
            self.edge_z3var_list.append(edge_z3var)
            total_sup = edge.get_support()
            direct_sup = edge.get_direct_support()
            if direct_sup == 0:
                self.solver.add(edge_z3var <= total_sup, edge_z3var >= 0)
            else:
                self.solver.add(Or(And(edge_z3var >= direct_sup, edge_z3var <= total_sup), edge_z3var == 0))
            # src_node_sup = edge.get_source().get_support()
            # self.solver.add(Implies(edge_z3var>0, edge_z3var >= (src_node_sup/5)))
            log(str(0)+' <= '+str(edge_z3var)+ ' <= ' + str(total_sup) + '\n', DEBUG)
    ### ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;



    #@ adding constraints on node and its outgoing edges
    #@--------------------------------------------------
    #@ constraints on outgoing edges of a node may cause the CSP to be UNSAT if 
    #@ the node is the source of simultaneous multiple destnations, eg, a cache-write message  
    #@ can trigger memory-write and cache-invalidate at the same time. 
    def create_outgoing_edge_constraints(self, node):
        if self.graph.is_terminal(node):
            return

        node_z3var = node.get_z3var()
        node_pulp_var = node.get_pulp_var()
        pulp_var_edge_sum = 0
        outgoing_edges = node.get_outgoing_edges()
        node_edge_vars = []
        strong_causality = False
        total_sup = 0
        for edge in outgoing_edges:
            strong_causality = ((edge.get_fconf()==1))# and (edge.get_bconf()==1))
            edge_support = edge.get_support()
            total_sup += edge_support
            edge_ranking = edge.get_ranking()
            edge_z3var = edge.get_z3var()
            pulp_var_edge_sum += edge.get_pulp_var()
            #@ only consider edges with ranking higher than the threshold
            if True: #edge_ranking >= ranking_threshold:
                node_edge_vars.append(edge_z3var)
            # log(str(0)+' <= '+str(edge_int_var)+ ' <= ' + str(edge_support), DEBUG)

        self.pulp_solver += node_pulp_var == pulp_var_edge_sum
            ### Create unique causality constraint for each edge
            # all_other_edge_nil = None
            # for other_edge in outgoing_edges:
            #     if other_edge == edge: continue
            #     all_other_edge_nil = (other_edge.get_z3var() == 0) if all_other_edge_nil is None else And(all_other_edge_nil, (other_edge.get_z3var() == 0))
            # if all_other_edge_nil != None:
            #     self.solver.add(Implies(all_other_edge_nil, (edge.get_z3var() == edge.get_support())))                

        #@------------------------  
        #@ generate constraints on outgoing edges of a node
        sum_z3vars = None
        concurrent_z3vars = None
        s = ''
        for edge_var in node_edge_vars:
            sum_z3vars = edge_var if sum_z3vars is None else sum_z3vars + edge_var
            s = str(edge_var) if sum_z3vars is None else s + ' + ' + str(edge_var) 
        if sum_z3vars != None:
            if strong_causality == True:
                self.solver.add(node_z3var <= sum_z3vars)
            else:
                self.solver.add(0 < sum_z3vars)
            log(str(node.get_z3var()) + " <= " + str(s) + '\n', DEBUG)
    ### '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            

    ### create constraints on incoming edges of node
    def create_incoming_edge_constraints(self, node):
        if self.graph.is_initial(node):
            return

        node_z3var = node.get_z3var()
        node_pulp_var = node.get_pulp_var()
        pulp_var_edge_sum = 0
        incoming_edges = node.get_incoming_edges()
        node_edge_vars = []
        for edge in incoming_edges:
            edge_support = edge.get_support()
            pulp_var_edge_sum += edge.get_pulp_var()
            edge_z3var = edge.get_z3var()
            node_edge_vars.append(edge_z3var)

        self.pulp_solver += node_pulp_var == pulp_var_edge_sum

        sum_z3vars = None
        s = ''
        for edge_var in node_edge_vars:
            sum_z3vars = edge_var if sum_z3vars is None else sum_z3vars + edge_var
            s = s + ' + ' + str(edge_var) if s != '' else str(edge_var)
            
        if sum_z3vars != None:
            self.solver.add(node_z3var == sum_z3vars)
            log(str(node_z3var) + " == " + str(s) + '\n', DEBUG)
    ### ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
    

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


    def find_model_interactive(self):
        #@ add CG constraints into the solver
        self.create_constraints(0)

        edge_exclusion_list = []
        while self.solver.check() == sat:
            model = self.solver.model()
            self.print_z3model_edges(model)

            cmdln = input('What to do next? ')
            tokens = cmdln.split(' ')
            if tokens[0] == 'noedge' or tokens[0] == 'ne':
                edge = self.graph.get_edge(tokens[1], tokens[2])
                if edge is None:
                    print('Edge (%s, %s) does not exist' % (tokens[1], tokens[2]))
                else:
                    edge_z3var = edge.get_z3var()
                    edge_support = edge.get_support()
                    if self.solver.check(edge_z3var == 0) == sat:
                        self.solver.add(edge_z3var == 0)
                        edge_exclusion_list.append(tokens[1]+' ' + tokens[2]+'\n')
                    else:
                        print('unsat -- edge not removed')
            elif tokens[0] == 'yesedge' or tokens[0]=='ye':
                edge = self.graph.get_edge(tokens[1], tokens[2])
                if edge is None:
                    print('Edge (%s, %s) does not exist' % (tokens[1], tokens[2]))
                else:
                    edge_z3var = edge.get_z3var()
                    edge_support = edge.get_support()
                    if self.solver.check(edge_z3var > 0) == sat:
                        self.solver.add(edge_z3var > 0)
                    else:
                        print('unsat -- edge not added')
            elif tokens[0] == 'p' or tokens[0] == 'print':
                log('@%s:%d: print the model into file %s\n' % (whoami(), line_numb(), tokens[1]), INFO)
                try:
                    fp = open(tokens[1], "w")
                except IOError as e:
                    print("Couldn't open file (%s)." % tokens[1])
                for edge in self.graph.get_edges().values():
                    edge_z3var = edge.get_z3var()
                    if model[edge_z3var].as_long() != 0:
                        fp.write(str(edge.get_source().get_index()) + ' ' + str(edge.get_destination().get_index()) + '\n')
                ### Draw the output model into graph file in png.
                fp.close()
                pt = Planter()
                pt.draw(self.graph.get_msg_def_file_name(), tokens[1])
            elif tokens[0] == 'quit' or tokens[0] == 'q':
                try:
                    fp = open("edge_exclusion_list.txt", "w")  
                except IOError as e:
                    print("Couldn't open file (%s)." % 'edge_exclusion_list.txt')
                print('Writing excluded edges into file (edge_exclusion_list.txt)')
                fp.writelines(edge_exclusion_list) 
                fp.close()  
                return

            # #@--- start a new scope and recrusively find a reduce model
            # self.solver.push()
            # new_constr = False
            # for edge_z3var in edge_z3var_list:
            #     if model[edge_z3var]==0:
            #         self.solver.add(edge_z3var==0)
            # self.reduce_model_recursive(model, edge_z3var_list, model_table, 0)
            # self.solver.pop()
            # #@--- end of the scope

            # new_constr = False
            # for edge_z3var in edge_z3var_list:
            #     new_constr = Or(new_constr, And(model[edge_z3var] > 0, edge_z3var == 0))
            # # new_constr = constr if new_constr is None else Or(new_constr, constr)
            # new_constr = simplify(new_constr)
            # self.solver.add(new_constr) 
            # log('@%s:%d: next iteration\n' % (whoami(), line_numb()), INFO, False)
            # #@-------------------------------------
        


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


    def print_z3model_edges(self, m):
        edges = self.graph.get_edges().values()
        edge_count = 0
        for edge in edges:
            edge_z3var = edge.get_z3var()
            if m[edge_z3var].as_long() != 0:
                print(edge.print_full() + '\t' + str(m[edge_z3var]))
                edge_count += 1
        print('Edges in the model: ', edge_count)

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
