import sympy as sp
import networkx as nx

from stages.enums import gate


def flowmap(labeled_graph: nx.DiGraph) -> nx.DiGraph:
    """The mapping phase of the FlowMap algorithm

    Input:
        labeled_graph: boolean network graph which is labeled
        according to FlowMap labeling phase

    Output:
        A graph where each node represents a LUT.
        The logical function of the LUT is stored
        in the node attr 'func'
    """
    LUT_graph = nx.DiGraph()
    circuit_outputs = [
        node for node, gtype in labeled_graph.nodes(data='gtype')
        if gtype == gate.PO
    ]
    circuit_inputs = [
        node for node, gtype in labeled_graph.nodes(data='gtype')
        if gtype == gate.PI
    ]

    to_be_mapped = []
    # begin mapping from POs
    for node in circuit_outputs:
        LUT_graph.add_node(node, label=node, gtype=gate.PO)
        to_be_mapped.append(node)

    for circuit_input in circuit_inputs:
        LUT_graph.add_node(
            circuit_input, func=sp.symbols(circuit_input),
            label=circuit_input, gtype=gate.PI
        )

    # while there are nodes that need to be mapped
    while len(to_be_mapped) > 0:
        # node that is to be mapped is output of LUT
        LUT_output = to_be_mapped.pop(0)

        # all nodes contained by the LUTs (except PIs)
        LUT_nodes = list(nx.topological_sort(labeled_graph.subgraph(
            node for node in labeled_graph.nodes[LUT_output]['cut']
            if node not in circuit_inputs
        )))

        func_stack = {}

        # recursively build logical function of the LUT in topological order
        for LUT_node in LUT_nodes:
            inputs = [i for i, _ in labeled_graph.in_edges(LUT_node)]

            if (labeled_graph.nodes[LUT_node]['gtype'] == gate.AND
                    or labeled_graph.nodes[LUT_node]['gtype'] == gate.OR):

                assert len(inputs) == 2

                """
                If input gate 0 is not inside LUT, a symbolic variable
                is used for the input gate.
                Otherwise, the calculated logical function of the input
                gate (the input gate is guaranteed to have a calculcated
                logical function as we traverse in topological order) is
                used for the input gate 0
                """
                if inputs[0] not in LUT_nodes:
                    a = sp.symbols(inputs[0])
                    func_stack[inputs[0]] = a
                    if inputs[0] not in LUT_graph.nodes:
                        LUT_graph.add_node(
                            inputs[0], label=inputs[0], gtype=gate.LUT
                        )
                        to_be_mapped.append(inputs[0])
                    LUT_graph.add_edge(inputs[0], LUT_output)

                else:
                    a = func_stack[inputs[0]]

                if inputs[1] not in LUT_nodes:
                    b = sp.symbols(inputs[1])
                    func_stack[inputs[1]] = b
                    if inputs[1] not in LUT_graph.nodes:
                        LUT_graph.add_node(
                            inputs[1], label=inputs[1], gtype=gate.LUT
                        )
                        to_be_mapped.append(inputs[1])

                    LUT_graph.add_edge(inputs[1], LUT_output)
                else:
                    b = func_stack[inputs[1]]

                # handle inverted edges
                if labeled_graph.edges[inputs[0], LUT_node]['inverted']:
                    a = ~a

                if labeled_graph.edges[inputs[1], LUT_node]['inverted']:
                    b = ~b

                # Combine input gate functions into one
                if labeled_graph.nodes[LUT_node]['gtype'] == gate.OR:
                    func_stack[LUT_node] = a | b
                else:
                    func_stack[LUT_node] = a & b

            else:
                assert len(inputs) == 1
                # input gate to be packed into LUT
                if inputs[0] not in LUT_nodes:
                    a = sp.symbols(inputs[0])
                    func_stack[inputs[0]] = a
                    if inputs[0] not in LUT_graph.nodes:
                        LUT_graph.add_node(
                            inputs[0], label=inputs[0], gtype=gate.LUT
                        )
                        to_be_mapped.append(inputs[0])
                    LUT_graph.add_edge(inputs[0], LUT_output)
                else:
                    a = func_stack[inputs[0]]

                # handle inverted edges
                if labeled_graph.edges[inputs[0], LUT_node]['inverted']:
                    func_stack[LUT_node] = ~a
                else:
                    func_stack[LUT_node] = a

        # recursive built up output function of the generated LUT
        LUT_graph.nodes[LUT_output]['func'] = func_stack[LUT_output]

    return LUT_graph
