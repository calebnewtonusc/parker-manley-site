from pathlib import Path
import json
"""Item 9: the Mac desktop the edit bay leaves onto.

desk_section(films, photos) returns one <section class="desk">: a macOS
desktop with Parker's lake photo as the wallpaper, a menu bar, a Dock, and a
Chrome window holding three pages: the Manleygle new tab, ManleyFlix (the
same markup as the Apple TV app in build.tv) and ManleyGram, his photos as an
Instagram profile. src/desk.css styles it and src/desk.js drives it.
"""
from build import M_ICON, art_src, e, tv_rows, tv_tile

WALLPAPER = "58.jpg"  # mountain lake holding the sky in its reflection
USER = "parkermanley"
NAME = "Parker Manley"
BIO = "Director · Cinematographer · Editor. USC Film &amp; TV."


def _svg(path, cls="", vb="0 0 24 24", fill=True):
    paint = 'fill="currentColor"' if fill else 'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
    return f'<svg class="{cls}" viewBox="{vb}" aria-hidden="true"><path {paint} d="{path}"/></svg>'


# Material icons (Apache 2.0), the set Chrome's own toolbar is drawn from.
I_BACK = "M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"
I_FWD = "M12 4l-1.41 1.41L16.17 11H4v2h12.17l-5.58 5.59L12 20l8-8z"
I_RELOAD = "M17.65 6.35A7.96 7.96 0 0 0 12 4a8 8 0 1 0 7.73 10h-2.08A6 6 0 1 1 12 6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"
I_TUNE = "M3 17v2h6v-2H3zM3 5v2h10V5H3zm10 16v-2h8v-2h-8v-2h-2v6h2zM7 9v2H3v2h4v2h2V9H7zm14 4v-2H11v2h10zm-6-4h2V7h4V5h-4V3h-2v6z"
I_STAR = "M22 9.24l-7.19-.62L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21 12 17.27 18.18 21l-1.63-7.03L22 9.24zM12 15.4l-3.76 2.27 1-4.28-3.32-2.88 4.38-.38L12 6.1l1.71 4.04 4.38.38-3.32 2.88 1 4.28L12 15.4z"
I_PUZZLE = "M20.5 11H19V7a2 2 0 0 0-2-2h-4V3.5a2.5 2.5 0 0 0-5 0V5H4a2 2 0 0 0-1.99 2v3.8H3.5a2.7 2.7 0 0 1 0 5.4H2V20a2 2 0 0 0 2 2h3.8v-1.5a2.7 2.7 0 0 1 5.4 0V22H17a2 2 0 0 0 2-2v-4h1.5a2.5 2.5 0 0 0 0-5z"
I_MORE = "M12 8a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm0 2a2 2 0 1 0 0 4 2 2 0 0 0 0-4zm0 6a2 2 0 1 0 0 4 2 2 0 0 0 0-4z"
I_ADD = "M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"
I_CLOSE = "M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"
I_SEARCH = "M15.5 14h-.79l-.28-.27A6.47 6.47 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"
I_MIC = "M12 14a3 3 0 0 0 2.99-3L15 5a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.48 6-3.3 6-6.72h-1.7z"
I_LENS = "M12 9.2a2.8 2.8 0 1 0 0 5.6 2.8 2.8 0 0 0 0-5.6zM20 5h-3.17L15 3H9L7.17 5H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2zm-8 13a5 5 0 1 1 0-10 5 5 0 0 1 0 10z"
I_DOWN = "M16.59 8.59L12 13.17 7.41 8.59 6 10l6 6 6-6z"
I_APPS = "M6 8a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm6 0a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm6 0a2 2 0 1 0 0-4 2 2 0 0 0 0 4zM6 14a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm6 0a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm6 0a2 2 0 1 0 0-4 2 2 0 0 0 0 4zM6 20a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm6 0a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm6 0a2 2 0 1 0 0-4 2 2 0 0 0 0 4z"
I_CHEV_L = "M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"
I_CHEV_R = "M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"

