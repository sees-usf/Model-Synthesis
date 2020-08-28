from multipledispatch import dispatch

from src.graph.edge import Edge


class Node:
    def __init__(self, symbol_index, message, command):
        self.symbol_index = symbol_index
        self.message = message
        self.command = command
        self.edges = {}
        self.support = 0
        self.depth = 0
        self.visited = False
        self.in_degree = 0
        self.out_degree = 0
        self.previous = None

    def __str__(self):
        return self.symbol_index

    def get_symbol_index(self):
        return self.symbol_index

    def get_message(self):
        return self.message

    def get_command(self):
        return self.command

    def get_edges(self):
        return self.edges

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

    @dispatch(Edge)
    def remove_edge(self, edge):
        self.edges.pop(str(edge), None)

    @dispatch(object)
    def remove_edge(self, destination):
        self.edges.pop(self.symbol_index + '_' + str(destination), None)

    def clear_edges(self):
        self.edges.clear()
