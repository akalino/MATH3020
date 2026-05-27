import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter


def build_graph_from_edge_list(_edges):
    """Return a simple undirected graph from an edge list.

    :param _edges: edge list.
    :return: undirected graph.
    """
    g = nx.Graph()
    g.add_edges_from(_edges)
    return g


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


def degree_histogram_data(G):
    counts = Counter(dict(G.degree()).values())
    return dict(sorted(counts.items()))


def plot_degree_histogram(G):
    hist = degree_histogram_data(G)
    x = list(hist.keys())
    y = list(hist.values())

    plt.figure(figsize=(6, 4))
    plt.bar(x, y)
    plt.xlabel("Degree")
    plt.ylabel("Number of vertices")
    plt.title("Degree Histogram")
    plt.xticks(x)
    plt.show()


def export_for_gephi(G, path="lab03_graph.gexf"):
    nx.write_gexf(G, path)
    return path