import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from networkx.algorithms.community import greedy_modularity_communities, modularity


def graph_summary(G):
    return {
        "number_of_nodes": G.number_of_nodes(),
        "number_of_edges": G.number_of_edges(),
        "density": nx.density(G),
        "connected": nx.is_connected(G) if not G.is_directed() else None,
    }


def draw_graph(G, title="", seed=7, with_labels=True, color_attribute=None):
    plt.figure(figsize=(7, 6))
    pos = nx.spring_layout(G, seed=seed)

    if color_attribute is None:
        node_colors = "lightgray"
    else:
        palette = {
            "red": "tomato",
            "blue": "skyblue",
            "left": "lightgreen",
            "right": "gold",
        }
        node_colors = [
            palette.get(G.nodes[v].get(color_attribute, None), "lightgray")
            for v in G.nodes()
        ]

    nx.draw(
        G,
        pos,
        with_labels=with_labels,
        node_size=500,
        node_color=node_colors,
    )
    plt.title(title)
    plt.show()


def draw_graph_colored_by_partition(G, communities, title="", seed=7):
    plt.figure(figsize=(7, 6))
    pos = nx.spring_layout(G, seed=seed)

    node_to_group = {}
    for i, comm in enumerate(communities):
        for v in comm:
            node_to_group[v] = i

    colors = [node_to_group.get(v, -1) for v in G.nodes()]
    nx.draw(G, pos, with_labels=True, node_color=colors, node_size=500, cmap=plt.cm.Set3)
    plt.title(title)
    plt.show()


def complete_graph(n):
    return nx.complete_graph(n)


def random_graph(n, m, seed=None):
    return nx.gnm_random_graph(n, m, seed=seed)


def karate_graph():
    return nx.karate_club_graph()


def planted_two_group_graph():
    G = nx.Graph()

    left = [f"L{i}" for i in range(1, 7)]
    right = [f"R{i}" for i in range(1, 7)]

    for v in left:
        G.add_node(v, group="left")
    for v in right:
        G.add_node(v, group="right")

    for i in range(len(left)):
        for j in range(i + 1, len(left)):
            G.add_edge(left[i], left[j])

    for i in range(len(right)):
        for j in range(i + 1, len(right)):
            G.add_edge(right[i], right[j])

    G.add_edge("L1", "R1")
    G.add_edge("L2", "R2")

    return G


def weak_two_group_graph():
    G = nx.Graph()

    left = [f"L{i}" for i in range(1, 7)]
    right = [f"R{i}" for i in range(1, 7)]

    for v in left:
        G.add_node(v, group="left")
    for v in right:
        G.add_node(v, group="right")

    for i in range(len(left) - 1):
        G.add_edge(left[i], left[i + 1])

    for i in range(len(right) - 1):
        G.add_edge(right[i], right[i + 1])

    G.add_edge("L3", "R3")
    G.add_edge("L4", "R4")
    G.add_edge("L5", "R5")

    return G


def labeled_homophily_graph():
    G = nx.Graph()

    red_nodes = [f"R{i}" for i in range(1, 6)]
    blue_nodes = [f"B{i}" for i in range(1, 6)]

    for v in red_nodes:
        G.add_node(v, color_group="red")
    for v in blue_nodes:
        G.add_node(v, color_group="blue")

    red_edges = [("R1", "R2"), ("R1", "R3"), ("R2", "R4"), ("R3", "R5"), ("R4", "R5")]
    blue_edges = [("B1", "B2"), ("B1", "B3"), ("B2", "B4"), ("B3", "B5"), ("B4", "B5")]
    cross_edges = [("R1", "B1"), ("R3", "B3")]

    G.add_edges_from(red_edges + blue_edges + cross_edges)

    return G


def detect_communities_greedy(G):
    communities = list(greedy_modularity_communities(G))
    return [sorted(list(c), key=str) for c in communities]


def modularity_score(G, communities):
    communities_as_sets = [set(c) for c in communities]
    return modularity(G, communities_as_sets)


def partition_table(communities):
    rows = []
    for i, comm in enumerate(communities):
        for v in comm:
            rows.append((v, i))
    return pd.DataFrame(rows, columns=["node", "community"]).sort_values(by=["community", "node"])


def community_size_table(communities):
    rows = []
    for i, comm in enumerate(communities):
        rows.append((i, len(comm)))
    return pd.DataFrame(rows, columns=["community", "size"])


def attribute_mixing_table(G, attribute):
    rows = []
    for u, v in G.edges():
        a = G.nodes[u].get(attribute, None)
        b = G.nodes[v].get(attribute, None)
        rows.append((a, b))
    return pd.DataFrame(rows, columns=[f"{attribute}_u", f"{attribute}_v"])


def attribute_assortativity(G, attribute):
    return nx.attribute_assortativity_coefficient(G, attribute)


def degree_assortativity(G):
    return nx.degree_assortativity_coefficient(G)


def export_for_gephi(G, path):
    nx.write_gexf(G, path)
    return path