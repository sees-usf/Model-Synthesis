import copy
from multipledispatch import dispatch
from nltk.tokenize import regexp_tokenize
from copy import deepcopy
from src.graph.edge import Edge
from src.graph.node import Node


class Graph:
    def __init__(self):
        self.nodes = {}
        self.roots = {}
        self.terminal_nodes = {}
        self.edges = {}
        self.max_height = 0
        self.DEBUG = False


    def generate_graph(self, filename):
        print("Generating causality graph for", filename)
        f = open(filename, 'r')

        root_node_strings = []

        f1 = f.readlines()
        is_root_definitions = False
        for line in f1:

            tokens = regexp_tokenize(line, pattern=r'\s|[,:]', gaps=True)

            if tokens[0] == '#':
                is_root_definitions = not is_root_definitions
                continue

            if is_root_definitions:
                root_node_strings.append(tokens[0])

            symbol_index = tokens[0]
            origin = tokens[1]
            destination = tokens[2]
            command = tokens[3]
            message = (origin, destination)

            if not self.has_node(symbol_index):
                node = Node(symbol_index, message, command)
                self.add_node(node)
                if symbol_index in root_node_strings:
                    self.add_root(node)

        f.close()
        self.generate_edges()
        
        # temp code for generating DAG-CG for each root node
        # for n in self.nodes.keys():
        #     idx=[]
        #     succ =  self.get_node(n).get_succ_nodes()
        #     for sn in succ:
        #         idx.append(sn.get_symbol_index())
        #     print(n, '-->', idx)
        # print(self.roots)
        # print("******************")
        # f = open("cg.cg", "w+")
        # for root in self.roots:
        #     print('Generating CG rooted at ', root, ' with length ', self.max_height)        
        #     mono_cg = self.generate_cg(self.nodes[root])
        #     f.write(self.print_cg(mono_cg))
        #     f.write("#\n")
        #     #exit()  
        # f.close()
        
        
    def generate_edges(self):
        for origin in self.nodes.values():
            if origin in self.terminal_nodes:
                continue

            origin_message = origin.get_message()

            for destination in self.nodes.values():
                if origin == destination or self.is_root(destination):
                    continue

                destination_message = destination.get_message()

                if origin_message[1] == destination_message[0]:
                    edge = Edge(origin, destination)
                    origin.add_edge(edge)
                    origin.add_succ(destination)
                    self.add_edge(edge)

            if not origin.get_edges():
                self.add_terminal_node(origin)
                
      
    # @Author: Zheng
    # @Function: check if an element in a list in terms of index
    def checkList(self, li, el):
        for target in li:
            if el.get_symbol_index() == target.get_symbol_index():
                return True
        return False
    
    # Author: Zheng
    # Function: generate a tree for 'root' node such that no cycle exists in any path from the root, and
    #           every path is up to length of 'heigth'
    def generate_cg(self, root_node):
        mono_cg = {}
        path_node = []
        path_succ = []

        root_node_copy = copy.copy(root_node)
        root_node_copy_succ = copy.copy(root_node.get_succ_nodes())
        path_node.append(root_node_copy)
        path_succ.append(root_node_copy_succ)
        mono_cg[root_node_copy] = []
            
        path_index=[]
        path_index.append(root_node.get_symbol_index())
            
        while len(path_node) != 0:
            head_node = path_node[-1]
            head_succ_nodes = path_succ[-1]
            if len(head_succ_nodes) == 0:
                path_node.pop(-1)
                path_succ.pop(-1)
                path_index.pop(-1)
                continue
                
            nxt_node = copy.copy(head_succ_nodes.pop(-1))
            if self.checkList(path_node, nxt_node) == False:#nxt_node not in path_node:
                # if len(path_node) == height-1:
                #     path_index.append(nxt_node.get_symbol_index())
                #     print(path_index)
                #     path_index.pop(-1)
                    
                if len(path_node) < self.max_height-1:
                    path_node.append(nxt_node)
                    path_succ.append(copy.copy(self.nodes[nxt_node.get_symbol_index()].get_succ_nodes()))
                    path_index.append(nxt_node.get_symbol_index())
                #if nxt_node not in mono_cg:
                mono_cg[nxt_node] = []
                nxt_node.set_depth(head_node.get_depth()+1)
                mono_cg[head_node].append(nxt_node)
            #     
            #     
            # else:
            #     print(' cycle found from ', nxt_node)
            #     print(path_index)
   
        # print(root_node_copy)
        # path = [root_node_copy.get_symbol_index()]
        # self.print_path(mono_cg, root_node_copy, path, 1)
        return mono_cg
        
        
    def print_cg(self, cg):
        cg_str = ""
        for node in cg.keys():
            cg_str += node.get_symbol_index() + "@" + str(node.get_depth()) + " : "
            succ_list = cg[node]
            for succ in succ_list:
                cg_str += succ.get_symbol_index() + "@" + str(succ.get_depth()) + " "
            cg_str += "\n"
        return cg_str
        
    # Author; Zheng
    # Function: print to stdout all paths in 'cg' starting from 'root_node'
    def print_path(self, cg, root_node, path, level):
        #print('level ', level, "  ", len(cg[root_node]))        
        for node in cg[root_node]:
            path.append(node.get_symbol_index())
            print(path)
            self.print_path(cg, node, path, level+1)
            path.pop(-1)

    
    def generate_dags(self):
        dags = []
        traversal_queue = []

        for root in self.roots.values():
            self.reset_visited_nodes()
            dag = Graph()
            traversal_queue.append(root)
            self.generate_dags_util(dag, traversal_queue)
            dag.generate_edges()
            dag.remove_cycles()
            dags.append(dag)

        return dags

    def generate_dags_util(self, dag, traversal_queue):
        if not traversal_queue:
            return

        node = traversal_queue.pop(0)
        copy_node = deepcopy(node)
        copy_node.set_support(0)

        if self.is_root(node):
            node.set_visited()
            dag.add_root(copy_node)
            dag.add_node(copy_node)

        for edge in node.get_edges().values():
            if not edge.get_destination().is_visited():
                destination = edge.get_destination()
                copy_node_2 = deepcopy(destination)
                copy_node_2.set_support(0)
                dag.add_node(copy_node_2)
                destination.set_visited()
                traversal_queue.append(destination)

        if not node.get_edges():
            dag.add_terminal_node(node)

        self.generate_dags_util(dag, traversal_queue)

    def add_node(self, node):
        self.nodes[str(node)] = node

    def get_node(self, symbol_index):
        return self.nodes[symbol_index]

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

    def add_terminal_node(self, node):
        self.terminal_nodes[str(node)] = node

    def is_terminal_node(self, node):
        return node in self.terminal_nodes.values() or str(node) in self.terminal_nodes

    def get_terminal_nodes(self):
        return self.terminal_nodes

    @dispatch(object)
    def add_edge(self, edge):
        edge.get_origin().add_edge(edge)
        self.edges[str(edge)] = edge

    @dispatch(str, str)
    def add_edge(self, origin_str, destination_str):
        origin = self.nodes[origin_str]
        destination = self.nodes[destination_str]
        self.add_edge(Edge(origin, destination))

    def remove_edge(self, edge):
        edge.get_origin().remove_edge(edge)
        self.edges.pop(str(edge), None)

    @dispatch(object, object)
    def get_edge(self, origin, destination):
        return self.edges[str(origin) + '_' + str(destination)]

    @dispatch(object)
    def get_edge(self, edge):
        return self.edges[str(edge)]

    def get_max_height(self):
        return self.max_height
    
    def get_edges(self):
        return self.edges

    def reset_support_of_nodes(self):
        for node in self.nodes.values():
            node.set_support(0)

    def reset_support_of_edges(self):
        for edge in self.edges.values():
            edge.set_edge_support(0)

    def reset_support_of_graph(self):
        self.reset_support_of_nodes()
        self.reset_support_of_edges()

    def reset_visited_nodes(self):
        for node in self.nodes.values():
            node.set_not_visited()

    def remove_cycles(self):
        visited_nodes = []
        self.reset_visited_nodes()
        graph_copy = deepcopy(self)
        for node in self.nodes.values():
            self.remove_cycles_util(graph_copy.get_node(str(node)), visited_nodes)

        for node in self.nodes.values():
            if not node.get_edges() and not self.terminal_nodes.__contains__(node):
                self.add_terminal_node(node)

    def remove_cycles_util(self, node, visited_nodes):
        if not node.is_visited():

            node.set_visited()
            visited_nodes.append(node)

            for edge in node.get_edges().values():
                destination = edge.get_destination()
                if not destination.is_visited():
                    if self.get_edge(edge.get_origin(), edge.get_destination()) is None:
                        continue
                    self.remove_cycles_util(destination, visited_nodes)
                elif destination in visited_nodes:
                    self.remove_edge(self.get_edge(edge.get_origin(), edge.get_destination()))

        if node in visited_nodes:
            visited_nodes.remove(node)

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


    def set_max_height(self, height):
        self.max_height = height
