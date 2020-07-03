import networkx as nx


class OPT1:
    """
    Class responsible of executing the OPT1 algorithm on a graph
    """

    def __init__(self, graph: nx.DiGraph, w: dict, d: dict):
        self.graph = graph
        self.w = w
        self.d = d

    def opt(self):
        self.sort_d()
        self.search_min_clock()
        self.apply_retiming()

    def sort_d(self):
        pass

    def search_min_clock(self):
        pass

    def apply_retiming(self):
        pass

