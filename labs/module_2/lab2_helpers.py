from collections import defaultdict, Counter
import random
import time

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd


def build_graph_from_edge_list(_edges):
    g = nx.Graph()
    g.add_edges_from(_edges)
    return g


def adjacency_dict(_edges):
    adj = defaultdict(set)
    for u, v in _edges:
        adj[u].add(v)
        adj[v].add(u)
    return {k: sorted(v, key=str) for k, v in adj.items()}


def basic_summary(_g):
    return {
        "num_vertices": _g.number_of_nodes(),
        "num_edges": _g.number_of_edges(),
        "vertices": sorted(_g.nodes(), key=str),
        "edges": sorted(tuple(sorted(e, key=str)) for e in _g.edges()),
    }


def graph_summary(_g):
    return {
        "nodes": list(_g.nodes()),
        "edges": list(_g.edges()),
        "number_of_nodes": _g.number_of_nodes(),
        "number_of_edges": _g.number_of_edges(),
        "connected": nx.is_connected(_g),
        "number_of_components": nx.number_connected_components(_g),
        "components": [sorted(c, key=str) for c in nx.connected_components(_g)],
        "bipartite": nx.is_bipartite(_g)
    }


def degree_table(_g):
    return sorted(_g.degree(), key=lambda x: (-x[1], str(x[0])))


def degree_histogram_data(_g):
    counts = Counter(dict(_g.degree()).values())
    return dict(sorted(counts.items()))


def plot_degree_histogram(_g, title="Degree Histogram"):
    hist = degree_histogram_data(_g)
    x = list(hist.keys())
    y = list(hist.values())

    plt.figure(figsize=(6, 4))
    plt.bar(x, y)
    plt.xlabel("Degree")
    plt.ylabel("Number of vertices")
    plt.title(title)
    plt.xticks(x)
    plt.show()


def draw_graph(_g, _labels=True, _seed=7, _title=""):
    plt.figure(figsize=(7, 6))
    pos = nx.spring_layout(_g, seed=_seed)
    nx.draw(_g, pos, with_labels=_labels, node_size=1200)
    plt.title(_title)
    plt.show()


def export_for_gephi(_g, _path="lab_module2_graph.gexf"):
    nx.write_gexf(_g, _path)
    return _path


def path_between(_g, source, target):
    if nx.has_path(_g, source, target):
        return nx.shortest_path(_g, source=source, target=target)
    return None


def cycle_basis(_g):
    return nx.cycle_basis(_g)


def induced_subgraph(_g, nodes):
    return _g.subgraph(nodes).copy()


def degree_sequence(_g, _descending=True):
    degrees = [deg for _, deg in _g.degree()]
    return sorted(degrees, reverse=_descending)


def isomorphic(_g1, _g2):
    return nx.is_isomorphic(_g1, _g2)


def isomorphism_mapping(_g1, _g2):
    matcher = nx.algorithms.isomorphism.GraphMatcher(_g1, _g2)
    if matcher.is_isomorphic():
        return matcher.mapping
    return None


def relabel_randomly(_g, seed=0):
    rng = random.Random(seed)
    old_nodes = list(_g.nodes())
    new_nodes = old_nodes[:]
    rng.shuffle(new_nodes)
    mapping = dict(zip(old_nodes, new_nodes))
    return nx.relabel_nodes(_g, mapping, copy=True)


def generate_random_graph(n, m, seed=None):
    max_edges = n * (n - 1) // 2
    if m < 0 or m > max_edges:
        raise ValueError(f"For a simple undirected graph on {n} nodes, m must be between 0 and {max_edges}.")
    return nx.gnm_random_graph(n, m, seed=seed)


def time_isomorphism_check(_g1, _g2):
    start = time.perf_counter()
    result = nx.is_isomorphic(_g1, _g2)
    elapsed = time.perf_counter() - start
    return {"isomorphic": result, "time_seconds": elapsed}


def plot_isomorphism_timings(vertex_sizes, edge_sizes, run_times):
    if not (len(vertex_sizes) == len(edge_sizes) == len(run_times)):
        raise ValueError("All input lists must have the same length.")

    plt.figure(figsize=(7, 5))
    plt.plot(vertex_sizes, run_times, marker="o")
    plt.xlabel("Number of vertices")
    plt.ylabel("Run time (seconds)")
    plt.title("Vertices vs Isomorphism Run Time")
    plt.grid(True)
    plt.show()

    plt.figure(figsize=(7, 5))
    plt.plot(edge_sizes, run_times, marker="o")
    plt.xlabel("Number of edges")
    plt.ylabel("Run time (seconds)")
    plt.title("Edges vs Isomorphism Run Time")
    plt.grid(True)
    plt.show()
