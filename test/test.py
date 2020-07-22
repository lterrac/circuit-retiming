import os

import src.utils.read_dot as rd
import src.retimer.retimer as rt
from utils.randomizer import node_randomizer


def random_test():
    """
    Run a random test to test the correctness of the algorithms. In order to do this a random graph is
    generated, some edges are pruned and some weights are moved along the circuit paths.

    The graph generated has at least one register per edge.

    After the edges has been randomly moved the script runs both opt1 and opt2 and checks that the clock
    found by both algorithms is the same as the initial one.
    """
    path = '/home/luca/circuit-retiming/graphs/'
    perf_test = [file for file in os.listdir(path) if 'rand-' in file]
    for file in perf_test:
        graph = rd.load_graph(path + '/' + file)
        print("file")
        print(file)
        retimer = rt.Retimer(graph)
        max_clock = max([weight['component_delay'] for (node, weight) in retimer.graph.nodes.data()])
        print("theoretical clock")
        print(max_clock)
        retimer.graph = node_randomizer(retimer.graph)
        retimer.retime('opt1')
        assert max_clock == retimer.opt.min_clock
        retimer = rt.Retimer(retimer.graph)
        retimer.retime('opt2')
        assert max_clock == retimer.opt.min_clock

    print("All tests passed")


if __name__ == '__main__':
    random_test()
    # for i in range(5000):
    #     random_test()
