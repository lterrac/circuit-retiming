from src.utils import utilities
import src.retimer.retimer as rt
import argparse


def draw(path: str, nodelabels: bool):
    """
    :param nodelabels: if set draw the component_delay label instead of the node name
    :param path:
    :return:
    """
    graph = utilities.load_graph(path)
    rt.draw_graph(graph, nodelabels)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, required=True, help='input graph file path')
    parser.add_argument('--nodelabels', action='store_true', help='show component_delay')
    args = parser.parse_args()
    draw(args.path, args.nodelabels)
