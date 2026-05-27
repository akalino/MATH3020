import random
import statistics
from collections import Counter

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd


def graph_summary(G):
    return {
        "number_of_nodes": G.number_of_nodes(),
        "number_of_edges": G.number_of_edges(),
        "density": nx.density(G),
        "average_degree": average_degree(G),
        "max_degree": max_degree(G),
    }


def average_degree(G):
    if G.number_of_nodes() == 0:
        return 0
    return sum(dict(G.degree()).values()) / G.number_of_nodes()


def max_degree(G):
    if G.number_of_nodes() == 0:
        return 0
    return max(dict(G.degree()).values())


def degree_table(G):
    return sorted(G.degree(), key=lambda x: (-x[1], str(x[0])))


def top_k_degrees(G, k=10):
    rows = degree_table(G)[:k]
    return pd.DataFrame(rows, columns=["node", "degree"])


def degree_sequence(G, descending=True):
    seq = [d for _, d in G.degree()]
    return sorted(seq, reverse=descending)


def degree_histogram_data(G):
    counts = Counter(dict(G.degree()).values())
    return dict(sorted(counts.items()))


def degree_cdf_data(G):
    degrees = sorted([d for _, d in G.degree()])
    n = len(degrees)
    x = []
    y = []
    for i, d in enumerate(degrees, start=1):
        x.append(d)
        y.append(i / n)
    return x, y


def degree_ccdf_data(G):
    degrees = sorted([d for _, d in G.degree()])
    n = len(degrees)
    unique_degrees = sorted(set(degrees))
    x = []
    y = []
    for k in unique_degrees:
        count = sum(d >= k for d in degrees)
        x.append(k)
        y.append(count / n)
    return x, y


def plot_degree_histogram(G, title="Degree Histogram"):
    hist = degree_histogram_data(G)
    x = list(hist.keys())
    y = list(hist.values())
    plt.figure(figsize=(6, 4))
    plt.bar(x, y)
    plt.xlabel("Degree")
    plt.ylabel("Number of vertices")
    plt.title(title)
    plt.show()


def plot_degree_cdf(G, title="Degree CDF"):
    x, y = degree_cdf_data(G)
    plt.figure(figsize=(6, 4))
    plt.step(x, y, where="post")
    plt.xlabel("Degree")
    plt.ylabel("Proportion of vertices with degree <= k")
    plt.title(title)
    plt.show()


def plot_degree_ccdf(G, title="Degree CCDF"):
    x, y = degree_ccdf_data(G)
    plt.figure(figsize=(6, 4))
    plt.step(x, y, where="post")
    plt.xlabel("Degree")
    plt.ylabel("Proportion of vertices with degree >= k")
    plt.title(title)
    plt.show()


def plot_degree_ccdf_loglog(G, title="Degree CCDF (log-log)"):
    x, y = degree_ccdf_data(G)
    x2 = []
    y2 = []
    for a, b in zip(x, y):
        if a > 0 and b > 0:
            x2.append(a)
            y2.append(b)
    plt.figure(figsize=(6, 4))
    plt.loglog(x2, y2, marker="o", linestyle="none")
    plt.xlabel("Degree")
    plt.ylabel("Proportion of vertices with degree >= k")
    plt.title(title)
    plt.show()


def draw_graph(G, title="", seed=7, with_labels=False):
    plt.figure(figsize=(7, 6))
    pos = nx.spring_layout(G, seed=seed)
    nx.draw(G, pos, with_labels=with_labels, node_size=80 if not with_labels else 900)
    plt.title(title)
    plt.show()


def draw_graph_by_type(G, title="", seed=7):
    plt.figure(figsize=(7, 6))
    pos = nx.spring_layout(G, seed=seed)
    color_map = {"T": "tomato", "M": "skyblue", "C": "lightgreen", "CP": "gold"}
    node_colors = [color_map.get(G.nodes[v].get("type", ""), "lightgray") for v in G.nodes()]
    nx.draw(G, pos, with_labels=False, node_size=80, node_color=node_colors)
    plt.title(title)
    plt.show()


def draw_graph_sized_by_degree(G, title="", seed=7):
    plt.figure(figsize=(7, 6))
    pos = nx.spring_layout(G, seed=seed)
    sizes = [30 + 20 * d for _, d in G.degree()]
    nx.draw(G, pos, with_labels=False, node_size=sizes)
    plt.title(title)
    plt.show()


def sample_graph():
    G = nx.Graph()
    G.add_edges_from([
        ("A", "B"), ("A", "C"), ("A", "D"),
        ("B", "C"), ("B", "E"), ("C", "F"),
        ("D", "E"), ("D", "F"), ("E", "G"),
        ("F", "H"), ("G", "H"),
    ])
    return G


def path_graph(n):
    return nx.path_graph(n)


def cycle_graph(n):
    return nx.cycle_graph(n)


def star_graph(n):
    return nx.star_graph(n - 1)


def random_graph(n, m, seed=None):
    return nx.gnm_random_graph(n, m, seed=seed)


def hub_graph(n):
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for i in range(1, n):
        G.add_edge(0, i)
    for i in range(1, n - 1):
        G.add_edge(i, i + 1)
    return G


def karate_graph():
    return nx.karate_club_graph()


def bridge_graph():
    G = nx.Graph()
    left = [0, 1, 2, 3]
    right = [4, 5, 6, 7]
    for i in range(len(left)):
        for j in range(i + 1, len(left)):
            G.add_edge(left[i], left[j])
    for i in range(len(right)):
        for j in range(i + 1, len(right)):
            G.add_edge(right[i], right[j])
    G.add_edge(3, 4)
    return G


