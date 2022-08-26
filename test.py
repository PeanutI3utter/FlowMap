import matplotlib.pyplot as plt
import networkx as nx

from draw import draw_digraph
from label import extract_subgraph_from, flowGraph


class tcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


G = nx.DiGraph()
G.add_edges_from([
    ('a', 'f'),
    ('b', 'f'), ('b', 'g'), ('c', 'g'),
    ('d', 'h'), ('e', 'h'), ('f', 'i'),
    ('g', 'i'), ('h', 'j'), ('i', 'j'),
    ('j', 'k'), ('g', 'k'), ('k', 'l'),
    ('h', 'l'), ('f', 'T'), ('l', 'T')
])


TEST_SET_SUBGRAPH = [
    {
        'graph': G,
        'node': 'i',
        'expected_nodes': {
            'a', 'b', 'c', 'f', 'g', 'i'
        },
        'expected_edges':{
            ('a', 'f'), ('b', 'f'), ('b', 'g'),
            ('c', 'g'), ('f', 'i'), ('g', 'i')
        }
    },
    {
        'graph': G,
        'node': 'k',
        'expected_nodes': {
            'a', 'b', 'c', 'd', 'e', 'f',
            'g', 'h', 'i', 'j', 'k'
        },
        'expected_edges':{
            ('a', 'f'), ('b', 'f'), ('b', 'g'),
            ('c', 'g'), ('d', 'h'), ('e', 'h'),
            ('f', 'i'), ('g', 'i'), ('h', 'j'),
            ('i', 'j'), ('j', 'k'), ('g', 'k')
        }
    }
]



def test_subgraph(test_set: dict):
    print("Starting subgraph test..")
    for i, test_data in enumerate(test_set):
        (graph, node, expected_nodes, expected_edges) = test_data.values()
        subgraph = extract_subgraph_from(graph, node)
        expected_graph = nx.DiGraph()
        expected_graph.add_nodes_from(expected_nodes)
        expected_graph.add_edges_from(expected_edges)

        if (nx.utils.graphs_equal(subgraph, expected_graph)):
            print(f"[SUBGRAPH TEST {i + 1}/{len(test_set)}] " + tcolors.OKGREEN + "passed" + tcolors.ENDC)
        else:
            print(f"[SUBGRAPH TEST {i + 1}/{len(test_set)}] " + tcolors.WARNING + "failed" + tcolors.ENDC)



test_subgraph(TEST_SET_SUBGRAPH)
