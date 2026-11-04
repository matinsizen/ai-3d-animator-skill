/**
 * PRO 3D ANIMATOR — Example model: "Jelly", a cute rounded city car
 * ═══════════════════════════════════════════════════════════════════════════
 * Vehicle body from an extruded side-profile with beveled edges (the pro
 * trick for rounded car bodies in one operation), separate glass canopy,
 * cylindrical wheels with rims, emissive lights.
 * Animations (stateless, loop-safe):
 *   showroom — full turntable (the one legal linear motion), suspension
 *              idle-bob, subtle headlight breathing
 *   drive    — wheel spin, body bounce & roll over fake road bumps
 */
import * as THREE from 'three';

const C = {
  paint: '#FF6B6B', paintDark: '#E85A5A', glass: '#1D2E40',
  tire: '#22252B', rim: '#F4F1EA', light: '#FFF3B0', tail: '#E63946',
};
const mat = (color, extra = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.5, metalness: 0.1, ...extra });
const M = {
  paint: new THREE.MeshPhysicalMaterial({ color: C.paint, roughness: 0.3, clearcoat: 0.9, clearcoatRoughness: 0.2, metalness: 0.15 }),
  glass: new THREE.MeshStandardMaterial({ color: C.glass, roughness: 0.06, metalness: 0.7 }),
  tire: mat(C.tire, { roughness: 0.9 }),
  rim: mat(C.rim, { metalness: 0.6, roughness: 0.3 }),
  light: new THREE.MeshStandardMaterial({ color: '#FFF9DB', emissive: C.light, emissiveIntensity: 1.6 }),
  tail: new THREE.MeshStandardMaterial({ color: '#7A1D24', emissive: C.tail, emissiveIntensity: 1.4 }),
};

/* side profile in XY (x = length, y = height) — body stops at the beltline,
   the glass canopy forms the greenhouse above it (classic toy-car build) */
function bodyShape() {
  const s = new THREE.Shape();
  s.moveTo(-1.05, 0.34);
  s.lineTo(-1.08, 0.60);                                   // rear
  s.quadraticCurveTo(-0.98, 0.72, -0.70, 0.72);            // trunk lip
  s.lineTo(0.42, 0.68);                                    // beltline
  s.quadraticCurveTo(0.80, 0.64, 1.02, 0.56);              // hood
  s.quadraticCurveTo(1.12, 0.50, 1.10, 0.38);              // nose
  s.lineTo(1.02, 0.30);
  /* wheel arches (cut out counterclockwise) */
  s.lineTo(0.86, 0.30);
  s.absarc(0.62, 0.30, 0.24, 0, Math.PI, true);
  s.lineTo(-0.38, 0.30);
  s.absarc(-0.62, 0.30, 0.24, 0, Math.PI, true);
  s.lineTo(-1.05, 0.30);
  s.closePath();
  return s;
}
function glassShape() {
  const s = new THREE.Shape();
  s.moveTo(-0.66, 0.70);
  s.quadraticCurveTo(-0.50, 0.99, -0.10, 1.01);            // roof
  s.quadraticCurveTo(0.26, 0.99, 0.42, 0.70);              // windshield
  s.lineTo(-0.66, 0.70);
  s.closePath();
  return s;
}

