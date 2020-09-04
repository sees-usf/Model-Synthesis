from nltk.tokenize import regexp_tokenize


class GraphAnnotator:

    def __init__(self, original_trace, graph):
        self.graph = graph
        self.original_trace = original_trace
        self.trace_tokens = []

    def annotate(self):
        tokens = regexp_tokenize(self.original_trace, pattern=r'\s|[,:]', gaps=True)

        for token in tokens:
            if token == '-2':
                break

            if token == '-1' or not self.graph.has_node(token):
                continue

            node = self.graph.get_node(token)
            node.set_support(node.get_support() + 1)
            self.trace_tokens.append(token)
            
        for node in self.graph.get_nodes().values():
            if node.get_edges().values():
                for edge in node.get_edges().values():
                    self.annotate_edge(edge)

    def annotate_edge(self, edge):
        instances = 0
        source_symbol_index = edge.get_origin().get_symbol_index()

        for token in self.trace_tokens:
            if not token == '-1':
                if source_symbol_index == token:
                    instances += 1
                elif str(edge) == source_symbol_index + '_' + token and instances > 0:
                    edge.set_edge_support(edge.get_edge_support() + 1)
                    instances -= 1
                    