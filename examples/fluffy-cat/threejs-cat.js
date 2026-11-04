/**
 * PRO 3D ANIMATOR — Example model: "Mochi", a puffy cat (zero sharp edges)
 * ═══════════════════════════════════════════════════════════════════════════
 * The signature Puffy/Bubbly style at its purest: everything is spheres,
 * capsules and squashed spheres — an edge that could cut foam does not exist.
 * Animations (stateless, loop-safe):
 *   hop  — anticipation squash → parabola with stretch → impact squash →
 *          settle overshoot; tail and ears lag with overlap offsets
 *   loaf — pure idle: breathing, tail sine, slow blink, ear twitch
 */
import * as THREE from 'three';

const C = {
  fur: '#FFE8D6', furShade: '#F7D6BC', earIn: '#FFADAD', nose: '#E8639B',
  eye: '#2B2320', cheek: '#FFB3C1', paw: '#FFFDF8',
};
const puffyMat = (color, extra = {}) => new THREE.MeshPhysicalMaterial({
  color, roughness: 0.42, clearcoat: 0.5, clearcoatRoughness: 0.5,
  sheen: 0.4, sheenColor: new THREE.Color('#FFFFFF'), ...extra,
});
const M = {
  fur: puffyMat(C.fur), earIn: puffyMat(C.earIn), nose: puffyMat(C.nose),
  paw: puffyMat(C.paw),
  eyeWhite: new THREE.MeshStandardMaterial({ color: '#ffffff', roughness: 0.25 }),
  pupil: new THREE.MeshStandardMaterial({ color: C.eye, roughness: 0.3 }),
  cheek: new THREE.MeshStandardMaterial({ color: C.cheek, roughness: 0.5, transparent: true, opacity: 0.75 }),
};

const sphere = (r, mat, w = 32, h = 24) => {
  const m = new THREE.Mesh(new THREE.SphereGeometry(r, w, h), mat);
  m.castShadow = true; m.receiveShadow = true;
  return m;
};

