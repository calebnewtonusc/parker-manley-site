"""Lighting and materials for the second pass of the shots (docs/SHOTS-tc.md).

The first pass was flat colour and read as a vector poster. The film's
frames get their depth from light: a real sky, haze that lightens with
distance, lamps that pool on surfaces, rim light on silhouettes. This
module gives the shot scripts those pieces. Built for Blender 5.1 (Nalana).
"""
import math

import bpy

from common import hexc


def square(size=None):
    """Square frames: the 16:9 film and the 9:16 phone cut are both crops of
    one render, so nothing is rendered twice. Compose inside the centre.
    2560 by default (TC_SIZE overrides): at 1280 the film was soft on every
    retina screen ("so ass and so blurry", Caleb, 2026-10-09)."""
    import os
    size = size or int(os.environ.get("TC_SIZE", "2560"))
    sc = bpy.context.scene
    sc.render.resolution_x = size
    sc.render.resolution_y = size
    return sc


def view(look="punchy", exposure=0.0):
    sc = bpy.context.scene
    try:
        sc.view_settings.view_transform = "AgX"
        looks = [i.identifier for i in sc.view_settings.bl_rna.properties["look"].enum_items]
        pick = next((l for l in looks if "Punchy" in l), "None") if look == "punchy" else "None"
        sc.view_settings.look = pick
    except TypeError:
        sc.view_settings.view_transform = "Standard"
    sc.view_settings.exposure = exposure


def volumetrics(end=30000.0, tile=8, samples=48):
    e = bpy.context.scene.eevee
    e.volumetric_start = 0.5
    e.volumetric_end = end
    e.volumetric_tile_size = str(tile)
    e.volumetric_samples = samples
    e.use_volumetric_shadows = True
    try:
        e.use_shadows = True
    except AttributeError:
        pass


