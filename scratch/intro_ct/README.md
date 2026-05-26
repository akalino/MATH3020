# Adding distances to graphs

When we first dealt with general graphs, we considered vertices and edges.
When we broached weighted graphs, we were still working in 1-dimension, so those weights (or contributions to a path length or walk) were rather intuitive.
Now, we will get more abstract.

### Software detail

For us to upgrade from graphs to cell complexes, we should start to work in a different tool.
Blender is a good choice here: we will be able so see come of the constructs in a meaningful way, but this isn't a crutch.
When we move to higher dimensional spaces (3D +++) we won't be able to conceptualize a visual.
These exercises are meant as a transition from that thinking to what will be needed later; a mental picture that we attempt to generalize.

Important software note: this is a huge and unnecessary jump, and it is intimidating jump. 
I was intimidated, but learning to overcome those goals is intellectual progress.

### Distances

Let $d$ be a metric to describe a distance $d(x,y)$. 
This can be any arbitrary metric; we will see some later on. 
To do this, we have to anchor the vertices of a graph, or cell complex (or later a simplicial complex) at a certain position.
Thus far, we have considered vertices embedded in the Euclidean plane, so if we placed an $(x,y)$ coordinate plane in any of our 1-dimensional graphs, we could measure a distance between any of the vertices.
Doing so forces the edges of our graphs to have a length, which now considers into how we proceed.

### With distance, neighbors

We have talked about neighborhoods in multiple contexts when studying graph theory, including the one-hop, two-hop, etc. neighbors of a particular vertex.
Adding in a distance is no longer about connectivity, it is about measurement.
If we begin to specify a radius around each vertex, with that radius increasing over time steps $t \in [0, 1, \ldots, n]$, we can measure how often these neighbors collide.
Collision can indicate several points in a graph or cell complex: close neighbors, connected components, ..., up to the entire graph.
This gives us a maginsciope over the entire space, and lets us "hone in" on important features.

### Visualizing goals

```
Part 1: Start with a nonplanar graph.
        See its obstruction core.

Part 2: Assign coordinates.
        Now the vertices are points in a metric space.

Part 3: Measure edge lengths.
        Edges are no longer all equal.

Part 4: Ignore the original edges and rebuild edges by distance.
        This creates a filtration.

Part 5: Add triangles when triples are mutually close.
        Now the graph becomes a simplicial complex.

Part 6: Watch cycles appear and disappear.
        This is the beginning of persistent homology.
```

We can use the following key to track what is being represented:

```angular2html
red spheres          = core obstruction vertices
gray spheres         = dangling tree/noise vertices
orange spheres       = triangle-flap vertices

black thick edges    = core obstruction edges
gray thin edges      = tree/noise edges
orange edges         = triangle-flap edges
blue edges           = Rips/distance-threshold edges
transparent orange   = triangular 2-faces
```

### Conjectures

```angular2html
As r increases, the number of connected components usually decreases.

As r increases, cycles can appear when edges close loops.

As r increases further, cycles can disappear when triangles fill them.

A graph drawing is not just a picture once coordinates matter;
it becomes a finite metric space.
```

Once vertices have coordinates and distances, a graph is no longer just a combinatorial object; it becomes a scaffold for geometry, neighborhoods, and eventually a simplicial complex.