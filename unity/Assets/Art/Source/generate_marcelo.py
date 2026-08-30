"""Build the first original Marcelo character handoff for XIV.

The result is a clean stylized-human FBX with named presentation transforms.
Unity keeps the player root, movement, and companion camera; this asset only
owns the visible character and can be replaced again without rewriting play.
"""

import bpy
import math
import os
from mathutils import Vector


OUTPUT_BLEND = "unity/Assets/Art/Source/MarceloHero.blend"
OUTPUT_FBX = "unity/Assets/Art/Exports/MarceloHero.fbx"


def make_material(name, color, metallic=0.0, roughness=0.5, emission=None):
    material = bpy.data.materials.new(name)
    material.diffuse_color = (*color, 1.0)
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    if shader is None:
        return material
    shader.inputs["Base Color"].default_value = (*color, 1.0)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    if emission:
        emission_color = shader.inputs.get("Emission Color")
        emission_strength = shader.inputs.get("Emission Strength")
        if emission_color:
            emission_color.default_value = (*emission, 1.0)
        if emission_strength:
            emission_strength.default_value = 2.5
    return material


SKIN = make_material("Marcelo Skin", (0.62, 0.31, 0.18), roughness=0.62)
HAIR = make_material("Marcelo Hair", (0.035, 0.018, 0.012), roughness=0.45)
COAT = make_material("Marcelo Teal Coat", (0.025, 0.16, 0.18), roughness=0.44)
SHIRT = make_material("Marcelo Amber Shirt", (0.84, 0.39, 0.10), roughness=0.5)
TROUSERS = make_material("Marcelo Trousers", (0.025, 0.035, 0.05), roughness=0.58)
BOOT = make_material("Marcelo Boots", (0.10, 0.055, 0.028), roughness=0.48)
LIME = make_material("Marcelo Signal Lime", (0.70, 0.94, 0.12), roughness=0.34, emission=(0.36, 0.72, 0.04))
GOLD = make_material("Marcelo Brass", (0.88, 0.50, 0.08), metallic=0.65, roughness=0.28)


def parent_to(obj, root):
    obj.parent = root
    return obj


def bevel(obj, width=0.04, segments=3):
    modifier = obj.modifiers.new("Soft tailored edges", "BEVEL")
    modifier.width = width
    modifier.segments = segments
    return obj


def box(name, location, dimensions, material, root, bevel_width=0.04, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    parent_to(obj, root)
    if bevel_width > 0:
        bevel(obj, bevel_width)
    return obj


def ellipsoid(name, location, dimensions, material, root):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    parent_to(obj, root)
    return obj


def cylinder(name, location, radius, depth, material, root, vertices=24, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    parent_to(obj, root)
    bevel(obj, 0.035, 2)
    return obj


def limb(name, start, end, radius, material, root):
    start_vector = Vector(start)
    end_vector = Vector(end)
    direction = end_vector - start_vector
    length = direction.length
    midpoint = (start_vector + end_vector) * 0.5
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=14, location=midpoint)
    obj = bpy.context.object
    obj.name = name
    obj.scale = (radius, radius, length * 0.5 + radius)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector((0.0, 0.0, 1.0)).rotation_difference(direction.normalized())
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    parent_to(obj, root)
    return obj


def build_character():
    root = bpy.data.objects.new("Marcelo Hero", None)
    bpy.context.collection.objects.link(root)

    # The body uses a believable human proportion: shoulders, waist, knees,
    # hands, and boots all read as one connected silhouette from the game camera.
    body = box("Marcelo Body", (0.0, 0.0, 1.30), (0.92, 0.52, 1.18), COAT, root, 0.14)
    box("Marcelo Shirt", (0.0, -0.285, 1.27), (0.42, 0.04, 0.62), SHIRT, root, 0.02)
    box("Marcelo Coat Trim", (0.0, -0.318, 1.28), (0.07, 0.03, 0.74), LIME, root, 0.01)
    box("Marcelo Belt", (0.0, 0.0, 0.80), (0.86, 0.48, 0.12), GOLD, root, 0.025)

    head = ellipsoid("Marcelo Head", (0.0, 0.0, 2.26), (0.56, 0.50, 0.68), SKIN, root)
    cylinder("Marcelo Neck", (0.0, 0.0, 1.85), 0.17, 0.24, SKIN, root)
    ellipsoid("Marcelo Hair", (0.0, 0.075, 2.52), (0.57, 0.49, 0.28), HAIR, root)
    cylinder("Marcelo Cap", (0.0, 0.03, 2.69), 0.34, 0.10, HAIR, root)
    box("Marcelo Cap Brim", (0.0, -0.22, 2.66), (0.42, 0.25, 0.06), HAIR, root, 0.02)

    shoulder_left = ellipsoid("Marcelo Shoulder Left", (-0.52, 0.0, 1.62), (0.30, 0.38, 0.34), COAT, root)
    shoulder_right = ellipsoid("Marcelo Shoulder Right", (0.52, 0.0, 1.62), (0.30, 0.38, 0.34), COAT, root)
    limb("Marcelo Arm Left", (-0.52, 0.0, 1.58), (-0.63, -0.01, 1.03), 0.16, COAT, root)
    limb("Marcelo Arm Right", (0.52, 0.0, 1.58), (0.63, -0.01, 1.03), 0.16, COAT, root)
    ellipsoid("Marcelo Hand Left", (-0.65, -0.02, 0.72), (0.23, 0.22, 0.23), SKIN, root)
    ellipsoid("Marcelo Hand Right", (0.65, -0.02, 0.72), (0.23, 0.22, 0.23), SKIN, root)

    limb("Marcelo Leg Left", (-0.22, 0.0, 0.72), (-0.24, 0.0, 0.25), 0.19, TROUSERS, root)
    limb("Marcelo Leg Right", (0.22, 0.0, 0.72), (0.24, 0.0, 0.25), 0.19, TROUSERS, root)
    box("Marcelo Boot Left", (-0.24, -0.08, 0.10), (0.34, 0.56, 0.22), BOOT, root, 0.06)
    box("Marcelo Boot Right", (0.24, -0.08, 0.10), (0.34, 0.56, 0.22), BOOT, root, 0.06)

    backpack = box("Marcelo Backpack", (0.0, 0.32, 1.33), (0.58, 0.20, 0.76), SHIRT, root, 0.08)
    box("Marcelo Backpack Badge", (0.0, 0.445, 1.42), (0.20, 0.025, 0.20), LIME, root, 0.03)
    scarf = box("Marcelo Scarf", (0.0, -0.03, 1.78), (0.48, 0.12, 0.18), LIME, root, 0.035)
    box("Marcelo Scarf Tail", (0.22, 0.15, 1.61), (0.14, 0.48, 0.08), LIME, root, 0.025, rotation=(math.radians(-16), 0.0, math.radians(-8)))

    # Parent the presentation pieces that should move with the named hooks.
    for obj in (shoulder_left, shoulder_right, backpack, head, scarf):
        obj.parent = root
    return root


def export_fbx(root):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in bpy.data.objects:
        if obj == root or obj.parent == root:
            obj.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.fbx(
        filepath=OUTPUT_FBX,
        use_selection=True,
        object_types={"EMPTY", "MESH"},
        apply_scale_options="FBX_SCALE_ALL",
    )


def main():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    root = build_character()
    os.makedirs(os.path.dirname(OUTPUT_BLEND), exist_ok=True)
    os.makedirs(os.path.dirname(OUTPUT_FBX), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_BLEND)
    export_fbx(root)


if __name__ == "__main__":
    main()
