import copy
from src.logging import *
from z3 import *

#@ A type of edges which have instances of the same edge in the original causality graph
#@ one for each sequnece
#@
class split_edge:
    def __init__(self, g_edge, s_index):
        self.graph_edge = g_edge
        self.seq_index = s_index
        self.z3var = Int(self.graph_edge.get_id() + '_' + str(self.seq_index))

    def get_id(self):
        return self.graph_edge.get_id()
    
    def get_index(self):
        return self.seq_index

    def get_z3var(self):
        return self.z3var

        

        
        

    