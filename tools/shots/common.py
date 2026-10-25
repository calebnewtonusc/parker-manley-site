"""Shared helpers for the T Combinator shots (docs/SHOTS-tc.md).

Run inside Nalana headless:
  nice -n 19 /Applications/Nalana.app/Contents/MacOS/Nalana -b --factory-startup --python shotN.py -- out.png
"""
import math
import random
import sys

import bpy
import bmesh


def out_path(default):
    argv = sys.argv
    return argv[argv.index("--") + 1] if "--" in argv else default


def reset(w=1920, h=1080):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = w
    sc.render.resolution_y = h
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    # Flat colour: what the material says is what lands in the frame.
    try:
        sc.view_settings.view_transform = "Standard"
    except TypeError:
        pass
    sc.view_settings.look = "None"
    if not sc.world:
        sc.world = bpy.data.worlds.new("World")
    return sc


def hexc(h, a=1.0):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    # sRGB to linear, so a hex picked by eye renders as that hex.
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (f(r), f(g), f(b), a)


def flat(name, color, strength=1.0):
    """An unlit material: the colour is the pixel. Shadow and light are drawn,
    not simulated, so every surface is a flat shape."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = hexc(color) if isinstance(color, str) else color
    em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


def vertex_lit(name, strength=1.0):
    """Unlit, coloured per face corner from the 'col' attribute."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    at = nt.nodes.new("ShaderNodeAttribute")
    at.attribute_name = "col"
    nt.links.new(at.outputs["Color"], em.inputs["Color"])
    em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


