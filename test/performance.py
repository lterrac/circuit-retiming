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
    path = '/home/luca/circuit-retiming/perf-graphs'
    perf_test = [file for file in os.listdir(path) if 'perf-' in file]
    for file in perf_test:
        graph = rd.load_graph(path + '/' + file)
        retimer = rt.Retimer(graph)
        retimer.graph = randomizer.node_randomizer(retimer.graph)
        nx.nx_agraph.write_dot(retimer.graph, '/home/luca/circuit-retiming/perf-rand/rand-{}'.format(file))
        retimer = rt.Retimer(graph)
        pr = cProfile.Profile()
        pr.enable()
        retimer.retime('opt1')
        pr.disable()
        pr.dump_stats('../profile-results/mem-{}-opt1.out'.format(file))
        pr = cProfile.Profile()
        pr.enable()
        retimer.retime('opt2')
        pr.disable()
        pr.dump_stats('../profile-results/mem-{}-opt2.out'.format(file))


if __name__ == '__main__':
    performance_test()
