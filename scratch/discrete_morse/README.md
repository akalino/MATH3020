# Discrete Morse cancellations

### From graphs to cell complexes

In our prior work, we only considered 1-dimensional objects from the graph: its vertices and edges.
What if we took this one step further?

We can start to do this by also considering the set of faces as 2-dimensional objects of study (and could continue to generalize to n-dimensional faces).
We will define a 2D **cell complex** as the set of vertices, the set of edges, and a selection of the filled faces (we'll color these in when visualizing).

Just like last time, we will consider cases where we can "cancel out" pieces of the cell complex (upgrading out nomenclature from graph to cell complex) while still retaining the overall **invariants**.
Since we're now dealing with a cell complex, we can consider both vertex-edge cancellations and edge-face cancellations.
In the latter, the 2D topological visualizations become more interesting.

### Peeling a 2D mesh

We will start with both square and triangular meshes with holes, where each cell will be a filled triangle or square.
We will then run a collapse rule where if an edge belonds to exactly one face, pair that boundary edge with the face and delete both.
The goal is to show how collapses of these types get "stuck" around the holes.


### Application to nonplanar graphs

Discrete Morse theory works for us even if our graph is nonplanar.
But, when we consider the fundamental $K_5, K_{3,3}$, we find
```angular2html
K_5 has no degree-1 vertices.
K_3,3 has no degree-1 vertices.
Dense random graphs often have no leaves.
```
Dense nonplanar graphs often have no obvious collapsible leaf structure, so graph-only Morse cancellation reveals a robust core.

The issue comes down to how we are visualizing. 
In a 1-dimensional graph, $K_5$ has crossings.
But now project the same graph into 2-dimensional space.
All of a sudden, that extra degree of choice in how we draw the graph does allow us to draw without crossings!
We can then create something that looks like a 5-sided die without the interior filled in (note: this is not a fair die to play with).

In 2-dimensions, our objects are now cell complexes.
We can build what is called a **clique complex** of any graph $G$, so it does not matter if our original graph was planar or nonplanar, it still maths out.
For example:

```angular2html
K_5:
    graph is nonplanar
    clique complex has many filled triangles
    topologically resembles the 2-skeleton of a 4-simplex

K_3,3:
    graph is nonplanar
    no triangles
    clique complex is just the graph
    only graph-level cancellations are possible

random geometric graph:
    may have many triangles
    clique complex has meaningful 2D structure

Barabási-Albert graph:
    may have triangles depending on parameters
    clique complex can be sparse or clustered
```

However, not every complex has obvious elementary collapses.
Discrete Morse theory often requires a more subtle matching, not just greedy collapsing of faces.

We can now run some experiments. 
We will see two examples: (A) $K_5$ with a "dangling" tree, and (B) $K_{3,3}$ with added trees.

In (A), we will find that Morse cancellations remove topological and combinatorial noise but don't "magically" planarize the graph.
In (B), we will find that leaf cancellations preserve the nonplanar obstruction if the obstruction lies in the 2-core.


#### Visualizing

Try out the following in Gephi:

```angular2html
node attributes:
    degree

Size nodes by:
    degree

Compare layouts:
    ForceAtlas2
    Fruchterman-Reingold
    Yifan Hu
```

### Summary of findings

- Planarity and topology interact, but they are not the same invariant.
- Morse-style cancellations simplify a graph or complex by removing locally inessential pieces. But if the nonplanar obstruction lies in the irreducible core, then the collapse exposes the obstruction rather than eliminating it.


### Next step

- Does this help to clarify Kuratowski's theorem?
- Does this help to describe the discrete Morse reductions?
- Maybe a picture isn't worth a thousand words in this case?
