# Planar visual conjecture

What happens when we "repair" a non-planar graph $G$ by removing a copy of $K_5$ or $K_{3,3}$?

### Original graph generation

We generate the original graph from a planar lattice graph $L$. 
We then add edges among a chosen set $S$ of vertices such that $S$ contains a $K_5$ or $K_{3,3}$ obstruction.
The resulting graph $L_{S+}$ is now non-planar.
We can then repair the graph to form a new graph $H = L - S$ that is a new planar graph. 

### Initial conjecture

When we do this in Gephi, we can play with the visualization to see that a removal of $K_5$ creates 5 holes, and a removal of $K_{3,3}$ creates 6 holes.
Does this always hold true?

This will depend on how we originally generated the graph $L$ and its structure.
The number of created holes in $H$ will depend on how the copy of $K_5$ or $K_{3,3}$ was embedded.
If the vertices we chose for $S$ are very separate (by a measure of their original path lengths), then we realize about 5 separate holes for $K_5$ and 6 separate holes in $K_{3,3}$.
However, if the vertices we chose are very clustered together, we may realize one larger hole when removing $K_5$ and two larger holes for $K_{3,3}$.

### A more precise conjecture

If the deleted vertices are interior vertices of the planar lattice and no two deleted vertices are adjacent, then deleting them leaves one visible defect face per deleted vertex.
If some deleted vertices are adjacent, their defect regions merge, so the number of visible holes is closer to the number of connected components of the deleted set in the original lattice.


### Argument about faces

If $H$ is connected, then the number of faces is $f_{\text{bounded}} = |E(H)| - |V(H)| + 1$.
One way to measure the holes is to enumerate the number of bounded faces.
For a triangular lattice, the number of bounded faces includes all the ordinary triangular cells as well.

In a triangular lattice, most ordinary faces are triangles. 
If you delete one isolated interior vertex of degree 6, the six triangles around it merge into one hexagonal hole. 
So the total number of bounded faces actually decreases, but the number of large non-triangular defect faces increases by one.

Let's call this the **defect-face conjecture:** In a triangular lattice, deleting a set S of marked obstruction vertices creates one non-triangular defect face for each connected cluster of deleted vertices, provided the deleted vertices are away from the boundary.

Formally: Let L be a planar triangular lattice graph with its natural planar embedding. 
Let $S \subseteq V(L)$, and form $G$ by adding edges among vertices of $S$ so that $G[S]$ contains $K_5$ or $K_{3,3}$.
Then G is nonplanar. 
However, deleting $S$ gives $G−S=L−S$, hence a planar graph. 
In the natural embedding of $L−S$, the new visible defect holes are governed by the connected components of $L[S]$, with one defect region per interior deleted cluster.

### Bounding the number of defect holes

How many of the defect holes can we expect?
Let $L$ be the original triangular lattice with a natural planar embedding.
Let $S$ be the set of deleted obstruction vertices (5 for $K_5$, 6 for $K_{3,3}$) or a potentially larger set.
Let $h(S)$ be the number of new defect holes created by deleting $S$, where a defect hole is defined as a bounded non-triangular face formed by merging ordinary triangular faces around the deleted vertices.

It should be obvious that $h(S)$ is bounded by $1 \leq h(S) \leq |S|$, provided $S$ is non-empty, on the interior (not a point that touches the exterior of the lattice), or deletion opens the outer face.

A more meaningful estimate is $h(S) \leq \kappa(S)$, where $\kappa(S)$ is the number of connected components of the induced subgraph $L[S]$.
In the cases we explored, we found that $h(S) = \kappa(S)$, and this holds when each deleted cluster is interior and locally simply connected: no cluster touches the boundary, separate clusters are not so close that their surrounding defect regions merge.

For example:
```angular2html
K_5 vertices all separated in the lattice:
    |S| = 5
    kappa(S) = 5
    expected defect holes = 5

K_5 vertices chosen as one connected cluster:
    |S| = 5
    kappa(S) = 1
    expected defect holes = 1

K_3,3 vertices all separated:
    |S| = 6
    kappa(S) = 6
    expected defect holes = 6

K_3,3 vertices chosen as two clusters of three:
    |S| = 6
    kappa(S) = 2
    expected defect holes = 2
```

This is further explored in "Polyominoes with Maximally Many Holes" referenced below.

### Summary of this lab

This lab combines Kuratowski’s forbidden-subdivision theorem with the elementary fact that subgraphs of planar graphs are planar, and with Euler’s formula for counting faces in a planar embedding.


```angular2html
@book{diestel2017graph,
  author    = {Reinhard Diestel},
  title     = {Graph Theory},
  edition   = {5},
  publisher = {Springer},
  year      = {2017}
}

@book{west2001introduction,
  author    = {Douglas B. West},
  title     = {Introduction to Graph Theory},
  edition   = {2},
  publisher = {Prentice Hall},
  year      = {2001}
}

@book{bondy2008graph,
  author    = {J. A. Bondy and U. S. R. Murty},
  title     = {Graph Theory},
  publisher = {Springer},
  year      = {2008}
}

@article{kahle2017polyominoes,
  author  = {Matthew Kahle and Frank H. Lutz and Andrew Newman and Kyle Parsons},
  title   = {Polyominoes with Maximally Many Holes},
  journal = {Geombinatorics},
  year    = {2017}
}
```