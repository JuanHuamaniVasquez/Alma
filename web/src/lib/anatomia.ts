import * as THREE from "three";

/** Medidas del cuerpo sobre las que se coloca el esqueleto (unidades de escena; pies en y = 0, frente = +z, lado «L» = −x).
 *  Se MIDEN sobre la malla de la piel del personaje (así el esqueleto cabe en CADA tripulante) o, si no hay malla (traje EVA), salen de proporciones antropométricas estándar.
 *  Todo es ilustrativo: no es un escaneo ni un diagnóstico. */
export type Lado = { sh: THREE.Vector3; el: THREE.Vector3; wr: THREE.Vector3; tip: THREE.Vector3; hip: THREE.Vector3; kn: THREE.Vector3; an: THREE.Vector3; heel: THREE.Vector3; toe: THREE.Vector3 };
export type Medidas = {
  S: number;                                                      // estatura de la piel (cabeza sin pelo)
  head: THREE.Vector3; headW: number; headH: number; headD: number; neck: THREE.Vector3; pelvis: THREE.Vector3;
  L: Lado; R: Lado;
  torso: { y: number; hw: number; zb: number; zf: number }[];     // semianchura y límites de profundidad del tronco por altura (de la pelvis al cuello)
  medido: boolean;
};

const V = (x: number, y: number, z: number) => new THREE.Vector3(x, y, z);

/** Proporciones estándar sobre la estatura S (Drillis y Contini; Winter): usadas cuando no hay malla que medir. */
export function medidasPorDefecto(S: number): Medidas {
  const P = (x: number, y: number, z = 0) => V(x * S, y * S, z * S);
  const lado = (s: number): Lado => ({
    sh: P(s * 0.105, 0.815), el: P(s * 0.17, 0.705), wr: P(s * 0.24, 0.585), tip: P(s * 0.275, 0.49),
    hip: P(s * 0.055, 0.5), kn: P(s * 0.062, 0.275), an: P(s * 0.07, 0.045), heel: P(s * 0.07, 0.0, -0.045), toe: P(s * 0.075, 0.0, 0.1),
  });
  const torso = Array.from({ length: 20 }, (_, i) => { const y = 0.5 + i * 0.0185; return { y: y * S, hw: (y < 0.62 ? 0.085 : 0.095) * S, zb: -0.062 * S, zf: 0.07 * S }; });
  return { S, head: P(0, 0.935, 0.005), headW: 0.075 * S, headH: 0.115 * S, headD: 0.095 * S, neck: P(0, 0.865), pelvis: P(0, 0.52), L: lado(-1), R: lado(1), torso, medido: false };
}

type Cluster = { min: number; max: number; n: number; mx: number; mz: number; zmin: number; zmax: number };
const clusters = (pts: Float32Array, y0: number, dy: number, gap: number): Cluster[] => {
  const sel: number[] = [];
  for (let i = 0; i < pts.length; i += 3) if (Math.abs(pts[i + 1] - y0) <= dy) sel.push(i);
  sel.sort((a, b) => pts[a] - pts[b]);
  const out: Cluster[] = [];
  let c: Cluster | null = null, last = 0;
  for (const i of sel) {
    const x = pts[i], z = pts[i + 2];
    if (!c || x - last > gap) { c = { min: x, max: x, n: 0, mx: 0, mz: 0, zmin: z, zmax: z }; out.push(c); }
    c.max = x; c.n++; c.mx += x; c.mz += z; c.zmin = Math.min(c.zmin, z); c.zmax = Math.max(c.zmax, z); last = x;
  }
  for (const k of out) { k.mx /= k.n; k.mz /= k.n; }
  return out.filter((k) => k.n >= 4);
};

