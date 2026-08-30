"""Create and export the first original XIV landmark in Blender 5.2+.

Green Gate v2: layered copper tower roofs, vaulted header roof with rafters,
stone footings, brick threshold, lantern posts, Rosco ranger booth (left),
park map board (right), ticker-tape relief, and a golden-hour arrival render
composed from behind Marcelo + Rosco stand-ins.

Material names must keep the substrings GreenMachineParkBuilder.cs rebinds:
Pine, Signal Lime, Coral, Gold, Cream, Grass, Wood, Gate Stone, Arrival Brick,
Patina Copper, Parchment, Lantern. Render-only objects (lights, camera,
stand-ins) never reach the FBX.
"""

import bpy
import math
import os
from mathutils import Vector


OUTPUT_BLEND = "unity/Assets/Art/Source/GreenGate.blend"
OUTPUT_RENDER = "unity/Assets/Art/Previews/green_gate.png"
OUTPUT_FBX = "unity/Assets/Art/Exports/GreenGate.fbx"

RENDER_ONLY = set()


def render_only(obj):
    RENDER_ONLY.add(obj)
    return obj


def material(name, color, metallic=0.0, roughness=0.5, emission=None, emission_strength=3.0, wear=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    if wear:
        # Subtle painted-wood wear: noise brightens the base color in patches.
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 9.0
        noise.inputs["Detail"].default_value = 4.0
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.42
        ramp.color_ramp.elements[1].position = 0.72
        mix = nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.inputs["Factor"].default_value = 0.0
        mix.inputs["A"].default_value = (*color, 1.0)
        worn = tuple(min(1.0, c * (1.0 + wear)) for c in color)
        mix.inputs["B"].default_value = (*worn, 1.0)
        links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
        links.new(ramp.outputs["Color"], mix.inputs["Factor"])
        links.new(mix.outputs["Result"], bsdf.inputs["Base Color"])
    return mat


PINE = material("Pine", (0.035, 0.19, 0.15), roughness=0.42, wear=0.5)
LIME = material("Signal Lime", (0.62, 0.95, 0.13), roughness=0.34, emission=(0.30, 0.62, 0.05), emission_strength=4.0)
CORAL = material("Coral", (0.95, 0.19, 0.12), roughness=0.44, wear=0.3)
GOLD = material("Gold Brass", (1.0, 0.58, 0.07), metallic=0.72, roughness=0.26)
CREAM = material("Cream", (0.98, 0.87, 0.58), roughness=0.68, wear=0.2)
GRASS = material("Grass", (0.08, 0.42, 0.20), roughness=0.9)
SKY = material("Sky", (0.14, 0.48, 0.64), roughness=0.4)
WOOD = material("Wood", (0.28, 0.09, 0.03), roughness=0.62, wear=0.4)
STONE = material("Gate Stone", (0.31, 0.34, 0.29), roughness=0.85, wear=0.25)
BRICK = material("Arrival Brick", (0.56, 0.20, 0.10), roughness=0.78, wear=0.35)
COPPER = material("Patina Copper", (0.08, 0.38, 0.29), metallic=0.5, roughness=0.34, wear=0.45)
PARCHMENT = material("Park Map Parchment", (0.92, 0.74, 0.38), roughness=0.7)
LAMP_GLOW = material("Lantern Glass", (1.0, 0.82, 0.45), roughness=0.3, emission=(1.0, 0.62, 0.16), emission_strength=6.0)


def cube(name, location, scale, mat, bevel=0.0, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=location, rotation=rotation)
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


def cylinder(name, location, radius, depth, mat, vertices=24, rotation=(0, 0, 0), soft=0.06):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    if soft:
        bevel = obj.modifiers.new("Soft Edges", "BEVEL")
        bevel.width = soft
        bevel.segments = 2
    return obj


def cone(name, location, radius_bottom, radius_top, depth, mat, vertices=24):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius_bottom, radius2=radius_top, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new("Soft Edges", "BEVEL")
    bevel.width = 0.04
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


def text(label, location, size, mat, body=None, tilt=78):
    bpy.ops.object.text_add(location=location, rotation=(math.radians(tilt), 0, 0))
    obj = bpy.context.object
    obj.name = label
    obj.data.body = body or label
    obj.data.align_x = "CENTER"
    obj.data.align_y = "CENTER"
    obj.data.size = size
    obj.data.extrude = 0.045
    obj.data.bevel_depth = 0.012
    obj.data.materials.append(mat)
    return obj


def tree(location, scale=1.0):
    x, y, z = location
    cylinder("Tree Trunk", (x, y, z + 1.0 * scale), 0.2 * scale, 2.0 * scale, WOOD)
    sphere("Tree Crown", (x, y, z + 2.4 * scale), (1.1 * scale, 1.1 * scale, 1.3 * scale), GRASS)
    sphere("Tree Crown Side", (x - 0.55 * scale, y + 0.3 * scale, z + 2.0 * scale), (0.7 * scale, 0.7 * scale, 0.8 * scale), GRASS)
    sphere("Tree Crown Top", (x + 0.3 * scale, y - 0.1 * scale, z + 3.2 * scale), (0.7 * scale, 0.7 * scale, 0.85 * scale), GRASS)


def grass_tuft(x, y, scale=1.0):
    sphere("Grass Tuft", (x, y, 0.07 * scale), (0.3 * scale, 0.26 * scale, 0.15 * scale), GRASS)
    sphere("Grass Tuft Small", (x + 0.28 * scale, y + 0.12 * scale, 0.05 * scale), (0.16 * scale, 0.14 * scale, 0.1 * scale), GRASS)


def flower(x, y, mat):
    cylinder("Flower Stem", (x, y, 0.14), 0.02, 0.28, GRASS, vertices=8, soft=0)
    sphere("Flower Head", (x, y, 0.3), (0.075, 0.075, 0.075), mat)


def lantern_post(x, y, tall=True):
    """Freestanding park lantern: wood post, brass collar, glowing box, copper cap."""
    post_h = 2.3 if tall else 1.7
    top = post_h
    cylinder("Lantern Post", (x, y, post_h / 2), 0.09, post_h, WOOD, vertices=12)
    cylinder("Lantern Collar", (x, y, top + 0.04), 0.14, 0.08, GOLD, vertices=12)
    glow = cube("Lantern Glass Box", (x, y, top + 0.28), (0.16, 0.16, 0.2), LAMP_GLOW, 0.03)
    cube("Lantern Cage Left", (x - 0.17, y, top + 0.28), (0.02, 0.14, 0.2), PINE, 0.01)
    cube("Lantern Cage Right", (x + 0.17, y, top + 0.28), (0.02, 0.14, 0.2), PINE, 0.01)
    cone("Lantern Cap", (x, y, top + 0.58), 0.26, 0.09, 0.2, COPPER, vertices=12)
    sphere("Lantern Finial", (x, y, top + 0.72), (0.05, 0.05, 0.05), GOLD)
    return glow


def point_light(location, color, energy=40, size=0.8):
    bpy.ops.object.light_add(type="POINT", location=location)
    light = bpy.context.object
    light.data.energy = energy
    light.data.color = color
    light.data.shadow_soft_size = size
    return render_only(light)


def build_tower(x):
    # Octagonal stone footing course with a ring of rough blocks.
    cylinder("Gate Stone Footing", (x, 0, 0.3), 1.6, 0.6, STONE, vertices=8)
    for i in range(8):
        a = i * math.pi / 4 + 0.2
        bx, by = x + 1.5 * math.cos(a), 1.5 * math.sin(a)
        cube("Gate Stone Block", (bx, by, 0.18), (0.28, 0.22, 0.18), STONE, 0.05, rotation=(0, 0, a))
    cylinder("Gate Tower", (x, 0, 2.8), 1.15, 5.0, PINE)
    # Painted band + brass cap ring under the roof.
    cylinder("Tower Band", (x, 0, 4.9), 1.19, 0.18, CORAL, soft=0.03)
    cylinder("Gold Cap Ring", (x, 0, 5.42), 1.34, 0.28, GOLD, soft=0.04)
    # Layered copper roof: broad tier, lit drum, steep tier, brass+coral finial.
    cone("Patina Roof Tier One", (x, 0, 5.98), 1.8, 0.75, 0.85, COPPER, vertices=24)
    cylinder("Roof Drum", (x, 0, 6.6), 0.7, 0.5, PINE)
    cube("Drum Lamp", (x, -0.68, 6.6), (0.16, 0.06, 0.14), LAMP_GLOW, 0.03)
    cone("Patina Roof Tier Two", (x, 0, 7.3), 1.02, 0.1, 0.95, COPPER, vertices=24)
    sphere("Finial Collar", (x, 0, 7.86), (0.14, 0.14, 0.12), GOLD)
    sphere("Tower Crown Orb", (x, 0, 8.06), (0.24, 0.24, 0.3), CORAL)
    # Inset signal-lime lamps facing the arrival path.
    for z in (1.5, 2.7, 3.9):
        cube("Tower Inset Lamp", (x, -1.12, z), (0.3, 0.1, 0.33), LIME, 0.06)
        cube("Tower Lamp Frame", (x, -1.1, z - 0.42), (0.36, 0.05, 0.04), GOLD, 0.02)


def build_header():
    cube("Gate Header", (0, 0, 4.25), (4.7, 0.66, 1.05), PINE, 0.2)
    cube("Header Base Trim", (0, 0, 3.28), (4.75, 0.72, 0.1), GOLD, 0.03)
    # Vaulted copper roof: squashed cylinder along X with real front/back overhang.
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=1.32, depth=8.4, location=(0, 0, 5.42), rotation=(0, math.pi / 2, 0))
    vault = bpy.context.object
    vault.name = "Patina Vault Roof"
    vault.scale = (0.4, 1.0, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    vault.data.materials.append(COPPER)
    vb = vault.modifiers.new("Soft Edges", "BEVEL")
    vb.width = 0.05
    vb.segments = 2
    cube("Vault Ridge Cap", (0, 0, 6.0), (4.1, 0.1, 0.06), GOLD, 0.02)
    # Visible wooden underside: soffit board plus exposed rafters under the overhang.
    cube("Roof Soffit", (0, 0, 5.3), (4.9, 0.92, 0.07), WOOD, 0.03)
    for i in range(-3, 4):
        cube("Roof Rafter", (i * 1.25, 0, 5.16), (0.09, 0.86, 0.09), WOOD, 0.02)
    # Coral arch supports keep the walkable opening obvious.
    cube("Left Arch Support", (-2.6, 0, 2.05), (0.55, 0.62, 2.0), CORAL, 0.12)
    cube("Right Arch Support", (2.6, 0, 2.05), (0.55, 0.62, 2.0), CORAL, 0.12)
    cube("Left Support Shoe", (-2.6, 0, 0.18), (0.68, 0.74, 0.18), STONE, 0.05)
    cube("Right Support Shoe", (2.6, 0, 0.18), (0.68, 0.74, 0.18), STONE, 0.05)
    # Ticker-tape relief: one quiet brass band, alternating tick heights, no symbols.
    cube("Ticker Band Backing", (0, -0.7, 5.02), (4.35, 0.05, 0.15), PINE, 0.02)
    for i, x in enumerate(x * 0.6 for x in range(-7, 8)):
        cube("Ticker Relief Tick", (x, -0.77, 5.02), (0.15, 0.03, 0.1 if i % 2 else 0.055), GOLD, 0.01)
    text("XIV", (0, -0.76, 4.55), 1.0, LIME)
    text("GREEN GATE", (0, -0.73, 3.72), 0.4, CREAM)
    # Hanging EST sign on brass chains; year is populated locally later.
    for cx in (-1.0, 1.0):
        cylinder("Sign Chain", (cx, -0.15, 3.02), 0.025, 0.42, GOLD, vertices=8, soft=0)
    cube("Hanging Sign Board", (0, -0.15, 2.78), (1.35, 0.09, 0.26), GOLD, 0.05)
    cube("Hanging Sign Face", (0, -0.22, 2.78), (1.22, 0.03, 0.18), CREAM, 0.02)
    text("EST. [YEAR]", (0, -0.29, 2.78), 0.17, PINE)


def build_grounds():
    cube("Park Lawn", (0, -0.5, -0.3), (16, 13.5, 0.3), GRASS, 0.2)
    cube("Outside Concrete Path", (0, -7.4, 0.03), (3.1, 6.4, 0.08), CREAM, 0.4)
    cube("Concrete Curb Left", (-3.2, -7.4, 0.07), (0.12, 6.4, 0.1), STONE, 0.03)
    cube("Concrete Curb Right", (3.2, -7.4, 0.07), (0.12, 6.4, 0.1), STONE, 0.03)
    # Threshold: path turns to warm brick exactly under the arch.
    cube("Inside Brick Path", (0, 2.7, 0.04), (3.1, 3.8, 0.1), BRICK, 0.18)
    cube("Threshold Brass Strip", (0, -1.02, 0.1), (3.1, 0.09, 0.05), GOLD, 0.02)
    for row in range(7):
        for column in range(5):
            x = (column - 2) * 1.15 + (0.55 if row % 2 else 0)
            y = 0.25 + row * 0.92
            cube("Warm Brick", (x, y, 0.16), (0.5, 0.38, 0.035), CREAM if (row + column) % 4 == 0 else BRICK, 0.035)


def build_rosco_corner():
    """Left of the gate: the little ranger booth where Rosco waits (companion itself lives in Unity)."""
    cube("Rosco Ranger Booth", (-7.2, -0.6, 1.05), (0.95, 0.85, 1.05), WOOD, 0.14)
    cube("Booth Window Sill", (-7.2, -1.5, 1.35), (0.7, 0.08, 0.06), GOLD, 0.02)
    cube("Booth Window", (-7.2, -1.44, 1.7), (0.62, 0.05, 0.32), LAMP_GLOW, 0.04)
    cylinder("Booth Roof Base", (-7.2, -0.6, 2.24), 1.25, 0.14, GOLD, soft=0.03)
    cone("Booth Roof", (-7.2, -0.6, 2.68), 1.35, 0.12, 0.8, CORAL, vertices=16)
    sphere("Booth Roof Finial", (-7.2, -0.6, 3.14), (0.1, 0.1, 0.1), GOLD)
    text("ROSCO", (-7.2, -1.53, 0.62), 0.2, CREAM, tilt=84)
    # Water bowl and bench make the corner read as a waiting spot, not a prop pile.
    cylinder("Rosco Bowl", (-6.0, -1.9, 0.1), 0.3, 0.18, GOLD, vertices=16)
    cylinder("Rosco Bowl Water", (-6.0, -1.9, 0.17), 0.24, 0.06, SKY, vertices=16, soft=0)
    cube("Bench Leg Left", (-8.7, -1.4, 0.24), (0.12, 0.3, 0.24), STONE, 0.03)
    cube("Bench Leg Right", (-7.9, -1.4, 0.24), (0.12, 0.3, 0.24), STONE, 0.03)
    cube("Bench Seat", (-8.3, -1.4, 0.53), (0.85, 0.34, 0.06), WOOD, 0.03)
    grass_tuft(-6.4, 0.4)
    grass_tuft(-8.2, -0.5, 0.8)
    flower(-6.5, -1.3, CORAL)


def build_map_corner():
    """Right of the gate: the mounted park-map board under a copper cap."""
    for px in (6.45, 7.95):
        cylinder("Map Board Post", (px, -0.4, 1.3), 0.11, 2.6, WOOD, vertices=12)
    cube("Mounted Park Map", (7.2, -0.5, 1.95), (1.28, 0.08, 0.82), PARCHMENT, 0.08)
    cube("Map Frame", (7.2, -0.44, 1.95), (1.4, 0.05, 0.94), GOLD, 0.06)
    cube("Map Cap Roof", (7.2, -0.42, 2.98), (1.6, 0.36, 0.08), COPPER, 0.04)
    cube("Map Cap Trim", (7.2, -0.72, 2.94), (1.6, 0.06, 0.05), GOLD, 0.02)
    text("PARK MAP", (7.2, -0.62, 2.42), 0.2, PINE, tilt=84)
    # Simple original map sketch: green lands, a lime path, a coral you-are-here dot.
    sphere("Map Land Blob", (6.9, -0.6, 1.9), (0.3, 0.02, 0.22), GRASS)
    sphere("Map Land Blob East", (7.55, -0.6, 2.0), (0.22, 0.02, 0.16), GRASS)
    cube("Map Path Line", (7.2, -0.6, 1.72), (0.5, 0.015, 0.03), LIME, 0.0, rotation=(0, math.radians(12), 0))
    sphere("Map Here Dot", (7.2, -0.61, 1.56), (0.05, 0.02, 0.05), CORAL)
    grass_tuft(6.4, 0.7)
    grass_tuft(8.3, -1.2, 0.85)
    flower(8.1, 0.2, GOLD)


def build_planters():
    for x in (-5.9, 5.9):
        cube("Planter Wood Box", (x, -2.1, 0.4), (0.8, 0.5, 0.4), WOOD, 0.08)
        cube("Planter Gold Lip", (x, -2.1, 0.82), (0.86, 0.56, 0.05), GOLD, 0.02)
        sphere("Planter Leaves", (x, -2.1, 1.15), (0.72, 0.5, 0.5), GRASS)
        sphere("Planter Bloom", (x + 0.3, -2.35, 1.4), (0.14, 0.14, 0.14), CORAL if x < 0 else GOLD)


def build_gate():
    build_grounds()
    for x in (-4.8, 4.8):
        build_tower(x)
    build_header()
    build_rosco_corner()
    build_map_corner()
    build_planters()
    for spot, s in (((-10.5, 2.2, 0), 1.15), ((-8.0, 3.4, 0), 0.9), ((8.0, 3.4, 0), 0.95), ((10.5, 2.2, 0), 1.2),
                    ((-11.5, -4.5, 0), 0.85), ((11.5, -4.5, 0), 0.8)):
        tree(spot, s)
    for tx, ty in ((-4.1, -1.7), (4.1, -1.7), (-5.7, 1.1), (5.7, 1.1), (-3.7, -6.5), (3.7, -6.5),
                   (-3.5, -10.5), (3.5, -10.5), (-9.9, 1.0), (9.9, 1.0), (-1.6, 5.6), (1.6, 5.6)):
        grass_tuft(tx, ty, 0.9)
    for fx, fy, fm in ((-3.8, -2.6, CORAL), (3.8, -2.6, GOLD), (-5.3, -1.2, GOLD), (5.3, -1.2, CORAL)):
        flower(fx, fy, fm)
    # Modular lantern posts pace the arrival walk; their glow boxes get render lights.
    glows = []
    for lx, ly in ((-3.6, -4.6), (3.6, -4.6), (-3.6, -9.4), (3.6, -9.4)):
        glows.append(lantern_post(lx, ly))
    return glows


def build_standins():
    """Render-only Marcelo + Rosco silhouettes for the arrival composition; excluded from FBX."""
    for lx in (0.49, 0.71):
        render_only(cylinder("Standin Marcelo Leg", (lx, -8.6, 0.5), 0.09, 1.0, PINE, vertices=12))
    render_only(cube("Standin Marcelo Torso", (0.6, -8.6, 1.32), (0.3, 0.19, 0.42), SKY, 0.08))
    for ax in (0.27, 0.93):
        render_only(cylinder("Standin Marcelo Arm", (ax, -8.6, 1.35), 0.07, 0.62, SKY, vertices=12))
    render_only(sphere("Standin Marcelo Head", (0.6, -8.6, 1.95), (0.17, 0.17, 0.19), CREAM))
    render_only(sphere("Standin Marcelo Cap", (0.6, -8.63, 2.08), (0.18, 0.18, 0.09), CORAL))
    render_only(sphere("Standin Rosco Body", (-0.7, -7.9, 0.42), (0.42, 0.3, 0.32), WOOD))
    render_only(sphere("Standin Rosco Head", (-0.7, -7.5, 0.72), (0.24, 0.22, 0.22), WOOD))
    render_only(sphere("Standin Rosco Ear L", (-0.86, -7.48, 0.92), (0.07, 0.05, 0.13), WOOD))
    render_only(sphere("Standin Rosco Ear R", (-0.54, -7.48, 0.92), (0.07, 0.05, 0.13), WOOD))
    render_only(sphere("Standin Rosco Tail", (-0.7, -8.42, 0.78), (0.06, 0.14, 0.06), WOOD))


def configure_render(glow_boxes):
    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.05, 0.12, 0.2, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.35

    def aim(obj, target):
        direction = Vector(target) - obj.location
        obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

    # Golden-hour key from behind the player, low and warm.
    bpy.ops.object.light_add(type="AREA", location=(6, -24, 6.5))
    key = render_only(bpy.context.object)
    key.data.energy = 6500
    key.data.color = (1.0, 0.55, 0.22)
    key.data.shape = "DISK"
    key.data.size = 9
    aim(key, (0, 0, 3.5))
    # Cool dusk fill from the left keeps the neon-market half of the palette alive.
    bpy.ops.object.light_add(type="AREA", location=(-14, -6, 7))
    fill = render_only(bpy.context.object)
    fill.data.energy = 650
    fill.data.color = (0.3, 0.55, 0.95)
    fill.data.size = 8
    aim(fill, (0, 0, 3))
    # Lamps already on for the arrival shot.
    for glow in glow_boxes:
        point_light((glow.location.x, glow.location.y, glow.location.z + 0.05), (1.0, 0.62, 0.16), energy=35)
    point_light((-4.8, -1.6, 2.7), (0.62, 0.95, 0.13), energy=25)
    point_light((4.8, -1.6, 2.7), (0.62, 0.95, 0.13), energy=25)
    point_light((-7.2, -1.8, 1.7), (1.0, 0.62, 0.16), energy=20)

    try:
        bpy.context.scene.render.engine = "BLENDER_EEVEE"
    except TypeError:
        bpy.context.scene.render.engine = "BLENDER_EEVEE_NEXT"
    bpy.context.scene.render.resolution_x = 1600
    bpy.context.scene.render.resolution_y = 1000
    bpy.context.scene.render.resolution_percentage = 100
    bpy.context.scene.render.image_settings.file_format = "PNG"
    bpy.context.scene.render.filepath = OUTPUT_RENDER
    bpy.ops.object.camera_add(location=(1.5, -21.5, 5.0))
    camera = render_only(bpy.context.object)
    camera.data.lens = 37
    aim(camera, (0, 0, 3.3))
    bpy.context.scene.camera = camera


def finalize_meshes():
    """Convert signage text to plain meshes so the FBX carries no font dependencies."""
    bpy.ops.object.select_all(action="DESELECT")
    for obj in list(bpy.data.objects):
        if obj.type == "FONT":
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
    if bpy.context.selected_objects:
        bpy.ops.object.convert(target="MESH")


def export_fbx():
    """Export meshes only — no lights, cameras, or render-only stand-ins."""
    bpy.ops.object.select_all(action="DESELECT")
    for obj in bpy.data.objects:
        if obj.type == "MESH" and obj not in RENDER_ONLY:
            obj.select_set(True)
    bpy.ops.export_scene.fbx(
        filepath=OUTPUT_FBX,
        use_selection=True,
        object_types={"MESH"},
        apply_scale_options="FBX_SCALE_ALL",
    )


def main():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    glow_boxes = build_gate()
    build_standins()
    configure_render(glow_boxes)
    finalize_meshes()
    os.makedirs(os.path.dirname(OUTPUT_FBX), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_BLEND)
    export_fbx()
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
