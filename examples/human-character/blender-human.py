# PRO 3D ANIMATOR — Example model (Path B / Blender): "Milo", stylized human
# ═════════════════════════════════════════════════════════════════════════════
# Fully-rigged procedural character: empty-objects as joints, meshes parented
# to them, walk / idle / wave keyframe animations with eased interpolation,
# soft three-point light rig, and headless MP4 rendering.
#
# Run:  blender -b -P blender-human.py -- --mode walk --secs 8 --fps 30 --render
#       blender --python blender-human.py            # open in the UI
#
# Structure mirrors examples/human-character/threejs-human.js (Path A).

import bpy, math, sys

# ── argv ─────────────────────────────────────────────────────────────────────
def get_args():
    rest = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    out = {'mode': 'walk', 'secs': 8.0, 'fps': 30, 'res': '1280x720', 'render': False}
    i = 0
    while i < len(rest):
        k = rest[i].lstrip('-')
        if k == 'render':
            out['render'] = True; i += 1
        else:
            out[k] = rest[i + 1]; i += 2
    return out

ARGS = get_args()
MODE = ARGS['mode']
FPS = int(ARGS['fps'])
SECS = float(ARGS['secs'])
FRAME_END = int(FPS * SECS)

# ── clean scene ──────────────────────────────────────────────────────────────
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ── materials (Puffy bible: pastel, soft, sheen-ish) ─────────────────────────
def mat(name, color, rough=0.45, sheen=0.35):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (*[int(color[i:i+2], 16) / 255 for i in (1, 3, 5)], 1)
    bsdf.inputs['Roughness'].default_value = rough
    if 'Sheen Weight' in bsdf.inputs:
        bsdf.inputs['Sheen Weight'].default_value = sheen
    if 'Coat Weight' in bsdf.inputs:
        bsdf.inputs['Coat Weight'].default_value = 0.3
    return m

M_SKIN, M_HAIR = mat('skin', '#FFD1A6'), mat('hair', '#5A4032')
M_SHIRT, M_PANTS = mat('shirt', '#FF8FA3'), mat('pants', '#6D8EA0')
M_SHOE, M_SOLE = mat('shoe', '#FBFBF7'), mat('sole', '#E76F51')
M_DARK = mat('dark', '#2B2320', rough=0.3)

def sphere(name, r, material, loc=(0, 0, 0), scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=32, ring_count=20)
    o = bpy.context.object
    o.name, o.scale = name, scale
    o.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return o

def cyl(name, r, depth, material, loc=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, vertices=24)
    o = bpy.context.object
    o.name = name
    o.data.materials.clear(); o.data.materials.append(material)
    bevel = o.modifiers.new('Bevel', 'BEVEL')
    bevel.width, bevel.segments = 0.04, 4
    bpy.ops.object.shade_smooth()
    return o

def empty(name, loc):
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 0.05
    e.location = loc
    scene.collection.objects.link(e)
    return e

def parent(child, p):
    child.parent = p
    child.matrix_parent_inverse = p.matrix_world.inverted()

# ── rig: hips at 0.72, knee 0.38, shoulders 1.14, head 1.38 (matches Path A) ─
hips = empty('hips', (0, 0, 0.72))

torso = empty('torso', (0, 0, 0.02)); parent(torso, hips)
chest = sphere('chest', 0.20, M_SHIRT, (0, 0, 0.17), (1.0, 0.82, 1.15)); parent(chest, torso)

head_j = empty('head_j', (0, 0, 0.44)); parent(head_j, torso)
head = sphere('head', 0.205, M_SKIN, (0, 0, 0.08)); parent(head, head_j)
hair = sphere('hair', 0.215, M_HAIR, (0, -0.015, 0.115), (1, 1.06, 1.0)); parent(hair, head_j)

