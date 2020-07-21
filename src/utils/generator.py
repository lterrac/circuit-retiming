import networkx as nx
import matplotlib.pyplot as plt
import numpy.random as rnd
import numpy as np

import src.utils.read_dot as rd


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
    correlator.add_nodes_from(['0', '1', '2'])
    nx.set_node_attributes(correlator, str(3), 'component_delay')
    correlator.add_edges_from([('0', '1'), ('2', '0'), ('1', '2')])
    nx.set_edge_attributes(correlator, str(0), 'wire_delay')

    up = 2
    down = 1

    for i in range(up + 1, nodes, 2):
        print(i)
        correlator.add_nodes_from([(str(i), {'component_delay': str(3)}), (str(i + 1), {'component_delay': str(7)})])
        correlator.add_edges_from([(str(down), str(i), {'wire_delay': str(1)}),
                                   (str(down), str(up), {'wire_delay': str(0)}),
                                   (str(i + 1), str(up), {'wire_delay': str(0)})
                                   ])
        print(i)
        print(down)
        up = i + 1
        down = i

    correlator.add_node(str(up + 1))
    nx.set_node_attributes(correlator, str(3), 'component_delay')
    correlator.add_edges_from([(str(down), str(up + 1), {'wire_delay': str(1)})])
    correlator.add_edges_from([(str(up + 1), str(up), {'wire_delay': str(0)})])
    print(correlator.nodes.data())
    print(correlator.edges.data())
    nx.draw(correlator, pos=nx.circular_layout(correlator), with_labels=True, font_weight='bold')
    plt.show()

    return correlator


def random_generator(n: int, k: int, number_of_test: int):
    graph = nx.DiGraph(nx.MultiDiGraph.to_directed(nx.random_k_out_graph(n, k, self_loops=False, alpha=4000)))

    # Delete incoming arcs from 0 -> starting node
    graph.remove_edges_from([(v1, v2) for (v1, v2) in graph.in_edges if v2 is 0])

    graph.add_edges_from([(0, max(graph.nodes))])

    print(len(graph.edges))
    for node in graph.nodes:
        incoming = [(v1, v2) for (v1, v2) in graph.in_edges if v2 == node]
        deleted_nodes = 0
        for edge in incoming:
            keep = np.average(rnd.binomial(1, 0.55, 5))
            if keep >= 0.4 and deleted_nodes < len(incoming) - 1 and len(graph.edges(edge[0])) > 1:
                graph.remove_edge(edge[0], edge[1])
                deleted_nodes = deleted_nodes + 1

    node_cycles = [(u, v) for (u, v) in graph.edges() if u in graph[v]]
    print(len(graph.edges))
    graph.remove_edges_from(node_cycles)
    graph.add_edges_from([(node, 0) for node in graph.nodes if node is not 0])
    nx.set_node_attributes(graph, 3, 'component_delay')
    nx.set_edge_attributes(graph, 1, 'wire_delay')
    print(len(graph.edges))
    nx.draw(nx.to_directed(graph), pos=nx.circular_layout(graph), with_labels=True, font_weight='bold')
    plt.show()
    if nx.is_weakly_connected(graph):
        print("yes")
        nx.nx_agraph.write_dot(graph,
                               '/home/luca/circuit-retiming/testsetbug/np-{}.dot'.format(n, n))
        if number_of_test % 10 == 0:
            print("{} done".format(number_of_test))
            nx.draw(nx.to_directed(graph), pos=nx.circular_layout(graph), with_labels=True, font_weight='bold')
            plt.show()
        return 1
    else:
        return 0


def performance_generator(n: int):
    # must make a copy because the graph is frozen
    graph = nx.DiGraph(nx.to_directed(nx.path_graph(n)))
    edges_to_delete = list(zip(list(graph.nodes)[1:], list(graph.nodes)[:-1]))
    graph.remove_edges_from(edges_to_delete)
    graph.add_edge(max(graph.nodes), 0)
    nx.set_node_attributes(graph, 3, 'component_delay')
    nx.set_edge_attributes(graph, 1, 'wire_delay')
    print(graph.nodes.data())
    print(graph.edges.data())
    nx.nx_agraph.write_dot(graph, '/home/luca/circuit-retiming/graphs/perf-{}.dot'.format(str(n)))


if __name__ == "__main__":
    random_generator(10, 100, 1)
    # i = 0
    # while i < 200:
    #     i = i + random_generator(50, 100, i)
