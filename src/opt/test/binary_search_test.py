import networkx as nx
from pytest_mock import mocker

from src.opt.opt1 import OPT1
import sys, os

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

def binary_search_all_positive(stub):

    mocker.patch('src.opt.opt1.OPT1._check_clock_feasibility', return_value=(True, []))

    opt1 = OPT1(nx.DiGraph(), dict(), dict())

    opt1._d_range = [1] * 10
    opt1.search_min_clock()
