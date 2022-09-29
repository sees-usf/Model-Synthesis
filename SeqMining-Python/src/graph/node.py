from multipledispatch import dispatch

from src.graph.edge import Edge
from src.logging import *
from z3 import *
# import pulp as pl

class Node:
    def __init__(self, graph, symbol_index, message, command, msg_type):
        self.symbol_index = symbol_index
        self.message = message
        self.command = command
        self.msg_type = msg_type
        self.edges = {}
        self.succ_nodes = []
        self.pred_nodes = []
        self.outgoing_edges = []
        self.incoming_edges = []
        self.support = 0
        self.depth = 0
        self.visited = False
        self.in_degree = 0
        self.out_degree = 0
        self.previous = None
        self.graph = graph
        self.z3var = Int(str(self.symbol_index))
        self.pulp_var = None

    def __str__(self):
        return self.symbol_index

    def get_symbol_index(self):
        return self.symbol_index

    def get_index(self):
        return self.symbol_index

    def get_message(self):
        return self.message
        
    def get_message_str(self):
        return '(' + self.get_source() + ', ' + self.get_destination() + ', ' + self.get_command() + ', ' + self.get_type() + ')'

    def get_type(self):
        return self.msg_type
    
    def get_source(self):
        return self.message[1]
    
    def get_destination(self):
        return self.message[2]

    def get_command(self):
        return self.command

    def get_edges(self):
        return self.edges

    def get_outgoing_edges(self):
        return self.outgoing_edges

    def get_incoming_edges(self):
        return self.incoming_edges

    def get_z3var(self):
        return self.z3var

    def get_succ_nodes(self):
        return self.succ_nodes
        # indices = []
        # for succ in self.succ_nodes:
        #     indices.append(succ.get_symbol_index())
        # return indices
    
    def get_pred_nodes(self):
        return self.pred_nodes

    def get_support(self):
        return self.support

    def get_depth(self):
        return self.depth

    def is_visited(self):
        return self.visited

    def get_in_degree(self):
        return self.in_degree

    def get_out_degree(self):
        return self.out_degree

    def get_previous(self):
        return self.previous

    def set_symbol_index(self, symbol_index):
        self.symbol_index = symbol_index

    def set_message(self, message):
        self.message = message

    def set_command(self, command):
        self.command = command

    def set_support(self, support):
        self.support = support

    def set_depth(self, depth):
        self.depth = depth

    def set_visited(self):
        self.visited = True

    def set_not_visited(self):
        self.visited = False

    def set_in_degree(self, in_degree):
        self.in_degree = in_degree

    def set_out_degree(self, out_degree):
        self.out_degree = out_degree

    def set_previous(self, previous):
        self.previous = previous

    def __str__(self):
        return self.symbol_index

    @dispatch(str)
    def get_edge(self, edge_id):
        return self.edges[edge_id]

    @dispatch(object)
    def get_edge(self, destination):
        return self.edges[self.symbol_index + '_' + str(destination)]

    def add_edge(self, edge):
        self.edges[str(edge)] = edge

    def add_succ(self, dest):
        self.succ_nodes.append(dest)

    def add_pred(self, src):
        self.pred_nodes.append(src)

    def add_incoming_edge(self, edge):
        self.pred_nodes.append(edge.get_source())
        self.incoming_edges.append(edge)

    def add_outgoing_edge(self, edge):
        self.succ_nodes.append(edge.get_destination())
        self.outgoing_edges.append(edge)

    def print_full(self):
        return "{:<7}".format(str(self.symbol_index) + ' : ') + '(' + self.get_source() + ', ' + self.get_destination()+', ' + self.get_command()+', '+self.get_type()+')'

    @dispatch(Edge)
    def remove_edge(self, edge):
        self.edges.pop(str(edge), None)

    @dispatch(object)
    def remove_edge(self, destination):
        self.edges.pop(self.symbol_index + '_' + str(destination), None)

    def clear_edges(self):
        self.edges.clear()

    def set_pulp_var(self, pulp_var):
        self.pulp_var = pulp_var

    def get_pulp_var(self):
        return self.pulp_var
