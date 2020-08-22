from copy import deepcopy

from z3 import *


class Z3Solver:
    def __init__(self, graph, dags):
        self.graph = graph
        self.dags = dags
        self.solver = Solver()
        self.edge_variables_3D_dict = {}
        self.node_variables_2D_dict = {}
        self.solutions = []

    def generate_split_solutions(self):
        dagID = 'a'

        for dag in self.dags:
            self.create_vars_and_edge_constraints(dag, dagID)
            dagID = chr(ord(dagID) + 1)

        self.create_unified_constraints()
        self.solve()

    def generate_monolithic_solutions(self):
        self.create_vars_and_edge_constraints(self.graph, '')
        self.solve()

    def create_vars_and_edge_constraints(self, graph, graphID):
        nodes = graph.get_nodes()
        edge_vars = {}
        node_vars = {}

        self.create_vars_and_outgoing_edge_constraints(graph, graphID, nodes, edge_vars, node_vars)
        self.create_incoming_edge_constraints(graphID, nodes, edge_vars, node_vars)

        self.edge_variables_3D_dict[graphID] = edge_vars
        self.node_variables_2D_dict[graphID] = node_vars

    def create_vars_and_outgoing_edge_constraints(self, graph, graphID, nodes, edge_vars, node_vars):
        # print("This loop prepares node variables, edge variables, and also all constraints related to the outgoing
        # edges of each node i")
        for origin in nodes.values():
            nodeID = graphID + str(origin)
            node_int_var = Int(nodeID)
            self.solver.add(node_int_var == origin.get_support()) if graph.is_root(origin) else self.solver.add(
                node_int_var <= origin.get_support(), 0 <= node_int_var)
            node_vars[nodeID] = node_int_var
            edges = origin.get_edges().values()

            if edges:
                node_edge_vars = {}
                for edge in edges:
                    edge_support = edge.get_edge_support()
                    edgeID = graphID + str(edge)
                    edge_int_var = Int(edgeID)
                    self.solver.add(edge_int_var <= edge_support, 0 <= edge_int_var)
                    node_edge_vars[edgeID] = edge_int_var

                sum_int_vars = None

                for edge_var in node_edge_vars.values():
                    if sum_int_vars is None:
                        sum_int_vars = edge_var
                    else:
                        sum_int_vars += edge_var
                # print(sum_int_vars, node_vars[i])

                self.solver.add(node_vars[nodeID] == sum_int_vars)
                edge_vars[nodeID] = node_edge_vars

    def create_incoming_edge_constraints(self, graphID, nodes, edge_vars, node_vars):
        # print("This loop prepares constraints for every node i that has incoming edges")
        for destination in nodes.values():
            sum_int_vars = None
            destinationID = graphID + str(destination)

            for origin in nodes.values():

                if origin == destination:
                    continue

                edgeID = str(origin) + '_' + str(destination)
                edges = origin.get_edges()

                if not edges.keys().__contains__(edgeID):
                    continue

                originID = graphID + str(origin)

                if sum_int_vars is None:
                    sum_int_vars = edge_vars[originID][graphID + edgeID]
                else:
                    sum_int_vars += edge_vars[originID][graphID + edgeID]

            if sum_int_vars is not None:
                self.solver.add(node_vars[destinationID] == sum_int_vars)

    def create_unified_constraints(self):
        self.create_unified_node_constraints()
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

    def create_unified_edge_constraints(self):
        for edge in self.graph.get_edges().values():

            sum_int_vars = None

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

            if sum_int_vars is not None:
                self.solver.add(sum_int_vars <= edge.get_edge_support(), sum_int_vars >= 0)

    def solve(self):

        if self.solver.check() == unsat:
            print('The constraints encoded are not satisfiable')
            print()
            for x in self.solver.assertions():
                print(x)
            return

        edge_vars = {}

        for dag_key in self.edge_variables_3D_dict:
            for node_key in self.edge_variables_3D_dict[dag_key]:
                for edge_var_key in self.edge_variables_3D_dict[dag_key][node_key]:
                    edge_vars[edge_var_key] = self.edge_variables_3D_dict[dag_key][node_key][edge_var_key]

        solution_edge_vars = deepcopy(edge_vars)

        old_m = self.solver.model()

        self.solutions.append(old_m)

        self.solver.add(Or([edge_var != old_m[edge_var] for edge_var in edge_vars.values()]))

        while self.solver.check() == sat:
            m = self.solver.model()
            self.solutions.append(m)

            for edge_var in edge_vars.values():
                if old_m[edge_var] is m[edge_var]:
                    edge_vars.pop(str(edge_var), None)

            self.solver.add(
                Or([And(old_m[edge_var] == m[edge_var], edge_var != m[edge_var]) for edge_var in edge_vars.values()]))

        for i, solution in enumerate(self.solutions):
            print()
            print('Solution ' + str(i+1))
            print()
            char_id = 'a'
            for edge_var in solution_edge_vars.values():
                if char_id != str(edge_var)[0]:
                    char_id = str(edge_var)[0]
                    print()
                if str(solution[edge_var]) != '0':
                    print(str(edge_var) + ' with edge support of ' + str(solution[edge_var]))
