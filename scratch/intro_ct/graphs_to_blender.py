from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import networkx as nx

Node = int
Point3D = Tuple[float, float, float]
Triangle = Tuple[Node, Node, Node]
Edge = Tuple[Node, Node]


# -----------------------------------------------------------------------------
# Triangle-complex helpers
# -----------------------------------------------------------------------------


def triangle_faces_from_graph(G: nx.Graph) -> List[Triangle]:
    """
    Return all triangular 2-faces from 3-cliques of G.
    """
    triangles = []

    for clique in nx.enumerate_all_cliques(G):
        if len(clique) == 3:
            triangles.append(tuple(sorted(clique)))
        elif len(clique) > 3:
            break

    return triangles


def triangle_edges(face: Triangle) -> List[Edge]:
    a, b, c = face
    return [
        tuple(sorted((a, b))),
        tuple(sorted((a, c))),
        tuple(sorted((b, c))),
    ]


def free_edges_triangle_complex(triangles: Sequence[Triangle]) -> Dict[Edge, List[int]]:
    """
    Return edges incident to exactly one triangle, with the incident triangle id.
    """
    edge_to_triangles = defaultdict(list)

    for idx, tri in enumerate(triangles):
        for e in triangle_edges(tri):
            edge_to_triangles[e].append(idx)

    return {
        e: incident
        for e, incident in edge_to_triangles.items()
        if len(incident) == 1
    }


def collapse_one_triangle_edge_pair(triangles: Sequence[Triangle]):
    """
    Remove one triangle that has a free edge.
    Returns (new_triangles, cancellation_pair).
    """
    free = free_edges_triangle_complex(triangles)

    if not free:
        return list(triangles), None

    free_edge, incident = next(iter(free.items()))
    tri_idx = incident[0]

    new_triangles = [
        tri for i, tri in enumerate(triangles)
        if i != tri_idx
    ]

    return new_triangles, (free_edge, triangles[tri_idx])


def triangle_collapse_snapshots(
    triangles: Sequence[Triangle],
    snapshot_steps: Iterable[int] = (0, 1, 2, 5, 10, 20, 40),
    max_steps: Optional[int] = None,
) -> Dict[int, List[Triangle]]:
    """
    Repeatedly collapse free edge-triangle pairs and save selected snapshots.
    """
    snapshot_steps = set(snapshot_steps)
    triangles = list(triangles)
    snapshots = {}
    step = 0

    if step in snapshot_steps:
        snapshots[step] = list(triangles)

    while triangles:
        if max_steps is not None and step >= max_steps:
            break

        new_triangles, pair = collapse_one_triangle_edge_pair(triangles)
        if pair is None:
            break

        triangles = new_triangles
        step += 1

        if step in snapshot_steps:
            snapshots[step] = list(triangles)

    snapshots[step] = list(triangles)
    return snapshots


def graph_from_triangles(triangles: Sequence[Triangle], keep_isolated_nodes: Optional[Iterable[Node]] = None) -> nx.Graph:
    """
    Build a 1-skeleton graph from triangles.
    """
    G = nx.Graph()

    if keep_isolated_nodes is not None:
        G.add_nodes_from(keep_isolated_nodes)

    for tri in triangles:
        for v in tri:
            G.add_node(v)

        for e in triangle_edges(tri):
            G.add_edge(*e, triangle_edge=True)

    return G


# -----------------------------------------------------------------------------
# Nonplanar examples
# -----------------------------------------------------------------------------


def k5_with_dangling_trees(num_leaves_per_vertex: int = 3) -> nx.Graph:
    G = nx.complete_graph(5)
    next_node = 5

    for v in range(5):
        G.nodes[v]["core"] = True
        G.nodes[v]["example_part"] = "K5_core"

    for u, v in G.edges:
        G.edges[u, v]["core_edge"] = True
        G.edges[u, v]["example_part"] = "K5_core_edge"

    for v in range(5):
        previous = v
        for _ in range(num_leaves_per_vertex):
            G.add_node(next_node, noise=True, example_part="tree_noise")
            G.add_edge(previous, next_node, noise_edge=True, example_part="tree_noise_edge")
            previous = next_node
            next_node += 1

    G.graph["example"] = "K5 with dangling trees"
    return G


