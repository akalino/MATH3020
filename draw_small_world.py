import argparse

import networkx as nx
import matplotlib.pyplot as plt

def create_small_world(_n, _d, _p):
    """
    Create a small world graph.
    :param _n: Number of nodes.
    :param _d: Average degree of graph.
    :param _p: Edge rewiring probability.
    :return: None, saves the graph drawing.
    """
    _G = nx.watts_strogatz_graph(_n ,_d, _p)

    # Draw the graph
    plt.figure(figsize=(6, 6))
    plt.title("Watts-Strogatz Small World)")
    pos = nx.spring_layout(_G, seed=42)
    nx.draw_networkx_nodes(_G, pos)
    nx.draw_networkx_edges(_G, pos, width=1.0, alpha=0.5)
    plt.axis("off")
    plt.savefig('images/small_world_{}_{}_{}.png'.format(_n, _d, _p))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--nodes", default=1, type=int, help="Number of nodes.")
    parser.add_argument("-d", "--degree", default=1, type=int, help="Average degree of graph.")
    parser.add_argument("-p", "--probability", default=1, type=float, help="Edge rewiring probability.")
    args = parser.parse_args()
    create_small_world(args.nodes, args.degree, args.probability)
