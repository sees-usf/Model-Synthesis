#!/usr/local/bin/python3

import os
import networkx as nx

from src.graph.graph import Graph
# from src.sequence_printer.sequence_printer import SequencePrinter
from src.solver.trace2flows import *
from src.annotator.annotator import GraphAnnotator
from src.logging import *
from src.filter_list import *
import src.essential.EssentialsEfficient
from src.evaluation.optimizedEvaluation import optimizedEvaluation

from datetime import timedelta

start_time = time.time()
def prepare_traces(filename):
    f = open(filename, 'r')
    f1 = f.readlines()
    f.close()
    return f1


G = nx.DiGraph()

print('Sequence Mining Tool Demo by USF')
print()

if __name__ == '__main__':
    # max_pat_len = 8
    # len_input = input("Maximum pattern length for mining (default 8): ")
    # if len_input:
    #     max_pat_len = int(len_input)
    # log('Max pattern length is ' + str(max_pat_len) + '\n\n')

    # max_solutions = 10
    # sol_input = input("Maximum number of solutions allowed (default 10): ")
    # if sol_input:
    #     max_solutions = int(sol_input)
    # log('Max number of solutions is ' + str(max_solutions) + '\n\n')

    # print('Which message definition example would you like to run?')
    # print()
    # print('1. Small example')
    # print('2. Medium example')
    # print('3. Large example')
    # print()
    # example_choice = input('Enter your choice (1-3): ')

    # def_f = ''
    # trace_f = ''
    # if example_choice == '1':
    #     def_f = 'small_def.txt'
    #     trace_f = 'small_trace.txt'
    # elif example_choice == '2':
    #     def_f = 'medium.msg'
    #     trace_f = 'medium_trace.txt'
    # elif example_choice == '3':
    #     # def_f = './definitions/large_def.txt'
    #     def_f = 'large.msg'
    #     trace_f = 'large_trace.txt'
    #     #trace_f = 'long-2.tr'
    # else:
    #     print('Run the script again and enter the correct option to run a message definition example.')
    #     exit()

    # filters_filename = input('Sequence filter file: ')
    # print('no sequence filters file specified') if not filters_filename else print('')

    # rank_filename = input('Binary sequence ranking file: ')
    # print('no binary sequence ranking file specified') if not rank_filename else print('')

    max_pat_len = 8
    max_solutions = 10
    def_f = ""
    trace_f = ""

    # Uncomment corresponding lines to genearte solutions for different traces

    # For gem5 traces

    # Full system (FS) simulation traces
    # def_f = './traces/gem5_traces/fs/definition/fs_def.msg'
    # def_f = './traces/gem5_traces/fs/definition/fs_def_withInitialsAndTerminals.msg'
    # def_f = './traces/gem5_traces/fs/definition/fs_manual.msg'

    # fs unsliced
    # trace_f = ['./traces/gem5_traces/fs/unsliced/fs_boot_unsliced.txt']
    # fileNamePrefix = "gem5/fs/unsliced"
    # fileNamePrefix = "gem5/fs/window_sliced"
    # fileNamePrefix = "gem5/fs/test"
    # fs packet id sliced
    # trace_f = ['./traces/gem5_traces/fs/packet_sliced/packet_sliced.jbl']
    # fs memory address sliced
    # trace_f = ['./traces/gem5_traces/fs/addr_sliced/address_sliced_no_duplicates.jbl']

    # Snoop (SE) traces
    # def_f = './traces/gem5_traces/snoop/definition/paterson_def.msg'
    # def_f = './traces/gem5_traces/snoop/definition/paterson_def_withInitialsAndTerminals.msg'
    # def_f = './traces/gem5_traces/snoop/definition/changedByBardia.msg'
    # def_f = './traces/gem5_traces/snoop/definition/renamed.msg'
    # snoop unsliced
    # trace_f = ['./traces/gem5_traces/snoop/unsliced/paterson_unsliced.txt']
    # fileNamePrefix = "gem5/snoop/test"
    # snoop packet id sliced
    # trace_f = ['./traces/gem5_traces/snoop/packet_sliced/packet_sliced.jbl']
    # snoop memory address sliced
    # trace_f = ['./traces/gem5_traces/snoop/addr_sliced/address_sliced.jbl']

    # Threads (SE) traces
    # def_f = './traces/gem5_traces/threads/definition/threads_def.msg' # This definition file doesn't include any initial or terminal nodes
    # def_f = './traces/gem5_traces/threads/definition/definition.txt'  # This is the one that is being used right now
    # def_f = './traces/gem5_traces/threads/definition/renamedDefinitionFile.msg'
    # def_f = './traces/gem5_traces/threads/definition/threads_defWithInitialsAndTerminals.msg'
    # def_f = './traces/gem5_traces/threads/definition/myDefinition.txt'  
    # def_f = './traces/gem5_traces/threads/definition/newDefinition.txt' 
    # def_f = './traces/gem5_traces/threads/definition/generatedByMeDef.msg'  
    def_f = './traces/gem5_traces/threads/definition/connectedThreadsDefinition.txt'  
    # threads unsliced
    trace_f = ['./traces/gem5_traces/threads/unsliced/unsliced.txt']
    # trace_f = ['./traces/gem5_traces/threads/unsliced/generatedByMeThreadsTraceFile.txt']
    fileNamePrefix = "gem5/threads/test"
    # threads packet id sliced
    # trace_f = ['./traces/gem5_traces/threads/packet_sliced/packet_sliced.jbl']   
    # fileNamePrefix = "gem5/threads/packet_sliced"
    # snoop memory address sliced
    # trace_f = ['./traces/gem5_traces/threads/addr_sliced/address_sliced.jbl']
    # trace_f = ['./traces/gem5_traces/threads/addr_sliced/address_sliced_compact.jbl']


    # For synthetic traces
    # def_f = './traces/synthetic/newLarge.msg'
    # def_f = './traces/synthetic/large.msg'
    # def_f = './traces/synthetic/medium.msg'
    # def_f = './traces/synthetic/small.msg'
    # def_f = './traces/synthetic/Test/testDefinition.msg'


    # small traces
    # trace_f = ['./traces/synthetic/trace-small-5.txt']
    # fileNamePrefix = "synthetic/small-5"
    # trace_f = ['./traces/synthetic/trace-small-10.txt']
    # fileNamePrefix = "synthetic/small-10/window"
    # trace_f = ['./traces/synthetic/trace-small-20.txt']
    # fileNamePrefix = "synthetic/small-20/window"

    # large traces
    # trace_f = ['./traces/synthetic/trace-large-5.txt']
    # fileNamePrefix = "synthetic/large-5/window"
    # trace_f = ['./traces/synthetic/trace-large-10.txt']
    # fileNamePrefix = "synthetic/large-10/window"
    # trace_f = ['./traces/synthetic/trace-large-20.txt']
    # fileNamePrefix = "synthetic/large-20"
    # trace_f = ['./traces/synthetic/new-trace-large-20.txt']
    # fileNamePrefix = "synthetic/large-20/test"

    # trace_f = ['./traces/synthetic/Test/testTrace.txt']

    # For Testing 
    # def_f = './traces/ForTest/testDefinitionFile.txt'
    # trace_f = ['./traces/ForTest/testTrace.txt']
    # fileNamePrefix = "test/test"
    # def_f = './traces/ForTest/L3cacheTestDefinitionFile.txt'
    # trace_f = ['./traces/ForTest/L3cacheTestTrace.txt']
    # fileNamePrefix = "test/L3cache"


    is_relaxed_mode_used = False

    essential_mode = False
    essential_edges_array = []
    if (essential_mode == True):
        print("Finding Essentails!")
        essential_edges_array = src.essential.EssentialsEfficient.find_essential_causalities(def_f, trace_f[0])
        print (essential_edges_array)
        print("Finding Essentails: Done!")

    filters_filename = None
    rank_filename = None

    graph = Graph()
    graph.set_max_height(max_pat_len)
    graph.set_max_solutions(max_solutions)

    graph.window = False
    graph.window_size = 300  

    if (graph.window and (graph.window <= 0)):
        print("Winodw size must > 0")
        exit()
    if(graph.window):
        print("Added window slicing...window size: ", graph.window_size)
        print()

    log('Reading the message definition file %s... ' % def_f)
    if def_f=="":
        exit()
    graph.read_message_file(def_f)
    log('Done\n\n')

    traces = None
    log('Reading the trace file(s) %s... ' % trace_f)
    # traces = prepare_traces(trace_f)
    # annotator = GraphAnnotator(traces[0], graph)
    # graph.read_trace_file(trace_f[0])
    graph.read_trace_file_list(trace_f)
    # annotator.annotate()
    log('Trace reading and processing status: Done\n\n')

    elapsed_time = time.time() - start_time
    msg = "Trace reading and proc took: %s secs (Wall clock time)" % timedelta(milliseconds=round(elapsed_time*1000))
    print(msg)

    if filters_filename:
        log('Reading the sequence filter file %s ... ' % filters_filename, INFO)
        graph.read_filters(filters_filename)
        log('Done\n', INFO)
    log('\n', INFO)

    if rank_filename:
        log('Reading the sequence filter file %s ... ' % rank_filename, INFO)
        graph.read_bin_seq_ranking(rank_filename)
        log('Done\n', INFO)
    log('\n', INFO)

    # breakpoint()
    # *** Solving the (mono or split) graphs
    cgs = []
    cgs.append(graph)

    # cgs[0].print_graph()

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
        # graph.remove_cycles()
        z3solver = trace2flows(cgs)
        # z3solver.find_model_interactive()
        log('Finding models with standard constraints ...\n')
        models = z3solver.find_reduced_model_bVersion(essential_mode=essential_mode, essential_edges_array=essential_edges_array)
        # models = z3solver.find_reduced_model(essential_mode=essential_mode, essential_edges_array=essential_edges_array)
        # @ find models with relaxed constraints if no model is found by the regular constraints
        if len(models) == 0:
            log('Finding models with relaxed constraints ...\n')
            models = z3solver.find_reduced_model_relaxed_bVersion(essential_mode=essential_mode, essential_edges_array=essential_edges_array)
            # models = z3solver.find_reduced_model_relaxed(essential_mode=essential_mode, essential_edges_array=essential_edges_array)
            is_relaxed_mode_used = True
        # z3solver.find_minimum_model()
        # z3solver.find_model_incremental()
        log('Numbers of models found is %s\n' % (len(models)))
    # exit()

    sorted_models = {}
    for k in sorted(models, key=len, reverse=False):
        sorted_models[k] = models[k]

    count = 0
    total_models = len(sorted_models)  # total number of models found

    save_models = 20
    if total_models < save_models:
        save_models = total_models

    print ("Initial Nodes:")
    for test in graph.root_nodes:
        print (test)
    print ("Terminal Nodes:")
    for test in graph.terminal_nodes:
        print (test)
    print ("Seperator............................................")
   
    ################################################################################################ Bardia ########################################
    myCounter = 0
    total_res1 = 0
    total_res2 = 0
    for model in sorted_models:
        m = model.split(' ')
        # print(len(m), m)

        if graph.window == True:
            f = open('./solutions/'+ fileNamePrefix + "/sol_" + str(myCounter) + '_size_' + str(len(m)) + "window_size_" + str(graph.window_size)  + '.txt', 'w')
        else:
            f = open('./solutions/'+ fileNamePrefix + "/sol_" + str(myCounter) + '_size_' + str(len(m)) + '.txt', 'w')
        for i in m:
            i = i.split('_')
            if len(i) > 1:
                G.add_edge(i[0], i[1])
                f.write(i[0] + ' ' + i[1] + "\n")
        f.close()

        # for node in G:
        #     if G.in_degree(node) == 0 and node not in graph.root_nodes:
        #         print("Problem with node: ", node)
        #         print("There is a problem with initial nodes in generated model!")

        #     if G.out_degree(node) == 0 and node not in graph.terminal_nodes:
        #         print("Problem with node: ", node)
        #         print ("There is a problem with terminal nodes in generated model!")

        if graph.window == True:
            # resultFileName = "./evaluationResults/" + fileNamePrefix + "/result_" + "window_size_" + str(graph.window_size) + '.txt'
            resultFileName = "./evaluationResults/" + fileNamePrefix + "/result_" + str(myCounter) + '_size_' + str(len(m)) + "window_size_" + str(graph.window_size) + '.txt'
        else:
            # resultFileName = "./evaluationResults/" + fileNamePrefix + "/result" + '.txt'
            resultFileName = "./evaluationResults/" + fileNamePrefix + "/result_" + str(myCounter) + '_size_' + str(len(m)) + '.txt'
        ev = optimizedEvaluation(trace_f[0], G, resultFileName)
        res1, res2 = ev.evaluate()
        total_res1 += res1
        total_res2 += res2
                      


        G.clear()
        myCounter = myCounter + 1
        if myCounter >= save_models:  # number of models to select for evaluation, we select smallest 20 for now
            break

    # for model in sorted_models:
    #     m = model.split(' ')
    #     # print(len(m), m)
    #     f = open('./solutions/sol_' + str(count) + '_size_' + str(len(m)) + '.txt', 'w')
    #     for i in m:
    #         i = i.split('_')
    #         # print("value: ",i)
    #         if len(i) > 1:
    #             f.write(i[0] + ' ' + i[1] + "\n")
    #         # print(i)
    #     f.close()
    #     count = count + 1
    #     if count >= save_models:  # number of models to select for evaluation, we select smallest 20 for now
    #         break
    ################################################################################################ Bardia ########################################
    if (save_models != 0):
        print ("\n\nAveraged results (ratio/total))= ", total_res1/save_models)
        print ("Averaged results (# of accepted events/total # of events)= ", total_res2/save_models)
    
    elapsed_time_secs = time.time() - start_time
    msg = "\bExecution took: %s secs (Wall clock time)" % timedelta(seconds=round(elapsed_time_secs))
    print(msg)

    log('Solutnions are saved in ./solutions directory\n')
    log('Done\n')
    if (len(models) > 0 and is_relaxed_mode_used == True):
        print("Relaxed function has been used for generated solutions!")
    elif (len(models) > 0):
        print("Reduced function has been used for generated solutions!")


    # print('Please indicate the constraint encoding strategy you\'d like to use: ')
    # print()
    # print('1. Monolithic graph strategy')
    # print('2. Split graph strategy')
    # print()

    # strategy_choice = input('Enter your choice (1-2): ')
    # print()
    # print("Solutions will be generated and printed to a sub-directory in the \"solutions\" directory.")
    # print()
    solution_dir_name = None  # input('Enter a name for this sub-directory: ')


    log('Solutions found ' + str(len(z3solver.get_solutions())) + '\n')
    if not z3solver.get_solutions():
        exit()
