import matplotlib.pyplot as plt
import networkx as nx
import random
import statistics
from collections import Counter
import pandas as pd


def graph_summary(G):
    return {
        "number_of_nodes": G.number_of_nodes(),
        "number_of_edges": G.number_of_edges(),
        "density": nx.density(G),
        "connected": nx.is_connected(G) if not G.is_directed() else None,
    }


def draw_graph(G, title="", seed=7):
    plt.figure(figsize=(6, 5))
    pos = nx.spring_layout(G, seed=seed)
    nx.draw(G, pos, with_labels=True, node_size=900)
    plt.title(title)
    plt.show()


def random_graph_gnm(n, m, seed=None):
    return nx.gnm_random_graph(n, m, seed=seed)


def random_graph_gnp(n, p, seed=None):
    return nx.gnp_random_graph(n, p, seed=seed)


def karate_graph():
    return nx.karate_club_graph()


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


def export_for_gephi(G, path):
    nx.write_gexf(G, path)
    return path