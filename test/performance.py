import os
import cProfile

import networkx as nx

import src.utils.read_dot as rd
import src.utils.randomizer as randomizer
import src.retimer.retimer as rt


def performance_test():
    """
    Run the performance test with both opt1 and opt2. To do this the algorithms are benched with some path graphs
    with and increasing number of edges. This is done to prove that, despite the differences in implementation, opt2
    has a better complexity than opt1.
    """
    path = '/home/luca/circuit-retiming/graphs/'
    perf_test = [file for file in os.listdir(path) if 'rand-' in file]
    for file in perf_test:
        graph = rd.load_graph(path + '/' + file)
        retimer = rt.Retimer(graph)
        graph = randomizer.node_randomizer(retimer.graph)
        retimer.graph = graph
        #nx.nx_agraph.write_dot(retimer.graph, '/home/luca/circuit-retiming/perf-rand/np-{}'.format(file))
        max_clock = max([weight['component_delay'] for (node, weight) in retimer.graph.nodes.data()])
        pr = cProfile.Profile()
        pr.enable()
        retimer.retime('opt1')
        pr.disable()
        assert max_clock == retimer.opt.min_clock
        # pr.dump_stats('../profile-results/np-{}-opt1.out'.format(file))
        retimer = rt.Retimer(graph)
        # graph = randomizer.node_randomizer(retimer.graph)
        retimer.graph = graph
        pr = cProfile.Profile()
        pr.enable()
        retimer.retime('opt2')
        pr.disable()
        assert max_clock == retimer.opt.min_clock
        #pr.dump_stats('../profile-results/np-{}-opt2.out'.format(file))
        retimer.graph = graph
        #print("opt1: {}".format(str(timeit.timeit(retimer.retime('opt1')))))
        #print("opt2: {}".format(str(timeit.timeit(retimer.retime('opt2')))))


if __name__ == '__main__':
    for i in range(100):
        performance_test()