def sky(elevation=0.5, rotation=0.0, strength=1.0, density=0.0, haze="#c9a3c9",
        anisotropy=0.4, tint=None, tint_mix=0.0, box=(30000.0, 30000.0, 1200.0), box_center=(0.0, 0.0, 0.0),
        paint=None, paint_scale=1.3, paint_wobble=0.12, paint_strength=1.0):
    """A physical sky (multiple scattering) as the world light, an optional
    tint mixed over it to push the shot's hue, and a box of haze for
    atmospheric perspective. The haze is an object, not the world volume:
    EEVEE's world volume swallowed the whole sky (mean pixel 0.58 without
    it, 0.00 with it, 2026-10-09 test render)."""
    w = bpy.context.scene.world
    w.use_nodes = True
    nt = w.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    sk = nt.nodes.new("ShaderNodeTexSky")
    sk.sky_type = "MULTIPLE_SCATTERING"
    sk.sun_elevation = math.radians(elevation)
    sk.sun_rotation = math.radians(rotation)
    sk.sun_disc = True
    src = sk.outputs["Color"]
    if tint is not None and tint_mix > 0:
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MULTIPLY"
        mix.inputs["Factor"].default_value = tint_mix
        nt.links.new(src, mix.inputs[6])
        mix.inputs[7].default_value = hexc(tint)
        src = mix.outputs[2]
    nt.links.new(src, bg.inputs["Color"])
    bg.inputs["Strength"].default_value = strength
    surface = bg.outputs[0]
    if paint:
        # What the camera sees is painted: a smooth ramp over screen height,
        # pushed around by broad noise like a loaded brush. Everything else
        # (the light on the scene) still comes from the physical sky.
        tc = nt.nodes.new("ShaderNodeTexCoord")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = paint_scale
        nz.inputs["Detail"].default_value = 4.0
        nz.inputs["Roughness"].default_value = 0.55
        ma = nt.nodes.new("ShaderNodeMath")
        ma.operation = "MULTIPLY_ADD"
        ma.inputs[1].default_value = paint_wobble
        ma.inputs[2].default_value = -paint_wobble / 2
        add = nt.nodes.new("ShaderNodeMath")
        add.operation = "ADD"
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.interpolation = "EASE"
        els = ramp.color_ramp.elements
        while len(els) > 1:
            els.remove(els[-1])
        els[0].position = paint[0][0]
        els[0].color = hexc(paint[0][1])
        for pos, c in paint[1:]:
            e = els.new(pos)
            e.color = hexc(c)
        nt.links.new(tc.outputs["Window"], sep.inputs[0])
        nt.links.new(tc.outputs["Window"], nz.inputs["Vector"])
        nt.links.new(nz.outputs["Fac"], ma.inputs[0])
        nt.links.new(sep.outputs["Y"], add.inputs[0])
        nt.links.new(ma.outputs[0], add.inputs[1])
        nt.links.new(add.outputs[0], ramp.inputs["Fac"])
        pbg = nt.nodes.new("ShaderNodeBackground")
        pbg.inputs["Strength"].default_value = paint_strength
        nt.links.new(ramp.outputs["Color"], pbg.inputs["Color"])
        lp = nt.nodes.new("ShaderNodeLightPath")
        mix = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs["Fac"])
        nt.links.new(surface, mix.inputs[1])
        nt.links.new(pbg.outputs[0], mix.inputs[2])
        surface = mix.outputs[0]
    nt.links.new(surface, out.inputs["Surface"])
    if density > 0:
        import bmesh
        m = bpy.data.materials.new("haze")
        m.use_nodes = True
        mt = m.node_tree
        for n in list(mt.nodes):
            mt.nodes.remove(n)
        mo = mt.nodes.new("ShaderNodeOutputMaterial")
        vol = mt.nodes.new("ShaderNodeVolumeScatter")
        vol.inputs["Color"].default_value = hexc(haze)
        vol.inputs["Density"].default_value = density
        vol.inputs["Anisotropy"].default_value = anisotropy
        mt.links.new(vol.outputs[0], mo.inputs["Volume"])
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        me = bpy.data.meshes.new("haze")
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new("haze", me)
        bpy.context.scene.collection.objects.link(ob)
        ob.scale = box
        ob.location = (box_center[0], box_center[1], box_center[2] + box[2] / 2 - 20)
        me.materials.append(m)


def lit(name, color, rough=0.85, metal=0.0, rim=None, rim_strength=2.0, rim_power=0.35,
        emit=None, emit_strength=0.0):
    """A lit surface. `rim` adds light along the silhouette from a facing
    ratio, which is how an illustrator rims a figure against the sky."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    p.inputs["Base Color"].default_value = hexc(color)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if emit:
        p.inputs["Emission Color"].default_value = hexc(emit)
        p.inputs["Emission Strength"].default_value = emit_strength
    shader = p.outputs[0]
    if rim:
        lw = nt.nodes.new("ShaderNodeLayerWeight")
        lw.inputs["Blend"].default_value = rim_power
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = hexc(rim)
        ramp = nt.nodes.new("ShaderNodeMath")
        ramp.operation = "POWER"
        ramp.inputs[1].default_value = 3.0
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        mul.inputs[1].default_value = rim_strength
        nt.links.new(lw.outputs["Facing"], ramp.inputs[0])
        nt.links.new(ramp.outputs[0], mul.inputs[0])
        nt.links.new(mul.outputs[0], em.inputs["Strength"])
        add = nt.nodes.new("ShaderNodeAddShader")
        nt.links.new(shader, add.inputs[0])
        nt.links.new(em.outputs[0], add.inputs[1])
        shader = add.outputs[0]
    nt.links.new(shader, out.inputs[0])
    return m


def glow(name, color, strength=8.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = hexc(color)
    em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


def windows(name, wall, lit_color, density=0.25, scale=(18.0, 26.0), strength=6.0, rough=0.25, metal=0.6):
    """Glass and steel with a grid of windows, some lit: a brick texture
    gives the grid, a noise picks which windows are on."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    p.inputs["Base Color"].default_value = hexc(wall)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (scale[0] / 100, scale[0] / 100, scale[1] / 100)
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.offset = 0.0
    br.inputs["Mortar Size"].default_value = 0.18
    br.inputs["Color1"].default_value = (1, 1, 1, 1)
    br.inputs["Color2"].default_value = (1, 1, 1, 1)
    br.inputs["Mortar"].default_value = (0, 0, 0, 1)
    nz = nt.nodes.new("ShaderNodeTexWhiteNoise")
    nz.noise_dimensions = "3D"
    snap = nt.nodes.new("ShaderNodeVectorMath")
    snap.operation = "SNAP"
    snap.inputs[1].default_value = (0.5, 0.5, 0.5)
    gt = nt.nodes.new("ShaderNodeMath")
    gt.operation = "GREATER_THAN"
    gt.inputs[1].default_value = 1.0 - density
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], br.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], snap.inputs[0])
    nt.links.new(snap.outputs[0], nz.inputs["Vector"])
    nt.links.new(nz.outputs["Value"], gt.inputs[0])
    nt.links.new(br.outputs["Fac"], mul.inputs[0])
    nt.links.new(gt.outputs[0], mul.inputs[1])
    p.inputs["Emission Color"].default_value = hexc(lit_color)
    em = nt.nodes.new("ShaderNodeMath")
    em.operation = "MULTIPLY"
    em.inputs[1].default_value = strength
    nt.links.new(mul.outputs[0], em.inputs[0])
    nt.links.new(em.outputs[0], p.inputs["Emission Strength"])
    nt.links.new(p.outputs[0], out.inputs[0])
    return m


