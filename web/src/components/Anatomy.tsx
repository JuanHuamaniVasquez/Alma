"use client";
import { useFrame } from "@react-three/fiber";
import { useMemo, useRef } from "react";
import * as THREE from "three";
import { perfil, type Lado, type Medidas } from "@/lib/anatomia";

/** Capa de anatomía: esqueleto y órganos PROCEDURALES ajustados a las medidas del cuerpo (ilustrativo, no un escaneo ni un diagnóstico).
 *  Esqueleto completo: cráneo con órbitas, mandíbula y dientes · 24 vértebras con apófisis · sacro y cóccix · 12 pares de costillas con cartílago y esternón ·
 *  clavículas y omóplatos · húmero, cúbito, radio y mano (carpo, metacarpianos, falanges) · pelvis (ilion, isquion, pubis) · fémur, rótula, tibia, peroné y pie.
 *  Cada indicador cae sobre su órgano: sueño/ánimo → cerebro, temperatura → hipotálamo, fc → corazón, presión → arteria del brazo izquierdo, glucosa → páncreas. */
export type OrganState = "ok" | "alarm" | "channel" | "blocked";
type V3 = THREE.Vector3;
const V = (x: number, y: number, z: number) => new THREE.Vector3(x, y, z);
const HUESO = "#e6dcc3", CARTILAGO = "#c9d6d2";

const tubo = (pts: V3[], r: number, seg = 24, radial = 8, closed = false) => new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts, closed, "catmullrom", 0.5), seg, r, radial, closed);

