import os

from src.graph.graph import Graph
from src.sequence_printer.sequence_printer import SequencePrinter
from src.solver.z3solver import Z3Solver
from src.annotator.annotator import GraphAnnotator
from src.logging import *


def prepare_traces(filename):
    f = open(filename, 'r')
    f1 = f.readlines()
    f.close()
    return f1


if __name__ == '__main__':
    max_pat_len = int(input("Maximum pattern length for mining: "))

    print('Sequence Mining Tool Demo by USF')
    print()
    print('Which message definition example would you like to run?')
    print()
    print('1. Small example')
    print('2. Medium example')
    print('3. Large example')
    print()

    example_choice = input('Enter your choice (1-3): ')

    graph = Graph()
    graph.set_max_height(max_pat_len)
    traces = None
    def_f = ''
    trace_f = ''
    if example_choice == '1':
        def_f = './definitions/small_def.txt'
        trace_f = './traces/small_trace.txt'
    elif example_choice == '2':
        def_f = './definitions/medium_def.txt'
        trace_f = './traces/medium_trace.txt'
    elif example_choice == '3':
        # def_f = './definitions/large_def.txt'
        def_f = './definitions/large_v1.def'
        trace_f = './traces/large_trace.txt'
    else:
        print('Run the script again and enter the correct option to run a message definition example.')
        exit()

    ignore_f = input('Sequence exclusion file: ')
    print('no sequence exclusion file specified') if not ignore_f else print('')

    log('Reading the message definition file ... ')
    graph.generate_graph(def_f)
    log('Done\n')

    log('Reading the sequence exclusion file ... ')
    graph.read_ignore(ignore_f)
    log('Done\n')

    log('Reading the trace file ... ')
    traces = prepare_traces(trace_f)
    annotator = GraphAnnotator(traces[0], graph)
    annotator.annotate()
    log('Done\n')

    
    # dags = graph.generate_dags()

    # for dag in dags:
    #     annotator = GraphAnnotator(traces[0], dag)
    #     annotator.annotate()
    #     dag.remove_cycles()

    #graph.remove_cycles()
    dags = []
    z3 = Z3Solver(graph, dags)

    # print('Please indicate the constraint encoding strategy you\'d like to use: ')
    # print()
    # print('1. Monolithic graph strategy')
    # print('2. Split graph strategy')
    # print()

    # strategy_choice = input('Enter your choice (1-2): ')
    # print()
    # print("Solutions will be generated and printed to a sub-directory in the \"solutions\" directory.")
    # print()
    solution_dir_name = None#input('Enter a name for this sub-directory: ')

    log('Mining message flows ... ')
    # if strategy_choice == '1':
    #     #graph.remove_cycles()
    #     #z3 = Z3Solver(graph, None)
    #     z3.generate_monolithic_solutions()
    # elif strategy_choice == '2':
    #     # dags = graph.generate_dags()
    #     # for dag in dags:
    #     #     annotator = GraphAnnotator(traces[0], dag)
    #     #     annotator.annotate()
    #     #     dag.remove_cycles()
    #     # 
    #     # graph.remove_cycles()
    #     # z3 = Z3Solver(graph, dags)
    #     z3.generate_split_solutions()
    # else:
    #     print('Run the script again and enter the correct option for the constraint encoding strategy.')
    #     exit()
    z3.generate_monolithic_solutions()
    log('done\n')

    log('Solutions found ' + str(len(z3.get_solutions()))+'\n')
    if not z3.get_solutions():
        exit()

    log('Generating solutions and sequence diagrams ... \n')
    abs_path = os.path.dirname(os.path.abspath(__file__))
    printer = SequencePrinter(z3.get_solutions(), abs_path, solution_dir_name, graph)
    printer.generate_solutions()
    log('done\n')