export function buildCat() {
  const root = new THREE.Group();                 // origin at ground contact
  const rig = { group: root, blink: [], tail: [], ears: [] };

  const body = sphere(0.42, M.fur, 48, 32);
  body.scale.set(1, 0.88, 1.22); body.position.y = 0.40; root.add(body);
  rig.body = body;

  /* head — slightly overlapping the body, tilted up a touch (cute axis) */
  const headG = new THREE.Group();
  headG.position.set(0, 0.72, 0.30); root.add(headG);
  const head = sphere(0.30, M.fur, 48, 32);
  head.scale.set(1.12, 0.95, 1); headG.add(head);
  rig.headG = headG;

  /* ears: rounded capsules, tilted out; inner-ear pastel disc */
  for (const s of [-1, 1]) {
    const ear = new THREE.Group();
    ear.position.set(0.17 * s, 0.24, -0.02); ear.rotation.z = 0.45 * s;
    const outer = sphere(0.10, M.fur, 20, 14);
    outer.scale.set(0.75, 1.25, 0.55); ear.add(outer);
    const inner = sphere(0.055, M.earIn, 14, 10);
    inner.scale.set(0.7, 1.1, 0.4); inner.position.z = 0.035; ear.add(inner);
    headG.add(ear); rig.ears.push(ear);
  }

  /* face — eyes at 60% up, big pupils, blush, tiny nose */
  for (const s of [-1, 1]) {
    const white = sphere(0.062, M.eyeWhite, 18, 12);
    white.position.set(0.115 * s, 0.045, 0.245);
    const pupil = sphere(0.033, M.pupil, 14, 10);
    pupil.position.set(0, 0, 0.045); white.add(pupil);
    headG.add(white); rig.blink.push(white);
    const cheek = sphere(0.045, M.cheek, 12, 8);
    cheek.position.set(0.19 * s, -0.06, 0.21); cheek.scale.set(1.3, 0.7, 0.4); headG.add(cheek);
  }
  const nose = sphere(0.032, M.nose, 12, 8);
  nose.position.set(0, -0.015, 0.315); nose.scale.set(1.2, 0.8, 0.7); headG.add(nose);
  const muzzleL = sphere(0.05, M.fur, 14, 10);   // two tiny muzzle puffs
  muzzleL.position.set(-0.045, -0.045, 0.28); muzzleL.scale.set(1, 0.8, 0.6); headG.add(muzzleL);
  const muzzleR = muzzleL.clone(); muzzleR.position.x = 0.045; headG.add(muzzleR);

  /* whiskers — thin capsules, still rounded */
  const whisk = new THREE.MeshStandardMaterial({ color: '#FFFFFF', roughness: 0.4, transparent: true, opacity: 0.85 });
  for (const s of [-1, 1]) for (const [dy, rz] of [[0.0, 0.15], [-0.035, 0], [0.035, -0.15]]) {
    const w = new THREE.Mesh(new THREE.CapsuleGeometry(0.004, 0.09, 4, 6), whisk);
    w.geometry.translate(0, -0.045, 0);
    w.position.set(0.24 * s, -0.01 + dy, 0.22); w.rotation.z = (Math.PI / 2 + rz) * s; w.rotation.y = 0.35 * s;
    headG.add(w);
  }

  /* legs + paws (front pair forward, back pair wide — loaf stance) */
  rig.legs = [];
  for (const [x, z, front] of [[-0.20, 0.22, 1], [0.20, 0.22, 1], [-0.24, -0.22, 0], [0.24, -0.22, 0]]) {
    const leg = new THREE.Mesh(new THREE.CapsuleGeometry(0.095, 0.10, 6, 16), M.fur);
    leg.position.set(x, 0.14, z); leg.castShadow = true; root.add(leg);
    const paw = sphere(0.095, front ? M.paw : M.fur, 18, 12);
    paw.position.set(x, 0.07, z + 0.03); paw.scale.set(1, 0.62, 1.25); root.add(paw);
    rig.legs.push(leg);
  }

  /* tail: 6 spheres, each a bit smaller — posed by animate() into a sine */
  rig.tail = [];
  for (let i = 0; i < 6; i++) {
    const seg = sphere(0.075 - i * 0.008, M.fur, 18, 12);
    root.add(seg); rig.tail.push(seg);
  }
  return rig;
}

/* ═══════════════════════ animation (pure function of t) ═══════════════════ */
const clamp01 = x => Math.min(1, Math.max(0, x));
const seg = (t, a, b, e = easeInOutCubic) => b > a ? e(clamp01((t - a) / (b - a))) : 1;
function easeInOutCubic(x) { return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; }
function easeOutBack(x, s = 1.9) { return 1 + (s + 1) * Math.pow(x - 1, 3) + s * Math.pow(x - 1, 2); }
function easeOutCubic(x) { return 1 - Math.pow(1 - x, 3); }

/* volume-preserving squash — origin sits at the ground contact point */
function squash(obj, s) { const r = 1 / Math.sqrt(s); obj.scale.set(r, s, r); }

function blinkAmt(t) {
  for (const w0 of [1.8, 5.9]) {
    const k = seg(t, w0, w0 + 0.07, easeOutCubic) * (1 - seg(t, w0 + 0.11, w0 + 0.18, easeOutCubic));
    if (k > 0.001) return k;
  }
  return 0;
}

