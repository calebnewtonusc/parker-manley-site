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
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400&family=Jost:wght@400;500&family=Oswald:wght@600;700&family=Caveat:wght@500&family=Bebas+Neue&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/styles.css">
</head>
<body class="{'is-home' if path == '/' else ''}">
<a class="skip" href="#main">Skip to content</a>
<header class="mast">
  <a class="mast__name" href="/">Parker Manley</a>
  <nav class="mast__side mast__side--r" aria-label="Pages">{nav("/photography/", "Photography", "photos")}{nav("/#contact", "Contact", "contact")}</nav>
  <button class="mast__sound" type="button" aria-pressed="true" aria-label="Sound"><svg viewBox="0 0 24 24" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="7" cy="8" r="4"/><circle cx="16" cy="8" r="4"/><rect x="4" y="13" width="12" height="7" rx="1"/><path d="M16 15l5-2.5v8L16 18"/></g></svg><span class="mast__sound-off" aria-hidden="true"></span></button>
</header>
<main id="main">
{body}
</main>
<footer class="foot"><div class="foot__pin"><img class="foot__star" src="/media/props/star/star-1000.webp" srcset="/media/props/star/star-1000.webp 1000w, /media/props/star/star-2000.webp 2000w" sizes="100vw" alt="A star on the Hollywood Walk of Fame reading Parker Manley" loading="lazy"><p class="foot__line">Parker Manley &middot; Boulder, Colorado to Los Angeles</p></div></footer>
<script src="/score.js" defer data-samples="clatter.mp3 clack.mp3 rip.mp3 shutter.mp3 flash.mp3 tapestop.mp3 crt.mp3 servo.mp3 runout.mp3 chk.mp3 stamp.mp3"></script>
<script src="/app.js" defer></script>
</body>
</html>
"""


def exists(rel):
    return (ROOT / rel).exists()


# Frames from films Parker shot himself, each with the one adjustment the
# monitor shows being made. The reasons describe what's visible in the frame.
LENS = [
    # None of these are in Now Showing: every film appears in one section only.
    ("anthropocene", 2, "nd", "0.0", "1.2", "ND in, so the sunlit rock keeps its detail"),
    ("ripped", 2, "iris", "1.4", "5.6", "Exposing for the light behind him, so he stays a silhouette"),
    ("the-pills", 2, "focus", "0.4", "1.2", "Focus on the reflection in the lens, not the face"),
    ("hot-tempered", 2, "wb", "3200", "4300", "Cooling the red room down so the skin doesn't go orange"),
    ("dogme-oner", 2, "focus", "3.0", "1.2", "Pulling focus off the window and onto her"),
    ("hooked-on-a-feeling", 1, "zoom", "50", "24", "Going wide so all five of them make the frame"),
]


def lens_scene(films):
    """A cinema camera's monitor. Each shot whips in, then one setting changes live."""
    by = {f["slug"]: f for f in films}
    shots = [(by[s_], n, k, a_, b_, why) for s_, n, k, a_, b_, why in LENS if s_ in by and exists(f"media/stills/{s_}-{n}.jpg")]
    items = "\n".join(
        f'<li data-src="/media/stills/{f["slug"]}-{n}.jpg" data-title="{e(f["title"])}" data-href="/films/{f["slug"]}/" '
        f'data-year="{f["year"]}" data-kind="{k}" data-from="{a_}" data-to="{b_}" data-why="{e(why)}"></li>'
        for f, n, k, a_, b_, why in shots
    )
    first = shots[0][0]
    return f"""<section class="lens" aria-label="Cinematography">
  <ol class="cam__shots" hidden>
{items}
  </ol>
  <div class="cam">
    <div class="cam__pin">
      <div class="cam__body">
        <span class="cam__tally" aria-hidden="true"></span>
        <div class="cam__screen">
          <div class="cam__frame"><div class="cam__strip">{"".join(f'<img src="/media/stills/{f["slug"]}-{n}.jpg" alt="">' for f, n, *_ in shots)}</div><span class="cam__tint"></span></div>
          <div class="vf" aria-hidden="true"><span class="vf__grid"></span><span class="vf__focus"></span></div>
          <div class="cam__hud" aria-hidden="true">
            <span class="cam__rec">Rec</span><span class="vf__tc">00:00:00:00</span>
            <span>24.00 fps</span><span>180.0&deg;</span><span>ISO 800</span>
            <span data-k="wb">5600K</span><span data-k="iris">T2.8</span><span data-k="nd">ND Clear</span><span data-k="zoom">35 mm</span>
          </div>
          <div class="cam__scale" aria-hidden="true"><span class="cam__mark"></span><span class="cam__dist">3.5 m</span></div>
          <div class="cam__call" aria-live="polite">
            <p class="cam__what">Adjusting focus</p>
            <p class="cam__val">0.9 m</p>
            <p class="cam__why"></p>
          </div>
          <span class="cam__meters" aria-hidden="true"><i></i><i></i></span>
        </div>
        <div class="cam__buttons" aria-hidden="true"><i>Menu</i><i>Disp</i><i>Peak</i><i>Zoom</i><i>Rec</i></div>
      </div>
      <p class="pan__cap"><a class="lens__title" href="/films/{first['slug']}/">{e(first['title'])}</a>
        <span class="lens__meta">{first['year']} &middot; Cinematography by Parker Manley</span></p>
    </div>
  </div>
</section>"""


