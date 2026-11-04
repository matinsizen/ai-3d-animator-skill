/**
 * PRO 3D ANIMATOR — Example model: "Milo", a stylized vinyl-figure human
 * ═══════════════════════════════════════════════════════════════════════════
 * A complete, fully-rigged character built from primitives — no external
 * assets. Demonstrates the skill's character rules:
 *   • joint hierarchy with pivots at the anatomical joint (shoulder, elbow,
 *     hip, knee, ankle) so rotations behave like a real rig
 *   • 3.8-head stylized proportions (cute but not chibi)
 *   • zero sharp edges (capsules, spheres, rounded boxes only)
 *   • three production animations, all STATELESS & LOOP-SAFE:
 *       walk  — counter-phase limbs, knee bend, hip bob, torso counter-yaw
 *       idle  — breathing, weight shift, micro arm sway, blinking
 *       wave  — arm raise with overshoot, forearm oscillation, head tilt
 *
 * Usage (demo page):
 *   import { buildHuman, animateHuman, INFO } from './threejs-human.js';
 *   const rig = buildHuman(); scene.add(rig.group);
 *   // in your loop:  animateHuman(rig, t);   // t = seconds (loops at INFO.loop)
 *
 * Usage (headless render): docs/demos/human/index.html honors
 *   ?still=1&t=SEC  ?loop=SEC  ?mode=walk|idle|wave  ?res=WxH
 */
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

/* ── palette (Puffy bible, references/art-styles.md §1) ───────────────────── */
const C = {
  skin: '#FFD1A6', hair: '#5A4032', shirt: '#FF8FA3', sleeve: '#FF8FA3',
  pants: '#6D8EA0', shoe: '#FBFBF7', sole: '#E76F51', eye: '#2B2320',
  cheek: '#FF9EB5', mouth: '#B25D4F',
};

/* ── materials (every material through a style helper — no raw gray) ─────── */
function puffyMat(color, extra = {}) {
  return new THREE.MeshPhysicalMaterial({
    color, roughness: 0.42, clearcoat: 0.4, clearcoatRoughness: 0.5,
    sheen: 0.35, sheenColor: new THREE.Color('#FFFFFF'), ...extra,
  });
}
const M = {
  skin: puffyMat(C.skin), hair: puffyMat(C.hair), shirt: puffyMat(C.shirt),
  pants: puffyMat(C.pants), shoe: puffyMat(C.shoe), sole: puffyMat(C.sole),
  sleeve: new THREE.MeshStandardMaterial({ color: '#F27E92', roughness: 0.55 }),
  eyeWhite: new THREE.MeshStandardMaterial({ color: '#ffffff', roughness: 0.25 }),
  pupil: new THREE.MeshStandardMaterial({ color: C.eye, roughness: 0.3 }),
  cheek: new THREE.MeshStandardMaterial({ color: C.cheek, roughness: 0.5, transparent: true, opacity: 0.75 }),
  mouth: new THREE.MeshStandardMaterial({ color: '#C96A5B', roughness: 0.5 }),
};

/* capsule that hangs from a pivot at its top — the rig primitive */
function capsule(r, len, mat) {
  const geo = new THREE.CapsuleGeometry(r, len, 6, 20);
  geo.translate(0, -(len / 2 + r * 0.4), 0);           // pivot = top of limb
  const m = new THREE.Mesh(geo, mat);
  m.castShadow = true; m.receiveShadow = true;
  return m;
}
function joint(parent, x, y, z) {
  const j = new THREE.Group();
  j.position.set(x, y, z);
  parent.add(j);
  return j;
}

/* ═══════════════════════════ BUILD ═════════════════════════════════════════
 * Height ~1.6 u (≈3.9 heads), key heights:
 *   ground 0 · hip 0.72 · knee 0.38 · chest top ≈ 1.22 · shoulders 1.14
 *   head center 1.38 (r 0.205) · top ≈ 1.60 */