def make_arm(side):                       # side: -1 left, +1 right
    sh = empty(f'shoulder_{side}', (0.215 * side, 0, 0.40)); parent(sh, torso)
    delt = sphere(f'delt_{side}', 0.08, M_SHIRT); parent(delt, sh)
    up = cyl(f'upper_{side}', 0.05, 0.20, M_SHIRT, (0, 0, -0.12)); parent(up, sh)
    el = empty(f'elbow_{side}', (0, 0, -0.27)); parent(el, sh)
    fo = cyl(f'fore_{side}', 0.042, 0.17, M_SKIN, (0, 0, -0.10)); parent(fo, el)
    hand = sphere(f'hand_{side}', 0.058, M_SKIN, (0, 0, -0.25)); parent(hand, el)
    return sh, el

shL, elL = make_arm(-1); shR, elR = make_arm(1)

def make_leg(side):
    hip = empty(f'hip_{side}', (0.105 * side, 0, 0)); parent(hip, hips)
    th = cyl(f'thigh_{side}', 0.08, 0.26, M_PANTS, (0, 0, -0.15)); parent(th, hip)
    kn = empty(f'knee_{side}', (0, 0, -0.34)); parent(kn, hip)
    sh = cyl(f'shin_{side}', 0.06, 0.24, M_PANTS, (0, 0, -0.13)); parent(sh, kn)
    an = empty(f'ankle_{side}', (0, 0, -0.30)); parent(an, kn)
    shoe = sphere(f'shoe_{side}', 0.085, M_SHOE, (0, 0.03, -0.045), (0.75, 1.25, 0.55)); parent(shoe, an)
    sole = sphere(f'sole_{side}', 0.09, M_SOLE, (0, 0.03, -0.09), (0.78, 1.3, 0.22)); parent(sole, an)
    return hip, kn

hipL, knL = make_leg(-1); hipR, knR = make_leg(1)

# eyes (blink via scale keyframes)
eyes = []
for s in (-1, 1):
    w = sphere(f'eye_{s}', 0.048, M_SHOE, (0.075 * s, 0.175, 0.10)); parent(w, head_j)
    p = sphere(f'pupil_{s}', 0.021, M_DARK, (0, 0.036, 0.004)); parent(p, w)
    eyes.append(w)

# ── ground + lights (soft-box rig) + camera ─────────────────────────────────
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -0.35))
ground = bpy.context.object; ground.name = 'ground'
ground.scale = (8, 6, 0.35)
bev = ground.modifiers.new('Bevel', 'BEVEL'); bev.width = 0.25; bev.segments = 6
gm = mat('ground', '#B7E4C7', rough=0.75, sheen=0)
ground.data.materials.append(gm)

def area_light(name, loc, power, size, color=(1, 1, 1)):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy, ld.size, ld.color = power, size, color
    o = bpy.data.objects.new(name, ld)
    o.location = loc
    scene.collection.objects.link(o)
    return o

key = area_light('key', (6, 6, 9), 400, 3)
key.rotation_euler = (math.radians(35), 0, math.radians(45))
fill = area_light('fill', (-7, 2, 4), 120, 4, (0.81, 0.89, 1.0))
rim = area_light('rim', (-2, -8, 6), 150, 2, (1.0, 0.82, 0.86))

cam_d = bpy.data.cameras.new('cam'); cam_d.lens = 55
cam = bpy.data.objects.new('cam', cam_d)
cam.location, cam.rotation_euler = (2.3, -3.2, 1.65), (math.radians(75), 0, math.radians(35))
scene.collection.objects.link(cam)
scene.camera = cam
bpy.context.view_layer.objects.active = cam

# ── animation ────────────────────────────────────────────────────────────────
def key_rot(obj, frame, euler, interp='BEZIER', easing='AUTO'):
    obj.rotation_euler = euler
    obj.keyframe_insert('rotation_euler', frame=frame)
    for fc in obj.animation_data.action.fcurves:
        for k in fc.keyframe_points:
            if abs(k.co[0] - frame) < 0.01:
                k.interpolation, k.easing = interp, easing

def loop_modifiers(obj):
    for fc in obj.animation_data.action.fcurves:
        m = fc.modifiers.new('CYCLES')
        m.mode = 'REPEAT_AFTER'
        m.frame_end = FRAME_END - 1

def key_scale(obj, frame, s, easing='AUTO'):
    obj.scale = (s, s, s) if isinstance(s, float) else s
    obj.keyframe_insert('scale', frame=frame)
    for fc in obj.animation_data.action.fcurves:
        for k in fc.keyframe_points:
            if abs(k.co[0] - frame) < 0.01:
                k.interpolation, k.easing = 'BEZIER', easing

