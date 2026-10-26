"""A film slate for Parker Manley's site, photoreal, in two layers so the page
can clap it: board.png (board, bottom stick, hinge) and stick.png (top stick).

    Nalana -b --factory-startup --python clapper.py -- OUTDIR
"""
import json
import math
import os
import sys

import bpy

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0] if argv else "/tmp/clapper"
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.samples = 96
sc.cycles.use_denoising = True
try:
    sc.cycles.device = "GPU"
except TypeError:
    pass
sc.render.film_transparent = True
sc.render.resolution_x = 1600
sc.render.resolution_y = 1400
sc.view_settings.view_transform = "AgX" if "AgX" in [i.identifier for i in bpy.types.ColorManagedViewSettings.bl_rna.properties["view_transform"].enum_items] else "Filmic"

# Real slate: 28 x 24 cm board, 1.2 cm acrylic, sticks 3.2 cm.
W, H, T = 2.8, 2.4, 0.12
SH = 0.32
OPEN = 14.0


def mat(name, color, rough=0.35, spec=0.5, metal=0.0, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    for k in ("Coat Weight", "Clearcoat"):
        if k in b.inputs:
            b.inputs[k].default_value = coat
    return m


def stripes(name):
    """Black and white diagonal stripes, the clapper's whole identity."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Roughness"].default_value = 0.28
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    add = nt.nodes.new("ShaderNodeMath"); add.operation = "ADD"
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = 2.6
    fr = nt.nodes.new("ShaderNodeMath"); fr.operation = "FRACT"
    gt = nt.nodes.new("ShaderNodeMath"); gt.operation = "GREATER_THAN"; gt.inputs[1].default_value = 0.5
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.012, 0.012, 0.012, 1)
    ramp.color_ramp.elements[1].color = (0.86, 0.85, 0.82, 1)
    ramp.color_ramp.interpolation = "CONSTANT"
    L = nt.links
    L.new(tc.outputs["Object"], sep.inputs[0])
    L.new(sep.outputs[0], add.inputs[0]); L.new(sep.outputs[2], add.inputs[1])
    L.new(add.outputs[0], mul.inputs[0]); L.new(mul.outputs[0], fr.inputs[0])
    L.new(fr.outputs[0], gt.inputs[0]); L.new(gt.outputs[0], ramp.inputs[0])
    L.new(ramp.outputs[0], b.inputs["Base Color"])
    return m


def box(name, size, loc, material, bevel=0.012):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    md = o.modifiers.new("bev", "BEVEL"); md.width = bevel; md.segments = 3
    o.data.materials.append(material)
    for p in o.data.polygons:
        p.use_smooth = True
    return o


acrylic = mat("acrylic", (0.008, 0.008, 0.009), rough=0.12, coat=1.0)
chalk = mat("chalk", (0.82, 0.8, 0.76), rough=0.9)
steel = mat("steel", (0.62, 0.62, 0.64), rough=0.25, metal=1.0)
stripe = stripes("stripe")

board = box("board", (W, T, H), (0, 0, 0), acrylic)
low = box("stick_low", (W, T * 1.15, SH), (0, 0, H / 2 + SH / 2 + 0.01), stripe)

# Chalk lines and labels on the face of the board.
face_y = -T / 2 - 0.002
rows = [0.66, 0.2, -0.26, -0.72]
for i, z in enumerate(rows):
    box(f"rule{i}", (W * 0.9, 0.003, 0.012), (0, face_y, z), chalk, bevel=0.0)
# Dividers sit inside the rows they split: ROLL | SCENE | TAKE, CAMERA | DATE.
box("div1", (0.012, 0.003, 0.46), (-0.38, face_y, 0.43), chalk, bevel=0.0)
box("div2", (0.012, 0.003, 0.46), (0.58, face_y, 0.43), chalk, bevel=0.0)
box("div3", (0.012, 0.003, 0.46), (0.12, face_y, -0.49), chalk, bevel=0.0)
labels = [("PROD.", -1.25, 0.94), ("ROLL", -1.25, 0.5), ("SCENE", -0.3, 0.5), ("TAKE", 0.66, 0.5),
          ("DIRECTOR", -1.25, 0.04), ("CAMERA", -1.25, -0.42), ("DATE", 0.2, -0.42)]
for text, x, z in labels:
    bpy.ops.object.text_add(location=(x, face_y - 0.001, z), rotation=(math.radians(90), 0, 0))
    t = bpy.context.object
    t.data.body = text
    t.data.size = 0.11
    t.data.extrude = 0.0
    t.data.materials.append(chalk)

# The hinge: a steel plate and pin at the left end.
hinge = box("hinge", (0.18, T * 1.3, 0.3), (-W / 2 + 0.1, -0.005, H / 2 + SH + 0.02), steel, bevel=0.01)
bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=T * 1.6, location=(-W / 2 + 0.1, 0, H / 2 + SH + 0.02), rotation=(math.radians(90), 0, 0))
pin = bpy.context.object; pin.data.materials.append(steel)

# The top stick: built closed, sitting on the bottom stick, then given an
# origin at the hinge pin and swung open about it.
pivot = (-W / 2 + 0.1, 0, H / 2 + SH + 0.02)
top = box("stick_top", (W, T * 1.15, SH), (0, -0.004, H / 2 + SH * 1.5 + 0.02), stripe)
sc.cursor.location = pivot
bpy.ops.object.select_all(action="DESELECT")
top.select_set(True)
bpy.context.view_layer.objects.active = top
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
top.rotation_euler = (0, math.radians(-OPEN), 0)

# Light: a big soft key from the upper left, a cool rim from behind right.
bpy.ops.object.light_add(type="AREA", location=(-3, -4, 4))
k = bpy.context.object; k.data.energy = 900; k.data.size = 4; k.rotation_euler = (math.radians(55), 0, math.radians(-35))
bpy.ops.object.light_add(type="AREA", location=(4, 3, 3))
r = bpy.context.object; r.data.energy = 500; r.data.size = 2; r.data.color = (0.8, 0.88, 1.0); r.rotation_euler = (math.radians(-60), 0, math.radians(140))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[1].default_value = 0.35

bpy.ops.object.empty_add(location=(0, 0, 0.55))
aim = bpy.context.object
bpy.ops.object.camera_add(location=(1.1, -9.4, 3.0))
cam = bpy.context.object; sc.camera = cam
cam.data.lens = 60
c = cam.constraints.new("TRACK_TO"); c.target = aim; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
board_center = board


def render(path, hide):
    for o in hide:
        o.hide_render = True
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    for o in hide:
        o.hide_render = False


render(os.path.join(OUT, "board.png"), [top])
render(os.path.join(OUT, "stick.png"), [o for o in bpy.data.objects if o.type in {"MESH", "FONT"} and o is not top])

# Where the hinge pin lands in the frame, for the page's transform-origin.
from bpy_extras.object_utils import world_to_camera_view
import mathutils
v = world_to_camera_view(sc, cam, mathutils.Vector(pivot))
json.dump({"pivot_px": [round(v.x * sc.render.resolution_x), round((1 - v.y) * sc.render.resolution_y)],
           "open_deg": OPEN, "size": [sc.render.resolution_x, sc.render.resolution_y]},
          open(os.path.join(OUT, "clapper.json"), "w"))
print("CLAPPER DONE", OUT)