APPLE = (
    '<svg class="mb__apple" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12.152 6.896c-.948 0-2.415-1.078-3.96-1.04-2.04.027-3.91 1.183-4.961 3.014-2.117 3.675-.546 9.103 1.519 12.09 1.013 1.454 2.208 3.09 3.792 3.039 1.52-.065 2.09-.987 3.935-.987 1.831 0 2.35.987 3.96.948 1.637-.026 2.676-1.48 3.676-2.948 1.156-1.688 1.636-3.325 1.662-3.415-.039-.013-3.182-1.221-3.22-4.857-.026-3.04 2.48-4.494 2.597-4.559-1.429-2.09-3.623-2.324-4.39-2.376-2-.156-3.675 1.09-4.61 1.09zM15.53 3.83c.843-1.012 1.4-2.427 1.245-3.83-1.207.052-2.662.805-3.532 1.818-.78.896-1.454 2.338-1.273 3.714 1.338.104 2.715-.688 3.559-1.701"/></svg>'
)

# Menu bar status items, drawn at the size macOS draws them.
BATTERY = (
    '<svg class="mb__bat" viewBox="0 0 28 13" aria-hidden="true">'
    '<rect x="0.75" y="0.75" width="23" height="11.5" rx="3.4" fill="none" stroke="currentColor" stroke-opacity="0.45" stroke-width="1.1"/>'
    '<rect x="2.4" y="2.4" width="16.2" height="8.2" rx="1.9" fill="currentColor"/>'
    '<path d="M25.4 4.4v4.2c.9-.3 1.5-1.1 1.5-2.1s-.6-1.8-1.5-2.1z" fill="currentColor" fill-opacity="0.45"/></svg>'
)
WIFI = (
    '<svg class="mb__wifi" viewBox="0 0 20 15" aria-hidden="true"><g fill="currentColor">'
    '<path d="M10 2.2c3 0 5.8 1.2 7.8 3.2l1.3-1.3A12.8 12.8 0 0 0 10 .4 12.8 12.8 0 0 0 .9 4.1l1.3 1.3a11 11 0 0 1 7.8-3.2z"/>'
    '<path d="M10 6c2 0 3.8.8 5.1 2.1l1.3-1.3A9 9 0 0 0 10 4.2a9 9 0 0 0-6.4 2.6l1.3 1.3A7.2 7.2 0 0 1 10 6z"/>'
    '<path d="M10 9.8c1 0 1.9.4 2.5 1L10 13.4l-2.5-2.6c.6-.6 1.5-1 2.5-1z"/></g></svg>'
)
CONTROL = (
    '<svg class="mb__cc" viewBox="0 0 18 14" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="1.3">'
    '<rect x="0.9" y="0.9" width="16.2" height="5" rx="2.5"/><rect x="0.9" y="8.1" width="16.2" height="5" rx="2.5"/></g>'
    '<circle cx="13.6" cy="3.4" r="1.6" fill="currentColor"/><circle cx="4.4" cy="10.6" r="1.6" fill="currentColor"/></svg>'
)

# Dock icons. macOS squircle tiles; each glyph is drawn, not borrowed.
SQUIRCLE = "M50 0C14 0 0 14 0 50s14 50 50 50 50-14 50-50S86 0 50 0z"
SQ = "M22 0h56c12.2 0 22 9.8 22 22v56c0 12.2-9.8 22-22 22H22C9.8 100 0 90.2 0 78V22C0 9.8 9.8 0 22 0z"

