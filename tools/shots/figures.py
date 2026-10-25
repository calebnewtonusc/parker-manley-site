"""People drawn with Grease Pencil, posed per frame and held on twos.

The first renders had people as static mesh silhouettes. Here a figure is a
few thick brushstrokes in 3D space (torso, head, two legs, two arms), each
tapering the way an inked figure does, so it reads as drawn, and its pose
comes from a handful of numbers: each arm's angle from hanging down, a lean,
a stance and a crouch. A shot rebuilds its figures only on even frames, so
they move at 12 poses a second while the camera moves every frame.
"""
import math

import bpy

from common import hexc

_ink = {}


def _material(color):
    if color not in _ink:
        m = bpy.data.materials.new("figure_ink_" + color)
        bpy.data.materials.create_gpencil_data(m)
        m.grease_pencil.color = hexc(color)
        _ink[color] = m
    return _ink[color]


def figure(name, base, facing=0.0, scale=1.0, arm_l=0.15, arm_r=0.15, lean=0.0,
           stance=0.12, crouch=0.0, color="#06050a"):
    """One person standing at base (x, y, z), drawn in the plane facing
    `facing` radians around z (0 faces -y, toward a camera behind -y)."""
    gpd = bpy.data.grease_pencils.new(name)
    ob = bpy.data.objects.new(name, gpd)
    bpy.context.scene.collection.objects.link(ob)
    gpd.materials.append(_material(color))
    dr = gpd.layers.new("body").frames.new(bpy.context.scene.frame_current).drawing
    c, s = math.cos(facing), math.sin(facing)

    def P(x, z):
        x, z = x * scale, z * scale
        return (base[0] + x * c, base[1] + x * s, base[2] + z)

    hip_z = 0.95 - 0.25 * crouch
    neck = (lean * 0.12, hip_z + 0.5)
    strokes = []
    # Torso, thickest at the chest.
    strokes.append([((0.0, hip_z), 0.15), ((lean * 0.06, hip_z + 0.28), 0.2), (neck, 0.12)])
    # Head: two points close together draw as one round dab.
    hx, hz = lean * 0.15, neck[1] + 0.18
    strokes.append([((hx - 0.005, hz), 0.12), ((hx + 0.005, hz), 0.12)])
    # Legs, apart by `stance`, knees bent by `crouch`.
    for side in (-1, 1):
        foot = (side * stance, 0.0)
        knee = (side * stance * 0.55 + 0.06 * crouch, hip_z * 0.5 + 0.02)
        strokes.append([((side * 0.07, hip_z), 0.08), (knee, 0.065), (foot, 0.05)])
    # Arms from the shoulders; angle 0 hangs straight down, pi/2 is level.
    for side, a in ((-1, arm_l), (1, arm_r)):
        sh = (neck[0] + side * 0.19, neck[1] - 0.06)
        el = (sh[0] + side * 0.29 * math.sin(a), sh[1] - 0.29 * math.cos(a))
        a2 = a + 0.25
        hand = (el[0] + side * 0.27 * math.sin(a2), el[1] - 0.27 * math.cos(a2))
        strokes.append([(sh, 0.065), (el, 0.055), (hand, 0.04)])

    dr.add_strokes([len(st) for st in strokes])
    for st, pts in zip(dr.strokes, strokes):
        for pt, ((x, z), r) in zip(st.points, pts):
            pt.position = P(x, z)
            pt.radius = r * scale
    return ob


def remove(ob):
    if ob is not None:
        data = ob.data
        bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.grease_pencils.remove(data)
