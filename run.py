import networkx as nx

from src.utils import utilities
from src.retimer import retimer as rt
import argparse


def run(path: str, printwd: bool, optimizer: str, output: str):
    graph = utilities.load_graph(path)
    retimer = rt.Retimer(graph, printwd)
    retimer.retime(optimizer)
    rt.save_graph(retimer.retimed_graph, output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, required=True, help='input graph file path')
    parser.add_argument('--printwd', action='store_true', help='print W and D matrices')
    parser.add_argument('--optimizer', type=str, required=True, help='specify algorithm to use: "opt1" or "opt2"')
    parser.add_argument('--outputfile', type=str, required=True, help='output graph file path')
    args = parser.parse_args()
    run(args.path, args.printwd, args.optimizer, args.outputfile)
