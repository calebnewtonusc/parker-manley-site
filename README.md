# parkermanley.com

Parker Manley's film portfolio. Static site built by `build.py` from `data/films.json`, served by Caddy on Railway.

## Add a film

1. Add an entry to `data/films.json` where it ranks. `featured: true` puts it in Now Showing.
2. Add `media/posters/<slug>.jpg`. Featured films also need `media/loops/<slug>.mp4` and `<slug>-720.mp4` (6 to 8 second muted loop).
3. Push to main. Railway rebuilds and deploys.

Run `/usr/bin/python3 build.py` to build into `dist/`, then `/usr/bin/python3 -m http.server 8000 -d dist` to preview it. `CLAUDE.md` has the full guide.

All glory to God! ✝️❤️

## Credits

The edit bay on the home page copies its look from FilmCraft (https://github.com/storytold/filmcraft, MIT OR Apache-2.0): colors from `crates/ui-egui/src/theme.rs`, layout from its screenshots. Sound recordings are CC0, sources in `media/sfx/SOURCES.md`.
