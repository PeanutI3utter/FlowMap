import networkx as nx

from .data import TEST_SET_SUBGRAPH
from ..stages.label import extract_subgraph_from


def test_subgraph_0():
    (graph, node, expected_nodes, expected_edges) = TEST_SET_SUBGRAPH[0].values()
    subgraph = extract_subgraph_from(graph, node)
    expected_graph = nx.DiGraph()
    expected_graph.add_nodes_from(expected_nodes)
    expected_graph.add_edges_from(expected_edges)
    
    assert nx.utils.graphs_equal(subgraph, expected_graph)



def test_subgraph_1():
    (graph, node, expected_nodes, expected_edges) = TEST_SET_SUBGRAPH[1].values()
    subgraph = extract_subgraph_from(graph, node)
    expected_graph = nx.DiGraph()
    expected_graph.add_nodes_from(expected_nodes)
    expected_graph.add_edges_from(expected_edges)
    
    assert nx.utils.graphs_equal(subgraph, expected_graph)
