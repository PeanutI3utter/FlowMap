import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout


def draw_digraph(graph: nx.DiGraph):
    pos = graphviz_layout(graph, prog='dot')
    nx.draw(graph, node_color='white', pos=pos, with_labels=True)