/** pose the cat at time t. opts: { mode:'hop'|'loaf' } */
export function animateCat(rig, t, opts = {}) {
  const T = opts.loop ?? INFO.loop;
  const mode = opts.mode ?? INFO.mode;
  const τ = Math.PI * 2;

  /* reset */
  rig.group.position.set(0, 0, 0); rig.group.rotation.set(0, 0, 0);
  rig.group.scale.set(1, 1, 1);
  rig.body.scale.set(1, 0.88, 1.22);
  rig.headG.position.set(0, 0.72, 0.30); rig.headG.rotation.set(0, 0, 0);
  for (const e of rig.blink) e.scale.y = 1;
  for (const [i, ear] of rig.ears.entries()) { ear.rotation.z = 0.45 * (i ? 1 : -1); ear.rotation.x = 0; }

  /* tail: flowing sine, tip lags most (overlap offsets: +0.35 rad per segment) */
  for (let i = 0; i < rig.tail.length; i++) {
    const f = i / (rig.tail.length - 1);
    const ph = τ * t / 2 - f * 0.85;
    rig.tail[i].position.set(
      0.02 * Math.sin(ph + f),
      0.30 + f * 0.16 + 0.03 * Math.sin(ph),
      -0.62 - f * 0.28 * Math.cos(f * 0.7) + 0.05 * f,
    );
    rig.tail[i].rotation.z = 0.12 * Math.sin(ph);
  }

  const blink = blinkAmt(t % T);
  for (const e of rig.blink) e.scale.y = 1 - 0.9 * blink;

  if (mode === 'hop') {
    /* one big hop per loop: 0–0.6 anticipate · 0.6–1.5 flight · land · settle */
    let s = 1, y = 0, stretch = 0;
    if (t < 0.60) {
      s = 1 - 0.20 * seg(t, 0.32, 0.60);                 // anticipation squash
    } else if (t < 1.50) {
      const p = seg(t, 0.60, 1.50, x => x);
      y = 0.95 * Math.sin(Math.PI * p);                  // parabola (moon gravity)
      stretch = 0.18 * Math.sin(Math.PI * p);            // stretch in flight
      s = 1 + stretch;
      rig.group.rotation.x = -0.08 * Math.sin(Math.PI * p);
    } else if (t < 1.66) {
      s = 1 - 0.24 * seg(t, 1.50, 1.66, easeOutCubic);   // impact squash
    } else {
      s = 0.76 + 0.24 * seg(t, 1.66, 2.45, easeOutBack); // settle overshoot
    }
    rig.group.position.y = y;
    squash(rig.group, s);
    /* tail whips with the jump (follow-through) */
    for (let i = 0; i < rig.tail.length; i++) {
      const f = i / (rig.tail.length - 1);
      rig.tail[i].position.y += 0.22 * stretch * f;
    }
    /* ears flap up in flight, pin back on launch (overlapping action) */
    const flap = mode === 'hop' ? Math.max(0, Math.sin(Math.PI * seg(t, 0.60, 1.50, x => x))) : 0;
    rig.ears[0].rotation.x = -0.3 * flap - 0.4 * seg(t, 0.32, 0.6);
    rig.ears[1].rotation.x = -0.3 * flap - 0.4 * seg(t, 0.32, 0.6);
    /* ear twitch events */
    for (const [ear, w0] of [[rig.ears[0], 4.1], [rig.ears[1], 5.3]]) {
      ear.rotation.z += 0.25 * Math.sin(τ * 6 * (t - w0)) * seg(t, w0, w0 + 0.35, easeOutCubic) * (1 - seg(t, w0 + 0.35, w0 + 0.5));
    }
  }

  /* shared life: breathing + head sway */
  const breath = 1 + 0.02 * Math.sin(τ * t / 2.5);
  rig.body.scale.y = 0.88 * breath;
  rig.headG.rotation.z = 0.04 * Math.sin(τ * t / 4);
  rig.headG.rotation.x = 0.03 * Math.sin(τ * t / 5 + 1);
}

export const INFO = {
  name: 'Mochi — Puffy Cat',
  style: 'Puffy / Bubbly',
  modes: ['hop', 'loaf'],
  mode: 'hop',
  loop: 8,
  cam: { fov: 34, position: [1.9, 1.15, 2.5], target: [0, 0.55, 0] },
  description: 'The zero-sharp-edges showcase: spheres-only cat with anticipation → stretch → squash → settle hopping, sine-lag tail, ear twitches, blinking.',
};
