import networkx as nx

from collections import defaultdict


def square_grid_complex(width=20, height=20):
    """
    Build a square cell complex.

    Vertices are coordinate pairs (i, j).
    Faces are 4-tuples of vertices in cyclic order.

    width, height count square cells, not vertices.
    """
    G = nx.grid_2d_graph(width + 1, height + 1)

    faces = []
    for i in range(width):
        for j in range(height):
            face = (
                (i, j),
                (i + 1, j),
                (i + 1, j + 1),
                (i, j + 1),
            )
            faces.append(face)

    return G, faces


def remove_square_hole(faces, center=(5, 5), radius=2):
    """
    Remove square faces whose centers lie inside a circular-ish region.
    """
    cx, cy = center
    kept = []

    for face in faces:
        xs = [v[0] for v in face]
        ys = [v[1] for v in face]
        mx = sum(xs) / 4
        my = sum(ys) / 4

        if (mx - cx) ** 2 + (my - cy) ** 2 > radius ** 2:
            kept.append(face)

    return kept


def remove_rectangular_hole(faces, x_min, x_max, y_min, y_max):
    """
    Remove all square faces whose lower-left cell coordinate (i, j)
    lies in the rectangle:

        x_min <= i < x_max
        y_min <= j < y_max

    Returns:
        kept_faces
        protected_cycle_edges
    """
    kept = []

    for face in faces:
        xs = [v[0] for v in face]
        ys = [v[1] for v in face]

        i = min(xs)
        j = min(ys)

        inside_hole = (x_min <= i < x_max) and (y_min <= j < y_max)

        if not inside_hole:
            kept.append(face)

    protected = rectangular_boundary_edges(x_min, x_max, y_min, y_max)

    return kept, protected


def rectangular_boundary_edges(x_min, x_max, y_min, y_max):
    """
    Boundary cycle around a rectangular block of removed square cells.

    Example:
        removed cells have x_min <= i < x_max, y_min <= j < y_max.
        The boundary runs along the vertex rectangle:
        x = x_min or x_max, y = y_min or y_max.
    """
    edges = set()

    # Bottom and top horizontal edges
    for x in range(x_min, x_max):
        edges.add(tuple(sorted(((x, y_min), (x + 1, y_min)))))
        edges.add(tuple(sorted(((x, y_max), (x + 1, y_max)))))

    # Left and right vertical edges
    for y in range(y_min, y_max):
        edges.add(tuple(sorted(((x_min, y), (x_min, y + 1)))))
        edges.add(tuple(sorted(((x_max, y), (x_max, y + 1)))))

    return edges


def face_edges(face):
    return [
        tuple(sorted((face[0], face[1]))),
        tuple(sorted((face[1], face[2]))),
        tuple(sorted((face[2], face[3]))),
        tuple(sorted((face[3], face[0]))),
    ]


def free_edges(faces):
    edge_to_faces = defaultdict(list)

    for idx, face in enumerate(faces):
        for e in face_edges(face):
            edge_to_faces[e].append(idx)

    return {
        e: incident_faces
        for e, incident_faces in edge_to_faces.items()
        if len(incident_faces) == 1
    }

# Collapse Modes
# first function completely collapse everything due to boundary break
#

def collapse_freely(faces, max_steps=None, snapshot_steps=None):
    """
    Repeatedly collapse any free edge-face pair.

    This is useful for showing that a contractible filled region can
    collapse away completely.
    """
    if snapshot_steps is None:
        snapshot_steps = {0, 10, 25, 50, 100, 200, 400, 800}
    else:
        snapshot_steps = set(snapshot_steps)

    faces = list(faces)
    snapshots = {}

    step = 0
    if step in snapshot_steps:
        snapshots[step] = list(faces)

    while faces:
        if max_steps is not None and step >= max_steps:
            break

        pairs = free_edge_face_pairs(faces)

        if not pairs:
            break

        edge, face_idx = pairs[0]

        faces = [
            face for idx, face in enumerate(faces)
            if idx != face_idx
        ]

        step += 1

        if step in snapshot_steps:
            snapshots[step] = list(faces)

    snapshots[step] = list(faces)
    return snapshots


# Collapse mode: protect the boundary cycle

def collapse_to_protected_cycle(faces, protected_edges, max_steps=None, snapshot_steps=None):
    """
    Collapse free edge-face pairs while refusing to collapse protected edges.

    This is useful for forcing the complex to collapse down toward a
    chosen boundary cycle around a hole.
    """
    if snapshot_steps is None:
        snapshot_steps = {0, 10, 25, 50, 100, 200, 400, 800}
    else:
        snapshot_steps = set(snapshot_steps)

    faces = list(faces)
    protected_edges = set(protected_edges)
    snapshots = {}

    step = 0
    if step in snapshot_steps:
        snapshots[step] = list(faces)

    while faces:
        if max_steps is not None and step >= max_steps:
            break

        pairs = free_edge_face_pairs(faces, protected_edges=protected_edges)

        if not pairs:
            break

        edge, face_idx = pairs[0]

        faces = [
            face for idx, face in enumerate(faces)
            if idx != face_idx
        ]

        step += 1

        if step in snapshot_steps:
            snapshots[step] = list(faces)

    snapshots[step] = list(faces)
    return snapshots


