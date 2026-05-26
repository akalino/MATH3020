# Planarity, topology, and discrete Morse theory

### Mathematical ideas

- Planar graph faces

In a planar embedding, cycles can bound faces.
Here, holes are not just "empty space"; they are bounded regions.

Euler's formula gives us a way of counting faces: $V - E + F = 1 +c$, where we introduce $c$ as the number of connected components.
Re-arranging, we see that the total faces (including the outside face) are $F_{\text{total}} = E - V + c +1$.
Using this formula tells us how many bounded faces there are, but cannot distinguish between faces of tiny cells in the mesh versus large, meaningful holes. 

- Counting cycles

Given a graph, we may wish to count how many cycles are in the graph.
This can also be viewed through the lens of topology, or the mathematical study of spaces and shapes that are preserved under continuous deformations.
In topology and **homology**, a measure that is preserved is called an **invariant**, and we have seen several of these related to graphs (where a graph isomorphism does not change the measure in question).
A family of these that is well-studied are the Betti numbers; for a graph, the first Betti number is $\beta_1 = E - V + c$.
This is the number of independent cycles in a graph.
We are here relating this to a graph, but it is also said to describe a one-dimensional homology count.

In a dense mesh like the ones we are visualizing, we will then count many tiny triangular or square cells, missing on capturing the larger holes we are looking for.
This motivates other approaches like persistent homology, where we can look at the underlying space at many different resolutions, but beyond the scope of this work.

- Collapses

We cal also "clean up" the graph by removing vertices that don't provide the information we care about.
An example would be removing a dangling vertex and it's incident edge, since we know this isn't providing us with any extra information.
We can do this repeatedly without losing any of the core structure we care about since we are not changing any of the graph's cycles.
This makes approaches more computationally feasible and can be accomplished using the ```nx.k_core``` function.
Here, we will care about the case when $k=2$ (the 2-core) which removes leaves and trees that are topologically noise, but preserving the cycles.
These types of simplifications are described in discrete Morse theory, another tangential branch of mathematics.

### Adding defects to a square mesh

To aid our visualizations, we will start with a simple planar graph: the square mesh.
We will "poke" three holes in the mesh to represent a round(ish) hole, a long, skinny hole, a small isolated defect, and a bite out of the boundary.
These four cases will allow us to compare their influence on the number of edges, vertices, components, and our $\beta_1$ count of cycles.

We can then compute this same set of metrics using some simplification rules.

The first, and most harmful, will be a **random thinning** of the edges of the graph.
It can preserve how the graph may look when zoomed out, but can destroy cycles and connectivity.

The second will be the 2-core concept, where we will keep the cycles that are relevant.

The third will be a process for adding noise to the graph by adding some random trees.
We can then use this to compare the graph with these new trees, and the later 2-core removal of them.

### Observing invariants

We will then compute the aforementioned invariants.
What will find is that 

```
Noisy graph:
    many more vertices and edges
    same beta_1 as original

Collapsed 2-core:
    fewer vertices and edges
    beta_1 returns to original

Random thinning:
    beta_1 often changes
    components may increase
```

### Visual conjectures

Think through the following questions and see what is happening in this process:

```angular2html
1. Which simplification preserves the large visible holes?
2. Which simplification changes the number of connected components?
3. Does removing many vertices necessarily change the topology?
4. Does preserving the rough shape of a graph preserve its cycles?
5. Can two graphs look similar in Gephi but have different beta_1?
6. Can two graphs look different but have the same beta_1?
7. What kind of deletion is “topologically safe”?
```

### A central theorem

Through this experiment, we can pose a theorem: Removing a degree-1 vertex and its incident edge preserves $\beta_1 = E - V + c$.
