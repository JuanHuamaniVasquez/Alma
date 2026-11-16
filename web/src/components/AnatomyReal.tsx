"use client";
import { useFrame } from "@react-three/fiber";
import { useGLTF } from "@react-three/drei";
import { Component, useEffect, useMemo, type ReactNode } from "react";
import * as THREE from "three";
import { perfil, type Medidas } from "@/lib/anatomia";
import { Anatomy, type OrganState } from "./Anatomy";

/** Anatomía REAL: piezas segmentadas de BodyParts3D 4.0 (cuerpo masculino adulto; DBCLS, CC BY 4.0) — 189 huesos, 14 cartílagos costales y 21 grupos de órganos —
 *  deformadas al cuerpo MEDIDO de cada tripulante: las extremidades se alinean por articulaciones (hombro-codo-muñeca-dedos, cadera-rodilla-tobillo-dedos del pie), el tronco y los
 *  órganos se escalan a su perfil, la cabeza a su tamaño. Ilustrativo: no es un escaneo del personaje (que es ficticio) ni un diagnóstico.
 *  Si el modelo no carga, vuelve a la anatomía esquemática (`Anatomy`). Reconocimiento: «BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International». */
useGLTF.preload("/models/anatomy_bp3d.glb");

type V3 = THREE.Vector3;
const V = (x = 0, y = 0, z = 0) => new THREE.Vector3(x, y, z);
type Pieza = { mesh: THREE.Mesh; nombre: string; cat: string; grupo: string; lado: "izq" | "der" | null };   // izq/der = del PACIENTE (izquierda = +x)

const posiciones = (m: THREE.Mesh): Float32Array => {
  const a = m.geometry.getAttribute("position"), out = new Float32Array(a.count * 3);
  for (let i = 0; i < a.count; i++) { out[3 * i] = a.getX(i); out[3 * i + 1] = a.getY(i); out[3 * i + 2] = a.getZ(i); }
  return out;
};
const centro = (p: Float32Array, pred: (x: number, y: number, z: number) => boolean) => {
  const c = V(); let n = 0;
  for (let i = 0; i < p.length; i += 3) if (pred(p[i], p[i + 1], p[i + 2])) { c.x += p[i]; c.y += p[i + 1]; c.z += p[i + 2]; n++; }
  return n ? c.multiplyScalar(1 / n) : c;
};
const rango = (p: Float32Array, eje: 0 | 1 | 2) => { let a = Infinity, b = -Infinity; for (let i = eje; i < p.length; i += 3) { a = Math.min(a, p[i]); b = Math.max(b, p[i]); } return [a, b] as const; };

/** Cadena rígida con escala: lleva el segmento A→B del modelo al segmento A'→B' del cuerpo. */
const cadena = (A: V3, B: V3, A2: V3, B2: V3) => {
  const d1 = B.clone().sub(A), d2 = B2.clone().sub(A2), k = d2.length() / Math.max(1e-6, d1.length());
  const q = new THREE.Quaternion().setFromUnitVectors(d1.clone().normalize(), d2.clone().normalize());
  return (v: V3, peso = 1) => { const r = v.clone().sub(A).applyQuaternion(q).multiplyScalar(k).add(A2); return peso >= 1 ? r : v.clone().lerp(r, peso); };
};

type Ajuste = { grupo: Map<string, Pieza[]>; todas: Pieza[]; sueno: V3; hipotalamo: V3; braquial: [V3, V3] };

