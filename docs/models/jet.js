/**
 * PRO 3D ANIMATOR — Example model: "Swift", a low-poly jet fighter
 * ═══════════════════════════════════════════════════════════════════════════
 * Hard-surface vehicle built entirely from code: lathe fuselage, extruded
 * delta wings & twin canted tails, glass canopy, engine nozzles with
 * animated afterburner cones, under-wing missiles. Low-poly Flat style bible
 * (flatShading, bold palette, crisp sun).
 * Animation (stateless, loop-safe):
 *   patrol — the jet flies one full circle per loop (seam-free), banks into
 *            the turn, afterburners pulse, clouds drift; a chase camera
 *            follows with its own gentle bob.
 */
import * as THREE from 'three';

const C = {
  body: '#5C7A99', belly: '#E8E9EB', accent: '#E76F51',
  glass: '#1D2E40', flame: '#FFB703', flameHot: '#FB8500',
  cloud: '#FFFFFF', sky: '#BDE0FE',
};
const mat = (color, extra = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.8, metalness: 0, flatShading: true, ...extra });
const M = {
  body: mat(C.body), belly: mat(C.belly), accent: mat(C.accent),
  glass: new THREE.MeshStandardMaterial({ color: C.glass, roughness: 0.08, metalness: 0.6, flatShading: true }),
  nozzle: mat('#3A4750', { metalness: 0.7, roughness: 0.4 }),
  flame: new THREE.MeshBasicMaterial({ color: C.flame, transparent: true, opacity: 0.85 }),
  flameHot: new THREE.MeshBasicMaterial({ color: C.flameHot, transparent: true, opacity: 0.95 }),
  cloud: mat(C.cloud, { roughness: 1, emissive: '#8A93A6', emissiveIntensity: 0.45 }),
};

export function buildJet() {
  const root = new THREE.Group();                 // origin = jet center of mass
  const rig = { group: root, flames: [] };

  /* fuselage — lathe profile, nose toward +Z */
  const profile = [
    [0.10, 0.0], [0.30, 0.45], [0.42, 1.10], [0.40, 1.90], [0.30, 2.55], [0.16, 3.05], [0.02, 3.35],
  ].map(([x, y]) => new THREE.Vector2(x, y));
  const fus = new THREE.Mesh(new THREE.LatheGeometry(profile, 10), M.body);
  fus.geometry.rotateX(Math.PI / 2);              // lathe axis Y → Z (nose +Z)
  fus.geometry.translate(0, 0, -(3.35 / 2) + 0.9); // center roughly over origin
  fus.castShadow = true; root.add(fus);

  /* belly plate */
  const belly = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.12, 2.2), M.belly);
  belly.position.set(0, -0.30, 0.55); root.add(belly);

  /* canopy — squashed low-poly sphere */
  const canopy = new THREE.Mesh(new THREE.SphereGeometry(0.30, 10, 8), M.glass);
  canopy.scale.set(0.75, 0.62, 1.65); canopy.position.set(0, 0.32, 1.05); root.add(canopy);

  /* nose accent ring */
  const ring = new THREE.Mesh(new THREE.CylinderGeometry(0.17, 0.19, 0.10, 10), M.accent);
  ring.rotation.x = Math.PI / 2; ring.position.set(0, 0, 2.62); root.add(ring);

  /* delta wings — extruded shape, swept back */
  const wingShape = new THREE.Shape();
  wingShape.moveTo(0, 0.95); wingShape.lineTo(2.30, -0.85); wingShape.lineTo(2.30, -1.30);
  wingShape.lineTo(0.18, -0.55); wingShape.lineTo(0, -0.55); wingShape.closePath();
  const wingGeo = new THREE.ExtrudeGeometry(wingShape, { depth: 0.07, bevelEnabled: true, bevelThickness: 0.02, bevelSize: 0.02, bevelSegments: 1 });
  wingGeo.rotateX(Math.PI / 2);                   // shape XZ-plane → lie flat
  const wingR = new THREE.Mesh(wingGeo, M.body);
  wingR.position.set(0.18, 0.02, 0.35); wingR.castShadow = true; root.add(wingR);
  const wingL = wingR.clone(); wingL.scale.x = -1; wingL.position.x = -0.18; root.add(wingL);

  /* twin canted vertical stabilizers */
  const tailShape = new THREE.Shape();
  tailShape.moveTo(0, 0); tailShape.lineTo(0.62, 0); tailShape.lineTo(0.50, 0.55); tailShape.lineTo(0.16, 0.62); tailShape.closePath();
  const tailGeo = new THREE.ExtrudeGeometry(tailShape, { depth: 0.05, bevelEnabled: true, bevelThickness: 0.015, bevelSize: 0.015, bevelSegments: 1 });
  tailGeo.rotateY(Math.PI / 2);
  for (const s of [-1, 1]) {
    const fin = new THREE.Mesh(tailGeo, M.accent);
    fin.position.set(0.30 * s, 0.28, -1.15); fin.rotation.z = 0.32 * s; fin.castShadow = true; root.add(fin);
  }

  /* horizontal stabilizers */
  const hStab = new THREE.Mesh(new THREE.BoxGeometry(1.35, 0.06, 0.42), M.body);
  hStab.position.set(0, 0.05, -1.35); hStab.rotation.y = 0; hStab.castShadow = true; root.add(hStab);
  const stabTipR = new THREE.Mesh(new THREE.BoxGeometry(0.10, 0.10, 0.44), M.accent);
  stabTipR.position.set(0.68, 0.05, -1.35); root.add(stabTipR);
  const stabTipL = stabTipR.clone(); stabTipL.position.x = -0.68; root.add(stabTipL);

  /* engines: two nozzles + animated afterburner cones */
  for (const s of [-1, 1]) {
    const nozzle = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.13, 0.30, 10), M.nozzle);
    nozzle.rotation.x = Math.PI / 2; nozzle.position.set(0.20 * s, 0.05, -1.62); root.add(nozzle);
    const flame = new THREE.Mesh(new THREE.ConeGeometry(0.11, 1.0, 8, 1, true), M.flame);
    flame.rotation.x = -Math.PI / 2; flame.position.set(0.20 * s, 0.05, -2.25);
    const core = new THREE.Mesh(new THREE.ConeGeometry(0.06, 0.6, 8, 1, true), M.flameHot);
    core.rotation.x = -Math.PI / 2; core.position.set(0.20 * s, 0.05, -2.05);
    root.add(flame, core); rig.flames.push({ flame, core, s });
  }

  /* under-wing missiles */
  const missile = (x) => {
    const g = new THREE.Group();
    const bodyM = new THREE.Mesh(new THREE.CapsuleGeometry(0.05, 0.55, 4, 8), M.belly);
    bodyM.rotation.x = Math.PI / 2; g.add(bodyM);
    const tip = new THREE.Mesh(new THREE.ConeGeometry(0.05, 0.14, 8), M.accent);
    tip.rotation.x = Math.PI / 2; tip.position.z = 0.42; g.add(tip);
    g.position.set(x, -0.10, 0.45); root.add(g);
  };
  missile(1.30); missile(-1.30);

  return rig;
}

