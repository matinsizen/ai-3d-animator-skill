#!/usr/bin/env python3
"""
PRO 3D ANIMATOR — Path B starter (Blender headless, 3.6 LTS → 4.5)

A complete, delivery-grade animated scene from one command — no GUI needed:

    blender -b -P blender-starter.py -- --res 1920x1080 --fps 30 --secs 8 --out ./puffy-blob.mp4
    blender -b -P blender-starter.py -- --still 45          # single lookdev frame (frame 45 = landing)

What it demonstrates (rules from the skill, applied):
  • Puffy style bible: bevel→subsurf on everything, pastel palette, sheen+coat
  • Soft area-light rig + colored world (no hard shadows)
  • The animation trio: anticipation → squash&stretch (volume-preserved,
    origin at contact point) → settle with overshoot
  • Explicit overshoot keys + AUTO_CLAMPED bezier easing pass
  • NOISE fcurve modifier for organic micro-motion (breathing)
  • CLI-driven spec (intake result → args), Cycles CPU headless-safe,
    lookdev --still mode, MP4 output via FFMPEG container
"""
import argparse
import math
import sys

import bpy

# ── 1 · CLI spec (intake-driven — never hardcode user requirements) ─────────
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
p = argparse.ArgumentParser()
p.add_argument('--res', default='1920x1080')
p.add_argument('--fps', type=int, default=30)
p.add_argument('--secs', type=float, default=8.0)
p.add_argument('--samples', type=int, default=96)
p.add_argument('--still', type=int, default=-1, help='render only frame N as PNG (lookdev)')
p.add_argument('--out', default='./puffy-blob')
a = p.parse_args(argv)

W, H = (int(v) for v in a.res.lower().split('x'))
FPS = a.fps
END = int(a.secs * FPS)


def srgb(hexstr):
    """hex (#RRGGBB) → linear RGB tuple. Blender colors are linear — without
    this conversion every pastel looks washed-out and wrong."""
    h = hexstr.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92 for c in c)


# ── 2 · Clean deterministic scene ───────────────────────────────────────────
bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene


def empty_at(loc):
    e = bpy.data.objects.new('aim', None)
    e.location = loc
    bpy.context.collection.objects.link(e)
    return e


def track_to(obj, target):
    c = obj.constraints.new('TRACK_TO')
    c.target = target
    c.track_axis = 'TRACK_NEGATIVE_Z'
    c.up_axis = 'UP_Y'
    return c


# ── 3 · Puffy material helper (version-safe input names: 3.x ↔ 4.x) ─────────
def set_input(node, names, value):
    for n in names:
        if n in node.inputs:
            node.inputs[n].default_value = value
            return


def mat_puffy(name, color, rough=0.42):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*srgb(color), 1.0)
    b.inputs['Roughness'].default_value = rough
    set_input(b, ('Sheen Weight', 'Sheen'), 0.6)
    set_input(b, ('Coat Weight', 'Clearcoat'), 0.25)
    set_input(b, ('Coat Roughness', 'Clearcoat Roughness'), 0.5)
    set_input(b, ('Specular IOR Level', 'Specular'), 0.4)
    return m


def apply(obj, mat):
    obj.data.materials.append(mat)


# ── 4 · Set: ground slab, mounds, tree, bush (bevel→subsurf = pillow silhouette) ──
def puffy_round(obj, bevel=0.18, sub=2):
    bev = obj.modifiers.new('bevel', 'BEVEL')
    bev.width = bevel
    bev.segments = 6
    bev.limit_method = 'ANGLE'
    sub_m = obj.modifiers.new('subsurf', 'SUBSURF')
    sub_m.levels = sub
    sub_m.render_levels = sub + 1
    bpy.ops.object.shade_smooth()


bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, -0.9))
slab = bpy.context.active_object
slab.scale = (7.5, 6.0, 0.9)
puffy_round(slab, bevel=0.5, sub=2)
apply(slab, mat_puffy('ground', '#B7E4C7'))

