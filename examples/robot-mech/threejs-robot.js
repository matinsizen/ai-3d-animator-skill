/**
 * PRO 3D ANIMATOR — Example model: "Bolt", a toy mech robot
 * ═══════════════════════════════════════════════════════════════════════════
 * Hard-surface character built from rounded boxes — the friendly-machine
 * look (no horror edges, but honest panel-like construction). Neon accents
 * are emissive-only, per the Neon bible's one rule.
 * Animations (stateless, loop-safe):
 *   patrol — heavy stomp walk: hip dip on plant, big feet, stiff elbows,
 *            torso counter-bob, servo head scan
 *   idle   — look-around, core pulse, antenna blink
 */
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

const C = {
  shell: '#3A4053', shellDark: '#262B3A', joint: '#8B95A8',
  visor: '#00F5D4', core: '#00F5D4', antenna: '#F15BB5', foot: '#232838',
};
const mat = (color, extra = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.5, metalness: 0.25, ...extra });
const M = {
  shell: mat(C.shell), shellDark: mat(C.shellDark), joint: mat(C.joint, { metalness: 0.5, roughness: 0.35 }),
  foot: mat(C.foot, { roughness: 0.7 }),
  visor: new THREE.MeshStandardMaterial({ color: '#062B26', emissive: C.visor, emissiveIntensity: 2.2, roughness: 0.2 }),
  core: new THREE.MeshStandardMaterial({ color: '#062B26', emissive: C.core, emissiveIntensity: 2.0, roughness: 0.3 }),
  antenna: new THREE.MeshStandardMaterial({ color: '#2B0F22', emissive: C.antenna, emissiveIntensity: 1.8, roughness: 0.3 }),
};

const rbox = (w, h, d, r, matRef) => {
  const m = new THREE.Mesh(new RoundedBoxGeometry(w, h, d, 4, r), matRef);
  m.castShadow = true; m.receiveShadow = true;
  return m;
};
const joint = (parent, x, y, z) => {
  const j = new THREE.Group(); j.position.set(x, y, z); parent.add(j); return j;
};
/* limb segment hanging from its pivot */
function limbSeg(w, h, d, r, matRef, drop) {
  const m = rbox(w, h, d, r, matRef);
  m.geometry.translate(0, -drop, 0);
  return m;
}

