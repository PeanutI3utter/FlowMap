import blifparser.blifparser as blifparser
import networkx as nx
import sympy as sp

from stages.enums import gate
from typing import Dict, List, Tuple


def blif_to_bng(path_to_blif: str) -> nx.DiGraph:
    """
    Build Boolean Network Graph from BLIF files

    Input:
        path_to_blif: Path to BLIF file

    Output:
        NetworkX.DiGraph representation of the BNG
    """

    try:
        blif = blifparser.BlifParser(path_to_blif).blif
    except Exception:
        raise RuntimeError("Error while opening/reading BLIF file.")

    if len(blif.latches) > 0 or blif.fsm.ispresent:
        raise RuntimeError("Complex Logic Modules not supported yet")

    bng = nx.DiGraph(name=blif.model.name)
    for input in blif.inputs.inputs:
        bng.add_node(input, gtype=gate.PI, label=input)

    for output in blif.outputs.outputs:
        bng.add_node(output, gtype=gate.PO, label=output)

    # Lookup tables for reusable gates
    and_lookup: Dict[Tuple[bool, str], Dict[Tuple[bool, str], str]] = {}
    or_lookup: Dict[Tuple[bool, str], Dict[Tuple[bool, str], str]] = {}

    and_counter = 0
    or_counter = 0

    for bool_func in blif.booleanfunctions:
        truth_table = bool_func.truthtable
        inputs = bool_func.inputs
        num_input = len(inputs)
        for i in range(num_input):
            if inputs[i] not in bng.nodes:
                bng.add_node(
                    inputs[i], gtype=gate.INTERMEDIATE, label=inputs[i]
                )

        ORs: List[str] = []
        # Build a tree of AND gates for each minterm
        for minterm in truth_table:
            if minterm[-1] != '1':
                continue

            ANDs = []
            for i in range(num_input):
                if minterm[i] == '1':
                    ANDs.append((False, inputs[i]))
                elif minterm[i] == '0':
                    ANDs.append((True, inputs[i]))

            while len(ANDs) > 1:
                left: Tuple[bool, str] = ANDs.pop(0)
                right: Tuple[bool, str] = ANDs.pop(0)

                # Check if node with left input gate exists
                if left not in and_lookup:
                    and_lookup[left] = {}

                """
                Check if node with right input gate exists
                If so, then to be built AND gate exists already
                and can be reused.
                Otherwise build new AND gate and store it in lookup table
                """
                if right not in and_lookup[left]:

                    new_and_node = f'AND[{and_counter}]'
                    and_lookup[left][right] = new_and_node
                    bng.add_node(
                        new_and_node, gtype=gate.AND, label=new_and_node,
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

        # Build a tree of OR gates combing all AND gates
        while len(ORs) > 1:
            left: str = ORs.pop(0)
            right: str = ORs.pop(0)

            # Check if node with left input gate exists
            if left not in or_lookup:
                or_lookup[left] = {}

            """
            Check if node with right input gate exists
            If so, then to be built OR gate exists already
            and can be reused.
            Otherwise build new OR gate and store it in lookup table
            """
            if right not in or_lookup[left]:

                new_or_node = f'OR[{or_counter}]'
                or_lookup[left][right] = new_or_node
                bng.add_node(
                    new_or_node, gtype=gate.OR, label=new_or_node,
                )
                bng.add_edge(
                    left[1],
                    new_or_node,
                    inverted=left[0],
                    color='purple' if right[0] else ''
                )
                bng.add_edge(
                    right[1],
                    new_or_node,
                    inverted=right[0],
                    color='purple' if right[0] else ''
                )
                ORs.append((False, new_or_node))
                or_counter += 1
            else:
                ORs.append((False, or_lookup[left][right]))

        # Create intermediate output nodes
        if not bng.has_node(bool_func.output):
            bng.add_node(
                bool_func.output,
                gtype=gate.INTERMEDIATE,
                label=bool_func.output,
            )
        bng.add_edge(
            ORs[0][1], bool_func.output, inverted=ORs[0][0],
            color='purple' if ORs[0][0] else ''
        )

    return bng


def bng_to_blif(
    bng: nx.DiGraph,
    output_file: str = 'a.blif',
    model_name: str = 'fpga'
) -> None:
    """
    Build BLIF file from Boolean Network Graph containing LUTs

    Input:
        bng:
            Boolean Network Graph containing LUTs
        output_file:
            Path to output BLIF file
        model_name: Name of .model in BLIF file

    Output:
        None
    """

    try:
        file = open(output_file, "w")
    except Exception:
        raise RuntimeError("Error while writing output BLIF file.")

    file.write(f'.model {model_name}\n')

    nodes = [(node, bng.nodes[node])for node in nx.topological_sort(bng)]

    inputs_str = '.inputs'
    outputs_str = '.outputs'
    func_str = ''

    for node, attributes in nodes:
        label = attributes['label']

        # Add to .inputs, no output-cover
        if attributes['gtype'] == gate.PI:
            inputs_str += f' {label}'
            continue

        # Add to .outputs, generate output cover
        if attributes['gtype'] == gate.PO:
            outputs_str += f' {label}'

        func: sp.logic.boolalg.BooleanFunction = attributes['func']

        # Generate .names
        input_order = []
        func_str += '.names'
        for input in func.free_symbols:
            func_str += f' {input}'
            input_order.append(input)
        func_str += f' {node}\n'

        # Generate output cover
        sat = sp.logic.inference.satisfiable(func, all_models=True)
        if sat:
            for minterm in sat:
                for input in input_order:
                    val = minterm[input]
                    func_str += f'{int(val)}'
                func_str += ' 1\n'

    func_str += '.end'
    file.write(inputs_str + '\n')
    file.write(outputs_str + '\n')
    file.write(func_str + '\n')

    file.close()
