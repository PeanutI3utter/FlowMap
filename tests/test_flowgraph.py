import networkx as nx

from .data import TEST_SET_FLOWGRAPH
from ..stages.label import flowGraph


def test_flowgraph():
    (graph, expected_nodes, expected_edges) = TEST_SET_FLOWGRAPH[0].values()
    flowgraph = flowGraph(graph)
    expected_graph = nx.DiGraph()
    expected_graph.add_nodes_from(expected_nodes)
    expected_graph.add_edges_from(expected_edges)
    
    assert nx.utils.graphs_equal(flowgraph, expected_graph)