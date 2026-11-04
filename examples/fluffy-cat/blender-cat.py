# PRO 3D ANIMATOR — Example model (Path B / Blender): "Mochi", puffy cat
# ═════════════════════════════════════════════════════════════════════════════
# Puffy/Bubbly bible in Blender: spheres-only cat (zero sharp edges), hop with
# anticipation → stretch → squash → settle, sine tail, blink.
# Mirrors examples/fluffy-cat/threejs-cat.js (Path A).
#
# Run:  blender -b -P blender-cat.py -- --secs 8 --fps 30 --render

import bpy, math, sys

def get_args():
    rest = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    out = {'secs': 8.0, 'fps': 30, 'res': '1280x720', 'render': False}
    i = 0
    while i < len(rest):
        k = rest[i].lstrip('-')
        if k == 'render': out['render'] = True; i += 1
        else: out[k] = rest[i + 1]; i += 2
    return out

ARGS = get_args()
FPS = int(ARGS['fps']); SECS = float(ARGS['secs'])
FRAME_END = int(FPS * SECS)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

def mat(name, color, rough=0.42, coat=0.5, sheen=0.6):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*[int(color[i:i+2], 16) / 255 for i in (1, 3, 5)], 1)
    b.inputs['Roughness'].default_value = rough
    if 'Coat Weight' in b.inputs: b.inputs['Coat Weight'].default_value = coat
    if 'Sheen Weight' in b.inputs: b.inputs['Sheen Weight'].default_value = sheen
    return m

M_FUR = mat('fur', '#FFE8D6')
M_EAR = mat('ear', '#FFADAD')
M_NOSE = mat('nose', '#E8639B')
M_WHITE = mat('white', '#FFFFFF', rough=0.25, coat=0, sheen=0)
M_DARK = mat('dark', '#2B2320', rough=0.3, coat=0, sheen=0)
M_CHEEK = mat('cheek', '#FFB3C1')

def ball(name, r, material, loc=(0, 0, 0), scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=40, ring_count=28)
    o = bpy.context.object; o.name = name; o.scale = scale
    o.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return o

# cat body (origin at ground contact — squash scales this pivot)
bpy.ops.object.empty_add(location=(0, 0, 0))
cat = bpy.context.object; cat.name = 'cat'

body = ball('body', 0.42, M_FUR, (0, 0, 0.40), (1, 1.22, 0.88)); body.parent = cat
head = ball('head', 0.30, M_FUR, (0, 0.30, 0.72), (1.12, 1, 0.95)); head.parent = cat
for s in (-1, 1):
    ear = ball(f'ear_{s}', 0.10, M_FUR, (0.17 * s, 0.28, 0.96), (0.75, 0.55, 1.25)); ear.parent = cat
    inner = ball(f'earin_{s}', 0.055, M_EAR, (0.17 * s, 0.315, 0.96), (0.7, 0.4, 1.1)); inner.parent = cat
for s in (-1, 1):
    eye = ball(f'eye_{s}', 0.062, M_WHITE, (0.115 * s, 0.545, 0.765)); eye.parent = cat
    pu = ball(f'pupil_{s}', 0.033, M_DARK, (0.115 * s, 0.59, 0.765)); pu.parent = cat
    ch = ball(f'cheek_{s}', 0.045, M_CHEEK, (0.19 * s, 0.51, 0.665), (1.3, 0.4, 0.7)); ch.parent = cat
nose = ball('nose', 0.032, M_NOSE, (0, 0.615, 0.705), (1.2, 0.7, 0.8)); nose.parent = cat
for s in (-1, 1):
    muz = ball(f'muz_{s}', 0.05, M_FUR, (0.045 * s, 0.58, 0.675), (1, 0.6, 0.8)); muz.parent = cat

# legs + paws
for (x, y, front) in [(-0.20, 0.22, True), (0.20, 0.22, True), (-0.24, -0.22, False), (0.24, -0.22, False)]:
    leg = ball(f'leg_{x}', 0.095, M_FUR, (x, y, 0.14), (1, 1, 1.05)); leg.parent = cat
    paw = ball(f'paw_{x}', 0.095, M_WHITE if front else M_FUR, (x, y + 0.03, 0.07), (1, 1.25, 0.62)); paw.parent = cat

# tail — 6 spheres, sine-animated
tail = []
for i in range(6):
    t = ball(f'tail_{i}', 0.075 - i * 0.008, M_FUR)
    t.parent = cat
    tail.append(t)

# ── ground + world + lights + camera ────────────────────────────────────────
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -0.35))
g = bpy.context.object; g.name = 'ground'
g.scale = (8, 6, 0.35)
gm = mat('ground', '#B7E4C7', rough=0.75, coat=0, sheen=0)
b = g.modifiers.new('Bevel', 'BEVEL'); b.width = 0.25; b.segments = 6
g.data.materials.append(gm)

