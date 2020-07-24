import networkx as nx
import matplotlib.pyplot as plt
from src.opt import opt
from src.wd import wd


class Retimer:
    """
    Performs retiming
    """

    def __init__(self, unopt_graph: nx.DiGraph):
        self.graph = unopt_graph
        self.wd = wd.WD(graph=unopt_graph)
        self.opt = opt.OPT(self.graph, self.wd.w, self.wd.d)

    def retime(self, optimizer='opt1'):
        """
        Executes WD and OPT algorithms
        :param optimizer:
        :return:
        """
        self.wd.wd()
        self.opt.w = self.wd.w
        self.opt.d = self.wd.d
        self.opt.opt(optimizer)

    @staticmethod
    def _draw_graph(graph: nx.DiGraph):
        nx.draw(graph, pos=nx.circular_layout(graph), with_labels=True, font_weight='bold')
        nx.draw_networkx_edge_labels(graph, pos=nx.circular_layout(graph))
        plt.show()