DOCK_FINDER = (
    '<svg viewBox="0 0 100 100" aria-hidden="true"><defs>'
    '<linearGradient id="dk-f1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4ec0fb"/><stop offset="1" stop-color="#1a6ff0"/></linearGradient>'
    '<linearGradient id="dk-f2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f4fafe"/><stop offset="1" stop-color="#cfe3f5"/></linearGradient>'
    f'<clipPath id="dk-fc"><path d="{SQ}"/></clipPath></defs>'
    '<g clip-path="url(#dk-fc)"><rect width="100" height="100" fill="url(#dk-f2)"/>'
    '<path d="M0 0h55c-6 14-9 27-9 41 0 4 .3 7 .9 9H38c-.4 8 .3 17 2.6 26 2.3 9 5.4 17 9.4 24H0z" fill="url(#dk-f1)"/></g>'
    '<g fill="#1d2b3a"><rect x="27" y="27" width="5.4" height="15" rx="2.7"/><rect x="67" y="27" width="5.4" height="15" rx="2.7"/></g>'
    '<path d="M24 66c16 9 36 9 52 0" fill="none" stroke="#1d2b3a" stroke-width="3.6" stroke-linecap="round"/></svg>'
)
DOCK_MESSAGES = (
    '<svg viewBox="0 0 100 100" aria-hidden="true"><defs><linearGradient id="dk-m" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#6cf37a"/><stop offset="1" stop-color="#0dbd2c"/></linearGradient></defs>'
    f'<path d="{SQ}" fill="url(#dk-m)"/>'
    '<path d="M50 22c-19.3 0-35 12.4-35 27.7 0 8.9 5.3 16.8 13.6 21.9-.6 4.4-2.7 8.4-6 11.4 6.5.3 12.5-1.8 17.1-5.5 3.3.8 6.8 1.2 10.3 1.2 19.3 0 35-12.4 35-27.7S69.3 22 50 22z" fill="#fff"/></svg>'
)
DOCK_PHOTOS = (
    f'<svg viewBox="0 0 100 100" aria-hidden="true"><path d="{SQ}" fill="#fff"/><g transform="translate(50 50)" style="mix-blend-mode:multiply">'
    + "".join(
        f'<ellipse cx="0" cy="-17" rx="9.5" ry="17" fill="{c}" fill-opacity="0.82" transform="rotate({i * 45})"/>'
        for i, c in enumerate(["#f8b51c", "#f58a1f", "#ee3e3a", "#c43f8f", "#7656a4", "#2f86d1", "#38b4c4", "#79c043"])
    )
    + "</g></svg>"
)
DOCK_CHROME = (
    '<svg viewBox="0 0 48 48" aria-hidden="true"><defs><path id="dk-cr" d="M24 14H41.32A20 20 0 0 0 6.68 14L15.34 29A10 10 0 0 1 24 14z"/></defs>'
    '<circle cx="24" cy="24" r="20" fill="#fff"/>'
    '<use href="#dk-cr" fill="#ea4335"/><use href="#dk-cr" fill="#fbbc04" transform="rotate(120 24 24)"/>'
    '<use href="#dk-cr" fill="#34a853" transform="rotate(240 24 24)"/>'
    '<circle cx="24" cy="24" r="8" fill="#1a73e8"/></svg>'
)
DOCK_CUT = (
    '<svg viewBox="0 0 100 100" aria-hidden="true"><defs><linearGradient id="dk-c" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#2a2340"/><stop offset="1" stop-color="#120e1f"/></linearGradient></defs>'
    f'<path d="{SQ}" fill="url(#dk-c)"/>'
    '<g fill="none" stroke="#c9b6ff" stroke-width="3.2" stroke-linecap="round">'
    '<rect x="22" y="40" width="56" height="34" rx="3"/><path d="M22 40l8-14 52 0-6 14"/><path d="M40 26l-6 14M58 26l-6 14"/></g>'
    '<path d="M44 50v14l12-7z" fill="#c9b6ff"/></svg>'
)
DOCK_CREDITS = (
    '<svg viewBox="0 0 100 100" aria-hidden="true"><defs><linearGradient id="dk-r" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#2b2b2e"/><stop offset="1" stop-color="#0e0e10"/></linearGradient></defs>'
    f'<path d="{SQ}" fill="url(#dk-r)"/>'
    '<circle cx="42" cy="44" r="24" fill="#c9c3b6"/><circle cx="42" cy="44" r="5" fill="#1a1a1c"/>'
    '<g fill="#1a1a1c"><circle cx="42" cy="30" r="6.5"/><circle cx="55.3" cy="39.7" r="6.5"/><circle cx="50.2" cy="55.3" r="6.5"/>'
    '<circle cx="33.8" cy="55.3" r="6.5"/><circle cx="28.7" cy="39.7" r="6.5"/></g>'
    '<path d="M42 68c10 0 22 2 34 10" fill="none" stroke="#c9c3b6" stroke-width="7" stroke-linecap="round"/>'
    '<path d="M44 66l2 5M54 67l1 5M64 70l-1 5" stroke="#1a1a1c" stroke-width="1.6"/></svg>'
)
DOCK_TRASH = (
    '<svg viewBox="0 0 100 100" aria-hidden="true"><defs><linearGradient id="dk-t" x1="0" y1="0" x2="1" y2="0">'
    '<stop offset="0" stop-color="#d6dadf"/><stop offset="0.5" stop-color="#f4f6f8"/><stop offset="1" stop-color="#c6cbd1"/></linearGradient></defs>'
    '<path d="M20 22h60l-6 70c-.3 3-2.8 5-5.8 5H31.8c-3 0-5.5-2-5.8-5z" fill="url(#dk-t)" fill-opacity="0.92" stroke="#9aa1a9" stroke-width="1"/>'
    '<ellipse cx="50" cy="22" rx="30" ry="5.5" fill="#e8ebee" stroke="#9aa1a9" stroke-width="1"/>'
    '<g stroke="#a8afb7" stroke-width="1.4" fill="none">'
    + "".join(f'<path d="M{x} 30 L{x + (x - 50) * -0.08:.1f} 90"/>' for x in (30, 37, 44, 50, 56, 63, 70))
    + "</g></svg>"
)