function construir(scene: THREE.Object3D, m: Medidas): Ajuste {
  const piezas: Pieza[] = [];
  scene.updateMatrixWorld(true);
  scene.traverse((o) => {
    const mesh = o as THREE.Mesh;
    if (!mesh.isMesh) return;
    const [, nombreRaw, cat] = mesh.name.split("|");                       // GLTFLoader cambia espacios por «_» en los nombres de nodo
    if (!nombreRaw || !cat) return;
    const nombre = nombreRaw.replace(/_/g, " ");
    const lado = /\bleft\b/.test(nombre) || /\bleft\b/.test(cat) ? "izq" : /\bright\b/.test(nombre) ? "der" : null;
    const c = mesh.clone(); c.userData.mw = mesh.matrixWorld.clone();
    piezas.push({ mesh: c, nombre, cat, grupo: cat.startsWith("organo-") ? cat.slice(7) : cat, lado });
  });
  const P = new Map<string, Float32Array>(), por = (n: string) => piezas.find((p) => p.nombre === n);
  for (const p of piezas) {                                          // el nodo trae escala 0,001 y un giro de 180°: se hornea en los vértices (y se orienta a la escena) y la malla queda en la identidad
    p.mesh.geometry = p.mesh.geometry.clone();
    const mw = p.mesh.userData.mw as THREE.Matrix4, a = p.mesh.geometry.getAttribute("position"), v = V();
    const out = new Float32Array(a.count * 3);
    for (let i = 0; i < a.count; i++) { v.set(a.getX(i), a.getY(i), a.getZ(i)).applyMatrix4(mw); out[3 * i] = -v.x; out[3 * i + 1] = v.y; out[3 * i + 2] = -v.z; }   // −x, −z: el exportador deja el cuerpo mirando a −z; la escena lo quiere a +z
    p.mesh.geometry.setAttribute("position", new THREE.BufferAttribute(out, 3));
    p.mesh.position.set(0, 0, 0); p.mesh.rotation.set(0, 0, 0); p.mesh.scale.set(1, 1, 1); p.mesh.updateMatrix();
    P.set(p.nombre, out.slice());
  }
  const get = (n: string) => P.get(n) ?? new Float32Array(0);
  const top = (n: string, f: number) => { const p = get(n), [a, b] = rango(p, 1); return centro(p, (_x, y) => y > b - f * (b - a)); };
  const bot = (n: string, f: number) => { const p = get(n), [a, b] = rango(p, 1); return centro(p, (_x, y) => y < a + f * (b - a)); };

  // ---- referencias del modelo (patient's left = +x en ambos): cadera, rodilla, tobillo, hombro, codo, muñeca, punta de los dedos, talón, dedos del pie
  const bp = (L: "left" | "right") => {
    const fem = `${L} femur`, tib = `${L} tibia`, hum = `${L} humerus`, rad = `${L} radius`, uln = `${L} ulna`, cal = `${L} calcaneus`;
    const hip = top(fem, 0.035), knee = top(tib, 0.04).add(bot(fem, 0.05)).multiplyScalar(0.5), ankle = bot(tib, 0.035);
    const sh = top(hum, 0.05), el = bot(hum, 0.05).add(top(uln, 0.05)).multiplyScalar(0.5), wr = bot(rad, 0.04).add(bot(uln, 0.03)).multiplyScalar(0.5);
    let tip = wr.clone(), dm = 0, ztoe = -Infinity;
    for (const p of piezas) {
      if (!p.nombre.includes(L)) continue;
      if (/thumb|finger|metacarpal/.test(p.nombre)) { const a = get(p.nombre); for (let i = 0; i < a.length; i += 3) { const d = Math.hypot(a[i] - wr.x, a[i + 1] - wr.y, a[i + 2] - wr.z); if (d > dm) { dm = d; tip = V(a[i], a[i + 1], a[i + 2]); } } }
      if (/toe/.test(p.nombre)) { const a = get(p.nombre); for (let i = 0; i < a.length; i += 3) ztoe = Math.max(ztoe, a[i + 2]); }
    }
    const c = get(cal), [z0] = rango(c, 2), [suelo] = rango(c, 1), heel = V(centro(c, () => true).x, suelo, z0), toe = V(ankle.x, suelo, ztoe);
    return { hip, knee, ankle, sh, el, wr, tip, heel, toe };
  };
  const BL = bp("left"), BR = bp("right");                          // paciente izquierdo (+x) y derecho (−x) del modelo
  const CL = m.R, CR = m.L;                                          // medidas del personaje: m.R es su +x = izquierda del paciente

  // ---- columna del modelo (alturas y z de cada vértebra) y del personaje
  const vert = piezas.filter((p) => /vertebra$/.test(p.nombre) || p.nombre === "atlas" || p.nombre === "axis").map((p) => { const c = centro(get(p.nombre), () => true); return c; }).sort((a, b) => a.y - b.y);
  const zSpineBP = (y: number) => { if (!vert.length) return 0; if (y <= vert[0].y) return vert[0].z; for (let i = 1; i < vert.length; i++) if (y <= vert[i].y) { const a = vert[i - 1], b = vert[i], k = (y - a.y) / (b.y - a.y); return a.z + (b.z - a.z) * k; } return vert[vert.length - 1].z; };
  const zSpineCh = (y: number) => { const p = perfil(m, Math.min(y, m.neck.y)); const z0 = p.zb + 0.3 * (p.zf - p.zb); if (y <= m.neck.y) return z0; const k = Math.min(1, (y - m.neck.y) / (0.1 * m.S)); return z0 + (m.head.z - 0.015 * m.S - z0) * k * k * (3 - 2 * k); };
  const yHipBP = (BL.hip.y + BR.hip.y) / 2, yHipCh = (CL.hip.y + CR.hip.y) / 2;
  const c7 = por("seventh cervical vertebra") ? centro(get("seventh cervical vertebra"), () => true).y : yHipBP + 0.5, atlas = por("atlas") ? centro(get("atlas"), () => true).y : c7 + 0.08;
  const yBaseCh = m.head.y - 0.0265 * m.S;                            // el atlas queda ≈ 0,085 S por debajo de la coronilla (antes 0,115 S: el cráneo bajaba demasiado)
  const cObj = m.neck.y - 0.03 * m.S;                                  // C7 está ≈ 0,03 S por debajo del punto más estrecho del cuello
  const mapY = (y: number) => {                                       // altura del modelo → altura del personaje (tres tramos: cadera–C7, C7–atlas, resto)
    if (y <= c7) return yHipCh + (y - yHipBP) * ((cObj - yHipCh) / (c7 - yHipBP));
    if (y <= atlas) return cObj + (y - c7) * ((yBaseCh - cObj) / Math.max(1e-6, atlas - c7));
    return yBaseCh + (y - atlas) * ((m.head.y - yBaseCh) / Math.max(1e-6, (m.head.y - yBaseCh) + 0.02));
  };
  // anchuras y fondo: caja torácica del modelo contra la del personaje
  const costillas = piezas.filter((p) => /rib$/.test(p.nombre));
  let xRib = 0, zRibA = Infinity, zRibB = -Infinity;
  for (const p of costillas) { const a = get(p.nombre); for (let i = 0; i < a.length; i += 3) { xRib = Math.max(xRib, Math.abs(a[i])); zRibA = Math.min(zRibA, a[i + 2]); zRibB = Math.max(zRibB, a[i + 2]); } }
  const yTor = yHipBP + 0.55 * (c7 - yHipBP), pTor = perfil(m, mapY(yTor));
  const sxChest = (0.82 * pTor.hw) / Math.max(1e-6, xRib);
  const sz = (0.9 * (pTor.zf - pTor.zb)) / Math.max(1e-6, zRibB - zRibA);
  const sxPel = Math.abs(CL.hip.x - CR.hip.x) / Math.max(1e-6, Math.abs(BL.hip.x - BR.hip.x));
  const sxAt = (y: number) => { const k = Math.min(1, Math.max(0, (y - yHipBP) / Math.max(1e-6, yTor - yHipBP))); return sxPel + (sxChest - sxPel) * k; };
  const torso = (v: V3): V3 => {
    const yy = mapY(v.y), s = sxAt(v.y);
    return V(v.x * s, yy, zSpineCh(yy) + (v.z - zSpineBP(v.y)) * sz);
  };

  // ---- cabeza: escala uniforme y centro del cráneo → centro de la cabeza medida
  const cr = get("neurocranium"), mand = get("mandible");
  const [cy0, cy1] = rango(cr, 1), [my0] = rango(mand, 1);
  const centroCr = V((rango(cr, 0)[0] + rango(cr, 0)[1]) / 2, (cy0 + cy1) / 2, (rango(cr, 2)[0] + rango(cr, 2)[1]) / 2);
  const anchoCr = rango(cr, 0)[1] - rango(cr, 0)[0], kHead = (0.8 * 0.8 * m.headW) / Math.max(1e-6, anchoCr);   // ancho del cráneo = 0,64 del de la cabeza medida (0,8 anatómico × 0,8 pedido: el humano lo ve grande frente al holograma)
  const anclaBP = por("atlas") ? centro(get("atlas"), () => true) : centroCr, anclaCh = torso(anclaBP);          // el cráneo se apoya en el atlas (C1) de la columna ajustada: unido al cuello, no al centro de la piel de la cabeza
  const cabeza = (v: V3): V3 => v.clone().sub(anclaBP).multiplyScalar(kHead).add(anclaCh);

  // ---- hombro: el brazo parte de donde el TÓRAX ajustado deja el hombro del modelo (así queda unido a su clavícula y omóplato); codo y muñeca siguen las medidas del personaje
  const hombro = { left: torso(BL.sh), right: torso(BR.sh) };
  const flex = V(0, 0, -0.036 * m.S);                                   // brazo relajado: el codo cede hacia atrás y el antebrazo se adelanta (≈ 20° de flexión), no un palo recto
  const codo = { left: hombro.left.clone().lerp(CL.wr, 0.186 / 0.332).add(flex), right: hombro.right.clone().lerp(CR.wr, 0.186 / 0.332).add(flex) };
  const brazoL = { left: [cadena(BL.sh, BL.el, hombro.left, codo.left), cadena(BL.el, BL.wr, codo.left, CL.wr), cadena(BL.wr, BL.tip, CL.wr, CL.tip)], right: [cadena(BR.sh, BR.el, hombro.right, codo.right), cadena(BR.el, BR.wr, codo.right, CR.wr), cadena(BR.wr, BR.tip, CR.wr, CR.tip)] };
  const piernaL = { left: [cadena(BL.hip, BL.knee, CL.hip, CL.kn), cadena(BL.knee, BL.ankle, CL.kn, CL.an), cadena(BL.ankle, BL.toe.clone().setX(BL.ankle.x), CL.an, V(CL.an.x, CL.toe.y, CL.toe.z))],
                    right: [cadena(BR.hip, BR.knee, CR.hip, CR.kn), cadena(BR.knee, BR.ankle, CR.kn, CR.an), cadena(BR.ankle, BR.toe.clone().setX(BR.ankle.x), CR.an, V(CR.an.x, CR.toe.y, CR.toe.z))] };

  for (const p of piezas) {
    const lado = p.nombre.includes("left") || p.lado === "izq" ? "left" : p.nombre.includes("right") ? "right" : null;
    const dedoMano = /(thumb|index finger|middle finger|ring finger|little finger)|metacarpal|^(left|right) (scaphoid|lunate|triquetral|pisiform|trapezium|trapezoid|capitate|hamate)$/.test(p.nombre);
    const fn: (v: V3) => V3 = (() => {
      const n = p.nombre;
      if (p.grupo === "frontal" || p.grupo === "corteza" || p.grupo === "cerebelo" || p.grupo === "tronco_encefalico" || p.grupo === "pineal" || p.grupo === "hipotalamo" || ["neurocranium", "mandible", "left maxilla", "right maxilla", "hyoid bone"].includes(n) || n === "hyoid bone")
        return n === "hyoid bone" ? (v: V3) => torso(v) : cabeza;
      if (lado && /\b(femur|patella)$/.test(n)) return (v) => piernaL[lado][0](v);
      if (lado && /\b(tibia|fibula)$/.test(n)) return (v) => piernaL[lado][1](v);
      if (/toe|talus|calcaneus|cuboid|cuneiform|navicular|metatarsal/.test(n)) { const l = lado ?? (p.nombre.includes("left") ? "left" : "right"); return (v) => piernaL[l][2](v); }
      if (lado && /\bhumerus$/.test(n)) return (v) => brazoL[lado][0](v);
      if (lado && /\b(radius|ulna)$/.test(n)) return (v) => brazoL[lado][1](v);
      if (dedoMano) { const l = lado ?? (n.includes("left") ? "left" : "right"); return (v) => brazoL[l][2](v); }
      if (lado && /\b(scapula|clavicle)$/.test(n)) return (v) => torso(v);
      return torso;
    })();
    const a = posiciones(p.mesh), v = V();
    for (let i = 0; i < a.length; i += 3) { v.set(a[i], a[i + 1], a[i + 2]); const r = fn(v); a[i] = r.x; a[i + 1] = r.y; a[i + 2] = r.z; }
    p.mesh.geometry.setAttribute("position", new THREE.BufferAttribute(a, 3));
    p.mesh.geometry.computeVertexNormals(); p.mesh.geometry.computeBoundingSphere(); p.mesh.geometry.computeBoundingBox();   // sin esto el recorte de cámara usa la esfera vieja y las piezas desaparecen
  }
  const grupo = new Map<string, Pieza[]>();
  for (const p of piezas) { const k = p.grupo; grupo.set(k, [...(grupo.get(k) ?? []), p]); }
  const ph = por("pineal body"), hy = piezas.find((p) => p.grupo === "hipotalamo");
  const cen = (p?: Pieza) => (p ? centro(posiciones(p.mesh), () => true) : V());
  return { grupo, todas: piezas, sueno: cen(ph), hipotalamo: cen(hy), braquial: [hombro.left, codo.left] };
}

