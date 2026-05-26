"""
Render a NetworkX-generated JSON scene in Blender.

Run from terminal:
    blender --background --python render_graph_json_in_blender.py -- input.json output.png

This script needs only Blender's built-in Python modules plus json and mathutils.
No NetworkX required inside Blender.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector


DEFAULT_INPUT = "/home/alex/Desktop/blender_json_exports/k5_leaf_collapse_step_000.json"
DEFAULT_OUTPUT = "/home/alex/Desktop/k5_leaf_collapse_step_000.png"


def args_after_double_dash():
    if "--" not in sys.argv:
        return []
    return sys.argv[sys.argv.index("--") + 1:]


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def make_material(name, color, alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color

    if alpha < 1.0:
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf is not None:
            bsdf.inputs["Alpha"].default_value = alpha
        mat.blend_method = "BLEND"
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
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()

    if material is not None:
        obj.data.materials.append(material)
    return obj


def add_triangle_face(p1, p2, p3, material=None, name="triangle"):
    mesh = bpy.data.meshes.new(name + "_mesh")
    mesh.from_pydata([p1, p2, p3], [], [(0, 1, 2)])
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if material is not None:
        obj.data.materials.append(material)
    return obj


def load_scene_json(path):
    with open(path, "r") as f:
        scene = json.load(f)

    nodes = {node["id"]: node for node in scene["nodes"]}
    edges = scene.get("edges", [])
    triangles = scene.get("triangles", [])
    metadata = scene.get("metadata", {})
    return scene, nodes, edges, triangles, metadata


def node_location(node):
    return (float(node["x"]), float(node["y"]), float(node["z"]))


def draw_scene(scene, nodes, edges, triangles):
    clear_scene()

    # Materials. Adjust these if you want a different visual style.
    mat_core_node = make_material("core nodes", (0.95, 0.12, 0.08, 1.0))
    mat_noise_node = make_material("noise nodes", (0.35, 0.35, 0.35, 1.0))
    mat_flap_node = make_material("flap nodes", (0.95, 0.6, 0.1, 1.0))
    mat_rips_node = make_material("rips nodes", (0.1, 0.1, 0.1, 1.0))

    mat_core_edge = make_material("core edges", (0.02, 0.02, 0.02, 1.0))
    mat_noise_edge = make_material("noise edges", (0.55, 0.55, 0.55, 1.0))
    mat_triangle_edge = make_material("triangle edges", (0.95, 0.55, 0.05, 1.0))
    mat_rips_edge = make_material("rips edges", (0.05, 0.15, 0.8, 1.0))

    mat_triangle_face = make_material("triangle faces", (1.0, 0.6, 0.05, 0.32), alpha=0.32)

    # Faces first, then edges, then nodes.
    for idx, tri in enumerate(triangles):
        ids = tri["vertices"]
        if all(v in nodes for v in ids):
            add_triangle_face(
                node_location(nodes[ids[0]]),
                node_location(nodes[ids[1]]),
                node_location(nodes[ids[2]]),
                material=mat_triangle_face,
                name=f"triangle_{idx}",
            )

    for edge in edges:
        u = edge["source"]
        v = edge["target"]
        if u not in nodes or v not in nodes:
            continue

        if edge.get("core_edge", False):
            mat = mat_core_edge
            radius = 0.055
        elif edge.get("noise_edge", False):
            mat = mat_noise_edge
            radius = 0.028
        elif edge.get("triangle_edge", False):
            mat = mat_triangle_edge
            radius = 0.035
        elif edge.get("rips_edge", False):
            mat = mat_rips_edge
            radius = 0.026
        else:
            mat = mat_noise_edge
            radius = 0.03

        add_cylinder_between(
            node_location(nodes[u]),
            node_location(nodes[v]),
            radius=radius,
            material=mat,
            name=f"edge_{u}_{v}",
        )

    for node_id, node in nodes.items():
        if node.get("core", False):
            mat = mat_core_node
            radius = 0.17
        elif node.get("flap", False):
            mat = mat_flap_node
            radius = 0.12
        elif node.get("noise", False):
            mat = mat_noise_node
            radius = 0.105
        else:
            mat = mat_rips_node
            radius = 0.10

        add_uv_sphere(
            node_location(node),
            radius=radius,
            material=mat,
            name=f"vertex_{node_id}",
        )


def setup_camera_and_light(nodes):
    coords = [Vector(node_location(n)) for n in nodes.values()]
    if coords:
        center = sum(coords, Vector((0, 0, 0))) / len(coords)
        max_radius = max((p - center).length for p in coords)
    else:
        center = Vector((0, 0, 0))
        max_radius = 5

    # Lights
    bpy.ops.object.light_add(type="AREA", location=(center.x, center.y - 7, center.z + 8))
    key = bpy.context.object
    key.name = "Key Light"
    key.data.energy = 800
    key.data.size = 6

    bpy.ops.object.light_add(type="POINT", location=(center.x + 5, center.y + 5, center.z + 5))
    fill = bpy.context.object
    fill.name = "Fill Light"
    fill.data.energy = 120

    # Camera, aimed at center.
    camera_distance = max(8, max_radius * 3.2)
    camera_location = center + Vector((0, -camera_distance, camera_distance * 0.65))
    bpy.ops.object.camera_add(location=camera_location)
    camera = bpy.context.object
    direction = center - Vector(camera.location)
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = camera

    bpy.context.scene.render.resolution_x = 1600
    bpy.context.scene.render.resolution_y = 1200

    # Nice default render settings.
    bpy.context.scene.eevee.taa_render_samples = 64 if hasattr(bpy.context.scene, "eevee") else 16


def render(input_json, output_png):
    scene, nodes, edges, triangles, metadata = load_scene_json(input_json)
    draw_scene(scene, nodes, edges, triangles)
    setup_camera_and_light(nodes)

    bpy.context.scene.render.filepath = output_png
    bpy.ops.render.render(write_still=True)

    blend_path = str(Path(output_png).with_suffix(".blend"))
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)

    print(f"Rendered: {output_png}")
    print(f"Saved blend: {blend_path}")
    print(f"Scene metadata: {metadata}")


def main():
    args = args_after_double_dash()
    input_json = args[0] if len(args) >= 1 else DEFAULT_INPUT
    output_png = args[1] if len(args) >= 2 else DEFAULT_OUTPUT
    render(input_json, output_png)


if __name__ == "__main__":
    main()
