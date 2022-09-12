import networkx as nx

from stages.label import label

G = nx.DiGraph()
G.add_nodes_from([
    'a', 'b', 'c',
    'd', 'e', 'f',
    'g', 'h', 'i',
    'j', 'k', 'l',
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


expected = nx.DiGraph()
expected.add_nodes_from([
    ('a', {'level': 0, 'cut': set()}),
    ('b', {'level': 0, 'cut': set()}),
    ('c', {'level': 0, 'cut': set()}),
    ('d', {'level': 0, 'cut': set()}),
    ('e', {'level': 0, 'cut': set()}),
    ('f', {'level': 1, 'cut': {'f'}}),
    ('g', {'level': 1, 'cut': {'g'}}),
    ('h', {'level': 1, 'cut': {'h'}}),
    ('i', {'level': 1, 'cut': {'f', 'g', 'i'}}),
    ('j', {'level': 2, 'cut': {'j'}}),
    ('k', {'level': 2, 'cut': {'i', 'j', 'k'}}),
    ('l', {'level': 2, 'cut': {'i', 'j', 'k', 'l'}}),
    ('m', {'level': 2, 'cut': {'i', 'j', 'k', 'l', 'm'}})
])
expected.add_edges_from([
    ('a', 'f'), ('b', 'f'), ('b', 'g'),
    ('c', 'g'), ('d', 'h'), ('e', 'h'),
    ('f', 'i'), ('g', 'i'), ('h', 'j'),
    ('i', 'j'), ('j', 'k'), ('g', 'k'),
    ('k', 'l'), ('h', 'l'), ('f', 'm'),
    ('l', 'm')
])


def test_labeling():
    assert nx.utils.graphs_equal(label(G, 3), expected)