const COLOR: Record<string, string> = { hueso: "#e6dcc3", cartilago: "#c9d6d2", corazon: "#c8323c", aorta: "#8e2a30", vena_cava: "#3b5c8a", pulmon_izq: "#e9a3a8", pulmon_der: "#e9a3a8", traquea: "#cbd5d6", esofago: "#d6a29a",
  diafragma: "#b87366", higado: "#8a3d2a", vesicula: "#7d8a3a", estomago: "#d9806a", pancreas: "#d8b24a", rinon_izq: "#a84a46", rinon_der: "#a84a46", vejiga: "#c98a7a", intestino_delgado: "#d99b86",
  intestino_grueso: "#c4826f", frontal: "#d98a8f", corteza: "#cf9a9d", cerebelo: "#b9696f", tronco_encefalico: "#c98a86", pineal: "#c9777f", hipotalamo: "#e8c06a" };
const INDICADOR: Record<string, string> = { frontal: "ánimo", pineal: "sueño", corazon: "fc", pancreas: "glucosa" };
const TRANSPARENTE = new Set(["pulmon_izq", "pulmon_der", "corteza", "diafragma"]);

function material(grupo: string) {
  const c = COLOR[grupo] ?? COLOR.hueso;
  return new THREE.MeshStandardMaterial({ color: c, roughness: grupo === "hueso" ? 0.62 : 0.5, emissive: grupo === "hueso" ? "#3a3326" : c, emissiveIntensity: grupo === "hueso" ? 0.28 : 0.16, side: THREE.DoubleSide,
    transparent: TRANSPARENTE.has(grupo), opacity: TRANSPARENTE.has(grupo) ? (grupo === "corteza" ? 0.35 : 0.55) : 1, depthWrite: !TRANSPARENTE.has(grupo) });
}