def k33_with_dangling_trees(num_leaves_per_vertex: int = 3) -> nx.Graph:
    G = nx.complete_bipartite_graph(3, 3)
    next_node = 6

    for v in range(6):
        G.nodes[v]["core"] = True
        G.nodes[v]["example_part"] = "K33_core"
        G.nodes[v]["bipartition"] = "left" if v < 3 else "right"

    for u, v in G.edges:
        G.edges[u, v]["core_edge"] = True
        G.edges[u, v]["example_part"] = "K33_core_edge"

    for v in range(6):
        previous = v
        for _ in range(num_leaves_per_vertex):
            G.add_node(next_node, noise=True, example_part="tree_noise")
            G.add_edge(previous, next_node, noise_edge=True, example_part="tree_noise_edge")
            previous = next_node
            next_node += 1

    G.graph["example"] = "K3,3 with dangling trees"
    return G


def k5_with_triangle_flaps() -> Tuple[nx.Graph, List[Triangle]]:
    """
    Start with a K5 core, then attach one triangular flap to each K5 edge.

    Each flap is a new vertex w plus a triangle (u, v, w) attached along core edge uv.
    These flaps have free outer edges, so triangle collapses remove them and reveal K5.
    """
    G = nx.complete_graph(5)
    triangles: List[Triangle] = []

    for v in range(5):
        G.nodes[v]["core"] = True
        G.nodes[v]["example_part"] = "K5_core"

    for u, v in G.edges:
        G.edges[u, v]["core_edge"] = True
        G.edges[u, v]["example_part"] = "K5_core_edge"

    next_node = 5
    core_edges = list(G.edges)
    for u, v in core_edges:
        w = next_node
        next_node += 1
        G.add_node(w, flap=True, example_part="triangle_flap_vertex")
        G.add_edge(u, w, triangle_edge=True, example_part="triangle_flap_edge")
        G.add_edge(v, w, triangle_edge=True, example_part="triangle_flap_edge")
        triangles.append(tuple(sorted((u, v, w))))

    G.graph["example"] = "K5 with collapsible triangle flaps"
    return G, triangles


# -----------------------------------------------------------------------------
# Collapse / summaries
# -----------------------------------------------------------------------------


def collapse_leaves_with_snapshots(
    G: nx.Graph,
    snapshot_steps: Iterable[int] = (0, 1, 2, 5, 10, 15, 20, 25, 30),
) -> Dict[int, nx.Graph]:
    """
    Repeatedly remove degree-1 vertices and save selected snapshots.
    """
    snapshot_steps = set(snapshot_steps)
    H = G.copy()
    snapshots: Dict[int, nx.Graph] = {}
    step = 0

    if step in snapshot_steps:
        snapshots[step] = H.copy()

    while True:
        leaves = sorted([v for v in H.nodes if H.degree(v) == 1])
        if not leaves:
            break

        H.remove_node(leaves[0])
        step += 1

        if step in snapshot_steps:
            snapshots[step] = H.copy()

    snapshots[step] = H.copy()
    return snapshots


def graph_summary(G: nx.Graph) -> Dict[str, object]:
    components = nx.number_connected_components(G) if G.number_of_nodes() else 0
    beta1 = G.number_of_edges() - G.number_of_nodes() + components
    planar = nx.check_planarity(G)[0] if G.number_of_nodes() else True
    return {
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "components": components,
        "beta1_graph_cycle_rank": beta1,
        "planar": planar,
    }


# -----------------------------------------------------------------------------
# Metric / Rips helpers
# -----------------------------------------------------------------------------


def assign_3d_layout(G: nx.Graph, seed: int = 7, scale: float = 5.0) -> Dict[Node, Point3D]:
    """
    Compute a reproducible 3D spring layout.
    """
    pos = nx.spring_layout(G, dim=3, seed=seed, scale=scale)
    return {
        v: (float(x), float(y), float(z))
        for v, (x, y, z) in pos.items()
    }


