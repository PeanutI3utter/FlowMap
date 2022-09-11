import networkx as nx

from networkx.algorithms.flow import shortest_augmenting_path


def extract_subgraph_from(graph: nx.DiGraph, node: str) -> nx.DiGraph:
    """
    Get a subgraph containing all ancestor nodes and itself
    of the given node
    """
    sub = list(nx.ancestors(graph, node))
    sub.append(node)
    return graph.subgraph(sub)


def flowGraph(graph: nx.DiGraph) -> nx.DiGraph:
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

    # nodes with highest label are packed into T with output node
    highest_level = graph.nodes[nodes_sorted[-2]]['level']
    highest_level_nodes = [nodes_sorted[-2]]
    for node in nodes_sorted[-3::-1]:
        if graph.nodes[node]['level'] == highest_level:
            highest_level_nodes.append(node)
        else:
            break
    highest_level_nodes = set(highest_level_nodes)

    # nodes which are not input nodes nor nodes with highest label
    inter_nodes = nodes_sorted[len(input_nodes):-len(highest_level_nodes)-1]

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

    # edges going to nodes packed into T (except output)
    for node in highest_level_nodes:
        incoming_edges = graph.in_edges(node)
        for edge in incoming_edges:
            # edges going from T to T are ignored
            if edge[0] not in highest_level_nodes:
                flowgraph.add_edge(edge[0] + '_out', 'T')

    # edges going to output node
    for edge in graph.in_edges(output):
        if edge[0] not in highest_level_nodes:
            flowgraph.add_edge(edge[0] + '_out', 'T')

    nx.set_node_attributes(
        flowgraph,
        {'T': {'contains': highest_level_nodes, 'mapped_to': output}}
    )

    return flowgraph


def label(graph: nx.DiGraph, k: int) -> nx.DiGraph:
    """
    Label phase of the FlowMap Algorithm

    Output:
        A shallow copy of the given graph, with labeled nodes.
        Nodes are extended with two attributes:
            level: label of the node
            cut: set of nodes which are combined to a k-lut
                in an k-feasible optimal height cut
    """
    labeled_graph = graph.copy()
    input_nodes = {
        node for node, deg in labeled_graph.in_degree()
        if not deg
    }

    nodes_to_be_labeled = [
        node for node in nx.topological_sort(graph)
        if node not in input_nodes
    ]

    # Input nodes labeled with 0 and no cut is saved
    for node in input_nodes:
        nx.set_node_attributes(
            labeled_graph, {node: {'level': 0, 'cut': set()}}
        )

    for node in nodes_to_be_labeled:
        parents = labeled_graph.predecessors(node)

        # nodes who are only connected to inputs are labeled with 1
        # (They have a label of 1 as inputs cannot be packed into LUTs)
        if all(parent in input_nodes for parent in parents):
            nx.set_node_attributes(
                labeled_graph, {node: {'level': 1, 'cut': {node}}}
            )
            continue

        subgraph = extract_subgraph_from(labeled_graph, node)
        flowgraph = flowGraph(subgraph)
        res_graph = shortest_augmenting_path(flowgraph, 'S', 'T')
        highest_label = max(
            nx.get_node_attributes(subgraph, 'level').values()
        )

        # if k-feasible cut exists, then pack gates into cut which are
        # not reachable from the source in the residual graph
        # set label to same as highest predecessor label
        if res_graph.graph['flow_value'] <= k:

            res_graph.remove_edges_from([
                (edge_i, edge_o) for edge_i, edge_o, val in res_graph.edges(data=True)
                if val['flow'] >= val['capacity']
            ])
            
            outside_nodes = list(
                node[:-3] for node in nx.dfs_preorder_nodes(res_graph, 'S')
                if node.endswith('_in')
            )

            cut = {
                n for n in subgraph.nodes
                if n not in input_nodes and n not in outside_nodes
            }
            nx.set_node_attributes(
                labeled_graph, {node: {'level': highest_label, 'cut': cut}}
            )

        # Otherwise set label to highest predecessor label + 1
        # Put node into cut
        else:

            nx.set_node_attributes(
                labeled_graph,
                {node: {'level': highest_label + 1, 'cut': {node}}}
            )

    return labeled_graph