/** Mide la malla de piel del tripulante (la de más vértices: el cuerpo) y devuelve la posición de las articulaciones y el perfil del tronco. `root` ya debe estar posicionado (matrixWorld al día). */
export function medirCuerpo(root: THREE.Object3D): Medidas | null {
  root.updateMatrixWorld(true);
  let best: THREE.Mesh | null = null, bestN = 0;
  root.traverse((o) => {
    const m = o as THREE.Mesh;
    if (!m.isMesh || o.userData.kind !== "skin") return;
    const n = m.geometry.getAttribute("position").count;
    if (n > bestN) { best = m; bestN = n; }
  });
  if (!best || bestN < 3000) return null;
  const mesh = best as THREE.Mesh, pos = mesh.geometry.getAttribute("position");
  const pts = new Float32Array(pos.count * 3), v = new THREE.Vector3();
  let ymax = -Infinity, ymin = Infinity;
  for (let i = 0; i < pos.count; i++) { v.fromBufferAttribute(pos, i).applyMatrix4(mesh.matrixWorld); pts.set([v.x, v.y, v.z], i * 3); ymax = Math.max(ymax, v.y); ymin = Math.min(ymin, v.y); }
  const S = ymax - ymin, y = (f: number) => ymin + f * S, d = medidasPorDefecto(S);
  const gap = 0.022 * S, dy = 0.012 * S;                    // la malla es ligera: cortes gruesos y huecos amplios para no partir un grupo en pedazos

  // ---- piernas: centroide de cada pierna a la altura de cadera, rodilla y tobillo
  const pierna = (s: number, f: number) => {
    const c = clusters(pts, y(f), dy, gap).filter((k) => Math.sign(k.mx) === s).sort((a, b) => b.n - a.n)[0];
    return c ? V(c.mx, y(f), c.mz) : null;
  };
  // entrepierna: la altura más alta en que no hay puntos en el plano medio
  let yCrotch = y(0.47);
  for (let f = 0.56; f > 0.36; f -= 0.004) {                         // por debajo de la entrepierna ningún grupo cubre el plano medio
    const cs = clusters(pts, y(f), dy, gap);
    if (cs.length >= 2 && !cs.some((k) => k.min < -0.01 * S && k.max > 0.01 * S)) { yCrotch = y(f); break; }
  }
  const hipY = yCrotch + 0.04 * S;
  const lados: Record<string, Lado> = {};
  for (const s of [-1, 1]) {
    const base = s < 0 ? d.L : d.R;
    const hip = pierna(s, (hipY - ymin) / S) ?? base.hip, kn = pierna(s, 0.285) ?? base.kn, an = pierna(s, 0.045) ?? base.an;
    hip.y = hipY; kn.y = y(0.285); an.y = y(0.039);
    let zheel = Infinity, ztoe = -Infinity;
    for (let i = 0; i < pts.length; i += 3) if (pts[i + 1] < y(0.03) && Math.sign(pts[i]) === s && Math.abs(pts[i]) > 0.02 * S) { zheel = Math.min(zheel, pts[i + 2]); ztoe = Math.max(ztoe, pts[i + 2]); }
    lados[s < 0 ? "L" : "R"] = { ...base, hip, kn, an, heel: V(an.x, ymin, Number.isFinite(zheel) ? zheel + 0.012 * S : an.z - 0.04 * S), toe: V(an.x * 1.04, ymin, Number.isFinite(ztoe) ? ztoe - 0.004 * S : an.z + 0.1 * S) };
  }

  // ---- brazos: la fila de grupos de un corte bajo la axila (tronco en medio, un brazo a cada lado); eje = ajuste por centroides entre muñeca y codo
  const sdf = (s: number) => {
    const cen: THREE.Vector3[] = [];
    for (let f = 0.42; f <= 0.62; f += 0.02) {
      const cs = clusters(pts, y(f), dy, gap);
      if (cs.length < 3) continue;
      const k = s < 0 ? cs[0] : cs[cs.length - 1];
      if (Math.abs(k.mx) > 0.12 * S) cen.push(V(k.mx, y(f), k.mz));
    }
    return cen;
  };
  const fila = (s: number): { sh: THREE.Vector3; el: THREE.Vector3; wr: THREE.Vector3; tip: THREE.Vector3 } | null => {
    const cen = sdf(s);
    if (cen.length < 3) return null;
    const a = cen[0], b = cen[cen.length - 1];                    // punto más bajo y más alto medidos
    const dir = b.clone().sub(a).normalize();                     // hacia arriba por el brazo
    let tipY = Infinity;
    const aprox = (yy: number) => a.clone().add(dir.clone().multiplyScalar((yy - a.y) / dir.y));
    for (let i = 0; i < pts.length; i += 3) {                      // punta del dedo: el punto más bajo cercano al eje del brazo
      if (pts[i + 1] > a.y + 0.02 * S) continue;
      const e = aprox(pts[i + 1]);
      if (Math.hypot(pts[i] - e.x, pts[i + 2] - e.z) < 0.05 * S && Math.sign(pts[i]) === s) tipY = Math.min(tipY, pts[i + 1]);
    }
    const tip = aprox(Number.isFinite(tipY) ? tipY : y(0.4));
    const sh = aprox(y(0.80)), L = sh.distanceTo(tip), up = dir.clone();
    const el = sh.clone().addScaledVector(up.clone().negate(), 0.186 / 0.332 * (L - 0.108 * S));
    const wr = tip.clone().addScaledVector(up, 0.108 * S);
    return { sh, el, wr, tip };
  };
  const bl = fila(-1), br = fila(1);
  const L: Lado = { ...lados.L, ...(bl ?? { sh: d.L.sh, el: d.L.el, wr: d.L.wr, tip: d.L.tip }) };
  const R: Lado = { ...lados.R, ...(br ?? { sh: d.R.sh, el: d.R.el, wr: d.R.wr, tip: d.R.tip }) };

  // ---- tronco: perfil por altura del grupo que contiene el plano medio (por encima de la axila los brazos se funden: se acota por la anchura de hombros)
  const torso: Medidas["torso"] = [];
  const hwLim = Math.max(Math.abs(L.sh.x), Math.abs(R.sh.x)) * 0.92;
  for (let f = 0.49; f <= 0.865; f += 0.0185) {
    const cs = clusters(pts, y(f), dy, gap), c = cs.find((k) => k.min <= 0 && k.max >= 0) ?? cs[0];
    if (!c) continue;
    torso.push({ y: y(f), hw: Math.min((c.max - c.min) / 2, hwLim), zb: c.zmin, zf: c.zmax });
  }
  const neckC = torso.reduce((m, t) => (t.y > y(0.8) && t.hw < m.hw ? t : m), { y: y(0.86), hw: 9, zb: 0, zf: 0 });
  const cabeza = (() => {
    const top = pts.filter((_, i) => i % 3 === 1).reduce((a, b) => Math.max(a, b), 0);
    let sx = 0, sz = 0, n = 0, zmin = Infinity, zmax = -Infinity, xmin = Infinity, xmax = -Infinity;
    for (let i = 0; i < pts.length; i += 3) if (pts[i + 1] > top - 0.1 * S && pts[i + 1] > y(0.885)) { sx += pts[i]; sz += pts[i + 2]; n++; zmin = Math.min(zmin, pts[i + 2]); zmax = Math.max(zmax, pts[i + 2]); xmin = Math.min(xmin, pts[i]); xmax = Math.max(xmax, pts[i]); }
    return n ? { c: V(sx / n, top - 0.0585 * S, sz / n), w: xmax - xmin, d: zmax - zmin } : null;
  })();
  const zMed = torso.length ? (torso[0].zb + torso[0].zf) / 2 : 0;
  return {
    ...d, S, medido: true, L, R, torso: torso.length > 4 ? torso : d.torso,
    head: cabeza?.c ?? d.head, headW: cabeza ? cabeza.w * 0.88 : d.headW, headH: 0.117 * S, headD: cabeza ? cabeza.d * 0.9 : d.headD,
    neck: V(0, neckC.hw < 9 ? neckC.y : y(0.86), neckC.hw < 9 ? (neckC.zb + neckC.zf) / 2 : 0), pelvis: V(0, hipY - 0.02 * S, zMed),
  };
}

/** Interpola el perfil del tronco a la altura yy. */
export function perfil(m: Medidas, yy: number) {
  const t = m.torso;
  if (yy <= t[0].y) return t[0];
  if (yy >= t[t.length - 1].y) return t[t.length - 1];
  const i = t.findIndex((p) => p.y >= yy), a = t[i - 1], b = t[i], k = (yy - a.y) / (b.y - a.y);
  return { y: yy, hw: a.hw + (b.hw - a.hw) * k, zb: a.zb + (b.zb - a.zb) * k, zf: a.zf + (b.zf - a.zf) * k };
}