def distance_3d(pos: Dict[Node, Point3D], u: Node, v: Node) -> float:
    x1, y1, z1 = pos[u]
    x2, y2, z2 = pos[v]
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)


def add_edge_lengths(G: nx.Graph, pos: Dict[Node, Point3D]) -> None:
    for u, v in G.edges:
        G.edges[u, v]["length"] = float(distance_3d(pos, u, v))


def rips_graph_from_positions(nodes: Iterable[Node], pos: Dict[Node, Point3D], r: float) -> nx.Graph:
    H = nx.Graph()
    nodes = list(nodes)
    H.add_nodes_from(nodes)

    for i, u in enumerate(nodes):
        for v in nodes[i + 1:]:
            d = distance_3d(pos, u, v)
            if d <= r:
                H.add_edge(u, v, length=float(d), r=float(r), rips_edge=True)

    H.graph["example"] = f"Rips graph at radius {r}"
    return H


def rips_triangles_from_positions(nodes: Iterable[Node], pos: Dict[Node, Point3D], r: float) -> List[Triangle]:
    triangles: List[Triangle] = []
    nodes = list(nodes)

    for i, a in enumerate(nodes):
        for j in range(i + 1, len(nodes)):
            b = nodes[j]
            for k in range(j + 1, len(nodes)):
                c = nodes[k]
                if (
                    distance_3d(pos, a, b) <= r
                    and distance_3d(pos, a, c) <= r
                    and distance_3d(pos, b, c) <= r
                ):
                    triangles.append(tuple(sorted((a, b, c))))

    return triangles


# -----------------------------------------------------------------------------
# JSON export
# -----------------------------------------------------------------------------


def _json_safe_value(value):
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def graph_to_scene_dict(
    G: nx.Graph,
    pos: Dict[Node, Point3D],
    triangles: Optional[Sequence[Triangle]] = None,
    name: str = "graph_scene",
    metadata: Optional[Dict[str, object]] = None,
) -> Dict[str, object]:
    """
    Convert graph + optional triangle faces into a Blender-friendly JSON dict.
    """
    triangles = list(triangles or [])
    metadata = dict(metadata or {})
    summary = graph_summary(G)

    nodes = []
    for v in G.nodes:
        x, y, z = pos[v]
        attrs = {k: _json_safe_value(val) for k, val in G.nodes[v].items()}
        nodes.append({
            "id": str(v),
            "x": float(x),
            "y": float(y),
            "z": float(z),
            "degree": int(G.degree(v)),
            **attrs,
        })

    edges = []
    for u, v, data in G.edges(data=True):
        attrs = {k: _json_safe_value(val) for k, val in data.items()}
        edges.append({
            "source": str(u),
            "target": str(v),
            **attrs,
        })

    return {
        "name": name,
        "metadata": {
            **metadata,
            **summary,
        },
        "nodes": nodes,
        "edges": edges,
        "triangles": [
            {"vertices": [str(a), str(b), str(c)]}
            for a, b, c in triangles
        ],
    }


