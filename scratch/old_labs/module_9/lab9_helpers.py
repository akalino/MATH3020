import matplotlib.pyplot as plt
import networkx as nx
from collections import Counter


def graph_summary(G):
    return {
        "number_of_nodes": G.number_of_nodes(),
        "number_of_edges": G.number_of_edges(),
        "nodes": list(G.nodes()),
        "edges": list(G.edges()),
        "degree_dict": dict(G.degree()),
    }


def sample_graph():
    G = nx.Graph()
    G.add_edges_from([
        ("A", "B"),
        ("A", "C"),
        ("A", "D"),
        ("B", "C"),
        ("B", "E"),
        ("C", "F"),
        ("D", "E"),
        ("D", "F"),
        ("E", "G"),
        ("F", "H"),
        ("G", "H"),
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


def degree_table(G):
    return sorted(G.degree(), key=lambda x: (-x[1], str(x[0])))


def degree_sequence(G, descending=True):
    seq = [d for _, d in G.degree()]
    return sorted(seq, reverse=descending)


def average_degree(G):
    if G.number_of_nodes() == 0:
        return 0
    return sum(dict(G.degree()).values()) / G.number_of_nodes()


def degree_histogram_data(G):
    counts = Counter(dict(G.degree()).values())
    return dict(sorted(counts.items()))


def plot_degree_histogram(G, title="Degree Histogram"):
    hist = degree_histogram_data(G)
    x = list(hist.keys())
    y = list(hist.values())

    plt.figure(figsize=(6, 4))
    plt.bar(x, y)
    plt.xlabel("Degree")
    plt.ylabel("Number of vertices")
    plt.title(title)
    plt.xticks(x)
    plt.show()


def degree_cdf_data(G):
    degrees = sorted([d for _, d in G.degree()])
    n = len(degrees)
    x = []
    y = []
    for i, d in enumerate(degrees, start=1):
        x.append(d)
        y.append(i / n)
    return x, y


def plot_degree_cdf(G, title="Degree CDF"):
    x, y = degree_cdf_data(G)
    plt.figure(figsize=(6, 4))
    plt.step(x, y, where="post")
    plt.xlabel("Degree")
    plt.ylabel("Proportion of vertices with degree ≤ k")
    plt.title(title)
    plt.show()


def draw_graph(G, title="", seed=7):
    plt.figure(figsize=(6, 5))
    pos = nx.spring_layout(G, seed=seed)
    nx.draw(G, pos, with_labels=True, node_size=900)
    plt.title(title)
    plt.show()


def export_for_gephi(G, path):
    nx.write_gexf(G, path)
    return path