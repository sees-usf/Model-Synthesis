import time
import os

from src.logging import *
from plantweb.render import render


class SequencePrinter:
    def __init__(self, solutions, abs_path, directory_name, graph):
        self.solutions = solutions #self.prepare_solutions(solutions)
        self.abs_path = 'solutions '+ time.asctime( time.localtime(time.time()) )#abs_path + '\\solutions\\'
        #self.directory_name = directory_name
        self.graph = graph
        self.list_of_sequences = []
        self.list_of_flows = []
        self.max_height = graph.get_max_height()
        self.DEBUG = False
        self.INFO = True

    def generate_solutions(self):
        self.extract_all_flows()
        return
        self.divide_solution_sequences()
        self.generate_plantuml_pngs()
        self.generate_solution_files()

    def extract_all_flows(self):
        sol_index = 1
        for solution in self.solutions:
            seq_list = self.extract_sequences(solution)
            sol_path = os.path.join(self.abs_path, 'Solution-' + str(sol_index))
            os.makedirs(sol_path, exist_ok=True)
            # write solution to the solution directory
            sol_file = os.path.join(sol_path, 'sol-sequences.txt')
            f = open(sol_file, 'w')
            for s in seq_list:
                f.write(str(s))
                f.write('\n')                
            f.close()
         
            flow_list = self.extract_flows(solution)
            log("outputting solution " + str(sol_index), DEBUG)
            self.flows_2_plantuml(flow_list, solution, sol_index)
            sol_index += 1


    def extract_flows(self, solution):
        all_flows = []
        sol_edges = {}
        nodes = self.graph.get_nodes()
        edges = self.graph.get_edges().values()

        for edge in edges:
            edge_z3var = edge.get_z3var()
            if solution[edge_z3var].as_long() == 0: 
                continue
            src_node = edge.get_source()
            dest_node = edge.get_destination() 

            if src_node in sol_edges:
                sol_edges[src_node].append(dest_node)
            else:
                sol_edges[src_node] = [dest_node]
        
        roots = self.graph.get_roots()
        terminals = self.graph.get_terminal_nodes()

        flow_list = []
        for root in roots.values():
            flow = [root]
            flow_list.append(flow)
        
        flow_list = self.get_flows(sol_edges, flow_list, terminals, 1)
        return flow_list


    def get_flows(self, edges, flow_list, terminals, depth):
        if depth == self.max_height:
            return flow_list

        new_flow_list = []
        go_deeper = False
        for flow in flow_list:
            last_node = flow[-1]
            
            if last_node in terminals:
                new_flow_list.append(flow)
                continue

            if last_node not in edges:
                new_flow_list.append(flow)
                continue
            go_deeper = True
                        
            succ_list = edges[last_node]
            for node in succ_list:
                if node in flow:  # no duplication messages in a flow
                    continue
                # do not include a flow that does not end with a terminal
                elif (node not in terminals) and (depth+1 == self.max_height):
                    continue

                flow_copy = flow.copy()
                flow_copy.append(node)
                new_flow_list.append(flow_copy)

        if go_deeper == True:  
            return self.get_flows(edges, new_flow_list, terminals, depth+1)
        else:
            return new_flow_list
        

    def divide_solution_sequences(self):
        for solution in self.solutions:
            self.extract_pattern(solution)

            sequences = []
            sequence = []
            graph_id = str(solution[0][0])[0]
            for (edge_var, value) in solution:
                if graph_id != str(edge_var)[0]:
                    graph_id = str(edge_var)[0]
                    sequences.append(list(sequence))
                    sequence.clear()
                if self.graph.is_root(self.graph.get_edge(str(edge_var)[1:]).get_origin()) \
                        and self.graph.is_terminal_node(self.graph.get_edge(str(edge_var)[1:]).get_destination()):
                    sequences.append([str(edge_var)[1:]])
                else:
                    sequence.append(str(edge_var)[1:])
            if sequence:
                sequences.append(sequence)
            self.list_of_sequences.append(sequences)
            
        self.extract_flows_from_sequences()

    def extract_flows_from_sequences(self):
        for sequences in self.list_of_sequences:
            all_sequence_flows = []
            for sequence in sequences:
                sequence_flows = self.extract_flow_from_sequence(sequence)
                all_sequence_flows.append(sequence_flows)
            self.list_of_flows.append(all_sequence_flows)

    def extract_flow_from_sequence(self, sequence):
        starting_edge = None

        for edge_id in sequence:
            edge = self.graph.get_edge(edge_id)
            if self.graph.is_root(edge.get_origin()):
                starting_edge = edge
                break

        flows = [[starting_edge.get_origin().get_symbol_index(), starting_edge.get_destination().get_symbol_index()]]
        self.flow_extract_util(sequence, starting_edge, flows, 1)

        return flows

    def flow_extract_util(self, sequence, edge, flows, depth):
        destination = edge.get_destination()

        if self.graph.is_terminal_node(destination):
            return

        if len(flows) > 0 and len(flows[-1]) >= self.graph.get_max_height():
            return

        if depth == self.max_height:
            return

        count = 0
        for next_edge in destination.get_edges().values():
            if sequence.__contains__(str(next_edge)):
                count += 1
                if count > 1:
                    flow = list(flows[-1][0:(flows[-1].index(next_edge.get_origin().get_symbol_index())+1)])
                    flow.append(next_edge.get_destination().get_symbol_index())
                    flows.append(flow)
                else:
                    flows[-1].append(next_edge.get_destination().get_symbol_index())
                self.flow_extract_util(sequence, next_edge, flows, depth+1)
                
            

    def generate_plantuml_pngs(self):
        for i, sequences in enumerate(self.list_of_flows):
            last_sequence_id = 0
            for j, sequence in enumerate(sequences):
                for k, flow in enumerate(sequence):
                    last_sequence_id += 1
                    CONTENT = self.generate_plantuml_syntax(flow, i + 1, last_sequence_id)
                    output = render(
                        CONTENT,
                        engine='plantuml',
                        format='svg',
                        cacheopts={
                            'use_cache': False
                        }
                    )

                    #sol_path = os.path.join(self.abs_path, self.directory_name, 'Solution ' + str(i + 1))
                    sol_path = os.path.join(self.abs_path, 'Solution ' + str(i + 1))
                    os.makedirs(sol_path, exist_ok=True)
                    seq_path = os.path.join(sol_path, 'Sequence ' + str(last_sequence_id) + '.svg')
                    f = open(seq_path, 'wb')
                    f.write(output[0])
                    f.close()

    def generate_solution_files(self):
        for i, solution in enumerate(self.solutions):
            #sol_path = os.path.join(self.abs_path, self.directory_name, 'Solution ' + str(i + 1))
            sol_path = os.path.join(self.abs_path, 'Solution ' + str(i + 1))
            os.makedirs(sol_path, exist_ok=True)
            sol_file_path = os.path.join(sol_path, 'Solution ' + str(i + 1) + '.txt')
            f = open(sol_file_path, 'w')
            f.write('\n')
            f.write('Solution ' + str(i + 1) + '\n')
            f.write('\n')
            char_id = 'a'
            for (edge_var, value) in solution:
                if char_id != str(edge_var)[0]:
                    char_id = str(edge_var)[0]
                    f.write('\n')
                if str(value) != '0':
                    f.write(str(edge_var) + ' with edge support of ' + str(value) + '\n')
            f.close()

    @staticmethod
    def prepare_solutions(solutions):
        sorted_solutions = []
        for solution in solutions:
            sorted_solution = sorted([[edge_var, solution[edge_var]] for edge_var in solution], key=lambda x: str(x[0]))
            sorted_solution = list(filter(lambda x: str(x[0]).__contains__('_') and str(x[1]) > '0', sorted_solution))
            # sorted_solution = list(map(lambda x: x[0], sorted_solution))
            sorted_solutions.append(sorted_solution)
        return sorted_solutions

    def generate_plantuml_syntax(self, sequence, solution_num, sequence_num):
        plantuml_syntax = '''title Solution ''' + str(solution_num) + ''' - Sequence ''' + str(sequence_num) + '''\n'''
        for node in sequence:
            message = self.graph.get_node(node).get_message()
            source_msg = message[0]
            destination_msg = message[1]
            plantuml_syntax += source_msg + '->' + destination_msg + ' : ' + self.graph.get_node(node).get_command() + '\n'

        return plantuml_syntax


    # @Author: Hao Zheng
    def flows_2_plantuml(self, flow_list, solution, sol_index):
        seq_id = 0
        sol_path = os.path.join(self.abs_path, 'Solution-' + str(sol_index))
        os.makedirs(sol_path, exist_ok=True)
        
        # write solution to the solution directory
        sol_file = os.path.join(sol_path, 'sol.txt')
        f = open(sol_file, 'w')
        f.write(str(solution))
        f.close()
            
        # write each sequence into a separate file
        for flow in flow_list:
            flow_index_seq = []
            for node in flow:
                flow_index_seq.append(node.get_index())

            # check validity of flow_seq wrt to filter lists.
            exclude = False
            include = True
            for ex_seq in self.graph.get_exclude_list():
                if set(ex_seq).issubset(set(flow_index_seq)):
                    exclude = True
                    break 
            for in_seq in self.graph.get_include_list():
                if ((in_seq[0] in flow_index_seq) and (in_seq[1] not in flow_index_seq)) or ((in_seq[0] not in flow_index_seq) and (in_seq[1] in flow_index_seq)):
                    include = False
                    break 
            if exclude or not include: continue

            flow_len = len(flow)
            first_index = flow[0].get_index()
            last_index = flow[-1].get_index()
            seq_name = str(first_index)+'_'+str(last_index)+'_'+str(flow_len)

            CONTENT = self.generate_plantuml(flow, sol_index, seq_id)
            # seq_path = os.path.join(sol_path, 'Sequence-' + str(seq_id) + '.png')
            seq_path = os.path.join(sol_path, 'Sequence-' + seq_name + '.txt')
            f = open(seq_path, 'w')
            # f.write(output[0])
            f.write(CONTENT)
            f.close()
            seq_id += 1

        log('\t solutioin '+ str(sol_index) + ': ' + str(seq_id) + ' flow sequences generated\n', INFO) 


    # @Author: Hao Zheng
    def generate_plantuml(self, flow, sol_index, seq_id):
        plantuml_syntax = '''title Solution ''' + str(sol_index) + ''' - Sequence ''' + str(seq_id) + '''\n'''
        for node in flow:
            message = node.get_message()
            source_msg = message[0]
            destination_msg = message[1]
            msg_type = node.get_type()
            plantuml_syntax += source_msg + '->' + destination_msg + ' : ' + node.get_command() +':' + msg_type + '\n'

        return plantuml_syntax


    #
    #
    def extract_sequences(self, solution):
        all_flows = []
        sol_edges = {}
        nodes = self.graph.get_nodes()
        edges = self.graph.get_edges().values()

        for edge in edges:
            if solution[edge.get_z3var()].as_long() == 0:
                continue
            edge_src = edge.get_source().get_index()
            edge_dest = edge.get_destination().get_index()

            if edge_src in sol_edges:
                sol_edges[edge_src].append(edge_dest)
            else:
                sol_edges[edge_src] = [edge_dest]
        
        roots = self.graph.get_roots()
        terminals = []
        for t in self.graph.get_terminal_nodes():
            terminals.append(t)

        flow_list = []
        for root in roots.values():
            flow = [root.get_index()]
            flow_list.append(flow)
        
        flow_list = self.get_sequences(sol_edges, flow_list, terminals, 1)
        return flow_list


    def get_sequences(self, edges, flow_list, terminals, depth):
        if depth == self.max_height:
            return flow_list

        new_flow_list = []
        go_deeper = False
        for flow in flow_list:
            last_node = flow[-1]
            
            if last_node in terminals:
                new_flow_list.append(flow)
                continue

            if last_node not in edges:
                new_flow_list.append(flow)
                continue
            go_deeper = True
                        
            succ_list = edges[last_node]
            for node in succ_list:
                if node in flow:  # no duplication messages in a flow
                    continue
                # do not include a flow that does not end with a terminal
                elif (node not in terminals) and (depth+1 == self.max_height):
                    continue

                flow_copy = flow.copy()
                flow_copy.append(node)
                new_flow_list.append(flow_copy)

        if go_deeper == True:  
            return self.get_flows(edges, new_flow_list, terminals, depth+1)
        else:
            return new_flow_list
        

    