def write_scene_json(
    G: nx.Graph,
    pos: Dict[Node, Point3D],
    path: Path,
    triangles: Optional[Sequence[Triangle]] = None,
    name: Optional[str] = None,
    metadata: Optional[Dict[str, object]] = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    scene = graph_to_scene_dict(
        G,
        pos,
        triangles=triangles,
        name=name or path.stem,
        metadata=metadata,
    )
    path.write_text(json.dumps(scene, indent=2))


def export_snapshot_sequence(
    snapshots: Dict[int, nx.Graph],
    pos: Dict[Node, Point3D],
    outdir: Path,
    prefix: str,
) -> None:
    for step, H in sorted(snapshots.items()):
        add_edge_lengths(H, pos)
        write_scene_json(
            H,
            pos,
            outdir / f"{prefix}_step_{step:03d}.json",
            name=f"{prefix} step {step}",
            metadata={"collapse_type": "leaf_vertex_edge", "step": step},
        )


# -----------------------------------------------------------------------------
# Main export driver
# -----------------------------------------------------------------------------


def export_all(outdir: Path, seed: int = 7) -> None:
    outdir.mkdir(parents=True, exist_ok=True)

    # 1. K5 + dangling trees, then leaf cancellations.
    k5 = k5_with_dangling_trees(num_leaves_per_vertex=4)
    k5_pos = assign_3d_layout(k5, seed=seed, scale=5.0)
    add_edge_lengths(k5, k5_pos)
    write_scene_json(k5, k5_pos, outdir / "k5_dangling_initial.json", name="K5 with dangling trees")
    export_snapshot_sequence(
        collapse_leaves_with_snapshots(k5, snapshot_steps=(0, 5, 10, 15, 20)),
        k5_pos,
        outdir,
        "k5_leaf_collapse",
    )

    # 2. K3,3 + dangling trees, then leaf cancellations.
    k33 = k33_with_dangling_trees(num_leaves_per_vertex=4)
    k33_pos = assign_3d_layout(k33, seed=seed + 1, scale=5.0)
    add_edge_lengths(k33, k33_pos)
    write_scene_json(k33, k33_pos, outdir / "k33_dangling_initial.json", name="K3,3 with dangling trees")
    export_snapshot_sequence(
        collapse_leaves_with_snapshots(k33, snapshot_steps=(0, 6, 12, 18, 24)),
        k33_pos,
        outdir,
        "k33_leaf_collapse",
    )

    # 3. K5 + triangle flaps, then triangle-edge cancellations.
    flap_graph, flap_triangles = k5_with_triangle_flaps()
    flap_pos = assign_3d_layout(flap_graph, seed=seed + 2, scale=5.0)
    add_edge_lengths(flap_graph, flap_pos)
    write_scene_json(
        flap_graph,
        flap_pos,
        outdir / "k5_triangle_flaps_initial.json",
        triangles=flap_triangles,
        name="K5 with triangle flaps",
        metadata={"triangle_count": len(flap_triangles)},
    )

    triangle_snaps = triangle_collapse_snapshots(
        flap_triangles,
        snapshot_steps=(0, 1, 2, 5, 10),
    )
    for step, tris in sorted(triangle_snaps.items()):
        H = graph_from_triangles(tris, keep_isolated_nodes=flap_graph.nodes)
        # Preserve original core edges so final image exposes K5, not empty graph.
        for u, v, data in flap_graph.edges(data=True):
            if data.get("core_edge"):
                H.add_edge(u, v, **data)
        for v, data in flap_graph.nodes(data=True):
            H.nodes[v].update(data)
        add_edge_lengths(H, flap_pos)
        write_scene_json(
            H,
            flap_pos,
            outdir / f"k5_triangle_collapse_step_{step:03d}.json",
            triangles=tris,
            name=f"K5 triangle-flap collapse step {step}",
            metadata={"collapse_type": "edge_triangle", "step": step, "remaining_triangles": len(tris)},
        )

    # 4. Metric/Rips sequence on the K5 noisy point cloud.
    radii = [1.2, 1.8, 2.4, 3.0]
    for r in radii:
        H = rips_graph_from_positions(k5.nodes, k5_pos, r)
        # Copy node tags from source graph.
        for v, data in k5.nodes(data=True):
            H.nodes[v].update(data)
        tris = rips_triangles_from_positions(k5.nodes, k5_pos, r)
        write_scene_json(
            H,
            k5_pos,
            outdir / f"k5_rips_r_{str(r).replace('.', '_')}.json",
            triangles=tris,
            name=f"K5 noisy Rips complex r={r}",
            metadata={"rips_radius": r, "triangle_count": len(tris)},
        )

    print(f"Wrote Blender JSON scenes to: {outdir.resolve()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export nonplanar graph examples as Blender-friendly JSON.")
    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path("blender_json_exports"),
        help="Directory for JSON scene files.",
    )
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()
    export_all(args.outdir, seed=args.seed)


if __name__ == "__main__":
    main()