def circuit(films):
    """The festival circuit: every laurel, stamped onto one poster."""
    entries = []
    for f in films:
        for fest in f["festivals"]:
            entries.append(("Official Selection", fest, f))
    for f in films:
        if f["made_for"].startswith("Accepted to"):
            entries.append(("Admission film", f["made_for"].replace("Accepted to the ", ""), f))
    fests = sum(len(f["festivals"]) for f in films)
    schools = sum(1 for f in films if f["made_for"].startswith("Accepted to"))
    items = "\n".join(
        f'<li class="laurel"><a href="/films/{f["slug"]}/"><span class="laurel__l">{LAUREL}</span>'
        f'<span class="laurel__t"><small>{kind}</small>{e(name)}<em>{e(f["title"])}</em></span>'
        f'<span class="laurel__r">{LAUREL}</span></a></li>'
        for kind, name, f in entries
    )
    return f"""<section class="circuit" aria-label="Festival selections">
  <div class="circuit__pin">
    <div class="searchlights" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
    <p class="circuit__count"><b class="circuit__n" data-to="{fests}">{fests}</b> festival selections &middot; <b>{schools}</b> films that got me into film school</p>
    <ul class="circuit__wall">
{items}
    </ul>
  </div>
</section>"""


def splice(reel, label):
    """A splice between reels: a strip of film whose edge print names the next one."""
    return (f'<div class="splice" aria-hidden="true"><span>Reel {reel} &nbsp;&#9656;&nbsp; {label}</span>'
            f'<span>Reel {reel} &nbsp;&#9656;&nbsp; {label}</span><span>Reel {reel} &nbsp;&#9656;&nbsp; {label}</span></div>')


def chair(line):
    """Part I's intertitle is the back of a director's chair."""
    return f"""<div class="intertitle intertitle--chair"><div class="chair" role="img" aria-label="A director's chair, the canvas back printed Director, P. Manley">
  <span class="chair__post chair__post--l"></span><span class="chair__post chair__post--r"></span>
  <span class="chair__canvas"><span class="chair__part">Part I</span><span class="chair__h">Director</span><span class="chair__name">P. Manley</span></span>
  <span class="chair__seat"></span>
  <span class="chair__leg chair__leg--a"></span><span class="chair__leg chair__leg--b"></span>
</div><p class="intertitle__line">{line}</p></div>"""


def intertitle(part, title, line):
    return f"""<div class="intertitle"><div class="intertitle__card">
  <p class="intertitle__part">{part}</p>
  <h2 class="intertitle__h">{title}</h2>
  <p class="intertitle__line">{line}</p>
</div></div>"""


