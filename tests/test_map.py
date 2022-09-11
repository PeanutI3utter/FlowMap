import sympy as sp
import networkx as nx

from stages.bng import blif_to_bng, gate
from stages.label import label
from stages.mapping import flowmap


expected0 = nx.DiGraph()


expected0.add_nodes_from([
    ('F', {
        'label': 'F',
        'func': sp.symbols('OR[1]')
                 | sp.symbols('AND[10]')
                 | sp.symbols('OR[0]'),
        'gtype': gate.PO
    }),
    ('AND[10]', {
        'label': 'AND[10]',
        'func': sp.symbols('AND[8]') & sp.symbols('AND[9]'),
        'gtype': gate.LUT
    }),
    ('OR[0]', {
        'label': 'OR[0]',
        'func': (sp.symbols('AND[0]') & sp.symbols('AND[1]')) |
                (sp.symbols('AND[0]') & sp.symbols('AND[3]')),
        'gtype': gate.LUT
    }),
    ('OR[1]', {
        'label': 'OR[1]',
        'func': (sp.symbols('AND[5]') & sp.symbols('AND[1]')) |
                (sp.symbols('AND[5]') & sp.symbols('AND[3]')),
        'gtype': gate.LUT
    }),
    ('AND[8]', {
        'label': 'AND[8]',
        'func': ~sp.symbols('a') & sp.symbols('b'),
        'gtype': gate.LUT
    }),
    ('AND[9]', {
        'label': 'AND[9]',
        'func': sp.symbols('c') & ~sp.symbols('d'),
        'gtype': gate.LUT
    }),
    ('AND[0]', {
        'label': 'AND[0]',
        'func': sp.symbols('a') & ~sp.symbols('b'),
        'gtype': gate.LUT
    }),
    ('AND[1]', {
        'label': 'AND[1]',
        'func': ~sp.symbols('c') & ~sp.symbols('d'),
        'gtype': gate.LUT
    }),
    ('AND[3]', {
        'label': 'AND[3]',
        'func': sp.symbols('c') & sp.symbols('d'),
        'gtype': gate.LUT
    }),
    ('AND[5]', {
        'label': 'AND[5]',
        'func': sp.symbols('a') & sp.symbols('b'),
        'gtype': gate.LUT
    }),
    ('AND[5]', {
        'label': 'AND[5]',
        'func': sp.symbols('a') & sp.symbols('b'),
        'gtype': gate.LUT
    }),
    ('a', {
        'label': 'a',
        'func': sp.symbols('a'),
        'gtype': gate.PI
    }),
    ('b', {
        'label': 'b',
        'func': sp.symbols('b'),
        'gtype': gate.PI
    }),
    ('c', {
        'label': 'c',
        'func': sp.symbols('c'),
        'gtype': gate.PI
    }),
    ('d', {
        'label': 'd',
        'func': sp.symbols('d'),
        'gtype': gate.PI
    })
])


expected0.add_edges_from([
    ('OR[1]', 'F'), ('AND[10]', 'F'), ('OR[0]', 'F'),
    ('AND[8]', 'AND[10]'), ('AND[9]', 'AND[10]'),
    ('AND[0]', 'OR[0]'), ('AND[1]', 'OR[0]'), ('AND[3]', 'OR[0]'),
    ('AND[1]', 'OR[1]'), ('AND[3]', 'OR[1]'), ('AND[5]', 'OR[1]'),
    ('a', 'AND[8]'), ('b', 'AND[8]'),
    ('c', 'AND[9]'), ('d', 'AND[9]'),
    ('a', 'AND[0]'), ('b', 'AND[0]'),
    ('c', 'AND[1]'), ('d', 'AND[1]'),
    ('c', 'AND[3]'), ('d', 'AND[3]'),
    ('a', 'AND[5]'), ('b', 'AND[5]'),
])


def test_map0():
    res = flowmap(label(blif_to_bng("tests/input_test.blif"), 3))
    for node in res.nodes:
        assert node in expected0.nodes
        assert res.nodes[node]['label'] == expected0.nodes[node]['label']
        assert res.nodes[node]['gtype'] == expected0.nodes[node]['gtype']
        assert res.nodes[node]['func'].equals(expected0.nodes[node]['func'])

    for edge in res.edges:
        assert edge in expected0.edges

    for edge in expected0.edges:
        assert edge in res.edges


expected1 = nx.DiGraph()


