import networkx as nx


def extract_subgraph_from (graph: nx.DiGraph, node: str) -> nx.DiGraph:
    sub = list(nx.ancestors(graph, node))
    sub.append(node)
    return graph.subgraph(sub)

