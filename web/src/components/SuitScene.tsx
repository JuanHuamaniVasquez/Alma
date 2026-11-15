"use client";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { ContactShadows, Line, useGLTF, useProgress } from "@react-three/drei";
import { Suspense, useEffect, useMemo, useRef, useState } from "react";
import * as THREE from "three";
import { BUDGETS, INDICATOR_NAMES, type Indicator, type LedgerDay } from "@/lib/api";
import type { CrewLook } from "./CrewFigure";

useGLTF.setDecoderPath("/draco/");
useGLTF.preload("/models/z2.glb");
for (const n of ["VEGA", "LYRA", "ALTAIR", "CASTOR", "RIGEL"]) useGLTF.preload(`/models/crew_${n}.glb`);
const HEIGHT = 1.9, FOCUS_Y = 0.98;
const IVORY = "#efe8da", SIGNAL = "#ff5a1f";

/** Holograma: fresnel (borde brillante), líneas de barrido que suben, parpadeo mínimo y el mapa de color del modelo como modulación de brillo (los detalles del traje se leen).
 *  Tono ÁMBAR/marfil (no el cian típico de las interfaces generadas). Aditivo y sin escribir profundidad: se ve «hecho de luz». */
const HOLO = { color: new THREE.Color("#ffb45c"), rim: new THREE.Color("#fff2dc") };
function holoMaterial(map: THREE.Texture | null): THREE.ShaderMaterial {
  return new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
    uniforms: { uTime: { value: 0 }, uMap: { value: map }, uHasMap: { value: map ? 1 : 0 }, uColor: { value: HOLO.color }, uRim: { value: HOLO.rim } },
    vertexShader: `varying vec3 vN; varying vec3 vV; varying vec3 vW; varying vec2 vUv;
      void main(){ vec4 mv = modelViewMatrix * vec4(position,1.0); vN = normalize(normalMatrix * normal); vV = normalize(-mv.xyz); vW = (modelMatrix * vec4(position,1.0)).xyz; vUv = uv; gl_Position = projectionMatrix * mv; }`,
    fragmentShader: `uniform float uTime; uniform sampler2D uMap; uniform float uHasMap; uniform vec3 uColor; uniform vec3 uRim; varying vec3 vN; varying vec3 vV; varying vec3 vW; varying vec2 vUv;
      void main(){
        float fres = pow(1.0 - abs(dot(normalize(vN), normalize(vV))), 2.2);
        float scan = 0.5 + 0.5 * sin(vW.y * 110.0 - uTime * 2.4);
        float sweep = smoothstep(0.96, 1.0, sin(vW.y * 1.4 - uTime * 0.9) * 0.5 + 0.5);          // una franja brillante que recorre el cuerpo
        float lum = uHasMap > 0.5 ? dot(texture2D(uMap, vUv).rgb, vec3(0.33)) : 0.7;
        float a = 0.10 + lum * 0.22 + fres * 0.78 + scan * 0.10 + sweep * 0.45;
        vec3 c = mix(uColor, uRim, clamp(fres * 1.3 + sweep, 0.0, 1.0));
        a *= 0.94 + 0.06 * sin(uTime * 37.0);
        gl_FragColor = vec4(c * (0.55 + lum * 0.7), clamp(a, 0.0, 1.0)); }`,
  });
}
type State = "closes" | "open" | "absent";
type Labels = React.MutableRefObject<Record<string, HTMLDivElement | null>>;
type Marks = React.MutableRefObject<Record<string, HTMLButtonElement | null>>;

/** Dónde se «toca» cada indicador oficial del reto sobre el traje de exterior (modelo normalizado: pies en y=0, altura 1,9; frente = +z). */
const ANCHORS_EVA: Record<string, [number, number, number]> = {
  "sueño": [0, 1.86, 0.02], "ánimo": [-0.16, 1.7, 0.2], temperatura: [0, 1.52, 0.22], fc: [-0.1, 1.3, 0.3], "presión": [0.42, 1.28, 0.05], glucosa: [0, 0.95, 0.3],
};
const INDICATOR_IDS = Object.keys(ANCHORS_EVA);