def festival_program(films):
    """All Films as an edit timeline: every film a clip on V1, oldest on the
    left, its width set by its runtime. Parker's own order is kept inside
    each year."""
    # The timeline holds the films no other section shows.
    shown = {f["slug"] for f in films if f["featured"]} | {s_ for s_, *_ in LENS}
    by_year = {}
    for f in films:
        if f["slug"] in shown:
            continue
        by_year.setdefault(f["year"] or 0, []).append(f)
    clips = []
    for y in sorted(by_year):
        for f in by_year[y]:
            still = f"/media/stills/{f['slug']}-1.jpg"
            if not exists(still[1:]):
                still = f"/media/posters/{f['slug']}.jpg"
            loop = f"media/loops/{f['slug']}-720.mp4"
            loop_attr = f' data-loop="/{loop}"' if f["featured"] and exists(loop) else ""
            role = e(f["role"]) if f["role"] else "Written, directed, shot &amp; edited"
            clips.append(
                f'<a class="clip clip--y{y % 4}" href="/films/{f["slug"]}/" data-year="{y}" data-min="{f["minutes"] or 3}" '
                f'data-still="{still}"{loop_attr} data-title="{e(f["title"])}" data-meta="{e(meta_line(f))}" data-role="{role}">'
                f'<span class="clip__v"><img src="{art_src(f)}" alt="" loading="lazy"><span class="clip__name">{e(f["title"])}</span></span>'
                f'<span class="clip__a" aria-hidden="true"></span></a>'
            )
    first = by_year[sorted(by_year)[0]][0]
    def ec_row(label, cls, val, key=False):
        k = '<span class="ec__k"><i>&#9666;</i><b>&#9670;</b><i>&#9656;</i></span>' if key else '<span class="ec__k"></span>'
        return f'<div class="ec__row"><span class="ec__sw">&#9201;</span><span class="ec__l">{label}</span><span class="ec__v {cls}">{val}</span>{k}</div>'

    def lum(label, cls, val, pos, track=""):
        return (f'<div class="lu__row"><span class="lu__l">{label}</span><span class="lu__track {track}"><i></i></span>'
                f'<span class="lu__v {cls}">{val}</span></div>')

    return f"""    <div class="edit">
      <div class="edit__pin fc" aria-label="Every film, in an edit">
        <div class="fc__bar" aria-hidden="true"><span class="fc__home">&#8962;</span><i>Import</i><i class="is-on">Edit</i><i>Export</i><b class="fc__title">Parker Manley, 2023 to now - Edited</b><span class="fc__icons">&#9776; &#8679; &#9906; &#128264; &#9974;</span></div>
        <p class="fc__note"><span class="fc__note-i" aria-hidden="true">i</span>Scroll to move the playhead. Click any clip to watch the film.</p>
        <div class="fc__top">
          <section class="fc__panel fc__ec" aria-hidden="true">
            <div class="fc__tabs"><span>Lumetri Scopes</span><span>Source</span><span class="is-on">Effect Controls &#9776;</span></div>
            <div class="ec__src"><span>Source &middot; <b class="fxc__clip">{e(first['title'])}</b></span><span class="ec__seq">Parker Manley, 2023 to now</span></div>
            <div class="ec__body">
              <p class="ec__h">Video</p>
              <div class="ec__row ec__fx"><span>&#8250;</span><em>fx</em> Motion</div>
              <div class="ec__row"><span class="ec__sw">&#9201;</span><span class="ec__l">Position</span><span class="ec__v fxc__pos">960.0 &nbsp;540.0</span><span class="ec__k"></span></div>
              {ec_row("Scale", "fxc__scale", "100.0", True)}
              {ec_row("Rotation", "", "0.0&deg;")}
              <div class="ec__row ec__fx"><span>&#8250;</span><em>fx</em> Opacity</div>
              {ec_row("Opacity", "fxc__op", "100.0%")}
              <div class="ec__row ec__fx"><span>&#8250;</span><em>fx</em> <span class="fxc__trname">Lumetri Color</span></div>
              <div class="fxc__bar"><i class="fxc__fill"></i></div>
              {ec_row("Temperature", "fxc__temp", "0.0")}
              {ec_row("Exposure", "fxc__exp", "0.0", True)}
              <span class="ec__ph"></span>
            </div>
            <div class="ec__tc monitor__tc3">00:00:00:00</div>
          </section>
          <section class="fc__panel monitor" aria-label="Program monitor">
            <div class="fc__tabs"><span class="is-on">Program &#9776;</span><span class="fc__now">Now: <span class="monitor__title">{e(first['title'])}</span></span><a class="monitor__open" href="/films/{first['slug']}/">Open film</a></div>
            <div class="monitor__screen">
              <div class="monitor__a"><img alt="" src="/media/posters/{first['slug']}.jpg"></div>
              <div class="monitor__b"><img alt=""></div>
              <span class="monitor__trlabel"></span>
            </div>
            <div class="pm__row" aria-hidden="true"><span class="monitor__tc">00:00:00:00</span><span class="pm__dd">Fit &#9662;</span><span class="pm__marks"><i></i><i></i><i></i><i></i><i></i><i></i></span><span class="pm__dd">Full &#9662;</span><span class="pm__dur">01:42:00:00</span></div>
            <div class="pm__transport" aria-hidden="true"><i>&#9670;</i><i>[</i><i>]</i><i>&#8676;</i><i>&#9664;|</i><i class="pm__play">&#10073;&#10073;</i><i>|&#9654;</i><i>&#8677;</i></div>
            <span class="monitor__meta">{e(meta_line(first))}</span>
          </section>
          <section class="fc__panel fc__lu" aria-hidden="true">
            <div class="fc__tabs"><span class="is-on">Lumetri Color &#9776;</span><span>Effects</span></div>
            <p class="lu__master">Master &middot; <b class="lu__clip">{e(first['title'])}</b></p>
            <p class="lu__sec"><span>&#8964;</span> Basic Correction <i class="lu__sw is-on"></i></p>
            <p class="lu__grp">Color</p>
            {lum("Temperature", "lu__temp", "0.0", 50, "lu__track--temp")}
            {lum("Tint", "", "0.0", 50, "lu__track--tint")}
            {lum("Saturation", "", "100.0", 50)}
            <p class="lu__grp">Light</p>
            {lum("Exposure", "lu__exp", "0.0", 50)}
            {lum("Contrast", "", "0.0", 50)}
            {lum("Highlights", "", "0.0", 50)}
            {lum("Shadows", "", "0.0", 50)}
            <p class="lu__sec"><span>&#8250;</span> Creative <i class="lu__sw is-on"></i></p>
            <p class="lu__sec"><span>&#8250;</span> Curves <i class="lu__sw is-on"></i></p>
            <p class="lu__sec"><span>&#8250;</span> Vignette <i class="lu__sw"></i></p>
          </section>
        </div>
        <div class="fc__bottom">
          <div class="fc__tools" aria-hidden="true"><i class="is-on">&#10148;</i><i>&#8677;</i><i>&#8597;</i><i>&#9634;</i><i>&#9998;</i><i>&#9995;</i><i>T</i></div>
          <section class="fc__panel timeline" aria-label="Timeline">
            <div class="fc__tabs"><span class="is-on">Timeline &#9776;</span></div>
            <div class="tl__head"><span class="monitor__tc2 tl__tc">00:00:00:00</span><span class="tl__btns" aria-hidden="true"><i>&#9635;</i><i>&#8746;</i><i>&#9644;</i><i>&#9636;</i><i>&#9873;</i><i>&#9874;</i></span></div>
            <div class="timeline__body">
              <div class="timeline__heads" aria-hidden="true">
                <span class="th th--ruler"></span>
                <span class="th"><i>&#128274;</i><b class="th__p">V3</b><i>&#9711;</i><u>Titles</u></span>
                <span class="th"><i>&#128274;</i><b class="th__p">V2</b><i>&#9711;</i><u>B-roll</u></span>
                <span class="th"><i>&#128274;</i><b class="th__src">V1</b><b class="th__p">V1</b><i>&#9711;</i><u>Picture</u></span>
                <span class="th"><i>&#128274;</i><b class="th__src">A1</b><b class="th__p">A1</b><i>M</i><i>S</i><u>Nat sound</u></span>
              </div>
              <div class="timeline__window">
                <div class="timeline__strip">
                  <div class="ruler" aria-hidden="true"></div>
                  <div class="fxlane" aria-hidden="true"></div>
                  <nav class="track" aria-label="Every film, oldest first">
{chr(10).join(clips)}
                  </nav>
                </div>
                <span class="playhead" aria-hidden="true"></span>
              </div>
            </div>
          </section>
          <section class="fc__panel fc__meter" aria-hidden="true">
            <div class="mt__scale"><i>0</i><i>-6</i><i>-12</i><i>-18</i><i>-24</i><i>-30</i><i>-36</i><i>-42</i><i>-48</i><i>-54</i></div>
            <div class="meters"><i></i><i></i></div>
            <div class="mt__lufs"><span>M</span><b>-14.8 LUFS</b><span>S</span><b>-16.2 LUFS</b><span>I</span><b class="is-hot">-15.7 LUFS</b><span>TP</span><b class="is-red">-1.2 dBTP</b></div>
          </section>
        </div>
      </div>
    </div>"""


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
    titles = "".join(f'<li><a href="/films/{f["slug"]}/">{e(f["title"])}</a></li>' for f in films)
    people = "".join(f"<li>{e(n)}</li>" for n in names)
    pair = lambda r, n: f'<div class="roll__pair"><dt>{r}</dt><dd>{n}</dd></div>'
    return f"""  <div class="roll"><audio class="roll__song" src="/media/music/where-is-my-mind.mp3" preload="none"></audio>
    <p class="roll__pre">A Parker Manley picture</p>
    <dl class="roll__pairs">
      {pair("Directed by", "Parker Manley")}
      {pair("Director of Photography", "Parker Manley")}
      {pair("Edited by", "Parker Manley")}
    </dl>
    <h3 class="roll__h">With</h3>
    <ul class="roll__cols roll__cols--names">{people}</ul>
    <dl class="roll__pairs">
      {pair("Special thanks", "Jesus Christ")}
      {pair("Reel music", "&ldquo;I Am Chemistry&rdquo; by Yeasayer")}
      {pair("Outro music", "&ldquo;Where Is My Mind?&rdquo; by Pixies")}
      {pair("Filmed in", "Boulder, Colorado<br>Los Angeles, California")}
    </dl>
  </div>
"""


