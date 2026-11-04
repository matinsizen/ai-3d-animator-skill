# PRO 3D ANIMATOR — Example model (Path B / Blender): "Swift", low-poly jet
# ═════════════════════════════════════════════════════════════════════════════
# Delta-wing jet from primitives: scaled-sphere fuselage, extruded wings,
# canted twin tails, emissive afterburner cones. Flies one perfect circle per
# loop (banked turn), low-poly Flat style bible.
#
# Run:  blender -b -P blender-jet.py -- --secs 8 --fps 30 --render
# Mirrors examples/jet-fighter/threejs-jet.js (Path A).

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

def mat(name, color, rough=0.8, metal=0.0, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*[int(color[i:i+2], 16) / 255 for i in (1, 3, 5)], 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if emit > 0 and 'Emission Color' in b.inputs:
        b.inputs['Emission Color'].default_value = (1, 0.6, 0.1, 1)
        b.inputs['Emission Strength'].default_value = emit
    return m

M_BODY, M_BELLY = mat('body', '#5C7A99'), mat('belly', '#E8E9EB')
M_ACCENT, M_GLASS = mat('accent', '#E76F51'), mat('glass', '#1D2E40', rough=0.1, metal=0.6)
M_FLAME = mat('flame', '#FFB703', emit=6.0)
M_CLOUD = mat('cloud', '#FFFFFF', rough=1.0)

def smooth(o):  # low-poly = flat shading, so NO smooth
    return o

# fuselage — UV sphere stretched into a lofted body (nose +Y in local, then rotate)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=12, ring_count=8)
fus = bpy.context.object; fus.name = 'fuselage'
fus.scale = (0.42, 1.9, 0.36); fus.location = (0, 0.5, 0)
fus.data.materials.append(M_BODY)
bpy.ops.mesh.primitive_cone_add(radius1=0.16, depth=0.7, vertices=12, location=(0, 2.6, 0))
nose = bpy.context.object; nose.name = 'nose'
nose.rotation_euler = (math.radians(-90), 0, 0)
nose.data.materials.append(M_ACCENT)

# canopy
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, segments=10, ring_count=7, location=(0, 1.15, 0.30))
can = bpy.context.object; can.name = 'canopy'
can.scale = (0.75, 1.5, 0.62); can.data.materials.append(M_GLASS)

# delta wings — extruded plane
bpy.ops.mesh.primitive_plane_add(size=1, location=(1.35, 0.2, 0.02))
wingR = bpy.context.object; wingR.name = 'wingR'
wingR.scale = (1.35, 0.95, 1)
bpy.ops.object.transform_apply(scale=True)
bpy.ops.object.mode_set(mode='EDIT')
import bmesh
bm = bmesh.from_edit_mesh(wingR.data)
# sweep the wing back: move +Y side vertices toward -X and down
for v in bm.verts:
    v.co.y += 0.9 if v.co.x > 0 else 0.2
    v.co.z = -0.12 if v.co.x > 0 else 0.02
bmesh.update_edit_mesh(wingR.data)
bpy.ops.object.mode_set(mode='OBJECT')
wingR.data.materials.append(M_BODY)
wingL = wingR.copy(); wingL.data = wingR.data.copy(); wingL.name = 'wingL'
wingL.scale.x = -1
scene.collection.objects.link(wingL)

# twin canted tails
for s in (-1, 1):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.3 * s, -1.15, 0.45))
    fin = bpy.context.object; fin.name = f'fin_{s}'
    fin.scale = (0.05, 0.55, 0.55)
    fin.rotation_euler = (math.radians(-20 * s), 0, 0)
    fin.data.materials.append(M_ACCENT)

# horizontal stabilizer
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -1.45, 0.06))
hs = bpy.context.object; hs.name = 'hstab'
hs.scale = (1.35, 0.28, 0.04); hs.data.materials.append(M_BODY)

# engines + afterburners
flames = []
for s in (-1, 1):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.35, vertices=10, location=(0.2 * s, -1.7, 0.05))
    noz = bpy.context.object; noz.name = f'nozzle_{s}'
    noz.rotation_euler = (math.radians(90), 0, 0)
    noz.data.materials.append(M_BELLY)
    bpy.ops.mesh.primitive_cone_add(radius1=0.11, depth=0.9, vertices=8, location=(0.2 * s, -2.3, 0.05))
    fl = bpy.context.object; fl.name = f'flame_{s}'
    fl.rotation_euler = (math.radians(-90), 0, 0)
    fl.data.materials.append(M_FLAME)
    flames.append(fl)