/* scenery: low-poly clouds kept OUTSIDE the camera orbit (radius > 13) */
export function buildSky(T = 8) {
  const clouds = new THREE.Group();
  const refs = [];
  const spots = [[-15, 3.5, -6, 1.7], [16, 5.0, -4, 2.3], [-12, 5.5, 11, 1.4], [14, 2.0, 12, 1.2], [1, 7.5, -16, 2.8], [-18, 3.0, 4, 1.1], [6, 4.5, 17, 1.5]];
  for (const [x, y, z, s] of spots) {
    const g = new THREE.Group();
    for (const [dx, dy, r] of [[0, 0, 0.8], [0.8, -0.1, 0.6], [-0.8, -0.12, 0.62], [0.15, 0.3, 0.55]]) {
      const p = new THREE.Mesh(new THREE.IcosahedronGeometry(r, 0), M.cloud);
      p.position.set(dx, dy, 0); g.add(p);
    }
    g.scale.setScalar(s); g.position.set(x, y, z);
    clouds.add(g); refs.push({ g, x, y, z });
  }
  clouds.userData.animate = (t) => {
    for (const [i, c] of refs.entries()) {
      c.g.position.x = c.x + 1.2 * Math.sin(Math.PI * 2 * t / T + i * 1.7);
      c.g.position.y = c.y + 0.25 * Math.sin(Math.PI * 2 * t / (T / 2) + i);
    }
  };
  return clouds;
}

/* ═══════════════════════ animation (pure function of t) ═══════════════════ */

/** pose the jet at time t. One full circle per loop → perfect seam. */
export function animateJet(rig, t, opts = {}) {
  const T = opts.loop ?? INFO.loop;
  const τ = Math.PI * 2;
  const R = 6.0;                                   // patrol radius
  const θ = τ * t / T;

  /* flight path: circle + gentle figure-bob (all periods divide T) */
  rig.group.position.set(
    R * Math.sin(θ),
    1.6 + 0.45 * Math.sin(2 * θ + 1.2),
    R * Math.cos(θ),
  );
  /* orientation: tangent to the circle, banked into the turn */
  rig.group.rotation.set(0, 0, 0);
  rig.group.rotateY(θ);                            // face travel direction
  rig.group.rotateZ(-0.42 - 0.06 * Math.sin(2 * θ)); // bank
  rig.group.rotateX(0.05 * Math.sin(2 * θ + 1.2));   // slight pitch breath

  /* afterburner pulse */
  const pulse = 0.75 + 0.45 * Math.abs(Math.sin(τ * 2 * t / T));
  for (const f of rig.flames) {
    f.flame.scale.set(1, pulse, 1);
    f.core.scale.set(1, pulse * 1.15, 1);
  }
}

/** chase camera — deterministic, follows the jet with a soft bob. */
export function chaseCamera(camera, rig, t, opts = {}) {
  const T = opts.loop ?? INFO.loop;
  const τ = Math.PI * 2;
  const θ = τ * t / T;
  const R = 6.0;
  const behind = 4.2, up = 1.6;
  const camPos = new THREE.Vector3(
    (R + behind) * Math.sin(θ + 0.55),
    2.4 + 0.5 * Math.sin(τ * t / (T / 2)),
    (R + behind) * Math.cos(θ + 0.55),
  );
  camera.position.copy(camPos);
  camera.lookAt(rig.group.position);
}

export const INFO = {
  name: 'Swift — Jet Fighter',
  style: 'Low-poly Flat',
  modes: ['patrol'],
  mode: 'patrol',
  loop: 8,
  cam: 'chase',                                    // demo uses chaseCamera()
  background: C.sky,
  description: 'Code-built delta-wing jet: lathe fuselage, extruded wings, canted twin tails, afterburner pulse, banked patrol loop with chase camera.',
};