/** Cuerpo: balanceo suave, anclas de los marcadores del DOM (se atenúan si miran hacia dentro) y toque para que ALMA hable. Sirve al traje y a la tripulación. */
function Body({ anchors: pos, marks, mode, onTap, children, holo }: { anchors: Record<string, [number, number, number]>; marks: Marks; mode: "books" | "body"; onTap: () => void; children: React.ReactNode; holo: boolean }) {
  const mats = useRef<THREE.ShaderMaterial[]>([]);
  const anchors = useRef<Record<string, THREE.Object3D | null>>({});
  const v = useMemo(() => new THREE.Vector3(), []);
  const { size } = useThree();
  const ref = useRef<THREE.Group>(null);
  useEffect(() => {                                                        // holograma ⇄ sólido: se intercambian los materiales y se guardan los originales
    const g = ref.current; if (!g) return;
    mats.current = [];
    g.traverse((o) => {
      const m = o as THREE.Mesh; if (!m.isMesh) return;
      if (holo) { if (!m.userData.orig) m.userData.orig = m.material; const map = (m.userData.orig as THREE.MeshStandardMaterial).map ?? null; const hm = holoMaterial(map); m.material = hm; mats.current.push(hm); }
      else if (m.userData.orig) { m.material = m.userData.orig; }
    });
  }, [holo, children]);
  useFrame(({ clock, camera }) => {
    for (const m of mats.current) m.uniforms.uTime.value = clock.elapsedTime;
    if (ref.current) ref.current.rotation.y = Math.sin(clock.elapsedTime * 0.2) * 0.5;
    for (const id of INDICATOR_IDS) {
      const a = anchors.current[id], el = marks.current[id];
      if (!a || !el) continue;
      a.getWorldPosition(v);
      const frente = v.x * camera.position.x + v.z * camera.position.z > 0;
      v.project(camera);
      el.style.transform = `translate(${(v.x * 0.5 + 0.5) * size.width}px, ${(-v.y * 0.5 + 0.5) * size.height}px) translate(-50%,-50%)`;
      el.style.opacity = mode === "body" ? (frente ? "1" : "0.25") : "0";
      el.style.pointerEvents = mode === "body" && frente ? "auto" : "none";
    }
  });
  return (
    <group ref={ref} onClick={(e) => { e.stopPropagation(); onTap(); }} onPointerOver={() => { document.body.style.cursor = "pointer"; }} onPointerOut={() => { document.body.style.cursor = ""; }}>
      {children}
      {Object.entries(pos).map(([id, p]) => <object3D key={id} ref={(o) => { anchors.current[id] = o; }} position={p} />)}
    </group>
  );
}

/** Traje NASA Z-2 (NASA 3D Resources, sin copyright): el tripulante FUERA de la nave. Visor oscuro y sin cara. */
function Suit(props: { marks: Marks; mode: "books" | "body"; onTap: () => void; holo: boolean }) {
  const { scene } = useGLTF("/models/z2.glb");
  const model = useMemo(() => {
    const m = scene.clone(true);
    const box = new THREE.Box3().setFromObject(m), size = box.getSize(new THREE.Vector3()), c = box.getCenter(new THREE.Vector3());
    m.traverse((o) => {                                    // el mapa de especular horneado del modelo produce manchas negras en three: se descarta
      const mesh = o as THREE.Mesh;
      if (!mesh.isMesh) return;
      const mat = (mesh.material as THREE.MeshPhysicalMaterial).clone();
      mat.specularIntensityMap = null; mat.specularColorMap = null; mat.normalMap = null; mat.roughness = 0.62; mat.needsUpdate = true;
      mesh.material = mat;
    });
    const k = HEIGHT / size.y;
    m.scale.setScalar(k); m.position.set(-c.x * k, -box.min.y * k, -c.z * k);
    return m;
  }, [scene]);
  return <Body anchors={ANCHORS_EVA} {...props}><primitive object={model} /></Body>;
}

/** Anclas de los indicadores sobre el cuerpo generado (fracciones de la altura H; pies en y=0, frente = +z; A-pose). */
function anchorsFor(H: number): Record<string, [number, number, number]> {
  return { "sueño": [0, 1.02 * H, 0.0], "ánimo": [-0.045 * H, 0.935 * H, 0.06 * H], temperatura: [0, 0.855 * H, 0.04 * H], fc: [-0.055 * H, 0.72 * H, 0.085 * H],
           "presión": [0.165 * H, 0.745 * H, 0.0], glucosa: [0, 0.57 * H, 0.09 * H] };
}
const HAIR = /short0|bob0|ponytail|long0|afro|braid|eyebrow|eyelash/;

