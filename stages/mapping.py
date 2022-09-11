import sympy as sp
import networkx as nx

from stages.enums import gate, inSymbol


def flowmap(labeled_graph: nx.DiGraph) -> nx.DiGraph:
    LUT_graph = nx.DiGraph()
    circuit_outputs = [
        node for node, deg in labeled_graph.out_degree() if not deg
    ]
    circuit_inputs = [
        node for node, deg in labeled_graph.in_degree() if not deg
    ]

    to_be_mapped = []
    for node in circuit_outputs:
        LUT_graph.add_node(node, label=node, gtype=gate.PO)
        to_be_mapped.append(node)

    for circuit_input in circuit_inputs:
        LUT_graph.add_node(
            circuit_input, func=sp.symbols(circuit_input),
            label=circuit_input, gtype=gate.PI
        )

    while len(to_be_mapped) > 0:
        LUT_output = to_be_mapped.pop(0)
        LUT_nodes = list(nx.topological_sort(labeled_graph.subgraph(
            node for node in labeled_graph.nodes[LUT_output]['cut']
            if node not in circuit_inputs
        )))

        func_stack = {}

        for LUT_node in LUT_nodes:
            inputs = [i for i, _ in labeled_graph.in_edges(LUT_node)]

            if (labeled_graph.nodes[LUT_node]['gtype'] == gate.AND
                    or labeled_graph.nodes[LUT_node]['gtype'] == gate.OR):

                assert len(inputs) == 2
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

                if labeled_graph.edges[inputs[0], LUT_node]['inverted']:
                    a = ~a

                if labeled_graph.edges[inputs[1], LUT_node]['inverted']:
                    b = ~b

                if labeled_graph.nodes[LUT_node]['gtype'] == gate.OR:
                    func_stack[LUT_node] = a | b
                else:
                    func_stack[LUT_node] = a & b

            else:
                assert len(inputs) == 1
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

                if labeled_graph.edges[inputs[0], LUT_node]['inverted']:
                    func_stack[LUT_node] = ~a
                else:
                    func_stack[LUT_node] = a

        LUT_graph.nodes[LUT_output]['func'] = func_stack[LUT_output]

    return LUT_graph


# this is based on the assumption that the order of incoming
# edges always coincides with the order of the input variables
# in the onSet of a LUT
def merge_LUTs(subgraph: nx.DiGraph, graph: nx.DiGraph) \
        -> nx.DiGraph:

    nodes = list(nx.topological_sort(subgraph))
    # make list from set
    inputs = list(
        {node for node in graph.nodes if graph.out_edges(node)[1] in nodes}
    )

    onSets = nx.get_node_attributes(nodes, "onSet")
    extendedOnSets = []

    for node in range(len(nodes)):
        if len(list(subgraph.predecessors(nodes[node]))) == 0:
            onSet = onSets[node]
            incomingEdges = list(graph.in_edges(node, data=False))

            # determine which inputs are connected to the current (upper) LUT
            connectedPositions = [False] * len(inputs)
            for inEdge in incomingEdges:
                position = inputs.index(inEdge[1])
                connectedPositions[position] = True
            # extend truth table/onSet with DC based on connected positions
            newOnSet = []
            for cube in onSet:
                newCube = []
                offset = 0
                for i in range(len(inputs)):
                    if connectedPositions[i]:
                        # keep old cube value (which is at i - offset)
                        newCube.append(cube[i - offset])
                    else:
                        # add new DC value
                        newCube.append(inSymbol.DC)
                        offset += 1
                newOnSet.append(newCube)
            extendedOnSets.append(newOnSet)

    # merge the extendedOnSets based on onSet of lower LUT
    # todo: check if the order of inputs in the lower onSet
    # is the same as the node order, otherwise use edges
    # to get the correct order and reorder the elements of
    # extendedOnSets accordingly
    lowerOnSet = onSets[nodes[-1]]
    for cube in lowerOnSet:
        mergeOnSets(extendedOnSets, cube)


def mergeOnSets(onSets, cube):
    return
