#!/usr/local/bin/python3

import os
import networkx as nx

from src.graph.graph import Graph
from src.solver.trace2flows import *
from src.logging import *
import src.essential.EssentialsEfficient
from src.evaluation.FSAEvaluation import FSAEvaluation

from datetime import timedelta
import sys

start_time = time.time()
def prepare_traces(filename):
    f = open(filename, 'r')
    f1 = f.readlines()
    f.close()
    return f1


G = nx.DiGraph()
solutions_output_path = "./output/solutions/"
results_output_path = "./output/results/"

print('Sequence Mining Tool Demo by USF')
print()

if __name__ == '__main__':

    max_pat_len = 8
    max_solutions = 10
    def_f = ""
    trace_f = ""

    is_relaxed_mode_used = False

    essential_mode = False
    essential_edges_array = []
    if (essential_mode == True):
        print("Finding Essentails!")
        essential_edges_array = src.essential.EssentialsEfficient.find_essential_causalities(def_f, trace_f[0])
        print (essential_edges_array)
        print("Finding Essentails: Done!")


    graph = Graph()
    graph.set_max_height(max_pat_len)
    graph.set_max_solutions(max_solutions)


    if sys.argv[1] == 'gem5':
        if sys.argv[2] == 'full_system':
            def_f = './benchmarks/gem5_traces/fs/definition/def-FS-RublePrintFormat.msg' 

            if sys.argv[3] == 'unsliced':
                trace_f = ['./benchmarks/gem5_traces/fs/unsliced/out1.txt','./benchmarks/gem5_traces/fs/unsliced/out2.txt','./benchmarks/gem5_traces/fs/unsliced/out3.txt'] 
                fileNamePrefix = "gem5/fs/unsliced"
                graph.window = False
                graph.window_size = 12
            elif sys.argv[3] == 'window_sliced':
                trace_f = ['./benchmarks/gem5_traces/fs/unsliced/out1.txt','./benchmarks/gem5_traces/fs/unsliced/out2.txt','./benchmarks/gem5_traces/fs/unsliced/out3.txt'] 
                fileNamePrefix = "gem5/fs/window_sliced"
                graph.window = True
                graph.window_size = 12
            elif sys.srgv[3] == "architectural_sliced": 
                trace_f = ['./benchmarks/gem5_traces/fs/packet_sliced/packet_sliced.jbl']
                fileNamePrefix = "gem5/fs/architectural_sliced"
                graph.window = False
                graph.window_size = 12
            elif sys.argv[3] == 'all_sliced':
                trace_f = ['./benchmarks/gem5_traces/fs/packet_sliced/packet_sliced.jbl']
                fileNamePrefix = "gem5/fs/all_sliced"
                graph.window = True
                graph.window_size = 12

        elif sys.argv[2] == 'threads':
            def_f = './benchmarks/gem5_traces/threads/definition/defThreads-RubelPrintFormat.msg' 

            if sys.argv[3] == 'unsliced':
                trace_f = ['./benchmarks/gem5_traces/threads/unsliced/unsliced-RubelPrintFormat.jbl']
                fileNamePrefix = "gem5/threads/unsliced"
                graph.window = False
                graph.window_size = 12
            elif sys.argv[3] == 'window_sliced':
                trace_f = ['./benchmarks/gem5_traces/threads/unsliced/unsliced-RubelPrintFormat.jbl']
                fileNamePrefix = "gem5/threads/window_sliced"
                graph.window = True
                graph.window_size = 12
            elif sys.srgv[3] == "architectural_sliced": 
                trace_f = ['./benchmarks/gem5_traces/threads/architecturalSliced/totalSliced.jbl']
                fileNamePrefix = "gem5/threads/architectural_sliced"
                graph.window = False
                graph.window_size = 12
            elif sys.argv[3] == 'all_sliced':
                trace_f = ['./benchmarks/gem5_traces/threads/architecturalSliced/totalSliced.jbl']
                fileNamePrefix = "gem5/threads/all_sliced"
                graph.window = True
                graph.window_size = 12

        elif sys.argv[2] == 'snoop':
            def_f = './benchmarks/gem5_traces/snoop/definition/defSnoop-RubelPrintFormat.msg'

            if sys.argv[3] == 'unsliced':
                trace_f = ['./benchmarks/gem5_traces/snoop/unsliced/unsliced-RubelPrintFormat.jbl']
                fileNamePrefix = "gem5/snoop/unsliced"
                graph.window = False
                graph.window_size = 12
            elif sys.argv[3] == 'window_sliced':
                trace_f = ['./benchmarks/gem5_traces/snoop/unsliced/unsliced-RubelPrintFormat.jbl']
                fileNamePrefix = "gem5/snoop/window_sliced"
                graph.window = True
                graph.window_size = 12
            elif sys.srgv[3] == "architectural_sliced": 
                ttrace_f = ['./benchmarks/gem5_traces/snoop/architecturalSliced/totalSliced.jbl']
                fileNamePrefix = "gem5/snoop/architectual_sliced"
                graph.window = False
                graph.window_size = 12
            elif sys.argv[3] == 'all_sliced':
                ttrace_f = ['./benchmarks/gem5_traces/snoop/architecturalSliced/totalSliced.jbl']
                fileNamePrefix = "gem5/snoop/all_sliced"
                graph.window = True
                graph.window_size = 12
        else:
            print ("Wrong type of Gem5 traces is chosen!")
            exit()
    elif sys.argv[1] == 'synthetic':
        def_f = './benchmarks/synthetic_traces/definition/newLarge.msg'

        if sys.argv[3] == 'unsliced':
            graph.window = False
            graph.window_size = 10
        elif sys.argv[3] == 'window_sliced':
            graph.window = True
            graph.window_size = 10
        else:
            print ("Wrong slicing technique is chosen!")
            exit()

        if sys.argv[2] == 'large-20':
            trace_f = ['./benchmarks/synthetic_traces/large/trace-large-20.txt']
            fileNamePrefix = "synthetic/large-20/" + str(sys.argv[3])
        elif sys.argv[2] == 'large-10':
            trace_f = ['./benchmarks/synthetic_traces/large/trace-large-10.txt']
            fileNamePrefix = "synthetic/large-10/" + str(sys.argv[3])
        elif sys.argv[2] == 'large-5':
            trace_f = ['./benchmarks/synthetic_traces/large/trace-large-5.txt']
            fileNamePrefix = "synthetic/large-5/" + str(sys.argv[3])
        elif sys.argv[2] == 'small-20':
            trace_f = ['./benchmarks/synthetic_traces/small/trace-small-20.txt']
            fileNamePrefix = "synthetic/small-20/" + str(sys.argv[3])
        elif sys.argv[2] == 'small-10':
            trace_f = ['./benchmarks/synthetic_traces/small/trace-small-10.txt']
            fileNamePrefix = "synthetic/small-10/" + str(sys.argv[3])
        elif sys.argv[2] == 'small-5':
            trace_f = ['./benchmarks/synthetic_traces/small/trace-small-5.txt']
            fileNamePrefix = "synthetic/small-5/" + str(sys.argv[3])

        elif sys.argv[2] == 'multiple_traces':
            trace_f = ["./benchmarks/synthetic_traces/multi_trace/multipleTraces-synthetic.txt"]
            fileNamePrefix = "synthetic/multipleTraces/" + str(sys.argv[3])
        elif sys.argv[2] == 'multiple_traces_large':
            trace_f = ["./benchmarks/synthetic_traces/multi_trace/multipleTraces-syntheticLarge.txt"]
            fileNamePrefix = "synthetic/multipleTraces-large/" + str(sys.argv[3])
        elif sys.argv[2] == 'multiple_traces_small':
            trace_f = ["./benchmarks/synthetic_traces/multi_trace/multipleTraces-syntheticSmall.txt"]
            fileNamePrefix = "synthetic/multipleTraces-small/" + str(sys.argv[3])
        elif sys.argv[2] == 'multiple_traces_mix':
            trace_f = ["./benchmarks/synthetic_traces/multi_trace/RubelMultiTrace.txt"]
            fileNamePrefix = "synthetic/multipleTraces-mix/" + str(sys.argv[3])
        else:
            print ("Wrong type of Synthetic traces is chosen!")
            exit()

    else:
        print ("Wrong type of input trace is chosen!")
        exit()


    if (graph.window and (graph.window <= 0)):
        print("Winodw size must > 0")
        exit()
    if(graph.window):
        print("Added window slicing...window size: ", graph.window_size)
        print()

    log('Reading the message definition file %s... ' % def_f)
    if def_f=="":
        print("Definition file not specified!")
        exit()
    graph.read_message_file(def_f)
    log('Done\n\n')

    traces = None
    log('Reading the trace file(s) %s... ' % trace_f)
    graph.read_trace_file_list(trace_f)
    log('Trace reading and processing status: Done\n\n')

    elapsed_time = time.time() - start_time
    msg = "Trace reading and proc took: %s secs (Wall clock time)" % timedelta(milliseconds=round(elapsed_time*1000))
    print(msg)


    nonZeroEdges = 0
    for edge in graph.edgesArrayForComputingSupport:
        if edge.get_support() != 0:
            nonZeroEdges += 1
    print("Non-zero Edges:", nonZeroEdges)

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
        print("Number of Reduced Function Used =", z3solver.numberOfReducedFunctionUsage)
        print("Number of Relaxed Function Used =", z3solver.numberOfRelaxedFunctionUsage)

    print ("The total number of solutions found:", len(models))
    sorted_models = {}
    for k in sorted(models, key=len, reverse=False):
        sorted_models[k] = models[k]

    count = 0
    total_models = len(sorted_models)  # total number of models found

    save_models = 20
    if total_models < save_models:
        save_models = total_models

    print ("\n\nSeperator............................................\n\n")
   
    myCounter = 0
    total_res1 = 0
    total_res2 = 0
    for model in sorted_models:
        m = model.split(' ')

        if not os.path.exists(solutions_output_path + fileNamePrefix):
            os.makedirs(solutions_output_path + fileNamePrefix)
        if graph.window == True:
            f = open(solutions_output_path + fileNamePrefix + "/sol_" + str(myCounter) + '_size_' + str(len(m)) + "_window_size_" + str(graph.window_size)  + '.txt', 'w')
        else:
            f = open(solutions_output_path + fileNamePrefix + "/sol_" + str(myCounter) + '_size_' + str(len(m)) + '.txt', 'w')
        for i in m:
            i = i.split('_')
            if len(i) > 1:
                G.add_edge(i[0], i[1])
                f.write(i[0] + ' ' + i[1] + "\n")
        f.close()

        if not os.path.exists(results_output_path + fileNamePrefix):
            os.makedirs(results_output_path + fileNamePrefix)
        if graph.window == True:
            resultFileName = results_output_path + fileNamePrefix + "/result_" + str(myCounter) + '_size_' + str(len(m)) + "window_size_" + str(graph.window_size) + '.txt'
        else:
            resultFileName = results_output_path + fileNamePrefix + "/result_" + str(myCounter) + '_size_' + str(len(m)) + '.txt'
        ev = FSAEvaluation(trace_f[0], G, resultFileName)
        res1, res2, notAccepted, finalTotalAccepted, notUsedEdges, pathSizes = ev.Evaluate()
        total_res1 += res1
        total_res2 += res2
                      

        G.clear()
        myCounter = myCounter + 1
        if myCounter >= save_models:  # number of models to select for evaluation, we select smallest 20 for now
            break

    ########################################################################################################################################
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


    solution_dir_name = None  # input('Enter a name for this sub-directory: ')

    log('Solutions found ' + str(len(models)) + '\n')
    exit()
