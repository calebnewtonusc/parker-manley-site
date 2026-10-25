#!/usr/bin/env python3
"""Builds the static site into dist/ from data/films.json, media/ and src/.

Adding a film: add an entry to data/films.json (newest goes where Parker
ranks it), drop media/posters/<slug>.jpg, and for a featured film
media/loops/<slug>.mp4 and <slug>-720.mp4. Then run `python3 build.py`.
"""
import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
EMAIL = "prmanley@usc.edu"
YOUTUBE = "https://www.youtube.com/@rekrapyelnam6777"
INSTAGRAM = "https://www.instagram.com/parkertheman677/"
SITE = "https://parkermanley.com"

e = html.escape

LAUREL = (
    '<svg viewBox="0 0 12 22" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="1.1" stroke-linecap="round">'
    '<path d="M9 21C4 17 2.5 11 4.5 2"/><path d="M4.2 6c-2-.6-3.2-2-3.2-3.6 1.8.2 3 1.4 3.2 3.6z"/>'
    '<path d="M4 11c-2.2-.2-3.6-1.4-3.8-3 2-.1 3.4 1 3.8 3z"/><path d="M5.2 15.6c-2.2.3-3.8-.6-4.4-2.1 1.9-.5 3.6.3 4.4 2.1z"/>'
    '<path d="M4.6 6.4c1.6-1 2.2-2.6 1.8-4.2-1.6.7-2.3 2.3-1.8 4.2z"/><path d="M4.4 11.2c1.8-.8 2.6-2.3 2.4-3.9-1.7.6-2.6 2.1-2.4 3.9z"/>'
    "</g></svg>"
)


def art_src(f):
    if exists(f"media/art/{f['slug']}.jpg"):
        return f"/media/art/{f['slug']}.jpg"
    return f"/media/posters/{f['slug']}.jpg"


def meta_line(f):
    parts = [f.get("years") or str(f["year"])] if f.get("year") else []
    parts.append(f["genre"])
    if f.get("minutes"):
        parts.append(f"{f['minutes']} min")
    return " · ".join(parts)


def page(title, body, *, current="", description="", image="/media/portraits/rock.jpg", path="/"):
    def nav(href, label, key):
        cur = ' aria-current="page"' if current == key else ""
        return f'<a href="{href}"{cur}>{label}</a>'
    desc = e(description or "Parker Manley is a director and cinematographer studying Film and Television Production at USC.")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#12110e">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{SITE}{image}">
<meta property="og:url" content="{SITE}{path}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=Jost:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/styles.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="mast">
  <nav class="mast__side mast__side--l" aria-label="Work">{nav("/#all-films", "Films", "films")}{nav("/photography/", "Photography", "photos")}</nav>
  <a class="mast__name" href="/">Parker Manley</a>
  <nav class="mast__side mast__side--r" aria-label="About">{nav("/#about", "About", "about")}{nav("/#contact", "Contact", "contact")}</nav>
</header>
<main id="main">
{body}
</main>
<footer class="foot">Parker Manley · Boulder, Colorado to Los Angeles</footer>
<script src="/app.js" defer></script>
</body>
</html>
"""


def exists(rel):
    return (ROOT / rel).exists()


def festival_program(films):
    """All Films as a festival program: one chapter per year, newest first,
    Parker's own order kept inside each year."""
    by_year = {}
    for f in films:
        by_year.setdefault(f["year"] or 0, []).append(f)
    out = []
    for y in sorted(by_year, reverse=True):
        group = by_year[y]
        rows = []
        for f in group:
            still = f"/media/stills/{f['slug']}-1.jpg"
            if not exists(still[1:]):
                still = f"/media/posters/{f['slug']}.jpg"
            loop = f"media/loops/{f['slug']}-720.mp4"
            loop_attr = f' data-loop="/{loop}"' if f["featured"] and exists(loop) else ""
            role = f["role"] or "Written, directed, shot &amp; edited"
            rows.append(
                f'<li><a class="bill" href="/films/{f["slug"]}/" data-still="{still}"{loop_attr} data-title="{e(f["title"])}">'
                f'<span class="bill__mat"><img src="{art_src(f)}" alt="" loading="lazy"></span>'
                f'<span class="bill__text"><span class="bill__title">{e(f["title"])}</span>'
                f'<span class="bill__meta">{e(meta_line(f))}</span>'
                f'<span class="bill__role">{role if not f["role"] else e(role)}</span></span></a></li>'
            )
        first = group[0]
        first_still = f"/media/stills/{first['slug']}-1.jpg"
        if not exists(first_still[1:]):
            first_still = f"/media/posters/{first['slug']}.jpg"
        count = f"{len(group)} film{'s' if len(group) != 1 else ''}"
        # The Grand Budapest move: each era gets its own aspect ratio, the
        # older years boxier, so the screen changes shape as you go back.
        ratio = {2026: "2.39", 2025: "1.85", 2024: "1.66"}.get(y, "1.37")
        out.append(f"""    <section class="yr" aria-label="{y}">
      <div class="yr__side"><div class="yr__stick">
        <p class="yr__n">{y}</p>
        <p class="yr__count">{count} &middot; {ratio} : 1</p>
        <div class="yr__screen" data-ar="{ratio}" aria-hidden="true"><img src="{first_still}" alt="" loading="lazy"><span class="yr__now">{e(first["title"])}</span></div>
      </div></div>
      <ol class="yr__list">
{chr(10).join(rows)}
      </ol>
    </section>""")
    return "\n".join(out)


