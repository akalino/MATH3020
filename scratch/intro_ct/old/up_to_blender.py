import bpy
import sys
import subprocess
import os
python_exe = os.path.join(sys.prefix, 'bin', 'python')
subprocess.call([python_exe, "-m", "pip", "install", "networkx"])
import networkx as nx
from mathutils import Vector


# ----------------------------
# Scene utilities
# ----------------------------

def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def make_material(name, color, alpha=1.0):
    """
    color should be RGBA, e.g. (1, 0, 0, 1).
    """
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color

    if alpha < 1.0:
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Alpha"].default_value = alpha
        mat.blend_method = "BLEND"
        mat.use_screen_refraction = True
        mat.show_transparent_back = True

    return mat


def add_uv_sphere(location, radius=0.12, material=None, name="vertex"):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=24,
        ring_count=12,
        radius=radius,
        location=location,
    )
    obj = bpy.context.object
    obj.name = name

    if material is not None:
        obj.data.materials.append(material)

    return obj


def add_cylinder_between(p1, p2, radius=0.035, material=None, name="edge"):
    """
    Add a cylinder joining p1 and p2.
    """
    p1 = Vector(p1)
    p2 = Vector(p2)
    midpoint = (p1 + p2) / 2
    direction = p2 - p1
    length = direction.length

    if length == 0:
        return None

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=radius,
        depth=length,
        location=midpoint,
    )

    obj = bpy.context.object
    obj.name = name

    # Cylinder is aligned along z-axis by default.
    # Rotate z-axis to match direction.
    quat = direction.to_track_quat("Z", "Y")
    obj.rotation_euler = quat.to_euler()

    if material is not None:
        obj.data.materials.append(material)

    return obj


def add_triangle_face(p1, p2, p3, material=None, name="triangle"):
    """
    Add a triangular mesh face.
    """
    mesh = bpy.data.meshes.new(name + "_mesh")
    verts = [p1, p2, p3]
    faces = [(0, 1, 2)]
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    if material is not None:
        obj.data.materials.append(material)

    return obj


def k5_with_dangling_trees(num_leaves_per_vertex=3):
    G = nx.complete_graph(5)
    next_node = 5

    for v in range(5):
        previous = v
        for _ in range(num_leaves_per_vertex):
            G.add_node(next_node)
            G.add_edge(previous, next_node)
            G.nodes[next_node]["noise"] = True
            previous = next_node
            next_node += 1

    for v in range(5):
        G.nodes[v]["core"] = True

    for u, v in G.edges:
        G.edges[u, v]["core_edge"] = u < 5 and v < 5

    return G


def assign_3d_layout(G, seed=7, scale=4.0):
    """
    NetworkX gives 3D spring positions if dim=3.
    """
    pos = nx.spring_layout(G, dim=3, seed=seed, scale=scale)

    return {
        v: (float(x), float(y), float(z))
        for v, (x, y, z) in pos.items()
    }


def draw_graph_3d(G, pos):
    clear_scene()

    mat_core_node = make_material("core nodes", (0.9, 0.15, 0.1, 1))
    mat_noise_node = make_material("noise nodes", (0.3, 0.3, 0.3, 1))
    mat_core_edge = make_material("core edges", (0.05, 0.05, 0.05, 1))
    mat_noise_edge = make_material("noise edges", (0.55, 0.55, 0.55, 1))

    for v in G.nodes:
        is_core = G.nodes[v].get("core", False)
        mat = mat_core_node if is_core else mat_noise_node
        radius = 0.18 if is_core else 0.11

        add_uv_sphere(
            location=pos[v],
            radius=radius,
            material=mat,
            name=f"vertex_{v}",
        )

    for u, v in G.edges:
        is_core_edge = G.edges[u, v].get("core_edge", False)
        mat = mat_core_edge if is_core_edge else mat_noise_edge
        radius = 0.055 if is_core_edge else 0.03

        add_cylinder_between(
            pos[u],
            pos[v],
            radius=radius,
            material=mat,
            name=f"edge_{u}_{v}",
        )


