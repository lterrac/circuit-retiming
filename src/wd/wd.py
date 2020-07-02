import networkx as nx

from src.utils import read_dot as rd


class WD:
    """
    Class responsible of executing the WD algorithm on a graph
    """

    def __init__(self, graph: nx.DiGraph):
        self._graph = graph
        self._weighted_graph = nx.DiGraph()

    def wd(self):
        """
        Executes the three steps of the WD algorithm
        :return: Matrices W and D
        """
        self._weight_edge()
        self._all_pairs_shortest_path()
        return self.compute_wd()

    def _weight_edge(self):
        """
        Weight the edge with (w, -d) where:
        - w: Arc cost
        - d: Logic component delay
        """
        # Change the component delay sign (-d)
        component_delay = nx.get_node_attributes(G=self._graph, name='component_delay')
        component_delay = {node: -1 * int(d) for (node, d) in component_delay.items()}
        self._weighted_graph.add_nodes_from(self._graph.nodes())

        # Get wire delay (w)
        wire_delay = nx.get_edge_attributes(G=self._graph, name='wire_delay')

        # Create the weight (w,-d)
        weights = {(v1, v2): (int(wire_delay), component_delay[v1]) for ((v1, v2), wire_delay) in wire_delay.items()}
        self._weighted_graph.add_edges_from(weights)
        nx.set_edge_attributes(G=self._weighted_graph, values=weights, name='weight')
        print(self._weighted_graph.edges.data())
     #   print(nx.get_edge_attributes(self._weighted_graph, 'aa'))

        #self._weighted_graph.add_weighted_edges_from(self._weighted_graph, weight='aa')


    def _all_pairs_shortest_path(self):
        """
        Resolve an all pair shortest path problem
        """
        pass

    def compute_wd(self):
        pass


if __name__ == '__main__':
    G = rd.load_graph('graphs/correlator.dot')

    wd = WD(graph=G)

    wd.wd()
