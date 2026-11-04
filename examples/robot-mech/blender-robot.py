# PRO 3D ANIMATOR — Example model (Path B / Blender): "Bolt", toy mech robot
# ═════════════════════════════════════════════════════════════════════════════
# Rounded-box mech: beveled cubes + spheres, emissive visor/core, stomp-walk
# with weight dips, servo head scan. Mirrors examples/robot-mech/threejs-robot.js
#
# Run:  blender -b -P blender-robot.py -- --mode patrol --secs 8 --fps 30 --render

import bpy, math, sys

def get_args():
    rest = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    out = {'mode': 'patrol', 'secs': 8.0, 'fps': 30, 'res': '1280x720', 'render': False}
    i = 0
    while i < len(rest):
        k = rest[i].lstrip('-')
        if k == 'render': out['render'] = True; i += 1
        else: out[k] = rest[i + 1]; i += 2
    return out

ARGS = get_args()
MODE = ARGS['mode']; FPS = int(ARGS['fps']); SECS = float(ARGS['secs'])
FRAME_END = int(FPS * SECS)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

def mat(name, color, rough=0.5, metal=0.25, emissive=None, ei=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*[int(color[i:i+2], 16) / 255 for i in (1, 3, 5)], 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if emissive:
        b.inputs['Emission Color'].default_value = (*[int(emissive[i:i+2], 16) / 255 for i in (1, 3, 5)], 1)
        b.inputs['Emission Strength'].default_value = ei
    return m

M_SHELL = mat('shell', '#3A4053')
M_DARK = mat('dark', '#262B3A', rough=0.6)
M_JOINT = mat('joint', '#8B95A8', rough=0.35, metal=0.5)
M_VISOR = mat('visor', '#062B26', emissive='#00F5D4', ei=3.0)
M_CORE = mat('core', '#062B26', emissive='#00F5D4', ei=2.5)
M_FOOT = mat('foot', '#232838', rough=0.7)

def rbox(name, size, material, loc=(0, 0, 0), bevel=0.06):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object; o.name = name
    o.scale = size
    b = o.modifiers.new('Bevel', 'BEVEL'); b.width = bevel; b.segments = 5
    o.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return o

def ball(name, r, material, loc=(0, 0, 0)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=24, ring_count=16)
    o = bpy.context.object; o.name = name
    o.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return o

def empty(name, loc):
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 0.06; e.location = loc
    scene.collection.objects.link(e)
    return e

def parent(c, p):
    c.parent = p; c.matrix_parent_inverse = p.matrix_world.inverted()

# rig: hips 0.92, torso top 1.52, head 1.62 (matches Path A)
hips = empty('hips', (0, 0, 0.92))
rbox('pelvis', (0.52, 0.36, 0.22), M_DARK, (0, 0, 0)).parent = hips

torso = empty('torso', (0, 0, 0.08)); parent(torso, hips)
chest = rbox('chest', (0.62, 0.42, 0.52), M_SHELL, (0, 0, 0.26)); parent(chest, torso)
core = ball('core', 0.075, M_CORE, (0, 0.21, 0.30)); parent(core, torso)
core.scale = (1, 0.35, 1)
for dy in (0.12, 0.04):
    v = rbox(f'vent_{dy}', (0.30, 0.02, 0.025), M_JOINT, (0, 0.215, dy), 0.01); parent(v, torso)

neck = empty('neck', (0, 0, 0.52)); parent(neck, torso)
head_j = empty('head_j', (0, 0, 0.10)); parent(head_j, neck)
head = rbox('head', (0.34, 0.30, 0.26), M_SHELL); parent(head, head_j)
visor = rbox('visor', (0.24, 0.05, 0.10), M_VISOR, (0, 0.15, 0.01), 0.02); parent(visor, head_j)
ant = ball('ant_tip', 0.028, M_VISOR, (0.10, 0, 0.17)); parent(ant, head_j)

def make_arm(side):
    sh = empty(f'shoulder_{side}', (0.38 * side, 0, 0.44)); parent(sh, torso)
    ball(f'shoulder_ball_{side}', 0.10, M_JOINT).parent = sh
    rbox(f'upper_{side}', (0.15, 0.15, 0.26), M_SHELL, (0, 0, -0.16)).parent = sh
    el = empty(f'elbow_{side}', (0, 0, -0.34)); parent(el, sh)
    ball(f'elbow_ball_{side}', 0.075, M_JOINT).parent = el
    rbox(f'fore_{side}', (0.13, 0.13, 0.24), M_DARK, (0, 0, -0.14)).parent = el
    for f in (-1, 1):
        rbox(f'finger_{side}_{f}', (0.05, 0.07, 0.12), M_JOINT, (0.035 * f, 0, -0.30), 0.02).parent = el
    return sh, el

shL, elL = make_arm(-1); shR, elR = make_arm(1)

def make_leg(side):
    hip = empty(f'hip_{side}', (0.17 * side, 0, -0.10)); parent(hip, hips)
    rbox(f'thigh_{side}', (0.20, 0.20, 0.30), M_SHELL, (0, 0, -0.16)).parent = hip
    kn = empty(f'knee_{side}', (0, 0, -0.36)); parent(kn, hip)
    ball(f'knee_ball_{side}', 0.085, M_JOINT).parent = kn
    rbox(f'shin_{side}', (0.17, 0.17, 0.28), M_DARK, (0, 0, -0.15)).parent = kn
    an = empty(f'ankle_{side}', (0, 0, -0.34)); parent(an, kn)
    rbox(f'foot_{side}', (0.24, 0.34, 0.12), M_FOOT, (0, 0.05, -0.05)).parent = an
    toe = rbox(f'toe_{side}', (0.20, 0.06, 0.03), M_VISOR, (0, 0.22, -0.10), 0.01); parent(toe, an)
    return hip, kn

hipL, knL = make_leg(-1); hipR, knR = make_leg(1)

# ── ground + world + lights + camera ────────────────────────────────────────
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -0.4))
g = bpy.context.object; g.name = 'ground'
g.scale = (8, 6, 0.4)
bg_mat = mat('ground', '#C9D3E0', rough=0.8)
b = g.modifiers.new('Bevel', 'BEVEL'); b.width = 0.3; b.segments = 6
g.data.materials.append(bg_mat)

