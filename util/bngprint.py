import os
from networkx.drawing.nx_pydot import write_dot

def print_bng(bng, numinputs):

    write_dot(bng, 'graph.dot')

    dot = open("graph.dot", "r")
    dotout = open("graph_out.dot", "w")
    dotlines = dot.readlines()
    dotlines = dotlines[:-1]
    for line in dotlines:
        dotout.write(line)
    dotout.write("{rank=min; ")
    for i in range(numinputs):
        dotout.write(" " + str(i) + ";")
    dotout.write("}" + "\n")
    dotout.write("}")
        

    dot.close()
    os.remove("graph.dot")
    dotout.close()

