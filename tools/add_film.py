#!/usr/bin/env python3
"""Add a film to the site from its YouTube link, with no hand editing.

/usr/bin/python3 tools/add_film.py "https://youtu.be/ID" --role "Directed, shot & edited" \
    --genre Comedy --minutes 7 --synopsis "One line." --cast "A, B" --music "C" --made-for "USC CTPR 290"

It fills the title from YouTube, saves the poster (his file with --poster, else YouTube's
thumbnail), puts the film at --rank (1 is first, default 1) and builds the site. It only
changes data/films.json and the poster, and nothing goes live until someone pushes.

--role is required: a blank role tells the site he wrote, directed, shot and edited it,
which a dry run of Plagiarism or Prophecy nearly claimed on 2026-11-06.
"""
import argparse
import datetime
import json
import re
import subprocess
import sys
import urllib.parse
import urllib.request

FILMS = "data/films.json"


def video_id(link):
    m = re.search(r"(?:v=|youtu\.be/|/shorts/|/embed/|/live/)([\w-]{11})", link)
    if not m and re.fullmatch(r"[\w-]{11}", link):
        return link
    if not m:
        sys.exit(f"That doesn't look like a YouTube link: {link}")
    return m.group(1)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "parker-site"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def youtube_title(vid):
    q = urllib.parse.quote(f"https://youtu.be/{vid}", safe="")
    try:
        data = json.loads(fetch(f"https://www.youtube.com/oembed?url={q}&format=json"))
    except Exception as err:
        sys.exit(f"YouTube didn't return that video ({err}). Is it public or unlisted, and is the link right?")
    title = re.sub(r"\s*[\(\[][^)\]]*(short film|official|trailer)[^)\]]*[\)\]]\s*$", "", data["title"], flags=re.I)
    return title.strip()


def slugify(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def split(text):
    return [x.strip() for x in (text or "").split(",") if x.strip()]


def save_poster(path_out, vid, given):
    if given:
        subprocess.run(["sips", "-s", "format", "jpeg", given, "--out", path_out], check=True, capture_output=True)
        return "your file"
    for name in ("maxresdefault", "hqdefault"):
        try:
            data = fetch(f"https://img.youtube.com/vi/{vid}/{name}.jpg")
        except Exception:
            continue
        with open(path_out, "wb") as f:
            f.write(data)
        return "YouTube's thumbnail"
    sys.exit("Couldn't get a poster from YouTube. Pass one with --poster.")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("link")
    p.add_argument("--role", required=True, help='like "Directed, shot & edited"')
    p.add_argument("--title")
    p.add_argument("--year", type=int, default=datetime.date.today().year)
    p.add_argument("--genre", default="")
    p.add_argument("--minutes", type=int, default=0)
    p.add_argument("--synopsis", default="")
    p.add_argument("--cast", default="")
    p.add_argument("--crew", default="")
    p.add_argument("--music", default="")
    p.add_argument("--made-for", default="")
    p.add_argument("--festivals", default="")
    p.add_argument("--poster")
    p.add_argument("--rank", type=int, default=1)
    a = p.parse_args()
    if not a.role.strip():
        sys.exit("Say what his role was: a blank role means he wrote, directed, shot and edited it.")

    vid = video_id(a.link)
    with open(FILMS, encoding="utf-8") as f:
        raw = f.read()
    data = json.loads(raw)
    films = data["films"]
    for film in films:
        if film.get("youtube") == vid:
            sys.exit(f"That video is already on the site as {film['title']}.")
    title = a.title or youtube_title(vid)
    slug = slugify(title)
    if not slug or any(film["slug"] == slug for film in films):
        sys.exit(f"There's already a film called {title}. Pass a different --title.")

    poster = save_poster(f"media/posters/{slug}.jpg", vid, a.poster)
    entry = {
        "slug": slug, "title": title, "year": a.year, "genre": a.genre, "minutes": a.minutes,
        "youtube": vid, "featured": False, "synopsis": a.synopsis, "role": a.role,
        "cast": split(a.cast), "crew": split(a.crew), "made_for": a.made_for,
        "festivals": split(a.festivals), "music": split(a.music),
    }
    films.insert(max(a.rank - 1, 0), entry)
    with open(FILMS, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n" if raw.endswith("\n") else "")

    out = subprocess.run([sys.executable, "build.py"], capture_output=True, text=True)
    if out.returncode:
        sys.exit("The film went in, but the site didn't build:\n" + out.stderr[-800:])
    print(f"Added {title} at rank {a.rank}. Poster: {poster}.")
    print(f"Page: /films/{slug}/")
    missing = [x for x, v in (("genre", a.genre), ("length", a.minutes), ("synopsis", a.synopsis)) if not v]
    if missing:
        print("Still blank: " + ", ".join(missing))


if __name__ == "__main__":
    main()
