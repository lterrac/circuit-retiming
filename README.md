# Synchrounous Circuit Retiming

Final project for Advanced Algorithms exam at Politecnico di Milano

## Table of Contents

- [Repository](#repository)
- [Prerequisites](#prerequisites)
- [Running the tests](#tests)
- [Team](#team)
- [FAQ](#faq)
- [Support](#support)
- [License](#license)

## Introduction

The goal of this project was to implement four algorithms that allows to reduce the clock cycle duration to its minimum without modifying its design. In fact only registers movement are performed.

The algorithms to implement are:
- **FEAS**: Simulates a Bellman Ford algorithm steps. Used by OPT1 
- **CP**: a
- **OPT1**: finds the minimum clock cycle duration. Runs in :
<p align="center"><img src="https://latex.codecogs.com/gif.latex?O(%5Cleft%20%7C%20V%5E%7B3%7D%20%5Cright%20%7C%20log(V))"></p>
- **OPT2**: a

## Repository

Tree:

```
├── docs
├── graphs
├── perf-graphs
├── profile-results-old
├── profile-results-optimized
├── src
└──test
```

Folders content:

- `docs`: contains the paper covering the algorithms to implement and the powerpoint presentation.
- `graphs`: contains 200 random generated graphs and 10 circular graphs with increasing size ready to be randomized and then tested.
- `perf-graphs`: contains the randomized graph used for the performance testing.
- `profile-results-old`: [OUTDATED] contains the profilings of the `beautified` implementation..
- `profile-results-optimized`: the actual profiling files. 
- `src`: the source code of the algorithms and utilities.
- `test`: scripts used for random, correlator, performance testing and profiling.


## Prerequisites
The project has been entirely developed using Python3 and Pycharm

## Running the tests
First of all install all the dependencies listed in `/requirements.txt`then you can either import the test functions that can be found under `/test` or just modify the main section at the end of each file.

Before launching the tests is necessary to change the global variable `root` by substituting the `path_to_the_repo` with the global path where the repository is located. I have no idea why but my virtual environment does not recognize python paths so I have done this workaround.

In `test/test.py` there are the following test categories:
- `Random`: this runs the algorithms on a test suite of 200 graphs random generated graphs.At runtime its edge weights are also changed. See `src.utils.utilities.py` at function  `node_randomizer`.
- `Correlator`: test the circuit described in the paper with also the option to customize the circuit length (it suffices to pass the desired number of nodes to the test function).

## images
![Screenshot from 2020-07-25 02-07-46](https://user-images.githubusercontent.com/25181201/88444669-842b6a80-ce1e-11ea-9f72-8fc0b8893305.png)

In `/test/performance.py` there are:
- `CPU Performance`: run the algorithms on graphs and print the execution time (already embedded inside the `opt.py` class).
- `CPU Profiler`: run the algorithms with cProfiler and print the output in `/profile-results-optimized`. This can be visualized with the `snakeviz` tool.
- `MEM Profiler`: run the algorithms with cProfiler and print the output in `/profile-results-optimized`. This can be visualized with the `snakeviz` tool.

All the performance tests runs the graphs inside `/perf-graphs` (graph already randomized) or the one in `/graphs` which have 'perf' in the name (graph to randomize)

## Performance Results and estimation

This section analyzes how the computational complexity has been assessed

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc
