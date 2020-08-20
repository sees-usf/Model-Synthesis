from z3 import *


class Z3Solver:
    def __init__(self, graph, dags):
        self.graph = graph
        self.dags = dags
        self.solver = Solver()
        self.edge_variables = []
        self.node_variables = []

    def generate_split_solutions(self):
        dagID = 'a'

        for dag in self.dags:
            self.create_vars_and_outgoing_edge_constraints(dag)
            self.create_incoming_edge_constraints(dag)

        self.create_unified_constraints()

    def generate_monolithic_solutions(self):
        graphID = ''

        self.create_vars_and_outgoing_edge_constraints(self.graph)
        self.create_incoming_edge_constraints(self.graph)

    def create_vars_and_outgoing_edge_constraints(self, graph):
        pass

    def create_unified_constraints(self):
        pass

    def create_incoming_edge_constraints(self, graph):
        pass