/** El tripulante DENTRO de la nave: humano GENERADO por script en Blender (MPFB; piel, ojos, pelo y dientes de assets CC0) con el mono de vuelo hecho a medida.
 *  Capas: «uniform» (con mono) o «body» (solo el cuerpo). Personaje FICTICIO: combinación de parámetros, nunca una persona real. */
function CrewGLB({ name, layer, ...props }: { name: string; layer: "uniform" | "body"; marks: Marks; mode: "books" | "body"; onTap: () => void; holo: boolean }) {
  const { scene } = useGLTF(`/models/crew_${name}.glb`);
  const { model, H } = useMemo(() => {
    const m = scene.clone(true);
    const box = new THREE.Box3().setFromObject(m), c = box.getCenter(new THREE.Vector3()), size = box.getSize(new THREE.Vector3());
    m.position.set(-c.x, -box.min.y, -c.z);
    m.traverse((o) => {
      const mesh = o as THREE.Mesh;
      if (!mesh.isMesh) return;
      const mat = (mesh.material as THREE.MeshStandardMaterial).clone();
      const n = (mat.name || "").toLowerCase();
      const pelo = HAIR.test(n);
      mat.transparent = false; mat.opacity = 1; mat.alphaTest = pelo ? 0.12 : 0; mat.depthWrite = true; mat.side = pelo ? THREE.DoubleSide : THREE.FrontSide;
      mat.roughness = n.includes("uniform") ? 0.86 : n.includes("body") || n.includes("lips") ? 0.55 : 0.6; mat.metalness = 0;
      if (n.includes("uniform")) mat.vertexColors = true;
      mesh.material = mat; mesh.userData.kind = n.includes("uniform") ? "uniform" : "skin";
    });
    return { model: m, H: size.y };
  }, [scene]);
  useEffect(() => { model.traverse((o) => { if (o.userData.kind === "uniform") o.visible = layer === "uniform"; }); }, [layer, model]);
  const anchors = useMemo(() => anchorsFor(H), [H]);
  return <Body anchors={anchors} {...props}><primitive object={model} /></Body>;
}

/** La bahía holográfica: peana con anillos, haz de luz vertical y anillos de barrido en el suelo. Solo luz (aditivo): sin geometría pesada. */
function Bay() {
  const sweep = useRef<THREE.Mesh>(null);
  useFrame(({ clock }) => {
    const t = clock.elapsedTime;
    if (sweep.current) { const k = (t * 0.35) % 1; sweep.current.scale.setScalar(0.6 + k * 1.1); (sweep.current.material as THREE.MeshBasicMaterial).opacity = (1 - k) * 0.35; }
  });
  const ring = (r: number, w: number, o: number) => <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.004, 0]}><ringGeometry args={[r, r + w, 96]} /><meshBasicMaterial color="#ffb45c" transparent opacity={o} blending={THREE.AdditiveBlending} depthWrite={false} /></mesh>;
  return (
    <group>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.002, 0]}><circleGeometry args={[1.0, 64]} /><meshBasicMaterial color="#ffb45c" transparent opacity={0.05} blending={THREE.AdditiveBlending} depthWrite={false} /></mesh>
      {ring(0.98, 0.012, 0.9)}{ring(0.78, 0.006, 0.45)}{ring(0.55, 0.004, 0.3)}
      <mesh ref={sweep} rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.006, 0]}><ringGeometry args={[0.97, 1.0, 96]} /><meshBasicMaterial color="#fff2dc" transparent opacity={0.3} blending={THREE.AdditiveBlending} depthWrite={false} /></mesh>
      <mesh position={[0, 1.15, 0]}><cylinderGeometry args={[0.92, 1.0, 2.3, 64, 1, true]} />
        <shaderMaterial transparent depthWrite={false} side={THREE.DoubleSide} blending={THREE.AdditiveBlending} uniforms={{ uT: { value: 0 } }}
          vertexShader={`varying float vY; void main(){ vY = position.y / 2.3 + 0.5; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`}
          fragmentShader={`varying float vY; void main(){ float a = pow(1.0 - vY, 1.8) * 0.16; gl_FragColor = vec4(1.0, 0.70, 0.36, a); }`} /></mesh>
    </group>
  );
}

