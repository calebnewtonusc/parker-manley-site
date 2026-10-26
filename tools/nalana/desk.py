"""Real paper objects for the About section, rendered alone on a shadow
catcher so the page can still move them (hover lifts a polaroid).

  Nalana -b --factory-startup --python-exit-code 1 --python desk.py -- sheet tex.png out.png
  Nalana -b --factory-startup --python-exit-code 1 --python desk.py -- polaroid photo.jpg out.png SEED

The camera is orthographic and straight down, so the printed sheet stays in
register with the HTML text laid over it (highlighter hover, screen readers).
"""
import math
import random
import sys

import bpy

argv = sys.argv[sys.argv.index("--") + 1:]
kind, tex, out = argv[0], argv[1], argv[2]
seed = int(argv[3]) if len(argv) > 3 else 1
rng = random.Random(seed)

scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

scene.render.engine = "CYCLES"
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "METAL"
    prefs.get_devices()
    for d in prefs.devices:
        d.use = True
    scene.cycles.device = "GPU"
except Exception:
    pass
scene.cycles.samples = 160
scene.cycles.use_denoising = True
scene.render.film_transparent = True
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Base Contrast"
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"

world = bpy.data.worlds.new("w")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[1].default_value = 0.04


def node(nt, t, **kw):
    n = nt.nodes.new(t)
    for k, v in kw.items():
        n.inputs[k].default_value = v
    return n


