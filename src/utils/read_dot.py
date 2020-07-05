import networkx as nx
import matplotlib.pyplot as plt


def load_graph(path: str):
    return nx.nx_agraph.read_dot(path)


if __name__ == "__main__":
    graph_path = 'graphs/correlator1.dot'
    #G = load_graph(path=graph_path)
    G = nx.DiGraph()
    nx.set_edge_attributes(G, [('h', '1', 1),
                               ('1', '2', 1),
                               ('2', '3', 1),
                               ('3', '4', 1),
                               ('1', '7', 0),
                               ('2', '6', 0),
                               ('3', '5', 0),
                               ('4', '5', 0),
                               ('5', '6', 0),
                               ('6', '7', 0),
                               ('7', 'h', 0),
                               ], name='wire_delay')
    nx.set_node_attributes(G, values={'h': 0,
                               '1':3,
                               '2':3,
                               '3':3,
                               '4':3,
                               '5':7,
                               '6':7,
                               '7':7}, name="component_delay")
    G.name = "correlator"
    nx.nx_agraph.write_dot(G, graph_path)
    plt.subplot(121)

    nx.draw(G, with_labels=True, font_weight='bold')
    plt.subplot(122)

    plt.subplot(121)

    nx.draw(G, with_labels=True, font_weight='bold')
    nx.draw_networkx_edge_labels(G, pos=nx.fruchterman_reingold_layout(G))
    plt.show()
    nx.draw(G)
    # nx.draw_shell(G, nlist=[range(5, 10), range(5)], with_labels=True, font_weight='bold')
    plt.show()