IG_GLYPH = (
    '<svg class="ig-glyph" viewBox="0 0 24 24" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="2">'
    '<rect x="2.5" y="2.5" width="19" height="19" rx="5.5"/><circle cx="12" cy="12" r="4.4"/></g>'
    '<circle cx="17.6" cy="6.4" r="1.25" fill="currentColor"/></svg>'
)
GRAM_FAV = (
    '<svg class="fav-gram" viewBox="0 0 24 24" aria-hidden="true"><defs>'
    '<radialGradient id="ig-fav" cx="0.3" cy="1.05" r="1.25"><stop offset="0" stop-color="#fdd56b"/><stop offset="0.12" stop-color="#fdd56b"/>'
    '<stop offset="0.45" stop-color="#f2463d"/><stop offset="0.7" stop-color="#d4237f"/><stop offset="1" stop-color="#6a3dd8"/></radialGradient></defs>'
    '<rect x="1" y="1" width="22" height="22" rx="6.2" fill="url(#ig-fav)"/>'
    '<g fill="none" stroke="#fff" stroke-width="1.8"><rect x="5.2" y="5.2" width="13.6" height="13.6" rx="4"/><circle cx="12" cy="12" r="3.2"/></g>'
    '<circle cx="16.1" cy="7.9" r="0.95" fill="#fff"/></svg>'
)

