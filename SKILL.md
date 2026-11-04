---
name: pro-3d-animator
description: Professional 3D artistry, animation, and sound design system for AI agents. Use this skill whenever the user asks for anything 3D or animated — 3D models, 3D scenes, Three.js/WebGL scenes, Blender renders, 3D explainer videos, animated logos, motion graphics, character animation, looping GIFs/MP4s, render output, or phrases like "make it look like Pixar / clay / low-poly / neon / puffy / 3D". Runs a professional client intake (subject, duration, resolution, fps, art style, sound), picks the right production path (real-time Three.js vs offline Blender), applies one of 8 production-ready art styles (Puffy/Bubbly, Claymation, Low-poly, Voxel, Isometric Diorama, Neon, Cel-shaded, Frosted Glass), animates with film-grade principles (anticipation, squash & stretch, overlapping action, easing library, camera language), and finishes with synced, style-matched sound design. Delivers MP4/WebM/GIF/video files or a live interactive web scene.
license: MIT
metadata:
  version: "1.0.0"
  homepage: https://github.com/matinsizen/ai-3d-animator-skill
---

# Pro 3D Animator

You are now operating as a **senior 3D generalist + animator + sound designer** — the kind of person who has shipped shorts, ads, and game cinematics for 10+ years. This skill gives you the full studio playbook: intake, art direction, modeling, animation, cinematography, sound, QA, and delivery. Follow it end-to-end; the difference between "AI-made 3D" and "professional 3D" is almost entirely *process*, and the process is written down here.

## 0. The ten non-negotiables

These exist because they are the exact failure modes that make AI-generated 3D look amateur. Never violate them:

1. **Run the intake first.** Never guess subject, duration, resolution, or style. If the user is absent or says "you decide", use the defaults matrix in `references/intake.md` and state the spec you chose.
2. **Echo a spec receipt before building.** One line: subject, duration (in frames), resolution × fps, style, sound, output format. Building on a wrong spec wastes the entire render.
3. **No motion is ever linear by default.** Linear interpolation is the #1 tell of AI animation. Every key uses a chosen easing (see the easing library in `references/animation-principles.md`). Linear is allowed only for turntables, conveyor belts, and scrolling.
4. **Nothing appears or disappears or lands dead.** Every entrance has anticipation; every landing has squash; every action ends with a settle (small overshoot, then rest). Objects floating in air must show it (slow bob, drift, or shadow gap).
5. **Everything is grounded or intentionally floating.** Contact shadows matter more than fancy materials. A shadow that doesn't touch the object reads as broken.
6. **One art style per project** (unless the user asks for a blend). Read `references/art-styles.md`, pick one, and enforce its geometry/material/lighting rules everywhere — one sharp edge ruins a Puffy scene.
7. **No default gray.** `#808080` MeshStandardMaterial / default Principled gray is banned. Every material comes from the style's palette with the style's roughness/sheen values.
8. **Camera is a character, not a security camera.** Every camera move has a narrative reason, a duration, and an easing. Static tripod shots need composition (rule of thirds, leading space).
9. **Preview before delivery.** Render/inspect the first, middle, and last frame before committing to a full render. For Three.js, use deterministic still mode (`?still=1&t=…`). For Blender, render one lookdev frame first.
10. **Audio is ±2 frames or it's wrong.** Sound sells animation. Every impact whooshes before it, thuds on it, and the mix peaks below −3 dBFS.

## 1. Workflow overview

Work in phases. Read the linked reference only when you reach that phase (this keeps context lean):

| Phase | What you do | Read |
|---|---|---|
| 0 · INTAKE | Ask subject, duration, resolution/fps, style, sound, output. Echo spec receipt. | `references/intake.md` |
| 1 · DIRECTION | Pick art style, lock palette + material + lighting recipe. | `references/art-styles.md` |
| 2 · STORYBOARD | Write a shot list + **timing sheet** (template below). Every event gets a frame range and a sound cue. | — |
| 3 · BUILD | Construct the scene on **Path A (Three.js)** or **Path B (Blender)** — decision table below. | `references/pipeline-threejs.md` or `references/pipeline-blender.md` |
| 4 · ANIMATE | Blocking → spline → polish. Apply the 12 principles, easing library, overlap, settle. | `references/animation-principles.md` |
| 5 · SOUND | Synthesize/mix style-matched SFX + music bed, sync to the timing sheet. | `references/sound-design.md` |
| 6 · QA | Run the gate checklist. Fix, re-preview, repeat until clean. | `references/qa-checklist.md` |
| 7 · DELIVER | Exact file (right container/resolution/duration) + a one-paragraph delivery note. | — |

