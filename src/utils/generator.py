import networkx as nx
import matplotlib.pyplot as plt
import numpy.random as rnd
import numpy as np


def generate_from_correlator(nodes: int):
    """
    Generates a circuit using the correlator schema.

    ----- n + 1      ---> n + 3
            |     +         |
    -----   n        ---> n + 2
    The total number of nodes will be nodes + 1 in order to add the
    last part of the correlator:

    ----- n + 1
            |   \
    -----   n -- n + 2

    :param nodes: the desidered number of nodes in the circuit
    :return:
    """
    correlator = nx.DiGraph()
    correlator.add_nodes_from(['0', '1'])
    nx.set_node_attributes(correlator, str(3), 'component_delay')
    correlator.add_nodes_from([('2', {'component_delay': str(7)})])
    correlator.add_edges_from([('1', '2'), ('2', '0')])
    nx.set_edge_attributes(correlator, str(0), 'wire_delay')
    correlator.add_edges_from([('0', '1', {'wire_delay': str(1)})])
    up = 2
    down = 1

    for i in range(up + 1, nodes, 2):
        correlator.add_nodes_from([(str(i), {'component_delay': str(3)}), (str(i + 1), {'component_delay': str(7)})])
        correlator.add_edges_from([(str(down), str(i), {'wire_delay': str(1)}),
                                   (str(down), str(up), {'wire_delay': str(0)}),
                                   (str(i + 1), str(up), {'wire_delay': str(0)})
                                   ])
        up = i + 1
        down = i

    correlator.add_nodes_from([(str(up + 1), {'component_delay': str(7)})])
    correlator.add_edges_from([(str(down), str(up + 1), {'wire_delay': str(1)})])
    correlator.add_edges_from([(str(down), str(up), {'wire_delay': str(0)})])
    correlator.add_edges_from([(str(up + 1), str(up), {'wire_delay': str(0)})])

    return correlator


def random_generator(n: int, k: int):
    """
    Generates a random connected graph with all the node attributes set to 3 and the edge weights to 1
    :param n: number of nodes
    :param k:
    :return:
    """
    # Generate an almost complete graph
    graph = nx.DiGraph(nx.MultiDiGraph.to_directed(nx.random_k_out_graph(n, k, self_loops=False, alpha=4000)))

    # Delete incoming arcs from 0 -> starting node
    graph.remove_edges_from([(v1, v2) for (v1, v2) in graph.in_edges if v2 is 0])

    # Connect the first and the last node
    graph.add_edges_from([(0, max(graph.nodes))])

    print(len(graph.edges))
    for node in graph.nodes:
        incoming = [(v1, v2) for (v1, v2) in graph.in_edges if v2 == node]
        deleted_nodes = 0
        # Randomly decide if an edge has to be kept or discarded
        for edge in incoming:
            keep = np.average(rnd.binomial(1, 0.55, 5))
            # Delete only if the nodes has more than one incoming and outcoming edge
            if keep >= 0.4 and deleted_nodes < len(incoming) - 1 and len(graph.edges(edge[0])) > 1:
                graph.remove_edge(edge[0], edge[1])
                deleted_nodes = deleted_nodes + 1

    # Delete node cycles in order to save the graph as strict
    node_cycles = [(u, v) for (u, v) in graph.edges() if u in graph[v]]
    graph.remove_edges_from(node_cycles)

    # Connect every arc to the first one
    graph.add_edges_from([(node, 0) for node in graph.nodes if node is not 0])
    # Set the attributes
    nx.set_node_attributes(graph, 3, 'component_delay')
    nx.set_edge_attributes(graph, 1, 'wire_delay')

    # Save it only if it is connected
    if nx.is_weakly_connected(graph):
        nx.nx_agraph.write_dot(graph,
                               '/home/luca/circuit-retiming/testsetbug/np-{}.dot'.format(n, n))


def performance_generator(n: int):
    """
    Creates a directed circular graph used to do the performance testing of the two algorithms which has
    the same number of nodes and edges
    :param n: the graph size
    :return:
    """
    # must make a copy because the graph is frozen
    graph = nx.DiGraph(nx.to_directed(nx.path_graph(n)))
    edges_to_delete = list(zip(list(graph.nodes)[1:], list(graph.nodes)[:-1]))
    graph.remove_edges_from(edges_to_delete)
    graph.add_edge(max(graph.nodes), 0)
    nx.set_node_attributes(graph, 3, 'component_delay')
    nx.set_edge_attributes(graph, 1, 'wire_delay')
    nx.nx_agraph.write_dot(graph, '/home/luca/circuit-retiming/graphs/perf-{}.dot'.format(str(n)))