def end_credits(films):
    """End credits built from films.json, so every name on it is real."""
    seen, names = set(), []
    for f in films:
        for n in list(f["cast"]) + [n for _, n in f["crew"]]:
            for part in n.split(" & "):
                part = part.strip()
                if part and part != "Parker Manley" and part not in seen:
                    seen.add(part)
                    names.append(part)
    names.sort(key=lambda n: n.split()[-1])
    titles = "".join(f"<li>{e(f['title'])}</li>" for f in films)
    people = "".join(f"<li>{e(n)}</li>" for n in names)
    pair = lambda r, n: f'<div class="roll__pair"><dt>{r}</dt><dd>{n}</dd></div>'
    return f"""  <div class="roll">
    <p class="roll__pre">A Parker Manley picture</p>
    <dl class="roll__pairs">
      {pair("Directed by", "Parker Manley")}
      {pair("Director of Photography", "Parker Manley")}
      {pair("Edited by", "Parker Manley")}
    </dl>
    <h3 class="roll__h">The films</h3>
    <ul class="roll__cols">{titles}</ul>
    <h3 class="roll__h">With</h3>
    <ul class="roll__cols roll__cols--names">{people}</ul>
    <dl class="roll__pairs">
      {pair("Reel music", "&ldquo;I Am Chemistry&rdquo; by Yeasayer")}
      {pair("Filmed in", "Boulder, Colorado<br>Los Angeles, California")}
    </dl>
  </div>
"""