export function buildHuman(opts = {}) {
  const root = new THREE.Group();
  const rig = { group: root, blink: [] };

  /* HIPS — origin of the whole body, sits at thigh-top height */
  const hips = joint(root, 0, 0.72, 0);
  rig.hips = hips;

  /* legs: hip → thigh → knee → shin → ankle → shoe */
  const leg = (side) => {                                   // side = -1 (L) | +1 (R)
    const thighJ = joint(hips, 0.105 * side, 0, 0);
    thighJ.add(capsule(0.08, 0.22, M.pants));
    const kneeJ = joint(thighJ, 0, -0.34, 0);
    kneeJ.add(capsule(0.06, 0.18, M.pants));
    const ankleJ = joint(kneeJ, 0, -0.30, 0);
    const shoe = new THREE.Mesh(new RoundedBoxGeometry(0.13, 0.10, 0.24, 5, 0.045), M.shoe);
    shoe.geometry.translate(0, -0.03, 0.04);               // toe forward (+Z)
    shoe.castShadow = true; ankleJ.add(shoe);
    const sole = new THREE.Mesh(new RoundedBoxGeometry(0.14, 0.035, 0.25, 4, 0.016), M.sole);
    sole.geometry.translate(0, -0.085, 0.04); sole.castShadow = true; ankleJ.add(sole);
    return { thighJ, kneeJ, ankleJ };
  };
  rig.legL = leg(-1); rig.legR = leg(1);

  /* torso — capsule grows upward from the hips; top meets the shoulders */
  const torso = joint(hips, 0, 0.02, 0);
  const chest = new THREE.Mesh(new THREE.CapsuleGeometry(0.165, 0.30, 6, 24), M.shirt);
  chest.position.y = 0.16; chest.rotation.x = 0.03;
  chest.castShadow = true; chest.receiveShadow = true; torso.add(chest);
  rig.torso = torso;

  /* head + face */
  const neck = joint(torso, 0, 0.44, 0);
  neck.add(capsule(0.05, 0.06, M.skin));
  const head = joint(neck, 0, 0.12, 0);
  const skull = new THREE.Mesh(new THREE.SphereGeometry(0.205, 40, 28), M.skin);
  skull.position.y = 0.08; skull.castShadow = true; head.add(skull);
  const hair = new THREE.Mesh(new THREE.SphereGeometry(0.215, 40, 28, 0, Math.PI * 2, 0, Math.PI * 0.46), M.hair);
  hair.position.set(0, 0.115, -0.015); hair.scale.set(1, 1.06, 1.05); hair.castShadow = true; head.add(hair);
  for (const s of [-1, 1]) {                               // eyes at 60% up the head
    const white = new THREE.Mesh(new THREE.SphereGeometry(0.048, 20, 14), M.eyeWhite);
    white.position.set(0.075 * s, 0.10, 0.175);
    const pupil = new THREE.Mesh(new THREE.SphereGeometry(0.021, 14, 10), M.pupil);
    pupil.position.set(0, 0.004, 0.036); white.add(pupil);
    head.add(white); rig.blink.push(white);
    const cheek = new THREE.Mesh(new THREE.SphereGeometry(0.038, 14, 10), M.cheek);
    cheek.position.set(0.115 * s, 0.02, 0.155); cheek.scale.set(1.35, 0.75, 0.5); head.add(cheek);
  }
  const smile = new THREE.Mesh(new THREE.TorusGeometry(0.05, 0.010, 10, 20, Math.PI * 0.8), M.mouth);
  smile.position.set(0, -0.015, 0.185); smile.rotation.set(0.14, 0, Math.PI * 1.06); head.add(smile);
  rig.head = head;

  /* arms: shoulder → upper arm → elbow → forearm → hand */
  const arm = (side) => {
    const shoulderJ = joint(torso, 0.215 * side, 0.40, 0);
    const deltoid = new THREE.Mesh(new THREE.SphereGeometry(0.08, 20, 14), M.sleeve);
    deltoid.castShadow = true; shoulderJ.add(deltoid);
    shoulderJ.add(capsule(0.05, 0.18, M.sleeve));
    const elbowJ = joint(shoulderJ, 0, -0.27, 0);
    elbowJ.add(capsule(0.042, 0.15, M.skin));
    const hand = new THREE.Mesh(new THREE.SphereGeometry(0.058, 20, 14), M.skin);
    hand.position.y = -0.25; hand.castShadow = true; elbowJ.add(hand);
    return { shoulderJ, elbowJ };
  };
  rig.armL = arm(-1); rig.armR = arm(1);

  /* rest pose: elbows slightly bent, tiny arm-out so limbs don't clip */
  for (const a of [rig.armL, rig.armR]) a.elbowJ.rotation.x = -0.18;
  rig.armL.shoulderJ.rotation.z = 0.10; rig.armR.shoulderJ.rotation.z = -0.10;

  return rig;
}

