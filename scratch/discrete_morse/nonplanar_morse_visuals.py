"""
Nonplanar Morse-style visualization lab for Gephi.

Story mirrored from the planar collapse lab:

1. Graph-only Morse cancellation:
   - Start with a nonplanar core: K5 or K3,3.
   - Add dangling tree noise.
   - Repeatedly cancel leaf vertex-edge pairs.
   - The noise disappears, but the nonplanar core remains.

2. Triangle-complex cancellation:
   - Treat triangles as filled 2-cells.
   - Collapse free edge-triangle pairs.
   - K5 as a full triangle clique complex gets stuck immediately under naive free-face peeling.
   - K5 with attached triangle flaps has collapsible 2D noise, but the nonplanar core remains.

Outputs are GEXF files for Gephi.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

import networkx as nx

Edge = Tuple[int, int]
Triangle = Tuple[int, int, int]


# Basic graph utilities

def sorted_edge(u, v):
    return tuple(sorted((u, v)))


def safe_check_planar(G: nx.Graph) -> bool:
    return nx.check_planarity(G, counterexample=False)[0]


def beta1(G: nx.Graph) -> int:
    """Cycle rank / first Betti number of a graph."""
    return G.number_of_edges() - G.number_of_nodes() + nx.number_connected_components(G)


def graph_summary(G: nx.Graph, name: str) -> Dict[str, object]:
    return {
        "name": name,
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "components": nx.number_connected_components(G),
        "beta1": beta1(G),
        "planar": safe_check_planar(G),
        "min_degree": min(dict(G.degree()).values()) if G.number_of_nodes() else None,
        "max_degree": max(dict(G.degree()).values()) if G.number_of_nodes() else None,
    }


def print_summary_table(rows: Sequence[Dict[str, object]]) -> None:
    keys = ["name", "nodes", "edges", "components", "beta1", "planar", "min_degree", "max_degree"]
    widths = {k: max(len(k), *(len(str(row.get(k, ""))) for row in rows)) for k in keys}
    print("  ".join(k.ljust(widths[k]) for k in keys))
    print("  ".join("-" * widths[k] for k in keys))
    for row in rows:
        print("  ".join(str(row.get(k, "")).ljust(widths[k]) for k in keys))


# GEXF export helpers

def add_basic_attributes(G: nx.Graph, graph_type: str = "") -> nx.Graph:
    """Add attributes useful for Gephi styling."""
    H = G.copy()
    H.graph["graph_type"] = graph_type

    degrees = dict(H.degree())
    nx.set_node_attributes(H, degrees, "degree")

    components = list(nx.connected_components(H))
    component_id = {}
    for i, comp in enumerate(components):
        for v in comp:
            component_id[v] = i
    nx.set_node_attributes(H, component_id, "component")

    for v, data in H.nodes(data=True):
        data.setdefault("core", False)
        data.setdefault("noise", False)
        data.setdefault("critical", False)
        data.setdefault("collapse_step", -1)

    for _, _, data in H.edges(data=True):
        data.setdefault("core_edge", False)
        data.setdefault("noise_edge", False)
        data.setdefault("triangle_edge", False)
        data.setdefault("collapse_step", -1)

    return H


def assign_layout_attributes(G: nx.Graph, seed: int = 7) -> nx.Graph:
    """Store spring-layout x/y attributes for Gephi import."""
    H = G.copy()
    pos = nx.spring_layout(H, seed=seed)
    for v, (x, y) in pos.items():
        H.nodes[v]["x"] = float(x)
        H.nodes[v]["y"] = float(y)
    return H


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


# Nonplanar cores with collapsible graph noise

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


def collapse_one_leaf_pair(G: nx.Graph, protect_core: bool = True) -> Tuple[nx.Graph, Optional[Tuple[int, Edge]]]:
    """
    Cancel one leaf vertex with its unique incident edge.

    If protect_core=True, never delete a node marked core=True.
    """
    H = G.copy()
    candidates = []
    for v in H.nodes():
        if H.degree(v) == 1:
            if protect_core and H.nodes[v].get("core", False):
                continue
            candidates.append(v)

    if not candidates:
        return H, None

    leaf = candidates[0]
    nbr = next(iter(H.neighbors(leaf)))
    H.remove_node(leaf)
    return H, (leaf, sorted_edge(leaf, nbr))


def leaf_collapse_snapshots(
    G: nx.Graph,
    snapshot_steps: Iterable[int] = (0, 1, 2, 5, 10, 15, 20, 30),
    protect_core: bool = True,
) -> Dict[int, nx.Graph]:
    """Repeatedly cancel leaf-edge pairs and save selected snapshots."""
    snapshot_steps = set(snapshot_steps)
    H = G.copy()
    snapshots = {}
    step = 0

    if step in snapshot_steps:
        snapshots[step] = H.copy()

    while True:
        H2, pair = collapse_one_leaf_pair(H, protect_core=protect_core)
        if pair is None:
            break
        step += 1
        H = H2
        if step in snapshot_steps:
            snapshots[step] = H.copy()

    snapshots[step] = H.copy()
    return snapshots


# Triangle-complex utilities

def triangle_faces_from_graph(G: nx.Graph) -> List[Triangle]:
    """Return all triangular 2-faces from 3-cliques of G."""
    triangles = []
    for clique in nx.enumerate_all_cliques(G):
        if len(clique) == 3:
            triangles.append(tuple(sorted(clique)))
        elif len(clique) > 3:
            break
    return triangles


def triangle_edges(face: Triangle) -> List[Edge]:
    a, b, c = face
    return [sorted_edge(a, b), sorted_edge(a, c), sorted_edge(b, c)]


def edge_to_triangle_map(triangles: Sequence[Triangle]) -> Dict[Edge, List[int]]:
    edge_to_triangles = defaultdict(list)
    for idx, tri in enumerate(triangles):
        for e in triangle_edges(tri):
            edge_to_triangles[e].append(idx)
    return edge_to_triangles


def free_edges_triangle_complex(triangles: Sequence[Triangle],
                                protected_edges: Optional[Set[Edge]] = None) -> Dict[Edge, List[int]]:
    if protected_edges is None:
        protected_edges = set()
    edge_to_triangles = edge_to_triangle_map(triangles)
    return {
        e: incident
        for e, incident in edge_to_triangles.items()
        if len(incident) == 1 and e not in protected_edges
    }


def collapse_one_triangle_edge_pair(
    triangles: Sequence[Triangle],
    protected_edges: Optional[Set[Edge]] = None,
) -> Tuple[List[Triangle], Optional[Tuple[Edge, Triangle]]]:
    free = free_edges_triangle_complex(triangles, protected_edges=protected_edges)
    if not free:
        return list(triangles), None

    free_edge, incident = next(iter(free.items()))
    tri_idx = incident[0]
    tri = triangles[tri_idx]
    new_triangles = [t for i, t in enumerate(triangles) if i != tri_idx]
    return new_triangles, (free_edge, tri)


def graph_from_triangles(triangles: Sequence[Triangle], extra_edges: Optional[Iterable[Edge]] = None) -> nx.Graph:
    G = nx.Graph()
    for tri in triangles:
        for v in tri:
            G.add_node(v)
        for e in triangle_edges(tri):
            G.add_edge(*e, triangle_edge=True)

    if extra_edges is not None:
        for u, v in extra_edges:
            G.add_edge(u, v, core_edge=True)

    return G


def triangle_collapse_snapshots(
    triangles: Sequence[Triangle],
    snapshot_steps: Iterable[int] = (0, 1, 2, 5, 10, 20, 50),
    protected_edges: Optional[Set[Edge]] = None,
) -> Dict[int, List[Triangle]]:
    snapshot_steps = set(snapshot_steps)
    triangles = list(triangles)
    snapshots = {}
    step = 0

    if step in snapshot_steps:
        snapshots[step] = list(triangles)

    while triangles:
        new_triangles, pair = collapse_one_triangle_edge_pair(triangles, protected_edges=protected_edges)
        if pair is None:
            break
        step += 1
        triangles = new_triangles
        if step in snapshot_steps:
            snapshots[step] = list(triangles)

    snapshots[step] = list(triangles)
    return snapshots


def k5_with_triangle_flaps(num_flaps_per_core_edge: int = 1) -> Tuple[nx.Graph, List[Triangle], Set[Edge]]:
    """
    Build a nonplanar K5 core with collapsible triangular 2D flaps attached to core edges.

    The core K5 edges are protected. Each flap is a triangle (u, v, w) attached
    along one K5 core edge (u, v). The two outer edges are free, so each flap
    can be removed by an edge-triangle cancellation.
    """
    G = nx.complete_graph(5)
    G = mark_k5_core(G)
    core_edges = {sorted_edge(u, v) for u, v in nx.complete_graph(5).edges()}
    triangles = []
    next_node = 5

    for u, v in sorted(core_edges):
        for _ in range(num_flaps_per_core_edge):
            w = next_node
            next_node += 1
            G.add_node(w, noise=True, core=False, face_node=False)
            G.add_edge(u, w, triangle_edge=True, noise_edge=True)
            G.add_edge(v, w, triangle_edge=True, noise_edge=True)
            # Core edge already exists.
            triangles.append(tuple(sorted((u, v, w))))

    return G, triangles, core_edges


def k5_full_clique_triangles() -> Tuple[nx.Graph, List[Triangle], Set[Edge]]:
    """
    K5 with every 3-clique filled as a triangle.

    Naive free edge-triangle collapses get stuck because every K5 edge lies in
    three triangles, so there are no free edges.
    """
    G = mark_k5_core(nx.complete_graph(5))
    triangles = triangle_faces_from_graph(G)
    core_edges = {sorted_edge(u, v) for u, v in G.edges()}
    return G, triangles, core_edges


# Export experiments

def export_leaf_collapse_experiment(G: nx.Graph, out_dir: Path, prefix: str) -> List[Dict[str, object]]:
    snapshots = leaf_collapse_snapshots(G)
    rows = []

    for step, H in sorted(snapshots.items()):
        H = add_basic_attributes(H, graph_type=f"{prefix}_leaf_collapse")
        H = assign_layout_attributes(H, seed=7)
        export_for_gephi(H, out_dir / f"{prefix}_leaf_collapse_step_{step}.gexf")
        rows.append(graph_summary(H, f"{prefix} leaf step {step}"))

    return rows


def export_triangle_collapse_experiment(
    triangles: Sequence[Triangle],
    core_edges: Set[Edge],
    out_dir: Path,
    prefix: str,
    protected_edges: Optional[Set[Edge]] = None,
) -> List[Dict[str, object]]:
    snapshots = triangle_collapse_snapshots(triangles, protected_edges=protected_edges)
    rows = []

    for step, tris in sorted(snapshots.items()):
        H = graph_from_triangles(tris, extra_edges=core_edges)
        H = add_basic_attributes(H, graph_type=f"{prefix}_triangle_collapse")
        H = assign_layout_attributes(H, seed=11)
        export_for_gephi(H, out_dir / f"{prefix}_triangle_collapse_step_{step}.gexf")
        rows.append(graph_summary(H, f"{prefix} triangle step {step}"))

    return rows


def run_all(out_dir: str | Path = "nonplanar") -> None:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []

    # Experiment 1: Graph-only cancellations preserve nonplanar cores.
    rows.extend(export_leaf_collapse_experiment(k5_with_dangling_trees(4), out_dir, "k5_noise"))
    rows.extend(export_leaf_collapse_experiment(k33_with_dangling_trees(4), out_dir, "k33_noise"))

    # Experiment 2: K5 full clique-complex triangles get stuck under naive peeling.
    G_k5_full, full_triangles, core_edges = k5_full_clique_triangles()
    rows.append(graph_summary(add_basic_attributes(assign_layout_attributes(G_k5_full),
                                                   "k5_full_core"), "K5 core"))
    rows.extend(
        export_triangle_collapse_experiment(
            full_triangles,
            core_edges,
            out_dir,
            "k5_full_clique_complex",
            protected_edges=None,
        )
    )

    # Experiment 3: K5 core with triangular flaps; flaps collapse, core remains.
    G_flap, flap_triangles, flap_core_edges = k5_with_triangle_flaps(num_flaps_per_core_edge=1)
    G_flap = add_basic_attributes(G_flap, graph_type="k5_with_triangle_flaps")
    G_flap = assign_layout_attributes(G_flap, seed=13)
    export_for_gephi(G_flap, out_dir / "k5_with_triangle_flaps_initial_graph.gexf")
    rows.append(graph_summary(G_flap, "K5 with triangle flaps initial"))
    rows.extend(
        export_triangle_collapse_experiment(
            flap_triangles,
            flap_core_edges,
            out_dir,
            "k5_triangle_flaps",
            protected_edges=flap_core_edges,
        )
    )

    print_summary_table(rows)
    print(f"\nWrote Gephi files to: {out_dir.resolve()}")


if __name__ == "__main__":
    run_all()