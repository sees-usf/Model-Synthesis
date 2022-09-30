from multipledispatch import dispatch

import uml_edge
from z3 import *

class Node:
    def __init__(self, index, src, dest, cmd, cmd_type):
        self.index = index
        self.source = src
        self.destination = dest
        self.command = cmd
        self.msg_type = cmd_type
        self.succ_nodes = []
        self.pred_nodes = []
        self.support = 0
        self.graph = None

    def __str__(self):
        return self.index

    def get_index(self):
        return self.index

    def get_message(self):
        return self.source + ':' + self.destination + ':' + self.command + ':' + self.msg_type

    def get_type(self):
        return self.msg_type
    
    def get_source(self):
        return self.source
    
    def get_destination(self):
        return self.destination

    def get_command(self):
        return self.command


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

    def set_index(self, index):
        self.index = index

    def set_source(self, src):
        self.source = src

    def set_destination(self, dest):
        self.destination = dest

    def set_command(self, command):
        self.command = command

    def set_support(self, support):
        self.support = support

    def add_succ(self, dest):
        self.succ_nodes.append(dest)

    def add_pred(self, src):
        self.pred_nodes.append(src)


    