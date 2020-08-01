import networkx as nx
import matplotlib.pyplot as plt
from src.opt import opt
from src.wd import wd


class Retimer:
    """
    Performs retiming
    """

    def __init__(self, unopt_graph: nx.DiGraph, print_matrices=False):
        self.graph = self.preprocess_graph(unopt_graph)
        self.wd = wd.WD(graph=self.graph, print_wd=print_matrices)
        self.opt = opt.OPT(self.graph, self.wd.w, self.wd.d)
        self.retimed_graph = None
        self.node_mapping = []

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
        mappings = nx.get_node_attributes(self.graph, 'original-id')
        self.retimed_graph = nx.relabel_nodes(self.opt.graph, mappings)

    def preprocess_graph(self, graph: nx.DiGraph) -> nx.DiGraph:
        """
        Convert delays from strings to int
        :param graph:
        :return:
        """
        graph = nx.convert_node_labels_to_integers(
            graph, first_label=0, label_attribute='original-id')
        component_delay = nx.get_node_attributes(
            G=graph, name='component_delay')
        node_attributes = {node: int(d)
                           for (node, d) in component_delay.items()}
        nx.set_node_attributes(
            G=graph, values=node_attributes, name='component_delay')

        wire_delay = nx.get_edge_attributes(G=graph, name='wire_delay')
        weights = {(v1, v2): int(wire_delay)
                   for ((v1, v2), wire_delay) in wire_delay.items()}
        nx.set_edge_attributes(G=graph, values=weights, name='wire_delay')
        return graph


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
        nx.draw(graph, pos=nx.circular_layout(graph),
                with_labels=True, font_weight='bold')

    nx.draw_networkx_edge_labels(graph, pos=nx.circular_layout(graph))
    plt.show()


def save_graph(g, path): 
    g = g.copy() 
    for v in g.nodes: 
        g.nodes[v]['label'] = f'{v};{g.nodes[v]["component_delay"]}' 
        for e in g.edges: 
            g.edges[e]['label'] = g.edges[e]['wire_delay'] 
            nx.nx_agraph.write_dot(g, path)
