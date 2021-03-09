from nltk.tokenize import regexp_tokenize
from src.logging import *


class GraphAnnotator:

    def __init__(self, original_trace, graph):
        self.graph = graph
        self.original_trace = original_trace
        self.trace_tokens = []
        self.annotate()

    def annotate(self):
        node_table = {}

        # tokens = regexp_tokenize(self.original_trace, pattern=r'\s|[,:]', gaps=True)
        tokens = self.original_trace.split(' ')
        
        trace_size = 0
        pos_index = 0
        for token in tokens:
            if token == '-2':
                break

            if token == '-1' or not self.graph.has_node(token):
                continue

            if (len(self.trace_tokens) - trace_size) % 100000 == 0:
                trace_size = len(self.trace_tokens)
                print('trace size now: ', trace_size)

            node = self.graph.get_node(token)
            node.set_support(node.get_support() + 1)
            if node in node_table:
                node_table[node].append(pos_index)
            else:
                idx_list = [pos_index]
                node_table[node] = idx_list 
            self.trace_tokens.append(token)

            pos_index += 1

        #@ iteratively finding initial and terminal messages from the input trace
        initial_msg_table = {}
        terminal_msg_table = {}
        while True:
            new_initial_msg = self.find_initial_msg(node_table, initial_msg_table, terminal_msg_table)
            new_terminal_msg = self.find_terminal_msg(node_table, initial_msg_table, terminal_msg_table)
            if not new_initial_msg and not new_terminal_msg:
                break
        #@ It is possible that some TRUE initial and terminal messages may not be found
        #@ as they itnterleave in the trace in certain manner, eg. 15 16 16 15 where 
        #@ 15 is terminal while 16 is initial. 

        
        self.graph.add_initial_messages(initial_msg_table)
        self.graph.add_terminal_messages(terminal_msg_table)
        
        # for node in node_table.keys():
        #     print(node.get_index(), ' ', len(node_table[node]))
        
        edges = self.graph.get_edges().values()
        for edge in edges:
            if edge.get_source() in terminal_msg_table.keys(): continue
            self.find_edge_support(edge, node_table)
            # self.annotate_edge(edge)
            print(edge, ' ', edge.get_support())

            
       
    def find_edge_support(self, edge, node_table):
        src_node = edge.get_source()
        dest_node = edge.get_destination()
        if src_node not in node_table or dest_node not in node_table:
            return
        src_idx_list = node_table[src_node]
        dest_idx_list = node_table[dest_node]
        src_head = 0
        dest_head = 0
        support = 0
        while True:
            if src_head == len(src_idx_list) or dest_head == len(dest_idx_list):
                break
            if src_idx_list[src_head] < dest_idx_list[dest_head]:
                support += 1
                src_head += 1
                dest_head += 1
            elif src_idx_list[src_head] >= dest_idx_list[dest_head]:
                dest_head += 1
        edge.set_support(support)
        # if support > 0: print(edge, ' ', support)


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
                # print('found init msg: ', this_msg)
        return new_initial_msg
                    

    def find_terminal_msg(self, node_table, initial_msg_table, terminal_msg_table):
        new_terminal_msg = False
        for this_msg in node_table:
            if this_msg in terminal_msg_table: continue
            this_tail = node_table[this_msg][-1]
            causal = False
            for other_msg in node_table:
                if other_msg is this_msg or other_msg in initial_msg_table: continue
                other_pos_list = node_table[other_msg]
                for other_pos in reversed(other_pos_list):
                    if other_pos <= this_tail: break
                    if self.causal(this_msg, other_msg):
                        if this_msg.get_index() == '35':
                            print(other_msg, ' ', other_pos, ' ', this_tail)
                        causal = True
                        break
                
                if causal: break
            if not causal:
                new_terminal_msg = True
                terminal_msg_table[this_msg] = ''
                # print('found terminal msg: ', this_msg)
        return new_terminal_msg
        
                
    #@ test causality relation between two messages.
    def causal(self, msg_1, msg_2):
        return msg_1.get_destination() == msg_2.get_source()

    def annotate_edge(self, edge):
        instances = 0
        source_symbol_index = edge.get_source().get_symbol_index()

        for token in self.trace_tokens:
            if not token == '-1':
                if source_symbol_index == token:
                    instances += 1
                elif str(edge) == source_symbol_index + '_' + token and instances > 0:
                    edge.set_edge_support(edge.get_edge_support() + 1)
                    instances -= 1
                    








                    