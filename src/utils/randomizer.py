import numpy as np
import networkx as nx
import numpy.random as rnd


def node_randomizer(graph: nx.DiGraph) -> nx.DiGraph:
    for node in graph.nodes:
        keep = np.average(rnd.binomial(1, 0.5, 1000))
        if keep < 0.5:
            pick_from_back(graph, node)
        else:
            pick_from_front(graph, node)
    print("ge")
    print(graph.edges.data())
    return graph


def pick_from_back(graph: nx.DiGraph, node: str):
    min_registers = min([weight['wire_delay'] for (v1, v2, weight) in graph.edges.data() if v2 == node])
    if min_registers > 0:
        nx.set_edge_attributes(graph,
                               {(v1, v2): {'wire_delay': weight['wire_delay'] - min_registers} for (v1, v2, weight) in
                                graph.edges.data() if v2 == node})
        nx.set_edge_attributes(graph,
                               {(v1, v2): {'wire_delay': weight['wire_delay'] + min_registers} for (v1, v2, weight) in
                                graph.edges.data() if v1 == node})


def pick_from_front(graph: nx.DiGraph, node: str):
    min_registers = min([weight['wire_delay'] for (v1, v2, weight) in graph.edges.data() if v1 == node])
    if min_registers > 0:
        nx.set_edge_attributes(graph,
                               {(v1, v2): {'wire_delay': weight['wire_delay'] - min_registers} for (v1, v2, weight) in
                                graph.edges.data() if v1 == node})
        nx.set_edge_attributes(graph,
                               {(v1, v2): {'wire_delay': weight['wire_delay'] + min_registers} for (v1, v2, weight) in
                                graph.edges.data() if v2 == node})