/** Cámara centrada en el cuerpo, con un paralaje mínimo del puntero (calma: nada brusco). */
function Rig() {
  useFrame(({ camera, pointer }) => {
    camera.position.x += (pointer.x * 0.45 - camera.position.x) * 0.04;
    camera.position.y += (FOCUS_Y + 0.12 + pointer.y * 0.2 - camera.position.y) * 0.04;
    camera.lookAt(0, FOCUS_Y, 0);
  });
  return null;
}

/** Un anillo = un presupuesto. Marfil fino si cierra; naranja señal que pulsa si NO cierra (regla: |residuo| > 2σ); punteado si no hay libro. */
function Ring({ i, id, state, onPick, active, labels }: { i: number; id: string; state: State; onPick: (id: string) => void; active: boolean; labels: Labels }) {
  const g = useRef<THREE.Group>(null), anchor = useRef<THREE.Object3D>(null), mat = useRef<THREE.Material>(null);
  const v = useMemo(() => new THREE.Vector3(), []);
  const { size } = useThree();
  const y = 0.16 + (i / 8) * 1.66, r = 0.72 + 0.14 * Math.sin(i * 1.7), tilt = 0.45 * Math.sin(i * 2.3), roll = 0.3 * Math.cos(i * 1.3);
  const pts = useMemo(() => Array.from({ length: 129 }, (_, k) => { const a = (k / 128) * Math.PI * 2; return new THREE.Vector3(Math.cos(a) * r, 0, Math.sin(a) * r * 0.82); }), [r]);
  const [hover, setHover] = useState(false);
  useFrame(({ clock, camera }) => {
    const t = clock.elapsedTime;
    if (g.current) g.current.rotation.y = t * (0.07 + i * 0.011) * (i % 2 ? 1 : -1);
    if (mat.current && state === "open") mat.current.opacity = 0.7 + 0.3 * Math.sin(t * 2.6);
    const el = labels.current[id];
    if (el && anchor.current) {                                   // etiqueta en el DOM, anclada al anillo (sin Html de drei)
      anchor.current.getWorldPosition(v).project(camera);
      el.style.transform = `translate(${(v.x * 0.5 + 0.5) * size.width}px, ${(-v.y * 0.5 + 0.5) * size.height}px) translate(-50%,-50%)`;
      el.style.opacity = v.z < 1 ? "1" : "0";
    }
  });
  const lw = state === "open" ? 2.4 : active || hover ? 1.8 : 1.1;
  const op = state === "absent" ? 0.16 : state === "open" ? 1 : active || hover ? 1 : 0.55;
  return (
    <group>
      <object3D ref={anchor} position={[(i % 2 ? 1 : -1) * 1.15, y, 0]} />{/* ancla fija, sin la inclinación del anillo: etiquetas a 0,2 m una de otra */}
    <group position={[0, y, 0]} rotation={[tilt, 0, roll]}>
      <group ref={g}>
        <Line ref={mat as never} points={pts} color={state === "open" ? SIGNAL : IVORY} lineWidth={lw} transparent opacity={op} dashed={state === "absent"} dashSize={0.04} gapSize={0.05} />
        <mesh onClick={(e) => { e.stopPropagation(); onPick(id); }} onPointerOver={() => { setHover(true); document.body.style.cursor = "pointer"; }}
          onPointerOut={() => { setHover(false); document.body.style.cursor = ""; }} rotation={[Math.PI / 2, 0, 0]} scale={[1, 0.82, 1]}>
          <torusGeometry args={[r, 0.06, 6, 48]} /><meshBasicMaterial transparent opacity={0} depthWrite={false} />
        </mesh>
      </group>
    </group>
    </group>
  );
}

