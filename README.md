# Low-Level-Synthesis Lab 2: FlowMap
## Description
FlowMap is an algorithm used to map components of a boolean network
onto k-input look-up-tables. This repository is an implementation
of the FlowMap algorithm in Python.

## Dependencies
To succesfully run `main.py`, the following packages are required:
```
networkx
pygraphviz
matplotlib
numpy
blifparser
```

## Usage

```
python3 main.py [PATH_TO_BLIF] [k]
```
where *k* is the number of inputs of the look-up-tables.
