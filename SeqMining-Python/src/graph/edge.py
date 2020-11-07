from src.logging import *
from z3 import *

class Edge:
    def __init__(self, graph, src, dest):
        self.edge_id = src.get_symbol_index() + "_" + dest.get_symbol_index()
        self.source = src
        self.destination = dest
        self.edge_support = 0
        self.conf_measure = 100
        self.graph = graph
        self.z3var = Int(self.edge_id)
        self.source.add_outgoing_edge(self)
        self.destination.add_incoming_edge(self)

    def __str__(self):
        return self.edge_id

    def get_id(self):
        return self.edge_id

    def get_source(self):
        return self.source

    def get_destination(self):
        return self.destination

    def get_edge_support(self):
        return self.edge_support

    def get_support(self):
        return self.edge_support

    def get_z3var(self):
        return self.z3var

    def set_edge_support(self, value):
        self.edge_support = value

    def set_conf_measure(self, value):
        self.conf_measure = Value

    def set_support(self, value):
        self.edge_support = value

    def equals(self, edge):
        return self.edge_id == edge.edge_id
