import networkx as nx

from ..stages.label import flowGraph

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


TEST_SET_FLOWGRAPH = [
    {
        'graph': G,
        'expected_nodes': [
            'S', 'a_in', 'a_out', 'b_in', 'b_out', 'c_in', 'c_out',
            'd_in', 'd_out', 'e_in', 'e_out', 'f_in', 'f_out',
            'g_in', 'g_out', 'h_in', 'h_out', 'i_in', 'i_out',
            ('T', {'contains': {'j', 'k', 'l'}, 'mapped_to': 'm'})
        ],
        'expected_edges': [
            ('a_in', 'a_out', {'capacity': 1}),
            ('b_in', 'b_out', {'capacity': 1}),
            ('c_in', 'c_out', {'capacity': 1}),
            ('d_in', 'd_out', {'capacity': 1}),
            ('e_in', 'e_out', {'capacity': 1}),
            ('f_in', 'f_out', {'capacity': 1}),
            ('g_in', 'g_out', {'capacity': 1}),
            ('h_in', 'h_out', {'capacity': 1}),
            ('i_in', 'i_out', {'capacity': 1}),
            ('S', 'a_in'),
            ('S', 'b_in'),
            ('S', 'c_in'),
            ('S', 'd_in'),
            ('S', 'e_in'),
            ('a_out', 'f_in'),
            ('b_out', 'f_in'),
            ('b_out', 'g_in'),
            ('c_out', 'g_in'),
            ('d_out', 'h_in'),
            ('e_out', 'h_in'),
            ('f_out', 'i_in'),
            ('g_out', 'i_in'),
            ('h_out', 'T'),
            ('i_out', 'T'),
            ('g_out', 'T'),
            ('f_out', 'T')
        ]
    },
]


def test_flowgraph():
    (graph, expected_nodes, expected_edges) = TEST_SET_FLOWGRAPH[0].values()
    flowgraph = flowGraph(graph)
    expected_graph = nx.DiGraph()
    expected_graph.add_nodes_from(expected_nodes)
    expected_graph.add_edges_from(expected_edges)

    assert nx.utils.graphs_equal(flowgraph, expected_graph)
