import copy
from src.logging import *
from z3 import *

#@ Input: a model of constraint problem generated from the annotated CG.
#@ Output: all possible sequences of nodes allowed by the input model
#@ Output: Z3 constraints that define the impossible sequences.
#@
class sequence_generator:
    def __init__(self, graph, model):
        self.graph = graph
        self.model = model
        self.noncycle_constraint_list = []
        self.sequence_list = []
        self.extract_sequences()

    # Extract all sequneces of nodes) from a solution
    def extract_sequences(self):
        all_flows = []
        sol_edges = {}
        
        edges = self.graph.get_edges().values()

        #@ find all edges that have non-zero support in a solution
        for edge in edges:
            edge_z3var = edge.get_z3var()
            if not len(self.model) or self.model[edge_z3var].as_long() == 0: 
                continue
            src_node = edge.get_source()
            dest_node = edge.get_destination() 
            if src_node in sol_edges:
                sol_edges[src_node].append(dest_node)
            else:
                sol_edges[src_node] = [dest_node]
        
        # #@ TEST: show the non-zero support of edges in the model
        # for e in sol_edges.keys():
        #     print(e, ' : ', end='')
        #     for f in sol_edges[e]:
        #         print(f, ', ', end='')
        #     print()
        # input('@ seqeunce_gen:42: ')
        # #@------------------------
        # 
        roots = self.graph.get_roots()

        #@ find all flows starting with every root node
        seq_list = []
        for root in roots.values():
            if root not in sol_edges:  # check if there is a flow starting from this root
                continue
            seq = [root]
            seq_list.append(seq)
        
        #@ extend the initial seqeunces following the edges in sol_edges recursively
        self.sequence_list = self.extract_sequences_recursive(sol_edges, seq_list, 1)
        
    #@ Recursively extend the sequences in seq_list with edges in 'edges' following three conditions
    #@ Consition 1: no duplicate node in any sequences
    #@ Condition 2: the length of a sequence is up to the 'max_height' in the CG
    #@ Condition 3: all sequences end with a terminal node in the CG
    def extract_sequences_recursive(self, edges, seq_list, depth):
        #@ check condition 2
        if depth == self.graph.get_max_height():
            return seq_list

        #@ extend sequences
        new_seq_list = []
        for seq in seq_list:
            last_node = seq[-1]
            
            # if last_node in terminals:
            if self.graph.is_terminal(last_node):
                new_seq_list.append(seq)
                continue

            # if last_node not in edges:  # check if last_node has succ in edges
            #     new_flow_list.append(flow)
            #     continue
            # go_deeper = True
            succ_list = edges[last_node] if last_node in edges.keys() else []
            for node in succ_list:
                #@ check condition 1:  no duplication messages in a flow
                if node in seq:
                    self.creaet_noncycle_constraints(seq, node)
                    continue
                #@ check condition 3: do not include a flow that does not end with a terminal
                elif (not self.graph.is_terminal(node)) and (depth+1 == self.graph.get_max_height()):
                    continue    
                    
                seq_copy = seq.copy()
                seq_copy.append(node)
                new_seq_list.append(seq_copy)                
        
        return self.extract_sequences_recursive(edges, new_seq_list, depth+1)

        # if go_deeper == True:  
        #     return self.extract_flows_recursive(edges, new_flow_list, terminals, depth+1)
        # else:
        #     return new_flow_list


    def print_sequences(self):
        for seq in self.sequence_list:
            for node in seq:
                print(node.get_index(), end=' ')
            print()
        log('@sequence_extractor:print_sequences:108 Total number of sequences = ' + str(len(self.sequence_list)) + '\n', INFO)

    

    #@ Input: a sequence 'seq', and a 'node' that has a duplicate in 'seq'
    #@ Output: z3 constraints restricting that if supports of edges in 'seq'
    #@ are >0, then the support of the end of 'seq' to the 'node' is ==0 
    def creaet_noncycle_constraints(self, seq, new_node):
        # for n in seq:
        #     print(n, ' ', end='')
        # print(': ', new_node)

        seq_copy = seq.copy()
        while True:
            if seq_copy[0] == new_node:
                break
            seq_copy.pop(0)

        constr = True
        idx = 0
        while idx < len(seq_copy)-1:
            edge = self.graph.get_edge(seq_copy[idx], seq_copy[idx+1])
            edge_z3var = edge.get_z3var()
            if self.model[edge_z3var].as_long() == 0:
                raise ValueError("edge has zero support")
            constr = And(constr, edge_z3var > 0)
            idx += 1
        
        last_node = seq_copy[-1]
        new_edge = self.graph.get_edge(last_node, new_node)
        if new_edge is None:
            raise ValueError("new_edge is None")
        new_edge_z3var = new_edge.get_z3var()
        new_constr = simplify(Implies(constr, new_edge_z3var==0))
        if new_constr not in self.noncycle_constraint_list:
            self.noncycle_constraint_list.append(simplify(new_constr))


    #@ return sequence list
    def get_sequence_list(self):
        return self.sequence_list

    #@ return the feasiable_constraint
    def get_noncycle_constraints(self):
        return self.noncycle_constraint_list

    #@ utility function
    def print_noncycle_constraints(self):
        for c in self.noncycle_constraint_list:
            print(c)
        print('--------------')






