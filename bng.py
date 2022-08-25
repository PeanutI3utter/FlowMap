import networkx as nx

import pydot
from networkx.drawing.nx_pydot import graphviz_layout
from networkx.drawing.nx_pydot import write_dot


from enum import Enum

class gate(Enum):
    PI = 0
    PO = 1
    AND = 2
    OR = 3
    
    
nodeid = 0
bng = nx.Graph()
infile = open("input.blif", "r")

width = 11
currentLevel = 0

for primary in range(width):
    bng.add_node(nodeid, gtype=gate.PI, level=currentLevel, label = str(nodeid))
    nodeid += 1
currentLevel += 1

lastGateInMinterm = []

minterm_spacing = 0;
lines = infile.readlines()
for line in lines:
    currentLevel = 1
    minterm = int(line, 2)

    for i in range(width):
        if (i == 1): continue
        bit = (minterm >> i) & 1
        bng.add_node(nodeid, gtype=gate.AND, level=currentLevel, label = "AND")
        
        if (i == 0):
            nextbit = (minterm >> 1) & 1
            if (bit & nextbit):
                bng.add_edge(0, nodeid, inverted=False)
                bng.add_edge(1, nodeid, inverted=False)
            elif (bit):
                bng.add_edge(0, nodeid, inverted=False)
                bng.add_edge(1, nodeid, inverted=True, label="~", color="red")
            elif (nextbit):
                bng.add_edge(0, nodeid, inverted=True, label="~", color="red")
                bng.add_edge(1, nodeid, inverted=False)
            else:
                bng.add_edge(0, nodeid, inverted=True, label="~", color="red")
                bng.add_edge(1, nodeid, inverted=True, label="~", color="red")
            currentLevel += 1
            nodeid += 1
            continue
         
        if (bit == 1):                
            bng.add_edge(nodeid - 1, nodeid, inverted=False)
            bng.add_edge(i, nodeid, inverted=False)
        else:
            bng.add_edge(nodeid - 1, nodeid, inverted=False)
            bng.add_edge(i, nodeid, inverted=True, label="~", color="red")
            
        nodeid += 1
        currentLevel += 1
        
    if (i == width - 1):
        lastGateInMinterm.append(nodeid - 1)

        
currentLevel = 20#need max
for i in range(len(lastGateInMinterm)):
    if (i == 1): continue
    if (i == 0):
        bng.add_node(nodeid, gtype=gate.OR, level = currentLevel, label = "OR")
        bng.add_edge(lastGateInMinterm[0], nodeid, inverted=False)
        bng.add_edge(lastGateInMinterm[1], nodeid, inverted=False)
        nodeid += 1
        currentLevel += 1
        #i += 2
        continue
    bng.add_node(nodeid, gtype=gate.OR, level = currentLevel, label = "OR")
    bng.add_edge(nodeid - 1, nodeid, inverted=False)
    bng.add_edge(lastGateInMinterm[i], nodeid, inverted=False)
    nodeid += 1
    currentLevel += 1

write_dot(bng, 'graph.dot')

dot = open("graph.dot", "r")
dotout = open("graph_out.dot", "w")
dotlines = dot.readlines()
dotlines = dotlines[:-1]
for line in dotlines:
    dotout.write(line)
dotout.write("{rank=min; ")
for i in range(width):
    dotout.write(" " + str(i) + ";")
dotout.write("}" + "\n")
dotout.write("}")
    


dotout.close()
infile.close()
