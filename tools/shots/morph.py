"""The joins between shots: one shot's lights become the next one's.

    python3 morph.py points A.png A.json B.png B.json OUTDIR TAG FRAMES
    python3 morph.py tgap   A.png B.png OUTDIR TAG FRAMES [pink.json]

Caleb, 2026-10-09: "you can totally have things morph into each other ...
it just has to be tasteful and not feel gimicky." So no shot cuts to the
next. Every join is built from geometry that is in both shots, exported by
each Blender scene (common.export_points): where its shared lights land on
screen on its last frame, and where the next shot's land on its first.

points  The lights of shot A travel to the lights of shot B on one eased
        curve with a small lift, in a wave across the frame, while A dims
        into the night around them and B builds up around where they land.
        The founder's pink light is matched to the pink light and never
        fades: it is the one object the take follows.
tgap    The climb ends looking up between the towers at a T of sky. The gap
        is traced as a star polygon (one radius per angle from its centre),
        the T of the strike is traced the same way, and the radii are
        interpolated, so the sky gap becomes the T while the towers' dark
        becomes cardinal.

Tasteful, per the brief: the link reads on a second look, moves on one
curve, never pauses (a join is 16 frames, about a third of a shot), and
nothing spins, bursts or sweeps colour.
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage


def load(p):
    return np.asarray(Image.open(p).convert("RGB")).astype(np.float32) / 255


def smooth(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def to_srgb(c):
    c = np.clip(np.asarray(c, np.float32), 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


def glow_layer(canvas, S, sigma_k=0.0035, gain=1.4):
    g = np.stack([ndimage.gaussian_filter(canvas[..., i], S * sigma_k) for i in range(3)], -1)
    return canvas + g * gain


def points(a_png, a_json, b_png, b_json, outdir, tag, frames):
    A, B = load(a_png), load(b_png)
    S = A.shape[0]
    ja, jb = json.load(open(a_json)), json.load(open(b_json))
    pa, pb = ja["pts"], jb["pts"]
    rng = np.random.default_rng(20261009)
    m = min(len(pa), len(pb), 1400)
    ia = np.sort(rng.choice(len(pa), m, replace=False))
    ib = np.sort(rng.choice(len(pb), m, replace=False))
    pa = [pa[i] for i in ia]
    pb = [pb[i] for i in ib]
    # Pair by order across the frame, so neighbours travel together and no
    # two streams cross: the move reads as one sheet of lights.
    key = lambda p: p[0] + 0.15 * p[1]
    pa.sort(key=key)
    pb.sort(key=key)
    ua = np.array([[p[0], p[1]] for p in pa])
    ub = np.array([[p[0], p[1]] for p in pb])
    ca = to_srgb([p[2] for p in pa])
    cb = to_srgb([p[2] for p in pb])
    rank = np.linspace(0, 1, m)
    pink_a, pink_b = ja.get("pink"), jb.get("pink")
    os.makedirs(outdir, exist_ok=True)
    r0 = max(1.5, S * 0.0011)
    for k in range(frames):
        s = (k + 1) / (frames + 1)
        # The scene: A dims to the night, then B rises out of it. Never
        # fully black, so the take never cuts.
        fa = 1 - 0.86 * smooth(s / 0.55)
        fb = 0.14 + 0.86 * smooth((s - 0.45) / 0.55)
        bg = A * fa if s < 0.5 else B * fb
        canvas = np.zeros_like(A)
        im = Image.new("RGB", (S, S))
        d = ImageDraw.Draw(im)
        # A wave across the frame: each light starts a little after the one
        # to its left, all on the same curve.
        e = np.array([smooth((s - 0.22 * r) / 0.78) for r in rank])
        u = ua * (1 - e[:, None]) + ub * e[:, None]
        u[:, 1] += 0.05 * np.sin(math.pi * e)
        col = ca * (1 - e[:, None]) + cb * e[:, None]
        alpha = smooth(s / 0.2) * smooth((1 - s) / 0.2)
        for (x, y), c in zip(u, col):
            px, py = x * S, (1 - y) * S
            cc = tuple(int(255 * v * alpha) for v in c)
            d.ellipse((px - r0, py - r0, px + r0, py + r0), fill=cc)
        if pink_a and pink_b:
            ep = smooth(s)
            x = pink_a[0] * (1 - ep) + pink_b[0] * ep
            y = pink_a[1] * (1 - ep) + pink_b[1] * ep + 0.04 * math.sin(math.pi * ep)
            px, py = x * S, (1 - y) * S
            rp = S * 0.0045
            d.ellipse((px - rp, py - rp, px + rp, py + rp), fill=(255, 79, 139))
            d.ellipse((px - rp * 0.4, py - rp * 0.4, px + rp * 0.4, py + rp * 0.4), fill=(255, 236, 244))
        canvas = np.asarray(im).astype(np.float32) / 255
        out = np.clip(bg + glow_layer(canvas, S), 0, 1)
        Image.fromarray((out * 255).astype(np.uint8)).save(os.path.join(outdir, f"{tag}_{k:04d}.png"))
    print("MORPH", tag, frames)


def star(mask, center, n=720):
    """The farthest masked pixel along each of n rays from center."""
    h, w = mask.shape
    cx, cy = center
    rmax = math.hypot(w, h)
    radii = np.zeros(n)
    steps = np.arange(0, rmax, 1.0)
    for i in range(n):
        a = 2 * math.pi * i / n
        xs = (cx + np.cos(a) * steps).astype(int)
        ys = (cy + np.sin(a) * steps).astype(int)
        ok = (xs >= 0) & (xs < w) & (ys >= 0) & (ys < h)
        xs, ys = xs[ok], ys[ok]
        hit = mask[ys, xs]
        # The first run of mask from the centre outward: stop at the first
        # gap so a far patch of sky never joins the T.
        if not hit.any():
            radii[i] = 0
            continue
        first_off = np.argmin(hit) if not hit.all() else len(hit)
        radii[i] = first_off
    return radii


def tgap(a_png, b_png, outdir, tag, frames, pink_json=None):
    A, B = load(a_png), load(b_png)
    S = A.shape[0]
    # The sky between the crowns: bright and cyan.
    r, g, b = A[..., 0], A[..., 1], A[..., 2]
    sky = (g > 0.35) & (b > 0.35) & (r < g * 0.75)
    lab, n = ndimage.label(sky)
    if n == 0:
        raise SystemExit("no sky gap found in " + a_png)
    sizes = ndimage.sum(sky, lab, range(1, n + 1))
    gap = lab == (1 + int(np.argmax(sizes)))
    gy, gx = ndimage.center_of_mass(gap)
    # The T of the strike: near-white paper on cardinal.
    paper = (B[..., 0] > 0.85) & (B[..., 1] > 0.85)
    ty, tx = ndimage.center_of_mass(paper)
    # Rays from the top of the T's stem, where the bar meets it, so the T is
    # star-shaped from its centre; the gap's own centre for the gap.
    ys, xs = np.nonzero(paper)
    tcy = ys.min() + (ys.max() - ys.min()) * 0.2
    ra = star(gap, (gx, gy))
    rb = star(paper, (tx, tcy))
    angles = np.linspace(0, 2 * math.pi, len(ra), endpoint=False)
    sky_col = np.median(A[gap], axis=0)
    cardinal = np.array([154, 0, 0], np.float32) / 255
    paper_col = np.median(B[paper], axis=0)
    pink = json.load(open(pink_json))["pink"] if pink_json else None
    # Where the strike's light sits: the pink pixels of B.
    pk = (B[..., 0] > 0.9) & (B[..., 1] < 0.45) & (B[..., 2] > 0.4)
    pky, pkx = ndimage.center_of_mass(pk) if pk.any() else (None, None)
    os.makedirs(outdir, exist_ok=True)
    for k in range(frames):
        s = (k + 1) / (frames + 1)
        e = smooth(s)
        cx = gx * (1 - e) + tx * e
        cy = gy * (1 - e) + tcy * e
        rr = ra * (1 - e) + rb * e
        poly = [(cx + math.cos(a) * q, cy + math.sin(a) * q) for a, q in zip(angles, rr)]
        mask_im = Image.new("L", (S, S), 0)
        ImageDraw.Draw(mask_im).polygon(poly, fill=255)
        mask = (np.asarray(mask_im).astype(np.float32) / 255)[..., None]
        # Outside the shape the towers' dark becomes cardinal; inside, the
        # sky becomes paper. The last frames settle onto the strike itself.
        outside = A * (1 - e) + cardinal * e
        inside = sky_col * (1 - e) + paper_col * e
        frame = outside * (1 - mask) + inside * mask
        settle = smooth((s - 0.8) / 0.2)
        frame = frame * (1 - settle) + B * settle
        im = Image.fromarray((np.clip(frame, 0, 1) * 255).astype(np.uint8))
        if pink and pkx is not None:
            d = ImageDraw.Draw(im)
            x = pink[0] * S * (1 - e) + pkx * e
            y = (1 - pink[1]) * S * (1 - e) + pky * e
            rp = S * 0.0065 * (0.7 + 0.3 * e)
            d.ellipse((x - rp, y - rp, x + rp, y + rp), fill=(255, 79, 139))
        im.save(os.path.join(outdir, f"{tag}_{k:04d}.png"))
    print("MORPH", tag, frames)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "points":
        a, aj, b, bj, outdir, tag, n = sys.argv[2:9]
        points(a, aj, b, bj, outdir, tag, int(n))
    elif mode == "tgap":
        a, b, outdir, tag, n = sys.argv[2:7]
        pj = sys.argv[7] if len(sys.argv) > 7 else None
        tgap(a, b, outdir, tag, int(n), pj)
