"""Art-directed light for the shots (docs/SHOTS-tc.md).

A physically lit pass (lit.py) went muddy: AgX and volume haze turned the
rose horizon green and flattened the planes into one dark band (2026-10-09
renders). Here every surface is an exact painted colour and the light is
designed into it, the way a background painter lights a plate:

- farther planes are given lighter, cooler values (atmospheric perspective
  by choice, not by simulation);
- light pools on surfaces as a falloff around a source, in the source's own
  colour;
- silhouettes take a rim from the facing ratio;
- a moving light (the founder's) is a falloff whose centre is set per frame.
"""
import bpy

from common import hexc


def _clear(nt):
    for n in list(nt.nodes):
        nt.nodes.remove(n)


def painted_sky(stops, scale=1.2, wobble=0.08, strength=1.0):
    """What the camera sees: a smooth painted ramp over screen height,
    pushed around by broad noise like a loaded brush."""
    sc = bpy.context.scene
    sc.view_settings.view_transform = "Standard"
    w = sc.world
    w.use_nodes = True
    nt = w.node_tree
    _clear(nt)
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = 3.0
    ma = nt.nodes.new("ShaderNodeMath")
    ma.operation = "MULTIPLY_ADD"
    ma.inputs[1].default_value = wobble
    ma.inputs[2].default_value = -wobble / 2
    add = nt.nodes.new("ShaderNodeMath")
    add.operation = "ADD"
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "EASE"
    els = ramp.color_ramp.elements
    while len(els) > 1:
        els.remove(els[-1])
    els[0].position = stops[0][0]
    els[0].color = hexc(stops[0][1])
    for pos, c in stops[1:]:
        e = els.new(pos)
        e.color = hexc(c)
    nt.links.new(tc.outputs["Window"], sep.inputs[0])
    nt.links.new(tc.outputs["Window"], nz.inputs["Vector"])
    nt.links.new(nz.outputs["Fac"], ma.inputs[0])
    nt.links.new(sep.outputs["Y"], add.inputs[0])
    nt.links.new(ma.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = strength
    nt.links.new(bg.outputs[0], out.inputs["Surface"])


# Lit windows sit above paper white so the bloom takes them.
WINDOW_GAIN = 2.2


def surface(name, color, rim=None, rim_power=0.3, rim_strength=1.0,
            pool=None, pool_at=(0.0, 0.0, 0.0), pool_r=100.0, pool_strength=1.0,
            moving=None, moving_r=40.0, moving_strength=1.0, grid=None):
    """One painted surface.

    color         the base value of the plane
    rim           colour of the silhouette rim (facing ratio)
    pool          colour of a light pooled around pool_at, falling off over pool_r
    moving        colour of a light whose centre is the node named 'LP',
                  set per frame with move_light()
    grid          (lit_color, density, scale_xy, scale_z, strength): a window
                  grid, some lit, for towers
    """
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    _clear(nt)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 1.0
    base = nt.nodes.new("ShaderNodeRGB")
    base.outputs[0].default_value = hexc(color)
    col = base.outputs[0]
    geo = nt.nodes.new("ShaderNodeNewGeometry")

    def add_light(col_socket, light_color, center_socket, radius, strength):
        d = nt.nodes.new("ShaderNodeVectorMath")
        d.operation = "DISTANCE"
        nt.links.new(geo.outputs["Position"], d.inputs[0])
        nt.links.new(center_socket, d.inputs[1])
        div = nt.nodes.new("ShaderNodeMath")
        div.operation = "DIVIDE"
        div.inputs[1].default_value = radius
        nt.links.new(d.outputs["Value"], div.inputs[0])
        sq = nt.nodes.new("ShaderNodeMath")
        sq.operation = "POWER"
        sq.inputs[1].default_value = 2.0
        nt.links.new(div.outputs[0], sq.inputs[0])
        one = nt.nodes.new("ShaderNodeMath")
        one.operation = "ADD"
        one.inputs[1].default_value = 1.0
        nt.links.new(sq.outputs[0], one.inputs[0])
        fall = nt.nodes.new("ShaderNodeMath")
        fall.operation = "DIVIDE"
        fall.inputs[0].default_value = strength
        nt.links.new(one.outputs[0], fall.inputs[1])
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "ADD"
        mix.clamp_result = False
        nt.links.new(fall.outputs[0], mix.inputs["Factor"])
        nt.links.new(col_socket, mix.inputs[6])
        mix.inputs[7].default_value = hexc(light_color)
        return mix.outputs[2]

    if grid:
        # A window grid in metres: (lit colour, share of windows lit, window
        # width, floor height, brightness). The brick texture is 2D (it reads
        # x and y only), so each wall picks its own plane from its normal; a
        # single mapping striped every wall facing along x (2026-10-09).
        lit_color, density, bw, rh, gstrength = grid
        tc = nt.nodes.new("ShaderNodeTexCoord")
        sepp = nt.nodes.new("ShaderNodeSeparateXYZ")
        sepn = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(tc.outputs["Object"], sepp.inputs[0])
        nt.links.new(tc.outputs["Normal"], sepn.inputs[0])
        absn = nt.nodes.new("ShaderNodeMath")
        absn.operation = "ABSOLUTE"
        nt.links.new(sepn.outputs["X"], absn.inputs[0])
        facing_x = nt.nodes.new("ShaderNodeMath")
        facing_x.operation = "GREATER_THAN"
        facing_x.inputs[1].default_value = 0.5
        nt.links.new(absn.outputs[0], facing_x.inputs[0])
        across = nt.nodes.new("ShaderNodeMix")
        across.data_type = "FLOAT"
        nt.links.new(facing_x.outputs[0], across.inputs["Factor"])
        nt.links.new(sepp.outputs["X"], across.inputs[2])
        nt.links.new(sepp.outputs["Y"], across.inputs[3])
        uv = nt.nodes.new("ShaderNodeCombineXYZ")
        nt.links.new(across.outputs[0], uv.inputs[0])
        nt.links.new(sepp.outputs["Z"], uv.inputs[1])
        br = nt.nodes.new("ShaderNodeTexBrick")
        br.offset = 0.0
        br.inputs["Scale"].default_value = 1.0
        br.inputs["Brick Width"].default_value = bw
        br.inputs["Row Height"].default_value = rh
        br.inputs["Mortar Size"].default_value = min(bw, rh) * 0.28
        br.inputs["Color1"].default_value = (1, 1, 1, 1)
        br.inputs["Color2"].default_value = (1, 1, 1, 1)
        br.inputs["Mortar"].default_value = (0, 0, 0, 1)
        nt.links.new(uv.outputs[0], br.inputs["Vector"])
        # Which windows are on: one random value per window cell.
        cell = nt.nodes.new("ShaderNodeVectorMath")
        cell.operation = "DIVIDE"
        cell.inputs[1].default_value = (bw, rh, 1.0)
        nt.links.new(uv.outputs[0], cell.inputs[0])
        fl = nt.nodes.new("ShaderNodeVectorMath")
        fl.operation = "FLOOR"
        nt.links.new(cell.outputs[0], fl.inputs[0])
        wn = nt.nodes.new("ShaderNodeTexWhiteNoise")
        nt.links.new(fl.outputs[0], wn.inputs["Vector"])
        gt = nt.nodes.new("ShaderNodeMath")
        gt.operation = "GREATER_THAN"
        gt.inputs[1].default_value = 1.0 - density
        nt.links.new(wn.outputs["Value"], gt.inputs[0])
        # Brick's Fac is 1 on the mortar, so the pane is its inverse; used
        # directly it drew every window as an outline (2026-10-09).
        pane = nt.nodes.new("ShaderNodeMath")
        pane.operation = "SUBTRACT"
        pane.inputs[0].default_value = 1.0
        nt.links.new(br.outputs["Fac"], pane.inputs[1])
        on = nt.nodes.new("ShaderNodeMath")
        on.operation = "MULTIPLY"
        nt.links.new(pane.outputs[0], on.inputs[0])
        nt.links.new(gt.outputs[0], on.inputs[1])
        gm = nt.nodes.new("ShaderNodeMix")
        gm.data_type = "RGBA"
        gm.blend_type = "MIX"
        nt.links.new(on.outputs[0], gm.inputs["Factor"])
        nt.links.new(col, gm.inputs[6])
        lc = hexc(lit_color)
        g = gstrength * WINDOW_GAIN
        gm.inputs[7].default_value = (lc[0] * g, lc[1] * g, lc[2] * g, 1)
        col = gm.outputs[2]

    if pool:
        c = nt.nodes.new("ShaderNodeCombineXYZ")
        c.inputs[0].default_value, c.inputs[1].default_value, c.inputs[2].default_value = pool_at
        col = add_light(col, pool, c.outputs[0], pool_r, pool_strength)
    if moving:
        lp = nt.nodes.new("ShaderNodeCombineXYZ")
        lp.name = "LP"
        col = add_light(col, moving, lp.outputs[0], moving_r, moving_strength)
    if rim:
        lw = nt.nodes.new("ShaderNodeLayerWeight")
        lw.inputs["Blend"].default_value = rim_power
        pw = nt.nodes.new("ShaderNodeMath")
        pw.operation = "POWER"
        pw.inputs[1].default_value = 3.0
        nt.links.new(lw.outputs["Facing"], pw.inputs[0])
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        mul.inputs[1].default_value = rim_strength
        nt.links.new(pw.outputs[0], mul.inputs[0])
        rm = nt.nodes.new("ShaderNodeMix")
        rm.data_type = "RGBA"
        rm.blend_type = "MIX"
        nt.links.new(mul.outputs[0], rm.inputs["Factor"])
        nt.links.new(col, rm.inputs[6])
        rm.inputs[7].default_value = hexc(rim)
        col = rm.outputs[2]
    nt.links.new(col, em.inputs["Color"])
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


def move_light(materials, pos):
    """Sets the moving light's centre on every material that has one."""
    for m in materials:
        n = m.node_tree.nodes.get("LP")
        if n:
            n.inputs[0].default_value, n.inputs[1].default_value, n.inputs[2].default_value = pos


def haze_card(name, center, width, height, color="#c9a3d4", alpha=0.35, axis="y"):
    """A sheet of air between two depth planes: a translucent card, densest
    at its base and gone at its top, so each plane behind it is lighter than
    the one in front, and the planes slide against it as the camera moves.
    axis is the direction the card faces ('y' for a wall across the view,
    'z' for a floor of haze seen from below)."""
    import bmesh
    from common import mesh_obj
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    _clear(nt)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = hexc(color)
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    els = ramp.color_ramp.elements
    els[0].position = 0.0
    els[0].color = (alpha, alpha, alpha, 1)
    els[1].position = 1.0
    els[1].color = (0, 0, 0, 1)
    edge = nt.nodes.new("ShaderNodeMath")
    edge.operation = "MULTIPLY"
    # Fade the sides too, so no card ever shows an edge.
    sx = nt.nodes.new("ShaderNodeMath")
    sx.operation = "PINGPONG"
    sx.inputs[1].default_value = 0.5
    sm = nt.nodes.new("ShaderNodeMath")
    sm.operation = "MULTIPLY"
    sm.inputs[1].default_value = 2.0
    nt.links.new(tc.outputs["UV"], sep.inputs[0])
    nt.links.new(sep.outputs["Y"], ramp.inputs["Fac"])
    nt.links.new(sep.outputs["X"], sx.inputs[0])
    nt.links.new(sx.outputs[0], sm.inputs[0])
    nt.links.new(ramp.outputs["Color"], edge.inputs[0])
    nt.links.new(sm.outputs[0], edge.inputs[1])
    nt.links.new(edge.outputs[0], mix.inputs["Fac"])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    try:
        m.surface_render_method = "BLENDED"
    except (AttributeError, TypeError):
        pass
    cx, cy, cz = center
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new()
    if axis == "y":
        corners = ((cx - width / 2, cy, cz), (cx + width / 2, cy, cz), (cx + width / 2, cy, cz + height), (cx - width / 2, cy, cz + height))
    else:
        corners = ((cx - width / 2, cy - height / 2, cz), (cx + width / 2, cy - height / 2, cz), (cx + width / 2, cy + height / 2, cz), (cx - width / 2, cy + height / 2, cz))
    f = bm.faces.new([bm.verts.new(c) for c in corners])
    for lp, (u, v) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        lp[uv].uv = (u, v)
    return mesh_obj(name, bm, m)
