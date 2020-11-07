import os

from src.graph.graph import Graph
from src.sequence_printer.sequence_printer import SequencePrinter
from src.solver.trace2flows import *
from src.annotator.annotator import GraphAnnotator
from src.logging import *
from src.filter_list import *


def prepare_traces(filename):
    f = open(filename, 'r')
    f1 = f.readlines()
    f.close()
    return f1

print('Sequence Mining Tool Demo by USF')
print()

if __name__ == '__main__':
    max_pat_len = 8
    len_input = input("Maximum pattern length for mining (default 8): ")
    if len_input:
        max_pat_len = int(len_input)
    log('Max pattern length is ' + str(max_pat_len) + '\n\n')

    max_solutions = 10
    sol_input = input("Maximum number of solutions allowed (default 10): ")
    if sol_input:
        max_solutions = int(sol_input)
    log('Max number of solutions is ' + str(max_solutions) + '\n\n')


    print('Which message definition example would you like to run?')
    print()
    print('1. Small example')
    print('2. Medium example')
    print('3. Large example')
    print()

    example_choice = input('Enter your choice (1-3): ')

    graph = Graph()
    graph.set_max_height(max_pat_len)
    graph.set_max_solutions(max_solutions)
    traces = None
    def_f = ''
    trace_f = ''
    if example_choice == '1':
        def_f = 'small_def.txt'
        trace_f = 'small_trace.txt'
    elif example_choice == '2':
        def_f = 'medium.msg'
        trace_f = 'medium_trace.txt'
    elif example_choice == '3':
        # def_f = './definitions/large_def.txt'
        def_f = 'large.msg'
        trace_f = 'large_trace.txt'
        #trace_f = 'long-2.tr'
    else:
        print('Run the script again and enter the correct option to run a message definition example.')
        exit()

    log('Reading the message definition file ... ')
    graph.generate_graph(def_f)
    log('DOne\n\n')

    log('Reading the trace file ... ')
    traces = prepare_traces(trace_f)
    annotator = GraphAnnotator(traces[0], graph)
    annotator.annotate()
    log('Done\n\n')

    filters_filename = input('Sequence filter file: ')
    print('no sequence filters file specified') if not filters_filename else print('')

    if filters_filename:
        log('Reading the sequence filter file %s ... ' %filters_filename, INFO)
        graph.read_filters(filters_filename)
        log('Done\n', INFO)
    log('\n', INFO)

    rank_filename = input('Binary sequence ranking file: ')
    print('no binary sequence ranking file specified') if not rank_filename else print('')

    if rank_filename:
        log('Reading the sequence filter file %s ... ' %rank_filename, INFO)
        graph.read_bin_seq_ranking(rank_filename)
        log('Done\n', INFO)
    log('\n', INFO)
    
    # *** Solving the (mono or split) graphs
    cgs = []
    cgs.append(graph)

    log('Mining message flows ...\n')
    split = False
    if split:
        # the split CG method does NOT work correct
        dags = graph.generate_dags()
        for dag in dags:
            annotator = GraphAnnotator(traces[0], dag)
            annotator.annotate()
            dag.remove_cycles()
            cgs.append(dag)
        graph.remove_cycles()
        z3 = Z3Solver(cgs)
        z3.generate_split_solutions()
    else:
        #graph.remove_cycles()
        z3 = trace2flows(cgs)    
    log('Done\n')


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
    #z3.generate_monolithic_solutions()
    #z3.generate_split_solutions()


    log('Solutions found ' + str(len(z3.get_solutions()))+'\n')
    if not z3.get_solutions():
        exit()

    log('Generating solutions and sequence diagrams ... \n')
    abs_path = os.path.dirname(os.path.abspath(__file__))
    printer = SequencePrinter(z3.get_solutions(), abs_path, solution_dir_name, graph)
    printer.generate_solutions()
    log('Done\n')

