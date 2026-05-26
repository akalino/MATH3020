import networkx as nx
import random


def grid_with_holes(m=25, n=25):
    """
    Square grid with regions deleted to create holes.

    :param m:
    :param n:
    :return:
    """
    G = nx.grid_2d_graph(m,n)

    holes = []

    # round(ish) hole
    center1 = (8, 8)
    radius1 = 3
    hole1 = [v for v in G.nodes
             if (v[0] - center1[0]) ** 2 + (v[1] - center1[1]) ** 2 <= radius1 ** 2]
    holes.extend(hole1)

    # long skinny hole
    hole2 = [
        v for v in G.nodes
        if 14 <= v[0] <= 19 and 14 <= v[1] <= 16
    ]
    holes.extend(hole2)

    # Small isolated defect
    hole3 = [(18, 6), (18, 7), (19, 6), (19, 7)]
    holes.extend(hole3)

    # Boundary bite
    hole4 = [
        v for v in G.nodes
        if v[0] <= 3 and 18 <= v[1] <= 22
    ]
    holes.extend(hole4)

    G.remove_nodes_from(holes)

    pos = {v: (v[0], v[1]) for v in G.nodes}

    # Basic attributes for Gephi
    for v in G.nodes:
        G.nodes[v]["x"] = float(v[0])
        G.nodes[v]["y"] = float(v[1])
        G.nodes[v]["degree"] = G.degree(v)

    return G, pos


def relabel_with_xy(G, pos):
    mapping = {v: i for i, v in enumerate(G.nodes)}
    H = nx.relabel_nodes(G, mapping)

    new_pos = {}
    for old, new in mapping.items():
        x, y = pos[old]
        H.nodes[new]["x"] = float(x)
        H.nodes[new]["y"] = float(y)
        H.nodes[new]["label"] = str(old)
        new_pos[new] = (x, y)

    return H, new_pos


# simplification rules
# Rule 1: random thinning
# destroys cycles and can disconnect graph

def random_edge_thinning(G, p_remove=0.25, seed=0):
    """
    Remove a random fraction of edges.
    This often damages cycles unpredictably.
    """
    rng = random.Random(seed)
    H = G.copy()

    for e in list(H.edges):
        if rng.random() < p_remove:
            H.remove_edge(*e)

    return H

# Rule 2: 2-core collapse
# discrete Morse-style operation
# leaf collapse removes tree-like noise but keeps cycles

def collapse_leaves_to_2core(G):
    """
    Repeatedly remove degree-1 vertices.
    Equivalent to taking the 2-core.

    This preserves the cycle structure of the graph.
    """
    return nx.k_core(G, k=2)


# Rule 3: noise added, then collapse
# topological simplication is evident
# run two steps in order
# noisy = attach_random_trees
# collapsed = collapse_leaves_to_2core

def attach_random_trees(G, num_trees=20, max_length=5, seed=0):
    """
    Attach dangling paths to random vertices.
    These are topological noise: they add vertices/edges but no cycles.
    """
    rng = random.Random(seed)
    H = G.copy()

    next_node = max(H.nodes) + 1 if all(isinstance(v, int) for v in H.nodes) else 0

    base_nodes = list(H.nodes)

    for _ in range(num_trees):
        root = rng.choice(base_nodes)
        length = rng.randint(1, max_length)

        prev = root
        for _ in range(length):
            while next_node in H:
                next_node += 1
            H.add_node(next_node)
            H.add_edge(prev, next_node)
            H.nodes[next_node]["noise"] = True
            prev = next_node
            next_node += 1

    return H


# Tracking of topological invariants

def graph_topology_summary(G, name="graph"):
    V = G.number_of_nodes()
    E = G.number_of_edges()
    c = nx.number_connected_components(G)
    beta1 = E - V + c

    is_planar = nx.check_planarity(G)[0]

    return {
        "name": name,
        "vertices": V,
        "edges": E,
        "components": c,
        "cycle_rank_beta1": beta1,
        "planar": is_planar,
    }


# plotting
def export_for_gephi(G, filename):
    H = G.copy()

    for v, data in H.nodes(data=True):
        bad_keys = [
            key for key, value in data.items()
            if isinstance(value, (tuple, list, dict, set))
        ]
        for key in bad_keys:
            del data[key]

    for u, v, data in H.edges(data=True):
        bad_keys = [
            key for key, value in data.items()
            if isinstance(value, (tuple, list, dict, set))
        ]
        for key in bad_keys:
            del data[key]

    nx.write_gexf(H, filename)


def main():
    base, pos = grid_with_holes()
    base, pos = relabel_with_xy(base, pos)

    thin = random_edge_thinning(base, p_remove=0.2, seed=1)
    noisy = attach_random_trees(base, num_trees=30, max_length=6, seed=2)
    collapsed = collapse_leaves_to_2core(noisy)

    for name, G in [
        ("base mesh with holes", base),
        ("randomly thinned mesh", thin),
        ("noisy mesh with dangling trees", noisy),
        ("collapsed 2-core", collapsed),
    ]:
        print(graph_topology_summary(G, name))

    export_for_gephi(base, "topology_base_mesh_with_holes.gexf")
    export_for_gephi(thin, "topology_randomly_thinned.gexf")
    export_for_gephi(noisy, "topology_noisy_with_trees.gexf")
    export_for_gephi(collapsed, "topology_collapsed_2core.gexf")


if __name__ == "__main__":
    main()