# Instagram's outline icon set, redrawn.
IGI = {
    "home": '<path d="M9.005 16.545a2.997 2.997 0 0 1 2.997-2.997A2.997 2.997 0 0 1 15 16.545V22h7V11.543L12 2 2 11.543V22h7.005z"/>',
    "search": '<path d="M19 10.5A8.5 8.5 0 1 1 10.5 2a8.5 8.5 0 0 1 8.5 8.5z"/><path d="M16.511 16.511 22 22"/>',
    "explore": '<polygon points="13.941 13.953 7.581 16.424 10.06 10.056 16.42 7.585 13.941 13.953"/><polygon points="10.06 10.056 13.949 13.945 7.581 16.424 10.06 10.056" fill="currentColor"/><circle cx="12.001" cy="12.005" r="10.5"/>',
    "reels": '<path d="M2.049 7.002h19.902"/><path d="m13.504 2.001 2.989 5.001"/><path d="m7.207 2.11 2.919 4.892"/><path d="M2 12.001v3.449c0 2.849.698 4.006 1.606 4.945.94.908 2.098 1.607 4.946 1.607h6.896c2.848 0 4.006-.699 4.946-1.607.908-.939 1.606-2.096 1.606-4.945V8.552c0-2.848-.698-4.006-1.606-4.945C19.454 2.699 18.296 2 15.448 2H8.552c-2.848 0-4.006.699-4.946 1.607C2.698 4.546 2 5.704 2 8.552z"/><path d="M9.763 17.664a.908.908 0 0 1-.454-.787V11.63a.909.909 0 0 1 1.364-.788l4.545 2.624a.909.909 0 0 1 0 1.575l-4.545 2.624a.91.91 0 0 1-.91 0z" fill="currentColor"/>',
    "direct": '<path d="M22 3 9.218 10.083"/><polygon points="11.698 20.334 22 3.001 2 3.001 9.218 10.084 11.698 20.334"/>',
    "heart": '<path d="M16.792 3.904A4.989 4.989 0 0 1 21.5 9.122c0 3.072-2.652 4.959-5.197 7.222-2.512 2.243-3.865 3.469-4.303 3.752-.477-.309-2.143-1.823-4.303-3.752C5.141 14.072 2.5 12.167 2.5 9.122a4.989 4.989 0 0 1 4.708-5.218 4.21 4.21 0 0 1 3.675 1.941c.84 1.175.98 1.763 1.12 1.763s.278-.588 1.11-1.766a4.17 4.17 0 0 1 3.679-1.938z"/>',
    "comment": '<path d="M20.656 17.008a9.993 9.993 0 1 0-3.59 3.615L22 22z"/>',
    "save": '<polygon points="20 21 12 13.44 4 21 4 3 20 3 20 21"/>',
    "create": '<path d="M2 12v3.45c0 2.849.698 4.005 1.606 4.944.94.909 2.098 1.608 4.946 1.608h6.896c2.848 0 4.006-.7 4.946-1.608C21.302 19.455 22 18.3 22 15.45V8.552c0-2.849-.698-4.006-1.606-4.945C19.454 2.7 18.296 2 15.448 2H8.552c-2.848 0-4.006.699-4.946 1.607C2.698 4.547 2 5.703 2 8.552z"/><path d="M6.545 12.001h10.91"/><path d="M12.003 6.545v10.91"/>',
    "menu": '<path d="M3 4h18M3 12h18M3 20h18"/>',
    "grid": '<rect x="3" y="3" width="18" height="18"/><path d="M9.015 3v18M14.985 3v18M21 9.015H3M21 14.985H3"/>',
    "tag": '<path d="M10.201 3.797 12 1.997l1.799 1.8a1.59 1.59 0 0 0 1.124.465h5.259A1.818 1.818 0 0 1 22 6.08v14.104a1.818 1.818 0 0 1-1.818 1.818H3.818A1.818 1.818 0 0 1 2 20.184V6.08a1.818 1.818 0 0 1 1.818-1.818h5.26a1.59 1.59 0 0 0 1.123-.465z"/><path d="M18.598 22.002V21.4a3.949 3.949 0 0 0-3.948-3.949H9.495A3.949 3.949 0 0 0 5.546 21.4v.603"/><circle cx="12.07211" cy="11.07515" r="3.55556"/>',
    "dots": '<circle cx="12" cy="12" r="1.5" fill="currentColor"/><circle cx="6" cy="12" r="1.5" fill="currentColor"/><circle cx="18" cy="12" r="1.5" fill="currentColor"/>',
    "back": '<path d="M15 4 7 12l8 8"/>',
}


def igi(name, cls=""):
    return (f'<svg class="igi {cls}" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{IGI[name]}</svg>')


PIN = ('<svg class="ig-pin" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M15.6 2.4a1 1 0 0 1 1.4 0l4.6 4.6a1 1 0 0 1 0 1.4l-1.3 1.3a1 1 0 0 1-1.1.2l-3.3 3.3.4 3.6a1 1 0 0 1-.3.8l-1 1a1 1 0 0 1-1.4 0l-3.4-3.4-5.1 5.1a1 1 0 0 1-1.4-1.4l5.1-5.1-3.4-3.4a1 1 0 0 1 0-1.4l1-1a1 1 0 0 1 .8-.3l3.6.4 3.3-3.3a1 1 0 0 1 .2-1.1z"/></svg>')

LETTERS = [("M", "b"), ("a", "r"), ("n", "y"), ("l", "b"), ("e", "g"), ("y", "r"), ("g", "b"), ("l", "g"), ("e", "r")]


def _mfx(films):
    """ManleyFlix, the same markup build.tv() renders, minus the TV."""
    top, rows = tv_rows(films)
    bill = next((f for f in films if f["slug"] == "scar-tissue"), films[0])
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
    return f"""<div class="mfx cw__page" data-page="flix" hidden aria-label="ManleyFlix">
        <header class="mfx__bar"><span class="mfx__word" aria-label="ManleyFlix">MANLEYFLIX</span>
          <nav class="mfx__nav" aria-hidden="true"><b>Home</b><span>Films</span><span>Music Videos</span><span>My List</span></nav></header>
        <div class="mfx__bill">
          <video class="mfx__bill-v" muted loop playsinline preload="none" poster="/media/posters/{bill['slug']}.jpg" data-src="/media/loops/{bill['slug']}.mp4"></video>
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
      </div>"""


