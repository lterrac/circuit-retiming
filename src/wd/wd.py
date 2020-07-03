import itertools

import networkx as nx

from src.utils import read_dot as rd


class WD:
    """
    Class responsible of executing the WD algorithm on a graph
    """

    def __init__(self, graph: nx.DiGraph):
        self._graph = graph
        self._weighted_graph = nx.DiGraph()
        self.w = {}
        self.d = {}


    def wd(self):
        """
        Executes the three steps of the WD algorithm
        :return: Matrices W and D
        """
        self._weight_edges()
        self._all_pairs_shortest_path()
        return self.compute_wd()

    def _weight_edges(self):
        """
        Weight the edge with (w, -d) where:
        - w: Arc cost
        - d: Logic component delay
        """

        component_delay = nx.get_node_attributes(G=self._graph, name='component_delay')

        # Used in _custom_weight function(). Get the highest gate delay
        self._max_component_delay = max([int(d) for (node, d) in component_delay.items()])

        # Change the component delay sign (-d)
        component_delay = {node: -1 * int(d) for (node, d) in component_delay.items()}
        self._weighted_graph.add_nodes_from(self._graph.nodes())

        # Get wire delay (w)
        wire_delay = nx.get_edge_attributes(G=self._graph, name='wire_delay')

        # Create the weight (w,-d)
        weights = {(v1, v2): (int(wire_delay), component_delay[v1]) for ((v1, v2), wire_delay) in wire_delay.items()}
        self._weighted_graph.add_edges_from(weights)
        nx.set_edge_attributes(G=self._weighted_graph, values=weights, name='weight')

    def _custom_weight(self, attributes):
        """
        Define a new weight by combining w and -d using the maximum value of d in order to prioritize the comparison
        first on w  (pick the lowest) and then on d (pick the highest one since the original comparison is done with -d).
        :param attributes:
        :return:
        """

        return attributes['weight'][0] * self._max_component_delay + (
                self._max_component_delay - attributes['weight'][1])

    def _all_pairs_shortest_path(self):
        """
        Resolve an all pair shortest path problem
        """
        self.all_pairs = dict(nx.all_pairs_dijkstra_path(G=self._weighted_graph,
                                                         weight=lambda v1, v2, attributes: self._custom_weight(
                                                             attributes)))

    def compute_wd(self):

        for (src, targets) in self.all_pairs.items():
            for (target, path) in targets.items():
                if src not in self.w:
                    self.w[src] = {}
                # add also the source node to compute the total w
                path.insert(0, src)
                self.w[src][target] = self.compute_w(path)

        for (src, targets) in self.w.items():
            print(str(targets))


    def compute_w(self, path):
        """
        sum all the wire delays along a path
        :param path:
        :return:
        """
        return sum([self._weighted_graph[v1][v2]['weight'][0] for v1, v2 in zip(path, path[1:]) if v2 in self._weighted_graph[v1]])




if __name__ == '__main__':
    G = rd.load_graph('graphs/correlator.dot')

    wd = WD(graph=G)

    wd.wd()
