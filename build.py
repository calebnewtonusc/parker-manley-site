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


def meta_line(f):
    parts = [str(f["year"])] if f.get("year") else []
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
<link href="https://fonts.googleapis.com/css2?family=Jost:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/styles.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="mast">
  <nav class="mast__side mast__side--l" aria-label="Work">{nav("/#films", "Films", "films")}{nav("/photography/", "Photography", "photos")}</nav>
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
    videos = "\n".join(
        f'<video muted loop playsinline preload="{"auto" if i == 0 else "none"}" poster="/media/posters/{f["slug"]}.jpg" '
        f'data-src="/media/loops/{f["slug"]}.mp4" data-src-small="/media/loops/{f["slug"]}-720.mp4"'
        + (' class="is-on"' if i == 0 else "") + "></video>"
        for i, f in enumerate(featured)
    )
    programme = "\n".join(
        f'<li><a href="/films/{f["slug"]}/" aria-current="{"true" if i == 0 else "false"}">'
        f'<span class="n">{i + 1:02d}</span><span class="t">{e(f["title"])}</span><span class="y">{f["year"] or ""}</span></a></li>'
        for i, f in enumerate(featured)
    )
    arch = "\n".join(
        f'<li><a href="/films/{f["slug"]}/"><span class="y">{f["year"] or ""}</span>'
        f'<span class="tt">{e(f["title"])}</span><span class="g">{e(f["genre"])}</span></a></li>'
        for f in archive
    )
    first = featured[0]
    body = f"""
<div class="hero">
  <div class="gate">
    <video id="reel" autoplay muted loop playsinline preload="auto" poster="/media/reel/reel-poster.jpg"
      data-src="/media/reel/reel.mp4" data-src-small="/media/reel/reel-720.mp4" aria-label="Parker Manley reel"></video>
  </div>
  <p class="hero__role">Director &amp; Cinematographer</p>
  <h1 class="hero__name">Parker Manley</h1>
  <button class="sound" type="button" aria-pressed="false"><span class="bars" aria-hidden="true"><i></i><i></i><i></i></span><span class="label">Sound off</span></button>
</div>

<section class="showing" id="films" aria-labelledby="films-h">
  <div class="head"><h2 id="films-h">Now Showing</h2></div>
  <div class="screen-wrap">
    <a class="screen" href="/films/{first['slug']}/" aria-label="Watch {e(first['title'])}">
      {videos}
      <span class="screen__play" aria-hidden="true">Watch the film</span>
    </a>
    <div class="now" aria-live="polite">
      <p class="now__meta">{e(showing[0]['meta'])}</p>
      <h3 class="now__title">{e(first['title'])}</h3>
      <p class="now__syn">{e(first['synopsis'])}</p>
      <p class="now__fest">{e(showing[0]['festivals'])}</p>
      <div class="now__cta"><a class="btn btn--ember now__watch" href="/films/{first['slug']}/">Watch the film</a></div>
    </div>
  </div>
  <ol class="programme" aria-label="Featured films">
{programme}
  </ol>
  <details class="archive">
    <summary>Every other film ({len(archive)}) <span class="chev" aria-hidden="true">&#8964;</span></summary>
    <ol>
{arch}
    </ol>
  </details>
  <script type="application/json" id="showing-data">{json.dumps(showing)}</script>
</section>

<section class="about" id="about" aria-labelledby="about-h">
  <div class="head"><h2 id="about-h">About</h2></div>
  <figure class="about__photo"><img src="/media/portraits/rock.jpg" alt="Parker framing a shot on a granite outcrop above a pine forest" loading="lazy"></figure>
  <p class="about__lede">I'm a filmmaker from Boulder, Colorado, studying Film and Television Production at USC.</p>
  <ul class="beats">
    <li><h3>Film</h3><p>Since 2023 I've made more than 25 shorts, from horror to a silent film to a Wes Anderson homage. On most of them I wrote, directed, shot and edited.</p></li>
    <li><h3>Faith</h3><p>I follow Jesus, and it shapes the stories I want to tell. At USC I'm part of Christian Challenge.</p></li>
    <li><h3>Outdoors</h3><p>I grew up at the foot of the Rockies and I'm happiest outside. At USC that means SC Outfitters.</p></li>
  </ul>
  <p class="also">Also fencing, the Trojan Stunt Team, EscapeSC, and Dungeons &amp; Dragons.</p>
  <blockquote class="verse">
    <p>So, whether you eat or drink, or whatever you do, do all to the glory of God.</p>
    <cite>1 Corinthians 10:31</cite>
  </blockquote>
</section>

<section class="contact" id="contact" aria-labelledby="contact-h">
  <div class="head"><h2 id="contact-h">Contact</h2></div>
  <figure class="contact__photo"><img src="/media/portraits/set.jpg" alt="Parker behind a Sony cinema camera on set" loading="lazy"></figure>
  <p class="contact__lede">Looking for a director or a DP? I'd love to hear about it.</p>
  <a class="contact__mail" href="mailto:{EMAIL}">{EMAIL}</a>
  <form class="form" action="https://formsubmit.co/ajax/{EMAIL}" method="POST">
    <input type="hidden" name="_subject" value="New message from parkermanley.com">
    <input type="hidden" name="_template" value="table">
    <div class="hp" aria-hidden="true"><input type="text" name="_honey" tabindex="-1" autocomplete="off"></div>
    <div class="row">
      <label>Name<input name="name" autocomplete="name" required></label>
      <label>Email<input name="email" type="email" autocomplete="email" required></label>
    </div>
    <label>Message<textarea name="message" required></textarea></label>
    <button class="btn btn--ember" type="submit">Send</button>
    <p class="form__status" role="status"></p>
  </form>
  <div class="elsewhere"><a href="{YOUTUBE}" rel="noopener">YouTube</a><a href="{INSTAGRAM}" rel="noopener">Instagram</a></div>
</section>
"""
    return page("Parker Manley, Director & Cinematographer", body, current="", path="/", image="/media/reel/reel-poster.jpg")


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
  <div class="player" data-yt="{f['youtube']}">
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
    body = f"""
<div class="sheet-head">
  <h1>Photography</h1>
  <p>Light painting, ice, mountains and the people in front of my camera.</p>
  <div class="sizes" role="group" aria-label="Photo size">
    <button type="button" data-size="s" aria-pressed="true">Contact sheet</button>
    <button type="button" data-size="l" aria-pressed="false">Large</button>
  </div>
</div>
<div class="sheet" data-size="s">
{shots}
</div>
<div class="lightbox" role="dialog" aria-modal="true" aria-label="Photo viewer">
  <img alt="">
  <button class="x" type="button" aria-label="Close">&#10005;</button>
  <button class="pv" type="button" aria-label="Previous photo">&#8592;</button>
  <button class="nx" type="button" aria-label="Next photo">&#8594;</button>
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
    for name in ("styles.css", "app.js"):
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
