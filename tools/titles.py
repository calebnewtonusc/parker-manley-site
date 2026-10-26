"""Physical title pieces as images, so nothing on the page is a CSS box:
the opening title card (letterpress on real paper) and a marquee board per
featured film (backlit panel, plastic letters, bulbs).

    python3 tools/titles.py

Paper: ambientCG paper002 (CC0), via the handwriting skill's paper-scans.
"""
import json
import os
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "media/titles"
OUT.mkdir(parents=True, exist_ok=True)
PAPER = Path.home() / ".chewbacca/skills/handwriting/scripts/paper-scans/paper002-color.jpg"
COPPER = "/System/Library/Fonts/Supplemental/Copperplate.ttc"
DIN = "/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf"
rng = np.random.default_rng(11)
random.seed(11)


def paper(w, h, tint=(236, 222, 192)):
    p = Image.open(PAPER).convert("L").resize((1024, 1024))
    tile = Image.new("L", (w, h))
    for x in range(0, w, 1024):
        for y in range(0, h, 1024):
            tile.paste(p, (x, y))
    a = np.asarray(tile, np.float32)
    detail = a / (np.asarray(tile.filter(ImageFilter.GaussianBlur(24)), np.float32) + 1)
    base = np.array(tint, np.float32)[None, None, :] * (0.82 + 0.18 * detail[..., None])
    # Edges a touch darker and warmer, from handling.
    yy, xx = np.mgrid[0:h, 0:w]
    edge = np.minimum.reduce([xx, yy, w - 1 - xx, h - 1 - yy]).astype(np.float32)
    base *= (0.86 + 0.14 * np.clip(edge / 60, 0, 1))[..., None]
    return Image.fromarray(np.clip(base, 0, 255).astype("uint8"), "RGB")


