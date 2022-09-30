import copy
from src.logging import *
from z3 import *


class trace2flows:
    def __init__(self, cg_vec):
        self.graph = cg_vec.pop(0)
        self.dags = cg_vec
        self.solver = Solver()
        self.edge_variables_3D_dict = {}
        self.node_variables_2D_dict = {}
        self.root_variables_2D_dict = {}
        self.solutions = []
        self.is_monolithic = None
        self.max_sol = self.graph.get_max_solutions()

    def generate_split_solutions(self):
        dagID = 'a'
        self.is_monolithic = False
        for dag in self.dags:
            self.create_vars_and_edge_constraints(dag, dagID)
            dagID = chr(ord(dagID) + 1)

        self.create_unified_constraints()
        self.solve()

    def generate_monolithic_solutions(self):
        self.is_monolithic = True
        graphID = 'x'
        self.create_vars_and_edge_constraints(self.graph, graphID)
        
        # Create the copy of the original solver for later use.
        solver_orig = Solver()
        solver_orig.add(self.solver.assertions())

        # solve and generate solutions.
        self.solve()

        # # ********** in progress ****************************
        # # break a solution to eliminate ambiguity
        # for sol in self.solutions:
        #     solver_copy = Solver()
        #     solver_copy.add(solver_orig.assertions())
            
        #     edge_vars = self.edge_variables_3D_dict[graphID]
        #     for edge_var_list in edge_vars.values():
        #         print(edge_var_list)
        #     root_vars = self.root_variables_2D_dict[graphID]
        #     node_vars = self.node_variables_2D_dict[graphID]

        #     # split nodes for each root nodes
        #     for nodeID in node_vars:
        #         if nodeID not in root_vars:
        #             node_z3var = node_vars[nodeID]
        #             root_node_z3var_sum = None
        #             for rootID in root_vars:
        #                 root_node_z3var = Int(rootID+'_'+nodeID)
        #                 if root_node_z3var_sum==None:
        #                     root_node_z3var_sum = root_node_z3var
        #                 else:
        #                     root_node_z3var_sum += root_node_z3var
        #             solver_copy.add(node_z3var == root_node_z3var_sum)

        #             # split edges for each root nodes
        #             if nodeID not in edge_vars:  # return in case nodeID is a terminal
        #                 return
        #             node_outedges = edge_vars[nodeID]
        #             for oedgeID in node_outedges:
        #                 oedge_z3var = node_outedges[oedgeID]
        #                 root_edge_z3var_sum = None
        #                 for rootID in root_vars:
        #                     root_edge_z3var = Int(rootID+'_'+oedgeID)
        #                     if root_edge_z3var_sum==None:
        #                         root_edge_z3var_sum = root_edge_z3var
        #                     else:
        #                         root_edge_z3var_sum += root_edge_z3var
        #                 solver_copy.add(oedge_z3var == root_edge_z3var_sum)
        #                 print(oedge_z3var == root_edge_z3var_sum)

        #     exit()    

        #     for root_var in root_vars:
                
        #         root_z3var = node_vars[root_var]
        #         root_outedges = edge_vars[root_var]
        #         for edge_var in root_outedges:
        #             edge_z3var = root_outedges[edge_var]
        #             edge_z3val = sol[edge_z3var]
        #             print(edge_var, ' ', edge_z3val)
        #             solver_copy.add(edge_z3var == edge_z3val)

        #     solver_copy.check()
        #     m = solver_copy.model()
        #     print(m)
        #     exit()
        # #********************************************************************


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
            return

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
            sol_count += 1
            if sol_count > self.max_sol:
                break
            m = self.solver.model()
            #self.solutions.append(m)
            self.add_solution(m)
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

            for dag_key in self.edge_variables_3D_dict:
                filtered_edge_vars = list(filter(lambda x: str(x)[0] == dag_key, edge_vars.values()))
                #self.solver.add(
                #    Or([And(m[edge_var] > 0, edge_var == 0) for edge_var in filtered_edge_vars]))

                new_constr = False
                for edge_var in filtered_edge_vars:
                    new_constr = Or(new_constr, And(m[edge_var] > 0, edge_var == 0))
                constr = simplify(new_constr)
                self.solver.add(constr)
                
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


    def get_solutions(self):
        return self.solutions
