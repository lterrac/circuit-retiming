import itertools

import networkx as nx


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
        """
        Optimize the graph choosing between opt1 and opt2 algorithm
        :param optimizer: the algorithm to use
        :return: void
        """
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
        :return: void
        """

        # extract all possible d values from a dictionary of dictionaries and put them in a list
        return sorted(list(set([
            delay for target in [
                targets.values() for targets in self.d.values()
            ] for delay in target
        ])))

    def search_min_clock(self):
        """
        Search the minimum clock cycle with a legal retiming
        :return: void
        """

        # keeps track of the clock already checked with the corresponding retimings
        # it is a kind of cache to save FEAS algorithm execution
        clocks_explored = [(clock_candidate, None, None) for clock_candidate in self._d_range]

        # Execute the binary search
        feasible, self.retimings = self._binary_search_recursive(clocks_explored, 0,
                                                                                 len(clocks_explored) - 1)
        # Apply the legal retiming found to the graph
        self._apply_retiming(self.retimed_graph, self.retimings)

        # Compute the minimum clock cycle
        self.min_clock, _ = self._clock_period(self.retimed_graph)
        print("f {} c {} r {}".format(feasible, self.min_clock, self.retimings))

    def _binary_search_recursive(self, clocks, start, end):
        """
        Custom binary searche function. Instead of finding a specific elements it finds the smallest one with a legal
        retiming by checking itself and its predecessor. The algorithm stops when the element has a legal retiming
        while the predecessor hasn't. Otherwise returns False if no possible retiming exists
        :param clocks: clock cycles to check
        :param start:
        :param end:
        :return: if a clock feasible exists returns the retimings to apply otherwise None
        """
        # TODO check if necessary, test it
        if start > end:
            return False, None

        mid = (start + end) // 2

        feasible, retimings = self._checker(clocks[mid][0])

        # update with values just discovered
        clocks[mid] = (clocks[mid][0], feasible, retimings)

        # exit positively if the possible retiming is the minimum one
        if mid is 0 and feasible is True:
            return feasible, retimings

        if mid is len(clocks) - 1 and feasible is False:
            return feasible, None

        # if the predecessor is not explored do it
        if feasible is True and clocks[mid - 1][1] is None:
            predecessor_feasible, predecessor_retimings = self._checker(clocks[mid - 1][0])
            clocks[mid - 1] = (clocks[mid - 1][0], predecessor_feasible, predecessor_retimings)

        if feasible is True:
            if clocks[mid - 1][1] is False:
                return feasible, retimings
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
        # add extra edges from the extra node to all the other ones
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
                                                   for (source, target, weight) in self.graph.edges.data()],
                                                  weight="wire_delay")

        # set r(v) -> lag to 0 for each node
        nx.set_node_attributes(G=feasibility_graph, values=0, name='lag')

        total_retimings = {node: 0 for node in feasibility_graph.nodes}
        partial_retimings = nx.get_node_attributes(feasibility_graph, 'lag')
        for _ in range(len(feasibility_graph.nodes) - 1):
            # Create Gr with the current values of r
            self._apply_retiming(feasibility_graph, partial_retimings)

            # run CP algorithm to compute the delta_v of all nodes
            clock_threshold, delta_vs = self._clock_period(feasibility_graph)

            # compute the graph incrementing lag of 1 <=> delta_v(v) > clock
            nx.set_node_attributes(G=feasibility_graph,
                                   values={node: (lag['lag'] + 1 if delta_vs[node] > clock else lag['lag'])
                                           for (node, lag) in feasibility_graph.nodes.data()},
                                   name='lag')

            # Since self._apply_retiming uses the retimings of the current iteration and then sets them to 0
            # save the total retimings in order to display them after the search of the minimum clock cycle
            partial_retimings = nx.get_node_attributes(feasibility_graph, 'lag')
            total_retimings = {node: total_retimings.get(node, 0) + partial_retimings.get(node, 0)
                               for node in set(total_retimings).union(partial_retimings)}

        clock_threshold, _ = self._clock_period(feasibility_graph)

        return clock_threshold <= clock, total_retimings

    def _clock_period(self, graph: nx.DiGraph):
        """
        Apply the CP algorithm and compute the circuit clock period
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

        delta_vs = {node: 0 for node in graph.nodes}
        for node in sorted_nodes:
            # If there are no incoming edges set delta_v to d(v)
            delta_vs[node] = no_registers_graph.nodes.data()[node]['component_delay']

            # Otherwise add the maximum d(u) between all the arcs u -> v
            if node in [incident_node for incident_node in
                        [incoming for (_, incoming) in no_registers_graph.in_edges]]:
                delta_vs[node] = delta_vs[node] + max(
                    [delta_vs[outgoing_node]
                     for outgoing_node in
                     [outgoing for (outgoing, _) in no_registers_graph.in_edges(nbunch=node)]])

        return max(list(delta_vs.values())), {node: delta_vs[node] for node in no_registers_graph.nodes}

    @staticmethod
    def _apply_retiming(graph: nx.DiGraph, retimings: dict):
        """
        Apply the retiming to the graph. This function has side effects:
        - resets the lag attribute of the input graph
        :param graph:
        :param retimings:
        :return: the retimed graph
        """
        nx.set_node_attributes(G=graph,
                               values={node: 0 for node in graph.nodes}, name='lag')
        nx.set_edge_attributes(G=graph,
                               values={(v1, v2): (int(graph[v1][v2]['wire_delay']) + retimings[v2] - retimings[v1]) for
                                       (v1, v2)
                                       in
                                       graph.edges}, name='wire_delay')
