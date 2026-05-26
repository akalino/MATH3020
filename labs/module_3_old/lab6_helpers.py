from __future__ import annotations

from itertools import permutations
from typing import Any, Dict, Iterable, List, Tuple

import matplotlib.pyplot as plt
import networkx as nx

Edge = Tuple[Any, Any]


def build_graph(edges: Iterable[Edge]) -> nx.Graph:
    G = nx.Graph()
    G.add_edges_from(edges)
    return G


def draw_graph(G: nx.Graph, seed: int = 7) -> None:
    pos = nx.spring_layout(G, seed=seed)
    nx.draw(G, pos, with_labels=True, node_size=1200)
    plt.show()


def degree_table(G: nx.Graph) -> List[Tuple[Any, int]]:
    return sorted(G.degree(), key=lambda x: (-x[1], str(x[0])))


def odd_degree_vertices(G: nx.Graph) -> List[Any]:
    return sorted([v for v, d in G.degree() if d % 2 == 1], key=str)


def graph_summary(G: nx.Graph) -> Dict[str, Any]:
    return {
        "number_of_nodes": G.number_of_nodes(),
        "number_of_edges": G.number_of_edges(),
        "connected": nx.is_connected(G),
        "degree_table": degree_table(G),
        "odd_degree_vertices": odd_degree_vertices(G),
        "num_odd_degree_vertices": len(odd_degree_vertices(G)),
    }


def has_euler_trail(G: nx.Graph) -> bool:
    return nx.has_eulerian_path(G)


def has_euler_circuit(G: nx.Graph) -> bool:
    return nx.is_eulerian(G)


def get_euler_trail(G: nx.Graph) -> List[Tuple[Any, Any]] | None:
    if not nx.has_eulerian_path(G):
        return None
    return list(nx.eulerian_path(G))


def get_euler_circuit(G: nx.Graph) -> List[Tuple[Any, Any]] | None:
    if not nx.is_eulerian(G):
        return None
    return list(nx.eulerian_circuit(G))


def is_hamilton_path(G: nx.Graph, path: List[Any]) -> bool:
    if len(path) != G.number_of_nodes():
        return False
    if len(set(path)) != len(path):
        return False
    return all(G.has_edge(path[i], path[i + 1]) for i in range(len(path) - 1))


def is_hamilton_cycle(G: nx.Graph, cycle: List[Any]) -> bool:
    if len(cycle) != G.number_of_nodes():
        return False
    if len(set(cycle)) != len(cycle):
        return False
    if not all(G.has_edge(cycle[i], cycle[i + 1]) for i in range(len(cycle) - 1)):
        return False
    return G.has_edge(cycle[-1], cycle[0])


def find_hamilton_path_bruteforce(G: nx.Graph) -> List[Any] | None:
    nodes = list(G.nodes())
    for perm in permutations(nodes):
        if is_hamilton_path(G, list(perm)):
            return list(perm)
    return None


def find_hamilton_cycle_bruteforce(G: nx.Graph) -> List[Any] | None:
    nodes = list(G.nodes())
    if not nodes:
        return None

    start = nodes[0]
    rest = [v for v in nodes if v != start]

    for perm in permutations(rest):
        cycle = [start] + list(perm)
        if is_hamilton_cycle(G, cycle):
            return cycle
    return False


def add_edge_and_analyze(G: nx.Graph, u: Any, v: Any) -> Dict[str, Any]:
    H = G.copy()
    H.add_edge(u, v)
    return {
        "new_edge": (u, v),
        "odd_degree_vertices": odd_degree_vertices(H),
        "num_odd_degree_vertices": len(odd_degree_vertices(H)),
        "has_euler_trail": has_euler_trail(H),
        "has_euler_circuit": has_euler_circuit(H),
        "hamilton_path": find_hamilton_path_bruteforce(H) if H.number_of_nodes() <= 8 else None,
        "hamilton_cycle": find_hamilton_cycle_bruteforce(H) if H.number_of_nodes() <= 8 else None,
    }


def export_for_gephi(G: nx.Graph, path: str = "lab06_graph.gexf") -> str:
    nx.write_gexf(G, path)
    return path