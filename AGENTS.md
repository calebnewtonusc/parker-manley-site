# Parker Manley's film site

This is Parker's portfolio, and he owns it. He's a film director, not a programmer, so explain things in plain English, use film comparisons when they help, and show him the result instead of describing it. Before changing anything, tell him the plan in a few bullets and wait for his go. He makes the creative calls.

## How it goes live

`data/films.json` and the files in `src/` and `media/` are the source. `build.py` turns them into a finished site in `dist/`. When a commit lands on `main`, Railway rebuilds from the `Dockerfile` and the site changes about a minute later. `main` is the live cut, so only push when he says to put it live.

## Preview on his laptop

Use the Mac's own Python. It's 3.9, so keep `build.py` free of newer syntax, and run `/usr/bin/python3 tools/check_system_python.py` after editing it.

```bash
/usr/bin/python3 build.py
/usr/bin/python3 -m http.server 8000 -d dist
```

Then open http://localhost:8000. The film pages are at `/films/<slug>/`. `dist/` is never committed.

## The commands he uses

Codex has no slash commands here, so when he says any of these in plain words, do what's written below.

### "Add this film" and a link

Parker's adding this film: (what he said)

1. If there's no link, ask for it. Ask him in one message, all at once, for anything you can't find: his role on it, genre, length, one line synopsis, cast, music, what class or festival it was for, where it ranks among his films, and a poster if he has one (otherwise YouTube's thumbnail is used). Check his old page at parkermanley.com/films and the YouTube description first, and offer what you found so he only has to confirm. Never guess his role. Show him the title you'll use, since YouTube's can differ from how he writes it, and pass `--title` if it does.
2. Run `/usr/bin/python3 tools/add_film.py "<link>"` with `--role`, `--genre`, `--minutes`, `--synopsis`, `--cast`, `--music`, `--made-for`, `--rank`, and `--poster` if he gave one.
3. Start the preview with `/usr/bin/python3 -m http.server 8000 -d dist` in the background and open `http://localhost:8000/films/<slug>/` for him. Tell him to look at that page and at ManleyFlix on the home page.
4. Wait. When he says it's good, commit `data/films.json` and the poster with a message naming the film, then push to main. Load the live page after a minute or two and tell him it's up, or exactly what went wrong.

### "Change" something

Parker wants this changed on his site: (what he said)

Read `CLAUDE.md`, and `SPEC.md` if it touches the home page. Tell him your plan in 3 bullets in plain English and wait for his go. Make the change, run `/usr/bin/python3 build.py`, start the preview with `/usr/bin/python3 -m http.server 8000 -d dist` in the background, and open the page for him. Don't push until he says to put it live. Add anything he tells you about his taste to "Parker's notes" in `CLAUDE.md`.

### "Put it live"

Show Parker in plain English what's about to go live, then commit those files by name with a message saying what changed and push to main. Wait a minute or two, load the live page, and confirm the change is really there. Report anything that failed in plain English.

### "Take it back"

Find the last commit that changed the live site and tell Parker what it was in plain English. When he says yes, `git revert` it and push to main, never force push. Load the live page after a minute or two and confirm it's back.

## Add a film

Use `tools/add_film.py`, which fills the title, saves the poster, places the film and builds. By hand it goes like this:

1. Add an entry to `data/films.json`, placed where he ranks it. The order is his ranking. Use `youtube` for the 11 character video ID.
2. Ask him for his role. A blank `role` tells the site he wrote, directed, shot and edited it, so never leave it blank unless that's true. Copy the wording of other entries, like "Co-directed & written".
3. Add a poster at `media/posters/<slug>.jpg`. `build.py` prints "missing media" if it's not there, and the tile shows a broken image. If he has no poster, offer `https://img.youtube.com/vi/<id>/maxresdefault.jpg`.
4. `featured: true` puts it in Now Showing and also needs `media/loops/<slug>.mp4` and `<slug>-720.mp4`, a 6 to 8 second muted loop. Ask him before making a film featured.
5. Build, preview, have him look at the film's page on his own screen, then commit and push when he says to.

## Things that break quietly

- The `Dockerfile` copies files by name. A new Python file that `build.py` imports has to be added to its COPY line too, or Railway's build fails and the old site stays up. After any push, load the live page and check the change is really there.
- `SITE` near the top of `build.py` sets the address used in link previews. It should match the site's real address.
- The contact form sends through FormSubmit to his USC email, set by `EMAIL` in `build.py`.
- Parker's domain is at Namecheap with email forwarding. Never change its MX records.
- `SPEC.md` explains how the one continuous scroll fits together. Read it before changing the home page. The check scripts in `tools/` need Playwright, so ask before installing it.

## Undoing

Every commit is a saved cut. If something he put live looks wrong, use `git revert` on that commit and push, so the history stays. Never force push `main`.

## Saving his taste

When he corrects how something looks or reads, add a line to the section below so it holds next time.

## Parker's notes

- Dark like a theater, rustic and nature-y, Grand Budapest symmetry.
- The audience is crew leads and SCA professors, and the goal is that they contact him for work.