export function buildRobot() {
  const root = new THREE.Group();                 // origin at ground
  const rig = { group: root, emissives: [] };

  /* hips */
  const hips = joint(root, 0, 0.92, 0);
  hips.add(limbSeg(0.52, 0.22, 0.36, 0.06, M.shellDark, 0));
  rig.hips = hips;

  /* torso */
  const torso = joint(hips, 0, 0.08, 0);
  const chest = rbox(0.62, 0.52, 0.42, 0.09, M.shell);
  chest.position.y = 0.26;                     // grows UP from the torso joint
  torso.add(chest);
  /* chest core + vents */
  const core = new THREE.Mesh(new THREE.CylinderGeometry(0.075, 0.075, 0.03, 20), M.core);
  core.rotation.x = Math.PI / 2; core.position.set(0, 0.30, 0.225);
  torso.add(core); rig.emissives.push(core);
  for (const dy of [0.12, 0.04]) {
    const vent = new THREE.Mesh(new THREE.BoxGeometry(0.30, 0.025, 0.02), M.joint);
    vent.position.set(0, dy, 0.225); torso.add(vent);
  }
  rig.torso = torso;

  /* head: box + visor + ears + antenna */
  const neck = joint(torso, 0, 0.52, 0);
  neck.add(rbox(0.10, 0.08, 0.10, 0.02, M.joint));
  const head = joint(neck, 0, 0.10, 0);
  head.add(rbox(0.34, 0.26, 0.30, 0.06, M.shell));
  const visor = new THREE.Mesh(new RoundedBoxGeometry(0.24, 0.10, 0.05, 3, 0.02), M.visor);
  visor.position.set(0, 0.01, 0.15); head.add(visor); rig.emissives.push(visor);
  for (const s of [-1, 1]) {
    const ear = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.045, 0.05, 12), M.joint);
    ear.rotation.z = Math.PI / 2; ear.position.set(0.19 * s, 0.02, 0); head.add(ear);
  }
  const ant = new THREE.Mesh(new THREE.CapsuleGeometry(0.012, 0.10, 4, 8), M.joint);
  ant.position.set(0.10, 0.20, 0); head.add(ant);
  const antTip = new THREE.Mesh(new THREE.SphereGeometry(0.028, 12, 8), M.antenna);
  antTip.position.set(0.10, 0.27, 0); head.add(antTip); rig.emissives.push(antTip);
  rig.head = head;

  /* arms: shoulder ball → upper → elbow → forearm → gripper */
  const arm = (side) => {
    const shoulderJ = joint(torso, 0.38 * side, 0.44, 0);
    const ball = new THREE.Mesh(new THREE.SphereGeometry(0.10, 18, 12), M.joint);
    ball.castShadow = true; shoulderJ.add(ball);
    shoulderJ.add(limbSeg(0.15, 0.26, 0.15, 0.045, M.shell, 0.16));
    const elbowJ = joint(shoulderJ, 0, -0.34, 0);
    const elbow = new THREE.Mesh(new THREE.SphereGeometry(0.075, 16, 10), M.joint);
    elbow.castShadow = true; elbowJ.add(elbow);
    elbowJ.add(limbSeg(0.13, 0.24, 0.13, 0.04, M.shellDark, 0.14));
    const grip = joint(elbowJ, 0, -0.30, 0);
    for (const f of [-1, 1]) {
      const finger = limbSeg(0.05, 0.12, 0.07, 0.02, M.joint, 0.06);
      finger.position.x = 0.035 * f; grip.add(finger);
    }
    return { shoulderJ, elbowJ, grip };
  };
  rig.armL = arm(-1); rig.armR = arm(1);

  /* legs: hip → thigh → knee → shin → big flat foot (weight!) */
  const leg = (side) => {
    const thighJ = joint(hips, 0.17 * side, -0.10, 0);
    thighJ.add(limbSeg(0.20, 0.30, 0.20, 0.05, M.shell, 0.16));
    const kneeJ = joint(thighJ, 0, -0.36, 0);
    const knee = new THREE.Mesh(new THREE.SphereGeometry(0.085, 16, 10), M.joint);
    knee.castShadow = true; kneeJ.add(knee);
    kneeJ.add(limbSeg(0.17, 0.28, 0.17, 0.045, M.shellDark, 0.15));
    const ankleJ = joint(kneeJ, 0, -0.34, 0);
    const foot = rbox(0.24, 0.12, 0.34, 0.045, M.foot);
    foot.geometry.translate(0, -0.05, 0.05); ankleJ.add(foot);
    const toe = new THREE.Mesh(new THREE.BoxGeometry(0.20, 0.03, 0.06), M.visor);
    toe.position.set(0, -0.10, 0.22); ankleJ.add(toe); rig.emissives.push(toe);
    return { thighJ, kneeJ, ankleJ };
  };
  rig.legL = leg(-1); rig.legR = leg(1);

  /* rest pose */
  rig.armL.elbowJ.rotation.x = -0.5; rig.armR.elbowJ.rotation.x = -0.5;
  return rig;
}

/* ═══════════════════════ animation (pure function of t) ═══════════════════ */
const clamp01 = x => Math.min(1, Math.max(0, x));
const seg = (t, a, b, e = easeInOutCubic) => b > a ? e(clamp01((t - a) / (b - a))) : 1;
function easeInOutCubic(x) { return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; }
function easeOutCubic(x) { return 1 - Math.pow(1 - x, 3); }

