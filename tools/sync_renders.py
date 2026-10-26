"""Copy finished draft renders from the render folder into media/, so the
site picks each one up the moment it lands. Safe to run any time."""
import shutil
import sys
from pathlib import Path

from PIL import Image

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "/private/tmp/claude-501/pm/draft3")
ROOT = Path(__file__).resolve().parent.parent
out = ROOT / "media/hall"
out.mkdir(parents=True, exist_ok=True)
n = 0
for f in sorted((SRC / "hall").glob("*.jpg")):
    dst = out / f"{f.stem}.webp"
    if not dst.exists() or dst.stat().st_mtime < f.stat().st_mtime:
        Image.open(f).convert("RGB").save(dst, quality=86)
        n += 1
print(f"hall stills synced: {n}")
