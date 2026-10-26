# Sky tilt: street realism notes

Status 2026-10-25: on hold until Parker sees the draft (pm/sky2/frames, 36 frames, the v2 draft now on the site as a preview) and okays the idea. Nothing below has rendered yet.

## What the coordinator flagged in the v2 draft

Mid-tilt (about frames 12 to 24) the street read like a video game:

- flat white rectangles for windows and storefronts
- a blocky "HOTEL" box sign
- plain stucco boxes
- an empty road
- a floating green bar (a blade sign not attached to anything)

The sky with palms (frame 1) and the star landing (frames 28 to 36) were approved, so their camera keys must not change.

## What skytilt2.py now does (written, not rendered)

- Storefronts: each shop is a recessed bay 2.6 m deep behind thin glass. The glass is a Fresnel mix of transparent and glossy, so it reflects the street at an angle and shows the room straight on. About 72 % of shops are lit by an area light (250 to 700 W, warm to neutral), the rest are dark. Shelving and racks stand in silhouette. Mullions and a kick plate frame each bay, and some have a canopy.
- Upper windows: a trim frame, glass, and a room or curtain behind (noise-varied emission, warm to cool). About 30 % are lit; the rest are nearly black.
- Signs: neon only. Each sign is the glyph outlines of a generic word (OPEN, COCKTAILS, LIVE MUSIC, VINYL, DINER, TATTOO, HOTEL, CAFE, THEATRE, BAR, PIZZA, SOUVENIRS), bevelled into 1.6 cm tubes, never filled, plus a small coloured spill light on the facade. No real brand names. The box signs and blade signs are gone.
- Traffic: long-exposure light trails. Seven red tail-light streaks run in the near lanes and six white head-light streaks on the far side, at 0.55 to 1.0 m high.
- Street lights: sodium (1.0, 0.60, 0.28) spots with a 110 degree cone, so they cast pools instead of a flat wash. Two more poles go on the near side, at x = 7.5 and -11.
- The lamp over his star keeps its approved colour and energy (3000 W, 2700 K-ish, 140 degree cone).
- Wet street: the asphalt roughness is puddled (0.06 to 0.5 from low-frequency noise), so the lights smear in it.
- Sky: the shanghai_bund HDRI at 0.15 strength, tinted sodium (1.0, 0.62, 0.42), plus an added glow band within about 20 degrees of the horizon.
- Depth of field: focus pulls from 40 m in to the star's distance over frames 8 to 15. The aperture opens to f/2 across the street and closes back to f/8 by frame 28, so the street is soft as we pass and the star lands exactly as star-2000.webp.
- Glow: a Fog Glow compositor pass (threshold 1.2) for neon and lamps. It tries the Blender 5 compositor API first and falls back to the legacy one. Check the log for "glare: on".
- Unchanged: the camera keys (108 degree tilt, quintic ease), the 960x576 frame (5:3, the star's aspect), the walk tiles and his slab.

The v2 script is kept at /private/tmp/claude-501/pm/skytilt2_v2a_backup.py if the draft look is wanted again.

## To run it once Parker okays

Test three frames first (street, mid, star) at 16 samples:

    chewbacca jobs submit --heavy --title "pm skytilt3 test 3f" -- /bin/sh -c "/Applications/Nalana.app/Contents/MacOS/Nalana -b --factory-startup --python ~/code/personal/parker-manley-site/tools/nalana/skytilt2.py -- /private/tmp/claude-501/pm/sky2/test3 /tmp/claude-501/pm/star/maps /private/tmp/claude-501/pm/sky2/tiles 16 36 12 22 28"

Then the 36 frames at 32 samples into a new folder, so the draft the site uses is not overwritten:

    ... skytilt2.py -- /private/tmp/claude-501/pm/sky2/frames_v3 /tmp/claude-501/pm/star/maps /private/tmp/claude-501/pm/sky2/tiles 32 36

For the final, raise the samples (128) and keep everything else.

## Check before shipping

1. In frames 12 and 22, look for any flat rectangle that is not glass with a room behind it, and any sign that is not a lit tube.
2. The neon must glow but not bloom across the facade. If it does, raise the glare threshold.
3. The light pools on the sidewalk must have dark gaps between them.
4. Frame 36 must match star-2000.webp's edges. The v2 frame 36 correlated at 0.92 at zero offset and 0.27 at a 4 px shift, so re-run that check.
5. If the shop interiors read as empty boxes at 960 px, add a person-height silhouette or two per lit shop. This is the most likely remaining "set" tell.
6. Real Hollywood Blvd details still missing: parked cars along the far curb, a bus shelter, overhead traffic signals at a crossing, and the Walk of Fame's second star row. Add them if the draft still reads as a set.

## Not done

- No car models: the light trails stand in for traffic.
- Facades are Poly Haven plaster and brick on boxes. There are no Hollywood Blvd landmarks, by design, because those are real places and brands.
