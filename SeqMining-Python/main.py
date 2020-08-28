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

    print('Please enter message definition filename: ')
    def_filename = str(input())
    print()
    print('Please enter execution trace filename: ')
    trace_filename = str(input())

    graph.generate_graph(def_filename)
    traces = prepare_traces(trace_filename)

    annotator = GraphAnnotator(traces[0], graph)
    annotator.annotate()
    # graph.print_graph()

    dags = graph.generate_dags()

    for dag in dags:
        annotator = GraphAnnotator(traces[0], dag)
        annotator.annotate()
        dag.remove_cycles()

    graph.remove_cycles()

    z3 = Z3Solver(graph, dags)

    z3.generate_split_solutions()


