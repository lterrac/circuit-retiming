import os
import src.utils.utilities as utils
import src.retimer.retimer as rt
import src.utils.generator as gn


def random_test(test_path: str):
    """
    Run a random test to test the correctness of the algorithms. In order to do this a random graph is
    generated, some edges are pruned and some weights are moved along the circuit paths.

    The graph generated has at least one register per edge.

    After the edges has been randomly moved the script runs both opt1 and opt2 and checks that the clock
    found by both algorithms is the same as the initial one.
    """
    path = os.getcwd() + '/' + test_path
    perf_test = [file for file in os.listdir(path)]
    for file in sorted(perf_test):
        graph = utils.load_graph(path + '/' + file)
        retimer = rt.Retimer(graph)
        print("file")
        print(file)
        max_clock = max([weight['component_delay'] for (node, weight) in retimer.graph.nodes.data()])
        print("theoretical clock")
        print(max_clock)
        retimer.graph = utils.node_randomizer(retimer.graph)
        retimer.retime('opt1')
        assert max_clock == retimer.opt.min_clock
        retimer = rt.Retimer(retimer.graph)
        retimer.retime('opt2')
        assert max_clock == retimer.opt.min_clock

    print("All tests passed")


def correlator_test(correlator_dimension=None):
    """
    Run OPT1 and OPT2 on the correlator circuit presented in the paper. If no parameter
    is passed the exact one is chosen, otherwise a correlator with the desired dimension
    will be created.
    """
    path = os.getcwd() + '/corr-graphs'
    perf_test = [file for file in os.listdir(path)]
    if correlator_dimension is None:
        path = path + 'correlator.dot'
        graph = utils.load_graph(path)
    else:
        graph = gn.generate_from_correlator(correlator_dimension)

    if correlator_dimension < 8:
        max_clock = 13
    else:
        max_clock = 14

    retimer = rt.Retimer(graph)
    print("theoretical clock")
    print(max_clock)
    retimer.retime('opt1')
    assert max_clock == retimer.opt.min_clock
    retimer = rt.Retimer(retimer.graph)
    retimer.retime('opt2')
    assert max_clock == retimer.opt.min_clock

    print("All tests passed")


if __name__ == '__main__':
    random_test('rand-graphs/clean/50')