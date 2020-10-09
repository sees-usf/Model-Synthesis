class Edge:
    def __init__(self, origin, destination):
        self.edge_id = origin.get_symbol_index() + "_" + destination.get_symbol_index()
        self.origin = origin
        self.destination = destination
        self.edge_support = 0

    def __str__(self):
        return self.edge_id

    def get_origin(self):
        return self.origin

    def get_destination(self):
        return self.destination

    def get_edge_support(self):
        return self.edge_support

    def get_support(self):
        return self.edge_support

    def set_edge_support(self, value):
        self.edge_support = value

    def set_support(self, value):
        self.edge_support = value

    def equals(self, edge):
        return self.edge_id == edge.edge_id
