import copy

from z3 import *


class Z3Solver:
    def __init__(self, graph, dags):
        self.graph = graph
        self.dags = dags
        self.solver = Solver()
        self.edge_variables_3D_dict = {}
        self.node_variables_2D_dict = {}
        self.solutions = []
        self.is_monolithic = None
        self.max_sol = 10
        self.DEBUG = False

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
        self.create_vars_and_edge_constraints(self.graph, 'x')
        self.solve()

    def create_vars_and_edge_constraints(self, graph, graphID):
        nodes = graph.get_nodes()
        edge_vars = {}
        node_vars = {}

        print(" node --> edge constraints ========") if self.DEBUG else None
        self.create_vars_and_outgoing_edge_constraints(graph, graphID, nodes, edge_vars, node_vars)
        print(" edge --> node constraints ========") if self.DEBUG else None
        #self.create_incoming_edge_constraints(graphID, nodes, edge_vars, node_vars)

        self.edge_variables_3D_dict[graphID] = edge_vars
        self.node_variables_2D_dict[graphID] = node_vars

    # Possibly need to make this function for monolithic, this is the dag version
    def create_vars_and_outgoing_edge_constraints(self, graph, graphID, nodes, edge_vars, node_vars):
        for origin in nodes.values():
            nodeID = graphID + str(origin)
            node_int_var = Int(nodeID)

            if graph.is_root(origin) or self.is_monolithic:
                self.solver.add(node_int_var == origin.get_support())
                print("Debug >> ", node_int_var, " == ", origin.get_support()) if self.DEBUG else None
            else:
                self.solver.add(node_int_var <= origin.get_support(), node_int_var >= 0)
                print("Debug >> 0 <= ", node_int_var, " <= ", origin.get_support()) if self.DEBUG else None

            node_vars[nodeID] = node_int_var
            edges = origin.get_edges().values()

            if edges:
                node_edge_vars = {}
                for edge in edges:
                    edge_support = edge.get_edge_support()
                    edgeID = graphID + str(edge)
                    edge_int_var = Int(edgeID)
                    self.solver.add(edge_int_var <= edge_support, edge_int_var >= 0)
                    node_edge_vars[edgeID] = edge_int_var
                    print(0, ' <= ', edge_int_var, " <= ", edge_support) if self.DEBUG else None
                
                sum_int_vars = None
                s = ''
                for edge_var in node_edge_vars.values():
                    if sum_int_vars is None:
                        sum_int_vars = edge_var
                        s = str(edge_var) if self.DEBUG else None
                    else:
                        sum_int_vars += edge_var
                        s = s + ' + ' + str(edge_var) if self.DEBUG else None

                self.solver.add(node_vars[nodeID] == sum_int_vars)
                print(node_vars[nodeID], " == ", s) if self.DEBUG else None
                edge_vars[nodeID] = node_edge_vars
        
        # if self.solver.check() == unsat:
        #     print("*** UNSAT ***")
        #     exit()

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
                    s = str(edge_var) if self.DEBUG else None
                else:
                    sum_int_vars += edge_var   #edge_vars[originID][graphID + edgeID]
                    s = s + ' + ' + str(edge_var) if self.DEBUG else None


            if sum_int_vars is not None:
                self.solver.add(node_vars[destinationID] == sum_int_vars)
                print(node_vars[destinationID], " == ", s) if self.DEBUG else None

            # if self.solver.check() == unsat:
            #     print("*** UNSAT ***")
            #     exit()

    def create_unified_constraints(self):
        print(" unified node constraints ========") if self.DEBUG else None
        self.create_unified_node_constraints()
        print(" unified edge constraints ========") if self.DEBUG else None
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
                print(sum_int_vars, " == ", node.get_support()) if self.DEBUG else None

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
                print(sum_int_vars, " <= ", edge.get_edge_support(), " ", "0 <= ", sum_int_vars) if self.DEBUG else None


    def solve(self):
        sol_count = 0
        if self.solver.check() == unsat:
            print()
            print('The constraints encoded are not satisfiable.')
            print("Number of solutions found: ", sol_count)
            print()
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
            self.solutions.append(m)
            print(m) if self.DEBUG==True else None

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
                if self.DEBUG == True:
                    print(new_constr)
                    print('-------------')
                    print(constr)
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
        #         if str(solution[edge_var]) != '0':
        #             print(str(edge_var) + ' with edge support of ' + str(solution[edge_var]))

        print()
        print("Number of solutions found: ", sol_count)
        print()
        # END

    def get_solutions(self):
        return self.solutions
