import math
import networkx as nx
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from pathlib import Path


def mark_k33_core(G: nx.Graph, left: Iterable[int] = range(3), right: Iterable[int] = range(3, 6)) -> nx.Graph:
    H = G.copy()
    left = set(left)
    right = set(right)
    core = left | right
    for v in core:
        H.nodes[v]["core"] = True
        H.nodes[v]["core_type"] = "K33_left" if v in left else "K33_right"
    for u, v in H.edges():
        if (u in left and v in right) or (u in right and v in left):
            H.edges[u, v]["core_edge"] = True
            H.edges[u, v]["core_type"] = "K33"
    return H


def mark_k5_core(G: nx.Graph, core_nodes: Iterable[int] = range(5)) -> nx.Graph:
    H = G.copy()
    core = set(core_nodes)
    for v in core:
        H.nodes[v]["core"] = True
        H.nodes[v]["core_type"] = "K5"
    for u, v in H.edges():
        if u in core and v in core:
            H.edges[u, v]["core_edge"] = True
            H.edges[u, v]["core_type"] = "K5"
    return H

def k5_with_dangling_trees(num_leaves_per_vertex: int = 3) -> nx.Graph:
    G = nx.complete_graph(5)
    G = mark_k5_core(G)
    next_node = 5

    for v in range(5):
        previous = v
        for _ in range(num_leaves_per_vertex):
            G.add_node(next_node, noise=True, core=False)
            G.add_edge(previous, next_node, noise_edge=True, core_edge=False)
            previous = next_node
            next_node += 1

    return G


def k33_with_dangling_trees(num_leaves_per_vertex: int = 3) -> nx.Graph:
    G = nx.complete_bipartite_graph(3, 3)
    G = mark_k33_core(G)
    next_node = 6

    for v in range(6):
        previous = v
        for _ in range(num_leaves_per_vertex):
            G.add_node(next_node, noise=True, core=False)
            G.add_edge(previous, next_node, noise_edge=True, core_edge=False)
            previous = next_node
            next_node += 1

    return G


def assign_metric_positions(G, layout="spring", seed=0, scale=10.0):
    """
    Assign 2D positions to nodes and store them as x/y attributes.

    Parameters
    ----------
    G : networkx.Graph
    layout : str
        One of: "spring", "kamada_kawai", "circular".
    seed : int
        Random seed for reproducible layouts.
    scale : float
        Layout scale.

    Returns
    -------
    pos : dict
        Dictionary mapping nodes to (x, y).
    """
    if layout == "spring":
        pos = nx.spring_layout(G, seed=seed, scale=scale)
    elif layout == "kamada_kawai":
        pos = nx.kamada_kawai_layout(G, scale=scale)
    elif layout == "circular":
        pos = nx.circular_layout(G, scale=scale)
    else:
        raise ValueError(f"Unknown layout: {layout}")

    for v, xy in pos.items():
        x, y = float(xy[0]), float(xy[1])
        G.nodes[v]["x"] = x
        G.nodes[v]["y"] = y

    return pos


def euclidean_distance(pos, u, v):
    """
    Euclidean distance between nodes u and v using a position dictionary.
    """
    x1, y1 = pos[u]
    x2, y2 = pos[v]
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def add_edge_lengths(G, pos, attr_name="length"):
    """
    Store Euclidean edge lengths as an edge attribute.
    """
    for u, v in G.edges:
        G.edges[u, v][attr_name] = euclidean_distance(pos, u, v)

    return G


def distance_threshold_graph(nodes, pos, r):
    """
    Build a graph on the given nodes by connecting pairs whose
    Euclidean distance is at most r.

    This is the 1-skeleton of a Vietoris-Rips-style complex.
    """
    H = nx.Graph()
    H.add_nodes_from(nodes)

    for v in nodes:
        x, y = pos[v]
        H.nodes[v]["x"] = float(x)
        H.nodes[v]["y"] = float(y)

    node_list = list(nodes)

    for i, u in enumerate(node_list):
        for v in node_list[i + 1:]:
            d = euclidean_distance(pos, u, v)
            if d <= r:
                H.add_edge(u, v, length=d, threshold=r)

    return H


def add_neighborhood_counts(G, pos, radii):
    """
    For each radius r, add a node attribute counting how many other
    points lie within distance r.
    """
    nodes = list(G.nodes)

    for r in radii:
        attr = {}

        for u in nodes:
            count = 0
            for v in nodes:
                if u == v:
                    continue
                if euclidean_distance(pos, u, v) <= r:
                    count += 1

            attr[u] = count

        nx.set_node_attributes(G, attr, f"neighbors_within_{r}")

    return G


def rips_triangles_from_positions(nodes, pos, r):
    """
    Return all triangles whose three pairwise distances are <= r.

    These are the 2-simplices of the Vietoris-Rips complex at scale r.
    """
    triangles = []
    node_list = list(nodes)

    for i, a in enumerate(node_list):
        for j in range(i + 1, len(node_list)):
            b = node_list[j]
            for k in range(j + 1, len(node_list)):
                c = node_list[k]

                if (
                    euclidean_distance(pos, a, b) <= r
                    and euclidean_distance(pos, a, c) <= r
                    and euclidean_distance(pos, b, c) <= r
                ):
                    triangles.append(tuple(sorted((a, b, c))))

    return triangles


def rips_complex_summary(nodes, pos, r):
    """
    Compute simple information about the Rips complex up to dimension 2.
    """
    G_r = distance_threshold_graph(nodes, pos, r)
    triangles = rips_triangles_from_positions(nodes, pos, r)

    V = G_r.number_of_nodes()
    E = G_r.number_of_edges()
    T = len(triangles)
    c = nx.number_connected_components(G_r)

    graph_beta1 = E - V + c

    return {
        "r": r,
        "vertices": V,
        "edges": E,
        "triangles": T,
        "components": c,
        "graph_beta1_before_filling_triangles": graph_beta1,
    }


def export_for_gephi(G: nx.Graph, filename: str | Path) -> None:
    """GEXF-safe export: remove tuple/list/dict/set attribute values."""
    H = G.copy()

    for _, data in H.nodes(data=True):
        bad_keys = [k for k, val in data.items() if isinstance(val, (tuple, list, dict, set))]
        for k in bad_keys:
            del data[k]

    for _, _, data in H.edges(data=True):
        bad_keys = [k for k, val in data.items() if isinstance(val, (tuple, list, dict, set))]
        for k in bad_keys:
            del data[k]

    filename = Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)
    nx.write_gexf(H, filename)


def export_rips_filtration(G, pos, radii, prefix="rips"):
    """
    Export a sequence of distance-threshold graphs for Gephi.
    """
    for r in radii:
        H = distance_threshold_graph(G.nodes, pos, r)

        # Useful attributes
        nx.set_node_attributes(H, dict(H.degree()), "degree")

        for u, v in H.edges:
            H.edges[u, v]["r"] = float(r)

        export_for_gephi(H, f"{prefix}_r_{str(r).replace('.', '_')}.gexf")


