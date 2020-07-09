import networkx as nx

from src.opt import opt
from src.wd import wd
from src.utils import read_dot as rd


class Retimer:
    """
    Performs retiming
    """

    def __init__(self, unopt_graph: nx.DiGraph):
        self.graph = unopt_graph
        self.wd = wd.WD(graph=unopt_graph)
        self.opt = None

    def retime(self):
        self.wd.wd()
        self.opt = opt.OPT(self.graph, self.wd.w, self.wd.d)
        self.opt.opt("opt1")


if __name__ == '__main__':
    G = rd.load_graph('graphs/mini-correlator.dot')

    retimer = Retimer(unopt_graph=G)

    retimer.retime()
