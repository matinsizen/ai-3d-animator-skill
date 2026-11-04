# PRO 3D ANIMATOR — Example model (Path B / Blender): "Jelly", city car
# ═════════════════════════════════════════════════════════════════════════════
# Toy car from a beveled extruded side-profile, glass canopy, spoked wheels.
# Showroom turntable or drive mode (wheel spin + body bounce/roll).
# Mirrors examples/sports-car/threejs-car.js (Path A).
#
# Run:  blender -b -P blender-car.py -- --mode showroom --secs 8 --fps 30 --render

import bpy, math, sys

def get_args():
    rest = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    out = {'mode': 'showroom', 'secs': 8.0, 'fps': 30, 'res': '1280x720', 'render': False}
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

def mat(name, color, rough=0.5, metal=0.1, coat=0.0, emissive=None, ei=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*[int(color[i:i+2], 16) / 255 for i in (1, 3, 5)], 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if coat and 'Coat Weight' in b.inputs: b.inputs['Coat Weight'].default_value = coat
    if emissive:
        b.inputs['Emission Color'].default_value = (*[int(emissive[i:i+2], 16) / 255 for i in (1, 3, 5)], 1)
        b.inputs['Emission Strength'].default_value = ei
    return m

M_PAINT = mat('paint', '#FF6B6B', rough=0.3, metal=0.15, coat=0.9)
M_GLASS = mat('glass', '#1D2E40', rough=0.08, metal=0.7)
M_TIRE = mat('tire', '#22252B', rough=0.9)
M_RIM = mat('rim', '#F4F1EA', rough=0.3, metal=0.6)
M_LIGHT = mat('light', '#FFF9DB', emissive='#FFF3B0', ei=4.0)
M_TAIL = mat('tail', '#7A1D24', emissive='#E63946', ei=3.0)

# ── car body: extruded side profile with wheel arches ───────────────────────
import bmesh
bpy.ops.mesh.primitive_circle_add(vertices=32, fill_type='NGON')
body = bpy.context.object; body.name = 'body'
bm = bmesh.new()
verts = [
    (-1.05, -0.36, 0.34), (-1.08, -0.36, 0.60), (-0.98, -0.36, 0.72), (-0.70, -0.36, 0.72),
    (0.42, -0.36, 0.68), (0.80, -0.36, 0.64), (1.02, -0.36, 0.56), (1.12, -0.36, 0.50),
    (1.10, -0.36, 0.38), (1.02, -0.36, 0.30), (0.86, -0.36, 0.30), (0.38, -0.36, 0.30),
    (-0.38, -0.36, 0.30), (-0.86, -0.36, 0.30), (-1.05, -0.36, 0.30),
]
# build one side face, then solidify across Z
mesh = bpy.data.meshes.new('body_mesh')
for v in verts:
    bm.verts.new(v)
bm.verts.ensure_lookup_table()
bm.faces.new(bm.verts)
bm.to_mesh(mesh); bm.free_mesh()
body.data = mesh
sol = body.modifiers.new('Solidify', 'SOLIDIFY'); sol.thickness = 0.72; sol.offset = 0
bev = body.modifiers.new('Bevel', 'BEVEL'); bev.width = 0.055; bev.segments = 4
body.data.materials.append(M_PAINT)
bpy.ops.object.shade_smooth()

# wheel arches: booleans cut from two cylinders (arch openings)
for x in (0.62, -0.62):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.26, depth=1.2, vertices=24, location=(x, 0, 0.30))
    cutter = bpy.context.object
    mod = body.modifiers.new(f'arch_{x}', 'BOOLEAN'); mod.object = cutter; mod.operation = 'DIFFERENCE'
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter)

# glass canopy
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.85))
glass = bpy.context.object; glass.name = 'glass'
glass.scale = (0.90, 0.66, 0.28)
gb = glass.modifiers.new('Bevel', 'BEVEL'); gb.width = 0.12; gb.segments = 5
glass.data.materials.append(M_GLASS)
bpy.ops.object.shade_smooth()

# lights
for s in (-1, 1):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.055, depth=0.04, vertices=14, location=(1.09, 0.20 * s, 0.47))
    hl = bpy.context.object; hl.name = f'headlight_{s}'
    hl.rotation_euler = (0, math.radians(90), 0)
    hl.data.materials.append(M_LIGHT)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-1.10, 0.22 * s, 0.55))
    tl = bpy.context.object; tl.name = f'taillight_{s}'
    tl.scale = (0.04, 0.16, 0.07)
    tl.data.materials.append(M_TAIL)

# bumpers
for x in (1.10, -1.10):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, 0.30))
    bp = bpy.context.object; bp.name = f'bumper_{x}'
    bp.scale = (0.10, 0.86, 0.10)
    bp.data.materials.append(M_PAINT)

