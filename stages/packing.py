import sympy as sp
import networkx as nx

from itertools import chain
from stages.enums import gate
from stages.label import extract_subgraph_from


def gate_decomposition(LUT_graph: nx.DiGraph, k: int):
    xor_masks = [(0, 1), (1, 0), (1, 1)]

    while True:
        LUT_nodes = [
            node for node in nx.topological_sort(LUT_graph)
            if LUT_graph.nodes[node]['gtype'] == gate.LUT
        ]
        decomp_found = False
        for LUT_node in LUT_nodes:
            LUT_parents = [
                node for node in LUT_graph.predecessors(LUT_node)
                if LUT_graph.nodes[node]['gtype'] == gate.LUT
            ]

            if len(LUT_parents) < 2:
                continue
            for i in range(len(LUT_parents) - 1):
                parent_i = LUT_parents[i]
                i_predecessors = list(LUT_graph.predecessors(parent_i))
                i_successors = list(LUT_graph.successors(parent_i))

                if len(i_successors) > 1:
                    continue

                for j in range(i + 1, len(LUT_parents)):
                    parent_j = LUT_parents[j]
                    j_predecessors = list(
                        LUT_graph.predecessors(parent_j)
                    )
                    j_successors = list(
                        LUT_graph.successors(parent_j)
                    )

                    if len(j_successors) > 1 \
                            or len(i_predecessors) + len(j_predecessors) > k:
                        continue

                    class_graph = nx.Graph([
                        ('00', '01'),
                        ('00', '10'),
                        ('00', '11'),
                        ('01', '10'),
                        ('01', '11'),
                        ('10', '11')
                    ])

                    LUT_func: sp.logic.boolalg.BooleanFunction = \
                        LUT_graph.nodes[LUT_node]['func']
                    var_i = sp.symbols(parent_i)
                    var_j = sp.symbols(parent_j)
                    sat = sp.logic.inference.satisfiable(
                            LUT_func, all_models=True)

                    for cube in sat:
                        if not cube:
                            break
                        for mask in xor_masks:
                            input_dict = {
                                key: val for key, val in cube.items()
                            }
                            input_dict[var_i] ^= mask[0]
                            input_dict[var_j] ^= mask[1]
                            if not LUT_func.subs(input_dict):
                                a_i = str(int(input_dict[var_i]))
                                a_j = str(int(input_dict[var_j]))
                                b_i = str(int(cube[var_i]))
                                b_j = str(int(cube[var_j]))

                                if class_graph.has_edge(f'{a_i}{a_j}',
                                                        f'{b_i}{b_j}'):

                                    class_graph.remove_edge(
                                        f'{a_i}{a_j}',
                                        f'{b_i}{b_j}'
                                    )

                    connected_comps = list(
                        nx.connected_components(class_graph)
                    )

                    if len(connected_comps) < 3:
                        decomp_found = True
                        new_childlut_str = f'{var_i}_{var_j}'
                        new_childlut = sp.symbols(new_childlut_str)
                        new_vars = list(LUT_func.free_symbols)
                        new_vars.remove(var_i)
                        new_vars.remove(var_j)
                        new_vars.append(new_childlut)
                        new_truthtable = []
                        sat = sp.logic.inference.satisfiable(
                                LUT_func, all_models=True)
                        for cube in sat:
                            entry = [0] * len(new_vars)
                            for var, val in cube.items():
                                if var in new_vars:
                                    entry[new_vars.index(var)] = int(val)

                            boundvars = f'{int(cube[var_i])}{int(cube[var_j])}'
                            if boundvars in connected_comps[0]:
                                entry[-1] = 1

                            new_truthtable.append(entry)

                        LUT_graph.nodes[LUT_node]['func'] = sp.simplify_logic(
                            sp.POSform(new_vars, new_truthtable)
                        )

                        child_func = sp.false
                        for boundvars in connected_comps[0]:
                            if boundvars[0] == '1':
                                a = LUT_graph.nodes[parent_i]['func']
                            else:
                                a = ~LUT_graph.nodes[parent_i]['func']

                            if boundvars[1] == '1':
                                b = LUT_graph.nodes[parent_j]['func']
                            else:
                                b = ~LUT_graph.nodes[parent_j]['func']

                            child_func |= a & b

                        LUT_graph.add_node(
                            new_childlut_str,
                            label=new_childlut_str,
                            func=child_func,
                            gtype=gate.LUT
                        )

                        for node in chain(i_predecessors, j_predecessors):
                            LUT_graph.add_edge(
                                node,
                                new_childlut_str
                            )

                        LUT_graph.add_edge(new_childlut_str, LUT_node)
                        LUT_graph.remove_nodes_from(
                            (parent_i, parent_j)
                        )
                    if decomp_found:
                        break
                if decomp_found:
                    break
            if decomp_found:
                break
        if not decomp_found:
            break