# The first two rows are his strongest and most varied frames, the way
# you'd curate the top of a real profile; the rest follow in his order.
GRAM_LEAD = ["01", "07", "58", "22", "39", "55", "03", "45", "59", "24"]
# Highlights group the photographs by what they are, from looking at each.
GRAM_HIGHLIGHTS = [
    ("Light", ["01", "02", "03", "05", "11", "43", "52", "56", "61", "65", "68"]),
    ("Night", ["07", "21", "49", "54", "64"]),
    ("Travel", ["04", "08", "09", "16", "20", "45", "46", "47"]),
    ("Faith", ["02", "14", "22", "24", "25", "28"]),
    ("Live", ["36", "38", "39", "40"]),
    ("Outside", ["13", "18", "29", "31", "35", "48", "51", "58", "59", "67", "69"]),
]
TAGGED = [("set", "Parker on set behind a cinema camera"), ("rock", "Parker filming on a granite outcrop"), ("bigbear", "Parker above a mountain lake")]


def _gram(photos, films=()):
    by = {p["file"][:2]: p for p in photos}
    lead = [by[k] for k in GRAM_LEAD if k in by]
    ordered = lead + [p for p in photos if p not in lead]
    posts = [{"thumb": f"/media/photos/thumb/{p['file']}", "full": f"/media/photos/{p['file']}", "w": p["w"], "h": p["h"]} for p in ordered]
    n = len(posts)
    tile = lambda p, i, total, label="Post": (
        f'<button type="button" class="ig-tile" data-i="{i}" data-full="{p["full"]}" '
        f'data-w="{p["w"]}" data-h="{p["h"]}" aria-label="{label} {i + 1} of {total}">'
        f'<img src="{p["thumb"]}" alt="" loading="lazy" decoding="async"></button>')
    tiles = "".join(tile(p, i, n) for i, p in enumerate(posts))
    def hl_set(ks):
        return ",".join(f"/media/photos/{by[k]['file']}|{by[k]['w']}|{by[k]['h']}" for k in ks if k in by)
    hl = "".join(
        f'<button type="button" class="ig-hl" data-set="{hl_set(ks)}">'
        f'<span class="ig-hl__ring"><img src="/media/photos/thumb/{by[ks[0]]["file"]}" alt="" loading="lazy"></span><span class="ig-hl__t">{t}</span></button>'
        for t, ks in GRAM_HIGHLIGHTS
    )
    # Sizes come from a file written when the photos were made: the deploy
    # image has no Pillow, so the build reads no images.
    sizes = json.loads(Path("media/desk/tagged/sizes.json").read_text())
    tagged = [{"thumb": f"/media/desk/tagged/{k}-t.jpg", "full": f"/media/desk/tagged/{k}.jpg", "w": sizes[k][0], "h": sizes[k][1]} for k, _ in TAGGED]
    tagged_html = "".join(tile(p, i, len(tagged), "Tagged photo") for i, p in enumerate(tagged))
    feat = [f for f in films if f.get("featured")]
    reels = (
        f'<button type="button" class="ig-reel ig-reel--mfx" data-go="flix" aria-label="Watch Parker\'s films on ManleyFlix">'
        f'<span class="ig-reel__m">{M_ICON}</span><span class="ig-reel__w">MANLEYFLIX</span>'
        f'<span class="ig-reel__c">All my films are streaming on ManleyFlix. Tap to watch.</span></button>'
    )
    av = '<img src="/media/desk/avatar.jpg" alt="">'
    rail = "".join(f'<span class="ig-rail__i">{igi(k)}</span>' for k in ("home", "search", "explore", "reels", "direct", "heart", "create"))
    tabbar = "".join(f'<span class="ig-nav__i">{igi(k)}</span>' for k in ("home", "explore", "reels", "create", "direct"))
    return f"""<div class="ig cw__page" data-page="gram" hidden aria-label="ManleyGram profile of {NAME}">
        <aside class="ig-rail" aria-hidden="true"><span class="ig-rail__logo">{IG_GLYPH}</span>{rail}
          <span class="ig-rail__i ig-rail__me"><span class="ig-av ig-av--xs">{av}</span></span><span class="ig-rail__i ig-rail__more">{igi("menu")}</span></aside>
        <div class="ig-main">
          <div class="ig-top" aria-hidden="true"><span class="ig-top__u">{USER}</span>{igi("dots")}</div>
          <header class="ig-head">
            <span class="ig-av ig-av--lg">{av}</span>
            <div class="ig-head__info">
              <div class="ig-head__row"><h2 class="ig-head__u">{USER}</h2>
                <span class="ig-head__btns"><button type="button" class="ig-btn ig-btn--blue">Follow</button><button type="button" class="ig-btn">Message</button>
                <span class="ig-head__more">{igi("dots")}</span></span></div>
              <p class="ig-head__stats"><span><b>{n}</b> posts</span></p>
              <div class="ig-head__bio"><p class="ig-head__name">{NAME}</p><p>{BIO}</p></div>
            </div>
          </header>
          <p class="ig-stats"><span><b>{n}</b><br>posts</span></p>
          <div class="ig-hls">{hl}</div>
          <nav class="ig-tabs" role="tablist"><button type="button" class="is-on" data-tab="posts">{igi("grid")}<i>Posts</i></button><button type="button" data-tab="reels">{igi("reels")}<i>Reels</i></button><button type="button" data-tab="tagged">{igi("tag")}<i>Tagged</i></button></nav>
          <div class="ig-grid" data-grid="posts">{tiles}</div>
          <div class="ig-grid ig-grid--reels" data-grid="reels" hidden>{reels}</div>
          <div class="ig-grid" data-grid="tagged" hidden>{tagged_html}</div>
        </div>
        <nav class="ig-nav" aria-hidden="true">{tabbar}<span class="ig-nav__i"><span class="ig-av ig-av--xs">{av}</span></span></nav>
      </div>
      <div class="igv" hidden role="dialog" aria-modal="true" aria-label="Post by {USER}">
        <button type="button" class="igv__x" aria-label="Close">{_svg(I_CLOSE)}</button>
        <div class="igv__bar"><button type="button" class="igv__back" aria-label="Back to profile">{igi("back")}</button><b>Posts</b><span></span></div>
        <div class="igv__card">
          <div class="igv__media"><img class="igv__img" alt="Photograph by Parker Manley">
            <button type="button" class="igv__nav igv__nav--p" aria-label="Previous post">{_svg(I_CHEV_L)}</button>
            <button type="button" class="igv__nav igv__nav--n" aria-label="Next post">{_svg(I_CHEV_R)}</button></div>
          <div class="igv__side">
            <div class="igv__head"><span class="ig-av ig-av--sm">{av}</span><b>{USER}</b><span class="igv__dot">&middot;</span><button type="button" class="igv__follow">Follow</button>{igi("dots", "igv__more")}</div>
            <div class="igv__body"><p class="igv__empty"><b>No comments yet.</b><span>Start the conversation.</span></p></div>
            <div class="igv__acts"><button type="button" class="igv__a igv__like" aria-label="Like" aria-pressed="false">{igi("heart")}</button>
              <button type="button" class="igv__a" aria-label="Comment">{igi("comment")}</button>
              <button type="button" class="igv__a" aria-label="Share">{igi("direct")}</button>
              <button type="button" class="igv__a igv__save" aria-label="Save" aria-pressed="false">{igi("save")}</button></div>
          </div>
        </div>
      </div>"""