def home(films):
    featured = [f for f in films if f["featured"]]
    archive = [f for f in films if not f["featured"]]

    showing = [
        {
            "title": f["title"],
            "meta": meta_line(f),
            "synopsis": f["synopsis"],
            "festivals": " · ".join(f["festivals"]) or (f["made_for"] if f["made_for"] else ""),
            "href": f"/films/{f['slug']}/",
        }
        for f in featured
    ]
    layers = "\n".join(
        f'<video muted loop playsinline preload="{"auto" if i == 0 else "none"}" poster="/media/posters/{f["slug"]}.jpg" '
        f'data-src="/media/loops/{f["slug"]}.mp4" data-src-small="/media/loops/{f["slug"]}-720.mp4"'
        + (' class="is-on"' if i == 0 else "") + "></video>"
        for i, f in enumerate(featured)
    )
    n = len(featured)
    cards = "\n".join(
        f'<div class="line{" is-on" if i == 0 else ""}"{"" if i == 0 else " aria-hidden=\"true\""}>'
        f'<p class="card__no">No. {i + 1} of {n}</p>'
        f'<h3 class="card__title">{e(s["title"])}</h3>'
        f'<p class="card__meta">{e(s["meta"])}</p>'
        f'<p class="card__syn">{e(s["synopsis"])}</p>'
        + (f'<p class="card__fest">{e(s["festivals"])}</p>' if s["festivals"] else "")
        + f'<a class="btn btn--ember" href="{s["href"]}"{"" if i == 0 else " tabindex=\"-1\""}>Watch the film</a></div>'
        for i, s in enumerate(showing)
    )
    tickets = "\n".join(
        f'<li><a href="{s["href"]}" data-step="{i}" aria-current="{"true" if i == 0 else "false"}">'
        f'<span class="n">{i + 1:02d}</span><span class="t">{e(s["title"])}</span></a></li>'
        for i, s in enumerate(showing)
    )
    ticks = "".join(f'<i{" class=\"is-on\"" if i == 0 else ""}></i>' for i in range(n))
    program = festival_program(films)
    arch = "\n".join(
        f'<li><a href="/films/{f["slug"]}/"><span class="y">{f.get("years") or f["year"] or ""}</span>'
        f'<span class="tt">{e(f["title"])}</span><span class="g">{e(f["genre"])}</span></a></li>'
        for f in archive
    )
    body = f"""
<div class="leader" aria-hidden="true">
  <svg class="leader__dial" viewBox="0 0 200 200">
    <circle cx="100" cy="100" r="92"/><circle cx="100" cy="100" r="74"/>
    <path d="M100 0V200M0 100H200"/>
  </svg>
  <span class="leader__sweep"></span>
  <span class="leader__n">3</span>
</div>
<div class="opening">
  <span class="cue" aria-hidden="true"></span>
  <div class="opening__pin">
    <div class="opening__frame">
      <video id="reel" autoplay muted loop playsinline preload="auto" poster="/media/reel/reel-poster.jpg"
        data-src="/media/reel/reel.mp4" data-src-small="/media/reel/reel-720.mp4" aria-label="Parker Manley reel"></video>
    </div>
    <div class="titlecard">
      <p class="titlecard__pre">A picture by</p>
      <h1 class="titlecard__name">Parker Manley</h1>
      <p class="titlecard__role">Director &middot; Cinematographer &middot; Editor</p>
    </div>
    <button class="sound" type="button" aria-pressed="false"><svg class="sun" viewBox="0 0 24 24" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.6M12 18.9v2.6M2.5 12h2.6M18.9 12h2.6M5.3 5.3l1.8 1.8M16.9 16.9l1.8 1.8M5.3 18.7l1.8-1.8M16.9 7.1l1.8-1.8"/></g></svg><span class="label">Sound off</span></button>
  </div>
</div>

<section class="reels" id="films" aria-label="Featured films">
  <div class="scene scene--films">
    <div class="scene__pin">
      <div class="scene__bg" aria-hidden="true">
{layers}
      </div>
      <p class="reels__label">Now Showing</p>
      <div class="scene__copy">
{cards}
      </div>
      <nav class="scene__nav tickets" aria-label="Featured films"><ol>
{tickets}
      </ol></nav>
      <div class="scene__ticks" aria-hidden="true">{ticks}</div>
    </div>
  </div>
  <div class="lobby" id="all-films">
    <div class="head"><h2>All Films</h2></div>
    <p class="lobby__sub">The full program, year by year.</p>
{program}
  </div>
</section>

<section class="about" id="about" aria-label="About Parker">
  <div class="scene">
    <div class="scene__pin">
      <div class="scene__bg" aria-hidden="true">
        <img class="is-on" src="/media/portraits/set.jpg" alt="" data-pos="film">
        <img src="/media/portraits/bigbear.jpg" alt="" data-pos="outdoors" loading="lazy">
        <img src="/media/portraits/faith.jpg" alt="" data-pos="faith" loading="lazy">
      </div>
      <div class="scene__copy">
        <div class="line is-on">
          <p class="card__no">Chapter I &middot; Storytelling</p>
          <p class="line__big">I'm a storyteller from Boulder, Colorado, studying Film and Television Production at USC.</p>
          <p class="line__small">On set or at the Dungeons &amp; Dragons table. More than 25 shorts since 2023, most of them written, directed, shot and edited by me.</p>
        </div>
        <div class="line" aria-hidden="true">
          <p class="card__no">Chapter II &middot; Outdoors</p>
          <p class="line__big">I'm a big hiker and camper.</p>
          <p class="line__small">I grew up at the foot of the Rockies. At USC: SC Outfitters, fencing, the Trojan Stunt Team and EscapeSC.</p>
        </div>
        <div class="line" aria-hidden="true">
          <p class="card__no">Chapter III &middot; Faith</p>
          <p class="line__big">I lay all my work before Jesus.</p>
          <p class="line__small">&ldquo;So, whether you eat or drink, or whatever you do, do all to the glory of God.&rdquo; 1 Corinthians 10:31</p>
        </div>
      </div>
      <div class="scene__ticks" aria-hidden="true"><i class="is-on"></i><i></i><i></i></div>
    </div>
  </div>
</section>

<section class="contact" id="contact" aria-labelledby="contact-h">
{end_credits(films)}
  <div class="nextup">
    <div class="nextup__iris">
      <p class="card__no">Coming soon</p>
      <h2 id="contact-h" class="nextup__title">Your film</h2>
      <p class="contact__lede">Looking for a director, a DP or an editor? I'd love to hear about it.</p>
      <a class="contact__mail" href="mailto:{EMAIL}">{EMAIL}</a>
    </div>
    <figure class="contact__photo"><img src="/media/portraits/rock.jpg" alt="Parker framing a shot on a granite outcrop above a pine forest" loading="lazy"></figure>
  </div>
  <div class="slate">
    <div class="slate__clap" aria-hidden="true"><span class="slate__stick slate__stick--top"></span><span class="slate__stick"></span></div>
    <form class="form slate__board" action="https://formsubmit.co/ajax/{EMAIL}" method="POST">
      <input type="hidden" name="_subject" value="New message from parkermanley.com">
      <input type="hidden" name="_template" value="table">
      <div class="hp" aria-hidden="true"><input type="text" name="_honey" tabindex="-1" autocomplete="off"></div>
      <div class="slate__info" aria-hidden="true"><span><small>Prod.</small>Your next film</span><span><small>Director</small>P. Manley</span><span><small>Take</small>1</span></div>
      <div class="row">
        <label>Name<input name="name" autocomplete="name" required></label>
        <label>Email<input name="email" type="email" autocomplete="email" required></label>
      </div>
      <label>Message<textarea name="message" required></textarea></label>
      <button class="btn btn--ember" type="submit">Action</button>
      <p class="form__status" role="status"></p>
    </form>
  </div>
  <div class="elsewhere"><a href="{YOUTUBE}" rel="noopener">YouTube</a><a href="{INSTAGRAM}" rel="noopener">Instagram</a></div>
</section>
"""
    return page("Parker Manley, Director, Cinematographer, Editor", body, current="", path="/", image="/media/reel/reel-poster.jpg")


