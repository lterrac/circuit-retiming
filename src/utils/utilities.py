import networkx as nx
import numpy as np
import numpy.random as rnd


def load_graph(path: str) -> nx.DiGraph:
    return nx.nx_agraph.read_dot(path)


def preprocess_graph(graph: nx.DiGraph) -> nx.DiGraph:
    """
    Convert delays from strings to int
    :param graph:
    :return:
    """
    component_delay = nx.get_node_attributes(G=graph, name='component_delay')
    node_attributes = {node: int(d) for (node, d) in component_delay.items()}
    nx.set_node_attributes(G=graph, values=node_attributes, name='component_delay')

    wire_delay = nx.get_edge_attributes(G=graph, name='wire_delay')
    weights = {(v1, v2): int(wire_delay) for ((v1, v2), wire_delay) in wire_delay.items()}
    nx.set_edge_attributes(G=graph, values=weights, name='wire_delay')
    return graph


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
    min_registers = min([weight['wire_delay'] for (v1, v2, weight) in graph.edges.data() if v2 == node])
    if min_registers > 0:
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
    min_registers = min([weight['wire_delay'] for (v1, v2, weight) in graph.edges.data() if v1 == node])
    if min_registers > 0:
        nx.set_edge_attributes(graph,
                               {(v1, v2): {'wire_delay': weight['wire_delay'] - min_registers} for (v1, v2, weight) in
                                graph.edges.data() if v1 == node})
        nx.set_edge_attributes(graph,
                               {(v1, v2): {'wire_delay': weight['wire_delay'] + min_registers} for (v1, v2, weight) in
                                graph.edges.data() if v2 == node})
