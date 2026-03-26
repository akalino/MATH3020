import networkx as nx
import matplotlib.pyplot as plt

def generate_graph():
    # Generates graph as in Figure 4.12
    _G = nx.Graph()
    _G.add_nodes_from([1,2,3,4,5,6,7,8])
    _G.add_edges_from([
        (1,2), (1,5), (1,6),
        (2,3), (2,4), (2,8), (2,5),
        (3,4), (3,7), (3,8),
        (4,5), (4,6), (4,7),
        (5, 6),
        (6, 7), (6,8),
        (7, 8)]
    )
    return _G

if __name__ == '__main__':
    G = generate_graph()
    sol = nx.check_planarity(G)
    if sol[0]:
        nx.draw(G, pos=nx.planar_layout(G), with_labels=True)
        plt.show()
    else:
        print('Not planar')