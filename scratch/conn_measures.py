import random

import networkx as nx
import matplotlib.pyplot as plt


def single_degree_centrality(_seed):
    """
    Creates network with one node of high degree centrality.
    :param _seed: Pre-defined random seed.
    :return: NetworkX graph, _G.
    """
    n = 250
    k = 6
    p = 0.1
    _G = nx.watts_strogatz_graph(n, k, p, _seed)

    # Create hub
    hub = 0
    trg_frac = 0.85
    trg_deg = int(trg_frac * (n-1))

    # Connect hub
    candidates = [v for v in _G.nodes if v!=hub and not _G.has_edge(hub, v)]
    random.shuffle(candidates)
    _add = candidates[:max(0, trg_deg - _G.degree(hub))]
    _G.add_edges_from((hub, v) for v in _add)

    return _G


def single_betweenness_centrality(_seed):
    """
    Creates network with one node of high betweenness centrality.
    :param _seed: Pre-defined random seed.
    :return: NetworkX graph, _G.
    """
    size_comm1 = 120
    size_comm2 = 250 - size_comm1

    comm1 = nx.erdos_renyi_graph(size_comm1, p=0.1, seed=_seed)
    comm2 = nx.erdos_renyi_graph(size_comm2, p=0.1, seed=_seed+1)

    # Re-label for merging
    comm1 = nx.relabel_nodes(comm1, lambda x: x+1)
    comm2 = nx.relabel_nodes(comm2, lambda x: x+1+size_comm1)

    # Link communities by central hub
    hub = 0
    _h = nx.Graph()
    _h.add_node(hub)

    # Combine the three graphs
    _G = nx.compose_all([_h, comm1, comm2])
    num_links = 15
    for trg in random.sample(list(comm1.nodes()), num_links):
        _G.add_edge(hub, trg)
    for trg in random.sample(list(comm2.nodes()), num_links):
        _G.add_edge(hub, trg)
    return _G


def export_gephi(_G, _lab):
    """
    Exports a graph to Gephi format.
    :param _G: Input graph.
    :param _lab: Label of graph.
    :return: None, outputs to gephi_files path.
    """
    nx.write_gexf(_G, "gephi_files/{}.gexf".format(_lab))


if __name__ == '__main__':
    export_gephi(single_betweenness_centrality(17), 'betweenness')
    export_gephi(single_degree_centrality(17), 'centrality')