export function buildCar() {
  const root = new THREE.Group();                 // origin at ground, car center
  const rig = { group: root };

  /* body — extrude across Z with bevel = rounded sides in one op */
  const bodyGeo = new THREE.ExtrudeGeometry(bodyShape(), {
    depth: 0.72, bevelEnabled: true, bevelThickness: 0.07, bevelSize: 0.07, bevelSegments: 4, curveSegments: 12,
  });
  bodyGeo.translate(0, 0, -0.36);
  const body = new THREE.Mesh(bodyGeo, M.paint);
  body.castShadow = true; body.receiveShadow = true; root.add(body);
  rig.body = body;

  /* glass canopy — wider than the roofline so the sides read as windows */
  const glassGeo = new THREE.ExtrudeGeometry(glassShape(), {
    depth: 0.66, bevelEnabled: true, bevelThickness: 0.04, bevelSize: 0.04, bevelSegments: 3, curveSegments: 10,
  });
  glassGeo.translate(0, 0.02, -0.33);
  const glass = new THREE.Mesh(glassGeo, M.glass);
  glass.castShadow = true; root.add(glass);

  /* lights */
  for (const s of [-1, 1]) {
    const head = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.055, 0.03, 14), M.light);
    head.rotation.x = Math.PI / 2; head.position.set(1.06, 0.47, 0.20 * s); root.add(head);
    const tailL = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.07, 0.16), M.tail);
    tailL.position.set(-1.09, 0.55, 0.22 * s); root.add(tailL);
  }

  /* bumpers + mirrors */
  const bumperF = new THREE.Mesh(new THREE.BoxGeometry(0.10, 0.10, 0.86), mat(C.paintDark));
  bumperF.position.set(1.10, 0.30, 0); root.add(bumperF);
  const bumperR = bumperF.clone(); bumperR.position.x = -1.10; root.add(bumperR);
  for (const s of [-1, 1]) {
    const mirror = new THREE.Mesh(new THREE.SphereGeometry(0.045, 12, 8), M.paint);
    mirror.scale.set(0.7, 0.7, 1); mirror.position.set(0.40, 0.74, 0.40 * s); root.add(mirror);
  }

  /* wheels: tire cylinder + rim + hub — spinning handled in animate() */
  rig.wheels = [];
  const wheel = (x, z) => {
    const g = new THREE.Group();
    const tire = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.24, 0.16, 20), M.tire);
    tire.rotation.x = Math.PI / 2; tire.castShadow = true; g.add(tire);
    for (let i = 0; i < 5; i++) {                          // spokes poke past the tire face so spin reads
      const spoke = new THREE.Mesh(new THREE.BoxGeometry(0.055, 0.40, 0.185), M.rim);
      spoke.rotation.z = Math.PI * i / 2.5; g.add(spoke);
    }
    const hub = new THREE.Mesh(new THREE.SphereGeometry(0.055, 10, 8), M.rim);
    hub.position.z = 0.095; g.add(hub);
    g.position.set(x, 0.26, z);
    root.add(g); rig.wheels.push(g);
  };
  wheel(0.62, 0.44); wheel(0.62, -0.44); wheel(-0.62, 0.44); wheel(-0.62, -0.44);

  return rig;
}

/* ═══════════════════════ animation (pure function of t) ═══════════════════ */
const τ = Math.PI * 2;

/** pose the car at time t. opts: { mode:'showroom'|'drive' } */
export function animateCar(rig, t, opts = {}) {
  const T = opts.loop ?? INFO.loop;
  const mode = opts.mode ?? INFO.mode;

  /* reset */
  rig.group.rotation.set(0, 0, 0);
  rig.group.position.set(0, 0, 0);
  rig.body.position.set(0, 0, 0); rig.body.rotation.set(0, 0, 0);
  for (const w of rig.wheels) { w.rotation.set(0, 0, 0); w.position.y = 0.26; }

  if (mode === 'drive') {
    /* wheels spin (visible thanks to spokes), body bounces & rolls */
    const spin = τ * 3 * t / T * 6;
    for (const w of rig.wheels) w.rotation.z = -spin;
    rig.body.position.y = 0.02 * Math.sin(τ * 4 * t / T) + 0.012 * Math.sin(τ * 7 * t / T + 1);
    rig.body.rotation.z = 0.02 * Math.sin(τ * 3 * t / T);
    rig.body.rotation.x = 0.012 * Math.sin(τ * 5 * t / T + 2);
  } else {                                        // showroom turntable
    rig.group.rotation.y = τ * t / T;             // constant rotation — legal here
    rig.body.position.y = 0.014 * Math.sin(τ * t / 2);
    for (const w of rig.wheels) w.position.y = 0.26 + 0.004 * Math.sin(τ * t / 2 + 0.4);
    rig.wheels.forEach((w, i) => { w.rotation.y = 0; void i; });
    M.light.emissiveIntensity = 1.6 + 0.3 * Math.sin(τ * t / T);
  }
}

export const INFO = {
  name: 'Jelly — City Car',
  style: 'Puffy-ish Product (clearcoat paint)',
  modes: ['showroom', 'drive'],
  mode: 'showroom',
  loop: 8,
  cam: { fov: 30, position: [3.4, 1.6, 3.4], target: [0, 0.55, 0] },
  description: 'Extruded-profile car body with beveled rounded sides, glass canopy, spoked wheels; showroom turntable or drive mode with body roll.',
};
