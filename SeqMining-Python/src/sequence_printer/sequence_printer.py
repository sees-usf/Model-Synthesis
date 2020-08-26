import os

from nltk import regexp_tokenize
from plantweb.render import render
from z3 import ModelRef


class SequencePrinter:
    def __init__(self, solutions, abs_path, directory_name, graph):
        self.solutions = self.prepare_solutions(solutions)
        self.abs_path = abs_path + '\\solutions\\'
        self.directory_name = directory_name
        self.graph = graph
        self.list_of_sequences = []

    def generate_solutions(self):
        self.extract_sequences()
        self.generate_plantuml_pngs()
        self.generate_solution_files()

    def extract_sequences(self):
        for solution in self.solutions:
            sequences = []
            for edge_var in solution:
                edge_symbol_indices = regexp_tokenize(str(edge_var[0])[1:], pattern=r'\s|[_]', gaps=True)
                origin_symbol_index = edge_symbol_indices[0]
                destination_symbol_index = edge_symbol_indices[1]
                if self.graph.is_root(origin_symbol_index):
                    sequences.append([self.graph.get_node(origin_symbol_index),
                                      self.graph.get_node(destination_symbol_index)])
                else:
                    for sequence in sequences:
                        if origin_symbol_index == str(sequence[-1]):
                            sequence.append(self.graph.get_node(destination_symbol_index))
            self.list_of_sequences.append(sequences)

    def generate_plantuml_pngs(self):
        for i, sequences in enumerate(self.list_of_sequences):
            for j, sequence in enumerate(sequences):
                CONTENT = self.generate_plantuml_syntax(sequence, i + 1, j + 1)
                output = render(
                    CONTENT,
                    engine='plantuml',
                    format='svg',
                    cacheopts={
                        'use_cache': False
                    }
                )

                sol_path = os.path.join(self.abs_path, self.directory_name, 'Solution ' + str(i+1))
                os.makedirs(sol_path, exist_ok=True)
                seq_path = os.path.join(sol_path, 'Sequence ' + str(j+1) + '.svg')
                f = open(seq_path, 'wb')
                f.write(output[0])
                f.close()

    def generate_solution_files(self):
        for i, solution in enumerate(self.solutions):
            sol_path = os.path.join(self.abs_path, self.directory_name, 'Solution ' + str(i + 1))
            os.makedirs(sol_path, exist_ok=True)
            sol_file_path = os.path.join(sol_path, 'Solution ' + str(i+1) + '.txt')
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
            sorted_solutions.append(sorted_solution)
        return sorted_solutions

    @staticmethod
    def generate_plantuml_syntax(sequence, solution_num, sequence_num):
        plantuml_syntax = '''title Solution ''' + str(solution_num) + ''' - Sequence ''' + str(sequence_num) + '''\n'''
        for node in sequence:
            message = node.get_message()
            source_msg = message[0]
            destination_msg = message[1]
            plantuml_syntax += source_msg + '->' + destination_msg + ' : ' + node.get_command() + '\n'

        return plantuml_syntax
