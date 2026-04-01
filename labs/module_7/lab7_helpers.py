import matplotlib.pyplot as plt
import networkx as nx


def graph_summary(G):
    return {
        "number_of_nodes": G.number_of_nodes(),
        "number_of_edges": G.number_of_edges(),
        "nodes": list(G.nodes()),
        "edges": list(G.edges()),
        "degree_dict": dict(G.degree()),
    }


def cycle_graph(n):
    return nx.cycle_graph(n)


def wheel_graph(n):
    return nx.wheel_graph(n)


def complete_graph(n):
    return nx.complete_graph(n)


def complete_bipartite_graph(m, n):
    G = nx.complete_bipartite_graph(m, n)
    for v in range(m):
        G.nodes[v]["part"] = "left"
        G.nodes[v]["highlight"] = 1
    for v in range(m, m + n):
        G.nodes[v]["part"] = "right"
        G.nodes[v]["highlight"] = 1
    return G


def draw_graph(G, title="", seed=7):
    plt.figure(figsize=(6, 5))
    pos = nx.spring_layout(G, seed=seed)
    nx.draw(G, pos, with_labels=True, node_size=900)
    plt.title(title)
    plt.show()


def draw_graph_spring(G, title="", seed=7):
    plt.figure(figsize=(6, 5))
    pos = nx.spring_layout(G, seed=seed)
    nx.draw(G, pos, with_labels=True, node_size=900)
    plt.title(title)
    plt.show()


def draw_graph_circular(G, title=""):
    plt.figure(figsize=(6, 5))
    pos = nx.circular_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=900)
    plt.title(title)
    plt.show()


def draw_graph_with_highlight(G, title="", seed=7):
    plt.figure(figsize=(6, 5))
    pos = nx.spring_layout(G, seed=seed)
    node_colors = []
    for v in G.nodes():
        if G.nodes[v].get("highlight", 0) == 1:
            node_colors.append("tomato")
        elif G.nodes[v].get("part", "") == "left":
            node_colors.append("skyblue")
        elif G.nodes[v].get("part", "") == "right":
            node_colors.append("lightgreen")
        else:
            node_colors.append("lightgray")
    nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=900)
    plt.title(title)
    plt.show()


def check_planarity_report(G):
    is_planar, embedding = nx.check_planarity(G)
    return {
        "is_planar": is_planar,
        "number_of_nodes": G.number_of_nodes(),
        "number_of_edges": G.number_of_edges(),
    }


def edge_bound_report(G):
    v = G.number_of_nodes()
    e = G.number_of_edges()
    bound = 3 * v - 6 if v >= 3 else None
    return {
        "v": v,
        "e": e,
        "bound_3v_minus_6": bound,
        "satisfies_bound": (e <= bound) if bound is not None else None,
    }


def planted_k5_graph():
    G = nx.Graph()
    core = [0, 1, 2, 3, 4]
    for v in core:
        G.add_node(v, highlight=1)
    for i in range(len(core)):
        for j in range(i + 1, len(core)):
            G.add_edge(core[i], core[j], highlight=1)

    extras = [5, 6, 7, 8]
    for v in extras:
        G.add_node(v, highlight=0)

    G.add_edges_from([
        (0, 5),
        (1, 5),
        (2, 6),
        (3, 7),
        (4, 8),
        (5, 6),
        (6, 7),
        (7, 8),
    ])

    return G


def planted_k33_graph():
    G = nx.Graph()
    left = [0, 1, 2]
    right = [3, 4, 5]

    for v in left:
        G.add_node(v, highlight=1, part="left")
    for v in right:
        G.add_node(v, highlight=1, part="right")

    for u in left:
        for v in right:
            G.add_edge(u, v, highlight=1)

    extras = [6, 7, 8]
    for v in extras:
        G.add_node(v, highlight=0)

    G.add_edges_from([
        (0, 6),
        (1, 6),
        (2, 7),
        (3, 7),
        (4, 8),
        (5, 8),
        (6, 8),
    ])

    return G


def subdivide_edge(G, u, v, new_node):
    H = G.copy()
    if H.has_edge(u, v):
        attrs = H.edges[u, v]
        H.remove_edge(u, v)
        H.add_node(new_node)
        H.add_edge(u, new_node, **attrs)
        H.add_edge(new_node, v, **attrs)
    return H


def subdivided_k33():
    G = complete_bipartite_graph(3, 3)
    H = subdivide_edge(G, 0, 3, 6)
    H.nodes[6]["highlight"] = 1
    H = subdivide_edge(H, 1, 4, 7)
    H.nodes[7]["highlight"] = 1
    return H


def export_for_gephi(G, path):
    nx.write_gexf(G, path)
    return path