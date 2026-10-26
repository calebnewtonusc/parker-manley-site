"""Every pinned scene on the home page must span the whole window.

A 40px section gutter once boxed the table scene in and let the reel show
through at both edges. Run against a local or live URL:
    python3 tools/check_full_bleed.py http://localhost:8000/
"""
import sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "https://parker-manley.up.railway.app/"
PINS = [".knoll__pin", ".rollin", ".cam__pin", ".edit", ".desk-run", ".irisout", ".sky", ".opening__pin"]

with sync_playwright() as p:
    b = p.chromium.launch()
    bad = []
    for w, h in [(1000, 506), (1440, 900)]:
        pg = b.new_page(viewport={"width": w, "height": h})
        pg.goto(URL, wait_until="load", timeout=60000)
        pg.wait_for_timeout(1500)
        for s in PINS:
            r = pg.evaluate(f"()=>{{const e=document.querySelector('{s}');if(!e)return null;const r=e.getBoundingClientRect();return [r.left,r.width]}}")
            # A scene hidden at this width (display: none) has nothing to frame.
            if r and r[1] > 0 and (abs(r[0]) > 0.5 or abs(r[1] - w) > 0.5):
                bad.append(f"{w}x{h} {s} left={r[0]:.0f} width={r[1]:.0f}")
        # A pinned scene's pin must sit at the top of its section, or the
        # section's own padding shows the scene before it for that many px
        # (the knoll's 90px top padding doubled the reel, 2026-10-25).
        for sec, pin in [(".knoll", ".knoll__pin"), (".irisout", ".irisout__pin"), (".rollin", ".rollin__pin"), (".cam", ".cam__pin")]:
            d = pg.evaluate(f"()=>{{const s=document.querySelector('{sec}'),p=document.querySelector('{pin}');if(!s||!p)return null;return p.getBoundingClientRect().top-s.getBoundingClientRect().top}}")
            if d is not None and abs(d) > 0.5:
                bad.append(f"{w}x{h} {pin} starts {d:.0f}px into {sec}")
        pg.close()
    b.close()
print("\n".join(bad) or "all pinned scenes are full bleed")
sys.exit(1 if bad else 0)
