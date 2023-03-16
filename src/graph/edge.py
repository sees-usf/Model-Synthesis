from src.logging import *
from z3 import *
# import pulp as pulp


class Edge:
    def __init__(self, graph, src, dest):
        self.graph = graph
        self.id = src.get_symbol_index() + "_" + dest.get_symbol_index()

        ## nodes in the causality_graph representing messages with potential causality 
        self.source = src
        self.destination = dest

        ## support is a list of index pairs of positions of src/dest in the trace
        ## its length gives support count
        self.support = []

        ## An approximate number of edges where src/dest happen w/o other causal messages 
        self.direct_support_count = 0

        self.forward_conf = 0
        self.backward_conf = 0
        self.mean_conf = 0
        self.ranking = 100
        self.z3var = Int(self.id)
        # self.pulp_var = pulp.LpVariable(self.id)
        self.source.add_outgoing_edge(self)
        self.destination.add_incoming_edge(self)

    def __str__(self):
        return self.id

    def get_id(self):
        return self.id

    def get_source(self):
        return self.source

    def get_destination(self):
        return self.destination

    def get_support(self):
        return 0 if self.support is None else len(self.support)
        
    def get_support_list(self):
        return self.support

    # def get_support_pos(self):
    #     return self.support

    def get_direct_support(self):
        return self.direct_support_count

    def get_fconf(self):
        return self.forward_conf

    def get_bconf(self):
        return self.backward_conf

    def get_hconf(self):
        return self.mean_conf

    def get_z3var(self):
        return self.z3var

    def get_ranking(self):
        return self.ranking

    def set_direct_support(self, value):
        self.direct_support_count = value

    def set_ranking(self, value):
        self.ranking = value

    def set_support(self, value):
        self.support = value
        self.forward_conf = (self.get_support() / self.source.get_support())
        self.backward_conf = (self.get_support() / self.destination.get_support())
        if self.get_support() != 0:
            self.mean_conf = (2 * self.forward_conf * self.backward_conf) / (self.forward_conf + self.backward_conf)

    def equals(self, edge):
        return self.id == edge.id

    def print_full(self):
        return "{:<45}".format(self.get_source().print_full()) + ' -->  ' + "{:<45}".format(
            self.get_destination().print_full())

    def set_pulp_var(self, pulp_var):
        self.pulp_var = pulp_var

    def get_pulp_var(self):
        return self.pulp_var