def film_page(films, i):
    f = films[i]
    prev_f = films[i - 1] if i > 0 else None
    next_f = films[i + 1] if i + 1 < len(films) else None
    poster = f"/media/posters/{f['slug']}.jpg"

    credits = [(f["role"] or "Written, Directed, Shot & Edited", "Parker Manley")]
    credits += [(r, n) for r, n in f["crew"]]
    if f["cast"]:
        credits.append(("Starring", "<br>".join(e(n) for n in f["cast"])))
    if f["music"]:
        credits.append(("Music", "<br>".join(e(n) for n in f["music"])))
    dl = "\n".join(
        f"<dt>{e(r)}</dt><dd>{n if r in ('Starring', 'Music') else e(n)}</dd>" for r, n in credits
    )
    laurels = ""
    if f["festivals"]:
        laurels = '<ul class="laurels" aria-label="Festivals">' + "".join(
            f"<li>{LAUREL}{e(x)}</li>" for x in f["festivals"]
        ) + "</ul>"
    made = f'<p class="made-for">{e(f["made_for"])}</p>' if f["made_for"] else ""
    sub = f'<p class="film__sub">{e(f["subtitle"])}</p>' if f.get("subtitle") else ""
    stills = [f"/media/stills/{f['slug']}-{n}.jpg" for n in (1, 2) if exists(f"media/stills/{f['slug']}-{n}.jpg")]
    poster_html = ""
    if exists(f"media/art/{f['slug']}.jpg"):
        poster_html = f'<figure class="film__poster"><img src="/media/art/{f["slug"]}.jpg" alt="{e(f["title"])} poster" loading="lazy"></figure>'
    stills_html = ""
    if len(stills) == 2:
        stills_html = '<div class="stills">' + "".join(
            f'<img src="{s}" alt="Still from {e(f["title"])}" loading="lazy">' for s in stills
        ) + "</div>"

    def pager_link(g, cls, label):
        if not g:
            return f'<span class="{cls}"></span>'
        return f'<a class="{cls}" href="/films/{g["slug"]}/"><small>{label}</small>{e(g["title"])}</a>'

    body = f"""
<article class="film">
  <div class="player" {'data-yt="' + f['youtube'] + '"' if f.get('youtube') else 'data-drive="' + f.get('drive', '') + '"'}>
    <img src="{poster}" alt="">
    <button type="button" aria-label="Play {e(f['title'])}"><span>&#9654;&nbsp; Play the film</span></button>
  </div>
  <header class="film__head">
    <p class="now__meta">{e(meta_line(f))}</p>
    <h1>{e(f['title'])}</h1>
    {sub}
    <p class="film__syn">{e(f['synopsis'])}</p>
    {laurels}
    {made}
  </header>
  <div class="credits"><dl>
{dl}
  </dl></div>
  {poster_html}
  {stills_html}
  <nav class="pager" aria-label="More films">
    {pager_link(prev_f, "prev", "Previous")}
    <a class="all" href="/#films">All films</a>
    {pager_link(next_f, "next", "Next")}
  </nav>
</article>
"""
    return page(
        f"{f['title']}, a film by Parker Manley",
        body,
        current="films",
        description=f["synopsis"],
        image=poster,
        path=f"/films/{f['slug']}/",
    )