def _ntp():
    word = "".join(f'<span class="mg-{c}">{ch}</span>' for ch, c in LETTERS)
    tile = lambda key, label, icon: (
        f'<button type="button" class="ntp__sc" data-go="{key}"><span class="ntp__sc-i">{icon}</span><span class="ntp__sc-t">{label}</span></button>'
    )
    return f"""<div class="ntp cw__page" data-page="ntp" aria-label="New Tab">
        <div class="ntp__top" aria-hidden="true"><span>Gmail</span><span>Images</span>{_svg(I_APPS, "ntp__apps")}<span class="ig-av ig-av--sm"><img src="/media/desk/avatar.jpg" alt=""></span></div>
        <div class="ntp__mid">
          <h2 class="ntp__logo" aria-label="Manleygle">{word}</h2>
          <form class="ntp__box" role="search">
            {_svg(I_SEARCH, "ntp__mag")}
            <input class="ntp__q" type="text" name="q" autocomplete="off" spellcheck="false" aria-label="Search Manleygle" placeholder="Search Manleygle or type a URL">
            {_svg(I_MIC, "ntp__mic")}{_svg(I_LENS, "ntp__lens")}
          </form>
          <div class="ntp__scs">{tile("flix", "ManleyFlix", M_ICON)}{tile("gram", "ManleyGram", GRAM_FAV)}</div>
        </div>
      </div>"""


