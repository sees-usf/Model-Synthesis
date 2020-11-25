from src.logging import *
from z3 import *

class Edge:
    def __init__(self, graph, src, dest):
        self.graph = graph
        self.id = src.get_symbol_index() + "_" + dest.get_symbol_index()
        self.source = src
        self.destination = dest
        self.support = 0
        self.forward_conf = 0
        self.backward_conf = 0
        self.ranking = 100
        self.z3var = Int(self.id)
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

    def get_edge_support(self):
        return self.support

    def get_support(self):
        return self.support

    def get_z3var(self):
        return self.z3var

    def get_ranking(self):
        return self.ranking

    def set_edge_support(self, value):
        self.support = value

    def set_ranking(self, value):
        self.ranking = value

    def set_support(self, value):
        self.support = value
        self.forward_conf = (self.support/self.source.get_support())
        self.backward_conf = (self.support/self.destination.get_support())

    def equals(self, edge):
        return self.id == edge.id
