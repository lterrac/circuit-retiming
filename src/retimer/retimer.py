import networkx as nx
import matplotlib.pyplot as plt
from src.opt import opt
from src.wd import wd


class Retimer:
    """
    Performs retiming
    """

    def __init__(self, unopt_graph: nx.DiGraph, print_matrices=False):
        self.graph = unopt_graph
        self.wd = wd.WD(graph=unopt_graph, print_wd=print_matrices)
        self.opt = opt.OPT(self.graph, self.wd.w, self.wd.d)
        self.retimed_graph = None

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
        self.retimed_graph = self.opt.graph


def draw_graph(graph: nx.DiGraph, draw_node_labels=False):
    """
    Draws the graph passed as input with its labels.
    :param draw_node_labels: if set draws the component delay instead of the node name
    :param graph:
    :return:
    """
    if draw_node_labels is True:
        nx.draw(graph, pos=nx.circular_layout(graph), font_weight='bold')
        nx.draw_networkx_labels(graph, pos=nx.circular_layout(graph),
                                labels=nx.get_node_attributes(graph, 'component_delay'))
    else:
        nx.draw(graph, pos=nx.circular_layout(graph), with_labels=True, font_weight='bold')

    nx.draw_networkx_edge_labels(graph, pos=nx.circular_layout(graph))
    plt.show()
