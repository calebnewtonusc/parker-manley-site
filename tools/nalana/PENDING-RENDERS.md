# Pending renders: hold until Parker signs off

Caleb's rule, 2026-10-25 23:55: render nothing until the final product is locked with Parker's vision. Nothing below is queued. Every job goes through `chewbacca jobs submit --heavy`, one at a time.

## Done and on disk (final quality, 128 samples, 1920 wide)

All in /private/tmp/claude-501/pm/final/:

- hall/: the five stills (scar-tissue, abundance, beneath-the-surface, somnambulist, the-five-stages-of-wasabi) and hall.json. The quads are exactly 2x the draft3 ones.
- knoll/: knoll_table.jpg, knoll_shadowcatch.png (polaroids removed, so lifting one leaves no dark hole) and knoll.json. The paper and lcd quads are identical to draft3.
- monitor/: monitor_base.png, monitor_glass.png, monitor_off.png and monitor.json. The booth light is hidden from reflections, so the glass has no hard rectangle.
- rollin/: frames 001 to 020 of 60, plus lensview.png and rollin.json. The job was killed at 20.

## 1. Roll-in final: finish frames 21 to 60

- Frames 1 to 20 are good. Frame 1 matches the final Wasabi hall still (mean diff 1.07). Frame 60's quad in rollin.json equals monitor.json's to the hundredth of a pixel.
- Time: about 5.5 to 8 min a frame on this Mac, so roughly 4 to 5 hours for the remaining 40.
- rollin.py renders every frame, or the single frame given as its 4th argument. To resume without redoing 1 to 20, either run 40 single-frame jobs, or first add a start-frame argument: render `range(START, FRAMES + 1)`, keep the json export over all frames, and skip the lensview prerender when lensview.png already exists.
- Command for one frame:

      PM_W=1920 PM_FILM=the-five-stages-of-wasabi /Applications/Nalana.app/Contents/MacOS/Nalana -b --factory-startup --python ~/code/personal/parker-manley-site/tools/nalana/rollin.py -- /private/tmp/claude-501/pm/final 128 60 <frame>

- Polish worth doing before the final, if Parker keeps the idea:
  - Frame 60 must stay pixel-identical to monitor_base.png. Any change to rig.py, premiere.py lighting, mid_loc or the monitor framing means re-rendering monitor_stills.py too.
  - The monitor feed (lensview.png) is a still of the hall from the rig's lens. If the page plays live film in the hall, the feed should be a frame of that film, or the page should map the live film into rollin.json's quad from frame 30 on.
  - The tally is at 6.0 emission (red, not white). The monitor turns on at frame 30 over two frames.
  - Hall stills were rendered before the booth light was hidden from reflections. The difference is invisible in the stills, but re-render them if anything in the hall changes.

## 2. Sky tilt: street realism pass

Full notes are in SKYTILT-STREET-NOTES.md, next to this file. In short: skytilt2.py already has the v3 street written and compiled but never rendered:

- recessed lit shop bays behind thin glass, some dark, with silhouetted fixtures
- curtained upper windows, most dark
- neon tube signs with generic words, plus a glow pass
- sodium street-light pools
- red and white light trails
- a wet street and a horizon glow
- f/2 depth of field over the street, back to f/8 on the star

Run the 3-frame test (12, 22, 28) first. Then render 36 frames into a new folder (sky2/frames_v3), so the draft on the site is not overwritten.

## 3. Open items, independent of Parker's direction

- Knoll table: the handheld camera reads blocky from overhead, and the left third of the table is sparse.
- Shadow catch: the pass is opaque (table plus shadows), not a transparent shadow-only layer. Ask if the page needs the latter.
- SPEC item 5 (Boulder to LA) has no render yet: it waits on Parker's story beats.