# ── wheels (spokes visible so spin reads) ────────────────────────────────────
wheels = []
for (x, y) in [(0.62, 0.44), (0.62, -0.44), (-0.62, 0.44), (-0.62, -0.44)]:
    bpy.ops.object.empty_add(location=(x, y, 0.26))
    wg = bpy.context.object; wg.name = f'wheel_{x}_{y}'
    bpy.ops.mesh.primitive_cylinder_add(radius=0.24, depth=0.16, vertices=24, location=(x, y, 0.26))
    tire = bpy.context.object; tire.name = f'tire_{x}_{y}'
    tire.rotation_euler = (0, math.radians(90), 0)
    tire.data.materials.append(M_TIRE)
    for i in range(5):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 0.26))
        sp = bpy.context.object; sp.name = f'spoke_{x}_{y}_{i}'
        sp.scale = (0.185, 0.10, 0.40)
        sp.rotation_euler = (0, 0, math.pi * i / 2.5)
        sp.data.materials.append(M_RIM)
        sp.parent = wg
    tire.parent = wg
    wheels.append(wg)

# parent body+glass+lights to car pivot
bpy.ops.object.empty_add(location=(0, 0, 0))
car = bpy.context.object; car.name = 'car'
for o in (body, glass):
    o.parent = car
for o in bpy.context.scene.objects:
    if o.type == 'MESH' and o.parent is None and o.name not in ('ground',):
        o.parent = car

# ── ground + world + lights + camera ────────────────────────────────────────
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -0.4))
g = bpy.context.object; g.name = 'ground'
g.scale = (9, 9, 0.4)
gm = mat('ground', '#D8D2C4', rough=0.85)
b = g.modifiers.new('Bevel', 'BEVEL'); b.width = 0.3; b.segments = 6
g.data.materials.append(gm)

world = bpy.data.worlds.new('w'); scene.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.99, 0.965, 0.925, 1)

def area(name, loc, power, size, color=(1, 1, 1)):
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy, ld.size, ld.color = power, size, color
    o = bpy.data.objects.new(name, ld); o.location = loc
    scene.collection.objects.link(o); return o

key = area('key', (6, 6, 9), 500, 4); key.rotation_euler = (math.radians(35), 0, math.radians(45))
area('fill', (-7, 2, 4), 150, 5, (0.85, 0.9, 1.0))
area('rim', (-2, -8, 6), 180, 3, (1.0, 0.85, 0.85))

cam_d = bpy.data.cameras.new('cam'); cam_d.lens = 60
cam = bpy.data.objects.new('cam', cam_d)
cam.location, cam.rotation_euler = (3.4, -3.4, 1.6), (math.radians(77), 0, math.radians(45))
scene.collection.objects.link(cam); scene.camera = cam

# ── animation ────────────────────────────────────────────────────────────────
def keys(o, data, interp='BEZIER', cycles=True):
    for f, attrs in data.items():
        for path, val in attrs.items():
            setattr(o, path, val)
            o.keyframe_insert(path, frame=f)
    if cycles and o.animation_data:
        for fc in o.animation_data.action.fcurves:
            m = fc.modifiers.new('CYCLES'); m.mode = 'REPEAT_AFTER'; m.frame_end = FRAME_END - 1
            for k in fc.keyframe_points: k.interpolation = interp

if MODE == 'showroom':
    keys(car, {
        1: {'rotation_euler': (0, 0, 0)},
        FRAME_END: {'rotation_euler': (0, 0, 2 * math.pi)},
    }, interp='LINEAR')
    keys(body, {
        1: {'location': (0, 0, 0.014)},
        int(FPS * 2): {'location': (0, 0, -0.014)},
        int(FPS * 4): {'location': (0, 0, 0.014)},
    }, interp='SINE')
else:  # drive
    spin = 2 * math.pi * 6
    for i, w in enumerate(wheels):
        keys(w, {
            1: {'rotation_euler': (0, 0, 0)},
            FRAME_END: {'rotation_euler': (0, -spin, 0)},
        }, interp='LINEAR')
    keys(body, {
        1: {'location': (0, 0, 0.02), 'rotation_euler': (0, 0, 0.02)},
        int(FPS * 2): {'location': (0, 0, -0.02), 'rotation_euler': (0.012, 0, -0.02)},
        int(FPS * 4): {'location': (0, 0, 0.02), 'rotation_euler': (0, 0, 0.02)},
    }, interp='SINE')

# ── render ───────────────────────────────────────────────────────────────────
w, h = ARGS['res'].split('x')
scene.render.resolution_x, scene.render.resolution_y = int(w), int(h)
scene.render.fps = FPS
scene.frame_start, scene.frame_end = 1, FRAME_END
scene.render.engine = 'BLENDER_EEVEE_NEXT' if bpy.app.version >= (4, 2) else 'BLENDER_EEVEE'
scene.view_settings.view_transform = 'Standard'
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'; scene.render.ffmpeg.codec = 'H264'
scene.render.filepath = f'./car-{MODE}_{w}x{h}_{FPS}fps'

if ARGS['render']:
    bpy.ops.render.render(animation=True)
    print(f'RENDERED → {scene.render.filepath}0001-0{FRAME_END}.mp4')
else:
    print(f'Car scene built ({MODE}, {FRAME_END} frames). Press Space to play.')
