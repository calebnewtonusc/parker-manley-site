"""Draws src/topo.svg: contour lines of a smooth random terrain, like a USGS
quad sheet of the Front Range. Seeded, so rebuilds give the same map."""
import numpy as np

W, H, NX, NY = 1600, 1000, 160, 100
rng = np.random.default_rng(7)
x = np.linspace(0, 1, NX)[None, :]
y = np.linspace(0, 1, NY)[:, None]
z = np.zeros((NY, NX))
for _ in range(14):
    cx, cy, s, a = rng.random(), rng.random(), 0.08 + rng.random() * 0.22, rng.uniform(-1, 1)
    z += a * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * s * s))
z += 0.35 * np.sin(x * 5.1 + y * 2.3) * np.cos(y * 4.2 - x)
levels = np.linspace(z.min(), z.max(), 24)[1:-1]
sx, sy = W / (NX - 1), H / (NY - 1)

def interp(p1, p2, v1, v2, t):
    f = (t - v1) / (v2 - v1)
    return (p1[0] + f * (p2[0] - p1[0]), p1[1] + f * (p2[1] - p1[1]))

paths = []
for li, t in enumerate(levels):
    d = []
    for j in range(NY - 1):
        for i in range(NX - 1):
            c = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
            v = [z[j, i], z[j, i + 1], z[j + 1, i + 1], z[j + 1, i]]
            pts = []
            for k in range(4):
                a, b = k, (k + 1) % 4
                if (v[a] < t) != (v[b] < t):
                    pts.append(interp(c[a], c[b], v[a], v[b], t))
            for k in range(0, len(pts) - 1, 2):
                (x1, y1), (x2, y2) = pts[k], pts[k + 1]
                d.append(f"M{x1*sx:.0f} {y1*sy:.0f}L{x2*sx:.0f} {y2*sy:.0f}")
    width = 1.1 if li % 5 == 0 else 0.6
    paths.append(f'<path stroke-width="{width}" d="{"".join(d)}"/>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">'
       f'<g fill="none" stroke="#c9b38a" stroke-linecap="round">{"".join(paths)}</g></svg>')
open("src/topo.svg", "w").write(svg)
print(len(svg) // 1024, "KB")
