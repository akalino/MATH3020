import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd


def graph_summary(G):
    return {
        "number_of_nodes": G.number_of_nodes(),
        "number_of_edges": G.number_of_edges(),
        "nodes": list(G.nodes()),
        "edges": list(G.edges()),
        "degree_dict": dict(G.degree()),
    }


def digraph_summary(G):
    return {
        "number_of_nodes": G.number_of_nodes(),
        "number_of_edges": G.number_of_edges(),
        "nodes": list(G.nodes()),
        "edges": list(G.edges()),
        "in_degree_dict": dict(G.in_degree()),
        "out_degree_dict": dict(G.out_degree()),
        "is_strongly_connected": nx.is_strongly_connected(G),
        "is_weakly_connected": nx.is_weakly_connected(G),
    }


def weighted_graph_summary(G):
    return {
        "number_of_nodes": G.number_of_nodes(),
        "number_of_edges": G.number_of_edges(),
        "nodes": list(G.nodes()),
        "weighted_edges": list(G.edges(data=True)),
        "degree_dict": dict(G.degree()),
    }


def sample_undirected_graph():
    G = nx.Graph()
    G.add_edges_from([
        ("A", "B"),
        ("A", "C"),
        ("B", "D"),
        ("C", "D"),
        ("D", "E"),
    ])
    return G


def sample_directed_graph():
    G = nx.DiGraph()
    G.add_edges_from([
        ("A", "B"),
        ("A", "C"),
        ("B", "D"),
        ("C", "D"),
        ("D", "E"),
        ("E", "C"),
    ])
    return G


def sample_weighted_graph():
    G = nx.Graph()
    G.add_weighted_edges_from([
        ("A", "B", 4),
        ("A", "C", 1),
        ("B", "D", 2),
        ("C", "D", 5),
        ("C", "E", 8),
        ("D", "E", 1),
    ])
    return G


def build_weighted_graph(weighted_edges):
    G = nx.Graph()
    G.add_weighted_edges_from(weighted_edges)
    return G


def draw_graph(G, title="", seed=7):
    plt.figure(figsize=(6, 5))
    pos = nx.spring_layout(G, seed=seed)
    nx.draw(G, pos, with_labels=True, node_size=900)
    plt.title(title)
    plt.show()


def draw_digraph(G, title="", seed=7):
    plt.figure(figsize=(6, 5))
    pos = nx.spring_layout(G, seed=seed)
    nx.draw(G, pos, with_labels=True, node_size=900, arrows=True)
    plt.title(title)
    plt.show()


def draw_weighted_graph(G, title="", seed=7):
    plt.figure(figsize=(6, 5))
    pos = nx.spring_layout(G, seed=seed)
    nx.draw(G, pos, with_labels=True, node_size=900)
    labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.title(title)
    plt.show()


def adjacency_matrix_table(G, weight=None):
    nodes = list(G.nodes())
    A = nx.to_pandas_adjacency(G, nodelist=nodes, weight=weight)
    return A


def in_out_degree_table(G):
    return pd.DataFrame({
        "in_degree": dict(G.in_degree()),
        "out_degree": dict(G.out_degree()),
    })


def weighted_edge_table(G):
    rows = []
    for u, v, data in G.edges(data=True):
        rows.append((u, v, data.get("weight", None)))
    return pd.DataFrame(rows, columns=["u", "v", "weight"])


def directed_path_between(G, u, v):
    if nx.has_path(G, u, v):
        return nx.shortest_path(G, u, v)
    return None


def connectivity_report_digraph(G):
    return {
        "is_strongly_connected": nx.is_strongly_connected(G),
        "is_weakly_connected": nx.is_weakly_connected(G),
        "strongly_connected_components": [sorted(c) for c in nx.strongly_connected_components(G)],
        "weakly_connected_components": [sorted(c) for c in nx.weakly_connected_components(G)],
    }


def shortest_path_unweighted(G, u, v):
    return nx.shortest_path(G, u, v)


def shortest_path_weighted(G, u, v):
    return nx.shortest_path(G, u, v, weight="weight")


def weighted_path_length(G, path):
    total = 0
    for i in range(len(path) - 1):
        total += G[path[i]][path[i + 1]]["weight"]
    return total


def export_for_gephi(G, path):
    nx.write_gexf(G, path)
    return path