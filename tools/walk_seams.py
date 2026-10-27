"""Shoot a frame either side of every hand-off at Caleb's window size.

Every bug on 2026-10-25 lived at a seam: a section's padding showing the
scene before it, a z-index change putting the Mac over Premiere, a monitor
switching pictures at the cut. Run this after any change and look at the
sheet it writes.
    python3 tools/walk_seams.py http://localhost:8765/ [out.png]
"""
import sys
from playwright.sync_api import sync_playwright
from PIL import Image

URL = sys.argv[1] if len(sys.argv) > 1 else "https://parker-manley.up.railway.app/"
OUT = sys.argv[2] if len(sys.argv) > 2 else "seams.png"
SEAMS = [(".knoll", 0.0), (".knoll", 0.5), (".knoll", 0.99), (".journey", 0.0), (".journey", 0.5), (".journey", 0.99), (".scene--films", 0.0), (".rollin", 0.0), (".rollin", 0.99),
         (".cam", 0.0), (".cam", 0.999), (".edit", 0.0), (".desk-run", 0.0), (".desk-run", 0.5), (".desk-run", 0.97)]
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1000, "height": 506})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(URL, wait_until="domcontentloaded", timeout=90000)
    pg.wait_for_timeout(3000)
    pg.evaluate("()=>document.querySelectorAll('.leader').forEach(e=>e.remove())")
    shots = []
    for i, (sel, f) in enumerate(SEAMS):
        y = pg.evaluate(f"()=>{{const e=document.querySelector('{sel}');if(!e)return null;const t=e.getBoundingClientRect().top+scrollY;return t+Math.max(0,e.offsetHeight-innerHeight)*{f}}}")
        if y is None:
            print("missing", sel)
            continue
        for dy in (-3, 3):
            pg.evaluate(f"scrollTo(0,{y + dy})")
            pg.wait_for_timeout(700)
            shots.append(pg.screenshot())
    b.close()
import io
ims = [Image.open(io.BytesIO(s)).resize((400, 202)) for s in shots]
sheet = Image.new("RGB", (800, 202 * ((len(ims) + 1) // 2)))
for k, im in enumerate(ims):
    sheet.paste(im, ((k % 2) * 400, (k // 2) * 202))
sheet.save(OUT)
print("errors", errs, "->", OUT)
sys.exit(1 if errs else 0)
