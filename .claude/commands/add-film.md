---
description: Add a new film to the site from its YouTube link
argument-hint: <youtube link>
---
Parker's adding this film: $ARGUMENTS

1. If there's no link, ask for it. Ask him in one message, all at once, for anything you can't find: his role on it, genre, length, one line synopsis, cast, music, what class or festival it was for, where it ranks among his films, and a poster if he has one (otherwise YouTube's thumbnail is used). Check his old page at parkermanley.com/films and the YouTube description first, and offer what you found so he only has to confirm. Never guess his role. Show him the title you'll use, since YouTube's can differ from how he writes it, and pass `--title` if it does.
2. Run `/usr/bin/python3 tools/add_film.py "<link>"` with `--role`, `--genre`, `--minutes`, `--synopsis`, `--cast`, `--music`, `--made-for`, `--rank`, and `--poster` if he gave one.
3. Start the preview with `/usr/bin/python3 -m http.server 8000 -d dist` in the background and open `http://localhost:8000/films/<slug>/` for him. Tell him to look at that page and at ManleyFlix on the home page.
4. Wait. When he says it's good, commit `data/films.json` and the poster with a message naming the film, then push to main. Load the live page after a minute or two and tell him it's up, or exactly what went wrong.
