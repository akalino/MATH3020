"""
Helper functions for the initial lab.
"""
from collections import defaultdict, Counter

import matplotlib.pyplot as plt
import networkx as nx


def build_graph_from_edge_list(_edges):
    """Return a simple undirected graph from an edge list.

    :param _edges: edge list.
    :return: undirected graph.
    """
    g = nx.Graph()
    g.add_edges_from(_edges)
    return g


def adjacency_dict(_edges):
    """Return an adjacency dictionary built from an undirected edge list.

    :param _edges: undirected edge list.
    :return: adjacency dictionary.
    """
    adj = defaultdict(set)
    for u, v in _edges:
        adj[u].add(v)
        adj[v].add(u)
    return {k: sorted(v) for k, v in adj.items()}


def basic_summary(_g):
    """Return a tiny dictionary of summary values for the graph.

    :param _g: undirected graph.
    :return: summary dictionary.
    """
    return {
        "num_vertices": _g.number_of_nodes(),
        "num_edges": _g.number_of_edges(),
        "vertices": sorted(_g.nodes()),
        "edges": sorted(tuple(sorted(e)) for e in _g.edges()),
    }


def graph_summary(_g):
    """
    Extended summary of graph metrics.

    :param _g: graph object.
    :return dict of metrics.
    """
    return {
        "nodes": list(_g.nodes()),
        "edges": list(_g.edges()),
        "number_of_nodes": _g.number_of_nodes(),
        "number_of_edges": _g.number_of_edges(),
        "connected": nx.is_connected(_g),
        "number_of_components": nx.number_connected_components(_g),
        "components": [sorted(c) for c in nx.connected_components(_g)],
        "bipartite": nx.is_bipartite(_g)
    }


def degree_table(_g):
    """Return a sorted list of (node, degree) pairs.
    
    :param _g: graph object.
    :return tuple of vertex and degree.
    """
    return sorted(_g.degree(), key=lambda x: (-x[1], str(x[0])))


def degree_histogram(_g):
    """Return degree counts as a dictionary.
    
    :param _g: graph object.
    :return dictionary of degree counts.
    """
    counts = Counter(dict(_g.degree()).values())
    return dict(sorted(counts.items()))


def draw_graph(_g, _labels=True, _seed=7):
    """Draw a simple graph using a spring layout.
    
    :param _g: graph object.
    :param _labels: boolean for printing labels.
    :param _seed: random seed for spring layout.
    """
    pos = nx.spring_layout(_g, seed=_seed)
    nx.draw(_g, pos, with_labels=_labels, node_size=1200)
    plt.show()


def export_for_gephi(_g, _path="lab01_graph.gexf"):
    """Export the graph to GEXF so it can be opened in Gephi.
    
    :param _g: graph object.
    :param _path: path to write Gephi file.
    """
    nx.write_gexf(_g, _path)
    print(f"Wrote file to {_path}")


def questions_for_students():
    """Return a few starter prompts for the lab."""
    return [
        "How many vertices and edges does your graph have?",
        "Which vertex has the highest degree?",
        "Is the graph connected?",
        "What changes if you add one new edge?",
        "Export the graph to Gephi and compare the visualization to the NetworkX drawing.",
    ]