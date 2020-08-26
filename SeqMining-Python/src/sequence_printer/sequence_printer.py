import os

from plantweb.render import render


class SequencePrinter:
    def __init__(self, solutions, abs_path, directory_name, graph):
        self.solutions = self.prepare_solutions(solutions)
        self.abs_path = abs_path + '\\solutions\\'
        self.directory_name = directory_name
        self.graph = graph
        self.list_of_sequences = []
        self.list_of_flows = []

    def generate_solutions(self):
        self.divide_solution_sequences()
        self.generate_plantuml_pngs()
        self.generate_solution_files()

    def divide_solution_sequences(self):
        for solution in self.solutions:
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
        self.flow_extract_util(sequence, starting_edge, flows)

        return flows

    def flow_extract_util(self, sequence, edge, flows):
        destination = edge.get_destination()

        if self.graph.is_terminal_node(destination):
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
                self.flow_extract_util(sequence, next_edge, flows)

    def generate_plantuml_pngs(self):
        for i, sequences in enumerate(self.list_of_flows):
            for j, sequence in enumerate(sequences):
                for k, flow in enumerate(sequence):
                    CONTENT = self.generate_plantuml_syntax(flow, i + 1, (k + 1))
                    output = render(
                        CONTENT,
                        engine='plantuml',
                        format='svg',
                        cacheopts={
                            'use_cache': False
                        }
                    )

                    sol_path = os.path.join(self.abs_path, self.directory_name, 'Solution ' + str(i + 1), 'DAG ' + str(j + 1))
                    os.makedirs(sol_path, exist_ok=True)
                    seq_path = os.path.join(sol_path, 'Sequence ' + str((k + 1)) + '.svg')
                    f = open(seq_path, 'wb')
                    f.write(output[0])
                    f.close()

    def generate_solution_files(self):
        for i, solution in enumerate(self.solutions):
            sol_path = os.path.join(self.abs_path, self.directory_name, 'Solution ' + str(i + 1))
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
