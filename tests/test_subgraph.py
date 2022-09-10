import networkx as nx

from ..stages.label import extract_subgraph_from

G = nx.DiGraph()
G.add_nodes_from([
    ('a', {'level': 0}),
    ('b', {'level': 0}),
    ('c', {'level': 0}),
    ('d', {'level': 0}),
    ('e', {'level': 0}),
    ('f', {'level': 1}),
    ('g', {'level': 1}),
    ('h', {'level': 1}),
    ('i', {'level': 1}),
    ('j', {'level': 2}),
    ('k', {'level': 2}),
    ('l', {'level': 2}),
    'm'
])
G.add_edges_from([
    ('a', 'f'), ('b', 'f'), ('b', 'g'),
    ('c', 'g'), ('d', 'h'), ('e', 'h'),
    ('f', 'i'), ('g', 'i'), ('h', 'j'),
    ('i', 'j'), ('j', 'k'), ('g', 'k'),
    ('k', 'l'), ('h', 'l'), ('f', 'm'),
    ('l', 'm')
])


TEST_SET_SUBGRAPH = [
    {
        'graph': G,
        'node': 'i',
        'expected_nodes': [
            ('a', {'level': 0}),
            ('b', {'level': 0}),
            ('c', {'level': 0}),
            ('f', {'level': 1}),
            ('g', {'level': 1}),
            ('i', {'level': 1}),
        ],
        'expected_edges': [
            ('a', 'f'), ('b', 'f'), ('b', 'g'),
            ('c', 'g'), ('f', 'i'), ('g', 'i')
        ]
    },
    {
        'graph': G,
        'node': 'k',
        'expected_nodes': [
            ('a', {'level': 0}),
            ('b', {'level': 0}),
            ('c', {'level': 0}),
            ('d', {'level': 0}),
            ('e', {'level': 0}),
            ('f', {'level': 1}),
            ('g', {'level': 1}),
            ('h', {'level': 1}),
            ('i', {'level': 1}),
            ('j', {'level': 2}),
            ('k', {'level': 2}),
        ],
        'expected_edges': [
            ('a', 'f'), ('b', 'f'), ('b', 'g'),
            ('c', 'g'), ('d', 'h'), ('e', 'h'),
            ('f', 'i'), ('g', 'i'), ('h', 'j'),
            ('i', 'j'), ('j', 'k'), ('g', 'k')
        ]
    }
]


def test_subgraph_0():
    (graph, node, expected_nodes, expected_edges) = \
        TEST_SET_SUBGRAPH[0].values()
    subgraph = extract_subgraph_from(graph, node)
    expected_graph = nx.DiGraph()
    expected_graph.add_nodes_from(expected_nodes)
    expected_graph.add_edges_from(expected_edges)

    assert nx.utils.graphs_equal(subgraph, expected_graph)


def test_subgraph_1():
    (graph, node, expected_nodes, expected_edges) = \
        TEST_SET_SUBGRAPH[1].values()
    subgraph = extract_subgraph_from(graph, node)
    expected_graph = nx.DiGraph()
    expected_graph.add_nodes_from(expected_nodes)
    expected_graph.add_edges_from(expected_edges)

    assert nx.utils.graphs_equal(subgraph, expected_graph)
