import networkx as nx
import sys
import pydot
from networkx.drawing.nx_pydot import graphviz_layout
from networkx.drawing.nx_pydot import write_dot
import blifparser.blifparser as blifparser
import os

from enum import IntEnum

class gate(IntEnum):
    PI = 0
    AND = 1
    OR = 2
    LUT = 3


def blif_to_bng(blif_path: str):

    try:
        parser = blifparser.BlifParser(blif_path)
        blif = parser.blif
        boolfunc = blif.booleanfunctions[0]
        minterms = boolfunc.truthtable
        inputnames = boolfunc.inputs
        outputnames = boolfunc.output
    except:
        raise RuntimeError("Error while opening/reading BLIF file.")
        
    nodeid = 0
    bng = nx.DiGraph()


    width = len(boolfunc.inputs)
    currentLevel = 0

    for _ in range(width):
        bng.add_node(nodeid, gtype=gate.PI, level=currentLevel, label = nodeid)
        nodeid += 1
    currentLevel += 1

    lastGateInMinterm = []

    for minterm in minterms:
        currentLevel = 1
        minterm = list(map(int, list(reversed(minterm[:-1]))))

        for i in range(width):
            if (i == 1): continue
            
            bit = minterm[i]
            bng.add_node(nodeid, gtype=gate.AND, level=currentLevel, label = "AND")
            
            if (i == 0):
                nextbit = minterm[1]
                if (bit & nextbit):
                    bng.add_edge(0, nodeid, inverted=False)
                    bng.add_edge(1, nodeid, inverted=False)
                elif (bit):
                    bng.add_edge(0, nodeid, inverted=False)
                    bng.add_edge(1, nodeid, inverted=True, color="red")
                elif (nextbit):
                    bng.add_edge(0, nodeid, inverted=True, color="red")
                    bng.add_edge(1, nodeid, inverted=False)
                else:
                    bng.add_edge(0, nodeid, inverted=True, color="red")
                    bng.add_edge(1, nodeid, inverted=True, color="red")
                currentLevel += 1
                nodeid += 1
                continue
             
            if (bit == 1):                
                bng.add_edge(nodeid - 1, nodeid, inverted=False)
                bng.add_edge(i, nodeid, inverted=False)
            else:
                bng.add_edge(nodeid - 1, nodeid, inverted=False)
                bng.add_edge(i, nodeid, inverted=True, color="red")
                
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
            continue
        bng.add_node(nodeid, gtype=gate.OR, level = currentLevel, label = "OR")
        bng.add_edge(nodeid - 1, nodeid, inverted=False)
        bng.add_edge(lastGateInMinterm[i], nodeid, inverted=False)
        nodeid += 1
        currentLevel += 1

    return (bng, inputnames, outputnames)




def bng_to_blif(bng, inputnames, outputnames):

    try:
        outputf = open("output.blif", "w")
    except:
        raise RuntimeError("Error while writing output BLIF file.")

    nodes = list(nx.topological_sort(bng))
    onSets = nx.get_node_attributes(bng, "onSet")
    outputf.write(".model mapping\n.inputs ")
    for inputname in inputnames:
        outputf.write(inputname + " ")
    outputf.write("\n.outputs " + outputnames + "\n\n")
    
    for node in nodes:
        if len(list(bng.predecessors(nodes[node]))) > 0:
            inpts = list(bng.in_edges(node, data = False))
            inpts_str = ""
            for inp in inpts:
                if inp[0] < len(inputnames):
                    inpts_str += inputnames[inp[0]] + " "
                else:
                    inpts_str += "w" + str(inp[0]) + " " 
            if len(list(bng.out_edges(node, data = False))) == 0:
                outputf.write(".names " + inpts_str + outputnames + "\n")
            else:
                outputf.write(".names " + inpts_str + "w" + str(inpts[0][1]) + "\n")

            for cube in onSets[node]:
                cubestr = ""
                for symbol in cube:
                    if symbol == inSymbol.ON:
                        cubestr += "1"
                    if symbol == inSymbol.OFF:
                        cubestr += "0"
                    if symbol == inSymbol.DC:
                        cubestr += "-"
                outputf.write(cubestr + " 1" + "\n")

            outputf.write("\n")

    outputf.write(".end")
    outputf.close()
            
            



#positional cube notation
class inSymbol(IntEnum):
    INV = 0
    ON = 1
    OFF = 2
    DC = 3

    
def handleAND(lhs, rhs):
    conjunction = []
    for entry_l in lhs:
        for entry_r in rhs:
            newcube = []
            for i in range(len(entry_l)):
                intersection = inSymbol(entry_l[i] & entry_r[i])
                if (intersection == 0):
                    newcube = []
                    break
                else:
                    newcube.append(intersection)
            if newcube != []:
                conjunction.append(newcube)
    return conjunction


def handleOR(lhs, rhs):
    disjunction = lhs + rhs
    return disjunction


def negateCubes(onSet):
    negated = []
    for cube in range(len(onSet)):
        negatedCube = []
        for symbol in range(len(onSet[cube])):
            negatedCube.append(inSymbol.ON if onSet[cube][symbol] == inSymbol.OFF else
                           inSymbol.OFF if onSet[cube][symbol] == inSymbol.ON else
                           inSymbol.DC)
        negated.append(negatedCube)
    return negated

    
def subgraphToOnSet(subgraph):
    nodes = list(nx.topological_sort(subgraph))
    inputs = []
    output= -1

    for node in range(len(nodes)):
        if len(list(subgraph.predecessors(nodes[node]))) == 0:
            inputs.append(node)
        if len(list(subgraph.successors(nodes[node]))) == 0:
            output = node

    for node in range(len(nodes)):
        if len(list(subgraph.predecessors(nodes[node]))) == 0:
            inputOnSet = [inSymbol.DC] * len(inputs)
            inputOnSet[node] = inSymbol.ON
            nx.set_node_attributes(subgraph, {node:{"onSet":[inputOnSet]}})
            continue
        else:
            onSets = nx.get_node_attributes(subgraph, "onSet")
            incomingEdges = list(subgraph.in_edges(node, data = True))
            leftParent = incomingEdges[0][0]
            rightParent = incomingEdges[1][0]
            leftEdgeInverted = incomingEdges[0][2].get("inverted") == True
            rightEdgeInverted = incomingEdges[1][2].get("inverted") == True
            leftOnSet = negateCubes(onSets[leftParent]) if leftEdgeInverted else onSets[leftParent]
            rightOnSet = negateCubes(onSets[rightParent]) if rightEdgeInverted else onSets[rightParent]
            gateTypes = nx.get_node_attributes(subgraph, "gtype")
            ownGate = gateTypes[nodes[node]]
            if(ownGate == gate.AND):
                ownOnSet = handleAND(leftOnSet, rightOnSet)
            elif(ownGate == gate.OR):
                ownOnSet = handleOR(leftOnSet, rightOnSet)
            else:
                raise RuntimeError("unexpected gate type")
                sys.exit()
            nx.set_node_attributes(subgraph, {node:{'onSet':ownOnSet}})
        if (node == output):
            return ownOnSet

    

    
