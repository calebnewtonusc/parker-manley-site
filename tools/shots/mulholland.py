"""Mulholland at last light, re-graded for Parker Manley's site: amber dusk, his light in ember.
From T Combinator's shot 1 (calebnewtonusc/tcombinator scripts/shots/shot1.py). Art-directed light
(scripts/shots/art.py): five planes, each lighter and cooler with distance:
the black ridge with a rim-lit palm and person; the Hollywood Hills with
house lights; the basin's 6,245 lights on a street grid, with light pooling
on the ground around downtown; two ranges of mountains; a painted rose
twilight with cut-paper clouds and a hard setting sun.

    nalana -b --factory-startup --python shot1.py -- OUTDIR [FRAMES] [FIRST] [LAST]

Square 1280 frames: the 16:9 film and the 9:16 phone cut are both crops.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bmesh
import bpy

from art import haze_card, painted_sky, surface
from common import camera, export_points, hexc, lights_mesh, lineart, mesh_obj, profile, reset, rng, vertex_lit
from figures import figure, remove
from lit import paint_pass, square

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUTDIR = argv[0] if argv else "/tmp/s1"
FRAMES = int(argv[1]) if len(argv) > 1 else 1
FIRST = int(argv[2]) if len(argv) > 2 else 0
LAST = int(argv[3]) if len(argv) > 3 else FRAMES - 1

sc = reset()
square()
CAM_Z = 78.2

# The horizon sits at about 0.40 of the square's height; below it is ground.
painted_sky([
    (0.38, "#f7d6a4"), (0.44, "#f0b878"), (0.52, "#d68d5c"),
    (0.64, "#8d5a4c"), (0.78, "#3f3040"), (0.94, "#16141a"),
], scale=1.0, wobble=0.07)

ink = bpy.data.collections.new("inked")
sc.collection.children.link(ink)


def ridge_line(x0, x1, base, amp, n, seed):
    import random
    r = random.Random(seed)
    pts = []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        h = base + amp * (0.55 + 0.45 * math.sin(i * 0.37 + seed) * math.sin(i * 0.11 + seed * 2)) + r.uniform(-amp * 0.08, amp * 0.08)
        pts.append((x, h))
    return pts


def disc(name, cx, cy, cz, r, mat, n=64):
    bm = bmesh.new()
    bm.faces.new([bm.verts.new((cx + r * math.cos(a), cy, cz + r * math.sin(a))) for a in [i / n * math.tau for i in range(n)]])
    return mesh_obj(name, bm, mat)


def cloud(name, cx, cz, w, h, mat, seed, y=12500):
    import random
    r = random.Random(seed)
    bm = bmesh.new()
    vs = []
    for i in range(48):
        a = i / 48 * math.tau
        rr = 1 + 0.18 * math.sin(a * 3 + seed) + r.uniform(-0.06, 0.06)
        z = math.sin(a) * h * rr
        vs.append(bm.verts.new((cx + math.cos(a) * w * rr, y, cz + (z if z > 0 else z * 0.35))))
    bm.faces.new(vs)
    return mesh_obj(name, bm, mat, ink)


# Plane 5: sky objects. The sun just above the far range; the clouds take
# its light on their edges.
disc("sun", 1300, 12800, 330, 480, surface("sun_m", "#fff4dc"))
cloud("cloud1", 2300, 900, 2600, 150, surface("c1", "#e8a76c", rim="#ffe2bd", rim_power=0.2, rim_strength=0.6), 1)
cloud("cloud2", -3200, 1350, 3400, 190, surface("c2", "#b0705a", rim="#f3c79a", rim_power=0.2, rim_strength=0.5), 4)
cloud("cloud3", 600, 2050, 4200, 160, surface("c3", "#6e4d4a"), 9)

# Plane 4: the San Gabriels, lighter the farther they are.
profile("mtn_far", ridge_line(-16000, 16000, 160, 620, 110, 3), 11500, -10,
        surface("mtn_far_m", "#8a6a66", rim="#f2c9a0", rim_power=0.15, rim_strength=0.35), ink)
profile("mtn_near", ridge_line(-14000, 14000, 60, 300, 90, 7), 9000, -10, surface("mtn_near_m", "#4d3b40"), ink)

# Plane 3: the basin. Light pools on the floor around downtown and around
# the founder's light, in the city's own colour.
FOUNDER = (-140.0, 2400.0)
bm = bmesh.new()
for v in ((-40000, 150, 0), (40000, 150, 0), (40000, 8800, 0), (-40000, 8800, 0)):
    bm.verts.new(v)
bm.faces.new(bm.verts)
mesh_obj("basin", bm, surface("basin_m", "#0f0d10", pool="#5e3e2a", pool_at=(300, 5200, 0), pool_r=1500, pool_strength=0.9))

hfov = math.atan(18 / 24)
cols = [(hexc("#ffd9a0"), 0.6), (hexc("#fff4e2"), 0.85), (hexc("#ffbe7a"), 0.95), (hexc("#f0e6c8"), 1.0)]


def pick():
    r = rng.random()
    for c, edge in cols:
        if r <= edge:
            return c
    return cols[0][0]


pts = []
while len(pts) < 6244:
    y = 900 * (8600 / 900) ** rng.random()
    xmax = math.tan(hfov) * y * 1.05
    k = rng.random()
    if k < 0.5:
        x = round(rng.uniform(-xmax, xmax) / 70) * 70 + rng.uniform(-3, 3)
    elif k < 0.93:
        x = rng.uniform(-xmax, xmax)
        y = round(y / 140) * 140 + rng.uniform(-3, 3)
    else:
        side = -1 if rng.random() < 0.5 else 1
        x = side * (120 + (y - 300) * 0.55) + rng.uniform(-40, 40)
        if abs(x) > xmax:
            continue
    pts.append((x, y, 0.6, 0.0017 * y * (1.3 if k >= 0.93 else 1.0), pick()))
pts.append((FOUNDER[0], FOUNDER[1], 0.6, 0.0017 * FOUNDER[1] * 4.6, hexc("#e08a43")))
lights_mesh("lights", pts)
# The founder's light pools pink on the ground around it.
bm = bmesh.new()
bm.faces.new([bm.verts.new((FOUNDER[0] + 260 * math.cos(a), FOUNDER[1] + 260 * math.sin(a), 0.2)) for a in [i / 40 * math.tau for i in range(40)]])
mesh_obj("founder_pool", bm, surface("founder_pool", "#1c1510", pool="#7a4a20", pool_at=(FOUNDER[0], FOUNDER[1], 0), pool_r=90, pool_strength=1.0))

bm = bmesh.new()
for x in range(-5600, 5601, 560):
    bm.faces.new([bm.verts.new(v) for v in ((x - 1.6, 900, 0.3), (x + 1.6, 900, 0.3), (x * 1.6 + 1.6, 8600, 0.3), (x * 1.6 - 1.6, 8600, 0.3))])
for y in range(1120, 8600, 1120):
    xm = math.tan(hfov) * y * 1.05
    bm.faces.new([bm.verts.new(v) for v in ((-xm, y - 2, 0.3), (xm, y - 2, 0.3), (xm, y + 2, 0.3), (-xm, y + 2, 0.3))])
mesh_obj("boulevards", bm, surface("boulevard_m", "#7a6650"))

# Plane 2: the Hollywood Hills, with house lights on their slopes.
# Low enough that the city still shows over them (at 20 to 72m they hid
# it, 2026-10-09 render).
hills = ridge_line(-7000, 7000, 6, 20, 140, 11)
profile("hills", hills, 760, -5, surface("hills_m", "#1c1614", rim="#c9946a", rim_power=0.2, rim_strength=0.35), ink)
bm = bmesh.new()
col = bm.loops.layers.float_color.new("col")
# Dense enough to read as lit hillsides at this distance; trees and a road
# of car lights were tried here and read as blobs and specks (2026-10-09).
for x, z in hills:
    for _ in range(7):
        hx, hz = x + rng.uniform(-50, 50), z - rng.uniform(1, 18)
        if hz < 2:
            continue
        s = 0.9
        f = bm.faces.new([bm.verts.new(v) for v in ((hx - s, 755, hz), (hx, 755, hz - s), (hx + s, 755, hz), (hx, 755, hz + s))])
        for lp in f.loops:
            lp[col] = hexc("#fff0dc")
mesh_obj("houses", bm, vertex_lit("houses_m", 1.0))

# Plane 1: the ridge, the palm and the person, near-black with a rose rim
# from the sky behind them.
ridge_m = surface("ridge_m", "#0a0807", rim="#e9a06a", rim_power=0.28, rim_strength=0.85)
figure_m = surface("figure_m", "#07050b", rim="#ffd2a0", rim_power=0.22, rim_strength=1.0)


def crest_z(x):
    return 77.6 - 5.4 * ((x + 46) / 56) ** 1.4


crest = []
for i in range(41):
    x = -46 + 56 * i / 40
    crest.append((x, crest_z(x) + math.sin(i * 1.7) * 0.25 + (0.35 if i % 7 == 0 else 0)))
# The slope runs on past the frame: ending it at x=26 let the sky show
# through under the ridge once the crane rose (a pink wedge, 2026-10-09).
crest += [(16, 66), (26, 40), (60, 10), (140, -5)]
profile("ridge", crest, 40, -5, ridge_m, ink)


def palm(x, y, z, h, lean):
    bm = bmesh.new()
    prev = None
    for i in range(13):
        t = i / 12
        cx, cz, r = x + lean * t ** 1.6, z + h * t, 0.32 - 0.12 * t
        ring = [bm.verts.new((cx + r * math.cos(a), y + r * math.sin(a), cz)) for a in [j * math.tau / 6 for j in range(6)]]
        if prev:
            for j in range(6):
                bm.faces.new((prev[j], prev[(j + 1) % 6], ring[(j + 1) % 6], ring[j]))
        prev = ring
    top = (x + lean, y, z + h)
    for f in range(11):
        a = f / 11 * math.tau + 0.2
        L = 3.6 + (f % 3) * 0.5
        p = [(top[0] + math.cos(a) * L * (s / 7), top[1] + math.sin(a) * L * (s / 7) * 0.5, top[2] + 0.9 * (s / 7) - 2.6 * (s / 7) ** 2) for s in range(8)]
        nx, ny = -math.sin(a), math.cos(a)
        for s in range(7):
            w0, w1 = 0.32 * math.sin(math.pi * s / 7) + 0.03, 0.32 * math.sin(math.pi * (s + 1) / 7) + 0.03
            p0, p1 = p[s], p[s + 1]
            bm.faces.new([bm.verts.new((p0[0] + nx * w0, p0[1] + ny * w0, p0[2])), bm.verts.new((p1[0] + nx * w1, p1[1] + ny * w1, p1[2])),
                          bm.verts.new((p1[0] - nx * w1, p1[1] - ny * w1, p1[2])), bm.verts.new((p0[0] - nx * w0, p0[1] - ny * w0, p0[2]))])
    return mesh_obj("palm", bm, figure_m, ink)


def person(x, y, z):
    bm = bmesh.new()

    def poly(points):
        bm.faces.new([bm.verts.new((x + px, y, z + pz)) for px, pz in points])
    poly([(-0.2, 0), (-0.08, 0), (-0.02, 0.8), (-0.24, 0.82)])
    poly([(0.08, 0), (0.2, 0), (0.24, 0.82), (0.02, 0.8)])
    poly([(-0.25, 0.8), (0.25, 0.8), (0.29, 1.36), (-0.29, 1.36)])
    poly([(-0.29, 1.36), (-0.38, 1.33), (-0.47, 0.82), (-0.37, 0.8)])
    poly([(0.29, 1.36), (0.38, 1.33), (0.47, 0.82), (0.37, 0.8)])
    poly([(-0.08, 1.36), (0.08, 1.36), (0.08, 1.45), (-0.08, 1.45)])
    poly([(0.12 * math.cos(a), 1.57 + 0.13 * math.sin(a)) for a in [i / 20 * math.tau for i in range(20)]])
    return mesh_obj("person", bm, figure_m, ink)


palm(-13.5, 40, crest_z(-13.5) - 0.4, 10.5, 1.4)
rx, rz = -6.0, crest_z(-6.0)
bm = bmesh.new()
bm.faces.new([bm.verts.new((rx + x, 40, rz + z)) for x, z in [(-1.6, 0), (-1.1, 1.6), (-0.2, 2.25), (0.9, 2.0), (1.5, 0.9), (1.8, 0)]])
mesh_obj("rock", bm, ridge_m, ink)
PERSON = (rx - 0.1, 40, rz + 2.1)

# Air between the planes: the city sits behind one sheet of haze and the
# mountains behind another, so each is lighter than the one in front and
# they slide against each other as the camera rises.
haze_card("haze_city", (0, 1500, 0), 30000, 140, "#b88a6c", 0.32)
haze_card("haze_far", (0, 6200, 0), 40000, 420, "#d9ad88", 0.3)

lineart(ink, color="#241a12", thickness=2)
paint_pass(3)

cam = camera((0, 0, CAM_Z), (97.5, 4, 0), lens=24)
cam.data.sensor_fit = "HORIZONTAL"

os.makedirs(OUTDIR, exist_ok=True)
person_obj = None
for f in range(FIRST, LAST + 1):
    t = f / max(1, FRAMES - 1)
    e = t * t * (3 - 2 * t)
    # The person and the cars move on twos: a pose holds for two frames.
    tp = (f - f % 2) / max(1, FRAMES - 1)
    remove(person_obj)
    lift = min(1.0, max(0.0, (tp - 0.45) / 0.3))
    lift = lift * lift * (3 - 2 * lift)
    # Standing, looking out; then the right arm comes up to point at the
    # city, at the founder's light.
    person_obj = figure("person", PERSON, facing=0.0, scale=1.0,
                        arm_l=0.12 + 0.05 * lift, arm_r=0.12 + 1.28 * lift,
                        lean=0.15 * lift, stance=0.11)
    # A crane up and over the ridge: the palm and the person sweep past and
    # below while the city opens out beyond them. A small push read as a
    # flat card ("It just looks 2d", Caleb, 2026-10-09).
    # The take opens on the empty sky, where the founder's company name is
    # written live (the hook, ShowCanvas over this frame), then tilts down
    # onto the basin and cranes over the ridge. One curve: the tilt and the
    # crane overlap so the camera never stops.
    tilt = min(1.0, t / 0.4)
    tilt = tilt * tilt * (3 - 2 * tilt)
    c = min(1.0, max(0.0, (t - 0.2) / 0.8))
    c = c * c * (3 - 2 * c)
    cam.location = (0.6 * c, 30.0 * c, CAM_Z + 5.5 * c)
    cam.rotation_euler = (math.radians(97.5 + 26.0 * (1 - tilt) - 5.0 * c), math.radians(4 - 2.0 * c), 0)
    export_points("s1", [(x, y, z, cc) for x, y, z, _, cc in pts[:-1]], f, FRAMES, pink=(FOUNDER[0], FOUNDER[1], 0.6))
    sc.render.filepath = os.path.join(OUTDIR, f"s1_{f:04d}.png")
    sc.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    print("RENDERED", sc.render.filepath)