def ink(page, mask, color=(43, 32, 24), strength=0.92):
    """Letterpress: ink spreads a little, coverage is uneven, the type bites
    into the sheet so there is a faint impression shadow."""
    m = np.asarray(mask.filter(ImageFilter.GaussianBlur(0.7)), np.float32) / 255
    noise = rng.random(m.shape).astype(np.float32)
    coarse = np.asarray(Image.fromarray((rng.random((m.shape[0] // 6 + 1, m.shape[1] // 6 + 1)) * 255).astype("uint8")).resize((m.shape[1], m.shape[0]), Image.BILINEAR), np.float32) / 255
    cover = m * (0.72 + 0.28 * coarse) * (noise > 0.035)
    imp = np.asarray(mask.filter(ImageFilter.GaussianBlur(2.2)).transform(mask.size, Image.AFFINE, (1, 0, -1.5, 0, 1, -1.5)), np.float32) / 255
    arr = np.asarray(page, np.float32)
    arr *= (1 - 0.08 * imp)[..., None]
    c = np.array(color, np.float32)
    a = (cover * strength)[..., None]
    arr = arr * (1 - a) + c * a
    return Image.fromarray(np.clip(arr, 0, 255).astype("uint8"), "RGB")


def wobbly_rect(d, box, width, jitter=0.8):
    x0, y0, x1, y1 = box
    for (ax, ay, bx, by) in ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)):
        n = 40
        pts = [(ax + (bx - ax) * i / n + random.uniform(-jitter, jitter), ay + (by - ay) * i / n + random.uniform(-jitter, jitter)) for i in range(n + 1)]
        d.line(pts, fill=255, width=width)


def title_card():
    W, H = 1800, 640
    page = paper(W, H)
    mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(mask)
    wobbly_rect(d, (26, 26, W - 26, H - 26), 5)
    wobbly_rect(d, (44, 44, W - 44, H - 44), 2)
    small = ImageFont.truetype(COPPER, 34, index=0)
    big = ImageFont.truetype(COPPER, 150, index=0)
    role = ImageFont.truetype(COPPER, 36, index=0)
    d.text((W / 2, 150), "A  P I C T U R E  B Y", font=small, fill=255, anchor="mm")
    d.text((W / 2, 320), "PARKER MANLEY", font=big, fill=255, anchor="mm")
    d.line([(W / 2 - 70, 430), (W / 2 + 70, 430)], fill=255, width=3)
    d.text((W / 2, 500), "DIRECTOR  ·  CINEMATOGRAPHER  ·  EDITOR", font=role, fill=255, anchor="mm")
    card = ink(page, mask)
    card.save(OUT / "titlecard.webp", "WEBP", quality=88, method=6)
    card.resize((900, 320), Image.LANCZOS).save(OUT / "titlecard-900.webp", "WEBP", quality=86, method=6)


def marquee(slug, title, meta):
    W, H = 1800, 470
    img = Image.new("RGB", (W, H), (22, 18, 14))
    d = ImageDraw.Draw(img)
    # Steel frame, then the backlit panel with uneven light (tubes behind it).
    d.rounded_rectangle((8, 8, W - 8, H - 8), 10, fill=(34, 28, 22), outline=(70, 58, 44), width=3)
    panel = (70, 92, W - 70, 382)
    yy, xx = np.mgrid[0:panel[3] - panel[1], 0:panel[2] - panel[0]]
    glow = 0.86 + 0.14 * np.cos((xx / (panel[2] - panel[0])) * np.pi * 6) ** 2 - 0.08 * (yy / (panel[3] - panel[1]))
    pa = np.stack([248 * glow, 240 * glow, 222 * glow], -1)
    pimg = Image.fromarray(np.clip(pa, 0, 255).astype("uint8"), "RGB")
    img.paste(pimg, panel[:2])
    # Letter rails.
    for y in (panel[1] + 96, panel[1] + 196):
        d.line([(panel[0], y), (panel[2], y)], fill=(160, 150, 130), width=3)
    # Bulbs, top and bottom, not all equal; one is dead.
    dead = random.randrange(10, 40)
    layer = Image.new("RGB", (W, H), (0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for row_y in (48, H - 48):
        for i, x in enumerate(range(48, W - 30, 44)):
            if i == dead and row_y == 48:
                d.ellipse((x - 8, row_y - 8, x + 8, row_y + 8), fill=(70, 62, 50))
                continue
            k = random.uniform(0.75, 1.0)
            ld.ellipse((x - 16, row_y - 16, x + 16, row_y + 16), fill=(int(255 * k), int(190 * k), int(110 * k)))
            d.ellipse((x - 8, row_y - 8, x + 8, row_y + 8), fill=(255, int(236 * k), int(190 * k)))
    img = ImageChops.screen(img, layer.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(img)
    # Plastic letters, each hung by hand on the rails: a slight tilt, a shadow.
    def letters(text, cy, size, color, track):
        f = ImageFont.truetype(DIN, size)
        widths = [f.getbbox(c)[2] - f.getbbox(c)[0] if c != " " else size * 0.35 for c in text]
        total = sum(widths) + track * (len(text) - 1)
        x = (W - total) / 2
        for c, wdt in zip(text, widths):
            if c != " ":
                tile = Image.new("RGBA", (int(size * 1.4), int(size * 1.4)), (0, 0, 0, 0))
                td = ImageDraw.Draw(tile)
                td.text((tile.width / 2, tile.height / 2), c, font=f, fill=color + (255,), anchor="mm")
                tile = tile.rotate(random.uniform(-2.2, 2.2), resample=Image.BICUBIC)
                sh = Image.new("RGBA", tile.size, (0, 0, 0, 0))
                sh.putalpha(tile.getchannel("A").filter(ImageFilter.GaussianBlur(3)).point(lambda v: v * 0.35))
                ox = int(x + wdt / 2 - tile.width / 2 + random.uniform(-1.5, 1.5))
                oy = int(cy - tile.height / 2 + random.uniform(-2, 2))
                img.paste((20, 16, 12), (ox + 4, oy + 5), sh)
                img.paste(tile, (ox, oy), tile)
            x += wdt + track
    letters("NOW SHOWING", panel[1] + 50, 64, (176, 30, 34), 14)
    t = title.upper()
    size = 100 if len(t) <= 18 else 80
    letters(t, panel[1] + 148, size, (18, 16, 14), 8)
    letters(meta.upper(), panel[1] + 246, 52, (18, 16, 14), 10)
    img.save(OUT / f"marquee-{slug}.webp", "WEBP", quality=86, method=6)
    img.resize((900, 235), Image.LANCZOS).save(OUT / f"marquee-{slug}-900.webp", "WEBP", quality=84, method=6)


if __name__ == "__main__":
    title_card()
    films = json.loads((ROOT / "data/films.json").read_text())["films"]
    for f in films:
        if f["featured"]:
            meta = " · ".join(x for x in [str(f["year"]), f["genre"].replace("/", "·"), f"{f['minutes']} MIN" if f.get("minutes") else ""] if x)
            marquee(f["slug"], f["title"], meta)
    print("titles:", sorted(os.listdir(OUT)))
