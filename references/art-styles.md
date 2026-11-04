# Phase 1 — Art Direction: The 14 Style Bibles

Each style below is a complete production recipe: identity, palette, geometry rules, material values (Three.js **and** Blender), lighting, motion personality, and sound personality. Follow one bible exactly — consistency is what makes output look designed rather than assembled.

**Table of contents**
1. [Puffy / Bubbly](#1-puffy--bubbly-soft-inflatable) (the signature style — nothing sharp)
2. [Claymation](#2-claymation)
3. [Low-poly Flat](#3-low-poly-flat)
4. [Voxel](#4-voxel)
5. [Isometric Diorama](#5-isometric-diorama)
6. [Neon / Cyberpunk](#6-neon--cyberpunk)
7. [Cel / Anime](#7-cel--anime)
8. [Frosted Glass](#8-frosted-glass)
9. [Realistic PBR](#9-realistic-pbr)
10. [Cartoon Bold](#10-cartoon-bold)
11. [Retro PS1](#11-retro-ps1)
12. [Steampunk & Industrial](#12-steampunk--industrial)
13. [Dark Fantasy](#13-dark-fantasy)
14. [Minimal Flat](#14-minimal-flat)

Plus: [style chooser](#style-chooser), [consistency rules](#consistency-rules), [blending rule](#blending-rule).

> 🎨 **See them all rendered:** open `docs/style-lab/index.html` (or the live
> Style Lab on GitHub Pages) — the same subject art-directed 14 ways. Use it to
> show the user options during intake.

---

## 1. Puffy / Bubbly (Soft Inflatable)

**Identity:** Everything looks like it was inflated — balloons, marshmallows, squishy toys. **Zero sharp edges anywhere** is the law of this style: if an edge would cut foam, it's wrong.

**Palette (max 5 + background):**
`#FFADAD` blush · `#FFD6A5` peach · `#FDFFB6` butter · `#B7E4C7` mint · `#A3C9F9` sky · background `#FFF6EC` cream · accent `#E8639B` berry (use sparingly)

**Geometry rules:**
- Allowed primitives: spheres, squashed spheres, capsules, rounded boxes. Forbidden: cubes with sharp edges, cones, pyramids, planes with visible corners.
- **Three.js:** `RoundedBoxGeometry(w, h, d, 6, radius)` with radius ≥ 15% of the smallest side; `CapsuleGeometry`; high-segment spheres (48×32).
- **Blender:** Bevel modifier (width 30% of edge, 6 segments) + Subdivision Surface level 2 viewport / 3 render on *everything*, then Shade Smooth.
- Eyes are spheres (never flat discs): white sphere + smaller dark pupil, placed **60% up the head**, never centered — this one detail reads "character designer was here".
- Cheeks: two flattened pastel spheres, opacity ~0.7, slightly wider than tall.

**Materials:**
| Param | Three.js `MeshPhysicalMaterial` | Blender Principled BSDF |
|---|---|---|
| Roughness | 0.40–0.48 | Roughness 0.42 |
| Clearcoat | 0.5, clearcoatRoughness 0.5 | Coat Weight 0.25, Coat Roughness 0.5 |
| Sheen | 0.4, white | Sheen Weight 0.6 |
| Specular | default | Specular IOR Level 0.4 |

**Lighting (soft-box rig):** Hemisphere (`#FFF3E0` sky / `#FFD9E0` ground, 0.55) + warm white key (1.6, casts soft shadows, mapSize 2048) + cool fill (0.5, opposite side) + pink rim from behind (0.7). Blender: three Area lights (key 400 W size 3 m, fill 150 W size 4 m, rim 100 W size 2 m), World `#FFF6EC` strength 0.7. Tone mapping: ACES, exposure 1.10–1.15. **No hard shadows** — if a shadow edge is crisp, enlarge the light.

**Motion personality:** floaty and slow — idle periods 2–4 s, gentle ±5° body sway, everything breathes (scale Y 1 → 1.015), squash & stretch on every landing (see `animation-principles.md`), overshoot ~6%, hops feel like the moon (hang time). Easings: `easeOutBack`, `easeOutElastic`, soft `easeInOutCubic`.

**Sound personality:** soft pops, marimba/xylophone plucks, boings, tiny "pomf" landings, airy whooshes. Music bed: lo-fi or music-box, major key, ~90 BPM.

**Do:** round the clouds, round the trees, round the UI. **Don't:** any cone spikes, any unlit gray, any fast snappy move (breaks the squish illusion).

**Tell-tale pro details:** contact shadows slightly larger and softer than the object · ground is never a flat plane (use a rounded slab or mounds) · 2–3 tiny background floaters (mini spheres) for depth · loop-safe sine drift on clouds.

---

## 2. Claymation

**Identity:** Hand-molded clay, stop-motion charm. Slightly imperfect, matte, warm.

**Palette:** `#E8D5B7` bone · `#D98E73` terracotta · `#7A9E7E` sage · `#5B7C99` denim · `#C75146` brick · background `#F4EDE1` paper.

**Geometry:** Rounded forms but *not* inflated — bevel 15%, Subsurf 2. Add subtle surface noise (Blender: Noise Texture → Bump, scale 8, detail 4, strength 0.02) to sell the handmade feel. Fingerprints optional but delightful (very light noise displacement on hero objects).

**Materials:** Three.js `MeshStandardMaterial` roughness 0.85–0.95, flat sheen. Blender Principled: Roughness 0.9, Specular 0.2, no coat.

**Lighting:** One warm practical-feel key (as if a desk lamp: 3500 K, Area 300 W size 1.5 m, close), weak cool fill, background slightly brighter behind subject (vignette feel). Long soft shadows welcome.

**Motion personality:** **shoot on twos** — animate at 12 fps steps inside a 24/30 fps timeline (hold each pose 2–3 frames). Poses are snappy, holds are confident, moves are slightly rough. No motion blur (Blender: render Motion Blur OFF; Three.js: no trail effects). Occasional 1-frame jitter = charm, not bug.

**Sound:** tactile — clay squelches, taps, wooden clicks, paper rustle. Music: ukulele/glockenspiel, ~100 BPM. Include room tone (very quiet brown noise) for warmth.

**Do:** show the handmade (seams, slight asymmetry). **Don't:** smooth 60 fps interpolation (kills the stop-motion illusion), glossy materials.

---

## 3. Low-poly Flat

**Identity:** Clean faceted geometry, bold flat colors, no textures. Confidence through restraint.

**Palette (6 colors max):** `#264653` ink · `#2A9D8F` teal · `#E9C46A` sand · `#F4A259` orange · `#E76F51` coral · `#F8F9FA` white · background `#FDF6EC` or dark `#1B263B`.

**Geometry:** Actually low-poly — sphere segments 12×8, cylinders 8 sides, planes as triangles. **Flat shading is the style:** Three.js `flatShading: true`; Blender: Shade Smooth OFF (or Shade Auto Smooth with angle 40°). No bevels, no subsurf.

**Materials:** `MeshStandardMaterial` roughness 0.8, metalness 0, per-face color variation ±8% lightness on adjacent pieces (faceted landscapes need it). Blender: Principled Roughness 0.8.

**Lighting:** One strong directional "sun" at a low angle (15–30° elevation) for long graphic shadows, hemisphere at 0.4, no rim light. Shadows are part of the design — compose with them.

**Motion:** crisp and snappy — actions 0.3–0.6 s, `easeOutCubic`, confident holds, minimal follow-through. World moves in clean loops (water = plane vertices sine wave, windmill = constant rotation, the only legal linear motion).

**Sound:** plucky synth (Square/triangle leads), soft clicks, marimba arps. Music: chiptune-lite or clean house, 110–120 BPM.

**Do:** hard color-block shadows, dramatic sun angle. **Don't:** gradients between faces, glow, soft shadows (crisp or nothing).

---

## 4. Voxel

**Identity:** Everything built from unit cubes on a strict grid. Chunky, toy-like, readable.

**Palette:** `#EF476F` red · `#FFD166` yellow · `#06D6A0` green · `#118AB2` blue · `#073B4C` navy · background `#F7F7F5`.

**Geometry:** all boxes, grid-locked positions (multiples of the unit size). Three.js: `InstancedMesh` of `BoxGeometry(1,1,1)` (one draw call for thousands of cubes — non-negotiable for perf). Blender: cube + Array modifier, or build via script instancing a linked-duplicate mesh.

**Materials:** one material, vertex colors or per-instance color; roughness 0.7. Add baked-style AO: Three.js — darken cubes whose top face is covered (bake factor into instance color); Blender — Ambient Occlusion node → multiply into base.

**Lighting:** bright, even, toy-commercial: hemisphere 0.7 + sun 1.2 from up-left. Everything visible, few dark corners.

**Motion:** grid-snapped — objects move in 1-unit jumps with 2-frame holds (feels like stop-motion made of LEGO), or smooth constant slides. Characters turn in 90° steps. Jumps: instant anticipation frame, parabola, hard landing with 1-frame squash (scale 0.85 then restore).

**Sound:** clicks, snaps, toy sounds, 8-bit blips. Music: chiptune, 120–140 BPM.

**Do:** per-instance color jitter, big readable silhouettes. **Don't:** rounded anything, tiny sub-unit details.

---

## 5. Isometric Diorama

**Identity:** A tiny floating world seen from a fixed 45° angle, like a jewel-box model.

**Palette:** background `#F7F3E9`; land `#B8E0D2`; accents `#E76F51`, `#F4D35E`, `#EE964B`, `#3D405B`.

**Geometry:** a rounded slab (RoundedBox or beveled cube) as the island base, chunky mini-props at 1:20 "dollhouse" scale, softened edges everywhere (bevel 10–20%).

**Camera — the defining rule:** Orthographic. Three.js: `OrthographicCamera`, position at azimuth 45° and elevation ≈ 35.264° (`atan(1/√2)` — the true isometric angle): `cam.position.set(d, d*0.816, d); cam.lookAt(0,0,0)` with `zoom` fitted to content. Blender: orthographic lens, rotation `(55.3°, 0°, 45°)`. **The camera never orbits** (only micro-drift ≤1° allowed); the *world* animates inside the frozen frame.

**Materials/Lighting:** soft matte (roughness 0.6–0.8), sun from up-right at 40°, hemisphere fill 0.6, gentle AO. Tilt-shift feel: slight depth blur on far edge (Blender DOF with focus on center; Three.js: skip or postprocess bokeh — optional).

**Motion:** the scene is 90% still — ambient life only: smoke puffs (rising spheres, shrink out), flags (sine wave), water shimmer, tiny characters walking loops, blinking windows at "night". Micro-motion periods 2–6 s.

**Sound:** gentle ambient — birds, breeze, distant chatter, soft music box. This style is *quiet*; keep the mix −6 dB below other styles.

**Do:** add one animated "hero prop" (windmill, train, fountain) as the focal point. **Don't:** perspective camera, fast action, camera cuts.

---

## 6. Neon / Cyberpunk

**Identity:** Night city energy — black glass, glowing edges, wet reflections.

**Palette:** background `#05060F` · neon cyan `#00F5D4` · magenta `#F15BB5` · blue `#00BBF9` · purple `#9B5DE5` · yellow `#FEE440`. Rule: neon colors appear **only as emission**, never as diffuse surface color.

**Geometry:** sleek boxes, cylinders, antennas, floating rings; hard edges are *allowed and welcome* here (the one style with sharpness). Panel gaps and thin emissive strips sell "machine".

**Materials:** Three.js — base `MeshStandardMaterial` color `#0A0A12` roughness 0.35 metalness 0.8, plus emissive meshes (`emissive: neonColor, emissiveIntensity: 2–4`) and `UnrealBloomPass` (strength 0.9, radius 0.6, threshold 0.75). Blender — Principled: Base `#0A0A12`, Roughness 0.3, Metallic 0.8; emission via Emission shader strength 5–15; bloom via Compositor Glare (Fog Glow, size 7, threshold 1.0) or EEVEE bloom.

**Lighting:** almost no white light. World black strength 0.1; key = large colored area (cyan) from one side, magenta counter from behind; wet floor = glossy dark plane (roughness 0.1) whose "reflection" in Three.js can be faked with a mirrored duplicate of emissive geometry at 15% opacity under the floor line.

**Motion:** constant subtle drift, pulsing emission (`intensity = 3 + 1.5*sin(2π*1.5*t)`), fast glints (1-frame flashes on rotating surfaces), slow hover bob. Camera: confident slow push-ins, occasional whip pan (3–5 frames, with motion blur).

**Sound:** synthwave — analog saw pads, bass pulses on the beat, risers, tape stops. UI: digital blips. Mix brighter and louder than other styles (−14 LUFS ok).

**Do:** fog (`scene.fog` dark blue, near 10 far 60) for depth. **Don't:** pure white lights, daylight, pastel anything.

---

## 7. Cel / Anime

**Identity:** 2D anime logic on 3D bodies — flat color bands, ink lines, snappy timing.

**Palette:** ink `#1A1A1A` · skin `#FFE0C7` · hair `#3B2F4E` (any), shadow band = base color × 0.72 lightness, highlight band = base × 1.25. Two bands only — no soft gradients.

**Shading (the whole style is here):**
- Three.js: `MeshToonMaterial` with a 3-step gradientMap (make a 3×1 DataTexture: 0.35, 0.8, 1.0, `NearestFilter`). Outlines: inverted-hull — duplicate mesh, `BackSide` black material, scale 1.03–1.05 (tune per object size).
- Blender: Shader to RGB → Color Ramp (2 stops) → ink via Solidify+Backface or Freestyle.

**Lighting:** one strong sun (the ramp does the work), white/colored background flats, rim highlight allowed as a hard white band.

**Motion:** the most *snappy* style — 3–6 frame anticipation, 2–3 frame action (with a **smear**: scale the mesh 3× along motion for 1–2 frames, or add afterimage trails), hard stops into 4–8 frame holds. Big silhouettes: exaggerate poses 20% past natural. Impact frames: 1–2 frames of inverted/white flash on hits.

**Sound:** orchestral-pop hits, taiko for impacts, "shing" for reveals, character vocal blips. Music: dramatic, tempo changes allowed — sync cuts to beats.

**Do:** speed lines (flat white wedges), dust puffs on landings (flat spheres shrinking). **Don't:** soft shadows, PBR gloss, slow floaty motion.

---

## 8. Frosted Glass

**Identity:** Premium studio product film — frosted glass forms, clean light, breaths of color.

**Palette:** background gradient `#EAF6FF` → `#FFFFFF` · glass neutral · accent `#7FD8FF` · text `#12283A`.

**Geometry:** smooth rounded solids (squashed spheres, rounded slabs, torus), large simple forms; nothing fiddly.

**Materials:**
- Three.js: `MeshPhysicalMaterial { transmission: 1, thickness: 1.5, ior: 1.45, roughness: 0.08–0.35, clearcoat: 0.6 }` + `scene.environment` from `RoomEnvironment` (this style *requires* an environment map — glass is black without it).
- Blender: Principled — Transmission Weight 1.0, IOR 1.45, Roughness 0.1, Base `#FFFFFF`, thin walls for the frosted look; Cycles with 256+ samples (noise in glass is unforgivable).

**Lighting:** big soft studio — two huge area lights (white) + gradient world; one colored accent light behind the hero object for a rim glow through the frost.

**Motion:** showcase turntables (constant rotation is legal here), slow rise-in with `easeOutCubic`, parts assembling with 0.4 s `easeOutBack` moves and 4-frame settle. Everything unhurried.

**Sound:** airy pads, glass "ping" (high sine 2–4 kHz with fast decay), soft clicks. Music: minimal piano/ambient, 70–90 BPM.

**Do:** gradient background via large soft world, subtle camera height drift. **Don't:** busy scenes, dark backgrounds, hard shadows (keep them faint, `#DCE9F5`-ish).

---

## 9. Realistic PBR

**Identity:** Believable materials, film-grade light. Nothing cartoonish; the camera behaves like a real lens.

**Palette (muted, value-structured):** `#DDE5EC` sky-fill · `#9AA8B0` concrete · `#6F8F6A` foliage · `#5D4A38` wood · `#E8E2D6` ceramic/cloth · accent **one** saturated color max (e.g. `#C25B4E`) used on ≤10% of surfaces.

**Geometry:** real-world proportions, bevels 1–3 mm on every hard edge (micro-bevel catches highlights and reads "manufactured"), high-res silhouettes on hero objects only; never spend polygons where the camera won't look.

**Materials (the style lives here):**
- Three.js: `MeshPhysicalMaterial` with per-part roughness maps via `roughness: 0.35–0.8`; metals `metalness 1.0 + roughness 0.25`; always `scene.environment` (RoomEnvironment or an HDRI via `RGBELoader`) — PBR without an env map is dead plastic. ACES tone mapping, exposure 1.0–1.1.
- Blender: Principled BSDF with believable values (dielectric Roughness 0.3–0.6, Metallic 0/1 — never 0.5), Cycles 128–512 samples with OpenImageDenoise, Filmic/AgX view transform.

**Lighting:** one dominant motivated source (sun through window, practical lamp) + HDRI fill; shadows are soft-edged but present; rim/separation light at 10–20% of key. Blender: 3-area studio for product, sun+sky for exterior.

**Camera:** 35–85 mm equivalents, shallow DOF only when it isolates subject, handheld micro-shake (±0.15° noise) for doc feel, locked-off tripod for product.

**Motion:** ease everything, but *restrained* — overshoot ≤3%, no cartoony squash. Simulations (cloth, rigid body, fluid) belong here.

**Sound:** sub-bass room tone, foley-realistic impacts, no musical stingers unless asked. Ambience > music.

**Do:** contact shadows, subtle surface variation (noise bump), color-grade in post. **Don't:** 100% saturated albedo, mirror-sharp everything, pastel backgrounds.

---

## 10. Cartoon Bold

**Identity:** Saturday-morning energy — saturated primaries, thick ink outlines, big shapes, confident exaggeration.

**Palette:** `#FF6B6B` red · `#FFD93D` yellow · `#4ECDC4` teal · `#1A535C` deep teal · `#F7FFF7` white · background `#FFEC99` or `#D4F1F4`.

**Geometry:** rounded silhouettes with a few BIG shapes (a nose, a backpack, a fist) — scale contrast > detail count. `RoundedBoxGeometry` + spheres; bevel generous (15–20%).

**Materials:** Three.js `MeshStandardMaterial` roughness 0.55–0.7 (soft matte, *slight* gloss on eyes) + **inverted-hull outlines**: duplicate mesh, `BackSide`, black, scale 1.05–1.07 (bigger for small parts). Blender: Freestyle lines (thickness 3–5 px) or Solidify+Backface.

**Lighting:** bright, even, cheerful — hemisphere 0.7 + key 1.3; shadows stay light (opacity feel). No moody rim lights.

**Motion:** the most expressive style — overshoot 8–12%, anticipation 4–8 frames, occasional 2-frame holds at pose extremes, head-tilts ±15°. Everything reacts: eyebrows, ears, antennae get their own follow-through layer.

**Sound:** comedic woodblock, kazoo/brass stings, slide whistle for jumps, big boingy impacts. Music: bright ukulele/pop, 110–130 BPM.

**Do:** smear frames on fast moves (scale 3× along motion for 1–2 frames), colored outlines (dark of the fill) instead of pure black for softer casts. **Don't:** realistic textures, muted colors, slow floaty pacing.

---

## 11. Retro PS1

**Identity:** 1998 3D — low polygons, vertex-lit look, fog, chunky pixels. Nostalgia with teeth.

**Palette:** desaturated darks: `#23233A` night · `#3E6D64` teal shadow · `#9C5B4E` rust · `#C8B896` bone · `#6A5D7A` dusk purple. Background: near-black `#14141F`.

**Geometry:** brutal budget — spheres 8×6 segments, boxes, no smooth curves; jitter vertices ±2% for hand-placed wobble. No bevels, no subsurf.

**Materials:** Three.js `MeshLambertMaterial` (vertex-lit look — no specular) or `MeshBasicMaterial` for unlit props; `flatShading: true`. **Pixelation is the fingerprint:** render at 1/3 resolution and upscale with `image-rendering: pixelated` (or Blender: render 640×480, nearest-neighbor upscale). Affine texture warp is optional authenticity (skip unless committed).

**Lighting:** one hard sun or point light + heavy distance fog (`Fog(bg, 6, 26)`) — fog IS the atmosphere. Everything at the edges dissolves.

**Motion:** stiff, 15–20 fps feel; snap turns in 90° steps; camera cuts hard (no smooth orbits); tank-like character turns.

**Sound:** lo-fi drum machine, PS1 startup-style pads, vinyl hiss, low-res UI blips. Music: dark ambient or jungle, 130–160 BPM.

**Do:** dithered gradients, CRT vignette overlay, chunky UI text. **Don't:** smooth shading, high-poly anything, bright daylight.

---

## 12. Steampunk & Industrial

**Identity:** brass, copper, rivets, steam — Victorian machinery with warm workshop light.

**Palette:** `#B08D57` brass · `#8C5A3C` copper · `#5A3E26` dark wood · `#2B1D12` background · `#7C8B3F` oxidized brass · glow `#FFB347` (furnace, lamps).

**Geometry:** cylinders + tori (pipes, boilers, gears), riveted plates (small spheres along seams), gauges (cylinder + emissive dial). High metalness everywhere structural.

**Materials:** Three.js `MeshStandardMaterial` `metalness 0.85, roughness 0.35–0.5`, with `envMap` (needed for metal); wood parts roughness 0.8 metalness 0. Blender: Metallic 0.9/Roughness 0.4 + Noise Texture bump for grime.

**Lighting:** warm workshop — key `#FFC98A`, strong orange practicals (furnaces, bulbs) as emissive + PointLights, dust motes (tiny emissive spheres drifting) sell the air. World `#2B1D12` strength 0.3.

**Motion:** mechanical logic — gears rotate at linked ratios, pistons stroke, steam puffs (spheres growing + fading), everything with satisfying clunks. Easing: constant rotation for machines, eased otherwise.

**Sound:** hiss, clank, ratchet clicks, creaking wood, low boiler rumble. Music: industrial folk, accordion or cello, 90–110 BPM.

**Do:** show the mechanism working (a gear that turns for no reason is set dressing; one that drives something is a story). **Don't:** clean shiny metal (add roughness variation), cool white light.

---

## 13. Dark Fantasy

**Identity:** mist, stone, cold light, weight. Souls-like gravity — every move costs something.

**Palette:** `#14161D` background · `#2E3440` stone · `#5A6478` armor slate · `#3B4252` iron · rim `#7FD8FF` cold moonlight · ember accent `#D08770` (candles, forge).

**Geometry:** heavy silhouettes, tall proportions, layered cloth/armor masses; keep silhouettes readable against fog.

**Materials:** low saturation, roughness 0.6–0.8, metalness only on weapons/armor (0.8 + roughness 0.45). Cloth: sheen 0.3. Stone: subtle noise bump.

**Lighting:** near-darkness + motivated pools: one cold rim (the defining look), warm ember points, volumetric-feel via dense fog (`Fog(#14161D, 7, 30)`). Blender: Cycles + volume scatter for god rays.

**Motion:** slow, deliberate, weighted — anticipation doubled, overshoot nearly zero, cape/cloth lags with big offsets. Camera: slow push-ins, long holds, subtle drift; never whip.

**Sound:** distant bells, wind, creaking leather, deep drums, sparse choir. Silence is a tool — leave 2–3 s of it after reveals.

**Do:** negative space, one hero light source per shot, particles (ash/embers/dust). **Don't:** bright fills, pastel anything, fast comedic timing.

---

## 14. Minimal Flat

**Identity:** vector-poster 3D — unlit flat colors, clean shapes, Swiss composition. Information first.

**Palette (4–5):** `#FFFFFF` background · `#FF6B6B` · `#4ECDC4` · `#45B7D1` · `#2B2D42` text/ink.

**Geometry:** primitives with almost no detail; axis-aligned compositions; consistent corner radius everywhere (pick one radius, use it for every rounded edge).

**Materials:** Three.js `MeshBasicMaterial` (truly flat) or `MeshStandardMaterial + hemisphere only` for the faintest form; **no shadows** (or a single flat-color ellipse under the subject). Blender: Emission shader at 1.0 + color ramp — or EEVEE with zero specular.

**Lighting:** none in the photographic sense — light IS the material color. If form is needed, add one hemisphere light at 0.8 max.

**Motion:** informative — slide/fade/pulse with `easeOutCubic`; objects arrive on the beat grid (every move lands on a multiple of the BPM); nothing bounces.

**Sound:** soft UI ticks, single piano notes on reveals, no ambience. Music: minimal piano/marimba, 80–100 BPM, mixed LOW.

**Do:** generous negative space, one accent color per scene, typographic integration (3D + HTML overlays). **Don't:** gradients, textures, glow, realistic materials.

---

## Style chooser

| User says / context | Pick |
|---|---|
| "cute", "fluffy", "puffy", "bubbly", "kids", "kawaii", "nothing sharp" | **Puffy / Bubbly** |
| "handmade", "stop motion", "clay", "Aardman" | **Claymation** |
| "game", "fast", "minimal", "polygon" | **Low-poly Flat** |
| "Minecraft", "retro", "blocky", "voxel" | **Voxel** |
| "isometric", "diorama", "tiny world", "map", "city" | **Isometric Diorama** |
| "neon", "cyberpunk", "gamer", "night", "Tron", "music" | **Neon / Cyberpunk** |
| "anime", "cartoon", "comic", "Dragon Ball" | **Cel / Anime** |
| "premium", "product", "apple-style", "glass", "clean" | **Frosted Glass** |
| "realistic", "photoreal", "film", "archviz", "simulation" | **Realistic PBR** |
| "pixar"-adjacent, "bold", "vibrant", "toy commercial", " kids TV" | **Cartoon Bold** |
| "PS1", "PSX", "90s 3D", "horror retro", "haunted PS1 game" | **Retro PS1** |
| "steampunk", "brass", "victorian", "industrial", "gears", "factory" | **Steampunk & Industrial** |
| "dark fantasy", "moody", "gothic", "souls-like", "mist" | **Dark Fantasy** |
| "flat", "corporate", "infographic", "swiss", "vector look" | **Minimal Flat** |
| Brand colors provided | Nearest style, then swap palette (keep value structure: light bg ↔ dark bg) |

## Consistency rules

1. **Lock the bible at Phase 1**: write the palette hexes, material values, and light rig into your scene config at the top of the file. Every object is created through the style's material helper — no inline raw materials.
2. Background, fog, and ground must come from the same palette family.
3. Shadow character must match style: soft (Puffy/Clay/Glass) vs crisp (Low-poly/Voxel/Cel) vs colored (Neon).
4. Motion personality is part of the style — a Neon scene with floaty Puffy motion feels haunted, not cool.

## Blending rule

Allowed: pick one **primary** style and borrow *at most* the motion personality or the sound palette from a second. Never mix palettes or geometry rules. State the blend in the spec receipt: "Puffy primary + Claymation stepped timing".
