"""Create the first original Green Machine landmark in Blender 5.2+."""

import bpy
import math
from mathutils import Vector


OUTPUT_BLEND = "unity/Assets/Art/Source/GreenGate.blend"
OUTPUT_RENDER = "unity/Assets/Art/Previews/green_gate.png"


def material(name, color, metallic=0.0, roughness=0.5, emission=None):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 3.0
    return mat


PINE = material("Pine", (0.035, 0.19, 0.15), roughness=0.38)
LIME = material("Signal Lime", (0.62, 0.95, 0.13), roughness=0.34, emission=(0.2, 0.55, 0.04))
CORAL = material("Coral", (0.95, 0.19, 0.12), roughness=0.4)
GOLD = material("Gold", (1.0, 0.58, 0.07), metallic=0.55, roughness=0.28, emission=(0.72, 0.25, 0.02))
CREAM = material("Cream", (0.98, 0.87, 0.58), roughness=0.7)
GRASS = material("Grass", (0.08, 0.42, 0.20), roughness=0.9)
SKY = material("Sky", (0.14, 0.48, 0.64), roughness=0.5)
WOOD = material("Wood", (0.28, 0.09, 0.03), roughness=0.65)


def cube(name, location, scale, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("Soft Corners", "BEVEL")
        mod.width = bevel
        mod.segments = 3
    return obj


def cylinder(name, location, radius, depth, mat, vertices=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new("Soft Edges", "BEVEL")
    bevel.width = 0.08
    bevel.segments = 2
    return obj


def sphere(name, location, scale, mat):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    return obj


def text(label, location, size, mat):
    bpy.ops.object.text_add(location=location, rotation=(math.radians(74), 0, 0))
    obj = bpy.context.object
    obj.name = label
    obj.data.body = label
    obj.data.align_x = "CENTER"
    obj.data.align_y = "CENTER"
    obj.data.size = size
    obj.data.extrude = 0.045
    obj.data.bevel_depth = 0.012
    obj.data.materials.append(mat)
    return obj


def tree(location, scale=1.0):
    cylinder("Tree Trunk", (location[0], location[1], location[2] + 1.0 * scale), 0.22 * scale, 2.0 * scale, WOOD)
    sphere("Tree Crown", (location[0], location[1], location[2] + 2.4 * scale), (1.15 * scale, 1.15 * scale, 1.45 * scale), GRASS)
    sphere("Tree Crown Top", (location[0] + 0.25 * scale, location[1], location[2] + 3.25 * scale), (0.75 * scale, 0.75 * scale, 0.9 * scale), GRASS)


def light_orb(location, color):
    sphere("Lantern", location, (0.18, 0.18, 0.18), material("Lantern Material", color, emission=color))
    bpy.ops.object.light_add(type="POINT", location=location)
    light = bpy.context.object
    light.data.energy = 100
    light.data.color = color
    light.data.shadow_soft_size = 1.5


def build_gate():
    cube("Park Lawn", (0, 0, -0.3), (15, 12, 0.3), GRASS, 0.2)
    cube("Welcome Path", (0, -6.3, 0.03), (3.1, 7.0, 0.08), CREAM, 0.4)

    for x in (-4.8, 4.8):
        cylinder("Gate Tower", (x, 0, 2.6), 1.2, 5.2, PINE)
        cylinder("Gate Tower Cap", (x, 0, 5.45), 1.38, 0.42, GOLD)
        sphere("Tower Crown", (x, 0, 6.1), (0.65, 0.65, 0.8), CORAL)
        for z in (1.4, 2.6, 3.8):
            cube("Tower Window", (x * 0.99, -1.18, z), (0.33, 0.08, 0.36), LIME, 0.08)

    cube("Gate Header", (0, 0, 4.35), (4.7, 0.68, 1.22), PINE, 0.2)
    cube("Gate Trim", (0, -0.72, 5.1), (4.35, 0.08, 0.12), GOLD, 0.04)
    cube("Left Arch Support", (-2.6, 0, 2.05), (0.55, 0.62, 2.0), CORAL, 0.12)
    cube("Right Arch Support", (2.6, 0, 2.05), (0.55, 0.62, 2.0), CORAL, 0.12)
    text("GREEN", (0, -0.78, 4.85), 0.72, LIME)
    text("MACHINE", (0, -0.79, 4.12), 0.73, CREAM)
    text("PARK", (0, -0.8, 3.55), 0.34, GOLD)

    for x in (-9, -6.8, 6.8, 9):
        tree((x, 1.5, 0), 1.1 if abs(x) < 8 else 0.85)
    for x in (-7.2, -3.5, 3.5, 7.2):
        light_orb((x, -3.2, 1.3), (1.0, 0.58, 0.07) if x < 0 else (0.62, 0.95, 0.13))

    sphere("Rosco Placeholder", (-2.1, -4.1, 0.8), (0.72, 0.48, 0.9), WOOD)
    sphere("Rosco Ear Left", (-2.65, -4.35, 1.35), (0.24, 0.15, 0.38), WOOD)
    sphere("Rosco Ear Right", (-1.55, -4.35, 1.35), (0.24, 0.15, 0.38), WOOD)


def configure_render():
    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.055, 0.14, 0.22, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.25
    bpy.ops.object.light_add(type="AREA", location=(0, -8, 10))
    key = bpy.context.object
    key.data.energy = 1700
    key.data.shape = "DISK"
    key.data.size = 10
    key.rotation_euler = (math.radians(25), 0, 0)
    bpy.ops.object.light_add(type="AREA", location=(-10, 2, 6))
    bpy.context.object.data.energy = 900
    bpy.context.object.data.color = (0.3, 0.7, 1.0)
    bpy.context.scene.render.engine = "BLENDER_EEVEE"
    bpy.context.scene.render.resolution_x = 1200
    bpy.context.scene.render.resolution_y = 800
    bpy.context.scene.render.resolution_percentage = 100
    bpy.context.scene.render.image_settings.file_format = "PNG"
    bpy.context.scene.render.filepath = OUTPUT_RENDER
    bpy.ops.object.camera_add(location=(13, -22, 12))
    camera = bpy.context.object
    camera.data.lens = 48
    direction = Vector((0, 0, 2.4)) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = camera


def main():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    build_gate()
    configure_render()
    bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_BLEND)
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
