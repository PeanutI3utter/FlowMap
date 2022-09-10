import blifparser.blifparser as blifparser
import boolexpr as bx
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


def bng_to_blif(bng: nx.DiGraph, output_file='a.blif', model_name='fpga'):

    try:
        file = open(output_file, "w")
    except Exception:
        raise RuntimeError("Error while writing output BLIF file.")

    file.write(f'.model {model_name}\n')

    nodes = [(node, bng.nodes[node] )for node in nx.topological_sort(bng)]
    print(len(nodes))

    inputs_str = '.inputs'
    outputs_str = '.outputs'
    func_str = ''

    for node, attributes in nodes:
        label = attributes['label']
        if attributes['gtype'] == gate.PI:
            inputs_str += f' {label}'
            continue
        
        if attributes['gtype'] == gate.PO:
            outputs_str += f' {label}'

        func: bx.BoolExpr = attributes['func']

        input_order = []
        func_str += '.names'
        for input in func.support():
            func_str += f' {input}'
            input_order.append(input)
        func_str += f' {node}\n'

        for minterm in func.iter_sat():
            for input in input_order:
                val = minterm[input]
                func_str += f'{val}'
            func_str += ' 1\n'
    
    func_str += '.end'
    file.write(inputs_str + '\n')
    file.write(outputs_str + '\n')
    file.write(func_str + '\n')

    file.close()


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
