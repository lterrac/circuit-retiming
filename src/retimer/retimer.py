import networkx as nx
import matplotlib.pyplot as plt
from src.opt import opt
from src.wd import wd
from src.utils import read_dot as rd
from utils.generator import generate_from_correlator


class Retimer:
    """
    Performs retiming
    """

    def __init__(self, unopt_graph: nx.DiGraph):
        self.graph = self.preprocess_graph(unopt_graph)
        self.wd = wd.WD(graph=unopt_graph)
        self.opt = opt.OPT(self.graph, self.wd.w, self.wd.d)

    def retime(self, optimizer='opt1'):
        self.wd.wd()
        self.opt.w = self.wd.w
        self.opt.d = self.wd.d
        self.opt.opt(optimizer)

    @staticmethod
    def _draw_graph(graph: nx.DiGraph):
        nx.draw(graph, pos=nx.circular_layout(graph), with_labels=True, font_weight='bold')
        nx.draw_networkx_edge_labels(graph, pos=nx.circular_layout(graph))
        plt.show()

    @staticmethod
    def preprocess_graph(graph: nx.DiGraph) -> nx.DiGraph:
        """
        Convert delays from strings to int
        :param graph:
        :return:
        """
        component_delay = nx.get_node_attributes(G=graph, name='component_delay')
        node_attributes = {node: int(d) for (node, d) in component_delay.items()}
        nx.set_node_attributes(G=graph, values=node_attributes, name='component_delay')

        wire_delay = nx.get_edge_attributes(G=graph, name='wire_delay')
        weights = {(v1, v2): int(wire_delay) for ((v1, v2), wire_delay) in wire_delay.items()}
        nx.set_edge_attributes(G=graph, values=weights, name='wire_delay')
        return graph


if __name__ == '__main__':
    #G = rd.load_graph('/home/luca/circuit-retiming/graphs/rand-3.dot')
    G = generate_from_correlator(1000)
    retimer = Retimer(unopt_graph=G)
    #retimer._draw_graph(G)
    retimer.retime()
    print(retimer.opt.min_clock)
