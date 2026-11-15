"use client";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { ContactShadows, Line, useGLTF, useProgress } from "@react-three/drei";
import { Suspense, useMemo, useRef, useState } from "react";
import * as THREE from "three";
import { BUDGETS, INDICATOR_NAMES, type Indicator, type LedgerDay } from "@/lib/api";

useGLTF.setDecoderPath("/draco/");
useGLTF.preload("/models/z2.glb");
const HEIGHT = 1.9, FOCUS_Y = 0.98;
const IVORY = "#efe8da", SIGNAL = "#ff5a1f";
type State = "closes" | "open" | "absent";
type Labels = React.MutableRefObject<Record<string, HTMLDivElement | null>>;
type Marks = React.MutableRefObject<Record<string, HTMLButtonElement | null>>;

/** Dónde se «toca» cada indicador oficial del reto sobre la figura (coordenadas del modelo normalizado: pies en y=0, altura 1,9; frente = +z). */
const BODY_ANCHORS: Record<string, [number, number, number]> = {
  "sueño": [0, 1.86, 0.02], "ánimo": [-0.16, 1.7, 0.2], temperatura: [0, 1.52, 0.22], fc: [-0.1, 1.3, 0.3], "presión": [0.42, 1.28, 0.05], glucosa: [0, 0.95, 0.3],
};

/** Traje NASA Z-2 (NASA 3D Resources, sin copyright). Visor oscuro y sin cara: la persona es el cuerpo, nunca un avatar. */
function Suit({ marks, mode }: { marks: Marks; mode: "books" | "body" }) {
  const anchors = useRef<Record<string, THREE.Object3D | null>>({});
  const v = useMemo(() => new THREE.Vector3(), []);
  const { size } = useThree();
  const { scene } = useGLTF(typeof window !== "undefined" && window.location.search.includes("orig") ? "/models/z2_orig.glb" : "/models/z2.glb");
  const ref = useRef<THREE.Group>(null);
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
  useFrame(({ clock, camera }) => {
    if (ref.current) ref.current.rotation.y = Math.sin(clock.elapsedTime * 0.2) * 0.5;
    for (const id of Object.keys(BODY_ANCHORS)) {                  // marcadores del DOM anclados al cuerpo; se atenúan si miran hacia dentro
      const a = anchors.current[id], el = marks.current[id];
      if (!a || !el) continue;
      a.getWorldPosition(v);
      const frente = v.x * camera.position.x + (v.z) * camera.position.z > 0;
      v.project(camera);
      el.style.transform = `translate(${(v.x * 0.5 + 0.5) * size.width}px, ${(-v.y * 0.5 + 0.5) * size.height}px) translate(-50%,-50%)`;
      el.style.opacity = mode === "body" ? (frente ? "1" : "0.25") : "0";
      el.style.pointerEvents = mode === "body" && frente ? "auto" : "none";
    }
  });
  return (
    <group ref={ref}>
      <primitive object={model} />
      {Object.entries(BODY_ANCHORS).map(([id, p]) => <object3D key={id} ref={(o) => { anchors.current[id] = o; }} position={p} />)}
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

export default function SuitScene({ ledger, picked, onPick, mode, indicators, pickedInd, onPickInd }: {
  ledger: LedgerDay | null; picked: string | null; onPick: (id: string) => void; mode: "books" | "body"; indicators: Indicator[]; pickedInd: string | null; onPickInd: (id: string) => void;
}) {
  const labels: Labels = useRef({});
  const marks: Marks = useRef({});
  const { active, progress } = useProgress();
  const ready = !active && progress >= 100;
  const indState = (i?: Indicator) => (!i || i.bloqueado ? "blocked" : i.canal === "autorreporte" ? "channel" : (i.alarma ?? 0) > 0 ? "alarm" : "ok");
  const stateOf = (id: string): State => { const p = ledger?.presupuestos[id]; return !p ? "absent" : p.cierra ? "closes" : "open"; };
  return (
    <div className="absolute inset-0">
      <Canvas camera={{ position: [0, 1.1, 5.4], fov: 30 }} dpr={[1, 2]} gl={{ antialias: true, toneMapping: THREE.ACESFilmicToneMapping, toneMappingExposure: 1.05 }}>
        <hemisphereLight args={["#e9e2d6", "#1a1612", 0.55]} />
        <directionalLight position={[2.6, 3.2, 3]} intensity={2.6} color="#ffd9b3" />
        <directionalLight position={[-3, 2, -2.5]} intensity={1.5} color="#d9dde0" />
        <pointLight position={[0, 0.2, 1.6]} intensity={0.8} color="#ffb47a" distance={4} />
        <Rig />
        <Suspense fallback={null}><Suit marks={marks} mode={mode} /></Suspense>
        <ContactShadows position={[0, 0, 0]} opacity={0.7} scale={4} blur={2.4} far={1.6} />
        {mode === "books" && BUDGETS.map(([id], i) => <Ring key={id} i={i} id={id} state={stateOf(id)} onPick={onPick} active={picked === id} labels={labels} />)}
      </Canvas>
      {!ready && <p className="pointer-events-none absolute inset-x-0 top-1/2 text-center font-mono text-[11px] uppercase tracking-[0.3em] text-ink-faint">Loading NASA Z-2 model…</p>}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        {Object.keys(BODY_ANCHORS).map((id) => {
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
