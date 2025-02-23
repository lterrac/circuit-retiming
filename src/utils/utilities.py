import networkx as nx
import numpy as np
import numpy.random as rnd


def load_graph(path: str) -> nx.DiGraph:
    return nx.nx_agraph.read_dot(path)


def node_randomizer(graph: nx.DiGraph) -> nx.DiGraph:
    """
    Randomize a graph moving forward or backward the registers among the arcs. This is done in a
    way that preserves the circuit behaviour. Given a node registers are removed from all the incoming/outgoing
    edges and being added to all outgoing/incoming ones. In this way the circuit behaviour remanins
    unchanged and so its minimal clock.
    also removed from the
    :param graph:
    :return:
    """
    for node in graph.nodes:
        keep = np.average(rnd.binomial(1, 0.5, 1000))
        if keep < 0.5:
            pick_from_back(graph, node)
        else:
            pick_from_front(graph, node)
    return graph


def pick_from_back(graph: nx.DiGraph, node: str):
    """
    Move from node's incoming arc to outgoing arc the common minimum edge number.
    Do nothing if there is an arc with zero registers
    """
    arcs = [weight['wire_delay'] for (v1, v2, weight) in graph.edges.data() if v2 == node]
    if arcs:
        min_registers = min(arcs)
        if min_registers and min_registers > 0:
            nx.set_edge_attributes(graph,
                                   {(v1, v2): {'wire_delay': weight['wire_delay'] - min_registers} for (v1, v2, weight) in
                                    graph.edges.data() if v2 == node})
            nx.set_edge_attributes(graph,
                                   {(v1, v2): {'wire_delay': weight['wire_delay'] + min_registers} for (v1, v2, weight) in
                                    graph.edges.data() if v1 == node})


def pick_from_front(graph: nx.DiGraph, node: str):
    """
    Move from node's outgoing arcs to incoming arc the common minimum edge number
    Do nothing if there is an arc with zero registers
    """
    arcs =[weight['wire_delay'] for (v1, v2, weight) in graph.edges.data() if v1 == node]
    if arcs:
        min_registers = min(arcs)
        if min_registers and min_registers > 0:
            nx.set_edge_attributes(graph,
                                   {(v1, v2): {'wire_delay': weight['wire_delay'] - min_registers} for (v1, v2, weight) in
                                    graph.edges.data() if v1 == node})
            nx.set_edge_attributes(graph,
                                   {(v1, v2): {'wire_delay': weight['wire_delay'] + min_registers} for (v1, v2, weight) in
                                    graph.edges.data() if v2 == node})
