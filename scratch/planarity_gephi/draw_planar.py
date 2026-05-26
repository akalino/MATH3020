import networkx as nx


def large_planar_graph(m=10, n=10):
    """

    :param m:
    :param n:
    :return:
    """
    G = nx.triangular_lattice_graph(m, n, with_positions=True)
    old_pos = nx.get_node_attributes(G, "pos")
    mapping = {v: i for i, v in enumerate(G.nodes())}
    G = nx.relabel_nodes(G, mapping)
    pos = {mapping[v]: old_pos[v] for v in old_pos}

    nx.set_node_attributes(G, pos, "pos")
    for v, (x, y) in pos.items():
        G.nodes[v]["x"] = float(x)
        G.nodes[v]["y"] = float(y)

    is_planar, _ = nx.check_planarity(G)
    assert is_planar

    G.graph["example_type"] = "planar_triangular_lattice"
    return G, pos


def large_nonplanar_graph_k33(m=10, n=10):
    """

    :param m:
    :param n:
    :return:
    """
    G, pos = large_planar_graph(m, n)

    nodes = list(G.nodes())

    # Pick six fairly spread-out vertices so the obstruction is visible.
    special = [
        nodes[len(nodes) // 5],
        nodes[2 * len(nodes) // 5],
        nodes[3 * len(nodes) // 5],
        nodes[4 * len(nodes) // 5],
        nodes[len(nodes) // 3],
        nodes[2 * len(nodes) // 3],
    ]

    left = special[:3]
    right = special[3:]

    # Add a K_{3,3} subgraph.
    for u in left:
        for v in right:
            G.add_edge(u, v, obstruction="K_3_3")

    # Mark the obstruction nodes for Gephi.
    for v in left:
        G.nodes[v]["part"] = "K33_left"
    for v in right:
        G.nodes[v]["part"] = "K33_right"

    is_planar, cert = nx.check_planarity(G, counterexample=True)
    assert not is_planar

    G.graph["example_type"] = "nonplanar_lattice_plus_K33"
    return G, pos


def large_nonplanar_graph_k5(m=10, n=10):
    """
    Return a graph of similar size to pretty_large_planar_graph,
    but guaranteed nonplanar by adding a K_5 subgraph.

    Construction:
    - Start with the same planar triangular lattice.
    - Choose five existing vertices.
    - Add all missing edges among those five vertices.
    - Since K_5 is nonplanar, the whole graph is nonplanar.
    """
    G, pos = large_planar_graph(m, n)

    nodes = list(G.nodes())

    # Pick five spread-out vertices so the obstruction is not too localized.
    special = [
        nodes[len(nodes) // 6],
        nodes[2 * len(nodes) // 6],
        nodes[3 * len(nodes) // 6],
        nodes[4 * len(nodes) // 6],
        nodes[5 * len(nodes) // 6],
    ]

    # Add all edges needed to make those vertices a K_5.
    for i, u in enumerate(special):
        for v in special[i + 1:]:
            G.add_edge(u, v, obstruction="K_5")

    # Mark the obstruction nodes for Gephi.
    for v in special:
        G.nodes[v]["part"] = "K5"

    is_planar, cert = nx.check_planarity(G, counterexample=True)
    assert not is_planar

    G.graph["example_type"] = "nonplanar_lattice_plus_K5"
    return G, pos


def export_for_gephi(G, filename):
    """
    Export to GEXF for Gephi.

    GEXF does not allow tuple-valued attributes, so we remove the
    NetworkX 'pos' attribute and keep scalar x/y coordinates instead.
    """
    H = G.copy()

    for v, data in H.nodes(data=True):
        if "pos" in data:
            x, y = data["pos"]
            data["x"] = float(x)
            data["y"] = float(y)
            del data["pos"]

    nx.write_gexf(H, filename)


def count_edge_crossings(G, pos, ignore_adjacent_edges=True):
    """
    Count crossings in a specific straight-line drawing of G.

    Parameters
    ----------
    G : networkx.Graph
        The graph.
    pos : dict
        Dictionary mapping nodes to (x, y) positions.
    ignore_adjacent_edges : bool
        If True, edges sharing an endpoint are not counted as crossings.

    Returns
    -------
    int
        Number of edge crossings in this particular drawing.
    """
    edges = list(G.edges())
    crossings = 0

    def orientation(a, b, c):
        """
        Return orientation of ordered triple (a, b, c).

        Positive/negative means clockwise/counterclockwise.
        Zero means collinear.
        """
        return (
            (b[0] - a[0]) * (c[1] - a[1])
            - (b[1] - a[1]) * (c[0] - a[0])
        )

    def segments_cross(a, b, c, d):
        """
        Return True if line segments ab and cd properly cross.

        This excludes collinear overlap and endpoint-touching.
        """
        o1 = orientation(a, b, c)
        o2 = orientation(a, b, d)
        o3 = orientation(c, d, a)
        o4 = orientation(c, d, b)

        return (o1 * o2 < 0) and (o3 * o4 < 0)

    for i, (u1, v1) in enumerate(edges):
        for u2, v2 in edges[i + 1:]:
            if ignore_adjacent_edges and len({u1, v1, u2, v2}) < 4:
                continue

            if segments_cross(pos[u1], pos[v1], pos[u2], pos[v2]):
                crossings += 1

    return crossings


def crossing_summary(G, pos, name):
    is_planar = nx.check_planarity(G)[0]
    drawing_crossings = count_edge_crossings(G, pos)

    if is_planar:
        true_crossing_number = 0
    else:
        true_crossing_number = "unknown from NetworkX"

    print(f"{name}")
    print(f"  Planar? {is_planar}")
    print(f"  True crossing number: {true_crossing_number}")
    print(f"  Crossings in this drawing: {drawing_crossings}")


def remove_obstruction_vertices(G, pos=None,
                                obstruction_parts=("K33_left", "K33_right", "K5")):
    """
    Remove only the vertices involved in a marked K_3,3 or K_5 obstruction.

    Parameters
    ----------
    G : networkx.Graph
        A graph whose obstruction vertices have node attribute 'part'.
    pos : dict or None
        Optional node-position dictionary.
    obstruction_parts : tuple
        Node 'part' values to remove.

    Returns
    -------
    H : networkx.Graph
        Graph with obstruction vertices removed.
    new_pos : dict or None
        Position dictionary restricted to remaining vertices.
    removed_vertices : list
        Vertices that were removed.
    """
    removed_vertices = [
        v for v, data in G.nodes(data=True)
        if data.get("part") in obstruction_parts
    ]

    H = G.copy()
    H.remove_nodes_from(removed_vertices)

    if pos is None:
        new_pos = None
    else:
        new_pos = {
            v: xy for v, xy in pos.items()
            if v in H.nodes
        }

    return H, new_pos, removed_vertices


def planar_face_count(G):
    """
    Return the number of faces and bounded faces predicted by Euler's formula.

    Assumes G is planar. If G is connected:
        F = E - V + 2
        bounded faces = E - V + 1

    If G is disconnected with c components:
        F = E - V + c + 1
        bounded faces = E - V + c
    """
    is_planar, _ = nx.check_planarity(G)
    if not is_planar:
        raise ValueError("Graph is not planar, so Euler face count does not apply cleanly.")

    n = G.number_of_nodes()
    m = G.number_of_edges()
    c = nx.number_connected_components(G)

    total_faces = m - n + c + 1
    bounded_faces = m - n + c

    return {
        "vertices": n,
        "edges": m,
        "components": c,
        "total_faces": total_faces,
        "bounded_faces": bounded_faces,
    }


def count_deleted_vertex_clusters(original_lattice, deleted_vertices):
    """
    Count how many connected clusters the deleted vertices formed
    inside the original lattice graph.

    This is a good proxy for the number of visible defect holes created
    by deleting those vertices, especially when the deleted vertices are
    interior vertices.
    """
    S = set(deleted_vertices)
    deleted_subgraph = original_lattice.subgraph(S)
    return nx.number_connected_components(deleted_subgraph)


def add_k5_obstruction_to_base_graph(B, selected_vertices):
    """
    Add a K_5 obstruction among selected vertices of a planar base graph.
    """
    if len(selected_vertices) != 5:
        raise ValueError("K_5 obstruction requires exactly 5 vertices.")

    G = B.copy()

    for i, u in enumerate(selected_vertices):
        for v in selected_vertices[i + 1:]:
            G.add_edge(u, v, obstruction="K5")

    for v in selected_vertices:
        G.nodes[v]["part"] = "K5"

    assert not nx.check_planarity(G)[0]
    return G


def add_k33_obstruction_to_base_graph(B, left, right):
    """
    Add a K_3,3 obstruction among selected vertices of a planar base graph.
    """
    if len(left) != 3 or len(right) != 3:
        raise ValueError("K_3,3 obstruction requires two sets of 3 vertices.")

    G = B.copy()

    for u in left:
        for v in right:
            G.add_edge(u, v, obstruction="K33")

    for v in left:
        G.nodes[v]["part"] = "K33_left"
    for v in right:
        G.nodes[v]["part"] = "K33_right"

    assert not nx.check_planarity(G)[0]
    return G


if __name__ == '__main__':
    m = 30
    n = 30
    planar, planar_pos = large_planar_graph(m,n)
    nonplanar_k33, nonplanar_pos_k33 = large_nonplanar_graph_k33(m,n)
    nonplanar_k5, nonplanar_pos_k5 = large_nonplanar_graph_k5(m,n)

    print("Planar example is_planar?", nx.check_planarity(planar)[0])
    print("Nonplanar example is_planar?", nx.check_planarity(nonplanar_k33)[0])
    print("Nonplanar example is_planar?", nx.check_planarity(nonplanar_k5)[0])

    print("Planar drawing crossings:", count_edge_crossings(planar, planar_pos))
    print("K_3,3 drawing crossings:", count_edge_crossings(nonplanar_k33, nonplanar_pos_k33))
    print("K_5 drawing crossings:", count_edge_crossings(nonplanar_k5, nonplanar_pos_k5))

    export_for_gephi(planar, "planar_example.gexf")
    export_for_gephi(nonplanar_k33, "nonplanar_example_1.gexf")
    export_for_gephi(nonplanar_k5, "nonplanar_example_2.gexf")


    k33_removed, k33_removed_pos, removed_k33_vertices = remove_obstruction_vertices(
        nonplanar_k33,
        nonplanar_pos_k33,
        obstruction_parts=("K33_left", "K33_right")
    )

    k5_removed, k5_removed_pos, removed_k5_vertices = remove_obstruction_vertices(
        nonplanar_k5,
        nonplanar_pos_k5,
        obstruction_parts=("K5",)
    )

    print("Removed K_3,3 vertices:", removed_k33_vertices)
    print("After removing K_3,3 vertices, planar?", nx.check_planarity(k33_removed)[0])

    print("Removed K_5 vertices:", removed_k5_vertices)
    print("After removing K_5 vertices, planar?", nx.check_planarity(k5_removed)[0])

    print("K_3,3 removed graph face count:")
    print(planar_face_count(k33_removed))

    print("K_5 removed graph face count:")
    print(planar_face_count(k5_removed))

    print(
        "Estimated K_3,3 defect holes:",
        count_deleted_vertex_clusters(planar, removed_k33_vertices)
    )

    print(
        "Estimated K_5 defect holes:",
        count_deleted_vertex_clusters(planar, removed_k5_vertices)
    )

    export_for_gephi(k33_removed, "nonplanar_example_1_repair.gexf")
    export_for_gephi(k5_removed, "nonplanar_example_2_repair.gexf")

    # try some other base graphs (non-lattice) and add/remove the fundamental
    # non-planar graphs K_5 and K_{3,3}
    # How does hole creation depend on the original graph embedding?
    base_graphs = {
        "tree": nx.balanced_tree(2, 5),
        "cycle": nx.cycle_graph(30),
        "grid": nx.grid_2d_graph(8, 8),
        "hexagonal_lattice": nx.hexagonal_lattice_graph(5, 5),
        "triangular_lattice": nx.triangular_lattice_graph(6, 6),
    }