export default function SuitScene({ ledger, picked, onPick, mode, indicators, pickedInd, onPickInd, onTapSuit, outfit, look, holo, layer }: {
  ledger: LedgerDay | null; picked: string | null; onPick: (id: string) => void; mode: "books" | "body"; indicators: Indicator[]; pickedInd: string | null; onPickInd: (id: string) => void; onTapSuit: () => void; outfit: "iva" | "eva"; look: CrewLook; holo: boolean; layer: "uniform" | "body";
}) {
  const labels: Labels = useRef({});
  const marks: Marks = useRef({});
  const { active, progress } = useProgress();
  const ready = !active && progress >= 100;
  const indState = (i?: Indicator) => (!i || i.bloqueado ? "blocked" : i.canal === "autorreporte" ? "channel" : i.crew ? (i.crew === "alarma" ? "alarm" : i.crew === "verde" ? "ok" : "channel") : (i.alarma ?? 0) > 0 ? "alarm" : "ok");
  const stateOf = (id: string): State => { const p = ledger?.presupuestos[id]; return !p ? "absent" : p.cierra ? "closes" : "open"; };
  return (
    <div className="absolute inset-0">
      <Canvas camera={{ position: [0, 1.1, 5.4], fov: 30, near: 2.5, far: 14 }} dpr={[1, 2]} gl={{ antialias: true, toneMapping: THREE.ACESFilmicToneMapping, toneMappingExposure: 1.05 }}>
        <hemisphereLight args={["#e9e2d6", "#1a1612", 0.55]} />
        <directionalLight position={[2.6, 3.2, 3]} intensity={2.6} color="#ffd9b3" />
        <directionalLight position={[-3, 2, -2.5]} intensity={1.5} color="#d9dde0" />
        <pointLight position={[0, 0.2, 1.6]} intensity={0.8} color="#ffb47a" distance={4} />
        <Rig />
        {holo && <Bay />}
        {outfit === "eva" ? <Suspense fallback={null}><Suit marks={marks} mode={mode} onTap={onTapSuit} holo={holo} /></Suspense> : <Suspense fallback={null}><CrewGLB name={look.indicativo} layer={layer} marks={marks} mode={mode} onTap={onTapSuit} holo={holo} /></Suspense>}
        <ContactShadows position={[0, 0, 0]} opacity={0.7} scale={4} blur={2.4} far={1.6} />
        {mode === "books" && BUDGETS.map(([id], i) => <Ring key={id} i={i} id={id} state={stateOf(id)} onPick={onPick} active={picked === id} labels={labels} />)}
      </Canvas>
      {!ready && <p className="pointer-events-none absolute inset-x-0 top-1/2 text-center font-mono text-[11px] uppercase tracking-[0.3em] text-ink-faint">Loading NASA Z-2 model…</p>}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        {INDICATOR_IDS.map((id) => {
          const st = indState(indicators.find((x) => x.indicador === id));
          return (
            <button key={id} ref={(el) => { marks.current[id] = el; }} onClick={() => onPickInd(id)} aria-label={`${INDICATOR_NAMES[id]} — open receipt`}
              className="group absolute left-0 top-0 flex items-center gap-2 opacity-0 will-change-transform focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-ink">
              <span className={`relative grid h-[22px] w-[22px] place-items-center rounded-full border ${pickedInd === id ? "border-ink bg-ink/20" : "border-ink-dim bg-bg/50"} backdrop-blur-sm`}>
                <span className={`h-[9px] w-[9px] rounded-full ${st === "alarm" ? "bg-signal animate-pulse" : st === "ok" ? "bg-ok" : st === "channel" ? "bg-ink-dim" : "border border-dashed border-ink-faint"}`} />
              </span>
              <span className="whitespace-nowrap bg-bg/80 px-1.5 py-px font-mono text-[10px] uppercase tracking-[0.2em] text-ink-dim backdrop-blur-sm group-hover:text-ink">{INDICATOR_NAMES[id]}</span>
            </button>
          );
        })}
        {mode === "books" && BUDGETS.map(([id, label]) => {
          const s = stateOf(id);
          return (
            <div key={id} ref={(el) => { labels.current[id] = el; }} className="absolute left-0 top-0 whitespace-nowrap font-mono text-[10px] uppercase tracking-[0.2em] will-change-transform [text-shadow:0_0_8px_#0d0c0b,0_0_2px_#0d0c0b]"
              style={{ color: s === "open" ? "var(--color-signal)" : s === "absent" ? "var(--color-ink-faint)" : "var(--color-ink-dim)" }}>
              {label}{s === "absent" ? " · no ledger" : s === "open" ? " · open" : ""}
            </div>
          );
        })}
      </div>
    </div>
  );
}
