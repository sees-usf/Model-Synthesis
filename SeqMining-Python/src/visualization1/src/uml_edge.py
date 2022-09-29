
class Edge:
    def __init__(self, src_node, dest_node, support):
        self.id = src_node.get_index() + "_" + dest_node.get_index()
        self.src_node = src_node
        self.dest_node = dest_node
        self.support = support

    def __str__(self):
        return self.id

    def get_id(self):
        return self.id

    def get_src_node(self):
        return self.src_node

    def get_dest_node(self):
        return self.dest_node

    def get_support(self):
        return self.support

    def set_support(self, value):
        self.support = value