def lamp(kind, loc, color, energy, size=1.0, rot=(0, 0, 0), spot=None):
    ld = bpy.data.lights.new(kind.lower(), kind)
    ld.color = hexc(color)[:3]
    ld.energy = energy
    if kind == "AREA":
        ld.size = size
    elif kind in ("POINT", "SPOT"):
        ld.shadow_soft_size = size
    if kind == "SPOT" and spot:
        ld.spot_size = math.radians(spot)
        ld.spot_blend = 0.6
    ob = bpy.data.objects.new(ld.name, ld)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = tuple(math.radians(a) for a in rot)
    return ob


GLOW = 0.7


def paint_pass(size=3):
    """A light Kuwahara: it takes the render edge off. The brushwork itself
    comes from paintover.py, which follows the forms."""
    sc = bpy.context.scene
    tree = bpy.data.node_groups.new("paint", "CompositorNodeTree")
    sc.compositing_node_group = tree
    rl = tree.nodes.new("CompositorNodeRLayers")
    kw = tree.nodes.new("CompositorNodeKuwahara")
    out = tree.nodes.new("NodeGroupOutput")
    tree.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    kw.inputs["Size"].default_value = size
    try:
        kw.inputs["Type"].default_value = "Anisotropic"
    except (TypeError, KeyError):
        pass
    tree.links.new(rl.outputs["Image"], kw.inputs["Image"])
    # Bloom on anything brighter than paper white: the city lights, lit
    # windows, the founder's light and the stadium lamps glow into the air
    # around them, and nothing else does. Without it every light was a hard
    # 2px chip and the frames read as a flat vector poster ("It just looks
    # 2d", Caleb, 2026-10-09).
    gl = tree.nodes.new("CompositorNodeGlare")
    for k, v in (("Type", "Bloom"), ("Quality", "High")):
        try:
            gl.inputs[k].default_value = v
        except (TypeError, KeyError):
            pass
    gl.inputs["Threshold"].default_value = 1.0
    gl.inputs["Smoothness"].default_value = 0.3
    gl.inputs["Strength"].default_value = GLOW
    gl.inputs["Size"].default_value = 0.55
    gl.inputs["Saturation"].default_value = 1.15
    tree.links.new(kw.outputs["Image"], gl.inputs["Image"])
    tree.links.new(gl.outputs["Image"], out.inputs[0])