M_ICON = (
    '<svg class="mfx-m" viewBox="0 0 100 100" aria-hidden="true">'
    '<defs><linearGradient id="mfx-shade" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#b1060f"/><stop offset="0.55" stop-color="#b1060f"/>'
    '<stop offset="1" stop-color="#5e0207"/></linearGradient></defs>'
    '<path d="M16 6h15v88l-15 3z" fill="url(#mfx-shade)"/>'
    '<path d="M69 6h15v91l-15-3z" fill="url(#mfx-shade)"/>'
    '<path d="M16 6h15l26 66h-15z" fill="#e50914"/>'
    '<path d="M84 6h-15l-26 66h15z" fill="#e50914"/>'
    "</svg>"
)


def tv_rows(films):
    """ManleyFlix rows. Every film once in Top 10 or a genre shelf; a film
    can sit on two shelves the way Netflix shelves overlap."""
    top = [f for f in films if f["featured"]][:10]
    usc = [f for f in films if f["made_for"] and ("USC" in f["made_for"] or "Trojan" in f["made_for"])]
    scary = [f for f in films if any(k in f["genre"] for k in ("Horror", "Thriller"))]
    funny = [f for f in films if "Comedy" in f["genre"]]
    drama = [f for f in films if any(k in f["genre"] for k in ("Drama", "Romance", "Coming of Age")) and f not in scary]
    early = sorted([f for f in films if (f["year"] or 0) <= 2024], key=lambda f: f["year"] or 0)
    placed = {f["slug"] for row in (top, usc, scary, funny, drama, early) for f in row}
    mv = [f for f in films if f["genre"] == "Music Video"]
    more = mv + [f for f in films if f["slug"] not in placed and f not in mv]
    rows = [
        ("Made at USC", usc),
        ("Horror &amp; Thrillers", scary),
        ("Comedies", funny),
        ("Dramas", drama),
        ("Music Videos, Game Shows &amp; More", more),
        ("Where It Started", early),
    ]
    return top, [(t, r) for t, r in rows if r]


def tv_tile(f):
    meta = " &middot; ".join(e(x) for x in [str(f.get("year") or ""), f["genre"], f"{f['minutes']} min" if f.get("minutes") else ""] if x)
    return (
        f'<a class="mfx-tile" href="/films/{f["slug"]}/">'
        f'<span class="mfx-tile__img"><img src="/media/posters/{f["slug"]}.jpg" alt="" loading="lazy">'
        f'{M_ICON}<span class="mfx-tile__name">{e(f["title"])}</span></span>'
        f'<span class="mfx-tile__card"><span class="mfx-tile__play" aria-hidden="true">&#9654;</span>'
        f'<span class="mfx-tile__meta">{meta}</span><span class="mfx-tile__syn">{e(f["synopsis"])}</span></span>'
        "</a>"
    )


