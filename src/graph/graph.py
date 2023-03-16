import copy, joblib
from copy import deepcopy
from enum import Enum

from nltk.tokenize import regexp_tokenize
from src.filter_list import *
from src.graph.edge import Edge
from src.graph.node import Node
from src.logging import *
import networkx as nx
import matplotlib.pyplot as plt


# import pulp as pl


class SecType(Enum):
    IDLE = 0
    START = 1
    MIDDLE = 2
    TERMINAL = 3


class Graph:
    def __init__(self):
        self.trace_tokens = []
        self.nodes = {}
        self.root_nodes = {}
        self.terminal_nodes = {}
        self.edges = {}

        self.edge_support_info = {}  # Rubel added
        self.node_support_info = {}  # Rubel added

        # ## transitive causality
        # self.transitive_causality_table = {}

        self.msg_def_file_name = None
        self.trace_file_name = None

        self.exclude_list = []
        self.include_list = []

        self.filters = None
        self.bin_seq_rank = {}
        self.max_height = 8
        self.max_solutions = 10

        self.DEBUG = False

        self.window = False
        self.window_size = 1000

    def read_message_file(self, msg_def_file_name):
        try:
            f = open(msg_def_file_name, 'r')
        except IOError as e:
            print("Couldn't open file (%s)." % e)

        f1 = f.readlines()
        self.msg_def_file_name = msg_def_file_name

        root_node_strings = []

        is_root_definitions = False
        parse_state = SecType.IDLE
        for line in f1:
            tokens = regexp_tokenize(line, pattern=r'\s|[,:]', gaps=True)
            if not tokens:  # token list is empty
                continue
            if tokens[0] == '#':
                # is_root_definitions = not is_root_definitions
                # continue

                if parse_state == SecType.IDLE:
                    parse_state = SecType.START
                    log('start section \n', DEBUG)
                elif parse_state == SecType.START:
                    parse_state = SecType.MIDDLE
                    log('middle section \n', DEBUG)
                elif parse_state == SecType.MIDDLE:
                    parse_state = SecType.TERMINAL
                    log('end section \n', DEBUG)
                # elif parse_state == SecType.TERMINAL:
                continue

            # if is_root_definitions:
            #     root_node_strings.append(tokens[0])

            symbol_index = tokens[0]
            origin = tokens[1]
            destination = tokens[2]
            command = tokens[3]
            msg_type = tokens[4]
            message = tokens  # (origin, destination)

            if not self.has_node(symbol_index):
                node = Node(self, symbol_index, message, command, msg_type)
                self.add_node(node)
                # if symbol_index in root_node_strings:
                if parse_state == SecType.START:
                    self.add_root(node)
                    log('Add root node ' + str(symbol_index) + '\n', DEBUG)
                elif parse_state == SecType.TERMINAL:
                    self.add_terminal(node)
                    log('Add terminal node ' + str(symbol_index) + '\n', DEBUG)

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
        G = nx.DiGraph()
        for node_src in self.nodes.values():
            if self.is_terminal(node_src):  # skip if the source node is terminal
                continue
            for node_dest in self.nodes.values():
                if self.is_initial(node_dest) or node_src == node_dest:  # skip if the destination is initial
                    continue

                # print("Src = ", node_src, "  dest = ", node_dest)
                if self.causal(node_src, node_dest):
                    edge = Edge(self, node_src, node_dest)
                    node_src.add_edge(edge)
                    node_src.add_succ(node_dest)
                    self.add_edge(edge)
                    # print("An Edge: ", node_src, "_", node_dest)
                    G.add_edge(int(node_src.get_index()), int(node_dest.get_index()))

        print("\nTotal number of edges in the graph = ", G.number_of_edges())

        # plt.figure(figsize=(10, 8))
        # pos = nx.circular_layout(G)
        # # pos = nx.kamada_kawai_layout(G)
        # # pos = nx.spectral_layout(G)
        # # pos = nx.spring_layout(G, seed=1000)
        # node_options = {"node_color": "blue", "node_size": 60}
        # edge_options = {"width": .50, "alpha": .5, "edge_color": "black"}
        # node_label_options = {"font_size": 15, "font_color": "blue", "verticalalignment": "bottom", "horizontalalignment":"left"}
        # # nx.draw_networkx_nodes(G, pos, **node_options)
        # # nx.draw_networkx_edges(G, pos, **edge_options)
        # # nx.draw_networkx_labels(G, pos, **node_label_options)
        # nx.draw(G, pos, with_labels=True)
        # plt.show()
        # # exit()

            # Commented by Bardia for test
            # if not node_src.get_edges():
            #     self.add_terminal_node(node_src)
            #     log('Add new terminal node ' + str(node_src.get_index()) + '\n', DEBUG)
            # Commented by Bardia for test

            # for node_dest in self.nodes.values():
            #     if node_src == node_dest or self.is_root(node_dest):
            #         continue

            #     dest_message = node_dest.get_message()

            #     if src_message[1] == dest_message[0]:
            #         edge = Edge(self, node_src, node_dest)
            #         node_src.add_edge(edge)
            #         node_src.add_succ(node_dest)
            #         self.add_edge(edge)

            # if not node_src.get_edges():
            #     self.add_terminal_node(node_src)
            #     log('Add new terminal node '+str(node_src.get_index())+'\n', DEBUG)
        ################################################################################################################
        # myInitialNodes = []
        # myTerminalNodes = []
        # for aNode in G:
        #     if (G.in_degree(aNode) == 0):
        #         myInitialNodes.append(aNode)
        #         # print("Initial node = ", aNode)
        #     if (G.out_degree(aNode) == 0):
        #         myTerminalNodes.append(aNode)
        #         # print("Terminal node = ", aNode)
        # maxN = 0
        # print("Total number of edges in the graph = ", G.number_of_edges())
        # print("Initial nodes:")
        # for temp in myInitialNodes:
        #     if(int(str(temp))>maxN):
        #         maxN = int(str(temp))
        #     print(temp)
        # print("Terminal nodes:")
        # for temp in myTerminalNodes:
        #     # if(int(str(temp))>maxN):
        #     #     maxN = int(str(temp))
        #     print(temp)

        # print("Starting nodes = ", myInitialNodes)
        # print("Ending nodes = ", myTerminalNodes)
        # exit()
        # all_paths_sorted = [[] for x in range(maxN+1)]  # = []
        # startAndEnds     = [[] for x in range(maxN+1)]
        # for start_node in myInitialNodes:
        #     print("Starting node = ", start_node)
        #     for end_node in myTerminalNodes:
        #         print("Ending node = ", end_node)
        #         # counter = 0
        #         for path in nx.all_simple_paths(G, source=start_node, target=end_node):
        #             all_paths_sorted[start_node].append(path)
        #             # counter += 1
        #             # if counter%100 == 0:
        #             #     print(".", end="")
        #             # startAndEnds[start_node].append(end_node)
        #         print("")
        # for aPath in all_paths_sorted:
        #     print(aPath)
        # exit()
        ############################################################################################################

    # read a list of trace files for mining
    def read_trace_file_list(self, trace_file_list):
        for tf in trace_file_list:
            self.read_trace_file(tf)

    # Dr. Zheng's original Trace file reading code

    # def read_trace_file(self, trace_file):
    #     try:
    #         trace_fp = open(trace_file, 'r')
    #     except IOError as e:
    #         print("Couldn't open file (%s)." % e)
    #         return
    #
    #     self.trace_file_name = trace_file
    #
    #     raw_trace_list = trace_fp.readlines()
    #     for raw_trace in raw_trace_list:
    #         self.process_trace(raw_trace)
    #
    #     trace_fp.close()
    #
    #     for node in self.nodes.values():
    #         print(node.print_full() + " %d" % (node.get_support()))
    #
    #     print()
    #
    #     edges = self.get_edges().values()
    #     for edge in edges:
    #         src_node = edge.get_source()
    #         dest_node = edge.get_destination()
    #         print("%s, %s, %d, %d, %d" % (src_node.get_index(), dest_node.get_index(), src_node.get_support(), dest_node.get_support(), edge.get_support()))

    def read_trace_file(self, trace_file):
        traces = 0
        if '.jbl' in trace_file:
            file = joblib.load(trace_file)
            for i in file:
                print("\n****************** Trace number :", traces, "***********************\n")
                # if traces in [969]:  #969, 981, 1278, 1282
                #     self.process_trace(file[i])
                #     print(i, file[i])
                #     traces = traces + 1
                #     break
                # else:
                self.process_trace(file[i])
                traces = traces + 1

                # if traces > 2800:
                #     print(i, len(file[i]), file[i])
                #     break
        else:
            try:
                trace_fp = open(trace_file, 'r')
            except IOError as e:
                print("Couldn't open file (%s)." % e)
                return

            self.trace_file_name = trace_file

            raw_trace_list = trace_fp.readlines()
            for raw_trace in raw_trace_list:
                print("\n****************** Trace number :", traces, "***********************\n")
                self.process_trace(raw_trace)
                # self.process_trace("'1','2','1','2'")
                traces = traces + 1
                # if traces > 100000:
                #     break

            trace_fp.close()

    def process_trace(self, raw_trace):
        # @ Tables of messags from the trace
        node_table = {}

        # tokens = regexp_tokenize(self.original_trace, pattern=r'\s|[,:]', gaps=True)
        # tokens = raw_trace.split(' ')

        # rubel added this if-else clause for jbl files
        if isinstance(raw_trace, list):
            tokens = raw_trace
        else:
            tokens = raw_trace.split(' ')

        trace_size = 0
        pos_index = 0
        split_traces = {}

        for token in tokens:
            if token == '-2':
                break

            if token == '-1' or not self.has_node(token):
                continue
            # # status report on reading input trace
            # if (len(self.trace_tokens) - trace_size) % 100000 == 0:
            #     trace_size = len(self.trace_tokens)
            #     print('trace size now: ', trace_size)

            # @ Find the support for each node
            node = self.get_node(token)
            node.set_support(node.get_support() + 1)
            if node in node_table:
                node_table[node].append(pos_index)
            else:
                idx_list = [pos_index]
                node_table[node] = idx_list
            self.trace_tokens.append(token)

            # print(token + " %d" % node.get_support())

            pos_index += 1

        # ## spliting traces for individual interfaces
        #     src = node.get_source()
        #     dest = node.get_destination()
        #     interface = src+'_'+dest
        #     interface1 = dest+'_'+src
        #     if interface not in split_traces and interface1 not in split_traces:
        #         tr = []
        #         tr.append(token)
        #         split_traces[interface] = tr
        #     elif interface in split_traces:
        #         split_traces[interface].append(token)
        #     else:
        #         split_traces[interface1].append(token)

        #     if src in split_traces:
        #         split_traces[src].append(token)
        #     else:
        #         tr = []
        #         tr.append(token)
        #         split_traces[src] = tr

        #     if dest in split_traces:
        #         split_traces[dest].append(token)
        #     else:
        #         tr = []
        #         tr.append(token)
        #         split_traces[dest] = tr

        # for key in split_traces:
        #     tr = split_traces[key]
        #     s = ''
        #     for t in tr:
        #         s += t + ' '
        #     file1 = open('split-trace-'+key+'.txt', "w")
        #     file1.write(s)
        #     file1.close()
        # exit()
        # ## end of trace splitting

        # @ create pulp variable along with node creation
        # for node in self.nodes.values():
        #    node.set_pulp_var(pl.LpVariable(node.get_symbol_index(), node.get_support(), node.get_support()))

        # @ iteratively finding initial and terminal messages from the input trace
        # initial_msg_table  = {}
        # terminal_msg_table = {}
        #     new_initial_msg = self.find_ini
        # while True:tial_msg(node_table, initial_msg_table, terminal_msg_table)
        #     new_terminal_msg = self.find_terminal_msg(node_table, initial_msg_table, terminal_msg_table)
        #     if not new_initial_msg and not new_terminal_msg:
        #         break
        # @ It is possible that some TRUE initial and terminal messages may not be found
        # @ as they itnterleave in the trace in certain manner, eg. 15 16 16 15 where
        # @ 15 is terminal while 16 is initial.

        # self.add_initial_messages(initial_msg_table)
        # self.add_terminal_messages(terminal_msg_table)

        # roots = self.get_roots()
        # terminals = self.get_terminal_nodes()
        # for t in roots:
        #     print(t)
        # print('---------------\n')
        # for t in terminals:
        #     print(t)
        # input()
        # exit()

        # node = self.get_node('44')
        # self.add_terminal(node)
        # for node in node_table.keys():
        #     print(node.get_index(), ' ', node.get_support())

        ## Compute edge support wrt the input trace
        print('\nBinary sequence information:')
        edges = self.get_edges().values()

        # print("nodes: ", self.get_nodes().values())
        # nodes = node_table.keys()

        ########################### Rubel Added for faster reading ###################
        # keys = self.get_nodes()
        # # for key in keys:
        # #     print(str(key))
        # causalty = dict.fromkeys(keys, [])
        #
        # for key in causalty.keys():
        #     temp = []
        #     for edge in edges:
        #         src_node = edge.get_source()
        #         dest_node = edge.get_destination()
        #         if self.is_terminal(src_node) or self.is_initial(dest_node): continue
        #         if str(dest_node) not in self.trace_tokens or str(src_node) not in self.trace_tokens: continue
        #         if str(src_node) == key:
        #             temp.append(edge)
        #     if temp:
        #         causalty[key] = set(temp)
        #         self.find_edge_support2_0(key, list(causalty[key]), node_table)
        ########################### Rubel Added for faster reading ###################

        # print("Length of edges vector = ", len(edges), " length of trace tokens = ", len(self.trace_tokens))
        for edge in edges:
            src_node = edge.get_source()
            dest_node = edge.get_destination()
            if self.is_terminal(src_node) or self.is_initial(dest_node): continue
            # print(src_node, dest_node)
            if str(src_node) not in self.trace_tokens: continue
            # causalty[str(src_node)].append(str(dest_node))
            self.find_edge_support(edge, node_table)

        # for key in causalty:
        #     print(key,set(causalty[key]))

        # edge.set_pulp_var(pl.LpVariable(edge.get_id(), 0, edge.get_support()))

        ## For each edge, compute its direct support count --> potentially more efficient model finding
        """ for edge in edges:
            sup_pos = edge.get_support_list()
            if sup_pos is None: continue
            if edge.get_fconf() != 1 or edge.get_bconf() != 1: continue
            direct_sup = 0
            for (head_idx, tail_idx) in sup_pos:
                seq = []
                s = self.find_edge_direct_support(head_idx, tail_idx)
                if s == True:
                    direct_sup += 1
            edge.set_direct_support(direct_sup) """

    #################################

    ## for argument 'edge', find its support as a list of index pairs, such that
    ## each pair specifies positions of src/dest of the 'edge' in the trace
    def find_edge_support2_0(self, root, childs, node_table):

        src_node = childs[0].get_source()
        # dest_idx_list = node_table[dest_node]
        src_idx_list = node_table[src_node]

        for edge in childs:
            # if child not in node_table: return 0
            dest_node = edge.get_destination()
            try:
                dest_idx_list = node_table[dest_node]
            except KeyError:
                print("Not found: ", str(dest_node))
                break
            src_head = 0
            dest_head = 0
            # support = 0
            support = []
            # if (self.window):
            #
            #     # Rubel added for window slicing code
            #     src_idx = src_idx_list.copy()
            #     dest_idx = dest_idx_list.copy()
            #
            #     # print(src_idx)
            #     # print(dest_idx)
            #
            #     # breakpoint()
            #
            #     while src_idx and dest_idx:
            #         if src_idx[0] > dest_idx[0]:
            #             dest_idx.pop(0)
            #             continue
            #
            #         if src_idx[0] + self.window_size >= dest_idx[0]:
            #             # print("Ping!!!")
            #             support.append((src_idx.pop(0), dest_idx.pop(0)))
            #             continue
            #
            #         if src_idx[0] + self.window_size < dest_idx[0]:
            #             src_idx.pop(0)
            #             continue
            #
            #     edge.set_support(edge.get_support_list() + support)

            # else:
            while True:
                if src_head == len(src_idx_list) or dest_head == len(dest_idx_list):
                    break
                src_idx = src_idx_list[src_head]
                dest_idx = dest_idx_list[dest_head]
                if src_idx < dest_idx:
                    # support += 1
                    support.append((src_idx, dest_idx))
                    src_head += 1
                    dest_head += 1
                elif src_idx_list[src_head] >= dest_idx_list[dest_head]:
                    dest_head += 1

            # edge = (self,root , child)
            edge.set_support(edge.get_support_list() + support)

            if True:  # edge.get_fconf()==1 and edge.get_bconf()==1:
                id = "{0:<10}".format(str(edge.get_id()))
                sup = "{0:<6}".format(str(edge.get_support()))
                fconf = "{0:<6}".format(str(round(edge.get_fconf(), 2)))
                bconf = "{0:<6}".format(str(round(edge.get_bconf(), 2)))
                hconf = "{0:<6}".format(str(round(edge.get_hconf(), 2)))
                print(id, ' ', sup, ' ', fconf, ' ', bconf, ' ', hconf)

        # print("done")
        # return len(support)

    ## for argument 'edge', find its support as a list of index pairs, such that
    ## each pair specifies positions of src/dest of the 'edge' in the trace
    def find_edge_support(self, edge, node_table):
        src_node = edge.get_source()
        dest_node = edge.get_destination()
        # print(src_node, dest_node)
        if src_node not in node_table or dest_node not in node_table:
            return 0
        src_idx_list = node_table[src_node]
        dest_idx_list = node_table[dest_node]
        # print ("src node = ", src_node, ", dest node = ", dest_node, ", src list = ", src_idx_list, ", dest list = ", dest_idx_list)
        # print("Node table size = ", len(node_table), " src index size = ", len(src_idx_list), " dest index size = ", len(dest_idx_list))

        src_head = 0
        dest_head = 0
        # support = 0
        support = []

        if (self.window):
            while True:
                if src_head == len(src_idx_list) or dest_head == len(dest_idx_list):
                    break
                src_idx = src_idx_list[src_head]
                dest_idx = dest_idx_list[dest_head]
                # print(src_idx, dest_idx)

                if src_idx > dest_idx:
                    # print ("1 - src head = ", src_head, ", dest head = ", dest_head)
                    dest_head += 1
                    # print("dest_head", dest_head)
                    continue
                if (src_idx + self.window_size) >= dest_idx:
                    # print ("2 - src head = ", src_head, ", dest head = ", dest_head)
                    _ = (src_idx, dest_idx)
                    # print(_)
                    support.append(_)
                    src_head += 1
                    dest_head += 1
                    continue

                if (src_idx + self.window_size) < dest_idx:
                    src_head += 1
                    # print("src_head", src_head)
                    continue
                # elif src_idx_list[src_head] >= dest_idx_list[dest_head]:
                #     dest_head += 1

            # # Rubel added for window slicing code
            # src_idx = src_idx_list.copy()
            # dest_idx = dest_idx_list.copy()
            #
            # # while src_idx and dest_idx:
            # while True:
            #     if len(src_idx) == 0 or len(dest_idx) == 0:
            #         break
            #     if src_idx[0] > dest_idx[0]:
            #         dest_idx.pop(0)
            #         continue
            #
            #     if src_idx[0] + self.window_size >= dest_idx[0]:
            #         _ = (src_idx.pop(0), dest_idx.pop(0))
            #         # print(_)
            #         support.append(_)
            #         continue
            #
            #     if src_idx[0] + self.window_size < dest_idx[0]:
            #         src_idx.pop(0)
            #         continue

            edge.set_support(edge.get_support_list() + support)

        else:
            while True:
                if src_head == len(src_idx_list) or dest_head == len(dest_idx_list):
                    break
                src_idx = src_idx_list[src_head]
                dest_idx = dest_idx_list[dest_head]
                if src_idx < dest_idx:
                    # support += 1
                    support.append((src_idx, dest_idx))
                    src_head += 1
                    dest_head += 1
                elif src_idx_list[src_head] >= dest_idx_list[dest_head]:
                    dest_head += 1
            edge.set_support(edge.get_support_list() + support)

        if True:  # edge.get_fconf()==1 and edge.get_bconf()==1:
            id = "{0:<10}".format(str(edge.get_id()))
            sup = "{0:<6}".format(str(edge.get_support()))
            fconf = "{0:<6}".format(str(round(edge.get_fconf(), 2)))
            bconf = "{0:<6}".format(str(round(edge.get_bconf(), 2)))
            hconf = "{0:<6}".format(str(round(edge.get_hconf(), 2)))
            print(id, ' ', sup, ' ', fconf, ' ', bconf, ' ', hconf)
        return len(support)

    ##################################

    def find_initial_msg(self, node_table, initial_msg_table, terminal_msg_table):
        new_initial_msg = False
        for this_msg in node_table:
            if this_msg in initial_msg_table: continue
            this_head = node_table[this_msg][0]
            causal = False
            for other_msg in node_table:
                if other_msg is this_msg or other_msg in terminal_msg_table: continue
                other_pos_list = node_table[other_msg]
                for other_pos in other_pos_list:
                    if other_pos >= this_head: break
                    if self.causal(other_msg, this_msg):
                        causal = True
                        break
                if causal: break
            if not causal:
                new_initial_msg = True
                initial_msg_table[this_msg] = ''
                print('found init msg: ', this_msg)
        # print("Initial: ",new_initial_msg)
        return new_initial_msg

    ## for each message (this_msg), check its final index (this_final_index) against
    ## the final indices (other_final_index) of other messages (other_msg)
    ## If no other message exists such that other_final_index > this_final_index, and
    ## causal(other_msg, this_msg), then this message is terminal
    def find_terminal_msg(self, node_table, initial_msg_table, terminal_msg_table):
        new_terminal_msg = False
        for this_msg in node_table:
            if this_msg in terminal_msg_table: continue
            this_final_index = node_table[this_msg][-1]
            causal = False
            for other_msg in node_table:
                if other_msg is this_msg or other_msg in initial_msg_table: continue
                # if other_msg.get_index() == '0': input('found initial 0')
                if other_msg.get_index() == '0': continue
                other_final_index = node_table[other_msg][-1]
                if other_final_index <= this_final_index: continue
                if self.causal(this_msg, other_msg):
                    causal = True
                    break
                # other_pos_list = node_table[other_msg]
                # for other_pos in reversed(other_pos_list):
                #     if other_pos <= this_tail: break
                #     if self.causal(this_msg, other_msg):
                #         # if this_msg.get_index() == '35':
                #         #     print(other_msg, ' ', other_pos, ' ', this_tail)
                #         causal = True
                #         break

                # if causal: break
            if not causal:
                new_terminal_msg = True
                terminal_msg_table[this_msg] = ''
                print('found terminal msg: ', this_msg)
        # print("Terminal: ",new_terminal_msg)
        return new_terminal_msg

    # ## Computer transitive causality using edge support.
    # def find_transitive_causality(self):
    #     matrix = {}
    #     nodes = self.get_nodes().values()
    #     for m in nodes:
    #         row = {}
    #         for n in nodes:
    #             row[n] = 0
    #         matrix[m] = row

    #     for (k, l) in self.transitive_causality_table.keys():
    #         matrix[k][l] = 1
    #         print(k.get_index(), ',', l.get_index())

    #     for i in nodes:
    #         if self.is_terminal(i): continue
    #         for k in nodes:
    #             if i == k or self.is_initial(k) or self.is_terminal(k) or matrix[i][k] == 0: continue
    #             for j in nodes:
    #                 if k == j or i == j or self.is_initial(j) or matrix[k][j] == 0: continue
    #                 matrix[i][j] = 1
    #                 self.transitive_causality_table[(i,j)] = ''

    #     # for (m, n) in self.transitive_causality_table:
    #     #     print(m.get_index(), ' ', n.get_index())

    # @ test causality relation between two messages.
    # @ the condition depends on source/destination matching, and relations between messages types
    # @ if there are more message types than just 'req' or 'resp', this function needs to update
    def causal(self, msg_1, msg_2):
        if msg_1.get_destination() != msg_2.get_source():
            # print("First If")
            return False

        if msg_1.get_source() == msg_2.get_destination():
            if msg_1.get_type().lower() == 'resp':
                # print("Second If")
                return False
            if msg_1.get_type().lower() == 'req':
                # print("Third If")
                return (msg_2.get_type().lower() == 'resp')
        elif msg_1.get_type().lower() == 'req':
            # print("Forth If")
            return (msg_2.get_type().lower() != 'resp')

        return True
        raise ValueError("Wrong message type:", msg_1.get_message(), ' ', msg_2.get_message())

    ## An approximate function to check if there is any direct support for an edge delimited by head_idx/tail_idx
    ## Returns True/False
    def find_edge_direct_support(self, head_idx, tail_idx):
        if (head_idx + 1) == tail_idx:
            return True
        for i in range(head_idx, tail_idx):
            if (self.is_initial(self.trace_tokens[i]) or self.is_terminal(self.trace_tokens[i])):
                continue
            else:
                return False
        return True

    ## From a trace segment delimited by head_idx and tail_idx, find a sequence of edges
    ## that connects nodes at head_idx and tail_idx, stored in argument 'seq'
    # def find_causal_seq(self, head_idx, tail_idx):
    #     head_node = self.get_node(self.trace_tokens[head_idx])
    #     head_outgoing_edges = head_node.get_outgoing_edges()
    #     for og_edge in head_outgoing_edges:
    #         if og_edge.get_support() == 0: continue
    #         next_node = og_edge.get_destination()
    #         i = head_idx+1
    #         found_next_node = False
    #         for i in range(head_idx+1, tail_idx+1):
    #             if i < tail_idx and (self.is_initial(self.trace_tokens[i]) or self.is_terminal(self.trace_tokens[i])):
    #                 continue
    #             if next_node.get_index() == self.trace_tokens[i]:
    #                 found_next_node = True
    #                 break
    #         if found_next_node == False:
    #             continue
    #         # print(next_node.get_index(), ' ', found_next_node, ' ', i)
    #         # input()
    #         if i < tail_idx:
    #             s = self.find_causal_seq(i, tail_idx)
    #             if s == True: return True
    #         else:
    #             return True
    #     return False

    # @Author: Hao Zheng
    # @Function: input a list of binary sequences ranked by their confidence measures
    def read_bin_seq_ranking(self, rank_filename):
        try:
            rank_fp = open(rank_filename, 'r')
        except IOError as e:
            print("Couldn't open file (%s)." % e)
            return

        lines = rank_fp.readlines()
        for line in lines:
            line = line.split()  # line.rstrip("\n")
            src = line[0]
            dest = line[1]
            edge = self.get_edge(src, dest)
            if edge is not None:
                edge.set_ranking(int(line[4]))
                log('@%s:%d: set edge ranking %s %d\n' % (whoami(), line_numb(), edge.get_id(), edge.get_ranking()),
                    DEBUG)

    # @Author: Hao Zheng
    # @Function: input a list of sequences that should be excluded from mined patterns
    def read_filters(self, filters_filename):
        self.filters = filter_list(filters_filename)

        # try:
        #     ignore_f = open(filters_filename, 'r')
        # except IOError as e:
        #     print("Couldn't open file (%s)." % e)
        #     return

        # lines = ignore_f.readlines()
        # INPUT_IDLE = 0
        # INPUT_EXCLUDE = 1
        # INPUT_INCLUDE = 2
        # parse_state = INPUT_IDLE
        # for line in lines:
        #     line = line.rstrip("\n")
        #     if line[0] == '#':
        #         if line.lower() == '#include':
        #             parse_state = INPUT_INCLUDE
        #         elif line.lower() == '#exclude':
        #             parse_state = INPUT_EXCLUDE
        #         else:
        #             log('Unrecognized section %s in filters file %s' %(line, filters_filename))
        #             return
        #         continue

        #     if parse_state == INPUT_EXCLUDE:
        #         self.exclude_list.append(line.split())
        #     elif parse_state == INPUT_INCLUDE:
        #         self.include_list.append(line.split())

        # log('filters are empty', WARN) if len(self.include_list)==0 and len(self.exclude_list)==0 else None

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

        path_index = []
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
            if self.checkList(path_node, nxt_node) == False:  # nxt_node not in path_node:
                # if len(path_node) == height-1:
                #     path_index.append(nxt_node.get_symbol_index())
                #     print(path_index)
                #     path_index.pop(-1)

                if len(path_node) < self.max_height - 1:
                    path_node.append(nxt_node)
                    path_succ.append(copy.copy(self.nodes[nxt_node.get_symbol_index()].get_succ_nodes()))
                    path_index.append(nxt_node.get_symbol_index())
                # if nxt_node not in mono_cg:
                mono_cg[nxt_node] = []
                nxt_node.set_depth(head_node.get_depth() + 1)
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
        # print('level ', level, "  ", len(cg[root_node]))
        for node in cg[root_node]:
            path.append(node.get_symbol_index())
            print(path)
            self.print_path(cg, node, path, level + 1)
            path.pop(-1)

    def generate_dags(self):
        dags = []
        traversal_queue = []

        for root in self.root_nodes.values():
            # self.reset_visited_nodes()
            path = []
            dag = Graph()

            ## for the new code
            # root_copy = deepcopy(root)
            # dag.add_root(root_copy)
            # dag.add_node(root_copy)
            # path.append(root.get_index())
            # self.generate_dags_util(dag, path)
            # dag.generate_edges()
            # dag.remove_cycles()
            # dags.append(dag)

            traversal_queue.append(root)
            self.generate_dags_util(dag, traversal_queue)
            dag.generate_edges()
            dag.remove_cycles()
            dags.append(dag)

            print('created dag for root ', root.get_index())

        return dags

    # # A recursive function that generates a rooted DAG up to max_height
    # def generate_dags_util(self, dag, path):
    #     head_index = path[-1]
    #     head_node = self.get_node(head_index)
    #     if len(path) == self.max_height or self.is_terminal(self.get_node(head_index)):
    #         print('pop', path)
    #         print(path.pop(-1))
    #         return

    #     head_node_copy = dag.get_node(head_index)
    #     for edge in head_node.get_edges().values():
    #         succ_node = edge.get_destination()
    #         succ_index = succ_node.get_index()
    #         print(head_index, " --> ", succ_index)

    #         if succ_index not in path:
    #             # create copy of the edge for head_node
    #             succ_node_copy = deepcopy(succ_node)
    #             dag.add_node(succ_node_copy)
    #             edge_copy = Edge(head_node_copy, succ_node_copy)
    #             edge_copy.set_edge_support(edge.get_edge_support())
    #             head_node_copy.add_edge(edge_copy)
    #             head_node_copy.add_succ(succ_node_copy)
    #             dag.add_edge(edge_copy)
    #             dag.add_node(succ_node_copy)
    #             print('add edge ', edge_copy.get_origin(), ' ', edge_copy.get_destination(), ' ', edge_copy.get_support())
    #             if self.is_terminal(succ_node):
    #                 dag.add_terminal(succ_node_copy)
    #             # extend the path and recurse
    #             path.append(succ_index)
    #             self.generate_dags_util(dag, path)
    #     print('pop', path)
    #     print(path.pop(-1))

    # ************ original definition.    ****************************
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
        try:
            return self.nodes[symbol_index]
        except IndexError as e:
            print('node ', symbol_index, ' does not exist!')
            print(e)
            exit()

    def get_nodes(self, msg_pattern=[]):
        if len(msg_pattern) == 0:
            return self.nodes

        src = msg_pattern[0]
        dest = msg_pattern[1]
        cmd = msg_pattern[2]
        ty = msg_pattern[3]
        node_list = []
        for node in self.nodes.values():
            if src != '-' and src != node.get_source():
                continue
            if dest != '-' and dest != node.get_destination():
                continue
            if cmd != '-' and cmd != node.get_command():
                continue
            if ty != '-' and ty != node.get_type():
                continue

            node_list.append(node)
        return node_list

    def remove_node(self, node):
        self.nodes.pop(str(node), None)

    def has_node(self, node):
        return node in self.nodes.values() or str(node) in self.nodes

    # @ utilities functions for root nodes
    def add_initial_messages(self, initial_msg_table):
        # self.root_nodes = {}
        for r in initial_msg_table.keys():
            self.add_root(r)

    def add_root(self, root):
        self.root_nodes[str(root)] = root

    def remove_root(self, root):
        self.root_nodes.pop(str(root), None)

    def is_root(self, node):
        return node in self.root_nodes.values() or str(node) in self.root_nodes

    def is_initial(self, node):
        return node in self.root_nodes.values() or str(node) in self.root_nodes

    def get_roots(self):
        return self.root_nodes

    # @-----------------------------------

    # @ Utility functions fro terminal nodes
    def add_terminal_messages(self, terminal_msg_table):
        # self.terminal_nodes = {}
        for t in terminal_msg_table:
            self.add_terminal(t)

    def add_terminal(self, node):
        self.terminal_nodes[str(node)] = node

    def add_terminal_node(self, node):
        self.terminal_nodes[str(node)] = node

    def is_terminal(self, node):
        return node in self.terminal_nodes.values() or str(node) in self.terminal_nodes

    def is_terminal_node(self, node):
        return node in self.terminal_nodes.values() or str(node) in self.terminal_nodes

    def get_terminal_nodes(self):
        return self.terminal_nodes

    # @----------------------------------------

    def get_exclude_list(self):
        return self.exclude_list

    def get_include_list(self):
        return self.include_list

    def add_edge(self, edge):
        self.edges[edge.get_id()] = edge

    # @dispatch(object)
    # def add_edge(self, edge):
    #     edge.get_source().add_edge(edge)
    #     self.edges[str(edge)] = edge

    # @dispatch(str, str)
    # def add_edge(self, origin_str, destination_str):
    #     origin = self.nodes[origin_str]
    #     destination = self.nodes[destination_str]
    #     self.add_edge(Edge(origin, destination))

    def remove_edge(self, edge):
        edge.get_origin().remove_edge(edge)
        self.edges.pop(str(edge), None)

    def get_edge(self, src, dest):
        id = str(src) + '_' + str(dest)
        if id in self.edges.keys():
            return self.edges[id]
        return None

    # @dispatch(object, object)
    # def get_edge(self, origin, destination):
    #     return self.edges[str(origin) + '_' + str(destination)]

    # @dispatch(object)
    # def get_edge(self, edge):
    #     return self.edges[str(edge)]

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

            self.node_support_info[node.get_symbol_index()] = node.get_support()  # Rubel Added

            total_node_support += node.get_support()
            print(text)
        print()
        print('Total Node Support: %d' % total_node_support)
        print()
        # joblib.dump(self.node_support_info, './node_support.jbl')

    def print_edges(self):
        print('Edges:')
        print()
        for node in self.nodes.values():
            print('     Origin: %s' % node.get_symbol_index())

            for edge in node.get_edges().values():
                # print('        ' + str(edge) + ' with edge support of ' + str(edge.get_support_pos())) origina implementation
                print('        ' + str(edge) + ' with edge support of ' + str(edge.get_support()))  # Rubel Edits
                self.edge_support_info[str(edge)] = str(edge.get_support())

            print()
        # joblib.dump(self.edge_support_info,'./edge_support.jbl')

    def print_graph(self):
        self.print_nodes()
        self.print_edges()

    def set_max_height(self, height):
        self.max_height = height

    def set_max_solutions(self, sols):
        self.max_solutions = sols

    def get_max_solutions(self):
        return self.max_solutions

    def get_msg_def_file_name(self):
        return self.msg_def_file_name

    def get_trace_file_name(self):
        return self.trace_file_name
