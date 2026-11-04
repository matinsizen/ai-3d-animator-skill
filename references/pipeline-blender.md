# Path B — Blender Production Pipeline (headless bpy)

Offline renderer for photorealism, real physics, and delivery-grade video files. Everything is scripted with `bpy` and runs headless — no GUI, no display server needed:

```bash
blender -b -P scene.py -- --res 1920x1080 --fps 30 --secs 8 --out ./out.mp4 --samples 96
#            └ everything after `--` is passed to your script
```

Works with Blender **3.6 LTS through 4.5** (the material helper below maps renamed inputs across versions). Prefer the Cycles renderer in headless — EEVEE needs a GPU/OpenGL context that often doesn't exist on render servers.

**Table of contents**
1. [Script skeleton](#1-script-skeleton) · 2. [Scene & modeling recipes](#2-scene--modeling-recipes) · 3. [Materials](#3-materials) · 4. [Lighting rigs](#4-lighting-rigs) · 5. [Camera](#5-camera) · 6. [Animation & easing control](#6-animation--easing-control) · 7. [Physics quick wins](#7-physics-quick-wins) · 8. [Render settings & MP4](#8-render-settings--mp4) · 9. [Lookdev protocol](#9-lookdev-protocol--iteration) · 10. [Error table](#10-common-background-mode-errors)

---

## 1. Script skeleton

`assets/templates/blender-starter.py` is a complete working example. Structure every scene script like it:

```python
import bpy, sys, math, argparse

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
p = argparse.ArgumentParser()
p.add_argument('--res', default='1920x1080'); p.add_argument('--fps', type=int, default=30)
p.add_argument('--secs', type=float, default=8.0); p.add_argument('--samples', type=int, default=96)
p.add_argument('--still', type=int, default=-1, help='render single frame N as PNG (lookdev)')
p.add_argument('--out', default='./out.mp4')
a = p.parse_args(argv)

bpy.ops.wm.read_factory_settings(use_empty=True)   # deterministic start, no default cube
S = bpy.context.scene
```

Read the intake spec from CLI args — never hardcode user requirements.

## 2. Scene & modeling recipes

```python
def srgb(hexstr):                                  # hex → linear RGB (Blender colors are linear!)
    h = hexstr.lstrip('#'); c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    return [((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92 for c in c]
```

**Puffy (rounded-everything):** UV sphere (48 seg) / capsule; for boxes: Bevel modifier (`width ≈ 30%` of edge, `segments 6`, limit ANGLE) **then** Subdivision (`levels 2`, `render_levels 3`), then Shade Smooth. Bevel-before-subsurf order is what makes the pillowy silhouette.

**Clay:** bevel 15%, subsurf 2, plus Noise Texture → Bump (scale 8, detail 4, strength 0.02).

**Low-poly:** 8–12 segment primitives, `shade_smooth()` **off** (flat facets are the style), no bevel/subsurf.

**Voxel:** one cube object + `Array` modifiers (X/Y/Z counts), or link-duplicate a cube data-mesh in a loop for full control; join into one mesh for render speed.

**Isometric diorama:** rounded slab island + miniature props; keep everything within a tight radius so the ortho frame is full.

Cleanup habit: link objects into a dedicated collection per role (`lights`, `actors`, `set`) — trivial via `bpy.data.collections.new` + `bpy.context.scene.collection.children.link`.

## 3. Materials

Principled BSDF input names changed in Blender 4.0 — always set through a guarded helper (from the starter):

```python
def set_input(node, names, value):
    for n in names:
        if n in node.inputs:
            node.inputs[n].default_value = value; return
    # names is an ordered list of version aliases, e.g. ('Coat Weight','Clearcoat')
```

| Style | Inputs (4.x name → 3.x alias) |
|---|---|
| Puffy | Base Color pastel · Roughness 0.42 · **Sheen Weight 0.6** · **Coat Weight 0.25** (3.x: Clearcoat) · Coat Roughness 0.5 |
| Clay | Roughness 0.9 · Specular IOR Level 0.2 (3.x: Specular) · bump noise |
| Low-poly | Roughness 0.8 · flat shading (material-independent) |
| Voxel | Roughness 0.7 · per-instance color via object color or vertex colors |
| Neon | Base `#0A0A12` · Metallic 0.8 · Roughness 0.3 · separate **Emission** shader strength 5–15 |
| Glass | Transmission Weight 1.0 (3.x: Transmission) · IOR 1.45 · Roughness 0.1 · needs Cycles 256+ samples |

## 4. Lighting rigs

```python
def area_light(name, loc, size, power, color=(1, 1, 1), target=None):
    d = bpy.data.lights.new(name, 'AREA'); d.energy = power; d.size = size; d.color = color
    o = bpy.data.objects.new(name, d); o.location = loc; bpy.context.collection.objects.link(o)
    if target:                                   # areas point down (-Z); track a target instead of guessing Euler angles
        t = target if isinstance(target, bpy.types.Object) else empty_at(target)
        c = o.constraints.new('TRACK_TO'); c.target = t; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
    return o

# Soft rig (Puffy/Clay):           # Dramatic rig (Neon/Cel):
area_light('key',  ( 5, -4, 7), 3.0, 400, srgb('#FFF1E0'))   # key colored
area_light('fill', (-6, -3, 4), 4.0, 150, srgb('#DCE8FF'))   # counter-color rim instead of fill
area_light('rim',  (-2,  6, 5), 2.0, 100, srgb('#FFD1DC'))
S.world = bpy.data.worlds.new('w'); S.world.use_nodes = True
bg = S.world.node_tree.nodes['Background']
bg.inputs[0].default_value = (*srgb('#FFF6EC'), 1); bg.inputs[1].default_value = 0.7   # 0.05 for Neon
```

Bigger light `size` = softer shadow. If shadows are still crisp, raise size and/or add the world background — that's the whole "softness" game.

## 5. Camera

```python
cd = bpy.data.cameras.new('cam'); cd.lens = 50; cd.sensor_width = 36
cd.dof.use_dof = True; cd.dof.aperture_fstop = 2.8; cd.dof.focus_distance = 6.0   # focus on subject eyes
cam = bpy.data.objects.new('cam', cd); bpy.context.collection.objects.link(cam); S.camera = cam
cam.location = (0, -17, 7.5); aim(cam, (0, 0, 1))     # track-to empty, like the lights
# push-in: key frames 1 → end, location.y -17 → -15.6, bezier auto-clamped
```

Z is up (Three.js muscle memory will betray you: "y" is depth here). Focal lengths: 35 wide / 50 neutral / 85 portrait.

## 6. Animation & easing control

Keyframe by setting the value then inserting:

```python
def key(obj, path, frame):
    obj.keyframe_insert(data_path=path, frame=frame)

# — hop with anticipation / squash / settle (frames for 30 fps) —
blob.location = (x, y, r);            key(blob, 'location', 15)
blob.scale    = (1.13, 1.13, 0.78);   key(blob, 'scale',    27)   # anticipation squash
blob.scale    = (0.95, 0.95, 1.10);   key(blob, 'scale',    33)   # stretch at takeoff
blob.location = (x, y, r + 2.4);      key(blob, 'location', 39)   # apex
blob.scale    = (0.88, 0.88, 1.28);   key(blob, 'scale',    39)
blob.location = (x, y, r);            key(blob, 'location', 45)   # contact
blob.scale    = (1.14, 1.14, 0.76);   key(blob, 'scale',    47)   # land squash
blob.scale    = (1.05, 1.05, 0.97);   key(blob, 'scale',    51)   # overshoot
blob.scale    = (1, 1, 1);            key(blob, 'scale',    57)   # settle → rest

# — easing pass: natural S-curves everywhere —
for fc in blob.animation_data.action.fcurves:
    for kp in fc.keyframe_points:
        kp.interpolation = 'BEZIER'
        kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
# magic eases exist: kp.interpolation in {'BACK','BOUNCE','ELASTIC','SINE','EXPO','QUAD','QUART'} + kp.easing —
# but explicit overshoot keys (like f51 above) give far better control. Prefer explicit.
```

Scale keyframes assume the object origin is at its base (contact point) — `bpy.ops.object.origin_set(type='ORIGIN_CURSOR')` with the 3D cursor on the floor.

**Pro life-hack — noise-modified breath:** add a `NOISE` fcurve modifier to scale-Z (strength 0.012, scale 8) for organic micro-motion on top of keys:

```python
fz = blob.animation_data.action.fcurves.find('scale', index=2)
n = fz.modifiers.new('NOISE'); n.strength = 0.012; n.scale = 8
```

**Stepped Claymation preview:** `kp.interpolation = 'CONSTANT'` on every curve, render at 2× fps and drop every other frame in post — or simply key every 2 frames.

Loop hygiene: first and last key must have identical values; breathing cycles must use periods that divide the loop (`2π f / (T·fps)` sampling in keys or the noise modifier with `scale` tuned).

## 7. Physics quick wins

```python
# Rigid body bounce (balls, dice, stacks)
bpy.ops.rigidbody.object_add(); blob.rigid_body.mass = 0.4
blob.rigid_body.restitution = 0.75      # bounciness
blob.rigid_body.damping = 0.04          # air
S.rigidbody_world.point_cache.frame_end = int(a.secs * a.fps)
bpy.ops.ptcache.bake_all(bake=True)     # bake BEFORE rendering
```

Cloth: add Cloth modifier, preset Cotton, pin vertex group. Particles for confetti/sparkles: `bpy.ops.object.particle_system_add()`, Emission → Render As → Collection. Always bake before render; never trust unbaked caches in headless runs.

## 8. Render settings & MP4

```python
S.render.engine = 'CYCLES'
S.cycles.device = 'CPU'                 # safe headless default; switch to 'GPU' when configured
S.cycles.samples = a.samples            # 64 draft / 96–128 delivery / 256 glass+product
S.cycles.use_denoising = True
S.render.resolution_x, S.render.resolution_y = W, H
S.render.fps = a.fps; S.render.frame_start = 0; S.render.frame_end = int(a.secs * a.fps)

vt = S.view_settings
vt.view_transform = 'AgX' if 'AgX' in {v.identifier for v in vt.bl_rna.properties['view_transform'].enum_items} else 'Filmic'
vt.look = next((v.identifier for v in vt.bl_rna.properties['look'].enum_items
                if 'Medium High Contrast' in v.identifier), 'None')

img = S.render.image_settings
img.file_format = 'FFMPEG'; img.color_mode = 'RGB'
ff = S.render.ffmpeg
ff.format = 'MPEG4'; ff.codec = 'H264'; ff.constant_rate_factor = 'HIGH'; ff.ffmpeg_preset = 'GOOD'
ff.audio_codec = 'NONE'                 # sound is mixed in post — see sound-design.md
S.render.filepath = a.out[:-4] if a.out.endswith('.mp4') else a.out
bpy.ops.render.render(animation=True)
```

**Lookdev still:** `--still N` sets `frame = N`, `file_format='PNG'`, renders one frame at final settings. Always ship one lookdev frame before the full animation (it's the cheapest place to catch wrong colors, bad shadows, clipping).

Estimate render cost honestly: time_one_frame × frames. At 1080p/96 samples expect 5–30 s/frame on CPU — a 240-frame shot is 20 min–2 h. Offer the user a 25%-resolution draft render first (`--res 480x270`) to approve motion, then final.

## 9. Lookdev protocol & iteration

1. `--still` on the hero action frame → check palette, shadows, composition (against the style bible).
2. Draft animation at 25% res, 12 fps (`--res 480x270 --fps 12` → scrub it).
3. Fix timing-sheet issues (this is the pass where anticipation/settle get tuned).
4. Final render; add sound in post (`sound-design.md`); mux:

```bash
ffmpeg -i silent.mp4 -i mix.wav -c:v copy -c:a aac -b:a 192k -shortest final.mp4
```

## 10. Common background-mode errors

| Error | Fix |
|---|---|
| `Context missing active object` on ops | Select explicitly: `bpy.context.view_layer.objects.active = obj` before operator calls |
| EEVEE fails headless ("Unable to open display") | Use CYCLES (CPU) — see §8 |
| Material input `KeyError` | 3.x/4.x renamed inputs → always `set_input(node, (alias4, alias3), v)` |
| Motion looks floaty/slow | Bezier auto-clamped eases everything equally — add explicit anticipation/overshoot keys (§6) |
| Render ignores resolution | Set `resolution_x/y` on `scene.render`, and `resolution_percentage = 100` |
| Physics re-simulates differently every run | Bake cache first (`ptcache.bake_all`) |
| Output has no extension | Keep `render.use_file_extension = True`, pass `--out` without `.mp4` |
| Colors look washed | Missing `srgb()` conversion or wrong view transform (§8) |