def photography():
    data = ROOT / "media/photos/photos.json"
    photos = json.loads(data.read_text()) if data.exists() else []
    shots = "\n".join(
        f'<button type="button" data-full="/media/photos/{p["file"]}" aria-label="Open photo {i + 1} of {len(photos)}">'
        f'<img src="/media/photos/thumb/{p["file"]}" width="{p["w"]}" height="{p["h"]}" alt="Photograph by Parker Manley" loading="lazy"></button>'
        for i, p in enumerate(photos)
    )
    n = len(photos)
    body = f"""
<div class="sheet-head">
  <h1>Photography</h1>
  <p>Light painting, ice, mountains and the people in front of my camera.</p>
  <div class="sizes" role="group" aria-label="View">
    <button type="button" data-view="projector" aria-pressed="true">Projector</button>
    <button type="button" data-view="sheet" aria-pressed="false">Contact sheet</button>
  </div>
</div>
<div class="photos" data-view="projector">
  <section class="projector" aria-roledescription="carousel" aria-label="Photographs, one at a time">
    <div class="projector__beam" aria-hidden="true"></div>
    <figure class="slide">
      <div class="slide__mount"><img alt="Photograph by Parker Manley"></div>
      <figcaption class="slide__no"></figcaption>
    </figure>
    <button class="projector__pv" type="button" aria-label="Previous slide">&#8592;</button>
    <button class="projector__nx" type="button" aria-label="Next slide">&#8594;</button>
    <div class="tray" role="slider" tabindex="0" aria-label="Carousel tray" aria-valuemin="1" aria-valuemax="{n}" aria-valuenow="1">
      <svg viewBox="0 0 120 120" aria-hidden="true"><circle class="tray__rim" cx="60" cy="60" r="56"/><circle class="tray__hub" cx="60" cy="60" r="16"/><g class="tray__slots"></g></svg>
      <span class="tray__count">01 / {n:02d}</span>
    </div>
  </section>
  <div class="sheet" data-size="s">
{shots}
  </div>
</div>
"""
    return page("Photography, Parker Manley", body, current="photos", path="/photography/")


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="6" fill="#12110e"/><rect x="5" y="11" width="22" height="10" fill="#d07a45"/></svg>"""

def main():
    films = json.loads((ROOT / "data/films.json").read_text())["films"]
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    (DIST / "index.html").write_text(home(films))
    for i, f in enumerate(films):
        out = DIST / "films" / f["slug"]
        out.mkdir(parents=True)
        (out / "index.html").write_text(film_page(films, i))
    (DIST / "photography").mkdir()
    (DIST / "photography/index.html").write_text(photography())
    for name in ("styles.css", "app.js", "topo.svg"):
        shutil.copy(ROOT / "src" / name, DIST / name)
    (DIST / "favicon.svg").write_text(FAVICON)
    if (ROOT / "media").exists():
        shutil.copytree(ROOT / "media", DIST / "media")
    missing = [
        p for f in films for p in (
            [f"media/posters/{f['slug']}.jpg"]
            + ([f"media/loops/{f['slug']}.mp4", f"media/loops/{f['slug']}-720.mp4"] if f["featured"] else [])
        ) if not exists(p)
    ]
    print(f"built {len(films)} film pages")
    if missing:
        print("missing media:", *missing, sep="\n  ")


if __name__ == "__main__":
    main()