def hub_bridge_graph():
    G = nx.Graph()
    G.add_edges_from([
        ("H", "A1"), ("H", "A2"), ("H", "A3"), ("H", "A4"),
        ("A4", "B1"),
        ("B1", "B2"), ("B2", "B3"), ("B3", "B4"),
    ])
    return G


def degree_centrality_dict(G):
    return nx.degree_centrality(G)


def closeness_centrality_dict(G):
    return nx.closeness_centrality(G)


def betweenness_centrality_dict(G):
    return nx.betweenness_centrality(G)


def eigenvector_centrality_dict(G):
    return nx.eigenvector_centrality(G, max_iter=1000)


def pagerank_dict(G):
    return nx.pagerank(G)


def centrality_table(G):
    df = pd.DataFrame({
        "degree": degree_centrality_dict(G),
        "closeness": closeness_centrality_dict(G),
        "betweenness": betweenness_centrality_dict(G),
        "eigenvector": eigenvector_centrality_dict(G),
        "pagerank": pagerank_dict(G),
    })
    return df.sort_index()


def top_k_by_measure(G, measure="degree", k=5):
    table = centrality_table(G)
    return table.sort_values(by=measure, ascending=False).head(k)


def compare_rankings(G):
    table = centrality_table(G).copy()
    table["degree_rank"] = table["degree"].rank(ascending=False, method="min")
    table["closeness_rank"] = table["closeness"].rank(ascending=False, method="min")
    table["betweenness_rank"] = table["betweenness"].rank(ascending=False, method="min")
    table["eigenvector_rank"] = table["eigenvector"].rank(ascending=False, method="min")
    table["pagerank_rank"] = table["pagerank"].rank(ascending=False, method="min")
    return table.sort_values(
        by=["degree_rank", "closeness_rank", "betweenness_rank", "eigenvector_rank", "pagerank_rank"]
    )


def internet_as_graph(n, seed=None):
    return nx.random_internet_as_graph(n, seed=seed)


def er_graph(n, m, seed=None):
    return nx.gnm_random_graph(n, m, seed=seed)


def ba_graph(n, m, seed=None):
    return nx.barabasi_albert_graph(n, m, seed=seed)


def compare_basic_degree_stats(graphs, names):
    rows = []
    for G, name in zip(graphs, names):
        rows.append({
            "graph": name,
            "nodes": G.number_of_nodes(),
            "edges": G.number_of_edges(),
            "density": nx.density(G),
            "average_degree": average_degree(G),
            "max_degree": max_degree(G),
        })
    return pd.DataFrame(rows)


def node_type_table(G):
    rows = []
    for v, data in G.nodes(data=True):
        rows.append((v, data.get("type", None)))
    return pd.DataFrame(rows, columns=["node", "type"])


def type_counts(G):
    counts = {}
    for _, data in G.nodes(data=True):
        t = data.get("type", "unknown")
        counts[t] = counts.get(t, 0) + 1
    return pd.DataFrame([(k, v) for k, v in sorted(counts.items())], columns=["type", "count"])


def degree_gini(G):
    degrees = sorted([d for _, d in G.degree()])
    n = len(degrees)
    if n == 0:
        return 0
    total = sum(degrees)
    if total == 0:
        return 0
    weighted_sum = 0
    for i, x in enumerate(degrees, start=1):
        weighted_sum += i * x
    return (2 * weighted_sum) / (n * total) - (n + 1) / n


def top_fraction_degree_share(G, fraction=0.05):
    degrees = sorted([d for _, d in G.degree()], reverse=True)
    n = len(degrees)
    if n == 0:
        return 0
    k = max(1, int(round(fraction * n)))
    total = sum(degrees)
    if total == 0:
        return 0
    return sum(degrees[:k]) / total


def observed_hub_statistics(G):
    return {
        "max_degree": max_degree(G),
        "degree_gini": degree_gini(G),
        "top_5pct_degree_share": top_fraction_degree_share(G, fraction=0.05),
    }


def simulate_er_hub_statistics(n, m_edges, trials=200, seed=0):
    rng = random.Random(seed)
    rows = []
    for _ in range(trials):
        s = rng.randint(0, 10**9)
        G = nx.gnm_random_graph(n, m_edges, seed=s)
        rows.append(observed_hub_statistics(G))
    return pd.DataFrame(rows)


def simulate_ba_hub_statistics(n, m_param, trials=200, seed=0):
    rng = random.Random(seed)
    rows = []
    for _ in range(trials):
        s = rng.randint(0, 10**9)
        G = nx.barabasi_albert_graph(n, m_param, seed=s)
        rows.append(observed_hub_statistics(G))
    return pd.DataFrame(rows)


def empirical_p_value_upper(null_values, observed_value):
    values = list(null_values)
    count = sum(v >= observed_value for v in values)
    return (count + 1) / (len(values) + 1)


def plot_null_histogram(values, observed_value=None, xlabel="", title=""):
    plt.figure(figsize=(7, 4))
    plt.hist(values, bins=15)
    if observed_value is not None:
        plt.axvline(observed_value, color='red')
    plt.xlabel(xlabel)
    plt.ylabel("Frequency")
    plt.title(title)
    plt.show()


def summarize_null(values):
    vals = list(values)
    return {
        "mean": statistics.mean(vals),
        "median": statistics.median(vals),
        "min": min(vals),
        "max": max(vals),
        "stdev": statistics.stdev(vals) if len(vals) > 1 else 0,
    }


def export_for_gephi(G, path):
    nx.write_gexf(G, path)
    return path