/** pose the robot at time t. opts: { mode:'patrol'|'idle' } */
export function animateRobot(rig, t, opts = {}) {
  const T = opts.loop ?? INFO.loop;
  const mode = opts.mode ?? INFO.mode;
  const τ = Math.PI * 2;

  /* reset */
  rig.hips.position.set(0, 0.92, 0); rig.hips.rotation.set(0, 0, 0);
  rig.torso.rotation.set(0, 0, 0);
  rig.head.rotation.set(0, 0, 0);
  for (const leg of [rig.legL, rig.legR]) {
    leg.thighJ.rotation.set(0, 0, 0); leg.kneeJ.rotation.set(0, 0, 0); leg.ankleJ.rotation.set(0, 0, 0);
  }
  rig.armL.shoulderJ.rotation.set(0, 0, 0); rig.armR.shoulderJ.rotation.set(0, 0, 0);
  rig.armL.elbowJ.rotation.set(-0.5, 0, 0); rig.armR.elbowJ.rotation.set(-0.5, 0, 0);
  for (const e of rig.emissives) e.material.emissiveIntensity = e === rig.emissives[0] ? 2.0 : 2.2;

  if (mode === 'patrol') {
    const cadence = 3;                            // stomp cycles per loop
    const p = τ * (cadence * t / T);
    const swing = 0.5;

    /* heavy legs */
    rig.legL.thighJ.rotation.x = swing * Math.sin(p);
    rig.legR.thighJ.rotation.x = swing * Math.sin(p + Math.PI);
    rig.legL.kneeJ.rotation.x = 0.85 * Math.max(0, Math.sin(p + 0.7));
    rig.legR.kneeJ.rotation.x = 0.85 * Math.max(0, Math.sin(p + Math.PI + 0.7));
    rig.legL.ankleJ.rotation.x = -0.25 * Math.sin(p);
    rig.legR.ankleJ.rotation.x = -0.25 * Math.sin(p + Math.PI);

    /* weight: body dips on plant (|sin| bottom), sways side to side */
    rig.hips.position.y = 0.92 - 0.045 * Math.abs(Math.sin(p)) + 0.012;
    rig.hips.rotation.z = 0.045 * Math.sin(p);
    rig.hips.rotation.y = 0.07 * Math.sin(p);
    rig.torso.rotation.y = -0.11 * Math.sin(p);
    rig.torso.rotation.x = 0.04 + 0.015 * Math.sin(2 * p);

    /* stiff arms swing less, elbows locked */
    rig.armL.shoulderJ.rotation.x = -0.30 * Math.sin(p + 0.3);
    rig.armR.shoulderJ.rotation.x = -0.30 * Math.sin(p + Math.PI + 0.3);

    /* servo head scan (once per loop, eased) */
    rig.head.rotation.y = 0.5 * Math.sin(τ * t / T);

  } else {                                        // idle
    rig.hips.position.y = 0.92 + 0.012 * Math.sin(τ * t / 3);
    rig.hips.rotation.z = 0.015 * Math.sin(τ * t / 3);
    rig.head.rotation.y = 0.35 * Math.sin(τ * t / T);
    rig.head.rotation.x = 0.06 * Math.sin(τ * t / (T / 2));
    rig.armL.shoulderJ.rotation.x = 0.04 * Math.sin(τ * t / 3);
    rig.armR.shoulderJ.rotation.x = 0.04 * Math.sin(τ * t / 3 + 1);
    rig.armL.shoulderJ.rotation.z = 0.05; rig.armR.shoulderJ.rotation.z = -0.05;
  }

  /* emissive life: core pulse + antenna blink (loop-safe periods) */
  rig.emissives[0].material.emissiveIntensity = 2.0 + 0.8 * Math.sin(τ * 2 * t / T);
  rig.emissives[2].material.emissiveIntensity = (t % 2 < 0.12) ? 3.2 : 1.8;
}

export const INFO = {
  name: 'Bolt — Toy Mech',
  style: 'Toy Hard-surface + Neon accents',
  modes: ['patrol', 'idle'],
  mode: 'patrol',
  loop: 8,
  cam: { fov: 32, position: [2.6, 1.7, 3.4], target: [0, 0.95, 0] },
  description: 'Rounded-box mech with honest machine construction: stomp walk with weight dips, servo head scan, pulsing emissive core & visor.',
};
