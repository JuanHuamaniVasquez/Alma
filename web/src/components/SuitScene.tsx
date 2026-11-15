"use client";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { ContactShadows, Line, useGLTF } from "@react-three/drei";
import { Suspense, useMemo, useRef, useState } from "react";
import * as THREE from "three";
import { BUDGETS, type LedgerDay } from "@/lib/api";

useGLTF.setDecoderPath("/draco/");
useGLTF.preload("/models/z2.glb");
const HEIGHT = 1.9, FOCUS_Y = 0.98;
const IVORY = "#efe8da", SIGNAL = "#ff5a1f";
type State = "closes" | "open" | "absent";
type Labels = React.MutableRefObject<Record<string, HTMLDivElement | null>>;

/** Traje NASA Z-2 (NASA 3D Resources, sin copyright). Visor oscuro y sin cara: la persona es el cuerpo, nunca un avatar. */
function Suit() {
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
  useFrame(({ clock }) => { if (ref.current) ref.current.rotation.y = Math.sin(clock.elapsedTime * 0.2) * 0.5; });
  return <group ref={ref}><primitive object={model} /></group>;
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
    <group position={[0, y, 0]} rotation={[tilt, 0, roll]}>
      <object3D ref={anchor} position={[(i % 2 ? 1 : -1) * 1.05, 0, 0]} />
      <group ref={g}>
        <Line ref={mat as never} points={pts} color={state === "open" ? SIGNAL : IVORY} lineWidth={lw} transparent opacity={op} dashed={state === "absent"} dashSize={0.04} gapSize={0.05} />
        <mesh onClick={(e) => { e.stopPropagation(); onPick(id); }} onPointerOver={() => { setHover(true); document.body.style.cursor = "pointer"; }}
          onPointerOut={() => { setHover(false); document.body.style.cursor = ""; }} rotation={[Math.PI / 2, 0, 0]} scale={[1, 0.82, 1]}>
          <torusGeometry args={[r, 0.06, 6, 48]} /><meshBasicMaterial transparent opacity={0} depthWrite={false} />
        </mesh>
      </group>
    </group>
  );
}

export default function SuitScene({ ledger, picked, onPick }: { ledger: LedgerDay | null; picked: string | null; onPick: (id: string) => void }) {
  const labels: Labels = useRef({});
  const stateOf = (id: string): State => { const p = ledger?.presupuestos[id]; return !p ? "absent" : p.cierra ? "closes" : "open"; };
  return (
    <div className="absolute inset-0">
      <Canvas camera={{ position: [0, 1.1, 5.4], fov: 30 }} dpr={[1, 2]} gl={{ antialias: true, toneMapping: THREE.ACESFilmicToneMapping, toneMappingExposure: 1.05 }}>
        <hemisphereLight args={["#e9e2d6", "#1a1612", 0.55]} />
        <directionalLight position={[2.6, 3.2, 3]} intensity={2.6} color="#ffd9b3" />
        <directionalLight position={[-3, 2, -2.5]} intensity={1.5} color="#d9dde0" />
        <pointLight position={[0, 0.2, 1.6]} intensity={0.8} color="#ffb47a" distance={4} />
        <Rig />
        <Suspense fallback={null}><Suit /></Suspense>
        <ContactShadows position={[0, 0, 0]} opacity={0.7} scale={4} blur={2.4} far={1.6} />
        {BUDGETS.map(([id], i) => <Ring key={id} i={i} id={id} state={stateOf(id)} onPick={onPick} active={picked === id} labels={labels} />)}
      </Canvas>
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        {BUDGETS.map(([id, label]) => {
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
