"""Draft stand-ins for /preview/: the props agent's low-sample test renders,
keyed and measured, so the whole planned site can be seen before the real
renders spend an hour each. Outputs media/draft/ and media/draft/boxes.json
(screen and tape boxes as percentages of each image)."""
import json
import sys
from pathlib import Path

from PIL import Image

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "/private/tmp/claude-501/pm")
OUT = Path(__file__).resolve().parent.parent / "media/draft"
OUT.mkdir(parents=True, exist_ok=True)


def key_green(im):
    """Green screen to alpha, with a soft edge and spill pulled out."""
    im = im.convert("RGBA")
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            lead = g - max(r, b)
            if lead > 40 and g > 70:
                px[x, y] = (r, g, b, 0)
            elif lead > 12:
                k = (lead - 12) / 28
                px[x, y] = (r, max(r, b), b, int(255 * (1 - k)))
    return im


def box(quad, size):
    xs = [p[0] for p in quad]
    ys = [p[1] for p in quad]
    w, h = size
    return {"l": min(xs) / w * 100, "t": min(ys) / h * 100,
            "w": (max(xs) - min(xs)) / w * 100, "h": (max(ys) - min(ys)) / h * 100}


boxes = {}
pr = json.loads((SRC / "premiere/screen_full.json").read_text())
Image.open(SRC / "premiere/prev48.png").convert("RGB").save(OUT / "premiere.webp", quality=82)
boxes["premiere"] = box(pr["corners"][-1], pr["size"])

mo = json.loads((SRC / "monitor/monitor_full.json").read_text())
key_green(Image.open(SRC / "monitor/prev.png")).save(OUT / "monitor.webp", quality=88)
boxes["monitor"] = box(mo["screen"], mo["size"])

Image.open(SRC / "knoll/prev.png").convert("RGB").save(OUT / "knolling.webp", quality=82)

sl = json.loads((SRC / "slate/slate_full.json").read_text())
Image.open(SRC / "slate/prev.png").convert("RGB").save(OUT / "slate.webp", quality=86)
boxes["slate"] = {k: box(v["quad"], sl["size"]) for k, v in sl["tape"].items()}

(OUT / "boxes.json").write_text(json.dumps(boxes, indent=1))
print(json.dumps(boxes))