if MODE == 'walk':
    cadence = 4                              # strides per loop
    n = cadence * 4                          # keys per stride (quarter poses)
    for i in range(n + 1):
        f = int(i * FRAME_END / n)
        p = 2 * math.pi * cadence * (i / n)
        key_rot(hipL, f, (0.58 * math.sin(p), 0, 0))
        key_rot(hipR, f, (0.58 * math.sin(p + math.pi), 0, 0))
        kn_bend = lambda pp: max(0.0, math.sin(pp + 0.9)) * 0.95
        key_rot(knL, f, (-kn_bend(p), 0, 0))
        key_rot(knR, f, (-kn_bend(p + math.pi), 0, 0))
        key_rot(shL, f, (-0.42 * math.sin(p + 0.25), 0, 0.10))
        key_rot(shR, f, (0.42 * math.sin(p + 0.25), 0, -0.10))
        key_rot(hips, f, (0, 0.09 * math.sin(p), 0), easing='AUTO')
    # hips bob: two dips per stride — location keys
    for i in range(cadence * 2 + 1):
        f = int(i * FRAME_END / (cadence * 2))
        hips.location.z = 0.72 - 0.016 + (0.032 if i % 2 == 0 else -0.016)
        hips.keyframe_insert('location', frame=f)
    loop_modifiers(hipL); loop_modifiers(hipR); loop_modifiers(knL)
    loop_modifiers(knR); loop_modifiers(shL); loop_modifiers(shR)
elif MODE == 'wave':
    key_rot(shR, 1, (0, 0, -0.10))
    key_rot(shR, int(FPS * 1.15), (0, 0, -2.45), interp='BACK', easing='EASE_OUT')
    for i in range(8):                       # hand oscillation
        f = int(FPS * (1.15 + i * (SECS - 2.4) / 8))
        key_rot(elR, f, (-0.45, 0, -0.55 * (1 if i % 2 else -1)), interp='SINE')
    key_rot(shR, FRAME_END, (0, 0, -0.10), interp='SINE', easing='EASE_IN')
else:                                        # idle
    key_rot(head_j, 1, (0, 0.10, 0)); key_rot(head_j, int(FPS * 2.5), (0, -0.10, 0))
    key_rot(head_j, FRAME_END, (0, 0.10, 0), interp='SINE')
    key_rot(hips, 1, (0, 0, 0.025)); key_rot(hips, FRAME_END, (0, 0, -0.025), interp='SINE')
    for i, f in enumerate([int(FPS * 2.2), int(FPS * 2.3), int(FPS * 2.4)]):
        key_scale(eyes[0], f, 1.0 if i % 2 == 0 else 0.15)
        key_scale(eyes[1], f, 1.0 if i % 2 == 0 else 0.15)

# blink for walk/idle bases
if MODE != 'idle':
    for i, f in enumerate([int(FPS * 2.2), int(FPS * 2.3), int(FPS * 2.4)]):
        key_scale(eyes[0], f, 1.0 if i % 2 == 0 else 0.15)
        key_scale(eyes[1], f, 1.0 if i % 2 == 0 else 0.15)

# ── output settings ──────────────────────────────────────────────────────────
w, h = ARGS['res'].split('x')
scene.render.resolution_x, scene.render.resolution_y = int(w), int(h)
scene.render.fps = FPS
scene.frame_start, scene.frame_end = 1, FRAME_END
scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'SceneEEVEE') and bpy.app.version >= (4, 2) else 'BLENDER_EEVEE'
scene.view_settings.view_transform = 'Standard'
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'HIGH'
scene.render.filepath = f'./human-{MODE}_{w}x{h}_{FPS}fps'

if ARGS['render']:
    bpy.ops.render.render(animation=True)
    print(f'RENDERED → {scene.render.filepath}0001-0{FRAME_END}.mp4')
else:
    print(f'Scene built ({MODE}, {FRAME_END} frames). Press Space to play, Ctrl+F12 to render.')
