import sympy as sp
import networkx as nx

from itertools import chain
from stages.enums import gate


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

                for j in range(i + 1,len(LUT_parents)):
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

                            bound_vars = f'{int(cube[var_i])}{int(cube[var_j])}'
                            if bound_vars in connected_comps[0]:
                                entry[-1] = 1
                            
                            new_truthtable.append(entry)

                        LUT_graph.nodes[LUT_node]['func'] = sp.simplify_logic(
                            sp.POSform(new_vars, new_truthtable)
                        )
                        
                        child_func = sp.false
                        for bound_vars in connected_comps[0]:
                            if bound_vars[0] == '1':
                                a = LUT_graph.nodes[parent_i]['func']
                            else:
                                a = ~LUT_graph.nodes[parent_i]['func']

                            if bound_vars[1] == '1':
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
    pass
