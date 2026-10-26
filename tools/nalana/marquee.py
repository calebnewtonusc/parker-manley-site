"""A real theater marquee for each featured film, rendered in Nalana (Cycles).
Steel box, chrome trim, glass bulbs with uneven glow, a backlit acrylic panel
with fluorescent banding and grime, extruded plastic letters on rails, shot
from below at an angle on a 50mm with shallow focus, bloom and grain.

    Nalana -b --factory-startup --python marquee.py -- OUTDIR "TITLE" "META" [samples]
"""
import math
import random
import sys

import bpy

argv = sys.argv[sys.argv.index("--") + 1:]
OUT, TITLE, META = argv[0], argv[1], argv[2]
SAMPLES = int(argv[3]) if len(argv) > 3 else 64
random.seed(7)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = True
try:
    sc.cycles.device = "GPU"
except TypeError:
    pass
sc.render.resolution_x, sc.render.resolution_y = 1800, 640
vt = [i.identifier for i in bpy.types.ColorManagedViewSettings.bl_rna.properties["view_transform"].enum_items]
sc.view_settings.view_transform = "AgX" if "AgX" in vt else "Filmic"
sc.view_settings.look = "None"
DIN = "/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf"
font = bpy.data.fonts.load(DIN)


def bsdf(name, color, rough=0.4, metal=0.0, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    for k in ("Coat Weight", "Clearcoat"):
        if k in b.inputs:
            b.inputs[k].default_value = coat
    return m, b


def grime(m, b, scale=6.0, amount=0.35):
    """Darken the base color with a noise mask: dirt, water streaks."""
    nt = m.node_tree
    tex = nt.nodes.new("ShaderNodeTexNoise"); tex.inputs["Scale"].default_value = scale; tex.inputs["Detail"].default_value = 8
    ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.color_ramp.elements[0].position = 0.45; ramp.color_ramp.elements[1].position = 0.75
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"
    mix.inputs[0].default_value = amount
    base = b.inputs["Base Color"].default_value[:]
    mix.inputs[6].default_value = base
    nt.links.new(tex.outputs["Fac"], ramp.inputs[0]); nt.links.new(ramp.outputs[0], mix.inputs[7])
    nt.links.new(mix.outputs[2], b.inputs["Base Color"])


def box(name, size, loc, mat, bevel=0.004):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object; o.name = name; o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    md = o.modifiers.new("b", "BEVEL"); md.width = bevel; md.segments = 2
    o.data.materials.append(mat)
    return o


W, H = 3.6, 1.2
steel, sb = bsdf("steel", (0.05, 0.045, 0.04), rough=0.55, metal=0.6); grime(steel, sb, 9, 0.5)
chrome, _ = bsdf("chrome", (0.9, 0.9, 0.92), rough=0.12, metal=1.0)
box("frame", (W + 0.36, 0.22, H + 0.46), (0, 0.08, 0), steel, 0.02)
for z in (H / 2 + 0.215, -H / 2 - 0.215):
    box("trim", (W + 0.36, 0.06, 0.03), (0, -0.04, z), chrome, 0.006)

# The panel: translucent acrylic lit from behind by tubes, so the light bands.
panel = bpy.data.materials.new("panel"); panel.use_nodes = True
nt = panel.node_tree
for n in list(nt.nodes):
    nt.nodes.remove(n)
outp = nt.nodes.new("ShaderNodeOutputMaterial")
emi = nt.nodes.new("ShaderNodeEmission")
diff = nt.nodes.new("ShaderNodeBsdfPrincipled")
diff.inputs["Base Color"].default_value = (0.92, 0.9, 0.84, 1); diff.inputs["Roughness"].default_value = 0.35
tc = nt.nodes.new("ShaderNodeTexCoord")
wave = nt.nodes.new("ShaderNodeTexWave"); wave.wave_type = "BANDS"; wave.bands_direction = "X"; wave.inputs["Scale"].default_value = 2.2
noise = nt.nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 3; noise.inputs["Detail"].default_value = 10
ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].color = (0.62, 0.58, 0.5, 1); ramp.color_ramp.elements[1].color = (1.0, 0.97, 0.88, 1)
mixc = nt.nodes.new("ShaderNodeMix"); mixc.data_type = "RGBA"; mixc.blend_type = "MULTIPLY"; mixc.inputs[0].default_value = 0.35
st = nt.nodes.new("ShaderNodeMath"); st.operation = "MULTIPLY"; st.inputs[1].default_value = 2.4
add = nt.nodes.new("ShaderNodeAddShader")
L = nt.links.new
L(tc.outputs["Object"], wave.inputs["Vector"]); L(tc.outputs["Object"], noise.inputs["Vector"])
L(wave.outputs["Fac"], ramp.inputs[0]); L(ramp.outputs[0], mixc.inputs[6]); L(noise.outputs["Color"], mixc.inputs[7])
L(mixc.outputs[2], emi.inputs["Color"]); L(wave.outputs["Fac"], st.inputs[0]); emi.inputs["Strength"].default_value = 2.2
L(diff.outputs[0], add.inputs[0]); L(emi.outputs[0], add.inputs[1]); L(add.outputs[0], outp.inputs["Surface"])
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -0.031, 0), rotation=(math.radians(90), 0, 0))
pl = bpy.context.object; pl.scale = (W, H, 1); pl.data.materials.append(panel)

