import matplotlib.pyplot as plt
import networkx as nx
import random
import statistics


def graph_summary(G):
    return {
        "number_of_nodes": G.number_of_nodes(),
        "number_of_edges": G.number_of_edges(),
        "connected": nx.is_connected(G) if not G.is_directed() else None,
        "density": nx.density(G),
    }


def draw_graph(G, title="", seed=7):
    plt.figure(figsize=(6, 5))
    pos = nx.spring_layout(G, seed=seed)
    nx.draw(G, pos, with_labels=True, node_size=900)
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


def karate_graph():
    return nx.karate_club_graph()


def largest_component_subgraph(G):
    if nx.is_connected(G):
        return G.copy()
    components = list(nx.connected_components(G))
    largest = max(components, key=len)
    return G.subgraph(largest).copy()


def average_path_length_safe(G):
    H = largest_component_subgraph(G)
    if H.number_of_nodes() < 2:
        return 0
    return nx.average_shortest_path_length(H)


def clustering_coefficient(G):
    return nx.average_clustering(G)


def transitivity_value(G):
    return nx.transitivity(G)


def graph_metrics(G):
    H = largest_component_subgraph(G)
    return {
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "largest_component_nodes": H.number_of_nodes(),
        "average_path_length": average_path_length_safe(G),
        "average_clustering": clustering_coefficient(G),
        "transitivity": transitivity_value(G),
        "density": nx.density(G),
    }


def er_graph_matching_observed(G, seed=None):
    n = G.number_of_nodes()
    m = G.number_of_edges()
    return nx.gnm_random_graph(n, m, seed=seed)


def simulate_er_metrics(G, trials=20, seed=0):
    rng = random.Random(seed)
    rows = []

    for _ in range(trials):
        s = rng.randint(0, 10**9)
        H = er_graph_matching_observed(G, seed=s)
        rows.append(graph_metrics(H))

    return rows


def extract_metric(sim_rows, key):
    return [row[key] for row in sim_rows]


def compare_observed_to_simulation(G, trials=20, seed=0):
    observed = graph_metrics(G)
    sims = simulate_er_metrics(G, trials=trials, seed=seed)

    return {
        "observed": observed,
        "simulated_path_lengths": extract_metric(sims, "average_path_length"),
        "simulated_clusterings": extract_metric(sims, "average_clustering"),
        "simulated_transitivity": extract_metric(sims, "transitivity"),
    }


def summarize_simulation(values):
    return {
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "min": min(values),
        "max": max(values),
        "stdev": statistics.stdev(values) if len(values) > 1 else 0,
    }


def plot_metric_comparison(sim_values, observed_value, xlabel="", title=""):
    plt.figure(figsize=(7, 4))
    plt.hist(sim_values, bins=10)
    plt.axvline(observed_value, color='red')
    plt.xlabel(xlabel)
    plt.ylabel("Frequency")
    plt.title(title)
    plt.show()


def export_for_gephi(G, path):
    nx.write_gexf(G, path)
    return path