expected1.add_nodes_from([
    ('F', {
        'label': 'F',
        'func': sp.symbols('OR[1]')
                 | sp.symbols('AND[10]')
                 | sp.symbols('OR[0]'),
        'gtype': gate.PO
    }),
    ('G', {
        'label': 'G',
        'func': sp.symbols('OR[4]') | sp.symbols('OR[5]'),
        'gtype': gate.PO
    }),
    ('AND[10]', {
        'label': 'AND[10]',
        'func': sp.symbols('AND[8]') & sp.symbols('AND[9]'),
        'gtype': gate.LUT
    }),
    ('OR[0]', {
        'label': 'OR[0]',
        'func': (sp.symbols('AND[0]') & sp.symbols('AND[1]')) |
                (sp.symbols('AND[0]') & sp.symbols('AND[3]')),
        'gtype': gate.LUT
    }),
    ('OR[1]', {
        'label': 'OR[1]',
        'func': (sp.symbols('AND[5]') & sp.symbols('AND[1]')) |
                (sp.symbols('AND[5]') & sp.symbols('AND[3]')),
        'gtype': gate.LUT
    }),
    ('OR[4]', {
        'label': 'OR[4]',
        'func': (sp.symbols('AND[0]') & sp.symbols('AND[3]')) |
                (sp.symbols('AND[0]') & sp.symbols('AND[11]')),
        'gtype': gate.LUT
    }),
    ('OR[5]', {
        'label': 'OR[5]',
        'func': (sp.symbols('AND[5]') & sp.symbols('AND[11]')) |
                (sp.symbols('AND[8]') & sp.symbols('AND[11]')),
        'gtype': gate.LUT
    }),
    ('AND[0]', {
        'label': 'AND[0]',
        'func': sp.symbols('a') & ~sp.symbols('b'),
        'gtype': gate.LUT
    }),
    ('AND[1]', {
        'label': 'AND[1]',
        'func': ~sp.symbols('c') & ~sp.symbols('d'),
        'gtype': gate.LUT
    }),
    ('AND[3]', {
        'label': 'AND[3]',
        'func': sp.symbols('c') & sp.symbols('d'),
        'gtype': gate.LUT
    }),
    ('AND[5]', {
        'label': 'AND[5]',
        'func': sp.symbols('a') & sp.symbols('b'),
        'gtype': gate.LUT
    }),
    ('AND[8]', {
        'label': 'AND[8]',
        'func': ~sp.symbols('a') & sp.symbols('b'),
        'gtype': gate.LUT
    }),
    ('AND[9]', {
        'label': 'AND[9]',
        'func': sp.symbols('c') & ~sp.symbols('d'),
        'gtype': gate.LUT
    }),
    ('AND[11]', {
        'label': 'AND[11]',
        'func': ~sp.symbols('c') & sp.symbols('d'),
        'gtype': gate.LUT
    }),
    ('a', {
        'label': 'a',
        'func': sp.symbols('a'),
        'gtype': gate.PI
    }),
    ('b', {
        'label': 'b',
        'func': sp.symbols('b'),
        'gtype': gate.PI
    }),
    ('c', {
        'label': 'c',
        'func': sp.symbols('c'),
        'gtype': gate.PI
    }),
    ('d', {
        'label': 'd',
        'func': sp.symbols('d'),
        'gtype': gate.PI
    })
])


expected1.add_edges_from([
    ('OR[1]', 'F'),
    ('AND[10]', 'F'),
    ('OR[0]', 'F'),
    ('OR[4]', 'G'),
    ('OR[5]', 'G'),
    ('AND[8]', 'AND[10]'),
    ('AND[9]', 'AND[10]'),
    ('AND[0]', 'OR[0]'),
    ('AND[1]', 'OR[0]'),
    ('AND[3]', 'OR[0]'),
    ('AND[1]', 'OR[1]'),
    ('AND[3]', 'OR[1]'),
    ('AND[5]', 'OR[1]'),
    ('AND[0]', 'OR[4]'),
    ('AND[3]', 'OR[4]'),
    ('AND[11]', 'OR[4]'),
    ('AND[5]', 'OR[5]'),
    ('AND[8]', 'OR[5]'),
    ('AND[11]', 'OR[5]'),
    ('a', 'AND[8]'),
    ('b', 'AND[8]'),
    ('c', 'AND[9]'),
    ('d', 'AND[9]'),
    ('c', 'AND[11]'),
    ('d', 'AND[11]'),
    ('a', 'AND[0]'),
    ('b', 'AND[0]'),
    ('c', 'AND[1]'),
    ('d', 'AND[1]'),
    ('c', 'AND[3]'),
    ('d', 'AND[3]'),
    ('a', 'AND[5]'),
    ('b', 'AND[5]'),
])


def test_map1():
    res = flowmap(label(blif_to_bng("tests/input_test_multi_output.blif"), 3))
    for node in res.nodes:
        print(node)
        assert node in expected1.nodes
        assert res.nodes[node]['label'] == expected1.nodes[node]['label']
        assert res.nodes[node]['gtype'] == expected1.nodes[node]['gtype']
        assert res.nodes[node]['func'].equals(expected1.nodes[node]['func'])

    for edge in res.edges:
        assert edge in expected1.edges

    for edge in expected1.edges:
        assert edge in res.edges
