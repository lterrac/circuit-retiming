import networkx as nx
import matplotlib.pyplot as plt
from src.opt import opt
from src.utils.generator import generate_from_correlator
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
        self._draw_graph(self.graph)
        self.wd.wd()
        self.opt = opt.OPT(self.graph, self.wd.w, self.wd.d)
        self.opt.opt("opt2")
        self._draw_graph(self.opt.retimed_graph)

    @staticmethod
    def _draw_graph(graph: nx.DiGraph):
        nx.draw(graph, pos=nx.circular_layout(graph), with_labels=True, font_weight='bold')
#        nx.draw_networkx_edge_labels(graph, pos=nx.circular_layout(graph))
#        nx.draw_networkx_labels(graph, pos=nx.circular_layout(graph), labels='component_delay')
        plt.show()


if __name__ == '__main__':
    G = rd.load_graph('graphs/correlator-1.dot')
    G = generate_from_correlator(24)
    retimer = Retimer(unopt_graph=G)
    retimer._draw_graph(G)
    retimer.retime()