def draw_neighborhood_balls(G, pos, r):
    mat_ball = make_material("neighborhood balls", (0.2, 0.5, 1.0, 0.18), alpha=0.18)

    for v in G.nodes:
        add_uv_sphere(
            location=pos[v],
            radius=r,
            material=mat_ball,
            name=f"ball_{v}",
        )


def euclidean_distance_3d(pos, u, v):
    p = Vector(pos[u])
    q = Vector(pos[v])
    return (p - q).length


def rips_graph_from_positions(nodes, pos, r):
    H = nx.Graph()
    H.add_nodes_from(nodes)

    nodes = list(nodes)
    for i, u in enumerate(nodes):
        for v in nodes[i + 1:]:
            d = euclidean_distance_3d(pos, u, v)
            if d <= r:
                H.add_edge(u, v, length=d)

    return H


def rips_triangles_from_positions(nodes, pos, r):
    triangles = []
    nodes = list(nodes)

    for i, a in enumerate(nodes):
        for j in range(i + 1, len(nodes)):
            b = nodes[j]
            for k in range(j + 1, len(nodes)):
                c = nodes[k]

                if (
                    euclidean_distance_3d(pos, a, b) <= r
                    and euclidean_distance_3d(pos, a, c) <= r
                    and euclidean_distance_3d(pos, b, c) <= r
                ):
                    triangles.append((a, b, c))

    return triangles


def draw_rips_complex_3d(nodes, pos, r):
    H = rips_graph_from_positions(nodes, pos, r)
    triangles = rips_triangles_from_positions(nodes, pos, r)

    mat_node = make_material("nodes", (0.05, 0.05, 0.05, 1))
    mat_edge = make_material("edges", (0.0, 0.0, 0.0, 1))
    mat_tri = make_material("triangles", (1.0, 0.6, 0.05, 0.35), alpha=0.35)

    for tri in triangles:
        a, b, c = tri
        add_triangle_face(
            pos[a],
            pos[b],
            pos[c],
            material=mat_tri,
            name=f"tri_{a}_{b}_{c}",
        )

    for u, v in H.edges:
        add_cylinder_between(pos[u], pos[v], radius=0.025, material=mat_edge)

    for v in H.nodes:
        add_uv_sphere(pos[v], radius=0.1, material=mat_node)

    return H, triangles


def render_rips_sequence(G, pos, radii, output_dir="//renders"):
    for i, r in enumerate(radii):
        clear_scene()
        draw_rips_complex_3d(G.nodes, pos, r)

        bpy.context.scene.frame_set(i)
        bpy.context.scene.render.filepath = f"{output_dir}/rips_{i:03d}_r_{r:.2f}.png"
        bpy.ops.render.render(write_still=True)


def collapse_leaves_with_snapshots(G, snapshot_steps=(0, 5, 10, 20, 40)):
    H = G.copy()
    snapshots = {}

    step = 0
    if step in snapshot_steps:
        snapshots[step] = H.copy()

    while True:
        leaves = [v for v in H.nodes if H.degree(v) == 1]
        if not leaves:
            break

        v = leaves[0]
        H.remove_node(v)
        step += 1

        if step in snapshot_steps:
            snapshots[step] = H.copy()

    snapshots[step] = H.copy()
    return snapshots


def main():
    G = k5_with_dangling_trees(num_leaves_per_vertex=3)
    pos = assign_3d_layout(G, seed=7)
    draw_graph_3d(G, pos)
    for r in [0.4, 0.7, 1.0, 1.4]:
        clear_scene()
        draw_graph_3d(G, pos)
        draw_neighborhood_balls(G, pos, r=r)
        bpy.ops.wm.save_as_mainfile(filepath=f"metric_neighborhood_r_{r}.blend")


if __name__ == "__main__":
    main()