for (mx, my, r) in [(-3.4, 1.4, 1.5), (2.9, -2.5, 1.2), (3.6, 2.2, 0.9)]:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=40, ring_count=28, location=(mx, my, -0.2))
    m = bpy.context.active_object
    m.scale = (1.0, 1.0, 0.38)
    puffy_round(m, bevel=0.0, sub=2)
    apply(m, mat_puffy('mound', '#A5D8C3'))

# tree: capsule trunk + blob canopy
bpy.ops.mesh.primitive_capsule_add(radius=0.18, depth=1.0, location=(-4.6, -2.6, 0.7))
trunk = bpy.context.active_object
bpy.ops.object.shade_smooth()
apply(trunk, mat_puffy('trunk', '#B08968'))
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.62, segments=32, ring_count=24, location=(-4.6, -2.6, 1.55))
cano = bpy.context.active_object
bpy.ops.object.shade_smooth()
apply(cano, mat_puffy('canopy', '#74C69D'))

# ── 5 · Hero blob (origin at contact point → squash reads from the ground) ──
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.9, segments=48, ring_count=32, location=(0, 0, 0.9))
blob = bpy.context.active_object
bpy.ops.object.shade_smooth()
apply(blob, mat_puffy('hero', '#FFADAD'))

# eyes: white sphere + pupil, 60% up the head (art-styles.md §1)
for ex in (-0.28, 0.28):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, segments=24, ring_count=16,
                                         location=(ex, 0.74, 1.22))
    eye = bpy.context.active_object
    bpy.ops.object.shade_smooth()
    apply(eye, mat_puffy('eye', '#FFFFFF', rough=0.25))
    eye.parent = blob
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07, segments=16, ring_count=12,
                                         location=(ex, 0.855, 1.23))
    pupil = bpy.context.active_object
    apply(pupil, mat_puffy('pupil', '#2B2320', rough=0.3))
    pupil.parent = blob

# ── 6 · Soft lighting rig + colored world (pipeline-blender.md §4) ──────────
def area_light(name, loc, size, power, color=(1, 1, 1)):
    d = bpy.data.lights.new(name, 'AREA')
    d.energy = power
    d.size = size
    d.color = color
    o = bpy.data.objects.new(name, d)
    o.location = loc
    bpy.context.collection.objects.link(o)
    track_to(o, empty_at((0, 0, 1)))
    return o


area_light('key', (5, -4, 7), 3.0, 400, srgb('#FFF1E0'))
area_light('fill', (-6, -3, 4), 4.0, 150, srgb('#DCE8FF'))
area_light('rim', (-2, 6, 5), 2.0, 100, srgb('#FFD1DC'))

S.world = bpy.data.worlds.new('world')
S.world.use_nodes = True
bg = S.world.node_tree.nodes['Background']
bg.inputs[0].default_value = (*srgb('#FFF6EC'), 1.0)
bg.inputs[1].default_value = 0.7

# ── 7 · Camera: 50 mm, soft DOF, push-in with bezier easing ─────────────────
cd = bpy.data.cameras.new('cam')
cd.lens = 50
cd.sensor_width = 36
cd.dof.use_dof = True
cd.dof.aperture_fstop = 4.0
cd.dof.focus_distance = 6.5
cam = bpy.data.objects.new('cam', cd)
bpy.context.collection.objects.link(cam)
S.camera = cam
track_to(cam, empty_at((0, 0, 1)))

cam.location = (0.5, -17, 7.2)
cam.keyframe_insert('location', frame=1)
cam.location = (0.5, -15.4, 6.7)
cam.keyframe_insert('location', frame=END)

# ── 8 · Animation: hop with anticipation → squash/stretch → settle ──────────
def k(obj, path, frame):
    obj.keyframe_insert(data_path=path, frame=frame)


