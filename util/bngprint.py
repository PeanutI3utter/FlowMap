import os
from networkx.drawing.nx_pydot import write_dot
from graphviz import render


def print_bng(bng):

    write_dot(bng, 'graph.dot')

    dot = open("graph.dot", "r")
    dotout = open("graph_out.dot", "w")
    dotlines = dot.readlines()
    dotlines = dotlines[:-1]
    for line in dotlines:
        dotout.write(line)
    dotout.write("{rank=min; ")
    inputs = [node for node, deg in bng.in_degree() if not deg]
    for input in inputs:
        dotout.write(" " + str(input) + ";")
    dotout.write("}" + "\n")
    dotout.write("}")

    dot.close()
    os.remove("graph.dot")
    dotout.close()

    render("dot", "png", "graph_out.dot")
