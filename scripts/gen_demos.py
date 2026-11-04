#!/usr/bin/env python3
"""Generates the 5 live demo pages (docs/demos/<key>/index.html) + gallery (docs/index.html)
for the Pro 3D Animator skill repo, and copies the example modules into docs/models/
(GitHub Pages serves only /docs, so the demos must import their modules from inside it).
Run from repo root:  python3 scripts/gen_demos.py"""
import os, json, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{TITLE} — Pro 3D Animator live demo</title>
<style>
  html, body {{ margin: 0; height: 100%; background: {BG}; overflow: hidden; }}
  #app {{ position: fixed; inset: 0; }}
  #hud {{ position: fixed; left: 12px; bottom: 12px; display: flex; gap: 10px; align-items: center;
         font: 12px/1.5 system-ui, sans-serif; color: {FG}; background: #ffffffd9;
         border-radius: 16px; padding: 8px 14px; box-shadow: 0 4px 14px #00000012; }}
  #hud b {{ font-size: 13px; }}
  #hud .badge {{ background: {ACCENT}; color: #fff; border-radius: 999px; padding: 2px 10px; font-weight: 700; font-size: 11px; }}
  #hud button {{ border: 0; border-radius: 999px; padding: 6px 13px; font-weight: 700; cursor: pointer;
                background: {ACCENT}; color: #fff; }}
  #hud button:hover {{ filter: brightness(1.08); }}
  #hud button.ghost {{ background: #00000010; color: {FG}; }}
  #hud a {{ color: {FG}; opacity: .7; text-decoration: none; }}
  .hide {{ display: none !important; }}
</style>
</head>
<body>
<div id="app"></div>
<div id="hud">
  <b>{TITLE}</b> <span class="badge">{STYLE}</span>
  <span id="modes">{MODE_BUTTONS}</span>
  <span style="opacity:.55">drag to orbit · scroll to zoom</span>
  <a href="../">↩ all demos</a>
</div>

<script type="importmap">
{{ "imports": {{
    "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
}}}}
</script>

<script type="module">
import * as THREE from 'three';
import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';
import {{ RoundedBoxGeometry }} from 'three/addons/geometries/RoundedBoxGeometry.js';
import {{ RoomEnvironment }} from 'three/addons/environments/RoomEnvironment.js';
import {{ {BUILD}, {ANIMATE}, INFO{EXTRA_IMPORTS} }} from '{MODULE}';

/* ── URL contract (headless rendering: examples/render-frames.mjs) ────────── */
const Q = new URLSearchParams(location.search);
const STILL = Q.get('still') !== null;
const stillT = STILL ? parseFloat(Q.get('t') ?? '0') : 0;
let loop = parseFloat(Q.get('loop') ?? INFO.loop);
let speed = parseFloat(Q.get('speed') ?? 1);
let mode = Q.get('mode') ?? INFO.mode;

/* ── renderer / scene / camera ────────────────────────────────────────────── */
const W = STILL ? parseInt((Q.get('res') ?? '1280x720').split('x')[0]) : 960;
const H = STILL ? parseInt((Q.get('res') ?? '1280x720').split('x')[1]) : 540;
const renderer = new THREE.WebGLRenderer({{ antialias: true, preserveDrawingBuffer: true }});
renderer.setPixelRatio(STILL ? 1 : Math.min(devicePixelRatio, 2));
renderer.setSize(W, H);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.12;
renderer.outputColorSpace = THREE.SRGBColorSpace;
document.getElementById('app').appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color('{BG}');
scene.fog = new THREE.Fog('{BG}', {FOG});
scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture;

/* ── lighting: soft three-point rig (works across styles) ─────────────────── */
scene.add(new THREE.HemisphereLight('#FFF3E0', '#D9E4EC', 0.55));
const key = new THREE.DirectionalLight('#FFFFFF', 1.6);
key.position.set(6, 9, 6);
key.castShadow = true;
key.shadow.mapSize.set(2048, 2048);
Object.assign(key.shadow.camera, {{ left: -11, right: 11, top: 11, bottom: -11, near: 1, far: 45 }});
key.shadow.camera.updateProjectionMatrix();
key.shadow.bias = -0.0002; key.shadow.normalBias = 0.02;
scene.add(key);
const fill = new THREE.DirectionalLight('#CFE3FF', 0.5); fill.position.set(-7, 4, -2); scene.add(fill);
const rim  = new THREE.DirectionalLight('#FFD1DC', 0.7); rim.position.set(-2, 6, -8);  scene.add(rim);

/* ── ground slab (soft, rounded — contact shadows land on it) ─────────────── */
{GROUND_BLOCK}

/* ── model ────────────────────────────────────────────────────────────────── */
const rig = {BUILD}();
scene.add(rig.group);
{SKY_BLOCK}

/* ── camera ───────────────────────────────────────────────────────────────── */
const CAM = INFO.cam;
const CHASE = CAM === 'chase';
const camera = new THREE.PerspectiveCamera(CHASE ? 40 : CAM.fov, W / H, 0.1, 120);
const controls = new OrbitControls(camera, renderer.domElement);
if (!CHASE) {{
  camera.position.set(...CAM.position);
  controls.target.set(...CAM.target);
  controls.update();               // sync camera orientation (also needed in still mode)
}}
controls.enableDamping = true; controls.dampingFactor = 0.08;
controls.maxPolarAngle = Math.PI * 0.52;

