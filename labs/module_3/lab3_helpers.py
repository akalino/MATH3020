import matplotlib.pyplot as plt
import networkx as nx


def graph_summary(G):
    return {
        "number_of_nodes": G.number_of_nodes(),
        "number_of_edges": G.number_of_edges(),
        "nodes": list(G.nodes()),
        "edges": list(G.edges()),
        "degree_dict": dict(G.degree()),
        "connected": nx.is_connected(G) if G.number_of_nodes() > 0 else False,
        "is_tree": nx.is_tree(G) if G.number_of_nodes() > 0 and nx.is_connected(G) else False,
    }


def draw_graph(G, title="", seed=7, with_labels=True):
    plt.figure(figsize=(7, 6))
    pos = nx.spring_layout(G, seed=seed)
    nx.draw(G, pos, with_labels=with_labels, node_size=900)
    plt.title(title)
    plt.show()


def build_graph(edges):
    G = nx.Graph()
    G.add_edges_from(edges)
    return G


def sample_distance_graph():
    edges = [
        ("A", "B"),
        ("B", "C"),
        ("C", "D"),
        ("D", "E"),
        ("C", "F"),
        ("F", "G"),
    ]
    return build_graph(edges)


def shortest_path_between(G, u, v):
    if nx.has_path(G, u, v):
        return nx.shortest_path(G, u, v)
    return None


def distance_between(G, u, v):
    if nx.has_path(G, u, v):
        return nx.shortest_path_length(G, u, v)
    return None


def all_pairs_distances(G):
    return {u: dict(lengths) for u, lengths in nx.all_pairs_shortest_path_length(G)}


def eccentricity_dict(G):
    return nx.eccentricity(G)


def graph_radius(G):
    return nx.radius(G)


def graph_diameter(G):
    return nx.diameter(G)


def graph_center(G):
    return nx.center(G)


def graph_periphery(G):
    return nx.periphery(G)


def generate_path_graph(n):
    return nx.path_graph(n)


def generate_star_graph(n):
    return nx.star_graph(n - 1)


def generate_random_tree(n, seed=None):
    return nx.random_tree(n, seed=seed)


def degree_table(G):
    return sorted(G.degree(), key=lambda x: (-x[1], str(x[0])))


def odd_degree_vertices(G):
    return sorted([v for v, d in G.degree() if d % 2 == 1], key=str)


def has_euler_trail(G):
    return nx.has_eulerian_path(G)


def has_euler_circuit(G):
    return nx.is_eulerian(G)


def get_euler_trail(G):
    if not nx.has_eulerian_path(G):
        return None
    return list(nx.eulerian_path(G))


def get_euler_circuit(G):
    if not nx.is_eulerian(G):
        return None
    return list(nx.eulerian_circuit(G))


def sample_euler_circuit_graph():
    return nx.cycle_graph(4)


def sample_euler_trail_graph():
    G = nx.path_graph(4)
    return G


def sample_non_eulerian_graph():
    G = nx.Graph()
    G.add_edges_from([
        ("A", "B"),
        ("A", "C"),
        ("A", "D"),
        ("B", "C"),
        ("C", "D"),
    ])
    return G


def is_hamilton_path(G, path):
    if len(path) != G.number_of_nodes():
        return False
    if len(set(path)) != len(path):
        return False
    return all(G.has_edge(path[i], path[i + 1]) for i in range(len(path) - 1))


def is_hamilton_cycle(G, cycle):
    if len(cycle) != G.number_of_nodes():
        return False
    if len(set(cycle)) != len(cycle):
        return False
    if not all(G.has_edge(cycle[i], cycle[i + 1]) for i in range(len(cycle) - 1)):
        return False
    return G.has_edge(cycle[-1], cycle[0])


def find_hamilton_path_bruteforce(G):
    from itertools import permutations
    nodes = list(G.nodes())
    for perm in permutations(nodes):
        if is_hamilton_path(G, list(perm)):
            return list(perm)
    return None


def find_hamilton_cycle_bruteforce(G):
    from itertools import permutations
    nodes = list(G.nodes())
    if not nodes:
        return None
    start = nodes[0]
    rest = [v for v in nodes if v != start]
    for perm in permutations(rest):
        cycle = [start] + list(perm)
        if is_hamilton_cycle(G, cycle):
            return cycle
    return None


def sample_hamiltonian_graph():
    G = nx.cycle_graph(5)
    return G


def sample_euler_but_not_hamilton_graph():
    G = nx.Graph()
    G.add_edges_from([
        ("A", "B"),
        ("B", "C"),
        ("C", "A"),
        ("C", "D"),
        ("D", "E"),
        ("E", "C"),
    ])
    return G


def sample_tree_edges():
    return [
        ("A", "B"),
        ("A", "C"),
        ("B", "D"),
        ("B", "E"),
        ("C", "F"),
        ("F", "G"),
    ]


def is_connected(G):
    return nx.is_connected(G)


def has_cycle(G):
    return not nx.is_forest(G)


def is_tree_by_definition(G):
    if G.number_of_nodes() == 0:
        return False
    return nx.is_connected(G) and nx.is_forest(G)


def leaves(G):
    return sorted([node for node, deg in G.degree() if deg == 1], key=str)


def unique_path_between(G, source, target):
    if not nx.has_path(G, source, target):
        return None
    return nx.shortest_path(G, source=source, target=target)


def remove_edge_and_analyze(G, u, v):
    H = G.copy()
    H.remove_edge(u, v)
    return {
        "connected": nx.is_connected(H) if H.number_of_nodes() > 0 else False,
        "components": [sorted(c) for c in nx.connected_components(H)] if H.number_of_nodes() > 0 else [],
        "is_tree": nx.is_tree(H) if H.number_of_nodes() > 0 and nx.is_connected(H) else False,
        "edges": list(H.edges()),
    }


def add_edge_and_analyze(G, u, v):
    H = G.copy()
    H.add_edge(u, v)
    return {
        "connected": nx.is_connected(H),
        "is_tree": nx.is_tree(H) if nx.is_connected(H) else False,
        "cycle_basis": nx.cycle_basis(H),
        "edges": list(H.edges()),
    }


def sample_connected_graph_with_cycles():
    G = nx.Graph()
    G.add_edges_from([
        ("A", "B"),
        ("B", "C"),
        ("C", "D"),
        ("D", "A"),
        ("A", "C"),
        ("C", "E"),
        ("E", "F"),
    ])
    return G


def spanning_tree_of_graph(G):
    return nx.minimum_spanning_tree(G)
