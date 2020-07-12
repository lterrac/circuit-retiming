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
    :param nodes: the desidered number of nodes in the circuit
    :return:
    """
    correlator = nx.DiGraph()
    correlator.add_nodes_from(['0', '1', '2'])
    nx.set_node_attributes(correlator, str(3), 'component_delay')
    correlator.add_edges_from([('0', '1'), ('2', '0')])
    nx.set_edge_attributes(correlator, str(0), 'wire_delay')
    correlator.add_edge('1', '2')
    up = 2
    down = 1

    for i in range(up + 1, nodes, 2):
        correlator.add_nodes_from([(str(i), {'component_delay': str(3)}), (str(i + 1), {'component_delay': str(7)})])
        correlator.add_edges_from([(str(i), str(up), {'wire_delay': str(0)}),
                                   (str(down), str(i), {'wire_delay': str(1)}),
                                   (str(down), up, {'wire_delay': str(0)})
                                   ])
        up = i
        down = i + 1

    correlator.add_edges_from([(str(down), str(up), {'wire_delay': str(0)})])
    print(correlator.nodes.data())
    print(correlator.edges.data())
    nx.draw(correlator, pos=nx.circular_layout(correlator), with_labels=True, font_weight='bold')
    plt.show()


    return correlator


def random_generator(n: int, k: int):
    graph = nx.random_k_out_graph(n, k, self_loops=False, alpha=4000)
    nx.draw(graph, pos=nx.circular_layout(graph), with_labels=True, font_weight='bold')
    plt.show()

    # Delete incoming arcs from 0 -> starting node
    print(graph.edges)
    graph.remove_edges_from([(v1, v2, weight) for (v1, v2, weight) in graph.in_edges if v2 is 0])

    graph.add_edges_from([(0, max(graph.nodes), {'wire_delay': 1})])

    for node in graph.nodes:
        incoming = [(v1, v2) for (v1, v2, weight) in graph.in_edges if v2 is node]
        print(incoming)
        print(len(incoming))
        deleted_nodes = 0
        for edge in incoming:
            keep = np.average(rnd.binomial(1, 0.1, 1000))
            print(keep / 5.0)
            print("incoming")
            print(len(incoming))
            print("outgoing")
            print(graph.edges(edge[0]))
            if keep < 0.5 and deleted_nodes < len(incoming) - 1 and len(graph.edges(edge[0])) > 1:
                graph.remove_edges_from([edge])
                deleted_nodes = deleted_nodes + 1

    nx.set_node_attributes(graph, 3, 'component_delay')
    nx.set_edge_attributes(graph, 1, 'wire_delay')
    nx.nx_agraph.write_dot(graph, '/home/luca/circuit-retiming/graphs/rand-3.dot')
    nx.draw(graph, pos=nx.circular_layout(graph), with_labels=True, font_weight='bold')
    plt.show()


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
    generate_from_correlator(10)