def tv(films):
    """The last room before the contact card: Parker's Apple TV, with two
    apps. ManleyFlix holds every film; Aerials plays his photographs the way
    the TV plays its screensaver."""
    top, rows = tv_rows(films)
    bill = next((f for f in films if f["slug"] == "scar-tissue"), films[0])
    photos_json = ROOT / "media/photos/photos.json"
    photos = json.loads(photos_json.read_text()) if photos_json.exists() else []
    photo_list = json.dumps([p["file"] for p in photos])
    shelf_photo = photos[57]["file"] if len(photos) > 57 else (photos[0]["file"] if photos else "")
    top10 = "".join(
        f'<a class="mfx-top" href="/films/{f["slug"]}/"><span class="mfx-top__n" aria-hidden="true">{i + 1}</span>'
        f'<span class="mfx-top__img"><img src="{art_src(f)}" alt="" loading="lazy"></span>'
        f'<span class="sr-only">{e(f["title"])}</span></a>'
        for i, f in enumerate(top)
    )
    shelves = "".join(
        f'<section class="mfx-row" aria-label="{t}"><h3 class="mfx-row__h">{t}</h3>'
        f'<div class="mfx-row__track">{"".join(tv_tile(f) for f in r)}</div></section>'
        for t, r in rows
    )
    loop = f'/media/loops/{bill["slug"]}.mp4'
    return f"""
<section class="tv" aria-label="Parker's Apple TV">
  <div class="tv__set">
    <div class="tv__screen">
      <div class="tvos" data-focus="mfx">
        <div class="tvos__shelf tvos__shelf--mfx" aria-hidden="true"><img src="/media/posters/{bill['slug']}.jpg" alt=""></div>
        <div class="tvos__shelf tvos__shelf--aer" aria-hidden="true"><img src="/media/photos/{shelf_photo}" alt=""></div>
        <div class="tvos__dock">
          <button type="button" class="tvos__app tvos__app--mfx" data-app="mfx" aria-label="Open ManleyFlix, every film">
            <span class="tvos__icon">{M_ICON}<i class="tvos__gloss"></i></span><span class="tvos__label">ManleyFlix</span>
          </button>
          <button type="button" class="tvos__app tvos__app--aer" data-app="aer" aria-label="Open Aerials, Parker's photographs">
            <span class="tvos__icon"><img src="/media/photos/thumb/{shelf_photo}" alt=""><b>Aerials</b><i class="tvos__gloss"></i></span><span class="tvos__label">Aerials</span>
          </button>
        </div>
      </div>
    </div>
  </div>
  <div class="mfx" hidden aria-label="ManleyFlix">
    <header class="mfx__bar"><button type="button" class="mfx__back" aria-label="Back to the TV">&#8249;</button>
      <span class="mfx__word" aria-label="ManleyFlix">MANLEYFLIX</span></header>
    <div class="mfx__bill">
      <video class="mfx__bill-v" muted loop playsinline preload="none" poster="/media/posters/{bill['slug']}.jpg" data-src="{loop}"></video>
      <div class="mfx__bill-copy">
        <p class="mfx__kind">{M_ICON}<span>Film</span></p>
        <h2 class="mfx__bill-t">{e(bill['title'])}</h2>
        <p class="mfx__bill-s">{e(bill['synopsis'])}</p>
        <p class="mfx__btns"><a class="mfx__play" href="/films/{bill['slug']}/">&#9654;&nbsp; Play</a></p>
      </div>
    </div>
    <section class="mfx-row mfx-row--top" aria-label="Top 10 on ManleyFlix today"><h3 class="mfx-row__h">Top 10 on ManleyFlix Today</h3>
      <div class="mfx-row__track">{top10}</div></section>
    {shelves}
  </div>
  <div class="aer" hidden aria-label="Aerials, photographs by Parker Manley" data-photos='{photo_list}'>
    <img class="aer__a" alt=""><img class="aer__b" alt="">
    <p class="aer__cap">Photographed by Parker Manley</p>
    <p class="aer__hint">Click to go back</p>
  </div>
</section>
"""


FLIGHT_BEATS = [
    ("falling", "Dawn over east Boulder, the Flatirons ahead", "2023, Boulder. Falling and Moments From My Life, made for his Film Studies class, and Keeping Up With the Olympians."),
    ("somnambulist", "Over the First Flatiron, rising past Green Mountain", "2024. Somnambulist, selected by the Colorado High School Film Festival and Rising Stars Colorado."),
    ("beneath-the-surface", "Climbing west over the Continental Divide", "2024. Beneath the Surface, the film that got him into the USC School of Cinematic Arts."),
    ("mad", "High over the red rock of the Colorado Plateau at noon", "2024. Mad, the film that got him into Loyola Marymount's Film Production program."),
    ("abundance", "Across the Mojave, down over the San Gabriels at sunset", "2025, Los Angeles. Abundance, selected for Indie Film LA."),
    ("scar-tissue", "Mulholland at dusk, Parker on the ridge, the basin lit", "2026, USC. Scar Tissue, Reflect and As We Are, You Shall Be, his shorts for USC production classes."),
]