def desk_section(films, photos):
    menus = "".join(f"<span>{m}</span>" for m in ("File", "Edit", "View", "History", "Bookmarks", "Profiles", "Tab", "Window", "Help"))
    dock = [("Google Chrome", DOCK_CHROME, True), ("FilmCraft", DOCK_CUT, True)]
    dock_html = "".join(
        f'<span class="dock__app" data-name="{n}">{svg}{"<i class=dock__dot></i>" if run else ""}<span class="dock__tip">{n}</span></span>'
        for n, svg, run in dock
    )
    tb = lambda cls, path, label: f'<button type="button" class="cw__btn {cls}" aria-label="{label}">{_svg(path)}</button>'
    return f"""
<section class="desk" aria-label="Parker's Mac">
  <div class="desk__screen" style="--wall: url('/media/photos/{WALLPAPER}')">
    <img class="desk__wall" src="/media/photos/{WALLPAPER}" alt="" aria-hidden="true">
    <div class="mb" aria-hidden="true">
      <span class="mb__l">{APPLE}<b>Chrome</b><span class="mb__menus">{menus}</span></span>
      <span class="mb__r">{BATTERY}{WIFI}{CONTROL}<time class="mb__clock"></time></span>
    </div>
    <div class="cw" data-at="flix">
      <div class="cw__strip">
        <span class="cw__lights" aria-hidden="true"><i></i><i></i><i></i></span>
        <div class="cw__tabs" role="tablist">
          <button type="button" role="tab" class="cw__tab" data-go="gram"><span class="cw__fav">{GRAM_FAV}</span><span class="cw__title">Parker Manley (@parkermanley)</span>{_svg(I_CLOSE, "cw__tabx")}</button>
          <button type="button" role="tab" class="cw__tab is-on" data-go="flix"><span class="cw__fav">{M_ICON}</span><span class="cw__title">ManleyFlix</span>{_svg(I_CLOSE, "cw__tabx")}</button>
          <button type="button" role="tab" class="cw__tab" data-go="contact"><span class="cw__fav cw__fav--pm">P</span><span class="cw__title">Contact Parker Manley</span>{_svg(I_CLOSE, "cw__tabx")}</button>
        </div>
        <span class="cw__newtab" aria-hidden="true">{_svg(I_ADD)}</span>
        <span class="cw__tsearch" aria-hidden="true">{_svg(I_DOWN)}</span>
      </div>
      <div class="cw__bar">
        {tb("cw__back", I_BACK, "Back")}{tb("cw__fwd", I_FWD, "Forward")}{tb("cw__reload", I_RELOAD, "Reload")}
        <form class="cw__omni" role="search">
          <span class="cw__chip" aria-hidden="true">{_svg(I_TUNE)}</span>
          <input class="cw__url" type="text" autocomplete="off" spellcheck="false" aria-label="Address and search bar" placeholder="Search Manleygle or type a URL">
          <span class="cw__star" aria-hidden="true">{_svg(I_STAR)}</span>
        </form>
        <span class="cw__ext" aria-hidden="true">{_svg(I_PUZZLE)}</span>
        <span class="cw__me ig-av ig-av--xs" aria-hidden="true"><img src="/media/desk/avatar.jpg" alt=""></span>
        <span class="cw__menu" aria-hidden="true">{_svg(I_MORE)}</span>
      </div>
      <div class="cw__vp">
      {_mfx(films)}
      {_gram(photos, films)}
      <div class="cpm cw__page" data-page="contact" aria-label="Contact Parker Manley" hidden><img class="cpm__shot" src="/media/desk/pinned.jpg" alt="Parker Manley filming on a green screen"></div>
      </div>
      <template class="cw__favs"><span data-for="flix">{M_ICON}</span><span data-for="gram">{GRAM_FAV}</span></template>
    </div>
    <div class="dock" aria-hidden="true"><div class="dock__glass">{dock_html}<span class="dock__app dock__app--credits" data-name="End Credits">{DOCK_CREDITS}<span class="dock__tip">End Credits</span></span><span class="dock__sep"></span>
      <span class="dock__app" data-name="Trash">{DOCK_TRASH}<span class="dock__tip">Trash</span></span></div></div>
  </div>
</section>
"""
