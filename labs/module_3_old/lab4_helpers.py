import random
import networkx as nx
import matplotlib.pyplot as plt


def sample_tree_edges():
    return [
        ("A", "B"),
        ("A", "C"),
        ("B", "D"),
        ("B", "E"),
        ("C", "F"),
        ("F", "G"),
    ]


def build_graph(edges):
    G = nx.Graph()
    G.add_edges_from(edges)
    return G


def draw_graph(G, seed=7):
    pos = nx.spring_layout(G, seed=seed)
    nx.draw(G, pos, with_labels=True, node_size=1200)
    plt.show()


def graph_summary(G):
    return {
        "number_of_nodes": G.number_of_nodes(),
        "number_of_edges": G.number_of_edges(),
        "connected": nx.is_connected(G),
        "is_tree": nx.is_tree(G),
        "degree_dict": dict(G.degree()),
    }


def leaves(G):
    return sorted([v for v, d in G.degree() if d == 1], key=str)


def unique_path(G, u, v):
    if nx.has_path(G, u, v):
        return nx.shortest_path(G, u, v)
    return None


def remove_edge_and_analyze(G, u, v):
    H = G.copy()
    H.remove_edge(u, v)
    return {
        "connected": nx.is_connected(H) if H.number_of_nodes() > 0 else False,
        "components": [sorted(c) for c in nx.connected_components(H)],
        "is_tree": nx.is_tree(H) if H.number_of_nodes() > 0 else False,
        "edges": list(H.edges()),
    }


def add_edge_and_analyze(G, u, v):
    H = G.copy()
    H.add_edge(u, v)
    return {
        "connected": nx.is_connected(H),
        "is_tree": nx.is_tree(H),
        "cycle_basis": nx.cycle_basis(H),
        "edges": list(H.edges()),
    }


def generate_random_tree(n, seed=None):
    return nx.random_labeled_tree(n, seed=seed)


def add_random_nonedge(G, seed=None):
    rng = random.Random(seed)
    H = G.copy()
    nodes = list(H.nodes())

    nonedges = [
        (u, v)
        for i, u in enumerate(nodes)
        for v in nodes[i + 1 :]
        if not H.has_edge(u, v)
    ]

    if not nonedges:
        return H, None

    u, v = rng.choice(nonedges)
    H.add_edge(u, v)
    return H, (u, v)


def remove_random_edge(G, seed=None):
    rng = random.Random(seed)
    H = G.copy()
    edges = list(H.edges())

    if not edges:
        return H, None

    e = rng.choice(edges)
    H.remove_edge(*e)
    return H, e


def export_for_gephi(G, path):
    nx.write_gexf(G, path)
    return path