# Parker Manley site: the spec

One continuous take. Every section hands off to the next on screen; nothing
is a slide. Written 2026-10-25 from every message Caleb sent that night.
`/preview/` shows this order with draft renders before anything final renders.

## Rules (Caleb's words)

- Nothing ever rendered until Caleb has answered the questions and seen `/preview/`.
- No final or polish renders until the final product is locked with Parker's vision (Caleb, 2026-10-25 23:55). Until then, low poly drafts only.
- Everything has to look REAL. Nothing can look HTML/CSS, like a video game, like a PDF, or like Claude slop.
- No repeats: each film appears in one place, except in ManleyFlix, which holds the whole library.
- No unintentional rectangles, gradients, lines, overflow or transitions. Complex is not the same as creative.
- No circles opening or closing (iris) anywhere.
- Sound has to be tasteful and intentional all the way through, and quiet in the camera scene.
- Every section is an intentional length, and every clip sits where it fits best.
- Header: name plus a sound toggle. No links that jump down the page.

## The take, in order (as built, 2026-10-26 00:20)

1. ADMIT ONE roll ticket with torn ends, bitten corners and two small rips. Click it to tear it.
2. 3 2 1 leader. Each number gets its own pop, and it's the same frame as the reel.
3. Opening reel. Music fades over about 2 s with the scroll, both ways.
4. Parker's table (knoll render). The reel keeps playing on his camera's flip screen. We pull back from that screen to the whole table, then lean in to the call sheet clipped to the board. The flip screen covers the window exactly the way the reel does, so the cut lands on the same pixels.
5. Boulder to LA. A red "Needs Parker" card until he answers the story questions. Don't render it until he gives direction.
6. Director: the premiere hall render with 5 films (scar-tissue, abundance, beneath-the-surface, somnambulist, the-five-stages-of-wasabi). The films and letterboard are inside the render. Click the screen to watch.
7. Roll-in: 60 frames of a camera rolling up the aisle, ending exactly on the camera scene's monitor framing.
8. Camera: the monitor opens on what the roll-in left on it (the live view of the hall screen), then the first take comes up over it and the cinematography adjustments play. Click the monitor to watch. At the end, our point of view dollies INTO the monitor (rig, glass and picture move together) until the picture fills the window. The bezel and theater fall to black.
9. Premiere Pro edit bay: it opens on that frame. Panels are dragged in from the edges by the cursor, then the window shrinks and slides off onto the Mac.
10. The Mac: Chrome at 85% with 3 big tabs (ManleyGram, ManleyFlix, Contact Parker Manley), no bookmarks bar. The Dock holds Chrome, Adobe Premiere Pro, End Credits and Trash.
    - ManleyFlix: Netflix layout, every film. Hover cards grow over neighbours without clipping.
    - ManleyGram: his photos, Instagram-style. Reels is one post pointing to ManleyFlix.
    - Contact tab: the end card lives INSIDE the tab. Opening it shows him on green, the key pulls to the real forest, then the slate is held in. Clap the sticks to send. Notes ("Fill in every line first") replace "Clap it to send" in the same hand.
    - Premiere Pro in the Dock scrolls back to the edit bay.
    - End Credits in the Dock does one macOS bounce when the viewer stops (4 s after the slate settles on Contact, else 9 s idle, at most twice).
11. The Mac is the END of the page. Scrolling never reaches the credits. Only End Credits does (Caleb, 2026-10-25: "the end credits button should be the only way"). Scrolling back up from the credits returns to the Mac.
12. End Credits clicked: "Where Is My Mind?" fades in, and the page lands with the title in the middle of the window. The Mac dissolves to black.
13. Credits roll on pure black: big title, a long gap, the three Parker Manley lines, the cast, then thanks, music, locations and Get in touch, each with room of its own.
14. A full window of black after the last credit. Then the palm-tree night above Hollywood Blvd comes up from under the credits (its dark sky melts into the black), pins, holds a beat and tilts down to his star. The page ends on the star. The song plays through all of it. The street is a DRAFT render until Parker okays the idea.

Phone: same order, simpler. The end card is its own section there, and the credits aren't locked.

## Open, waiting on someone

- Parker: the flight story beats (item 5), checking film titles, years and credits, and whether he likes the overall take.
- Parker: click FormSubmit's activation email in prmanley@usc.edu (sent by Caleb's test on 2026-10-26). Until then contact messages don't reach him. FormSubmit answers in 17 to 26 s, so the slate waits up to 45 s.
- Renders, after Parker signs off: the roll-in polish and the realistic street. Notes are in tools/nalana/PENDING-RENDERS.md and tools/nalana/SKYTILT-STREET-NOTES.md.

## Checks to run after any change

- `python3 tools/check_build_no_pil.py`. Railway's image has no Pillow.
- `python3 tools/check_full_bleed.py <url>`. Every pinned scene fills the window and sits flush at the top of its section.
- `python3 tools/walk_seams.py <url>`. Shoots a frame either side of every hand-off at 1000x506 (Caleb's window). Look at the sheet.
- Any z-index or overlap change: rerun the walk. On 2026-10-25, raising the Mac above the credits put it above the edit bay too.