# missiles
for s in (-1, 1):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.7, vertices=8, location=(1.15 * s, 0.6, -0.14))
    ms = bpy.context.object; ms.name = f'missile_{s}'
    ms.rotation_euler = (math.radians(90), 0, 0)
    ms.data.materials.append(M_BELLY)

# parent everything to a "jet" pivot
bpy.ops.object.empty_add(location=(0, 0, 1.6))
jet = bpy.context.object; jet.name = 'jet'
for o in bpy.context.scene.objects:
    if o.name not in ('jet',) and o.parent is None and o.type == 'MESH':
        o.parent = jet

# clouds (far outside the flight circle)
for i, (x, y, z, s) in enumerate([(-15, 3.5, -6, 1.7), (16, 5, -4, 2.3), (-12, 5.5, 11, 1.4), (14, 2, 12, 1.2), (1, 7.5, -16, 2.8)]):
    for j, (dx, dy, r) in enumerate([(0, 0, 0.8), (0.8, 0, 0.6), (-0.8, 0, 0.62)]):
        bpy.ops.mesh.primitive_icosphere_add(subdivisions=1, radius=r * s, location=(x + dx * s, y, z + dy))
        c = bpy.context.object; c.name = f'cloud_{i}_{j}'
        c.data.materials.append(M_CLOUD)

# ── world: sky blue ──────────────────────────────────────────────────────────
world = bpy.data.worlds.new('sky'); scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.74, 0.88, 0.996, 1)
bg.inputs['Strength'].default_value = 1.0

# ── lights + camera (chase) ──────────────────────────────────────────────────
sun_d = bpy.data.lights.new('sun', 'SUN'); sun_d.energy = 3.5
sun = bpy.data.objects.new('sun', sun_d)
sun.rotation_euler = (math.radians(50), 0, math.radians(30))
scene.collection.objects.link(sun)

cam_d = bpy.data.cameras.new('cam'); cam_d.lens = 45
cam = bpy.data.objects.new('cam', cam_d)
scene.collection.objects.link(cam)
scene.camera = cam

# ── animation: one full circle per loop, banked ──────────────────────────────
R = 6.0
steps = 48
for i in range(steps + 1):
    f = 1 + int(i * (FRAME_END - 1) / steps)
    th = 2 * math.pi * i / steps
    jet.location = (R * math.sin(th), R * math.cos(th), 1.6 + 0.45 * math.sin(2 * th + 1.2))
    jet.rotation_euler = (0.05 * math.sin(2 * th + 1.2), -0.42 - 0.06 * math.sin(2 * th), -th)
    jet.keyframe_insert('location', frame=f)
    jet.keyframe_insert('rotation_euler', frame=f)
    # chase camera: behind-outside the jet, looking at it
    cam.location = ((R + 4.2) * math.sin(th + 0.55), (R + 4.2) * math.cos(th + 0.55), 2.4)
    cam.keyframe_insert('location', frame=f)
    # aim camera at the jet via a Track To constraint instead of keys
for fc in jet.animation_data.action.fcurves:
    for k in fc.keyframe_points:
        k.interpolation = 'LINEAR'          # constant circular motion is legal here

tc = cam.constraints.new('TRACK_TO')
tc.target = jet; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'

# flame flicker — scale keys with CYCLES
for i, fl in enumerate(flames):
    for j, s in enumerate([1.0, 1.35, 0.9, 1.25]):
        fl.scale = (1, s, 1)
        fl.keyframe_insert('scale', frame=1 + int(j * FRAME_END / 4))
    for fc in fl.animation_data.action.fcurves:
        m = fc.modifiers.new('CYCLES'); m.mode = 'REPEAT_AFTER'; m.frame_end = FRAME_END - 1
        for k in fc.keyframe_points: k.interpolation = 'SINE'

# ── render settings ──────────────────────────────────────────────────────────
w, h = ARGS['res'].split('x')
scene.render.resolution_x, scene.render.resolution_y = int(w), int(h)
scene.render.fps = FPS
scene.frame_start, scene.frame_end = 1, FRAME_END
scene.render.engine = 'BLENDER_EEVEE_NEXT' if bpy.app.version >= (4, 2) else 'BLENDER_EEVEE'
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.filepath = f'./jet-patrol_{w}x{h}_{FPS}fps'

if ARGS['render']:
    bpy.ops.render.render(animation=True)
    print(f'RENDERED → {scene.render.filepath}0001-0{FRAME_END}.mp4')
else:
    print(f'Jet scene built ({FRAME_END} frames). Press Space to play.')