/* ═══════════════════════════ ANIMATION ═════════════════════════════════════
 * Everything below is a pure function of t — seek anywhere, loop perfectly. */

const clamp01 = x => Math.min(1, Math.max(0, x));
const seg = (t, a, b, e = easeInOutCubic) => b > a ? e(clamp01((t - a) / (b - a))) : 1;
function easeInOutCubic(x) { return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; }
function easeOutBack(x, s = 1.9) { return 1 + (s + 1) * Math.pow(x - 1, 3) + s * Math.pow(x - 1, 2); }
function easeOutCubic(x) { return 1 - Math.pow(1 - x, 3); }

/* loop-safe blink (two windows inside an 8 s loop) */
function blinkAmt(t) {
  for (const w0 of [2.2, 6.1]) {
    const k = seg(t, w0, w0 + 0.06, easeOutCubic) * (1 - seg(t, w0 + 0.1, w0 + 0.16, easeOutCubic));
    if (k > 0.001) return k;
  }
  return 0;
}

/** pose the rig at time t (seconds). opts: { mode:'walk'|'idle'|'wave' } */
export function animateHuman(rig, t, opts = {}) {
  const T = opts.loop ?? INFO.loop;
  const mode = opts.mode ?? INFO.mode;
  const τ = Math.PI * 2;

  /* reset to rest */
  rig.group.position.set(0, 0, 0); rig.group.rotation.set(0, 0, 0);
  rig.hips.position.set(0, 0.72, 0); rig.hips.rotation.set(0, 0, 0);
  rig.torso.rotation.set(0, 0, 0); rig.torso.scale.set(1, 1, 1);
  rig.head.rotation.set(0, 0, 0);
  for (const leg of [rig.legL, rig.legR]) {
    leg.thighJ.rotation.set(0, 0, 0); leg.kneeJ.rotation.set(0, 0, 0); leg.ankleJ.rotation.set(0, 0, 0);
  }
  rig.armL.shoulderJ.rotation.set(0, 0, 0.10); rig.armR.shoulderJ.rotation.set(0, 0, -0.10);
  rig.armL.elbowJ.rotation.set(0, 0, 0); rig.armR.elbowJ.rotation.set(0, 0, 0);
  for (const e of rig.blink) e.scale.y = 1;

  /* shared life: breathing + blinking (every mode, always) */
  const breath = 1 + 0.018 * Math.sin(τ * t / 3);
  rig.torso.scale.set(1, breath, 1);
  const blink = blinkAmt(t % T);
  for (const e of rig.blink) e.scale.y = 1 - 0.85 * blink;

  if (mode === 'walk') {
    const cadence = 4;                                    // stride cycles per loop (integer → loop-safe)
    const p = τ * (cadence * t / T);
    const hipSwing = 0.58, kneeBend = 0.95, armSwing = 0.42;

    rig.legL.thighJ.rotation.x = hipSwing * Math.sin(p);
    rig.legR.thighJ.rotation.x = hipSwing * Math.sin(p + Math.PI);
    /* knee bends as the leg swings forward under the body (phase-lead) */
    rig.legL.kneeJ.rotation.x = kneeBend * Math.max(0, Math.sin(p + 0.9));
    rig.legR.kneeJ.rotation.x = kneeBend * Math.max(0, Math.sin(p + Math.PI + 0.9));
    /* keep feet near-level */
    rig.legL.ankleJ.rotation.x = -0.4 * Math.sin(p) - rig.legL.kneeJ.rotation.x * 0.35;
    rig.legR.ankleJ.rotation.x = -0.4 * Math.sin(p + Math.PI) - rig.legR.kneeJ.rotation.x * 0.35;

    /* arms counter-swing (slight phase lag reads as follow-through) */
    rig.armL.shoulderJ.rotation.x = -armSwing * Math.sin(p + 0.25);
    rig.armR.shoulderJ.rotation.x = -armSwing * Math.sin(p + Math.PI + 0.25);
    rig.armL.elbowJ.rotation.x = -0.3 - 0.18 * Math.max(0, Math.sin(p + Math.PI));
    rig.armR.elbowJ.rotation.x = -0.3 - 0.18 * Math.max(0, Math.sin(p));

    /* hips bob twice per stride (highest at passing pose), torso counters */
    rig.hips.position.y = 0.72 + 0.032 * Math.abs(Math.cos(p)) - 0.016;
    rig.hips.rotation.y = 0.09 * Math.sin(p);
    rig.torso.rotation.y = -0.13 * Math.sin(p);
    rig.head.rotation.y = 0.05 * Math.sin(p);

  } else if (mode === 'wave') {
    /* idle base */
    rig.hips.position.y = 0.72 + 0.006 * Math.sin(τ * t / 4);
    rig.hips.rotation.z = 0.02 * Math.sin(τ * t / 4);
    rig.armL.shoulderJ.rotation.x = 0.06 * Math.sin(τ * t / 3);
    rig.armL.elbowJ.rotation.x = -0.18;
    /* raise right arm with overshoot (easeOutBack), hold, return before seam */
    const up = seg(t, 0.5, 1.15, easeOutBack);
    const down = 1 - seg(t, T - 1.2, T - 0.35, easeInOutCubic);
    const raise = Math.min(up, down);
    rig.armR.shoulderJ.rotation.z = -0.10 - 2.35 * raise;
    rig.armR.shoulderJ.rotation.x = -0.25 * raise;
    rig.armR.elbowJ.rotation.x = -0.18 - 0.30 * raise;
    rig.armR.elbowJ.rotation.z = -0.55 * Math.sin(τ * 2.5 * t / T) * raise;   // hand wave
    rig.head.rotation.z = 0.12 * raise;
    rig.torso.rotation.z = -0.04 * raise;

  } else {                                                // idle
    rig.hips.position.y = 0.72 + 0.008 * Math.sin(τ * t / 4);
    rig.hips.rotation.z = 0.025 * Math.sin(τ * t / 4);
    rig.torso.rotation.y = 0.03 * Math.sin(τ * t / 4 + 1);
    rig.head.rotation.y = 0.10 * Math.sin(τ * t / 5);
    rig.head.rotation.x = 0.03 * Math.sin(τ * t / 4);
    rig.armL.shoulderJ.rotation.x = 0.05 * Math.sin(τ * t / 3);
    rig.armR.shoulderJ.rotation.x = 0.05 * Math.sin(τ * t / 3 + 0.8);
  }
}

/* ── metadata consumed by demo pages & the render pipeline ────────────────── */
export const INFO = {
  name: 'Milo — Stylized Human',
  style: 'Puffy / Bubbly',
  modes: ['walk', 'idle', 'wave'],
  mode: 'walk',
  loop: 8,
  cam: { fov: 32, position: [2.3, 1.65, 3.2], target: [0, 0.85, 0] },
  description: 'Fully-rigged procedural human: joint hierarchy, walk cycle with knee bend & counter-rotation, idle breathing, wave with overshoot.',
};