def flowpackGraph(graph: nx.DiGraph) -> nx.DiGraph:
    """
    Create graph which is used to determine the label of the output of
    the given subgraph

    Input:
        graph: Original graph, from which a flow graph is to be created

    Output:
        flow graph of the original function, the drain node has a attribute
        "contains", which is a set of all nodes that is combined into the
        drain node.

    Requirements:
        Requires that every node except the output node in subgraph to
        have the attribute "level"
    """
    flowgraph = nx.DiGraph()
    nodes_sorted = list(nx.topological_sort(graph))

    input_nodes = [node for node, deg in graph.in_degree() if not deg]
    output = nodes_sorted[-1]

    # nodes which are not input nodes nor output node
    inter_nodes = nodes_sorted[len(input_nodes):-1]

    # input nodes are connected to S (sink)
    for node in input_nodes:
        flowgraph.add_edge('S', node + '_in')
        flowgraph.add_edge(node + '_in', node + '_out', capacity=1)

    # Split intermediate node, add bridging edge
    # add edges going to intermediate node
    for node in inter_nodes:
        incoming_edges = graph.in_edges(node)
        for edge in incoming_edges:
            flowgraph.add_edge(edge[0] + '_out', node + '_in')
        flowgraph.add_edge(node + '_in', node + '_out', capacity=1)

    for node in graph.predecessors(output):
        flowgraph.add_edge(node + '_out', output)

    return flowgraph


def flow_pack(LUT_graph: nx.DiGraph, k: int):
    for node in LUT_graph:
        if LUT_graph.nodes[node]['gtype'] == gate.PI:
            continue
        
        packed = {node}

        best_cut:nx.DiGraph = extract_subgraph_from(LUT_graph, node)

        _, (_, X) = nx.minimum_cut(flowpackGraph(best_cut), 'S', node)

        for n in X:
            if n.endswith('_in'):
                best_cut = nx.contracted_nodes(
                    best_cut, node, n[:-3], self_loops=False
                )
                packed.add(n[:-3])

        while True:
            s_t_nodes = set([
                n for n in best_cut.predecessors(node)
                if best_cut.nodes[n]['gtype'] != gate.PI
            ])
            
            ranked_cuts = []
            for s_t_node in s_t_nodes:
                try:
                    new_cut: nx.DiGraph = \
                        nx.contracted_nodes(
                            best_cut, node, s_t_node, self_loops=False
                        )
                    maxflow, _ = nx.maximum_flow(flowpackGraph(new_cut), 'S', node)
                    if maxflow <= k:
                        rank = new_cut.in_degree(node)
                        ranked_cuts.append((rank, s_t_node, new_cut))
                except nx.NetworkXUnfeasible:
                    pass
            
            if len(ranked_cuts) < 1:
                break

            best = min(ranked_cuts, key=lambda x: x[0])
            best_cut = best[2]
            packed.add(best[1])
        
        LUT_graph.nodes[node]['pack'] = packed

    optimised = nx.DiGraph()
    to_be_mapped = [
        node for node, gtype in LUT_graph.nodes(data='gtype')
        if gtype == gate.PO
    ]

    while len(to_be_mapped) > 0:
        output = to_be_mapped.pop(0)

        output_func = LUT_graph.nodes[output]['func']
        pack = list(nx.topological_sort(LUT_graph.subgraph(
            node for node in LUT_graph.nodes[output]['pack']
            if LUT_graph.nodes[output]['gtype'] != gate.PI
        )))[:-1]

        for lut in reversed(pack):
            sym = sp.symbols(lut)
            lut_func = LUT_graph.nodes[lut]['func']
            output_func = output_func.xreplace({sym: lut_func})
        
        optimised.add_node(
            output,
            label=output,
            gtype=LUT_graph.nodes[output]['gtype'],
            func=output_func
        )

        for input in output_func.free_symbols:
            in_str = str(input)
            if LUT_graph.nodes[in_str]['gtype'] == gate.PI:
                if not optimised.has_node(in_str):
                    optimised.add_node(
                        in_str,
                        label=in_str,
                        gtype=gate.PI,
                        func=sp.symbols(in_str)
                    )
            else:
                to_be_mapped.append(in_str)
            optimised.add_edge(in_str, output)
    
    return optimised

