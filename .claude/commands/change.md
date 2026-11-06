---
description: Change anything on the site, see it, then decide
argument-hint: <what you want different>
---
Parker wants this changed on his site: $ARGUMENTS

Read `CLAUDE.md`, and `SPEC.md` if it touches the home page. Tell him your plan in 3 bullets in plain English and wait for his go. Make the change, run `/usr/bin/python3 build.py`, start the preview with `/usr/bin/python3 -m http.server 8000 -d dist` in the background, and open the page for him. Don't push until he says to put it live. Add anything he tells you about his taste to "Parker's notes" in `CLAUDE.md`.