def preview(home_html):
    """/preview/: the whole planned site with the props agent's low-sample
    draft renders standing in, so the layout can be judged before the real
    renders run. Every stand-in wears a DRAFT tag."""
    h = home_html.replace('<body class="is-home"', '<body class="is-home is-preview"', 1)
    h = h.replace("<title>", '<meta name="robots" content="noindex"><title>DRAFT · ', 1)
    # Director: the premiere hall, the film playing on its screen.
    h = h.replace('<div class="scene__pin">\n      <div class="scene__bg"',
                  '<div class="scene__pin">\n      <img class="draft-hall" src="/media/draft/premiere.webp" alt=""><span class="draft-tag">Premiere hall, draft render</span>\n      <div class="scene__bg"', 1)
    # Cinematographer: the real monitor body around the live feed.
    h = h.replace('<div class="cam__screen">',
                  '<div class="cam__screen"><img class="draft-mon" src="/media/draft/monitor.webp" alt=""><span class="draft-tag">Monitor, draft render</span>', 1)
    # About: the knolled kit after the call sheet, then the flight.
    beats = "".join(
        f'<li class="fl__beat"><img src="/media/stills/{s}-1.jpg" alt="" loading="lazy"><p class="fl__where">{w}</p><p class="fl__cap">{e(c)}</p></li>'
        for s, w, c in FLIGHT_BEATS
    )
    after_about = (
        '<figure class="draft-frame"><img src="/media/draft/knolling.webp" alt="Parker\'s kit laid out on a desk" loading="lazy">'
        '<span class="draft-tag">Knolling, draft render</span></figure>'
    )
    i = h.index('<section class="flight-todo"')
    h = h[:i] + after_about + h[i:]
    h = h.replace('<div class="slate draft-slate">', '<div class="slate draft-slate"><span class="draft-tag">Slate, draft render</span>', 1)
    return h


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
            "laurels": f["festivals"],
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
        + (f'<p class="card__laurels">' + "".join(f'<span>{LAUREL}{e(x)}{LAUREL}</span>' for x in s["laurels"]) + '</p>' if s["laurels"] else (f'<p class="card__fest">{e(s["festivals"])}</p>' if s["festivals"] else ""))
        + f'<a class="btn btn--ticket" href="{s["href"]}"{"" if i == 0 else " tabindex=\"-1\""}>Watch the film</a></div>'
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
<div class="leader" role="dialog" aria-label="Opening countdown">
  <span class="leader__sprockets leader__sprockets--l" aria-hidden="true"></span><span class="leader__sprockets leader__sprockets--r" aria-hidden="true"></span>
  <canvas class="leader__dirt" aria-hidden="true"></canvas>
  <svg class="leader__dial" viewBox="0 0 200 200">
    <circle cx="100" cy="100" r="92"/><circle cx="100" cy="100" r="74"/>
    <path d="M100 0V200M0 100H200"/>
  </svg>
  <span class="leader__sweep"></span>
  <span class="leader__n">3</span>
  <div class="leader__gate">
    <button class="admit leader__roll" type="button" aria-label="Admit one: tear the ticket to roll the film, with sound">
      <img class="admit__main" src="/media/titles/ticket-main.webp" alt="">
      <img class="admit__stub" src="/media/titles/ticket-stub.webp" alt="">
    </button>
    <p class="leader__sound">Sound on &middot; scroll to skip</p>
  </div>
</div>
<div class="opening">
  <span class="cue" aria-hidden="true"></span>
  <div class="opening__pin">
    <div class="opening__frame">
      <video id="reel" autoplay muted loop playsinline preload="auto" poster="/media/reel/reel-poster.jpg"
        data-src="/media/reel/reel.mp4" data-src-small="/media/reel/reel-720.mp4" aria-label="Parker Manley reel"></video>
    </div>
    <div class="titlecard">
      <h1 class="sr">A picture by Parker Manley, director, cinematographer, editor</h1>
      <img class="titlecard__img" src="/media/titles/titlecard-900.webp" srcset="/media/titles/titlecard-900.webp 900w, /media/titles/titlecard.webp 1800w" sizes="(max-width: 700px) 92vw, 760px" alt="">
    </div>
    <button class="sound" type="button" aria-pressed="false"><svg class="sun" viewBox="0 0 24 24" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.6M12 18.9v2.6M2.5 12h2.6M18.9 12h2.6M5.3 5.3l1.8 1.8M16.9 16.9l1.8 1.8M5.3 18.7l1.8-1.8M16.9 7.1l1.8-1.8"/></g></svg><span class="label">Sound off</span></button>
  </div>
</div>

<section class="about" id="about" aria-label="About Parker">
  <div class="callsheet-wrap">
    <article class="callsheet">
      <header class="cs__head">
        <div><p class="cs__label">Production</p><p class="cs__val">Parker Manley</p></div>
        <h2 class="cs__title">Call Sheet</h2>
        <div class="cs__right"><p class="cs__label">Base camp</p><p class="cs__val">Boulder, Colorado</p></div>
      </header>
      <div class="cs__strip">
        <div><p class="cs__label">Crew</p><p>Director &middot; Cinematographer &middot; Editor</p></div>
        <div><p class="cs__label">School</p><p>USC, Film &amp; Television Production</p></div>
        <div><p class="cs__label">Shorts since 2023</p><p>25+</p></div>
      </div>
      <table class="cs__sched">
        <thead><tr><th>Sc.</th><th>Set / Description</th><th>Location</th></tr></thead>
        <tbody>
          <tr><td class="cs__sc">1</td><td><b>Storytelling.</b> I'm a storyteller from Boulder, Colorado, studying Film and Television Production at USC. On set or at the Dungeons &amp; Dragons table. Most of my shorts I wrote, directed, shot and edited myself.</td><td class="cs__loc">INT. Set / D&amp;D table</td></tr>
          <tr><td class="cs__sc">2</td><td><b>Outdoors.</b> I'm a big hiker and camper. I grew up at the foot of the Rockies. At USC: SC Outfitters, fencing, the Trojan Stunt Team and EscapeSC.</td><td class="cs__loc">EXT. Rocky Mountains</td></tr>
          <tr><td class="cs__sc">3</td><td><b>Faith.</b> I lay all my work before Jesus. &ldquo;So, whether you eat or drink, or whatever you do, do all to the glory of God.&rdquo; 1 Corinthians 10:31</td><td class="cs__loc">Every location</td></tr>
        </tbody>
      </table>
    </article>
    <div class="polaroids">
      <figure class="polaroid"><img src="/media/portraits/set.jpg" alt="Parker behind a Sony cinema camera on set" loading="lazy"><figcaption>Sc. 1 &middot; on set</figcaption></figure>
      <figure class="polaroid"><img src="/media/portraits/bigbear.jpg" alt="Parker outdoors" loading="lazy"><figcaption>Sc. 2 &middot; outdoors</figcaption></figure>
      <figure class="polaroid"><img src="/media/portraits/faith.jpg" alt="A crucifix against a castle tower" loading="lazy"><figcaption>Sc. 3 &middot; faith</figcaption></figure>
    </div>
  </div>