export function Anatomy({ m, picked, onPick, states, arrastrado }: { m: Medidas; picked: string | null; onPick: (id: string) => void; states: Record<string, OrganState>; arrastrado: () => boolean }) {
  const S = m.S, u = (f: number) => f * S;
  const bone = useMemo(() => new THREE.MeshStandardMaterial({ color: HUESO, roughness: 0.62, emissive: "#3a3326", emissiveIntensity: 0.28 }), []);
  const cart = useMemo(() => new THREE.MeshStandardMaterial({ color: CARTILAGO, roughness: 0.6, emissive: "#2a3633", emissiveIntensity: 0.2 }), []);
  const hueco = useMemo(() => new THREE.MeshStandardMaterial({ color: "#15110d", roughness: 1 }), []);
  const neutro = (c: string, o = 1) => new THREE.MeshStandardMaterial({ color: c, roughness: 0.5, emissive: c, emissiveIntensity: 0.16, transparent: o < 1, opacity: o });

  /** Cápsula entre dos puntos. */
  const Seg = ({ a, b, r, mat = bone, k = 1 }: { a: V3; b: V3; r: number; mat?: THREE.Material; k?: number }) => {
    const d = b.clone().sub(a), len = d.length(), q = new THREE.Quaternion().setFromUnitVectors(V(0, 1, 0), d.clone().normalize());
    return <mesh position={a.clone().add(b).multiplyScalar(0.5)} quaternion={q} scale={[k, 1, k]} material={mat}><capsuleGeometry args={[r, Math.max(0.0005, len - 2 * r), 5, 10]} /></mesh>;
  };
  const Ball = ({ p, r, sc = [1, 1, 1], mat = bone }: { p: V3; r: number; sc?: [number, number, number]; mat?: THREE.Material }) => <mesh position={p} scale={sc} material={mat}><sphereGeometry args={[r, 16, 12]} /></mesh>;
  const Tube = ({ pts, r, mat = bone, closed = false }: { pts: V3[]; r: number; mat?: THREE.Material; closed?: boolean }) => <mesh geometry={useMemo(() => tubo(pts, r, 28, 8, closed), [pts, r, closed])} material={mat} />;

  // ---------- columna: trayectoria L5 → C1 siguiendo la curvatura del cuerpo medido
  const spine = useMemo(() => {
    const yb = m.pelvis.y + u(0.035), yt = m.head.y - u(0.056);
    const zEn = (y: number) => {
      if (y <= m.neck.y) { const p = perfil(m, y); return p.zb + 0.3 * (p.zf - p.zb) + (y > m.pelvis.y + u(0.1) ? 0 : 0.01 * S); }
      const pn = perfil(m, m.neck.y), z0 = pn.zb + 0.3 * (pn.zf - pn.zb), k = Math.min(1, (y - m.neck.y) / Math.max(1e-3, yt - m.neck.y));
      return z0 + (m.head.z - u(0.015) - z0) * (k * k * (3 - 2 * k));
    };
    return Array.from({ length: 24 }, (_, i) => { const t = i / 23, y = yb + t * (yt - yb); return V(0, y, zEn(y)); });
  }, [m]);                                                                       // eslint-disable-line react-hooks/exhaustive-deps
  const zEje = (y: number) => { let b = spine[0]; for (const p of spine) if (Math.abs(p.y - y) < Math.abs(b.y - y)) b = p; return b.z; };

  const Organ = ({ id, color, pos, scale = [1, 1, 1], rot = [0, 0, 0], r }: { id?: string; color: string; pos: V3; scale?: [number, number, number]; rot?: [number, number, number]; r: number }) => {
    const on = !!id && picked === id, ref = useRef<THREE.Mesh>(null), st = id ? states[id] : undefined;
    useFrame(({ clock }) => { if (ref.current) ref.current.scale.set(scale[0] * (on ? 1 + 0.07 * Math.sin(clock.elapsedTime * 5) : 1), scale[1] * (on ? 1 + 0.07 * Math.sin(clock.elapsedTime * 5) : 1), scale[2] * (on ? 1 + 0.07 * Math.sin(clock.elapsedTime * 5) : 1)); });
    const mat = on ? <meshStandardMaterial color="#ff7a3a" roughness={0.45} emissive="#ff5a1f" emissiveIntensity={0.9} />       // el color del órgano ES el estado de su recibo
      : st === "blocked" ? <meshStandardMaterial color="#6b6258" roughness={0.8} transparent opacity={0.55} />
      : st === "alarm" ? <meshStandardMaterial color={color} roughness={0.45} emissive="#ff5a1f" emissiveIntensity={0.7} />
      : st === "ok" ? <meshStandardMaterial color={color} roughness={0.45} emissive="#6fae7a" emissiveIntensity={0.32} />
      : <meshStandardMaterial color={color} roughness={0.45} emissive={color} emissiveIntensity={0.18} />;
    return (
      <mesh ref={ref} position={pos} rotation={rot} scale={scale}
        onClick={id ? (e) => { e.stopPropagation(); if (!arrastrado()) onPick(id); } : undefined}
        onPointerOver={id ? () => { document.body.style.cursor = "pointer"; } : undefined} onPointerOut={id ? () => { document.body.style.cursor = ""; } : undefined}>
        <sphereGeometry args={[r, 22, 16]} />{mat}
      </mesh>
    );
  };

  // ---------- caja torácica: 12 pares de costillas sobre el perfil medido; las 7 primeras llegan al esternón por cartílago
  const costillas = useMemo(() => {
    const yT1 = m.neck.y - u(0.02), yT12 = spine[Math.round(23 * 0.38)].y, out: { rib: V3[]; cart: V3[] | null; yFin: number; zFin: number }[] = [];
    for (let i = 0; i < 12; i++) {
      const y0 = yT1 - (yT1 - yT12) * (i / 11), p = perfil(m, y0 - u(0.02));
      const k = 0.62 + 0.38 * Math.sin(Math.min(1, (i + 1.5) / 7.5) * Math.PI * 0.5);                 // la caja se ensancha hacia las costillas medias
      const a = Math.max(u(0.045), p.hw * (0.62 + 0.2 * Math.sin(Math.min(1, i / 7) * Math.PI * 0.5))) * (i < 2 ? 0.55 + 0.2 * i : 1), zc = (p.zb + p.zf) / 2 + u(0.004), b = ((p.zf - p.zb) / 2) * 0.82 * (0.6 + 0.4 * k);
      const zs = zEje(y0), fin = i < 7 ? Math.PI * 0.94 : i < 10 ? Math.PI * 0.86 : Math.PI * (0.5 + 0.04 * (11 - i));
      const rib: V3[] = [], n = 14, drop = u(0.026 + 0.004 * (i < 8 ? i : 8 - (i - 8) * 0.8));
      for (let j = 0; j <= n; j++) {
        const th = 0.12 + (fin - 0.12) * (j / n), x = a * Math.sin(th), z = j === 0 ? zs : zc - b * Math.cos(th);
        rib.push(V(x, y0 - drop * (th / Math.PI) ** 1.4 + u(0.004) * Math.sin(th), j < 2 ? zs + (z - zs) * j / 1.2 : z));
      }
      rib[0].set(u(0.012), y0, zs);
      const e = rib[rib.length - 1];
      out.push({ rib, cart: null, yFin: e.y, zFin: e.z });
    }
    const zStern = (i: number) => out[i].zFin + u(0.006), yStern = (i: number) => out[Math.min(i, 6)].yFin - u(0.014);
    for (let i = 0; i < 10; i++) {
      const e = out[i].rib[out[i].rib.length - 1], tgt = i < 7 ? V(u(0.011), yStern(i) + (i === 6 ? 0 : 0), zStern(i)) : V(out[6].rib[out[6].rib.length - 1].x * (0.35 + 0.18 * (10 - i) / 3), out[6].yFin - u(0.012 * (i - 6)), out[6].zFin);
      out[i].cart = [e.clone(), e.clone().lerp(tgt, 0.55).add(V(0, u(0.01), u(0.003))), tgt];
    }
    return out;
  }, [m, spine]);                                                                // eslint-disable-line react-hooks/exhaustive-deps

  const yEs0 = costillas[0].yFin + u(0.016), yEs1 = costillas[6].yFin - u(0.012), zEs = (y: number) => perfil(m, y).zf - u(0.017);
  const ladoOf = (s: number): Lado => (s < 0 ? m.L : m.R);

  /** Mano: carpo, 5 metacarpianos y falanges en abanico (la palma mira al muslo: los dedos se alinean de delante hacia atrás). */
  const Mano = ({ s }: { s: number }) => {
    const l = ladoOf(s), dir = l.tip.clone().sub(l.wr).normalize(), spread = V(0, 0, 1).sub(dir.clone().multiplyScalar(dir.z)).normalize(), len = l.tip.distanceTo(l.wr);
    const at = (f: number, off: number) => l.wr.clone().addScaledVector(dir, len * f).addScaledVector(spread, off);
    const dedos = [{ off: 0.0155, mc: 0.36, ph: [0.3, 0.2, 0.14], rr: 0.0042 }, { off: 0.0075, mc: 0.43, ph: [0.34, 0.2, 0.13], rr: 0.0042 }, { off: -0.0015, mc: 0.46, ph: [0.36, 0.22, 0.13], rr: 0.0043 }, { off: -0.0095, mc: 0.43, ph: [0.34, 0.2, 0.13], rr: 0.0041 }, { off: -0.017, mc: 0.38, ph: [0.26, 0.16, 0.12], rr: 0.0038 }];
    return (
      <group>
        {[-0.012, -0.004, 0.004, 0.012].map((o, i) => <Ball key={i} p={at(0.06, u(o))} r={u(0.0058)} sc={[1, 0.8, 1]} />)}
        {[0.018, 0.006, -0.008].map((o, i) => <Ball key={"c" + i} p={at(0.13, u(o))} r={u(0.0056)} sc={[1, 0.8, 1]} />)}
        {dedos.map((d, i) => {
          const base = at(0.12 + (i === 0 ? 0.04 : 0), u(d.off * 0.9)), k0 = at(0.12 + d.mc, u(d.off * (i === 0 ? 1.6 : 1.1)));
          const pts = [base, k0];
          let cur = k0.clone();
          const lenF = len * (1 - 0.12 - d.mc);
          d.ph.slice(i === 0 ? 1 : 0).forEach((f) => { const nx = cur.clone().addScaledVector(dir, lenF * f * (i === 0 ? 1.5 : 1.05)).addScaledVector(spread, u(d.off * 0.25)); pts.push(nx); cur = nx; });
          return <group key={i}>{pts.slice(0, -1).map((a, j) => <Seg key={j} a={a} b={pts[j + 1]} r={u(d.rr) * (j === 0 ? 1.25 : 1 - j * 0.12)} />)}{pts.slice(1, -1).map((p, j) => <Ball key={"n" + j} p={p} r={u(d.rr) * 1.25} />)}</group>;
        })}
      </group>
    );
  };

  /** Pie: astrágalo, calcáneo, 5 metatarsianos y dedos. */
  const Pie = ({ s }: { s: number }) => {
    const l = ladoOf(s), heel = l.heel, toe = l.toe, ax = toe.clone().sub(heel).setY(0).normalize(), lat = V(-ax.z, 0, ax.x).multiplyScalar(s < 0 ? -1 : 1), len = toe.distanceTo(heel);
    const at = (f: number, off: number, h = 0.012) => heel.clone().addScaledVector(ax, len * f).addScaledVector(lat, u(off) * s * -1).setY(u(h));
    return (
      <group>
        <Ball p={l.an.clone().add(V(0, -u(0.014), u(0.004)))} r={u(0.015)} sc={[1, 0.8, 1.15]} />
        <Ball p={at(0.13, 0, 0.019)} r={u(0.0185)} sc={[0.9, 0.75, 1.5]} />
        {[0.0, 0.01, 0.02].map((o, i) => <Ball key={i} p={at(0.42 + i * 0.02, o - 0.004, 0.017)} r={u(0.009)} sc={[1, 0.8, 1]} />)}
        {[-0.016, -0.0075, 0.0, 0.0075, 0.015].map((o, i) => {
          const a = at(0.46, o * 0.8, 0.014), b = at(0.74, o * 1.4, 0.009), c = at(0.86 + (i === 2 ? 0.02 : 0), o * 1.6, 0.007), d = at(0.97 - Math.abs(i - 1.5) * 0.015, o * 1.7, 0.006);
          return <group key={i}><Seg a={a} b={b} r={u(0.0046)} /><Seg a={b} b={c} r={u(0.0041)} />{i !== 4 && <Seg a={c} b={d} r={u(0.0035)} />}</group>;
        })}
      </group>
    );
  };

  // ---------- geometrías extruidas: omóplato e ilion
  const gOmoplato = useMemo(() => {
    const sh = new THREE.Shape(); const P: [number, number][] = [[-0.002, 0.052], [0.026, 0.056], [0.055, 0.047], [0.062, 0.034], [0.036, 0.018], [0.036, -0.012], [0.022, -0.052], [0.004, -0.07], [-0.014, -0.055], [-0.03, -0.012], [-0.034, 0.03]];
    const k = 0.62; P.forEach(([x, y], i) => (i ? sh.lineTo(x * S * k, y * S * k) : sh.moveTo(x * S * k, y * S * k))); sh.closePath();
    return new THREE.ExtrudeGeometry(sh, { depth: u(0.004), bevelEnabled: true, bevelSize: u(0.0018), bevelThickness: u(0.0018), bevelSegments: 2, curveSegments: 6 });
  }, [S]);                                                                        // eslint-disable-line react-hooks/exhaustive-deps
  const gIlion = useMemo(() => {
    const sh = new THREE.Shape(); const P: [number, number][] = [[0.006, 0.01], [0.012, 0.055], [0.04, 0.083], [0.082, 0.078], [0.1, 0.056], [0.092, 0.03], [0.07, 0.01], [0.062, -0.012], [0.04, -0.012], [0.02, -0.004]];
    const k = 0.82; P.forEach(([x, y], i) => (i ? sh.lineTo(x * S * k, y * S * k) : sh.moveTo(x * S * k, y * S * k))); sh.closePath();
    return new THREE.ExtrudeGeometry(sh, { depth: u(0.011), bevelEnabled: true, bevelSize: u(0.003), bevelThickness: u(0.003), bevelSegments: 2, curveSegments: 6 });
  }, [S]);                                                                        // eslint-disable-line react-hooks/exhaustive-deps

  const brazo = (s: number) => {
    const l = ladoOf(s), dirH = l.wr.clone().sub(l.el).normalize(), ap = V(0, 0, 1), perp = ap.clone().sub(dirH.clone().multiplyScalar(dirH.dot(ap))).normalize();
    return (
      <group key={"br" + s}>
        <Ball p={l.sh} r={u(0.0145)} /><Seg a={l.sh.clone().lerp(l.el, 0.04)} b={l.el.clone().lerp(l.sh, 0.03)} r={u(0.0082)} k={1} />
        <Ball p={l.el.clone().add(perp.clone().multiplyScalar(u(0.004)))} r={u(0.0125)} sc={[1, 0.9, 1]} />
        <Seg a={l.el.clone().addScaledVector(perp, -u(0.003))} b={l.wr.clone().addScaledVector(perp, -u(0.006))} r={u(0.0062)} />
        <Seg a={l.el.clone().addScaledVector(perp, u(0.006))} b={l.wr.clone().addScaledVector(perp, u(0.006))} r={u(0.0056)} />
        <Ball p={l.el.clone().add(V(0, 0, -u(0.01)))} r={u(0.007)} />
        <Mano s={s} />
      </group>
    );
  };

  const pierna = (s: number) => {
    const l = ladoOf(s), lat = V(s, 0, 0), mal = l.an.clone();
    const troc = l.hip.clone().addScaledVector(lat, u(0.031)).add(V(0, -u(0.028), -u(0.003)));
    return (
      <group key={"pi" + s}>
        <Ball p={l.hip} r={u(0.0145)} />
        <Tube pts={[l.hip, l.hip.clone().lerp(troc, 0.55).add(V(0, u(0.004), 0)), troc, troc.clone().lerp(l.kn, 0.35).addScaledVector(lat, -u(0.004)), l.kn.clone().lerp(troc, 0.2).add(V(0, u(0.004), u(0.001)))]} r={u(0.0125)} />
        <Ball p={troc.clone().add(V(0, u(0.006), 0))} r={u(0.0115)} sc={[0.9, 1.3, 1]} />
        <Ball p={l.kn.clone().add(V(s * u(0.013), -u(0.002), 0))} r={u(0.0145)} /><Ball p={l.kn.clone().add(V(-s * u(0.013), -u(0.002), 0))} r={u(0.0148)} />
        <Ball p={l.kn.clone().add(V(0, 0, u(0.02)))} r={u(0.0115)} sc={[1, 1.1, 0.5]} />
        <mesh position={l.kn.clone().add(V(0, -u(0.014), 0))} material={bone}><cylinderGeometry args={[u(0.021), u(0.018), u(0.005), 18]} /></mesh>
        <Seg a={l.kn.clone().add(V(0, -u(0.016), 0))} b={mal.clone().add(V(-s * u(0.004), u(0.014), 0))} r={u(0.0102)} />
        <Seg a={l.kn.clone().add(V(s * u(0.024), -u(0.022), -u(0.006)))} b={mal.clone().add(V(s * u(0.019), u(0.005), -u(0.004)))} r={u(0.0058)} />
        <Ball p={mal.clone().add(V(-s * u(0.011), -u(0.007), 0))} r={u(0.0095)} /><Ball p={mal.clone().add(V(s * u(0.02), -u(0.011), -u(0.003)))} r={u(0.009)} />
        <Pie s={s} />
      </group>
    );
  };

  // ---------- posiciones de órganos (según el perfil medido)
  const yC = (costillas[1].rib[7].y + costillas[7].rib[7].y) / 2, pC = perfil(m, yC), zC = (pC.zb + pC.zf) / 2;
  const cabeza = m.head, sw = m.headW * 0.86;
  const dientes = Array.from({ length: 12 }, (_, i) => { const t = (i - 5.5) / 5.5, a = t * 0.85; return V(Math.sin(a) * u(0.022), -u(0.0745), u(0.04) * Math.cos(a) + u(0.002)); });

  return (
    <group name="anatomy">
      {/* ---- cráneo, cara y mandíbula */}
      <group position={cabeza}>
        <mesh position={[0, u(0.012), -u(0.004)]} scale={[sw / 2, u(0.056), u(0.064)]}><sphereGeometry args={[1, 28, 20]} /><meshStandardMaterial color={HUESO} roughness={0.55} transparent opacity={0.42} depthWrite={false} /></mesh>
        <Ball p={V(0, -u(0.036), u(0.034))} r={u(0.03)} sc={[1.05, 0.85, 0.85]} />
        {[-1, 1].map((s) => (
          <group key={s}>
            <Ball p={V(s * u(0.0205), -u(0.0105), u(0.0545))} r={u(0.0082)} sc={[1.1, 0.9, 0.45]} mat={hueco} /><mesh position={[s * u(0.0205), -u(0.0105), u(0.0575)]} scale={[1.1, 0.92, 1]} material={bone}><torusGeometry args={[u(0.0092), u(0.0013), 6, 20]} /></mesh>
            <Tube pts={[V(s * u(0.036), -u(0.024), u(0.03)), V(s * u(0.044), -u(0.016), u(0.012)), V(s * u(0.0455), -u(0.014), -u(0.006))]} r={u(0.0042)} />
            <Ball p={V(s * u(0.04), -u(0.026), u(0.032))} r={u(0.0085)} sc={[1, 0.8, 0.7]} />
            <Tube pts={[V(s * u(0.0435), -u(0.016), -u(0.004)), V(s * u(0.042), -u(0.048), u(0.004)), V(s * u(0.034), -u(0.07), u(0.02)), V(s * u(0.018), -u(0.078), u(0.036)), V(0, -u(0.0805), u(0.043))]} r={u(0.0058)} />
          </group>
        ))}
        <Ball p={V(0, -u(0.032), u(0.057))} r={u(0.0085)} sc={[0.6, 1.2, 0.6]} mat={hueco} />
        {dientes.map((p, i) => <mesh key={i} position={[p.x, p.y + u(0.0105), p.z]} material={neutro("#f3eee0")}><boxGeometry args={[u(0.003), u(0.0052), u(0.0024)]} /></mesh>)}
        {/* cerebro: dos hemisferios + cerebelo + tronco; los dos con indicador son «ánimo» (anterior) y «sueño» (posterior) */}
        <Organ id="ánimo" color="#d98a8f" pos={V(0, u(0.014), u(0.018))} scale={[1, 0.88, 1.05]} r={u(0.03)} />
        <Organ id="sueño" color="#c9777f" pos={V(0, u(0.012), -u(0.016))} scale={[1, 0.88, 1]} r={u(0.03)} />
        <Ball p={V(0, -u(0.014), -u(0.034))} r={u(0.02)} sc={[1.3, 0.75, 0.9]} mat={neutro("#b9696f")} /><Seg a={V(0, -u(0.01), -u(0.008))} b={V(0, -u(0.05), -u(0.016))} r={u(0.007)} mat={neutro("#c98a86")} />
        <Organ id="temperatura" color="#e8c06a" pos={V(0, -u(0.004), u(0.0)) } r={u(0.0078)} />
      </group>

      {/* ---- columna: 7 cervicales, 12 torácicas, 5 lumbares (cuerpo + apófisis espinosa y transversas), sacro y cóccix */}
      {spine.map((p, i) => {
        const tan = (spine[Math.min(23, i + 1)].clone().sub(spine[Math.max(0, i - 1)])).normalize(), q = new THREE.Quaternion().setFromUnitVectors(V(0, 1, 0), tan);
        const reg = i < 5 ? 0 : i < 17 ? 1 : 2, r = u(reg === 0 ? 0.0185 : reg === 1 ? 0.0152 - 0.0005 * (i - 5) * 0.5 : 0.0112), h = u(reg === 2 ? 0.0078 : 0.0092), esp = u(reg === 0 ? 0.027 : reg === 1 ? 0.03 : 0.017), tr = u(reg === 0 ? 0.026 : reg === 1 ? 0.027 : 0.016);
        return (
          <group key={i} position={p} quaternion={q}>
            <mesh material={bone} scale={[1.18, 1, 0.9]}><cylinderGeometry args={[r, r * 1.04, h, 14]} /></mesh>
            <Seg a={V(0, u(0.002), -r * 0.8)} b={V(0, -u(reg === 1 ? 0.013 : 0.004), -r * 0.8 - esp)} r={u(0.0034)} />
            <Seg a={V(-r * 0.7, 0, -r * 0.4)} b={V(-r * 0.7 - tr, u(0.002), -r * 0.7)} r={u(0.0028)} /><Seg a={V(r * 0.7, 0, -r * 0.4)} b={V(r * 0.7 + tr, u(0.002), -r * 0.7)} r={u(0.0028)} />
            {i < 23 && <mesh position={[0, h * 0.62, 0]} material={cart}><cylinderGeometry args={[r * 0.9, r * 0.9, h * 0.22, 12]} /></mesh>}
          </group>
        );
      })}
      <group position={[0, 0, 0]}>
        <Tube pts={[spine[0].clone().add(V(0, -u(0.014), -u(0.002))), spine[0].clone().add(V(0, -u(0.045), -u(0.012))), spine[0].clone().add(V(0, -u(0.078), -u(0.003)))]} r={u(0.017)} />
        <Seg a={spine[0].clone().add(V(0, -u(0.078), -u(0.003))).add(V(0, 0, 0))} b={spine[0].clone().add(V(0, -u(0.1), u(0.006)))} r={u(0.0055)} />
      </group>

      {/* ---- costillas + cartílago costal + esternón */}
      {costillas.map((c, i) => (
        <group key={i}>
          {[-1, 1].map((s) => (
            <group key={s} scale={[s, 1, 1]}>
              <Tube pts={c.rib} r={u(0.0036)} />
              {c.cart && <Tube pts={c.cart} r={u(0.0034)} mat={cart} />}
              <Ball p={c.rib[0]} r={u(0.0048)} />
            </group>
          ))}
        </group>
      ))}
      <mesh position={[0, (yEs0 + yEs1) / 2, zEs((yEs0 + yEs1) / 2)]} material={bone} rotation={[-0.1, 0, 0]}><boxGeometry args={[u(0.021), yEs0 - yEs1, u(0.0085)]} /></mesh>
      <mesh position={[0, yEs0 + u(0.002), zEs(yEs0)]} material={bone}><boxGeometry args={[u(0.04), u(0.026), u(0.0095)]} /></mesh>
      <mesh position={[0, yEs1 - u(0.011), zEs(yEs1) + u(0.002)]} material={cart}><coneGeometry args={[u(0.007), u(0.025), 6]} /></mesh>

      {/* ---- cintura escapular y brazos */}
      {[-1, 1].map((s) => {
        const l = ladoOf(s), pEs = V(s * u(0.011), yEs0 + u(0.004), zEs(yEs0) - u(0.002)), acr = l.sh.clone().add(V(-s * u(0.004), u(0.025), -u(0.01))), pb = perfil(m, l.sh.y - u(0.04));
        return (
          <group key={"sc" + s}>
            <Tube pts={[pEs, pEs.clone().lerp(acr, 0.3).add(V(0, u(0.006), u(0.014))), pEs.clone().lerp(acr, 0.7).add(V(0, u(0.011), u(0.002))), acr]} r={u(0.0058)} />
            <mesh geometry={gOmoplato} material={bone} position={[s * u(0.088), l.sh.y - u(0.05), pb.zb + u(0.022)]} rotation={[0.08, 0, s * 0.06]} scale={[s, 1, 1]} />
          </group>
        );
      })}
      {[-1, 1].map((s) => brazo(s))}

      {/* ---- pelvis: ilion (alas), isquion y pubis, articulación con el sacro */}
      {[-1, 1].map((s) => {
        const l = ladoOf(s), py = m.pelvis.y + u(0.03), pz = m.pelvis.z;
        return (
          <group key={"pv" + s}>
            <mesh geometry={gIlion} material={bone} position={[s * u(0.014), py - u(0.045), pz - u(0.014)]} rotation={[0.12, -s * 0.64, s * 0.1]} scale={[s, 1, 1]} />
            <Tube pts={[l.hip.clone().add(V(0, u(0.01), -u(0.004)), ), l.hip.clone().add(V(-s * u(0.012), -u(0.03), -u(0.026))), V(s * u(0.04), l.hip.y - u(0.062), pz - u(0.028)), V(s * u(0.046), l.hip.y - u(0.07), pz + u(0.002))]} r={u(0.0085)} />
            <Tube pts={[l.hip.clone().add(V(-s * u(0.008), -u(0.004), u(0.008))), V(s * u(0.035), l.hip.y - u(0.024), pz + u(0.05)), V(s * u(0.011), l.hip.y - u(0.046), pz + u(0.067))]} r={u(0.0072)} />
          </group>
        );
      })}
      <Ball p={V(0, m.pelvis.y - u(0.03), m.pelvis.z + u(0.067))} r={u(0.0075)} mat={cart} />
      {[-1, 1].map((s) => pierna(s))}

      {/* ---- órganos (colores neutros salvo los que son indicadores: su color es el estado de su recibo) */}
      <Tube pts={[V(0, m.neck.y + u(0.04), zEje(m.neck.y) + u(0.028)), V(0, m.neck.y - u(0.04), zEje(m.neck.y - u(0.05)) + u(0.026)), V(0, yC + u(0.05), zC - u(0.01))]} r={u(0.0058)} mat={neutro("#cbd5d6")} />
      {[-1, 1].map((s) => (
        <group key={"pul" + s}>
          <Ball p={V(s * pC.hw * 0.5, yC + u(0.01), zC - u(0.004))} r={u(0.034)} sc={[0.92, 2.0, 1.05]} mat={neutro("#e9a3a8", 0.92)} />
          <Ball p={V(s * pC.hw * 0.52, yC - u(0.052), zC + u(0.004))} r={u(0.03)} sc={[1.0, 0.95, 1.0]} mat={neutro("#df9aa0", 0.92)} />
          {s < 0 && <Ball p={V(s * pC.hw * 0.46, yC - u(0.012), zC + u(0.004))} r={u(0.03)} sc={[0.95, 1.1, 1.0]} mat={neutro("#d98f96", 0.92)} />}
        </group>
      ))}
      <Organ id="fc" color="#c8323c" pos={V(pC.hw * 0.18, yC - u(0.018), zC + u(0.018))} rot={[0, 0, -0.5]} scale={[0.9, 1.2, 0.9]} r={u(0.028)} />
      <Ball p={V(-pC.hw * 0.04, yC + u(0.016), zC + u(0.006))} r={u(0.014)} sc={[1, 0.9, 0.9]} mat={neutro("#b3262e")} />
      <Tube pts={[V(pC.hw * 0.06, yC + u(0.02), zC), V(pC.hw * 0.06, yC + u(0.066), zC - u(0.006)), V(pC.hw * 0.2, yC + u(0.062), zC - u(0.022)), V(pC.hw * 0.2, yC - u(0.02), zEje(yC) + u(0.022))]} r={u(0.0072)} mat={neutro("#8e2a30")} />
      <Tube pts={[V(pC.hw * 0.2, yC - u(0.02), zEje(yC) + u(0.022)), V(u(0.006), yC - u(0.12), zEje(yC - u(0.12)) + u(0.026)), V(u(0.006), m.pelvis.y + u(0.05), zEje(m.pelvis.y) + u(0.03))]} r={u(0.0072)} mat={neutro("#8e2a30")} />
      <Tube pts={[V(-u(0.014), yC - u(0.04), zEje(yC) + u(0.03)), V(-u(0.016), yC - u(0.13), zEje(yC - u(0.13)) + u(0.032)), V(-u(0.014), m.pelvis.y + u(0.05), zEje(m.pelvis.y) + u(0.034))]} r={u(0.0072)} mat={neutro("#3b5c8a")} />
      <Ball p={V(-pC.hw * 0.44, yC - u(0.066), zC + u(0.0))} r={u(0.04)} sc={[1.55, 0.78, 1.0]} mat={neutro("#8a3d2a")} />
      <Ball p={V(pC.hw * 0.44, yC - u(0.082), zC + u(0.012))} r={u(0.028)} sc={[1.15, 0.95, 1.0]} mat={neutro("#d9806a")} />
      <Ball p={V(pC.hw * 0.62, yC - u(0.078), zC - u(0.034))} r={u(0.012)} sc={[0.7, 1.4, 0.8]} mat={neutro("#6a4a7a")} />
      {[-1, 1].map((s) => <Ball key={"ri" + s} p={V(s * pC.hw * 0.32, yC - u(0.12), zEje(yC - u(0.12)) + u(0.038))} r={u(0.016)} sc={[0.7, 1.35, 0.7]} mat={neutro("#a84a46")} />)}
      <Organ id="glucosa" color="#d8b24a" pos={V(0, yC - u(0.108), zC - u(0.006))} scale={[1.9, 0.5, 0.65]} r={u(0.023)} />
      <Tube pts={[V(-pC.hw * 0.5, yC - u(0.14), zC + u(0.02)), V(-pC.hw * 0.2, yC - u(0.15), zC + u(0.034)), V(pC.hw * 0.3, yC - u(0.145), zC + u(0.028)), V(pC.hw * 0.5, yC - u(0.17), zC + u(0.02)), V(pC.hw * 0.4, yC - u(0.205), zC + u(0.03)), V(0, yC - u(0.19), zC + u(0.036)), V(-pC.hw * 0.4, yC - u(0.2), zC + u(0.028)), V(-pC.hw * 0.5, yC - u(0.235), zC + u(0.02)), V(0, yC - u(0.24), zC + u(0.03)), V(pC.hw * 0.45, yC - u(0.245), zC + u(0.02))]} r={u(0.0095)} mat={neutro("#d99b86")} />
      <Ball p={V(0, m.pelvis.y + u(0.002), m.pelvis.z + u(0.035))} r={u(0.016)} mat={neutro("#c98a7a")} />
      {/* arteria braquial (presión arterial): sigue el húmero izquierdo del paciente (+x: mira a +z), donde está su marca */}
      {Array.from({ length: 8 }, (_, i) => <Organ key={i} id="presión" color="#b3262e" pos={m.R.sh.clone().lerp(m.R.el, 0.08 + i * 0.12).add(V(-u(0.004), 0, u(0.011)))} r={u(0.0062)} />)}
    </group>
  );
}
