# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# def print_hi(name):
#     # Use a breakpoint in the code line below to debug your script.
#     print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
from src.annotator.annotator import GraphAnnotator
from src.graph.graph import Graph
from src.solver.z3solver import Z3Solver


def prepare_traces(filename):
    f = open(filename, 'r')
    f1 = f.readlines()
    f.close()
    return f1


if __name__ == '__main__':
    graph = Graph()
    print('Please enter node definition filename: ')
    # def_filename = 'C:\\Users\\abdel\\OneDrive\\Documents\\GitHub\\REU ' \
    #               'Project\\SeqMining-Python\\src\\main\\example.def'  # str(input())
    def_filename = str(input())
    print('Please enter trace filename: ')
    # trace_filename = 'C:\\Users\\abdel\\OneDrive\\Documents\\GitHub\\REU ' \
    #                 'Project\\SeqMining-Python\\src\\main\\example_trace-1'  # str(input())
    trace_filename = str(input())
    graph.generate_graph(def_filename)

    traces = prepare_traces(trace_filename)
    annotator = GraphAnnotator(traces[0], graph)
    annotator.annotate()

    dags = graph.generate_dags()

    for dag in dags:
        annotator = GraphAnnotator(traces[0], dag)
        annotator.annotate()
        dag.remove_cycles()

    graph.remove_cycles()
    z3 = Z3Solver(graph, dags)

    z3.generate_split_solutions()


