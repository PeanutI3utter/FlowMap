import networkx as nx
import pydot
from networkx.drawing.nx_pydot import graphviz_layout
from networkx.drawing.nx_pydot import write_dot
import blifparser.blifparser as blifparser
import os
from util.bngprint import print_bng

from enum import Enum

class gate(Enum):
    PI = 0
    AND = 1
    OR = 2


def blif_to_bng(blif_path: str):
    try:
        parser = blifparser.BlifParser(blif_path)
        blif = parser.blif
        boolfunc = blif.booleanfunctions[0]
        minterms = boolfunc.truthtable
    except:
        raise RuntimeError("Error while opening/reading BLIF file.")
        
    nodeid = 0
    bng = nx.DiGraph()

    width = len(boolfunc.inputs)
    currentLevel = 0

    for _ in range(width):
        bng.add_node(str(nodeid), gtype=gate.PI, level=currentLevel, label = str(nodeid))
        nodeid += 1
    currentLevel += 1

    lastGateInMinterm = []

    minterm_spacing = 0

    for minterm in minterms:
        currentLevel = 1
        minterm = list(map(int, list(reversed(minterm[:-1]))))

        for i in range(width):
            if (i == 1): continue
            
            bit = minterm[i]
            bng.add_node(str(nodeid), gtype=gate.AND, level=currentLevel, label = "AND")
            
            if (i == 0):
                nextbit = minterm[1]
                if (bit & nextbit):
                    bng.add_edge('0', str(nodeid), inverted=False)
                    bng.add_edge('1', str(nodeid), inverted=False)
                elif (bit):
                    bng.add_edge('0', str(nodeid), inverted=False)
                    bng.add_edge('1', str(nodeid), inverted=True, color="red")
                elif (nextbit):
                    bng.add_edge('0', str(nodeid), inverted=True, color="red")
                    bng.add_edge('1', str(nodeid), inverted=False)
                else:
                    bng.add_edge('0', str(nodeid), inverted=True, color="red")
                    bng.add_edge('1', str(nodeid), inverted=True, color="red")
                currentLevel += 1
                nodeid += 1
                continue
            
            if (bit == 1):                
                bng.add_edge(str(nodeid - 1), str(nodeid), inverted=False)
                bng.add_edge(str(i), str(nodeid), inverted=False)
            else:
                bng.add_edge(str(nodeid - 1), str(nodeid), inverted=False)
                bng.add_edge(str(i), str(nodeid), inverted=True, color="red")
                
            nodeid += 1
            currentLevel += 1
            
        if (i == width - 1):
            lastGateInMinterm.append(nodeid - 1)

        
    currentLevel = 20#need max
    for i in range(len(lastGateInMinterm)):
        if (i == 1): continue
        if (i == 0):
            bng.add_node(str(nodeid), gtype=gate.OR, level = currentLevel, label = "OR")
            bng.add_edge(str(lastGateInMinterm[0]), str(nodeid), inverted=False)
            bng.add_edge(str(lastGateInMinterm[1]), str(nodeid), inverted=False)
            nodeid += 1
            currentLevel += 1
            continue
        bng.add_node(str(nodeid), gtype=gate.OR, level = currentLevel, label = "OR")
        bng.add_edge(str(nodeid - 1), str(nodeid), inverted=False)
        bng.add_edge(str(lastGateInMinterm[i]), str(nodeid), inverted=False)
        nodeid += 1
        currentLevel += 1

    return bng
