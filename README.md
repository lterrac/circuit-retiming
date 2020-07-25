# Synchrounous Circuit Retiming

Final project for Advanced Algorithms exam at Politecnico di Milano

## Table of Contents

- [Synchrounous Circuit Retiming](#synchrounous-circuit-retiming)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Repository](#repository)
  - [Tools](#tools)
  - [Testing](#testing)
  - [Test Generation](#test-generation)
  - [Graphs](#graphs)
    - [Graph schemes](#graph-schemes)
      - [Correlator Graph Schema](#correlator-graph-schema)
      - [Path Graph Schema](#path-graph-schema)
      - [Custom Random K Out Graph](#custom-random-k-out-graph)
  - [CPU Profiling and Estimation](#cpu-profiling-and-estimation)
    - [Legend](#legend)
    - [Estimation vs. Real execution time](#estimation-vs-real-execution-time)
  - [Memory Profiling](#memory-profiling)
  - [Authors](#authors)

## Introduction

The goal of this project was to implement four algorithms that allows to reduce the clock cycle duration to its minimum duration without modifying the design and the behaviour of the circuit. In fact only registers movement are performed in order to achieve this result. In the reference paper during the project introduction the following algorithm are presented:

- **OPT1**: the first algorithm presented in order to find a legal retiming which minimizes the circuit clock cycle. To solve the problem a binary search is used to try different clock cycles while an all pairs shortest path (Bellman Ford) is used to check wheter a legal retiming for the given clock cycle exists. An important consideration that will become relevant during the performance analysis is that the algorithm used is a Networkx library function implemented in C++ which gives a significant performance boost to this algorithm. In the end the computational complexity of this algorithm is:  
![equation](http://www.sciweavers.org/tex2img.php?eq=O%28%20%5C%7C%20V%20%5C%7C%20%5E%7B3%7D%20log%28%20%5C%7C%20V%20%5C%7C%20%29%29&bc=White&fc=Black&im=jpg&fs=12&ff=arev&edit=0)
- **OPT2**: the second algorithm which has a better computational complexity since it takes into account the circuit edges rather than only nodes. Like OPT1 it uses a binary search to search for the minimum clock but FEAS algorith is used to check if the retiming produced for the selected clock cycle is feasible. Unlike OPT1 this algorithm is implemented using a lot more of Python code which introduces an overhead which makes it perform worse in the performance tests. However, in the [conclusions](#conclusions) and [performance analysis](#performance) sections it is proved that the implementation complexity is compliant with the theoretical one, The algorithm complexity is:  
![equation](http://www.sciweavers.org/tex2img.php?eq=O%28%20%5C%7C%20V%20%5C%7C%20%5C%7C%20E%20%5C%7C%20log%28%20%5C%7C%20V%20%5C%7C%20%29%29&bc=White&fc=Black&im=jpg&fs=12&ff=arev&edit=0)

- **FEAS**: It is used by OPT2 to check whether a retiming is feasible or not. It simulates a Bellman Ford algorithm iteration step. The algorithm complexity is:  
![equation](http://www.sciweavers.org/tex2img.php?eq=O%28%20%5C%7C%20V%20%5C%7C%20%5C%7C%20E%20%5C%7C%29&bc=White&fc=Black&im=jpg&fs=12&ff=arev&edit=0)
- **CP**: Used to compute to minimum clock cycle of a circuit. The complexity is:  
![equation](http://www.sciweavers.org/tex2img.php?eq=O%28%20%5C%7C%20E%20%5C%7C%29&bc=White&fc=Black&im=jpg&fs=12&ff=arev&edit=0)


## Repository

Tree:

```
├── corr-graphs
├── docs
│   ├── Retiming.pdf
│   └── SummerSessionProjectAA.pdf
├── perf-graphs
│   ├── clean
│   └── randomized
├── profile-results-old
├── profile-results-optimized
├── rand-graphs
│   ├── clean
│   └── randomized
├── requirements.txt
├── src
│   ├── opt
│   ├── retimer
│   ├── utils
│   └── wd
└── test
    ├── performance.py
    └── test.py
```

Folders content:

- `corr-graphs`: contains the circuit representing a correlator at N bits.
- `docs`: contains the paper covering the algorithms to implement and the powerpoint presentation.
- `rand-graphs`: contains the random generated graph. There are two graph versions: the already randomized one (with the registers already moved) and the clean one.
- `perf-graphs`: contains the path graph used for the performance testing.
- `profile-results-old`: [OUTDATED] contains the profilings of the `beautified` implementation.
- `profile-results-optimized`: the actual profiling files. 
- `src`: the source code of the algorithms and utilities.
- `test`: scripts used for random, correlator, performance testing and profiling.


## Tools

- Language: Python3
- Libraries:
  - NetworkX
  - Numpy
  - Graphviz
- Profiling:
  - cProfiler
  - memory-profiler
- Graph File extension:
  - `.dot` files

## Testing
First of all install all the dependencies listed in `/requirements.txt`then you can either import the test functions that can be found under `/test` or just modify the main section at the end of each file.

Before launching the tests is necessary to change the global variable `root` by substituting the `path_to_the_repo` with the global path where the repository is located. I have no idea why but my virtual environment does not recognize python paths so I have done this workaround.

In `test/test.py` there are the following test categories:
- `Random`: this runs the algorithms on a test suite of 200 graphs random generated graphs.At runtime its edge weights are also changed. See `src.utils.utilities.py` at function  `node_randomizer`.
- `Correlator`: test the circuit described in the paper with also the option to customize the circuit length (it suffices to pass the desired number of nodes to the test function).

In `/test/performance.py` there are:
- `CPU Performance`: run the algorithms on graphs and print the execution time (already embedded inside the `opt.py` class).
- `CPU Profiler`: run the algorithms with cProfiler and print the output in `/profile-results-optimized`. This can be visualized with the `snakeviz` tool.
- `MEM Profiler`: run the algorithms with memory-profiler and print the output in `/profile-results-optimized`. This can be visualized with the `snakeviz` tool.

All the performance tests runs the graphs inside `/perf-graphs` which containe both the ones already randomized and the ones to randomize.

## Test Generation
One of the project requirement was to generate randomly some test cases in order to assess the correctness of the implemented solution. In order to do this the following approch has been adopted:

1) The graph is generated with exactly one register on each arc.
2) Then, iterating through all the nodes, an amount of registers is selected from incoming/outcoming arcs (this is choosen randomly) and passed to backward/forward paths. In addition, the randomization process is designed to avoid creating arcs with a negative number of registers and doing the register movement on all incoming/outgoing arcs ensures that the circuit behaviour does not change and so the minimum clock cycle is preserved.
3) Since the graph behaviour does not change the maximum clock is the maximum of the node delays and, by applying the retiming algorithms to the randomized graphs, the original graph or at least one with the same minimum clock cycle is obtained.

The randomizer mechanism is show in figure:  
![Randomizer](https://user-images.githubusercontent.com/25181201/88468279-712d9e80-cee1-11ea-9142-dd83a4d407e3.png)

The maximum number of register that can be moved is the minimum between all the arc edges with the same direction (incoming or outgoing) and then added to all the other edges in the opposite direction.

## Graphs
The graphs used in this project to test the implementation correctness belongs to three types:

- `Correlator`: graph shown in the paper. It is possible to generate this graph schema with an arbitrary amount of nodes.
- `Path`: graphs used to conduct the performance tests. The circuit creates a directed ring and has the same number of nodes and edges.
- `Custom random K out graph`: used to assess the code correctness. Starting from a `random_k_out_graph` (documentation available in the Networkx documentation), some edges are deleted to make the graph a little bit more sparse while keeping attention to maintain the graph always connected.

Except for the `Correlator`, all the other graphs starts with one register per edge and then are randomized. For more information refer to [test generation section](#test-generation).

### Graph schemes
The following images give an overview of what the graphs descripted above look like.

#### Correlator Graph Schema
<img src="https://user-images.githubusercontent.com/25181201/88468344-40019e00-cee2-11ea-88c1-033d5eb540cb.png" width="200"/>  

#### Path Graph Schema
<img src="https://user-images.githubusercontent.com/25181201/88468343-3d9f4400-cee2-11ea-9d05-73441baf6ed7.png" width="200" height="400"/>  

#### Custom Random K Out Graph
<img src="https://user-images.githubusercontent.com/25181201/88444669-842b6a80-ce1e-11ea-9f72-8fc0b8893305.png" width="600"/>

## CPU Profiling and Estimation

This section analyzes how the computational complexity has been assessed.

The performance of the two algorithms significantly differs in their execution time. In fact, OPT1 calls the `all pairs shortest path` function which uses the C++ library `Boost Graph Library`. This gives to OPT1 a significant speed increase with respect to OPT2 despite the latter heavily uses Numpy data structures. Even so, the profile results confirm the fact that the implementation of both algorithms is coherent with respect to the given computational complexity and that OPT2 is penalised only by the amount of Python code used to implement it.

In order to estimate the run duration the algorithm complexities, a time reference, an input size difference and eventually a constant factor are used.
For example, the estimation of the run with 1000 nodes is computed as follows:
- time reference T: execution time of the graph with 200 nodes
- complexity : OPT2 complexity
- input size difference D: 5
- constant C: initially suppose that is 1

The estimation is computed as:  
![equation](http://www.sciweavers.org/tex2img.php?eq=C%20%2A%20T%20%2A%20%28%20%5C%7C%20D%20%5C%7C%20%5E%7B2%7D%20log%28%5C%7CD%5C%7C%29&bc=White&fc=Black&im=jpg&fs=12&ff=arev&edit=0)

```
Note that since the number of nodes and edges are the same in path graphs the complexity of OPT2 can be reduced with the one above.
```

The time reference is taken on the graph execution with 200 nodes and 200 edges in order to delete some profiling noise generated by short runs.
The following tables shows the results obtained by executing the algorithms on path graphs of increasing size:
|N   |Input difference|Complexity factor OPT1|Estimation OPT1|Estimation with Ratios|Real OPT1  |Ratios      |Complexity factor OPT2|Estimation OPT2|Estimation with Ratios|Real OPT2  |Ratios      |
|----|----------------|----------------------|---------------|----------------------|-----------|------------|----------------------|---------------|----------------------|-----------|------------|
|100 |0.5             |0.125                 |0.2282397747   |0.06298992422         |0.36749506 |1.610127159 |0.25                  |2.138666809    |2.424141512           |1.717460394|0.8030518765|
|200 |1               |1                     |1.825918198    |0.5039193938          |1.825918198|1           |1                     |8.554667234    |9.696566047           |8.554667234|1           |
|300 |1.5             |1.97424844            |3.604816153    |0.994862077           |4.931491852|1.368028671 |1.316165627           |11.25935896    |12.76228693           |21.93270683|1.947953423 |
|400 |2               |8                     |14.60734558    |4.03135515            |8.560532808|0.5860430125|4                     |34.21866894    |38.78626419           |43.11432934|1.259965121 |
|500 |2.5             |20.65512648           |37.71457132    |10.40851882           |13.25896287|0.3515607471|8.262050593           |70.6790935     |80.11351926           |77.66988254|1.098908867 |
|600 |3               |42.79398752           |78.13832056    |21.56472025           |24.2570281 |0.3104370292|14.26466251           |122.029441     |138.3182421           |130.0198784|1.065479587 |
|700 |3.5             |77.49034228           |141.4910261    |39.04888631           |31.79156351|0.2246896102|22.1400978            |189.4011692    |214.6829206           |178.5944922|0.9429429236|
|800 |4               |128                   |233.7175293    |64.5016824            |41.10195923|0.175861688 |32                    |273.7493515    |310.2901135           |272.9435275|0.9970563436|
|900 |4.5             |197.7344158           |361.046868     |99.64220692           |53.44911456|0.1480392694|43.94098128           |375.9004728    |426.0766272           |368.1362629|0.9793450382|
|1000|5               |290.2410119           |529.9563453    |146.2580747           |71.67033577|0.1352381878|58.04820237           |496.5830549    |562.8682282           |451.7374651|0.9096916633|

### Legend
- `N`: number of nodes and edges in the graph
- `Input difference`: difference in input size between different runs
- `Complexity factor`: the complexity factor that is multiplied with the execution time of the circuit taken as reference (N = 200 in this case) to obtain the `Estimation` column
- `Estimation`: estimated duration of the run
- `Estimation with ratios`: estimated duration that takes into account also constant factor derived by the average of `Ratios`
- `Real`: effective execution time of the run
- `Ratios`: how much `Real` differs from `Estimation`

### Estimation vs. Real execution time
Using the first runs of the algorithms to estimate the costants C, the following one have been derived:
- OPT1: 0.6401265117
- OPT2: 1.195893146

Results:  
![Estimation vs  Real OPT1](https://user-images.githubusercontent.com/25181201/88468812-56f7be80-cee9-11ea-8b14-42d0b19479ab.png)
![Estimation vs  Real OPT2](https://user-images.githubusercontent.com/25181201/88468821-5b23dc00-cee9-11ea-918a-5e508f4e2745.png)

The last run with 1000 nodes has been estimated with this more accurate constants:
- OPT1: 0.2759813635
- OPT2: 1.133482552

Results:  
![Estimation vs  Real OPT1 (1)](https://user-images.githubusercontent.com/25181201/88468861-97573c80-cee9-11ea-9216-28fa611e1206.png)
![Estimation vs  Real OPT2 (1)](https://user-images.githubusercontent.com/25181201/88468862-98886980-cee9-11ea-9e8d-2e2fb087121d.png)
```
In the plots the X axis represents the input size while the Y axis represents the execution time
```
From these table and plots it is clear that OPT1 always performs better than OPT2 but, observing the `Ratios` columns of OPT2, we can see that the estimation on the execution time is more accurate for OPT2 in longer runs and so it is coherent with the theoretical complexity. In fact, from runs with N greater than 500 nodes the constant factor is really close to 1. This allows to assess that, despite the longer runs of OPT2, the algorithm has the desired complexity and when N will reach a certain value, OPT2 will perform better than OPT1 despite it executes C++ code.

## Memory Profiling
***TBA***
## Authors

* **Luca Terracciano**
