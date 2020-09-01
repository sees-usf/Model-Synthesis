import os

from src.annotator.annotator import GraphAnnotator
from src.graph.graph import Graph
from src.sequence_printer.sequence_printer import SequencePrinter
from src.solver.z3solver import Z3Solver


def prepare_traces(filename):
    f = open(filename, 'r')
    f1 = f.readlines()
    f.close()
    return f1


if __name__ == '__main__':
    print('Sequence Mining Tool Demo by USF')
    print()
    print('Which message definition example would you like to run?')
    print()
    print('1. Small example')
    print('2. Medium example')
    print('3. Large example')
    print()

    example_choice = input('Enter your choice (1-3): ')

    print()
    print('Generating graph...')
    print()

    graph = Graph()

    traces = None
    if example_choice == '1':
        graph.generate_graph('./definitions/small_def.txt')
        traces = prepare_traces('./traces/small_trace.txt')
    elif example_choice == '2':
        graph.generate_graph('./definitions/medium_def.txt')
        traces = prepare_traces('./traces/medium_trace.txt')
    elif example_choice == '3':
        graph.generate_graph('./definitions/large_def.txt')
        traces = prepare_traces('./traces/large_trace.txt')
    else:
        print('Run the script again and enter the correct option to run a message definition example.')
        exit()

    annotator = GraphAnnotator(traces[0], graph)
    annotator.annotate()

    dags = graph.generate_dags()

    for dag in dags:
        annotator = GraphAnnotator(traces[0], dag)
        annotator.annotate()
        dag.remove_cycles()

    graph.remove_cycles()
    z3 = Z3Solver(graph, dags)

    print('Please indicate the constraint encoding strategy you\'d like to use: ')
    print()
    print('1. Monolithic graph strategy')
    print('2. Split graph strategy')
    print()

    strategy_choice = input('Enter your choice (1-2): ')
    print()
    print("Solutions will be generated and printed to a sub-directory in the \"solutions\" directory.")
    print()
    solution_dir_name = None#input('Enter a name for this sub-directory: ')

    print()
    print('Mining message flows...')
    print()

    if strategy_choice == '1':
        z3.generate_monolithic_solutions()
    elif strategy_choice == '2':
        z3.generate_split_solutions()
    else:
        print('Run the script again and enter the correct option for the constraint encoding strategy.')
        exit()

    if not z3.get_solutions():
        exit()

    print('Generating solutions and sequence diagrams...')

    abs_path = os.path.dirname(os.path.abspath(__file__))
    printer = SequencePrinter(z3.get_solutions(), abs_path, solution_dir_name, graph)
    printer.generate_solutions()

    print()
    print('Sequences have been successfully mined and converted to PlantUML diagrams.')
    print()
