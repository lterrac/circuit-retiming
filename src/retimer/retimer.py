import networkx as nx

from src.opt import opt1
from src.wd import wd


class Retimer:
    """
    Performs retiming
    """

    def __init__(self, unopt_graph: nx.DiGraph):
        self.graph = unopt_graph
        self.wd = wd.WD(graph=unopt_graph)
        self.opt1 = None

    def retime(self):
        self.wd.wd()
        self.opt1 = opt1.OPT1(self.graph, self.wd.w, self.wd.d)
        self.opt1.opt()