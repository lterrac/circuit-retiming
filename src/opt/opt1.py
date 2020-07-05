import itertools

import networkx as nx


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
        self.retimed_graph = nx.DiGraph(self.graph)
        self.retimings = {}

    def opt(self):
        self._d_range = self._create_d_range()
        self._search_min_clock()
        self._apply_retiming()

        print("minimum clock cycle: {}".format(self.min_clock))

    def _create_d_range(self):
        """
        Sort D values, and delete the duplicates
        :return:
        """

        # extract d from a dictionary of dictionaries in a list
        return sorted(list(set([
            delay for target in [
                targets.values() for targets in self.d.values()
            ] for delay in target
        ])))

    def _search_min_clock(self):
        """
        Use binary search
        :return:
        """
        # keeps track of the clock already checked
        clocks_explored = [(clock_candidate, None) for clock_candidate in self._d_range]

        feasible = self.binary_search_recursive(clocks_explored, 0, len(clocks_explored))

        feasible, self.retimings = self._check_clock_feasibility(13)
        return

    def binary_search_recursive(self, array, start, end):
        if start > end:
            return False

        mid = (start + end) // 2
        feasible, retimings = self._check_clock_feasibility(array[mid][0])
        array[mid] = (array[mid][1], feasible)

        if array[mid - 1][1] is None:
            predecessor_feasible, _ = self._check_clock_feasibility(array[mid - 1][0])
            array[mid] = (array[mid][1], predecessor_feasible)
            # TODO implement retimings cache

        if feasible is True:
            if array[mid - 1][1] is False:
                self.min_clock = array[mid][0]
                self.retimings = retimings
                return True
            else:
                return self.binary_search_recursive(array, start, mid - 1)
        else:
            return self.binary_search_recursive(array, mid + 1, end)

    def _check_clock_feasibility(self, clock: int):
        """
        Check if a legal retiming exists given a clock duration
        :param clock:
        :return: If the retiming is legal and the retiming to apply
        """
        feasibility_graph = nx.DiGraph()
        feasibility_graph.add_nodes_from(self.graph.nodes)

        # add first type of constraint from the original graph -> r(u) - r(v) <= w(e), so create arc v -> u
        feasibility_graph.add_weighted_edges_from([(target, source, int(weight['wire_delay']))
                                                   for (source, target, weight) in self.graph.edges.data()])
        # add first type of constraint from the original graph: r(u) - r(v) <= W(u,v) - 1 if D(u,v) > c
        feasibility_graph.add_weighted_edges_from([(target, source, self.w[source][target] - 1)
                                                   for (source, target) in list(
                itertools.product(feasibility_graph.nodes, feasibility_graph.nodes))
                                                   if self.d[source][target] > clock])
        # add extra node for Bellman Ford
        extra_node = 'extra_node'
        feasibility_graph.add_node(extra_node)
        # add extra edges
        feasibility_graph.add_weighted_edges_from([(extra_node, node, 0)
                                                   for node in self.graph.nodes])

        try:
            retimings = nx.single_source_bellman_ford_path_length(G=feasibility_graph, source=extra_node)
            retimings.pop('extra_node')
            return True, retimings
        except nx.exception.NetworkXUnbounded:
            print("Negative cost cycle detected for clock {}...".format(clock))
            return False, None

    def _apply_retiming(self):
        nx.set_node_attributes(G=self.retimed_graph,
                               values={node: self.retimings[node] for node in self.retimed_graph.nodes}, name='lag')
        nx.set_edge_attributes(G=self.retimed_graph,
                               values={(v1, v2): (self.w[v1][v2] + self.retimings[v2] - self.retimings[v1]) for (v1, v2) in
                                       self.retimed_graph.edges}, name='registers')
        print(str(nx.get_edge_attributes(self.retimed_graph, 'registers')))