# Rails the letters hang on.
rail, _ = bsdf("rail", (0.35, 0.34, 0.3), rough=0.4, metal=0.7)
rows = [0.36, 0.0, -0.36]
for z in (0.18, -0.18, 0.54, -0.54):
    box("rail", (W, 0.012, 0.012), (0, -0.04, z), rail, 0.002)

plastic_k, _ = bsdf("letter_black", (0.012, 0.012, 0.012), rough=0.28, coat=0.6)
plastic_r, _ = bsdf("letter_red", (0.5, 0.03, 0.035), rough=0.3, coat=0.6)


def letters(text, z, size, mat, track):
    objs = []
    x = 0.0
    for ch in text:
        if ch == " ":
            x += size * 0.38
            continue
        bpy.ops.object.text_add(location=(0, -0.05, z), rotation=(math.radians(90), 0, 0))
        t = bpy.context.object
        t.data.body = ch; t.data.font = font; t.data.size = size; t.data.extrude = 0.006
        t.data.align_x = "LEFT"; t.data.align_y = "CENTER"
        t.data.materials.append(mat)
        bpy.context.view_layer.update()
        w = t.dimensions.x
        t.location.x = x
        t.rotation_euler.y = math.radians(random.uniform(-1.6, 1.6))
        t.location.z += random.uniform(-0.006, 0.006)
        objs.append((t, w))
        x += w + track
    total = x - track
    for t, w in objs:
        t.location.x -= total / 2
    return objs


letters("NOW SHOWING", rows[0], 0.22, plastic_r, 0.035)
tsize = 0.3 if len(TITLE) <= 16 else 0.24
letters(TITLE.upper(), rows[1], tsize, plastic_k, 0.03)
letters(META.upper(), rows[2], 0.17, plastic_k, 0.03)

# Bulbs: a socket, a glass envelope, a filament glow, no two the same.
glass = bpy.data.materials.new("glass"); glass.use_nodes = True
gb = next(n for n in glass.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
gb.inputs["Transmission Weight" if "Transmission Weight" in gb.inputs else "Transmission"].default_value = 1.0
gb.inputs["Roughness"].default_value = 0.05
socket, _ = bsdf("socket", (0.6, 0.55, 0.45), rough=0.3, metal=1.0)
dead = random.randrange(8, 30)
n = 0
for z in (H / 2 + 0.11, -H / 2 - 0.11):
    x = -W / 2 - 0.06
    while x <= W / 2 + 0.07:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.026, depth=0.03, location=(x, -0.02, z), rotation=(math.radians(90), 0, 0))
        bpy.context.object.data.materials.append(socket)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.034, location=(x, -0.05, z), segments=24, ring_count=12)
        g = bpy.context.object; g.data.materials.append(glass)
        if n != dead:
            fm = bpy.data.materials.new(f"fil{n}"); fm.use_nodes = True
            fnt = fm.node_tree; fo = fnt.nodes["Material Output"]
            for nn in list(fnt.nodes):
                if nn != fo:
                    fnt.nodes.remove(nn)
            e = fnt.nodes.new("ShaderNodeEmission")
            e.inputs["Color"].default_value = (1.0, 0.62 + random.uniform(-0.05, 0.05), 0.28, 1)
            e.inputs["Strength"].default_value = random.uniform(70, 160)
            fnt.links.new(e.outputs[0], fo.inputs["Surface"])
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.008, location=(x, -0.05, z))
            bpy.context.object.data.materials.append(fm)
        n += 1
        x += 0.12

# Night: a dim sky, a warm practical bouncing off the front, a cool fill.
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.012, 0.016, 0.03, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.6
bpy.ops.object.light_add(type="AREA", location=(0, -2.2, -1.6))
k = bpy.context.object; k.data.energy = 60; k.data.size = 3; k.data.color = (1, 0.8, 0.6); k.rotation_euler = (math.radians(-55), 0, 0)

# Camera: from the sidewalk, below and to the left, a 50mm wide open.
bpy.ops.object.empty_add(location=(0.25, 0, 0.0)); aim = bpy.context.object
bpy.ops.object.camera_add(location=(-1.15, -4.6, -1.05)); cam = bpy.context.object; sc.camera = cam
cam.data.lens = 50
c = cam.constraints.new("TRACK_TO"); c.target = aim; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
cam.data.dof.use_dof = True; cam.data.dof.focus_object = aim; cam.data.dof.aperture_fstop = 2.0

# Bloom is added after the render (Blender 5 moved the compositor tree).
sc.render.filepath = OUT
sc.render.image_settings.file_format = "PNG"
bpy.ops.render.render(write_still=True)
print("MARQUEE DONE", OUT)