class Resguardo extends Component<{ fallback: ReactNode; children: ReactNode }, { error: boolean }> {
  state = { error: false };
  static getDerivedStateFromError() { return { error: true }; }
  componentDidCatch(e: unknown) { console.error("AnatomyReal falló; se usa la anatomía esquemática:", e); }
  render() { return this.state.error ? this.props.fallback : this.props.children; }
}

function Real({ m, picked, onPick, states, arrastrado }: { m: Medidas; picked: string | null; onPick: (id: string) => void; states: Record<string, OrganState>; arrastrado: () => boolean }) {
  const { scene } = useGLTF("/models/anatomy_bp3d.glb");
  const aj = useMemo(() => construir(scene, m), [scene, m]);
  const mats = useMemo(() => { const o = new Map<string, THREE.MeshStandardMaterial>(); for (const k of Object.keys(COLOR)) o.set(k, material(k)); return o; }, []);
  useEffect(() => {
    for (const p of aj.todas) p.mesh.material = mats.get(p.grupo === "hueso" || p.grupo === "cartilago" ? p.grupo : p.grupo) ?? mats.get("hueso")!;
  }, [aj, mats]);
  useEffect(() => {                                                    // el color del órgano ES el estado de su recibo (verde con recibo · naranja alarma · gris sin sensor verificado)
    for (const [g, id] of Object.entries(INDICADOR)) {
      const mt = mats.get(g)!, st = states[id], base = COLOR[g];
      mt.color.set(st === "blocked" ? "#6b6258" : base); mt.emissive.set(st === "alarm" ? "#ff5a1f" : st === "ok" ? "#6fae7a" : st === "blocked" ? "#000000" : base);
      mt.emissiveIntensity = st === "alarm" ? 0.7 : st === "ok" ? 0.32 : st === "blocked" ? 0 : 0.18; mt.transparent = st === "blocked"; mt.opacity = st === "blocked" ? 0.55 : 1; mt.needsUpdate = true;
    }
  }, [states, mats, picked]);
  useFrame(({ clock }) => {                                            // el elegido late y brilla
    for (const [g, id] of Object.entries(INDICADOR)) { const mt = mats.get(g)!; if (picked === id) { mt.color.set("#ff7a3a"); mt.emissive.set("#ff5a1f"); mt.emissiveIntensity = 0.7 + 0.3 * Math.sin(clock.elapsedTime * 5); } }
  });
  const S = m.S;
  return (
    <group name="anatomy-real">
      {aj.todas.map((p) => {
        const id = INDICADOR[p.grupo];
        return <primitive key={p.mesh.uuid} object={p.mesh}
          onClick={id ? (e: { stopPropagation: () => void }) => { e.stopPropagation(); if (!arrastrado()) onPick(id); } : undefined}
          onPointerOver={id ? () => { document.body.style.cursor = "pointer"; } : undefined} onPointerOut={id ? () => { document.body.style.cursor = ""; } : undefined} />;
      })}
      {/* dianas de toque: la glándula pineal y el hipotálamo miden milímetros */}
      {([["sueño", aj.sueno, 0.011], ["temperatura", aj.hipotalamo, 0.009]] as [string, V3, number][]).map(([id, pos, r]) => (
        <mesh key={id} position={pos} onClick={(e) => { e.stopPropagation(); if (!arrastrado()) onPick(id); }} onPointerOver={() => { document.body.style.cursor = "pointer"; }} onPointerOut={() => { document.body.style.cursor = ""; }}>
          <sphereGeometry args={[r * S, 14, 10]} /><meshStandardMaterial color={picked === id ? "#ff7a3a" : "#e8c06a"} emissive={picked === id ? "#ff5a1f" : "#e8c06a"} emissiveIntensity={picked === id ? 0.9 : 0.35} transparent opacity={0.85} />
        </mesh>
      ))}
      {/* arteria braquial: sigue el húmero izquierdo del paciente (+x), donde está la marca de la presión */}
      {Array.from({ length: 8 }, (_, i) => { const pos = aj.braquial[0].clone().lerp(aj.braquial[1], 0.08 + i * 0.12).add(V(-0.004 * S, 0, 0.011 * S)); const on = picked === "presión", st = states["presión"];
        return (
          <mesh key={i} position={pos} onClick={(e) => { e.stopPropagation(); if (!arrastrado()) onPick("presión"); }} onPointerOver={() => { document.body.style.cursor = "pointer"; }} onPointerOut={() => { document.body.style.cursor = ""; }}>
            <sphereGeometry args={[0.0034 * S, 10, 8]} /><meshStandardMaterial color={st === "blocked" ? "#6b6258" : "#b3262e"} emissive={on ? "#ff5a1f" : st === "ok" ? "#6fae7a" : "#b3262e"} emissiveIntensity={on ? 0.9 : st === "ok" ? 0.32 : 0.18} />
          </mesh>
        ); })}
    </group>
  );
}

export function AnatomyReal(props: { m: Medidas; picked: string | null; onPick: (id: string) => void; states: Record<string, OrganState>; arrastrado: () => boolean }) {
  return <Resguardo fallback={<Anatomy {...props} />}><Real {...props} /></Resguardo>;
}