def bsdf(mat):
    return next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def paper_material(name, image_path, warm=(0.965, 0.955, 0.93, 1)):
    """Printed paper: the print multiplied into a slightly warm sheet, matte,
    with a fibre bump so the raking light catches the surface."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    b = bsdf(mat)
    b.inputs["Roughness"].default_value = 0.88
    paper = node(nt, "ShaderNodeRGB")
    paper.outputs[0].default_value = warm
    if image_path:
        img = nt.nodes.new("ShaderNodeTexImage")
        img.image = bpy.data.images.load(image_path)
        img.interpolation = "Cubic"
        mul = nt.nodes.new("ShaderNodeMix")
        mul.data_type = "RGBA"
        mul.blend_type = "MULTIPLY"
        mul.inputs["Factor"].default_value = 1.0
        nt.links.new(paper.outputs[0], mul.inputs[6])
        nt.links.new(img.outputs[0], mul.inputs[7])
        nt.links.new(mul.outputs[2], b.inputs["Base Color"])
    else:
        nt.links.new(paper.outputs[0], b.inputs["Base Color"])
    fib = nt.nodes.new("ShaderNodeTexNoise")
    fib.inputs["Scale"].default_value = 900.0
    fib.inputs["Detail"].default_value = 8.0
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.06
    bump.inputs["Distance"].default_value = 0.0004
    nt.links.new(fib.outputs[0], bump.inputs["Height"])
    nt.links.new(bump.outputs[0], b.inputs["Normal"])
    return mat


def plane(name, w, h, cuts=0):
    bpy.ops.mesh.primitive_plane_add(size=1)
    o = bpy.context.active_object
    o.name = name
    o.scale = (w, h, 1)
    bpy.ops.object.transform_apply(scale=True)
    if cuts:
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.subdivide(number_cuts=cuts)
        bpy.ops.object.mode_set(mode="OBJECT")
    return o


def bend(o, corner_lift, wave):
    """A sheet that has been handled: one corner lifts off the table and the
    middle carries a faint wave. Small, so the print stays in register."""
    xs = [v.co.x for v in o.data.vertices]
    ys = [v.co.y for v in o.data.vertices]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    for v in o.data.vertices:
        u = (v.co.x - x0) / (x1 - x0)
        t = (v.co.y - y0) / (y1 - y0)
        lift = corner_lift * max(0.0, (u - 0.72) / 0.28) ** 2 * max(0.0, (0.3 - t) / 0.3) ** 2
        v.co.z = lift + wave * math.sin(u * math.pi * 1.3 + 0.4) * math.sin(t * math.pi)


def catcher(size):
    c = plane("floor", size, size)
    c.location.z = -0.0006
    c.is_shadow_catcher = True
    return c


def lights(w, h):
    key = bpy.data.lights.new("key", "AREA")
    key.energy = 260 * max(w, h) ** 2
    key.size = max(w, h) * 0.6
    k = bpy.data.objects.new("key", key)
    k.location = (-w * 1.4, h * 1.2, max(w, h) * 1.1)
    k.rotation_euler = (math.radians(50), 0, math.radians(-130))
    k.rotation_euler = (0, 0, 0)
    direction = -k.location.normalized()
    k.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(k)
    fill = bpy.data.lights.new("fill", "AREA")
    fill.energy = 40 * max(w, h) ** 2
    fill.size = max(w, h) * 2
    f = bpy.data.objects.new("fill", fill)
    f.location = (w, -h, max(w, h) * 2)
    f.rotation_euler = (-f.location.normalized()).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(f)


def camera(w, h, margin, px_w):
    cam = bpy.data.cameras.new("cam")
    cam.type = "ORTHO"
    cam.ortho_scale = max(w, h) * (1 + 2 * margin)
    c = bpy.data.objects.new("cam", cam)
    c.location = (0, 0, 2)
    scene.collection.objects.link(c)
    scene.camera = c
    scene.render.resolution_x = px_w
    scene.render.resolution_y = round(px_w * (h * (1 + 2 * margin * max(w, h) / h)) / (w * (1 + 2 * margin * max(w, h) / w)))
    scene.render.resolution_percentage = 100
    # ortho_scale covers the longer side; the margin is in units of it.


if kind == "sheet":
    img = bpy.data.images.load(tex)
    iw, ih = img.size
    w = 0.216  # letter width in metres
    h = w * ih / iw
    s = plane("sheet", w, h, cuts=80)
    bend(s, corner_lift=0.006, wave=0.0007)
    s.data.materials.append(paper_material("print", tex))
    catcher(w * 3)
    lights(w, h)
    margin = 0.06
    camera(w, h, margin, 2000)
else:
    # Polaroid 600: 88 x 107 mm card, 79 x 79 mm image, wide bottom lip.
    w, h = 0.088, 0.107
    card = plane("card", w, h)
    bpy.ops.object.modifier_add(type="SOLIDIFY")
    card.modifiers["Solidify"].thickness = 0.0009
    card.data.materials.append(paper_material("card", None, warm=(0.95, 0.94, 0.91, 1)))
    photo = plane("photo", 0.079, 0.079, cuts=0)
    photo.location = (0, h / 2 - 0.0045 - 0.0395, 0.0001)
    pm = bpy.data.materials.new("photo")
    pm.use_nodes = True
    pb = bsdf(pm)
    im = pm.node_tree.nodes.new("ShaderNodeTexImage")
    im.image = bpy.data.images.load(tex)
    # Square crop from the centre, like the print itself.
    mapn = pm.node_tree.nodes.new("ShaderNodeMapping")
    coord = pm.node_tree.nodes.new("ShaderNodeTexCoord")
    ar = im.image.size[0] / im.image.size[1]
    if ar > 1:
        mapn.inputs["Scale"].default_value = (1 / ar, 1, 1)
        mapn.inputs["Location"].default_value = ((1 - 1 / ar) / 2, 0, 0)
    else:
        mapn.inputs["Scale"].default_value = (1, ar, 1)
        mapn.inputs["Location"].default_value = (0, (1 - ar) / 2, 0)
    pm.node_tree.links.new(coord.outputs["UV"], mapn.inputs["Vector"])
    pm.node_tree.links.new(mapn.outputs[0], im.inputs["Vector"])
    pm.node_tree.links.new(im.outputs[0], pb.inputs["Base Color"])
    pb.inputs["Roughness"].default_value = 0.32
    pb.inputs["Coat Weight"].default_value = 0.6
    pb.inputs["Coat Roughness"].default_value = 0.12
    photo.data.materials.append(pm)
    # A strip of matte tape across the top edge, a little crooked.
    tape = plane("tape", 0.042, 0.016, cuts=16)
    tape.location = (rng.uniform(-0.006, 0.006), h / 2 - 0.002, 0.0011)
    tape.rotation_euler.z = math.radians(rng.uniform(-6, 6))
    # Tape is torn by hand, so the short ends are ragged, never square.
    half = 0.021
    for v in tape.data.vertices:
        v.co.z = 0.00012 * math.sin(v.co.x * 900 + seed)
        if abs(abs(v.co.x) - half) < 1e-6:
            v.co.x += (1 if v.co.x > 0 else -1) * rng.uniform(-0.0016, 0.0006)
    tm = bpy.data.materials.new("tape")
    tm.use_nodes = True
    tb = bsdf(tm)
    tb.inputs["Base Color"].default_value = (0.93, 0.9, 0.82, 1)
    tb.inputs["Roughness"].default_value = 0.55
    tb.inputs["Transmission Weight"].default_value = 0.5
    tb.inputs["Alpha"].default_value = 0.72
    tape.data.materials.append(tm)
    for o in (card, photo, tape):
        o.select_set(False)
    catcher(w * 4)
    lights(w, h)
    camera(w, h, 0.12, 900)

scene.render.filepath = out
bpy.ops.render.render(write_still=True)
print("DESK_DONE", out)