def graph_from_faces_and_extra_edges(faces, extra_edges=None):
    """
    Build a graph from remaining faces, plus optional protected edges.

    This lets us visualize the final protected hole cycle even after
    all faces have collapsed.
    """
    G = graph_from_faces(faces)

    if extra_edges is not None:
        for u, v in extra_edges:
            G.add_node(u)
            G.add_node(v)
            G.add_edge(u, v, protected=True)

    return G


# Incremental collapses (depricated/not used here)

def collapse_one_face_edge_pair(faces):
    """
    Perform one elementary 2D collapse:
    remove a face together with one free boundary edge.

    For visualization we mainly remove the face. Later we rebuild
    the 1-skeleton from the remaining faces.
    """
    free = free_edges(faces)

    if not free:
        return faces, None

    free_edge, incident = next(iter(free.items()))
    face_idx = incident[0]

    new_faces = [
        face for i, face in enumerate(faces)
        if i != face_idx
    ]

    return new_faces, (free_edge, faces[face_idx])


def collapse_faces(faces, max_steps=None, snapshots=(0, 10, 50, 100, 200, 500)):
    """
    Repeatedly collapse free edge-face pairs.
    Return selected face-list snapshots.
    """
    faces = list(faces)
    saved = {}

    step = 0
    if 0 in snapshots:
        saved[0] = list(faces)

    while faces:
        if max_steps is not None and step >= max_steps:
            break

        new_faces, pair = collapse_one_face_edge_pair(faces)

        if pair is None:
            break

        faces = new_faces
        step += 1

        if step in snapshots:
            saved[step] = list(faces)

    saved[step] = list(faces)
    return saved


def graph_from_faces(faces):
    """
    Build the 1-skeleton graph from a list of square faces.
    """
    G = nx.Graph()

    for face in faces:
        for v in face:
            G.add_node(v)

        for e in face_edges(face):
            G.add_edge(*e)

    return G


def edge_to_face_map(faces):
    """
    Map each edge to the indices of faces containing it.
    """
    edge_faces = defaultdict(list)

    for idx, face in enumerate(faces):
        for e in face_edges(face):
            edge_faces[e].append(idx)

    return edge_faces


def free_edge_face_pairs(faces, protected_edges=None):
    """
    Return all possible free edge-face collapse pairs.

    If protected_edges is given, do not collapse across those edges.
    """
    if protected_edges is None:
        protected_edges = set()

    edge_faces = edge_to_face_map(faces)

    pairs = []
    for edge, incident_faces in edge_faces.items():
        if edge in protected_edges:
            continue

        if len(incident_faces) == 1:
            face_idx = incident_faces[0]
            pairs.append((edge, face_idx))

    return pairs


# Gephi helpers

def relabel_for_gephi(G):
    """
    Relabel coordinate nodes to integers and preserve x/y coordinates.
    """
    mapping = {v: i for i, v in enumerate(G.nodes)}
    H = nx.relabel_nodes(G, mapping)

    for old, new in mapping.items():
        if isinstance(old, tuple) and len(old) == 2:
            x, y = old
            H.nodes[new]["x"] = float(x)
            H.nodes[new]["y"] = float(y)
            H.nodes[new]["original_label"] = str(old)

    for u, v, data in H.edges(data=True):
        if "protected" not in data:
            data["protected"] = False

    return H


def export_for_gephi(G, filename):
    """
    GEXF-safe export.
    Removes tuple/list/dict/set attributes.
    """
    H = G.copy()

    for _, data in H.nodes(data=True):
        bad_keys = [
            key for key, value in data.items()
            if isinstance(value, (tuple, list, dict, set))
        ]
        for key in bad_keys:
            del data[key]

    for _, _, data in H.edges(data=True):
        bad_keys = [
            key for key, value in data.items()
            if isinstance(value, (tuple, list, dict, set))
        ]
        for key in bad_keys:
            del data[key]

    nx.write_gexf(H, filename)



def add_xy_attributes(G):
    for v in G.nodes:
        x, y = v
        G.nodes[v]["x"] = float(x)
        G.nodes[v]["y"] = float(y)
        G.nodes[v]["label"] = str(v)
    return G


def export_collapse_snapshots():
    G, faces = square_grid_complex(width=20, height=20)

    faces_with_hole, protected_cycle = remove_rectangular_hole(
        faces,
        x_min=8,
        x_max=12,
        y_min=8,
        y_max=12,
    )

    # Experiment A: free collapse
    free_snapshots = collapse_freely(
        faces_with_hole,
        snapshot_steps={0, 20, 50, 100, 200, 300, 400}
    )

    for step, step_faces in free_snapshots.items():
        H = graph_from_faces(step_faces)
        H = relabel_for_gephi(H)
        export_for_gephi(H, f"free_collapse_step_{step}.gexf")

    # Experiment B: protected collapse to the hole cycle
    protected_snapshots = collapse_to_protected_cycle(
        faces_with_hole,
        protected_edges=protected_cycle,
        snapshot_steps={0, 20, 50, 100, 200, 300, 400}
    )

    for step, step_faces in protected_snapshots.items():
        H = graph_from_faces_and_extra_edges(
            step_faces,
            extra_edges=protected_cycle
        )
        H = relabel_for_gephi(H)
        export_for_gephi(H, f"planar/protected_collapse_step_{step}.gexf")


if __name__ == "__main__":
    export_collapse_snapshots()
