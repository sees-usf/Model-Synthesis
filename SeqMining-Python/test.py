from src.graph.graph import Graph

g = Graph()
g.generate_graph('./definitions/large_def.txt')

g.print_graph()
print(g.get_roots())
print(g.get_terminal_nodes())
