# Path A — Three.js Production Pipeline

Real-time, programmatic, web-native. Best for interactive scenes, loops, motion graphics, and fast iteration. Everything below targets **three r160+** via ES modules and import maps (no build step — a single HTML file runs everywhere).

**Table of contents**
1. [File skeleton](#1-file-skeleton) · 2. [Renderer & color](#2-renderer--color) · 3. [Geometry kit](#3-geometry-kit) · 4. [Lighting kit](#4-lighting-kit) · 5. [Timeline engine](#5-timeline-engine-stateless--loop-safe) · 6. [Camera rigs](#6-camera-rigs) · 7. [Export: video, GIF, stills](#7-export-video-gif-stills) · 8. [Headless deterministic rendering](#8-headless-deterministic-rendering) · 9. [Performance & errors](#9-performance--common-errors)

---

## 1. File skeleton

Copy `assets/templates/threejs-starter.html` — it contains all of the below, pre-wired, in one file. The non-negotiable structure:

```html
<!doctype html><html><head><meta charset="utf-8">
<script type="importmap">
{ "imports": {
    "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
}}
</script>
</head><body>
<script type="module">
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
// SPEC → renderer → scene → lights → build → pose(t) → loop/export
</script></body></html>
```

Pin the version. Never use non-module builds. Addons you'll actually use: `RoundedBoxGeometry`, `RoomEnvironment`, `OrbitControls` (debug only), `EffectComposer`+`UnrealBloomPass` (Neon), `BokehPass` (close-ups).

## 2. Renderer & color

```js
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));   // cap DPR: crisp + fast
renderer.setSize(SPEC.width, SPEC.height);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;      // filmic roll-off; default NoToneMapping looks cheap
renderer.toneMappingExposure = 1.12;
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
scene.background = new THREE.Color('#FFF6EC');           // from the style bible
scene.fog = new THREE.Fog('#FFF6EC', 18, 42);            // fog color == bg color (seamless depth)

const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;  // image-based light for sheen
```

`preserveDrawingBuffer: true` is required for screenshots/`toDataURL`. Fog + matching background is the cheapest "cinematic depth" trick that exists — use it in every outdoor scene.

## 3. Geometry kit

| Need | Use |
|---|---|
| Rounded slab / box | `new RoundedBoxGeometry(w, h, d, 6, radius)` — radius ≥ 15% min side (Puffy), 5–10% (others) |
| Squishy character body | `SphereGeometry(r, 48, 32)` scaled by `squash()` |
| Pills / limbs / trunks | `CapsuleGeometry(radius, length, 8, 24)` |
| Clouds / bushes | 3–5 overlapping spheres in a `Group` |
| Many cubes (Voxel) | `InstancedMesh` — one draw call, per-instance color via `setColorAt` |
| Flat ground shadow catcher | `ShadowMaterial({ opacity: 0.18 })` on a big plane |

Set `castShadow = true` on actors, `receiveShadow = true` on ground. Always.

## 4. Lighting kit

```js
// Soft rig (Puffy/Clay/Glass/Isometric) — three-point + hemi
scene.add(new THREE.HemisphereLight('#FFF3E0', '#FFD9E0', 0.55));
const key = new THREE.DirectionalLight('#FFFFFF', 1.6);
key.position.set(6, 9, 6);
key.castShadow = true;
key.shadow.mapSize.set(2048, 2048);
Object.assign(key.shadow.camera, { left: -11, right: 11, top: 11, bottom: -11, near: 1, far: 40 });
key.shadow.bias = -0.0002;            // kills shadow acne without peter-panning
key.shadow.normalBias = 0.02;
scene.add(key);
scene.add(Object.assign(new THREE.DirectionalLight('#CFE3FF', 0.5), { position: new THREE.Vector3(-7, 4, -2) }));
scene.add(Object.assign(new THREE.DirectionalLight('#FFD1DC', 0.7), { position: new THREE.Vector3(-2, 6, -8) }));
```

Shadow frustum must tightly wrap the action — a 2048 map over a 100-unit area is blurry mush. Dramatic/Neon rig: drop hemisphere to 0.05, use two colored directional/point lights + emissives (see art-styles §6).

## 5. Timeline engine — stateless & loop-safe

The starter ships a tiny pattern that is *deterministic* (same t ⇒ same frame, essential for headless rendering and loops). Compose every pose from pure functions of time:

```js
const clamp01 = x => Math.min(1, Math.max(0, x));
const seg = (t, a, b, e = easeInOutCubic) => b > a ? e(clamp01((t - a) / (b - a))) : 1; // progress 0..1 inside [a,b]
const lerp = (a, b, p) => a + (b - a) * p;

function pose(t) {                 // t = loop-local seconds ∈ [0, LOOP)
  // breathing (loop-safe: period divides LOOP)
  for (const b of blobs) {
    const s = 1 + 0.015 * Math.sin(2 * Math.PI * t / 2 + b.phase);
    squash(b.body, s);
  }
  // one-shot gag inside the loop (ends settled → seam is invisible)
  const p2 = seg(t, 0.75, 1.35, x => x);                  // flight, linear-in-parabola
  blobA.g.position.y = 0.9 + 2.4 * Math.sin(Math.PI * p2);
  squash(blobA.body, 1 + 0.22 * Math.sin(Math.PI * p2) - 0.22 * seg(t, 0.5, 0.75) + 0);
  // camera: gentle drift, all sines with period == LOOP
  const az = 0.10 * Math.sin(2 * Math.PI * t / LOOP);
  const r  = 17 + 0.35 * Math.sin(2 * Math.PI * t / LOOP + Math.PI / 2);
  camera.position.setFromSpherical(new THREE.Spherical(r, Math.PI / 2 - 0.34, az)).add(TARGET);
  camera.lookAt(TARGET);
}
```

Rules that keep it professional:

- **One-shot gags must end settled** before the loop wraps (last key ≥ 0.3 s before the seam).
- **All continuous motion = sines whose period divides LOOP** — this is the entire secret to invisible loop seams.
- Every visual property is set from scratch inside `pose(t)` (stateless). No incremental state, no `+=` in the render loop — that's how loops break.
- Expose a `TUNE` object (`{ speed: 1, squash: 1, cameraDrift: 1 }`) so the scene is re-tunable without touching logic.

## 6. Camera rigs

```js
const TARGET = new THREE.Vector3(0, 0.9, 0);
function orbitCam(t, { r = 17, el = 0.34, az = 0, drift = 1 } = {}) {
  camera.position.setFromSpherical(new THREE.Spherical(
    r * (1 + 0.02 * Math.sin(2 * Math.PI * t / LOOP) * drift),
    Math.PI / 2 - el,
    az + 0.10 * Math.sin(2 * Math.PI * t / LOOP) * drift
  )).add(TARGET);
  camera.lookAt(TARGET);
}
```

- Push-in = animate `r` with `seg(t, 0, 3.5, easeInOutQuint)` × −10%.
- Follow = `spring()` per axis toward the subject (animation-principles §3).
- Debug with `OrbitControls` behind `?debug=1`; never ship it as the animation.

## 7. Export: video, GIF, stills

**WebM in-browser (live path, includes audio):**

```js
const stream = renderer.domElement.captureStream(SPEC.fps);
const recDest = audioCtx.createMediaStreamDestination();     // sound-design.md kit
masterGain.connect(recDest);
recDest.stream.getAudioTracks().forEach(t => stream.addTrack(t));
const rec = new MediaRecorder(stream, { mimeType: 'video/webm;codecs=vp9', videoBitsPerSecond: 12_000_000 });
rec.ondataavailable = e => chunks.push(e.data);
rec.onstop = () => download(new Blob(chunks, { type: 'video/webm' }), 'scene.webm');
rec.start(); /* let the timeline play exactly SPEC.loop seconds */ setTimeout(() => rec.stop(), SPEC.loop * 1000);
```

Convert WebM → MP4: `ffmpeg -i scene.webm -c:v libx264 -crf 17 -pix_fmt yuv420p -movflags +faststart scene.mp4`.

**Deterministic frames → MP4/GIF (highest quality, reproducible):** see §8.

**PNG stills:** `renderer.render(scene, camera); renderer.domElement.toDataURL('image/png')`.

## 8. Headless deterministic rendering

For guaranteed-framerate, perfect-resolution MP4/GIF from a Three.js scene (no real-time capture dropped frames):

1. Scene must implement `window.__seek(t)` (the starter does): sets loop-time `t`, runs `pose(t)`, renders once.
2. `examples/render-frames.mjs` (Playwright, SwiftShader WebGL) captures every frame:

```bash
npm i -D playwright && npx playwright install chromium --with-deps
node examples/render-frames.mjs ./scene.html --w 1920 --h 1080 --fps 30 --secs 8
bash examples/assemble-video.sh frames out.mp4 --gif preview.gif
```

3. `assemble-video.sh` = `ffmpeg -framerate 30 -i frames/f%04d.png -c:v libx264 -crf 17 -pix_fmt yuv420p -movflags +faststart out.mp4` (+ palettegen GIF path).

Flags that make headless WebGL work: launch Chromium with `--enable-unsafe-swiftshader` (software GL). If textures/CORS bite on `file://`, serve with `python3 -m http.server` and load `http://localhost:8000/scene.html`.

## 9. Performance & common errors

- One material per color (reuse), merge static geometry (`BufferGeometryUtils.mergeGeometries`), `InstancedMesh` for repeats. 60 fps @ 1080p should be trivial for stylized scenes.
- `dispose()` geometries/materials if you rebuild scenes at runtime.
- Resize: update `camera.aspect` + `renderer.setSize`.

| Symptom | Cause → fix |
|---|---|
| Black screen headless | No GL context → launch flag `--enable-unsafe-swiftshader` |
| Textures washed out | Wrong colorspace → `tex.colorSpace = THREE.SRGBColorSpace` |
| Shadow stripes on ground | shadow acne → `shadow.bias = -0.0002` + `normalBias 0.02` |
| Loop "hiccups" once | stateful `+=` in render loop → make `pose(t)` stateless |
| Everything looks gray/flat | No env map / no tone mapping → §2 |
| Bloom makes gray mush | threshold too low → 0.75+, strength ≤ 1.0 |
| GIF is 40 MB | 30 fps full-res → render GIF at 10–12 fps, 480–640 px, palettegen |