/* ── loop / still contract ────────────────────────────────────────────────── */
function pose(t) {{
  {ANIMATE}(rig, t, {{ loop }});
  if (sky) sky.userData.animate(t);
  if (CHASE) chaseCamera(camera, rig, t, {{ loop }});
}}
window.__seek = t => {{ pose(t % loop); renderer.render(scene, camera); }};

if (STILL) {{
  document.getElementById('hud').classList.add('hide');
  requestAnimationFrame(() => {{ window.__seek(stillT); window.__ready = true; }});
}} else {{
  const clock = new THREE.Clock();
  renderer.setAnimationLoop(() => {{
    const t = (clock.getElapsedTime() * speed) % loop;
    pose(t);
    if (!CHASE) controls.update();
    renderer.render(scene, camera);
    window.__ready = true;
  }});
  document.querySelectorAll('#hud button[data-mode]').forEach(b => {{
    if (b.dataset.mode === mode) b.classList.add('ghost');
    b.addEventListener('click', () => {{
      mode = b.dataset.mode;
      document.querySelectorAll('#hud button[data-mode]').forEach(x => x.classList.remove('ghost'));
      b.classList.add('ghost');
    }});
  }});
}}
</script>
</body>
</html>
"""

MODELS = [
    dict(key='human', title='Milo — Stylized Human', style='Puffy / Bubbly',
         module='../../models/human.js', src='examples/human-character/threejs-human.js', build='buildHuman',
         animate='animateHuman', bg='#FFF6EC', fg='#5B4B49', accent='#E8639B',
         ground=('#B7E4C7', True), extra_imports=''),
    dict(key='cat', title='Mochi — Puffy Cat', style='Puffy / Bubbly',
         module='../../models/cat.js', src='examples/fluffy-cat/threejs-cat.js', build='buildCat',
         animate='animateCat', bg='#FFF6EC', fg='#5B4B49', accent='#FFADAD',
         ground=('#B7E4C7', True), extra_imports=''),
    dict(key='jet', title='Swift — Jet Fighter', style='Low-poly Flat',
         module='../../models/jet.js', src='examples/jet-fighter/threejs-jet.js', build='buildJet',
         animate='animateJet', bg='#BDE0FE', fg='#264653', accent='#E76F51',
         ground=None, extra_imports=', buildSky, chaseCamera', sky=True),
    dict(key='robot', title='Bolt — Toy Mech', style='Toy Hard-surface',
         module='../../models/robot.js', src='examples/robot-mech/threejs-robot.js', build='buildRobot',
         animate='animateRobot', bg='#E9EDF4', fg='#262B3A', accent='#00BBA7',
         ground=('#C9D3E0', True), extra_imports=''),
    dict(key='car', title='Jelly — City Car', style='Puffy Product',
         module='../../models/car.js', src='examples/sports-car/threejs-car.js', build='buildCar',
         animate='animateCar', bg='#FDF6EC', fg='#5B4B49', accent='#FF6B6B',
         ground=('#D8D2C4', True), extra_imports=''),
]

# Mode buttons are injected from the modules' INFO; keep a static map here (parsed from modules).
MODES = {
    'human': ['walk', 'idle', 'wave'],
    'cat': ['hop', 'loaf'],
    'jet': ['patrol'],
    'robot': ['patrol', 'idle'],
    'car': ['showroom', 'drive'],
}

for m in MODELS:
    modes = MODES[m['key']]
    buttons = ' '.join(f'<button data-mode="{x}">{x}</button>' for x in modes)
    ground_block = ''
    if m['ground']:
        color, shadows = m['ground']
        ground_block = f"""const ground = new THREE.Mesh(new RoundedBoxGeometry(16, 1.2, 12, 5, 0.5),
  new THREE.MeshStandardMaterial({{ color: '{color}', roughness: 0.75 }}));
ground.position.y = -0.6; ground.receiveShadow = true; scene.add(ground);"""
    sky_block = "const sky = buildSky(loop); scene.add(sky);" if m.get('sky') else 'const sky = null;'
    html = TEMPLATE.format(
        TITLE=m['title'], STYLE=m['style'], BG=m['bg'], FG=m['fg'], ACCENT=m['accent'],
        MODE_BUTTONS=buttons, BUILD=m['build'], ANIMATE=m['animate'],
        MODULE=m['module'], EXTRA_IMPORTS=m['extra_imports'],
        FOG='16, 60' if m['ground'] else '30, 90',
        GROUND_BLOCK=ground_block, SKY_BLOCK=sky_block,
    )
    out = os.path.join(ROOT, 'docs', 'demos', m['key'], 'index.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w') as f:
        f.write(html)
    print('wrote', os.path.relpath(out, ROOT))

# docs/models/ — Pages-served copies of the canonical example modules
models_dir = os.path.join(ROOT, 'docs', 'models')
os.makedirs(models_dir, exist_ok=True)
for m in MODELS:
    shutil.copyfile(os.path.join(ROOT, m['src']), os.path.join(models_dir, m['key'] + '.js'))
    print('copied', m['src'], '→ docs/models/' + m['key'] + '.js')

print('done')
