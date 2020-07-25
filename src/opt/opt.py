import itertools
import time

import numpy as np
import networkx as nx


class OPT:
    """
    Class responsible of executing the OPT1 algorithm on a graph
    """

    def __init__(self, graph: nx.DiGraph, w: np.core.ndarray, d: np.core.ndarray):
        self.node_delay = None
        self.graph = graph
        self.retimed_graph = nx.DiGraph(graph)
        self.w = w
        self.d = d
        self.min_clock = 0
        self._d_range = []
        self.retimings = {}
        self._checker = None
        self._wire_delay = 'wire_delay'
        self._component_delay = 'component_delay'
        self._lag = 'lag'

    def opt(self, optimizer: str):
        """
        Optimize the graph choosing between opt1 and opt2 algorithm.
        Print also the total execution time
        :param optimizer: the algorithm to use
        :return: void
        """

        self._d_range = self._create_d_range()

        if optimizer is "opt1":
            self._checker = self._bellman_ford_checker
        else:
            self._checker = self._feas_checker

        init = time.time()
        self.search_min_clock()
        end = time.time()
        print("{} algorithm {}".format(optimizer, end - init))

        print("minimum clock cycle: {}".format(self.min_clock))

    def _create_d_range(self):
        """
        Sort D values, and delete the duplicates
        :return: void
        """

        return np.sort(np.unique(self.d.ravel()))

    def search_min_clock(self):
        """
        Search the minimum clock cycle with a legal retiming
        :return: void
        """
        # keeps track of the clock already checked with the corresponding retimings
        clocks_explored = [(clock_candidate, None, None) for clock_candidate in self._d_range]

        # Execute the binary search
        feasible, self.retimings = self._binary_search_recursive(clocks_explored, 0,
                                                                 len(clocks_explored) - 1)
        # Apply the legal retiming found to the graph
        self._apply_retiming(self.graph, self.retimings)

        # Compute the minimum clock cycle
        self.min_clock, _ = self._clock_period(self.graph)

    def _binary_search_recursive(self, clocks, start, end):
        """
        Custom binary search function. Instead of finding a specific elements it finds the smallest one with a legal
        retiming by checking itself and its predecessor. The algorithm stops when the element has a legal retiming
        while the predecessor hasn't. Otherwise returns False if no possible retiming exists
        :param clocks: clock cycles to check
        :return: if a clock feasible exists returns the retimings to apply otherwise None
        """

        mid = (start + end) // 2
        feasible, retimings = self._checker(clocks[mid][0])

        # update with values just discovered
        clocks[mid] = (clocks[mid][0], feasible, retimings)

        # exit positively if the possible retiming is the minimum one
        if mid is 0 and feasible is True:
            return feasible, retimings

        # if the highest possible clock is not feasible return false
        if mid is len(clocks) - 1 and feasible is False:
            return feasible, None

        # Explore the predecessor
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
        feasibility_graph.add_weighted_edges_from([(target, source, weight[self._wire_delay])
                                                   for (source, target, weight) in self.graph.edges.data()])

        # add second type of constraint from the original graph: r(u) - r(v) <= W(u,v) - 1 if D(u,v) > c
        feasibility_graph.add_weighted_edges_from([(target, source, self.w[int(source)][int(target)] - 1)
                                                   for (source, target) in
                                                   #Do the nodes cartesian product
                                                   list(itertools.product(feasibility_graph.nodes, feasibility_graph.nodes))
                                                   if self.d[int(source)][int(target)] > clock])
        # add extra node for Bellman Ford
        extra_node = 'extra_node'
        feasibility_graph.add_node(extra_node)
        # add extra edges from the extra node to all the other ones
        feasibility_graph.add_weighted_edges_from([(extra_node, node, 0)
                                                   for node in self.graph.nodes])

        try:
            retimings = nx.single_source_bellman_ford_path_length(G=feasibility_graph, source=extra_node)
            retimings.pop(extra_node)
            return True, np.array([x[1] for x in sorted(retimings.items(), key=lambda x: int(x[0]))], dtype=int)
        except nx.exception.NetworkXUnbounded:
            print("Negative cost cycle detected for clock {}...".format(clock))
            return False, None

    def _feas_checker(self, clock: int):
        """
        Check if a legal retiming exists given a clock duration using FEAS algorithm
        :param clock:
        :return: If the retiming is legal and the retiming to apply
        """

        clock_period = self._clock_period
        apply_retiming = self._apply_retiming
        starting_graph = nx.DiGraph(self.graph)

        # set r(v) -> lag to 0 for each node
        nx.set_node_attributes(G=starting_graph, values=0, name=self._lag)

        total_retimings = np.zeros(len(starting_graph), dtype=int)
        delta_vs = np.zeros(len(starting_graph), dtype=int)

        for _ in range(len(starting_graph) - 1):
            # Create Gr with the current values of r
            apply_retiming(starting_graph, delta_vs)

            # run CP algorithm to compute the delta_v of all nodes
            clock_threshold, delta_vs = clock_period(starting_graph)

            # compute the retimings incrementing lag of 1 <=> delta_v(v) > clock
            delta_vs = np.where(delta_vs > clock, 1, 0)
            if bool(np.any(delta_vs)) is True:
                total_retimings = np.add(total_retimings, delta_vs)

        apply_retiming(starting_graph, delta_vs)
        clock_threshold, _ = clock_period(starting_graph)
        return bool(clock_threshold <= clock), total_retimings

    def _clock_period(self, graph: nx.DiGraph):
        """
        Apply the CP algorithm and compute the circuit clock period
        :param graph:
        :return:
        """
        wire_delay = self._wire_delay

        # Initialize all delta_v with the component delay
        nodes_delay = np.copy(self.d.diagonal())

        # Pick only the edges with w(e) = 0. Use the adjacency matrix to take advantage of numpy arrays
        no_registers_adjacency = np.where(nx.to_numpy_array(graph, nodelist=sorted(graph.nodes, key=int), dtype=int, weight=wire_delay, nonedge=-1,) == 0, 1, 0)

        # Create a graph and do the topological sort
        no_registers_graph = nx.from_numpy_matrix(no_registers_adjacency, create_using=nx.DiGraph)

        sorted_nodes = nx.topological_sort(no_registers_graph)

        for node in sorted_nodes:
            node = int(node)

            # Get incident edges
            incident_edges = no_registers_adjacency[:, node]

            try:
                incident_edges = np.where(incident_edges > 0)
            except:
                incident_edges = None

            # In case of incident edges add the maximum d(u) between all the arcs u -> v
            if incident_edges is not None and incident_edges[0].size > 0:
                nodes_delay[node] = nodes_delay[node] + np.max(nodes_delay[incident_edges])

        return np.max(nodes_delay), nodes_delay

    def _apply_retiming(self, graph: nx.DiGraph, retimings):
        """
            Apply the retiming to the graph.
            :param graph:
            :param retimings:
            :return: the retimed graph
            """
        nx.set_edge_attributes(G=graph,
                               values={(v1, v2): (graph[v1][v2][self._wire_delay] + retimings[int(v2)] - retimings[int(v1)])
                                   for
                                   (v1, v2)
                                   in
                                   graph.edges}, name=self._wire_delay)