</section>

<section class="flight-todo" aria-label="Boulder to Los Angeles, coming soon">
  <div class="flight-todo__card">
    <p class="ft__h">Boulder &rarr; Los Angeles</p>
    <p class="ft__what">One unbroken flight from where Parker started filming to where he is now, his films along the way. Coming soon.</p>
    <p class="ft__ask">Parker, for this part:</p>
    <ol class="ft__qs">
      <li>What made you start filming in Boulder?</li>
      <li>One real moment from high school in Boulder</li>
      <li>One from the summer you made Somnambulist</li>
      <li>One from getting into USC</li>
      <li>One from your first semester in LA</li>
    </ol>
  </div>
</section>
<section class="reels" id="films" aria-label="Featured films">
  <div class="scene scene--films">
    <div class="scene__pin">
      <div class="scene__bg" aria-hidden="true">
{layers}
      </div>
      <div class="marquee" aria-hidden="true">
        <img class="marquee__img" src="/media/titles/marquee-{featured[0]["slug"]}-900.webp" alt="" data-slugs="{" ".join(f["slug"] for f in featured)}">
      </div>
      <div class="scene__copy">
{cards}
      </div>
      <div class="scene__ticks" aria-hidden="true">{ticks}</div>
    </div>
  </div>
</section>
{lens_scene(films)}
<section class="reels" aria-label="Every film">
  <div class="lobby" id="all-films">
{program}
  </div>
</section>

{tv(films)}
<section class="contact" id="contact" aria-labelledby="contact-h">
  <div class="irisout">
    <div class="irisout__pin">
      <img class="irisout__img" src="/media/portraits/rock.jpg" alt="Parker framing a shot on a granite outcrop above a pine forest" loading="lazy">
      <div class="irisout__mask" aria-hidden="true"></div>
      <img class="end__green" src="/media/props/end/greenscreen.webp" alt="" aria-hidden="true">
      <img class="end__parker" src="/media/props/end/parker-fg.webp" alt="" aria-hidden="true">
      <div class="irisout__card">
        <h2 id="contact-h" class="sr-only">Your film</h2>
  <div class="slate draft-slate">
          <form class="form slate__board" action="https://formsubmit.co/ajax/{EMAIL}" method="POST" novalidate>
            <input type="hidden" name="_subject" value="New message from parkermanley.com">
            <input type="hidden" name="_template" value="table">
            <div class="hp" aria-hidden="true"><input type="text" name="_honey" tabindex="-1" autocomplete="off"></div>
            <label class="sl-prod">Your film<input name="message" autocomplete="off" placeholder="Your film" required></label>
            <label class="sl-dir">Your name<input name="name" autocomplete="name" placeholder="Your name" required></label>
            <label class="sl-cam">Your email<input name="email" type="email" autocomplete="email" placeholder="Your email" required></label>
            <button class="btn btn--ember" type="submit">Send</button>
            <p class="form__status" role="status"></p>
          </form>
        </div>
        <p class="end__links"><a href="mailto:{EMAIL}">{EMAIL}</a><a href="{YOUTUBE}" rel="noopener">YouTube</a><a href="{INSTAGRAM}" rel="noopener">Instagram</a></p>
      </div>
    </div>
  </div>
{end_credits(films)}
</section>
"""
    body += screenings(films)
    return page("Parker Manley, Director, Cinematographer, Editor", body, current="", path="/", image="/media/reel/reel-poster.jpg")


def screening(f, standalone=False):
    """One film, shown the way a theater shows it: the room goes dark, the
    screen comes up, the credits sit under it. The home page clones these
    in place; /films/<slug>/ renders the same thing for shared links."""
    credits = [(f["role"] or "Written, directed, shot & edited by", "Parker Manley")]
    credits += [(r, n) for r, n in f["crew"]]
    if f["cast"]:
        credits.append(("Starring", "<br>".join(e(n) for n in f["cast"])))
    if f["music"]:
        credits.append(("Music", "<br>".join(e(n) for n in f["music"])))
    pairs = "".join(
        f'<div class="roll__pair"><dt>{e(r)}</dt><dd>{n if r in ("Starring", "Music") else e(n)}</dd></div>'
        for r, n in credits
    )
    fest = ""
    if f["festivals"]:
        fest = '<p class="scr__fest">' + " &middot; ".join(e(x) for x in f["festivals"]) + "</p>"
    src = (f'data-yt="{f["youtube"]}"' if f.get("youtube") else f'data-drive="{f.get("drive", "")}"')
    up = ('<a class="scr__up" href="/">Lights up</a>' if standalone
          else '<button type="button" class="scr__up">Lights up</button>')
    return f"""<div class="scr" role="dialog" aria-modal="true" aria-labelledby="scr-{f['slug']}" data-slug="{f['slug']}">
  {up}
  <div class="scr__screen" {src}>
    <img src="/media/posters/{f['slug']}.jpg" alt="">
    <button type="button" class="scr__play" aria-label="Play {e(f['title'])}"><span>&#9654;</span></button>
  </div>
  <div class="scr__under">
    <p class="scr__meta">{e(meta_line(f))}</p>
    <h2 class="scr__title" id="scr-{f['slug']}">{e(f['title'])}</h2>
    <p class="scr__syn">{e(f['synopsis'])}</p>
    {fest}
    <dl class="roll__pairs scr__credits">{pairs}</dl>
  </div>
