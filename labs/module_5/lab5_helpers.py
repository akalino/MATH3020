from __future__ import annotations

from typing import Any, Dict, Iterable, List, Tuple

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

Edge = Tuple[Any, Any]


def sample_tree_edges() -> List[Edge]:
    return [
        ("A", "B"),
        ("B", "C"),
        ("C", "D"),
        ("D", "E"),
        ("C", "F"),
        ("F", "G"),
    ]


def sample_modified_edges() -> List[Edge]:
    """
    A graph obtained by adding one extra edge to the sample tree.
    """
    return [
        ("A", "B"),
        ("B", "C"),
        ("C", "D"),
        ("D", "E"),
        ("C", "F"),
        ("F", "G"),
        ("A", "E"),
    ]


def build_graph(edges: Iterable[Edge]) -> nx.Graph:
    G = nx.Graph()
    G.add_edges_from(edges)
    return G


def draw_graph(G: nx.Graph, seed: int = 7) -> None:
    pos = nx.spring_layout(G, seed=seed)
    nx.draw(G, pos, with_labels=True, node_size=1200)
    plt.show()


def graph_summary(G: nx.Graph) -> Dict[str, Any]:
    return {
        "number_of_nodes": G.number_of_nodes(),
        "number_of_edges": G.number_of_edges(),
        "connected": nx.is_connected(G),
        "is_tree": nx.is_tree(G),
        "degree_dict": dict(G.degree()),
    }


def shortest_path_between(G: nx.Graph, u: Any, v: Any) -> List[Any] | None:
    if nx.has_path(G, u, v):
        return nx.shortest_path(G, source=u, target=v)
    return None


def distance_between(G: nx.Graph, u: Any, v: Any) -> int | None:
    if nx.has_path(G, u, v):
        return nx.shortest_path_length(G, source=u, target=v)
    return None


def all_pairs_distances(G: nx.Graph) -> Dict[Any, Dict[Any, int]]:
    return {u: dict(lengths) for u, lengths in nx.all_pairs_shortest_path_length(G)}


def valuesort(d):
    return [d[key] for key in sorted(d.keys())]


def distance_matrix(G: nx.Graph):
    distance_dict = all_pairs_distances(G)
    verts = list(distance_dict.keys())
    verts.sort()
    print(f"Vertices: {verts}")
    n_verts = len(verts)
    dm = np.zeros((n_verts, n_verts))
    for i in range(n_verts):
        start = verts[i]
        for j in range(n_verts):
            end = verts[j]
            dist = distance_dict[start][end]
            dm[i, j] = dist
    return dm


def eccentricity_dict(G: nx.Graph) -> Dict[Any, int]:
    return nx.eccentricity(G)


def graph_diameter(G: nx.Graph) -> int:
    return nx.diameter(G)


def graph_radius(G: nx.Graph) -> int:
    return nx.radius(G)


def graph_center(G: nx.Graph) -> List[Any]:
    return nx.center(G)


def graph_periphery(G: nx.Graph) -> List[Any]:
    return nx.periphery(G)


def add_edge_and_compare(G: nx.Graph, u: Any, v: Any) -> Dict[str, Any]:
    H = G.copy()
    H.add_edge(u, v)

    return {
        "new_edge": (u, v),
        "connected": nx.is_connected(H),
        "is_tree": nx.is_tree(H),
        "diameter": nx.diameter(H),
        "radius": nx.radius(H),
        "center": nx.center(H),
        "periphery": nx.periphery(H),
    }


def export_for_gephi(G: nx.Graph, path: str = "lab05_graph.gexf") -> str:
    nx.write_gexf(G, path)
    return path


def generate_path_graph(n: int) -> nx.Graph:
    return nx.path_graph(n)


def generate_star_graph(n: int) -> nx.Graph:
    """
    Returns a star graph on n vertices total.
    NetworkX star_graph(k) creates k+1 vertices, so adjust accordingly.
    """
    if n < 2:
        raise ValueError("n must be at least 2")
    return nx.star_graph(n - 1)


def generate_random_tree(n: int, seed: int | None = None) -> nx.Graph:
    return nx.random_labeled_tree(n, seed=seed)