world = bpy.data.worlds.new('w'); scene.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.91, 0.93, 0.96, 1)

sun_d = bpy.data.lights.new('sun', 'SUN'); sun_d.energy = 3.0
sun = bpy.data.objects.new('sun', sun_d)
sun.rotation_euler = (math.radians(45), 0, math.radians(40))
scene.collection.objects.link(sun)
fill_d = bpy.data.lights.new('fill', 'AREA'); fill_d.energy = 120; fill_d.size = 4; fill_d.color = (0.8, 0.88, 1.0)
fill = bpy.data.objects.new('fill', fill_d); fill.location = (-6, -3, 4)
scene.collection.objects.link(fill)

cam_d = bpy.data.cameras.new('cam'); cam_d.lens = 50
cam = bpy.data.objects.new('cam', cam_d)
cam.location, cam.rotation_euler = (2.6, -3.4, 1.7), (math.radians(76), 0, math.radians(37))
scene.collection.objects.link(cam); scene.camera = cam

# ── animation ────────────────────────────────────────────────────────────────
def key_rot(o, f, eul, interp='BEZIER'):
    o.rotation_euler = eul
    o.keyframe_insert('rotation_euler', frame=f)
    for fc in o.animation_data.action.fcurves:
        for k in fc.keyframe_points:
            if abs(k.co[0] - f) < 0.01: k.interpolation = interp

def cycles(o):
    for fc in o.animation_data.action.fcurves:
        m = fc.modifiers.new('CYCLES'); m.mode = 'REPEAT_AFTER'; m.frame_end = FRAME_END - 1

if MODE == 'patrol':
    cadence, n = 3, 24
    for i in range(n + 1):
        f = 1 + int(i * (FRAME_END - 1) / n)
        p = 2 * math.pi * cadence * i / n
        key_rot(hipL, f, (0.5 * math.sin(p), 0, 0))
        key_rot(hipR, f, (0.5 * math.sin(p + math.pi), 0, 0))
        key_rot(knL, f, (-0.85 * max(0, math.sin(p + 0.7)), 0, 0))
        key_rot(knR, f, (-0.85 * max(0, math.sin(p + math.pi + 0.7)), 0, 0))
        key_rot(shL, f, (-0.30 * math.sin(p + 0.3), 0, 0))
        key_rot(shR, f, (0.30 * math.sin(p + 0.3), 0, 0))
        key_rot(torso, f, (0.04, -0.11 * math.sin(p), 0))
        key_rot(hips, f, (0, 0.07 * math.sin(p), 0.045 * math.sin(p)))
        hips.location.z = 0.92 - 0.045 * abs(math.sin(p)) + 0.012
        hips.keyframe_insert('location', frame=f)
    for o in (hipL, hipR, knL, knR, shL, shR, torso, hips): cycles(o)
    # servo head scan — one sweep per loop
    key_rot(head_j, 1, (0, 0.5, 0), 'SINE')
    key_rot(head_j, int(FPS * 2), (0, -0.35, 0), 'SINE')
    key_rot(head_j, int(FPS * 4), (0, 0.5, 0), 'SINE')
    key_rot(head_j, FRAME_END, (0, 0.5, 0), 'SINE')
    cycles(head_j)
else:  # idle
    key_rot(head_j, 1, (0, 0.35, 0), 'SINE')
    key_rot(head_j, int(FPS * 2), (0.06, -0.35, 0), 'SINE')
    key_rot(head_j, FRAME_END, (0, 0.35, 0), 'SINE')
    hips.location.z = 0.93; hips.keyframe_insert('location', frame=1)
    hips.location.z = 0.91; hips.keyframe_insert('location', frame=FRAME_END)
    cycles(head_j); cycles(hips)
    for fc in hips.animation_data.action.fcurves:
        for k in fc.keyframe_points: k.interpolation = 'SINE'

# ── render ───────────────────────────────────────────────────────────────────
w, h = ARGS['res'].split('x')
scene.render.resolution_x, scene.render.resolution_y = int(w), int(h)
scene.render.fps = FPS
scene.frame_start, scene.frame_end = 1, FRAME_END
scene.render.engine = 'BLENDER_EEVEE_NEXT' if bpy.app.version >= (4, 2) else 'BLENDER_EEVEE'
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'; scene.render.ffmpeg.codec = 'H264'
scene.render.filepath = f'./robot-{MODE}_{w}x{h}_{FPS}fps'

if ARGS['render']:
    bpy.ops.render.render(animation=True)
    print(f'RENDERED → {scene.render.filepath}0001-0{FRAME_END}.mp4')
else:
    print(f'Robot scene built ({MODE}, {FRAME_END} frames).')