def mesh_obj(name, bm, mat, collection=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    (collection or bpy.context.scene.collection).objects.link(ob)
    if mat:
        ob.data.materials.append(mat)
    return ob


LIGHT_GAIN = 3.0


def lights_mesh(name, pts, collection=None):
    """Thousands of small camera-facing quads in one mesh, each with its own
    colour. pts: (x, y, z, size, (r,g,b,a))."""
    bm = bmesh.new()
    col = bm.loops.layers.float_color.new("col")
    for x, y, z, s, c in pts:
        # Two diamonds crossed, one standing and one lying flat, so a light
        # reads as a point from a low camera and from a crane above it (one
        # standing diamond went edge-on and drew as a triangle when shot 1
        # rose over the ridge, 2026-10-09).
        for vs in (((x - s, y, z), (x, y, z - s), (x + s, y, z), (x, y, z + s)),
                   ((x - s, y, z), (x, y - s, z), (x + s, y, z), (x, y + s, z))):
            f = bm.faces.new([bm.verts.new(v) for v in vs])
            for lp in f.loops:
                lp[col] = c
    # Brighter than paper white, so the bloom in paint_pass takes them.
    return mesh_obj(name, bm, vertex_lit(name + "_m", LIGHT_GAIN), collection)


def profile(name, xs_zs, y, bottom, mat, collection=None):
    """An extruded silhouette: a crest line at depth y down to `bottom`."""
    bm = bmesh.new()
    top = [bm.verts.new((x, y, z)) for x, z in xs_zs]
    bot = [bm.verts.new((x, y, bottom)) for x, _ in xs_zs]
    for i in range(len(top) - 1):
        bm.faces.new((bot[i], bot[i + 1], top[i + 1], top[i]))
    return mesh_obj(name, bm, mat, collection)


def camera(loc, rot_deg, lens=24.0):
    cd = bpy.data.cameras.new("cam")
    cd.lens = lens
    cd.sensor_width = 36
    cd.clip_end = 40000
    cam = bpy.data.objects.new("cam", cd)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = loc
    cam.rotation_euler = tuple(math.radians(a) for a in rot_deg)
    bpy.context.scene.camera = cam
    return cam


def banded_sky(stops, wobble=0.035, scale=3.0):
    """A screen-space sky in hard bands (constant ramp), its edges wobbled by
    noise like a loaded brush, so the gradient is killed but not ruled."""
    w = bpy.context.scene.world
    w.use_nodes = True
    nt = w.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = scale
    noise.inputs["Detail"].default_value = 6.0
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY_ADD"
    mul.inputs[1].default_value = wobble
    mul.inputs[2].default_value = -wobble / 2
    add = nt.nodes.new("ShaderNodeMath")
    add.operation = "ADD"
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    els = ramp.color_ramp.elements
    while len(els) > 1:
        els.remove(els[-1])
    els[0].position = 0.0
    els[0].color = hexc(stops[0][1])
    for pos, c in stops[1:]:
        e = els.new(pos)
        e.color = hexc(c)
    nt.links.new(tc.outputs["Window"], sep.inputs[0])
    nt.links.new(tc.outputs["Window"], noise.inputs["Vector"])
    nt.links.new(noise.outputs["Fac"], mul.inputs[0])
    nt.links.new(sep.outputs["Y"], add.inputs[0])
    nt.links.new(mul.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 1.0
    nt.links.new(bg.outputs[0], out.inputs["Surface"])


def lineart(collection, color="#120a1e", thickness=3, name="ink"):
    """Grease Pencil Line Art on one collection: silhouettes inked in 3D."""
    bpy.ops.object.grease_pencil_add(type="LINEART_COLLECTION")
    gp = bpy.context.active_object
    gp.name = name
    for md in gp.modifiers:
        if md.type == "LINEART":
            md.source_type = "COLLECTION"
            md.source_collection = collection
            try:
                md.thickness = thickness
            except AttributeError:
                md.radius = thickness / 1000
    mat = gp.data.materials[0] if gp.data.materials else None
    if mat and mat.grease_pencil:
        mat.grease_pencil.color = hexc(color)
    return gp


def paint_pass(size=6):
    """Compositor: an anisotropic Kuwahara pass, so flat shapes take a brush
    edge. Blender 5 keeps the compositor in a node group on the scene."""
    sc = bpy.context.scene
    try:
        tree = bpy.data.node_groups.new("paint", "CompositorNodeTree")
        sc.compositing_node_group = tree
        rl = tree.nodes.new("CompositorNodeRLayers")
        kw = tree.nodes.new("CompositorNodeKuwahara")
        out = tree.nodes.new("NodeGroupOutput")
        tree.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        try:
            kw.variation = "ANISOTROPIC"
        except (AttributeError, TypeError):
            pass
        size_in = kw.inputs.get("Size")
        if size_in is not None:
            size_in.default_value = size
        else:
            kw.size = size
        tree.links.new(rl.outputs["Image"], kw.inputs["Image"])
        tree.links.new(kw.outputs["Image"], out.inputs[0])
        return True
    except Exception as exc:  # report and render without the pass
        print("PAINT_PASS_FAILED", repr(exc))
        return False


def render(path):
    sc = bpy.context.scene
    sc.render.filepath = path
    sc.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    print("RENDERED", path)


rng = random.Random(20261009)


def export_points(tag, world_pts, frame, frames, pink=None):
    """Write where the shared lights of this shot land on screen, for the
    morphs between shots (morph.py). Only on the first and last frame, and
    only when TC_POINTS names a directory. world_pts: [(x, y, z, (r,g,b,a))];
    pink: the founder's light, (x, y, z) or None. Screen u, v run 0 to 1 from
    the bottom left of the square frame."""
    import json
    import os
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector
    d = os.environ.get("TC_POINTS")
    if not d or frame not in (0, frames - 1):
        return
    os.makedirs(d, exist_ok=True)
    sc = bpy.context.scene
    bpy.context.view_layer.update()
    cam = sc.camera

    def proj(p):
        v = world_to_camera_view(sc, cam, Vector(p[:3]))
        return v.x, v.y, v.z

    out = {"pts": [], "pink": None}
    for x, y, z, c in world_pts:
        u, v, depth = proj((x, y, z))
        if depth > 0 and -0.2 < u < 1.2 and -0.2 < v < 1.2:
            out["pts"].append([round(u, 5), round(v, 5), [round(k, 4) for k in c[:3]]])
    if pink is not None:
        u, v, depth = proj(pink)
        out["pink"] = [round(u, 5), round(v, 5)]
    end = "first" if frame == 0 else "last"
    with open(os.path.join(d, f"{tag}_{end}.json"), "w") as fh:
        json.dump(out, fh)
    print("POINTS", tag, end, len(out["pts"]))
