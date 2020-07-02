import networkx as nx
import matplotlib.pyplot as plt


def load_graph(path: str):
    return nx.nx_agraph.read_dot(path)


if __name__ == "__main__":
    graph_path = 'graphs/correlator.dot'
    G = load_graph(path=graph_path)
    # G = nx.DiGraph()
    # G.add_weighted_edges_from([('vh', 'v1', 1),
    #                            ('v1', 'v2', 1),
    #                            ('v2', 'v3', 1),
    #                            ('v3', 'v4', 1),
    #                            ('v1', 'v7', 0),
    #                            ('v2', 'v6', 0),
    #                            ('v3', 'v5', 0),
    #                            ('v4', 'v5', 0),
    #                            ('v5', 'v6', 0),
    #                            ('v6', 'v7', 0),
    #                            ('v7', 'vh', 0),
    #                            ])
    # nx.set_node_attributes(G, values={'vh': 0,
    #                            'v1':3,
    #                            'v2':3,
    #                            'v3':3,
    #                            'v4':3,
    #                            'v5':7,
    #                            'v6':7,
    #                            'v7':7}, name="delay")
    # G.name = "correlator"
    # nx.nx_agraph.write_dot(G, path)
    plt.subplot(121)

    nx.draw(G, with_labels=True, font_weight='bold')
    plt.subplot(122)

    nx.draw(G)
    # nx.draw_shell(G, nlist=[range(5, 10), range(5)], with_labels=True, font_weight='bold')
    plt.show()