</div>"""


def screenings(films):
    return "".join(f'<template id="t-{f["slug"]}">{screening(f)}</template>' for f in films)


def film_page(films, i):
    f = films[i]
    body = f"""<article class="film-page">{screening(f, standalone=True)}</article>"""
    return page(
        f"{f['title']}, a film by Parker Manley",
        body,
        current="films",
        description=f["synopsis"],
        image=f"/media/posters/{f['slug']}.jpg",
        path=f"/films/{f['slug']}/",
    )


def photography():
    data = ROOT / "media/photos/photos.json"
    photos = json.loads(data.read_text()) if data.exists() else []
    shots = "\n".join(
        f'<button type="button" data-full="/media/photos/{p["file"]}" aria-label="Open photo {i + 1} of {len(photos)}">'
        f'<img src="/media/photos/thumb/{p["file"]}" width="{p["w"]}" height="{p["h"]}" alt="Photograph by Parker Manley" loading="lazy">'
        f'<span class="edge">&#9656; {i + 1}A</span></button>'
        for i, p in enumerate(photos)
    )
    n = len(photos)
    body = f"""
<div class="photos" data-view="table">
  <section class="lighttable" aria-label="Photographs on a light table">
    <div class="lighttable__pin">
      <div class="lighttable__head">
        <p class="card__no">{n} slides on the light table</p>
        <h1 class="lighttable__h">Photography</h1>
        <p class="lighttable__sub">Light painting, ice, mountains and the people in front of my camera. Tap a slide to project it.</p>
      </div>
      <div class="lighttable__surface sheet">
{shots}
      </div>
      <div class="loupe" aria-hidden="true"><div class="loupe__view"></div></div>
    </div>
  </section>
  <section class="room" aria-roledescription="carousel" aria-label="Photographs by Parker Manley, one slide at a time">
    <div class="room__beam" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i></div>
    <div class="wall">
      <div class="wall__title">
        <p class="card__no">{n} slides</p>
        <h1 class="wall__h">Photography</h1>
        <p class="wall__sub">Light painting, ice, mountains and the people in front of my camera.</p>
        <p class="wall__hint">Click, swipe or press &rarr; to advance</p>
      </div>
      <img class="wall__img" alt="">
      <p class="wall__no" aria-live="polite"></p>
      <button class="wall__hit wall__hit--pv" type="button" aria-label="Previous slide"></button>
      <button class="wall__hit wall__hit--nx" type="button" aria-label="Next slide"></button>
    </div>
    <div class="machine">
      <button class="machine__btn" type="button" data-step="-1" aria-label="Previous slide">&#9664;</button>
      <div class="tray" role="slider" tabindex="0" aria-label="Carousel tray" aria-valuemin="0" aria-valuemax="{n}" aria-valuenow="0">
        <svg viewBox="0 0 120 120" aria-hidden="true"><circle class="tray__rim" cx="60" cy="60" r="56"/><circle class="tray__hub" cx="60" cy="60" r="16"/><g class="tray__slots"></g></svg>
        <span class="tray__count">Title</span>
      </div>
      <button class="machine__btn" type="button" data-step="1" aria-label="Next slide">&#9654;</button>
      <span class="machine__body" aria-hidden="true"><span class="machine__lens"></span></span>
    </div>
    <button class="room__sheet" type="button" data-view="table">Back to the light table</button>
  </section>
</div>
"""
    return page("Photography, Parker Manley", body, current="photos", path="/photography/")


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="6" fill="#12110e"/><rect x="5" y="11" width="22" height="10" fill="#d07a45"/></svg>"""

def main():
    films = json.loads((ROOT / "data/films.json").read_text())["films"]
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    home_html = home(films)
    (DIST / "index.html").write_text(home_html)
    (DIST / "preview").mkdir(exist_ok=True)
    (DIST / "preview/index.html").write_text(preview(home_html))
    for i, f in enumerate(films):
        out = DIST / "films" / f["slug"]
        out.mkdir(parents=True)
        (out / "index.html").write_text(film_page(films, i))
    (DIST / "404.html").write_text(page("Missing reel, Parker Manley", """
<section class="lost">
  <div class="lost__dial" aria-hidden="true"><span>?</span></div>
  <p class="card__no">Reel not found</p>
  <h1 class="lost__title">This reel never made it to the booth</h1>
  <p class="lost__sub">The page you were looking for isn't on the program.</p>
  <a class="btn btn--ticket" href="/">Back to the screening</a>
</section>
""", path="/404"))
    (DIST / "photography").mkdir()
    (DIST / "photography/index.html").write_text(photography())
    for name in ("styles.css", "app.js", "score.js", "topo.svg"):
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
