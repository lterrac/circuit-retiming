import networkx as nx
import matplotlib.pyplot as plt
import itertools

class OPT1:
    """
    Class responsible of executing the OPT1 algorithm on a graph
    """

    def __init__(self, graph: nx.DiGraph, w: dict, d: dict):
        self.graph = graph
        self.w = w
        self.d = d
        self.min_clock = 0
        self._d_range = []

    def opt(self):
        self._d_range = self._create_d_range()
        self._search_min_clock()
        self._apply_retiming()

    def _create_d_range(self):
        """
        Sort D values, and delete the duplicates
        :return:
        """

        # extract d from a dictionary of dictionaries in a list
        return sorted(list(set([delay for target in [
            targets.values() for targets in self.d.values()
        ]
                                for delay in target])))

    def _search_min_clock(self):
        feasible, retimings = self._check_clock_feasibility(13)
        if feasible is True:
            print(retimings)

    def _check_clock_feasibility(self, clock: int):
        clock_feasible = False
        feasibility_graph = nx.DiGraph()
        feasibility_graph.add_nodes_from(self.graph.nodes)
        print(feasibility_graph.nodes)

        # add first type of constraint from the original graph -> r(u) - r(v) <= w(e)
        feasibility_graph.add_weighted_edges_from([(source, target, int(weight['wire_delay']))
                                                   for (source, target, weight) in self.graph.edges.data()])

        # add first type of constraint from the original graph -> r(u) - r(v) <= W(u,v) - 1 if D(u,v) > c
        feasibility_graph.add_weighted_edges_from([(source, target, self.w[source][target] - 1)
                                                   for (source, target) in list(itertools.product(feasibility_graph.nodes, feasibility_graph.nodes))
                                                   if self.d[source][target] > clock])

        # add extra node for Bellman Ford
        extra_node = 'extra_node'
        feasibility_graph.add_node(extra_node)
        # add extra edges
        feasibility_graph.add_weighted_edges_from([(extra_node, node, 0)
                                                   for node in self.graph.nodes])

        try:
            retimings = nx.single_source_bellman_ford(G=feasibility_graph, source=extra_node)
            return True, retimings
        except nx.exception.NetworkXUnbounded:
            print("Negative cost cycle detected...")
            return False, None

    def _apply_retiming(self):
        pass
