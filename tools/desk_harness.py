#!/usr/bin/env python3
"""Writes dist/desk-test/index.html: the house page() with only the Mac
desktop section in it, so item 9 can be looked at on its own. Run after
build.py, which has already copied media/ (including media/desk/) to dist.
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import build  # noqa: E402
from site_desk import desk_section  # noqa: E402


def main():
    films = json.loads((ROOT / "data/films.json").read_text())["films"]
    photos = json.loads((ROOT / "media/photos/photos.json").read_text())
    body = desk_section(films, photos) + build.screenings(films)
    # path="/" so app.js treats film links as in-place screenings, as on home.
    html = build.page("Desk test, Parker Manley", body, path="/")
    html = html.replace('<link rel="stylesheet" href="/styles.css">',
                        '<link rel="stylesheet" href="/styles.css">\n<link rel="stylesheet" href="/desk.css">')
    html = html.replace('<script src="/app.js" defer></script>',
                        '<script src="/app.js" defer></script>\n<script src="/desk.js" defer></script>')
    # The test page shows the desk alone: no masthead or footer around it.
    html = html.replace("</head>", "<style>.mast,.foot,.skip{display:none!important}</style>\n</head>")
    out = build.DIST / "desk-test"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(html)
    for name in ("desk.css", "desk.js"):
        shutil.copy(ROOT / "src" / name, build.DIST / name)
    if (ROOT / "media/desk").exists():
        shutil.copytree(ROOT / "media/desk", build.DIST / "media/desk", dirs_exist_ok=True)
    print("wrote", out / "index.html")


if __name__ == "__main__":
    main()
