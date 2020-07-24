import os
import cProfile
import time
import networkx as nx
import src.utils.utilities as utils
import src.retimer.retimer as rt

root = '/path_to_the_repo/circuit-retiming/'

def bench_memory():
    """
    Bench both opt1 and opt2 memory consumption using the graph generated for the performance tests. The execution times
    are printed in the terminal. In order to process bigger graphs and save time, matrices W and D are
    directly passed to the retimer that executes opt2, avoiding to be computed twice per graph.
    """
    pass


def bench_cpu(randomize=False):
    """
    Bench both opt1 and opt2 execution time using the graph generated for the performance tests. The execution times
    are printed in the terminal. In order to process bigger graphs and save time, matrices W and D are
    directly passed to the retimer that executes opt2, avoiding to be computed twice per graph.
    """
    path = root + 'perf-graphs/'
    perf_test = [file for file in os.listdir(path) if 'perf' in file]
    for file in sorted(perf_test):
        graph = utils.load_graph(path + '/' + file)
        graph = utils.preprocess_graph(graph)

        if randomize is True:
            graph = utils.node_randomizer(graph)
            nx.nx_agraph.write_dot(graph, root + 'perf-graphs/np-{}'.format(file))

        max_clock = max([weight['component_delay'] for (node, weight) in graph.nodes.data()])
        retimer = rt.Retimer(graph.copy())
        init = time.time()
        retimer.retime('opt1')
        end = time.time()
        print("opt1 {}".format(end - init))
        assert max_clock == retimer.opt.min_clock
        nretimer = rt.Retimer(graph.copy())
        nretimer.opt.w = retimer.wd.w
        nretimer.opt.d = retimer.wd.d
        del retimer
        nretimer.opt.opt('opt2')
        assert max_clock == nretimer.opt.min_clock
        del nretimer


def profile(randomize=False):
    """
    Profile both opt1 and opt2 using the graph generated for the performance tests.
    cProfiler output files can be visualized with snakeviz
    """
    path = root + 'perf-graphs/'
    perf_test = [file for file in os.listdir(path) if 'np-perf' in file]
    for file in sorted(perf_test):
        graph = utils.load_graph(path + '/' + file)
        graph = utils.preprocess_graph(graph)

        if randomize is True:
            graph = utils.node_randomizer(graph)
            nx.nx_agraph.write_dot(graph, root + 'perf-graphs/np-{}'.format(file))

        max_clock = max([weight['component_delay'] for (node, weight) in graph.nodes.data()])
        retimer = rt.Retimer(graph.copy())
        pr = cProfile.Profile()
        pr.enable()
        retimer.retime('opt1')
        pr.disable()
        assert max_clock == retimer.opt.min_clock
        pr.dump_stats(root + 'profile-results-optimized/{}-opt1.out'.format(file))
        del retimer

        nretimer = rt.Retimer(graph.copy())
        pr = cProfile.Profile()
        pr.enable()
        nretimer.retime('opt2')
        assert max_clock == nretimer.opt.min_clock
        pr.disable()
        pr.dump_stats(root + 'profile-results-optimized/{}-opt2.out'.format(file))
        del nretimer


if __name__ == '__main__':
    profile()
