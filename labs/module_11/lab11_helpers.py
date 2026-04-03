import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd


def graph_summary(G):
    return {
        "number_of_nodes": G.number_of_nodes(),
        "number_of_edges": G.number_of_edges(),
        "nodes": list(G.nodes()),
        "edges": list(G.edges()),
        "degree_dict": dict(G.degree()),
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


def export_for_gephi(G, path):
    nx.write_gexf(G, path)
    return path