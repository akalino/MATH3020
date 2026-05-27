import random
import statistics

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
        node_size=500 if with_labels else 120,
        node_color=node_colors,
    )
    plt.title(title)
    plt.show()


def draw_graph_colored_by_partition(G, communities, title="", seed=7, with_labels=True):
    plt.figure(figsize=(7, 6))
    pos = nx.spring_layout(G, seed=seed)
    node_to_group = {}
    for i, comm in enumerate(communities):
        for v in comm:
            node_to_group[v] = i
    colors = [node_to_group.get(v, -1) for v in G.nodes()]
    nx.draw(
        G,
        pos,
        with_labels=with_labels,
        node_color=colors,
        node_size=500 if with_labels else 120,
        cmap=plt.cm.Set3,
    )
    plt.title(title)
    plt.show()


def path_graph(n):
    return nx.path_graph(n)


def cycle_graph(n):
    return nx.cycle_graph(n)


def star_graph(n):
    return nx.star_graph(n - 1)


def random_graph(n, m, seed=None):
    return nx.gnm_random_graph(n, m, seed=seed)


def random_graph_gnm(n, m, seed=None):
    return nx.gnm_random_graph(n, m, seed=seed)


def random_graph_gnp(n, p, seed=None):
    return nx.gnp_random_graph(n, p, seed=seed)


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


def largest_component_subgraph(G):
    if G.number_of_nodes() == 0:
        return G.copy()
    if nx.is_connected(G):
        return G.copy()
    largest = max(nx.connected_components(G), key=len)
    return G.subgraph(largest).copy()


def average_degree(G):
    if G.number_of_nodes() == 0:
        return 0
    return sum(dict(G.degree()).values()) / G.number_of_nodes()


def average_path_length_safe(G):
    H = largest_component_subgraph(G)
    if H.number_of_nodes() < 2:
        return 0
    return nx.average_shortest_path_length(H)


def clustering_coefficient(G):
    return nx.average_clustering(G)


def transitivity_value(G):
    return nx.transitivity(G)


def connected_components_count(G):
    return nx.number_connected_components(G)


def graph_metrics(G):
    H = largest_component_subgraph(G)
    return {
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "connected_components": connected_components_count(G),
        "largest_component_size": H.number_of_nodes(),
        "average_degree": average_degree(G),
        "average_path_length": average_path_length_safe(G),
        "average_clustering": clustering_coefficient(G),
        "transitivity": transitivity_value(G),
        "density": nx.density(G),
    }


def er_graph_matching_observed(G, seed=None):
    return nx.gnm_random_graph(G.number_of_nodes(), G.number_of_edges(), seed=seed)


def simulate_matching_observed(G, trials=100, seed=0):
    rng = random.Random(seed)
    rows = []
    for _ in range(trials):
        s = rng.randint(0, 10**9)
        H = er_graph_matching_observed(G, seed=s)
        rows.append(graph_metrics(H))
    return pd.DataFrame(rows)


def simulate_gnp_metrics(n, p, trials=100, seed=0):
    rng = random.Random(seed)
    rows = []
    for _ in range(trials):
        s = rng.randint(0, 10**9)
        G = nx.gnp_random_graph(n, p, seed=s)
        rows.append(graph_metrics(G))
    return pd.DataFrame(rows)


def summarize_metric(df, column):
    values = list(df[column])
    return {
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "min": min(values),
        "max": max(values),
        "stdev": statistics.stdev(values) if len(values) > 1 else 0,
    }


def empirical_p_value_upper(null_values, observed_value):
    values = list(null_values)
    count = sum(v >= observed_value for v in values)
    return (count + 1) / (len(values) + 1)


def empirical_p_value_lower(null_values, observed_value):
    values = list(null_values)
    count = sum(v <= observed_value for v in values)
    return (count + 1) / (len(values) + 1)


def empirical_p_value_two_sided(null_values, observed_value):
    values = list(null_values)
    center = statistics.mean(values)
    observed_distance = abs(observed_value - center)
    count = sum(abs(v - center) >= observed_distance for v in values)
    return (count + 1) / (len(values) + 1)


def plot_metric_histogram(values, observed_value=None, xlabel="", title=""):
    plt.figure(figsize=(7, 4))
    plt.hist(values, bins=15)
    if observed_value is not None:
        plt.axvline(observed_value, color="red")
    plt.xlabel(xlabel)
    plt.ylabel("Frequency")
    plt.title(title)
    plt.show()


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


def capstone_workflow_summary(G, trials=200, seed=0):
    observed = graph_metrics(G)
    null_df = simulate_matching_observed(G, trials=trials, seed=seed)
    communities = detect_communities_greedy(G)
    return {
        "observed_metrics": observed,
        "null_summary_clustering": summarize_metric(null_df, "average_clustering"),
        "null_summary_path_length": summarize_metric(null_df, "average_path_length"),
        "p_value_clustering_upper": empirical_p_value_upper(null_df["average_clustering"], observed["average_clustering"]),
        "p_value_path_two_sided": empirical_p_value_two_sided(null_df["average_path_length"], observed["average_path_length"]),
        "number_of_communities": len(communities),
        "modularity": modularity_score(G, communities),
    }


def export_for_gephi(G, path):
    nx.write_gexf(G, path)
    return path
