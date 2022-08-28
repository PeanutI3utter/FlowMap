import networkx as nx

'''
    Get a subgraph containing all ancestor nodes and itself
    of the given node
'''
def extract_subgraph_from (graph: nx.DiGraph, node: str) -> nx.DiGraph:
    sub = list(nx.ancestors(graph, node))
    sub.append(node)
    return graph.subgraph(sub)

'''
    Create graph which is used to determine the label of the output of
    the given subgraph

    Input:
        graph: Original graph, from which a flow graph is to be created
    
    Output:
        flow graph of the original function, the drain node has a attribute
        "contains", which is a set of all nodes that is combined into the
        drain node.
'''
def flowGraph(graph: nx.DiGraph) -> nx.DiGraph:
    flowgraph = nx.DiGraph()
    nodes_sorted = list(nx.topological_sort(graph))

    input_nodes = [node for node, deg in graph.in_degree() if not deg]
    output = nodes_sorted[-1]

    highest_level = graph.nodes[nodes_sorted[-2]]['level']
    highest_level_nodes = [nodes_sorted[-2]]
    for node in nodes_sorted[-3::-1]:
        if graph.nodes[node]['level'] == highest_level:
            highest_level_nodes.append(node)
        else:
            break
    highest_level_nodes = set(highest_level_nodes)

    inter_nodes = nodes_sorted[len(input_nodes):-len(highest_level_nodes)-1]
    
    for node in input_nodes:
        flowgraph.add_edge('S', node + '_in')
        flowgraph.add_edge(node + '_in', node + '_out', capacity=1)
    
    for node in inter_nodes:
        incoming_edges = graph.in_edges(node)
        for edge in incoming_edges:
            flowgraph.add_edge(edge[0] + '_out', node + '_in')
        flowgraph.add_edge(node + '_in', node + '_out', capacity=1)
    
    for node in highest_level_nodes:
        incoming_edges = graph.in_edges(node)
        for edge in incoming_edges:
            if edge[0] not in highest_level_nodes:
                flowgraph.add_edge(edge[0] + '_out', f'DRAIN_{output}')

    for edge in graph.in_edges(output):
        if edge[0] not in highest_level_nodes:
            flowgraph.add_edge(edge[0] + '_out', f'DRAIN_{output}')

    nx.set_node_attributes(flowgraph, {f'DRAIN_{output}': {'contains': highest_level_nodes, 'mapped_to': output}})

    return flowgraph
        