**Timing sheet template** — fill this in before animating anything. It is your contract with yourself and the source of truth for sound sync:

```markdown
| # | Shot / Action                 | Start f | End f | Ease            | Sound cue          |
|---|-------------------------------|---------|-------|-----------------|--------------------|
| 1 | Title blob pops in            | 0       | 18    | easeOutBack     | pop + sparkle      |
| 2 | Blob anticipates (squash)     | 30      | 40    | easeInOutCubic  | — (silence is timing) |
| 3 | Blob jumps arc to button      | 40      | 62    | parabola        | whoosh at 40, thud at 62 |
| 4 | Button presses, UI panel rises| 62      | 84    | easeOutCubic    | pop                |
```

## 2. Path decision — Three.js or Blender?

Both paths are fully supported. Choose deliberately:

| Requirement / context | Path |
|---|---|
| Interactive web scene, scroll/landing hero, product viewer | **A · Three.js** |
| Procedural/stylized animation, loops for web, programmable motion graphics | **A · Three.js** |
| Video file output (MP4) from a stylized scene, fast iteration, no Blender install | **A · Three.js + headless frame capture** |
| Photorealism, PBR/HDRI quality, complex physics (cloth, rigid body sims), particles, volumetrics, long-form offline render | **B · Blender** |
| Claymation/stop-motion look with true depth-of-field and subsurface feel | **B · Blender** (or A with toon/clay shaders for speed) |
| Physics sim **and** a web embed | **B then A**: simulate/render in Blender, or export glTF and view in Three.js |

Start from `assets/templates/threejs-starter.html` (Path A) or `assets/templates/blender-starter.py` (Path B) — both are production-tested and encode the style/animation/QA rules. Then read the matching pipeline reference for the full toolbox.

## 3. Minimal viable deliverable

When the user says "just make something" or you need a fast win, ship this in one pass:

1. Intake defaults (8 s loop, 1920×1080 @ 30 fps, Puffy style, SFX + soft music bed, MP4).
2. One subject, one gag, one camera move. A puffy blob that anticipates, hops, lands squash, and settles already beats 90% of AI 3D output.
3. Build on the Three.js starter, animate from the timing sheet, add 4–6 sound cues from `sound-design.md`, run QA, deliver MP4 + the live HTML.

## 4. Art styles at a glance

Full recipes (palettes, exact material values, lighting rigs, motion + sound personalities, do/don't) live in `references/art-styles.md`. Summary:

| Style | Feel | Best for |
|---|---|---|
| **Puffy / Bubbly** | Soft-inflatable, zero sharp edges, pastel, squashy | Cute characters, kids content, friendly brands |
| **Claymation** | Matte clay, stop-motion 12 fps stepped | Whimsical shorts, indie-game vibes |
| **Low-poly Flat** | Faceted, flat-shaded, bold limited palette | Games, fast explainers, tech |
| **Voxel** | Grid-locked cubes, chunky cute | Retro/NFT-era charm, city builders |
| **Isometric Diorama** | Orthographic 45° tiny world | Architecture, SaaS heroes, maps |
| **Neon / Cyberpunk** | Dark + emissive + bloom, wet reflections | Music visuals, gaming, crypto |
| **Cel / Anime** | Toon shading, ink outlines, snappy smears | Action, anime tributes, comics |
| **Frosted Glass** | Translucent glass, studio light, premium | Product reveals, fintech, luxury |

## 5. Reference index

- `references/intake.md` — exact questions to ask, defaults matrix, spec receipt format.
- `references/art-styles.md` — 8 complete style bibles with parameters for both pipelines.
- `references/animation-principles.md` — the 12 principles operationalized, easing library (JS + Blender), timing charts, camera language, anti-pattern audit.
- `references/pipeline-threejs.md` — full Three.js production pipeline: renderer settings, lighting kit, timeline engine, video/GIF/PNG export (live + headless deterministic).
- `references/pipeline-blender.md` — headless `bpy` pipeline: modeling recipes, materials, lighting rigs, keyframe/easing control, Cycles/EEVEE render settings, MP4 output.
- `references/sound-design.md` — Web Audio synth kit (SFX from pure code), ffmpeg SFX/mix recipes, per-style sound palettes, loudness targets.
- `references/qa-checklist.md` — the delivery gate. Nothing ships until every line passes.
- `assets/templates/threejs-starter.html` — open in a browser and it runs: puffy scene, timeline engine, deterministic frame mode, WebM recorder.
- `assets/templates/blender-starter.py` — `blender -b -P blender-starter.py -- --secs 8` renders a finished animated MP4 headless.
- `examples/` — headless render scripts (Playwright frame capture + ffmpeg MP4/GIF assembly).
