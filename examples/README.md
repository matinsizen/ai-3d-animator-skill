# 📐 Example Model Library

Five complete, production-tested example models — each built **twice**: as a
Three.js ES module (Path A) and as a headless Blender Python script (Path B).
No external assets; every vertex is code. Agents: **copy these patterns, don't
reinvent them** — they encode every rule of the skill (pivots, loop-safety,
easing, style bibles).

| Model | Path A (Three.js) | Path B (Blender) | Style | Shows off |
|---|---|---|---|---|
| 🧍 **Milo**, stylized human | [`threejs-human.js`](human-character/threejs-human.js) | [`blender-human.py`](human-character/blender-human.py) | Puffy | joint rig, walk/idle/wave, counter-rotation |
| 🐱 **Mochi**, puffy cat | [`threejs-cat.js`](fluffy-cat/threejs-cat.js) | [`blender-cat.py`](fluffy-cat/blender-cat.py) | Puffy | zero sharp edges, squash & stretch, overlap |
| ✈️ **Swift**, jet fighter | [`threejs-jet.js`](jet-fighter/threejs-jet.js) | [`blender-jet.py`](jet-fighter/blender-jet.py) | Low-poly | lathe + extrude surfaces, banked flight, chase cam |
| 🤖 **Bolt**, toy mech | [`threejs-robot.js`](robot-mech/threejs-robot.js) | [`blender-robot.py`](robot-mech/blender-robot.py) | Toy + Neon | rounded boxes, weight walk, emissive accents |
| 🚗 **Jelly**, city car | [`threejs-car.js`](sports-car/threejs-car.js) | [`blender-car.py`](sports-car/blender-car.py) | Product | profile-extrude body, arches, turntable, wheel spin |

**Live demos (GitHub Pages):** [gallery](https://matinsizen.github.io/ai-3d-animator-skill/) ·
[human](https://matinsizen.github.io/ai-3d-animator-skill/demos/human/) ·
[cat](https://matinsizen.github.io/ai-3d-animator-skill/demos/cat/) ·
[jet](https://matinsizen.github.io/ai-3d-animator-skill/demos/jet/) ·
[robot](https://matinsizen.github.io/ai-3d-animator-skill/demos/robot/) ·
[car](https://matinsizen.github.io/ai-3d-animator-skill/demos/car/) ·
[style lab (14 styles)](https://matinsizen.github.io/ai-3d-animator-skill/style-lab/)

## Module contract (Path A)

Every `threejs-*.js` is a self-contained ES module with the same interface:

```js
import { buildHuman, animateHuman, INFO } from './threejs-human.js';

const rig = buildHuman();          // returns { group, parts… } — add rig.group to your scene
animateHuman(rig, t, { loop: 8, mode: 'walk' });   // pure function of t → seek anywhere, loops perfectly
INFO.cam                            // recommended camera { fov, position, target } or 'chase'
INFO.loop / INFO.modes / INFO.mode  // loop length & animation modes
```

Demos in `docs/demos/` wire this up with OrbitControls, a soft light rig, a
ground slab, and the headless render contract (`?still=1&t=SEC&res=WxH`).

## Script contract (Path B)

Every `blender-*.py` is a single-file scene that runs headless:

```bash
blender -b -P <script>.py -- --mode walk --secs 8 --fps 30 --res 1920x1080 --render
```

Same structure inside: clean scene → materials → model → lights → camera →
keyframes (with `CYCLES` modifiers for perfect loops) → MP4 output settings.

## Render utilities

- [`render-frames.mjs`](../examples/render-frames.mjs) — deterministic headless frame capture (Playwright)
- [`assemble-video.sh`](../examples/assemble-video.sh) — ffmpeg MP4 + GIF assembly
- [`screenshot.mjs`](../scripts/screenshot.mjs) — single-frame still capture
