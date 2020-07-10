import src.utils.read_dot as rd


def generate_from_correlator(nodes: int):
    correlator = rd.load_graph("graphs/correlator-1.dot")
    up = 6
    down = 7
    correlator.remove_edge('7', '6')

    for i in range(down + 1, nodes, 2):
        correlator.add_nodes_from([(str(i), {'component_delay': str(3)}), (str(i + 1), {'component_delay': str(7)})])
        correlator.add_edges_from([(str(i), str(up), {'wire_delay': str(0)}),
                                   (str(down), str(i), {'wire_delay': str(0)}),
                                   (str(down), str(i+1), {'wire_delay': str(1)})
                                   ])
        up = i
        down = i + 1

    correlator.add_edges_from([(str(down), str(up), {'wire_delay': str(0)})])

    return correlator
