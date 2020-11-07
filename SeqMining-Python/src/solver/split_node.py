import copy
from src.logging import *
from z3 import *

#@ A type of edges which have instances of the same edge in the original causality graph
#@ one for each sequnece
#@
class split_node:
    def __init__(self, g_node, s_index):
        self.graph_node = g_node
        self.seq_index = s_index
        self.z3var = Int(self.graph_node.get_index() + '_' + str(self.seq_index))

    def __str__(self):
        return self.graph_node.get_index() + '_' + str(self.seq_index)

    def get_split_index(self):
        return self.graph_node.get_index() + '_' + str(self.seq_index)

    def get_node_index(self):
        return self.graph_node.get_index()

    def get_index(self):
        return self.graph_node.get_index()
    
    def get_seq_index(self):
        return self.seq_index

    def get_z3var(self):
        return self.z3var

        

        
        

    