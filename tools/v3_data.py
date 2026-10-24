"""One-off: apply Parker's Oct 23 text answers to films.json and import his posters."""
import json
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
POSTERS = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/Posters"

p = ROOT / "data/films.json"
d = json.loads(p.read_text())
films = d["films"]
by = {f["slug"]: f for f in films}

for s in ("the-five-stages-of-wasabi", "the-perfect-hill"):
    by[s]["featured"] = True
by["the-bend"]["role"] = "Co-directed & cinematography"
by["reflect"]["role"] = "Co-directed & written"
by["as-we-are-you-shall-be"]["synopsis"] = by["as-we-are-you-shall-be"]["synopsis"].replace("Jeremey", "Jeremy")
by["the-ultimate-trojan"]["year"] = 2025
by["the-ultimate-trojan"]["years"] = "2025 & 2026"
if "austin-ringgold" not in by:
    at = [f["slug"] for f in films].index("wither-and-bloom") + 1
    films.insert(at, {
        "slug": "austin-ringgold", "title": "Austin Ringgold Presidency Video", "year": 2025,
        "genre": "Student Council Video", "minutes": 3, "youtube": "",
        "drive": "1lQDbJo4SwuJ-0UjtA8ezk-kG33Vk3mir", "featured": False,
        "synopsis": "Made to help Austin Ringgold become President of the Peak to Peak Student Council, showing why he was the right choice.",
        "role": "", "cast": [], "crew": [], "made_for": "", "festivals": [], "music": ["Kid Rock"],
    })
p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")

ART = {
    "hooked-on-a-feeling": "2024/HookedOnAFeeling.jpeg", "abundance": "2025/AbundancePoster2.png",
    "bye-bye-bye": "2025/BYEBYEBYEposter.png", "the-brawn-identity": "2025/BrawnPoster.jpg",
    "dogme-oner": "2025/DogmaOner.jpg", "the-perfect-hill": "2025/HillsPoster.jpg",
    "the-pills": "2025/PillsPoster2.jpg", "ripped": "2025/RippedPoster.png",
    "wither-and-bloom": "2025/Wither&BloomPoster.jpg", "anthropocene": "2026/ANTHROPOCENE2.jpg",
    "as-we-are-you-shall-be": "2026/AWAYSBposter.jpg", "everybody": "2026/BackstreetPoster.jpg",
    "the-bend": "2026/BendPoster.jpg", "the-best-worst-day-of-my-life": "2026/BestWorstPoster.jpg",
    "hot-tempered": "2026/HotTempered.jpg", "a-moment": "2026/Moment poster.png",
    "reflect": "2026/ReflectPoster.jpg", "the-runaround": "2026/RunaroundPoster.png",
    "scar-tissue": "2026/ScarTissue.jpg", "the-teeth-deal": "2026/Teeth.jpg",
}
out = ROOT / "media/art"
out.mkdir(exist_ok=True)
sizes = {}
for slug, rel in ART.items():
    im = ImageOps.exif_transpose(Image.open(POSTERS / rel)).convert("RGB")
    im.thumbnail((1400, 1400))
    im.save(out / f"{slug}.jpg", quality=84, optimize=True, progressive=True)
    sizes[slug] = im.size
(out / "art.json").write_text(json.dumps(sizes))
print("featured:", [f["slug"] for f in films if f["featured"]])
print("posters:", len(sizes))
