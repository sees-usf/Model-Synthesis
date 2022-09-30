import re, os, random, sys
from datetime import datetime
from enum import Enum
import copy
from multipledispatch import dispatch
from nltk.tokenize import regexp_tokenize
from copy import deepcopy
from uml_edge import Edge
from uml_node import Node


class Graph:
    def __init__(self):
        self.msg_start_table = {}
        self.msg_middle_table = {}
        self.msg_terminal_table = {}
        self.nodes = {}
        self.roots = {}
        self.edges = {}
        self.msg_filename = None
        self.model_file = None 
           

    def read_msg_def(self, msg_def_file):
        try:
            fp = open(msg_def_file, 'r')
        except IOError as e:
            print("Couldn't open file (%s)." % e)
            return

        self.msg_filename = msg_def_file

        f1 = fp.readlines()
        parse_state = None
        for line in f1:
            tokens = regexp_tokenize(line, pattern=r'\s|[,:]', gaps=True)
            if not tokens: # token list is empty
                continue 
            if tokens[0] == '#':
                if parse_state == None:
                    parse_state = 'start'
                elif parse_state == 'start':
                    parse_state = 'middle'
                elif parse_state == 'middle':
                    parse_state = 'terminal'
                continue

            if parse_state == 'start':
                self.msg_start_table[tokens[0]] = tokens[1:5]
            elif parse_state == 'middle':
                self.msg_middle_table[tokens[0]] = tokens[1:5]
            elif parse_state == 'terminal':
                self.msg_terminal_table[tokens[0]] = tokens[1:5]

        fp.close()


    def read_bin_model(self, model_file):
        try:
            fp = open(model_file, 'r')
        except IOError as e:
            print("Couldn't open file (%s)." % e)
            return

        self.model_file = model_file 

        section = None
        lines = fp.readlines()
        for line in lines:
            if line[0:5] == '#Node':
                section = 'node'
                continue
            elif line[0:5] == '#Edge':
                section = 'edge'
                continue
            
            line = line.split()#line.rstrip("\n")
            if not len(line): 
                continue

            if section == 'node':
                msg = self.get_message(line[0])
                node = Node(line[0], msg[0], msg[1], msg[2], msg[3])
                node.set_support(line[1])
                self.add_node(node)

            if section == 'edge':
                self.create_edge(line[0], line[1], line[2])
            

    def add_node(self, node):
        self.nodes[str(node)] = node

    def get_node(self, symbol_index):
        try:
            return self.nodes[symbol_index]
        except IndexError as e:
            print('node ', symbol_index, ' does not exist!')
            print(e)
            exit()

    def remove_node(self, node):
        self.nodes.pop(str(node), None)

    def has_node(self, node):
        return node in self.nodes.values() or str(node) in self.nodes

    def get_nodes(self):
        return self.nodes

    def add_root(self, root):
        self.roots[str(root)] = root

    def remove_root(self, root):
        self.roots.pop(str(root), None)

    def is_root(self, node):
        return node in self.roots.values() or str(node) in self.roots

    def get_roots(self):
        return self.roots

    def get_message(self, msg_idx):
        if msg_idx in self.msg_start_table.keys():
            return self.msg_start_table[msg_idx]
        if msg_idx in self.msg_middle_table.keys():
            return self.msg_middle_table[msg_idx]
        if msg_idx in self.msg_terminal_table.keys():
            return self.msg_terminal_table[msg_idx]


    def create_edge(self, src_index, dest_index, support):
        src_node = self.nodes[src_index]
        dest_node = self.nodes[dest_index]
        edge = Edge(src_node, dest_node, int(support))
        self.edges[edge.get_id()] = edge


    def print_nodes(self):
        print('Nodes: ')
        print()
        total_node_support = 0

        for node in self.nodes.values():
            text = (
                '''     %s : %s to %s with node support of %d'''
                % (node.get_symbol_index(), node.get_message()[0], node.get_message()[1], node.get_support())
            )

            total_node_support += node.get_support()
            print(text)
        print()
        print('Total Node Support: %d' % total_node_support)
        print()

    def print_edges(self):
        print('Edges:')
        print()
        for node in self.nodes.values():
            print('     Origin: %s' % node.get_symbol_index())

            for edge in node.get_edges().values():
                print('        ' + str(edge) + ' with edge support of ' + str(edge.get_edge_support()))
            print()

    def print_graph(self):
        self.print_nodes()
        self.print_edges()


    def draw_plantuml(self):
        plantuml_syntax = '@startuml\n'
        for node in self.nodes.values():
            message = node.get_message()
            plantuml_syntax += 'Message_' + str(node.get_index()) + ':' + message + '\n'

        for edge in self.edges.values():
            src_index = edge.get_src_node().get_index()
            dest_index = edge.get_dest_node().get_index()
            plantuml_syntax += 'Message_' + str(src_index) + ' --> Message_' + str(dest_index) + '\n'

        plantuml_syntax += '@enduml'

        #@ write to files
        now = datetime.now()
        mfilename = self.model_file.split('.')
        print(mfilename)
        ofilename = mfilename[0] + '_'+ now.strftime("%H-%M-%S")
        try:
            fp = open(ofilename+'.txt', 'w')
        except IOError as e:
            print("Couldn't open file (%s)." % e)
            return

        fp.write(plantuml_syntax)
        fp.close()
        os.system("java -jar "+ str(sys.path[1])+"/plantuml.jar " + ofilename+'.txt')
        print(f"Done! State diagram @%s.png"%ofilename)