world = bpy.data.worlds.new('w'); scene.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (1.0, 0.965, 0.925, 1)

def area(name, loc, power, size, color=(1, 1, 1)):
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy, ld.size, ld.color = power, size, color
    o = bpy.data.objects.new(name, ld); o.location = loc
    scene.collection.objects.link(o); return o

key = area('key', (6, 6, 9), 400, 3); key.rotation_euler = (math.radians(35), 0, math.radians(45))
area('fill', (-7, 2, 4), 120, 4, (0.81, 0.89, 1.0))
area('rim', (-2, -8, 6), 150, 2, (1.0, 0.82, 0.86))

cam_d = bpy.data.cameras.new('cam'); cam_d.lens = 48
cam = bpy.data.objects.new('cam', cam_d)
cam.location, cam.rotation_euler = (1.9, -2.5, 1.15), (math.radians(76), 0, math.radians(37))
scene.collection.objects.link(cam); scene.camera = cam

# ── animation: hop (anticipation → flight → squash → settle) ────────────────
HOP_T = [0.00, 0.32, 0.60, 1.50, 1.66, 2.45]           # seconds of the hop phases
def sec_to_frame(s): return 1 + int(s * FPS)

def key_cat(f, z, sx, sz):
    cat.location.z = z
    cat.scale = (sx, sx, sz)                            # volume-preserving-ish (x=y plane)
    cat.keyframe_insert('location', frame=f)
    cat.keyframe_insert('scale', frame=f)

phases = [                                              # (frame, z, squash_y)
    (sec_to_frame(0.0),  0.0, 1.00),
    (sec_to_frame(0.32), 0.0, 1.00),
    (sec_to_frame(0.60), 0.0, 0.80),                    # anticipation squash
    (sec_to_frame(1.05), 0.95, 1.18),                   # apex, stretched
    (sec_to_frame(1.50), 0.0, 1.18),
    (sec_to_frame(1.66), 0.0, 0.76),                    # impact squash
    (sec_to_frame(2.45), 0.0, 1.00),                    # settle (BACK easing)
    (sec_to_frame(SECS), 0.0, 1.00),
]
for (f, z, s) in phases:
    key_cat(f, z, 1 / math.sqrt(s), s)
for fc in cat.animation_data.action.fcurves:
    for k in fc.keyframe_points:
        k.interpolation = 'BEZIER'
        if abs(k.co[0] - sec_to_frame(2.45)) < 2: k.interpolation = 'BACK'
    m = fc.modifiers.new('CYCLES'); m.mode = 'REPEAT_AFTER'; m.frame_end = FRAME_END - 1

# tail sine — keys + cycles
for i, t in enumerate(tail):
    for j in range(9):
        f = 1 + int(j * FRAME_END / 8)
        ph = 2 * math.pi * j / 8 - i * 0.85
        t.location = (0.02 * math.sin(ph) * (i / 5), -0.62 - i * 0.11 * math.cos(i * 0.7) + 0.05 * i / 5,
                      0.30 + i * 0.032 + 0.03 * math.sin(ph))
        t.keyframe_insert('location', frame=f)
    for fc in t.animation_data.action.fcurves:
        m = fc.modifiers.new('CYCLES'); m.mode = 'REPEAT_AFTER'; m.frame_end = FRAME_END - 1
        for k in fc.keyframe_points: k.interpolation = 'SINE'

# blink
for i, f in enumerate([sec_to_frame(1.8), sec_to_frame(1.9), sec_to_frame(2.0)]):
    for s in (-1, 1):
        eye = bpy.data.objects[f'eye_{s}']
        eye.scale = (1, 1, 1 if i % 2 == 0 else 0.12)
        eye.keyframe_insert('scale', frame=f)
for s in (-1, 1):
    for fc in bpy.data.objects[f'eye_{s}'].animation_data.action.fcurves:
        m = fc.modifiers.new('CYCLES'); m.mode = 'REPEAT_AFTER'; m.frame_end = FRAME_END - 1

# ── render ───────────────────────────────────────────────────────────────────
w, h = ARGS['res'].split('x')
scene.render.resolution_x, scene.render.resolution_y = int(w), int(h)
scene.render.fps = FPS
scene.frame_start, scene.frame_end = 1, FRAME_END
scene.render.engine = 'BLENDER_EEVEE_NEXT' if bpy.app.version >= (4, 2) else 'BLENDER_EEVEE'
scene.view_settings.view_transform = 'Standard'
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'; scene.render.ffmpeg.codec = 'H264'
scene.render.filepath = f'./cat-hop_{w}x{h}_{FPS}fps'

if ARGS['render']:
    bpy.ops.render.render(animation=True)
    print(f'RENDERED → {scene.render.filepath}0001-0{FRAME_END}.mp4')
else:
    print(f'Cat scene built ({FRAME_END} frames). Press Space to play.')
