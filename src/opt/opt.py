import itertools

import networkx as nx


def _apply_retiming(graph: nx.DiGraph, retimings: dict):
    """
    Apply the retiming to the graph
    :param graph: 
    :param retimings: 
    :return: 
    """
    nx.set_node_attributes(G=graph,
                           values={node: 0 for node in graph.nodes}, name='lag')
    nx.set_edge_attributes(G=graph,
                           values={(v1, v2): (int(graph[v1][v2]['wire_delay']) + retimings[v2] - retimings[v1]) for (v1, v2)
                                   in
                                   graph.edges}, name='wire_delay')


class OPT:
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
        self._checker = None

    def opt(self, optimizer: str):
        self._d_range = self._create_d_range()

        if optimizer is "opt1":
            self._checker = self._bellman_ford_checker
        else:
            self._checker = self._feas_checker

        self.search_min_clock()
        print("minimum clock cycle: {}".format(self.min_clock))

    def _create_d_range(self):
        """
        Sort D values, and delete the duplicates
        :return:
        """

        # extract all possible d values from a dictionary of dictionaries and put them in a list
        return sorted(list(set([
            delay for target in [
                targets.values() for targets in self.d.values()
            ] for delay in target
        ])))

    def search_min_clock(self):
        """
        Use binary search
        :return:
        """
        # keeps track of the clock already checked with the corresponding retimings
        clocks_explored = [(clock_candidate, None, None) for clock_candidate in self._d_range]

        feasible, self.min_clock, self.retimings = self._binary_search_recursive(clocks_explored, 0,
                                                                                 len(clocks_explored) - 1)
        _apply_retiming(self.retimed_graph, self.retimings)
        print("f {} c {} r {}".format(feasible, self.min_clock, self.retimings))
        return

    def _binary_search_recursive(self, clocks, start, end):
        """

        :param clocks:
        :param start:
        :param end:
        :return: if a clock feasible exists, the clock period, the retimings to apply
        """
        # TODO check if necessary, test it
        if start > end:
            return False, None, None

        mid = (start + end) // 2
        feasible, retimings = self._checker(clocks[mid][0])

        # update with values just discovered
        clocks[mid] = (clocks[mid][0], feasible, retimings)

        # exit positively if the possible retiming is the minimum one
        if mid is 0 and feasible is True:
            return feasible, clocks[mid], retimings

        if mid is len(clocks) - 1 and feasible is False:
            return feasible, None, None

        # if the predecessor is not explored do it
        if feasible is True and clocks[mid - 1][1] is None:
            predecessor_feasible, predecessor_retimings = self._checker(clocks[mid - 1][0])
            clocks[mid - 1] = (clocks[mid - 1][0], predecessor_feasible, predecessor_retimings)

        if feasible is True:
            if clocks[mid - 1][1] is False:
                return feasible, clocks[mid][0], retimings
            else:
                return self._binary_search_recursive(clocks, start, mid - 1)
        else:
            return self._binary_search_recursive(clocks, mid + 1, end)

    def _bellman_ford_checker(self, clock: int):
        """
        Check if a legal retiming exists given a clock duration using Bellman Ford algorithm
        :param clock:
        :return: If the retiming is legal and the retiming to apply
        """
        feasibility_graph = nx.DiGraph()
        feasibility_graph.add_nodes_from(self.graph.nodes)

        # add first type of constraint from the original graph -> r(u) - r(v) <= w(e), so create arc v -> u
        feasibility_graph.add_weighted_edges_from([(target, source, int(weight['wire_delay']))
                                                   for (source, target, weight) in self.graph.edges.data()])
        # add second type of constraint from the original graph: r(u) - r(v) <= W(u,v) - 1 if D(u,v) > c
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

    def _feas_checker(self, clock: int):
        """
        Check if a legal retiming exists given a clock duration using FEAS algorithm
        :param clock:
        :return: If the retiming is legal and the retiming to apply
        """
        feasibility_graph = nx.DiGraph()
        feasibility_graph.add_nodes_from(self.graph.nodes)
        feasibility_graph.add_weighted_edges_from([(source, target, int(weight['wire_delay']))
                                                   for (source, target, weight) in self.graph.edges.data()], weight="wire_delay")

        # set r(v) to 0 for each node
        nx.set_node_attributes(G=feasibility_graph, values=0, name='lag')

        for i in range(len(feasibility_graph.nodes) - 1):
            _apply_retiming(feasibility_graph, {node: lag['lag'] for (node, lag) in feasibility_graph.nodes.data()})
            # run CP algorithm to compute delta_v
            clock_threshold, possible_retimings = self._clock_period(feasibility_graph, metric="component_delay")
            # compute the graph incrementing lag of 1 <=> delta_v(v) > clock
            nx.set_node_attributes(G=feasibility_graph,
                                   values={node: (lag['lag'] + 1 if possible_retimings[node] > clock else lag['lag'])
                                           for (node, lag) in feasibility_graph.nodes.data()},
                                   name='lag')
        clock_threshold, _ = self._clock_period(feasibility_graph, metric="lag")

        return clock_threshold <= clock, {node: lag['lag'] for (node, lag) in feasibility_graph.nodes.data()}

    def _clock_period(self, graph: nx.DiGraph, metric: str):
        """
        Apply the CP algorithm
        :param graph:
        :return:
        """

        no_registers_graph = nx.DiGraph()
        no_registers_graph.add_nodes_from(graph)

        nx.set_node_attributes(G=no_registers_graph, values={node: {"component_delay": self.d[node][node]}
                                                             for node in graph.nodes})

        # Pick only the edges with w(e) = 0
        no_registers_graph.add_weighted_edges_from([(source, target, 0)
                                                    for (source, target, weight) in graph.edges.data()
                                                    if int(weight['wire_delay']) is 0])

        sorted_nodes = nx.topological_sort(no_registers_graph)

        clocks = {node: 0 for node in graph.nodes}
        for node in sorted_nodes:
            clocks[node] = no_registers_graph.nodes.data()[node]['component_delay']
            if node in [incident_node for incident_node in
                        [incoming for (_, incoming) in no_registers_graph.in_edges]]:

                clocks[node] = clocks[node] + max(
                    [clocks[outgoing_node]
                     for outgoing_node in
                     [outgoing for (outgoing, _) in no_registers_graph.in_edges(nbunch=node)]])

        return max(list(clocks.values())), {node: clocks[node] for node in no_registers_graph.nodes}
