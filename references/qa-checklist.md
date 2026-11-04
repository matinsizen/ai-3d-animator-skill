# Phase 6 — QA Gate

Nothing ships until every applicable line passes. Run the checklist yourself, honestly — it takes 2 minutes and it's the difference between "AI made a thing" and "a studio delivered a film".

## A. Spec compliance
- [ ] Duration matches the receipt exactly (frame count = seconds × fps; verify with `ffprobe`)
- [ ] Resolution and fps match the receipt exactly
- [ ] Output container/codec plays in a plain browser/videoplayer (MP4/H.264/yuv420p, or WebM as agreed)
- [ ] Filename follows convention: `subject_WxH_fps_duration_style.ext` (e.g. `blob-button_1920x1080_30fps_8s_puffy.mp4`)
- [ ] Loop requested → first frame pose == last frame pose; motion + audio both seamless (no master fades)

## B. Style consistency (check against the style bible)
- [ ] All colors from the locked palette (no default `#808080`, no off-palette strays)
- [ ] Geometry rules respected (Puffy: **zero sharp edges**; Low-poly: actually low-poly; Voxel: grid-locked)
- [ ] Background/fog/shadows from the same palette family
- [ ] Motion personality matches the style (no floaty Puffy in a Neon scene, no 60 fps-smooth Claymation)
- [ ] Materials have the style's roughness/sheen/coat values (not raw defaults)

## C. Visual sanity
- [ ] First, middle, and last frames inspected as standalone stills (composition, rule of thirds)
- [ ] Everything grounded: contact shadows touch objects; floaters bob and have soft/growing shadows
- [ ] No z-fighting (coplanar surfaces offset by ≥ 0.001)
- [ ] No clipped/intersecting meshes, nothing important cut by frame edge
- [ ] Eyes/focal details at intentional placement (Puffy: eyes at 60% up the head)
- [ ] Tone mapping on, exposure intentional (not washed, not murky)

## D. Motion (run the anti-pattern audit from animation-principles.md)
- [ ] No unjustified linear/default easing anywhere
- [ ] Main action has anticipation → action → settle (the trio)
- [ ] Landings squash with volume preservation; takeoffs stretch
- [ ] Parts overlap (body/head/arms offsets), idle has breath + blink
- [ ] Camera move has a reason, an easing, and clean first/last compositions
- [ ] Loop gags end settled ≥ 0.3 s before the seam

## E. Sound
- [ ] Every timing-sheet cue exists and is within ±2 frames of its event
- [ ] Whooshes lead impacts; impacts land on the contact frame
- [ ] Peaks ≤ −3 dBFS; limiter at −1; loudness ≈ −16 LUFS
- [ ] Master fades in/out (non-loop) — or bed loops cleanly (loop)
- [ ] Watched once muted (readable) and once with sound (feels better, not busier)

## F. Delivery note (include with every delivery)
One short paragraph: what was built, the spec line, the style + why, where the sound came from, how to request changes ("want it faster? loop longer? vertical version?"). Offer one concrete next iteration — professionals suggest, not just deliver.

## Self-test protocol
1. Stills: render frame 1, mid-action, last → inspect (catches composition/grounding/color instantly).
2. Muted watch, then sound watch.
3. `ffprobe` duration/resolution/streams.
4. If anything fails: fix in the *generator/timing sheet*, re-render, re-run this gate. Never patch a single frame by hand.