R = 0.9
f = lambda sec: int(round(sec * FPS))

# idle
blob.location = (0, 0, R);            k(blob, 'location', f(0.0))
blob.scale = (1, 1, 1);               k(blob, 'scale', f(0.0))
# anticipation: squash 22% (volume preserved: xz = 1/√0.78 ≈ 1.133)
blob.scale = (1.133, 1.133, 0.78);    k(blob, 'scale', f(0.75))
# takeoff stretch
blob.scale = (0.955, 0.955, 1.10);    k(blob, 'scale', f(0.85))
# apex (hang time comes from the bezier through these keys)
blob.location = (0, 0, R + 2.3);      k(blob, 'location', f(1.05))
blob.scale = (0.88, 0.88, 1.28);      k(blob, 'scale', f(1.05))
# contact
blob.location = (0, 0, R);            k(blob, 'location', f(1.35))
# impact squash 25%
blob.scale = (1.155, 1.155, 0.75);    k(blob, 'scale', f(1.47))
# overshoot ~7%
blob.scale = (0.985, 0.985, 1.065);   k(blob, 'scale', f(1.72))
# settle to rest
blob.scale = (1, 1, 1);               k(blob, 'scale', f(2.10))
# hold rest through the loop seam
blob.location = (0, 0, R);            k(blob, 'location', END)
blob.scale = (1, 1, 1);               k(blob, 'scale', END)

# easing pass: natural S-curves (explicit overshoot keys do the "magic easing")
for fc in blob.animation_data.action.fcurves:
    for kp in fc.keyframe_points:
        kp.interpolation = 'BEZIER'
        kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'

# breathing: organic micro-motion on top of the keys (loop-safe noise modifier)
fz = blob.animation_data.action.fcurves.find('scale', index=2)
if fz:
    n = fz.modifiers.new('NOISE')
    n.strength = 0.012
    n.scale = 8.0

# ── 9 · Render settings (pipeline-blender.md §8) ────────────────────────────
S.render.engine = 'CYCLES'
S.cycles.device = 'CPU'          # headless-safe; switch to 'GPU' when configured
S.cycles.samples = a.samples
S.cycles.use_denoising = True
S.render.resolution_x = W
S.render.resolution_y = H
S.render.resolution_percentage = 100
S.render.fps = FPS
S.render.frame_start = 0
S.render.frame_end = END

vt = S.view_settings
names = {v.identifier for v in vt.bl_rna.properties['view_transform'].enum_items}
vt.view_transform = 'AgX' if 'AgX' in names else 'Filmic'
looks = {v.identifier for v in vt.bl_rna.properties['look'].enum_items}
if looks:
    vt.look = next((v for v in looks if 'Medium High Contrast' in v), 'None')

if a.still >= 0:                                   # lookdev: one frame, PNG
    S.frame_set(a.still)
    S.render.image_settings.file_format = 'PNG'
    S.render.filepath = a.out.rstrip('/') + '_still'
    bpy.ops.render.render(write_still=True)
    print(f'[pro-3d-animator] lookdev frame {a.still} → {a.out}_still*.png')
else:                                              # full animation → MP4 (silent; add sound in post)
    img = S.render.image_settings
    img.file_format = 'FFMPEG'
    img.color_mode = 'RGB'
    ff = S.render.ffmpeg
    ff.format = 'MPEG4'
    ff.codec = 'H264'
    ff.constant_rate_factor = 'HIGH'
    ff.ffmpeg_preset = 'GOOD'
    ff.audio_codec = 'NONE'
    S.render.filepath = a.out[:-4] if a.out.endswith('.mp4') else a.out
    bpy.ops.render.render(animation=True)
    print(f'[pro-3d-animator] delivered → {S.render.filepath}.mp4 '
          f'({W}x{H} @ {FPS}fps, {END} frames) — next: sound pass (references/sound-design.md)')
