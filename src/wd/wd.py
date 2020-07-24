import networkx as nx
import numpy as np


class WD:
    """
    Class responsible of executing the WD algorithm on a graph
    """

    def __init__(self, graph: nx.DiGraph):
        self._graph = graph
        self._weighted_graph = nx.DiGraph()
        self._matrix_dimension = len(graph)
        self.w = None
        self.d = None
        self.component_delay = 'component_delay'
        self.wire_delay = 'wire_delay'
        self.weight = 'weight'

    def wd(self):
        """
        Executes the three steps of the WD algorithm
        :return: Matrices W and D
        """
        self._weight_edges()
        self._all_pairs_shortest_path()
        self._compute_wd()

    def _weight_edges(self):
        """
        Weight the edge with (w, -d) where:
        - w: Arc cost
        - d: Logic component delay
        """

        component_delay = nx.get_node_attributes(G=self._graph, name=self.component_delay)

        # Used in _custom_weight function(). Get the highest gate delay
        self._max_component_delay = max([d for (node, d) in component_delay.items()])

        node_attributes = {node: d for (node, d) in component_delay.items()}

        # Change the component delay sign (-d)
        component_delay = {node: -1 * d for (node, d) in node_attributes.items()}

        # Add nodes and import attributes for d computation
        self._weighted_graph.add_nodes_from(self._graph.nodes())
        nx.set_node_attributes(G=self._weighted_graph, values=node_attributes, name=self.component_delay)

        # Get wire delay (w)
        wire_delay = nx.get_edge_attributes(G=self._graph, name=self.wire_delay)
        # Create the weight (w,-d)
        weights = {(v1, v2): (wire_delay, component_delay[v1]) for ((v1, v2), wire_delay) in wire_delay.items()}
        self._weighted_graph.add_edges_from(weights)
        nx.set_edge_attributes(G=self._weighted_graph, values=weights, name=self.weight)

    def _custom_weight(self, attributes):
        """
        Define a new weight by combining w and -d using the maximum value of d in order to prioritize the comparison
        first on w  (pick the lowest) and then on d (pick the highest one since the original comparison is done with -d).
        Formula w * max(all component delays) + max(all component delays) - (-d)
        :param attributes:
        :return:
        """

        return attributes[self.weight][0] * self._max_component_delay + (self._max_component_delay - attributes[self.weight][1])

    def _all_pairs_shortest_path(self):
        """
        Resolve an all pair shortest path problem
        """
        self.all_pairs = dict(nx.all_pairs_dijkstra_path(G=self._weighted_graph,
                                                         weight=lambda v1, v2, attributes: self._custom_weight(
                                                             attributes)))

    def _compute_wd(self):
        mat_dim = self._matrix_dimension
        w = np.zeros((mat_dim, mat_dim), dtype=int)
        d = np.zeros((mat_dim, mat_dim), dtype=int)
        compute_w = self._compute_w
        compute_d = self._compute_d

        for (src, targets) in self.all_pairs.items():
            for (target, path) in targets.items():
                # add also the source node to compute the total w and d
                path.insert(0, src)
                w[int(src)][int(target)] = compute_w(path)
                d[int(src)][int(target)] = compute_d(path)

        self.w = w
        self.d = d

    def _compute_w(self, path: list):
        """
        :param path: path from the source to the target node
        :return: the sum all the wire delays along a path
        """
        grapg = self._weighted_graph
        return sum([grapg[v1][v2][self.weight][0] for v1, v2 in zip(path, path[1:])
                    if v2 in grapg[v1]])

    def _compute_d(self, path: list):
        """
        :param path: path from the source to the target node
        :return: the sum all the gate delays along a path plus the target one's
        """
        target = path[-1]
        return self._weighted_graph.nodes[target][self.component_delay] - sum(
            [self._weighted_graph[v1][v2][self.weight][1] for v1, v2 in zip(path, path[1:])
             if v2 in self._weighted_graph[v1]])
