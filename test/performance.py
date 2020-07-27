import cProfile
import os
import time
import networkx as nx
from memory_profiler import profile
import src.retimer.retimer as rt
import src.utils.utilities as utils


@profile
def profile_memory(retimer, param):
    retimer.retime(param)


def bench_memory():
    """
    Bench both opt1 and opt2 memory consumption using the graph generated for the performance tests. The execution times
    are printed in the terminal. In order to process bigger rand-graphs and save time, matrices W and D are
    directly passed to the retimer that executes opt2, avoiding to be computed twice per graph.
    """
    path = os.getcwd() + '/perf-graphs/randomized'
    perf_test = [file for file in os.listdir(path)]
    for file in sorted(perf_test):
        print(file)
        graph = utils.load_graph(path + '/' + file)
        graph = utils.preprocess_graph(graph)
        max_clock = max([weight['component_delay'] for (node, weight) in graph.nodes.data()])
        retimer = rt.Retimer(graph.copy())
        profile_memory(retimer, 'opt1')
        assert max_clock == retimer.opt.min_clock
        nretimer = rt.Retimer(graph.copy())
        del retimer
        profile_memory(nretimer, 'opt2')
        assert max_clock == nretimer.opt.min_clock
        del nretimer


def bench_cpu(test_path: str, randomize=False):
    """
    Bench both opt1 and opt2 execution time using the graph generated for the performance tests. The execution times
    are printed in the terminal. In order to process bigger rand-graphs and save time, matrices W and D are
    directly passed to the retimer that executes opt2, avoiding to be computed twice per graph.
    """
    path = os.getcwd() + '/../' + test_path
    perf_test = [file for file in os.listdir(path)]
    for file in sorted(perf_test):
        print(file)
        graph = utils.load_graph(path + '/' + file)
        graph = utils.preprocess_graph(graph)

        if randomize is True:
            graph = utils.node_randomizer(graph)
            nx.nx_agraph.write_dot(graph, path + '/np-{}'.format(file))

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


def profile(test_path: str, randomize=False):
    """
    Profile both opt1 and opt2 using the graph generated for the performance tests.
    cProfiler output files can be visualized with snakeviz
    """

    path = os.getcwd() + '/../' + test_path
    perf_test = [file for file in os.listdir(path)]
    for file in sorted(perf_test):
        print(file)
        graph = utils.load_graph(path + '/' + file)
        graph = utils.preprocess_graph(graph)

        if randomize is True:
            graph = utils.node_randomizer(graph)
            nx.nx_agraph.write_dot(graph, path + 'np-{}'.format(file))

        max_clock = max([weight['component_delay'] for (node, weight) in graph.nodes.data()])
        retimer = rt.Retimer(graph.copy())
        pr = cProfile.Profile()
        pr.enable()
        retimer.retime('opt1')
        pr.disable()
        assert max_clock == retimer.opt.min_clock
        pr.dump_stats(os.getcwd() + '/../profile-results-optimized/{}-opt1.out'.format(file))
        del retimer

        nretimer = rt.Retimer(graph.copy())
        pr = cProfile.Profile()
        pr.enable()
        nretimer.retime('opt2')
        assert max_clock == nretimer.opt.min_clock
        pr.disable()
        pr.dump_stats(os.getcwd() + '/../profile-results-optimized/{}-opt2.out'.format(file))
        del nretimer


if __name__ == '__main__':
    bench_cpu('perf-graphs/randomized', False)
