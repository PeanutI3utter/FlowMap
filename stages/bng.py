import blifparser.blifparser as blifparser
import networkx as nx
import sys

from enum import IntEnum
from typing import Dict, List, Tuple


class gate(IntEnum):
    PI = 0
    AND = 1
    OR = 2
    PO = 3
    INTERMEDIATE = 4
    LUT = 5


def blif_to_bng(path_to_blif: str) -> nx.DiGraph:

    try:
        blif = blifparser.BlifParser(path_to_blif).blif
    except Exception:
        raise RuntimeError("Error while opening/reading BLIF file.")

    if len(blif.latches) > 0 or blif.fsm.ispresent:
        raise RuntimeError("Complex Logic Modules not supported yet")

    bng = nx.DiGraph()
    for input in blif.inputs.inputs:
        bng.add_node(input, gtype=gate.PI, label=input)

    for output in blif.outputs.outputs:
        bng.add_node(output, gtype=gate.PO, label=output)

    and_lookup: Dict[Tuple[bool, str], Dict[Tuple[bool, str], str]] = {}
    or_lookup: Dict[str, Dict[str, str]] = {}

    and_counter = 0
    or_counter = 0

    for bool_func in blif.booleanfunctions:
        truth_table = bool_func.truthtable
        inputs = bool_func.inputs
        num_input = len(inputs)

        ORs: List[str] = []
        for minterm in truth_table:
            if minterm[-1] != '1':
                continue

            ANDs = []
            for i in range(num_input):
                if inputs[i] not in bng.nodes:
                    bng.add_node(
                        inputs[i], gtype=gate.INTERMEDIATE, label=inputs[i]
                    )

                if minterm[i] == '1':
                    ANDs.append((False, inputs[i]))
                elif minterm[i] == '0':
                    ANDs.append((True, inputs[i]))

            while len(ANDs) > 1:
                left: Tuple[bool, str] = ANDs.pop(0)
                right: Tuple[bool, str] = ANDs.pop(0)

                if left not in and_lookup:
                    and_lookup[left] = {}

                if right not in and_lookup[left]:

                    new_and_node = f'AND[{and_counter}]'
                    and_lookup[left][right] = new_and_node
                    bng.add_node(
                        new_and_node, gtype=gate.AND, label=new_and_node
                    )
                    bng.add_edge(
                        left[1], new_and_node, inverted=left[0],
                        color='purple' if left[0] else ''
                    )
                    bng.add_edge(
                        right[1], new_and_node, inverted=right[0],
                        color='purple' if right[0] else ''
                    )
                    ANDs.append((False, new_and_node))
                    and_counter += 1
                else:
                    ANDs.append((False, and_lookup[left][right]))

            ORs.append(ANDs[0])

        while len(ORs) > 1:
            left: str = ORs.pop(0)
            right: str = ORs.pop(0)

            if left[1] not in or_lookup:
                or_lookup[left[1]] = {}

            if right[1] not in or_lookup[left[1]]:

                new_or_node = f'OR[{or_counter}]'
                or_lookup[left[1]][right[1]] = new_or_node
                bng.add_node(new_or_node, gtype=gate.OR, label=new_or_node)
                bng.add_edge(left[1], new_or_node, inverted=left[0], color='')
                bng.add_edge(
                    right[1], new_or_node, inverted=right[0], color=''
                )
                ORs.append((False, new_or_node))
                or_counter += 1
            else:
                ORs.append((False, or_lookup[left[1]][right[1]]))

        bng.add_edge(
            ORs[0][1], bool_func.output, inverted=ORs[0][0],
            color='purple' if ORs[0][0] else ''
        )

    return bng


def bng_to_blif(bng, inputnames, outputnames):

    try:
        outputf = open("output.blif", "w")
    except Exception:
        raise RuntimeError("Error while writing output BLIF file.")

    nodes = list(nx.topological_sort(bng))
    onSets = nx.get_node_attributes(bng, "onSet")
    outputf.write(".model mapping\n.inputs ")
    for inputname in inputnames:
        outputf.write(inputname + " ")
    outputf.write("\n.outputs " + outputnames + "\n\n")

    for node in nodes:
        if len(list(bng.predecessors(nodes[node]))) > 0:
            inpts = list(bng.in_edges(node, data=False))
            inpts_str = ""
            for inp in inpts:
                if inp[0] < len(inputnames):
                    inpts_str += inputnames[inp[0]] + " "
                else:
                    inpts_str += "w" + str(inp[0]) + " "
            if len(list(bng.out_edges(node, data=False))) == 0:
                outputf.write(".names " + inpts_str + outputnames + "\n")
            else:
                outputf.write(
                    ".names " + inpts_str + "w" + str(inpts[0][1]) + "\n"
                )

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


# positional cube notation
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
            negatedCube.append(
                inSymbol.ON if onSet[cube][symbol] == inSymbol.OFF else
                inSymbol.OFF if onSet[cube][symbol] == inSymbol.ON else
                inSymbol.DC
            )

        negated.append(negatedCube)
    return negated


def subgraphToOnSet(subgraph):
    nodes = list(nx.topological_sort(subgraph))
    inputs = []
    output = -1

    for node in range(len(nodes)):
        if len(list(subgraph.predecessors(nodes[node]))) == 0:
            inputs.append(node)
        if len(list(subgraph.successors(nodes[node]))) == 0:
            output = node

    for node in range(len(nodes)):
        if len(list(subgraph.predecessors(nodes[node]))) == 0:
            inputOnSet = [inSymbol.DC] * len(inputs)
            inputOnSet[node] = inSymbol.ON
            nx.set_node_attributes(subgraph, {node: {"onSet": [inputOnSet]}})
            continue
        else:
            onSets = nx.get_node_attributes(subgraph, "onSet")
            incomingEdges = list(subgraph.in_edges(node, data=True))
            leftParent = incomingEdges[0][0]
            rightParent = incomingEdges[1][0]
            leftEdgeInverted = bool(incomingEdges[0][2].get("inverted"))
            rightEdgeInverted = bool(incomingEdges[1][2].get("inverted"))
            leftOnSet = negateCubes(onSets[leftParent]) \
                if leftEdgeInverted else onSets[leftParent]
            rightOnSet = negateCubes(onSets[rightParent]) \
                if rightEdgeInverted else onSets[rightParent]
            gateTypes = nx.get_node_attributes(subgraph, "gtype")
            ownGate = gateTypes[nodes[node]]
            if (ownGate == gate.AND):
                ownOnSet = handleAND(leftOnSet, rightOnSet)
            elif (ownGate == gate.OR):
                ownOnSet = handleOR(leftOnSet, rightOnSet)
            else:
                raise RuntimeError("unexpected gate type")
                sys.exit()
            nx.set_node_attributes(subgraph, {node: {'onSet': ownOnSet}})
        if (node == output):
            return ownOnSet
