"use client";
import { Canvas, useFrame } from "@react-three/fiber";
import { ContactShadows, Html, Line, useGLTF } from "@react-three/drei";
import { useMemo, useRef, useState } from "react";
import * as THREE from "three";
import { BUDGETS, type LedgerDay } from "@/lib/api";

useGLTF.setDecoderPath("/draco/");
const HEIGHT = 1.9;
const IVORY = "#efe8da", SIGNAL = "#ff5a1f";

/** Traje NASA Z-2 (NASA 3D Resources, sin copyright). Visor oscuro y sin cara: la persona es el cuerpo, nunca un avatar. */
function Suit() {
  const { scene } = useGLTF("/models/z2.glb");
  const ref = useRef<THREE.Group>(null);
  const model = useMemo(() => {
    const m = scene.clone(true);
    const box = new THREE.Box3().setFromObject(m), size = box.getSize(new THREE.Vector3()), c = box.getCenter(new THREE.Vector3());
    const k = HEIGHT / size.y;
    m.scale.setScalar(k); m.position.set(-c.x * k, -box.min.y * k, -c.z * k);
    return m;
  }, [scene]);
  useFrame(({ clock }) => { if (ref.current) ref.current.rotation.y = Math.sin(clock.elapsedTime * 0.22) * 0.55; });
  return <group ref={ref}><primitive object={model} /></group>;
}

type RingProps = { i: number; id: string; label: string; state: "closes" | "open" | "absent"; onPick: (id: string) => void; active: boolean };

/** Un anillo = un presupuesto. Marfil fino si cierra; naranja señal que pulsa si NO cierra (regla: |residuo| > 2σ); punteado si no hay libro. */
function Ring({ i, id, label, state, onPick, active }: RingProps) {
  const g = useRef<THREE.Group>(null);
  const mat = useRef<THREE.LineBasicMaterial>(null);
  const y = 0.18 + (i / 8) * 1.62, r = 0.78 + 0.16 * Math.sin(i * 1.7), tilt = 0.5 * Math.sin(i * 2.3), roll = 0.35 * Math.cos(i * 1.3);
  const pts = useMemo(() => Array.from({ length: 129 }, (_, k) => { const a = (k / 128) * Math.PI * 2; return new THREE.Vector3(Math.cos(a) * r, 0, Math.sin(a) * r * 0.82); }), [r]);
  const [hover, setHover] = useState(false);
  useFrame(({ clock }) => {
    const t = clock.elapsedTime;
    if (g.current) g.current.rotation.y = t * (0.08 + i * 0.012) * (i % 2 ? 1 : -1);
    if (mat.current && state === "open") mat.current.opacity = 0.65 + 0.35 * Math.sin(t * 2.6);
  });
  const color = state === "open" ? SIGNAL : IVORY;
  const lw = state === "open" ? 2.2 : active || hover ? 1.8 : 1;
  const op = state === "absent" ? 0.28 : state === "open" ? 1 : active || hover ? 0.95 : 0.5;
  return (
    <group position={[0, y, 0]} rotation={[tilt, 0, roll]}>
      <group ref={g}>
        <Line points={pts} color={color} lineWidth={lw} transparent opacity={op} dashed={state === "absent"} dashSize={0.05} gapSize={0.05} />
        <mesh onClick={(e) => { e.stopPropagation(); onPick(id); }} onPointerOver={() => { setHover(true); document.body.style.cursor = "pointer"; }}
          onPointerOut={() => { setHover(false); document.body.style.cursor = ""; }} rotation={[Math.PI / 2, 0, 0]} scale={[1, 0.82, 1]}>
          <torusGeometry args={[r, 0.07, 6, 48]} /><meshBasicMaterial transparent opacity={0} depthWrite={false} />
        </mesh>
        <Html position={[r, 0, 0]} center distanceFactor={7} zIndexRange={[10, 0]} style={{ pointerEvents: "none" }}>
          <div className={`whitespace-nowrap font-mono text-[10px] uppercase tracking-[0.2em] ${state === "open" ? "text-signal" : state === "absent" ? "text-ink-faint" : "text-ink-dim"}`}>
            {label}{state === "absent" ? " · no ledger" : ""}
          </div>
        </Html>
      </group>
    </group>
  );
}

export default function SuitScene({ ledger, picked, onPick }: { ledger: LedgerDay | null; picked: string | null; onPick: (id: string) => void }) {
  return (
    <Canvas camera={{ position: [0, 1.05, 4.4], fov: 32 }} dpr={[1, 2]} gl={{ antialias: true, toneMapping: THREE.ACESFilmicToneMapping, toneMappingExposure: 1.05 }}>
      <hemisphereLight args={["#e9e2d6", "#1a1612", 0.55]} />
      <directionalLight position={[2.6, 3.2, 3]} intensity={2.6} color="#ffd9b3" />
      <directionalLight position={[-3, 2, -2.5]} intensity={1.5} color="#d9dde0" />
      <pointLight position={[0, 0.2, 1.6]} intensity={0.8} color="#ffb47a" distance={4} />
      <Suit />
      <ContactShadows position={[0, 0, 0]} opacity={0.65} scale={4} blur={2.4} far={1.6} />
      {BUDGETS.map(([id, label], i) => {
        const p = ledger?.presupuestos[id];
        return <Ring key={id} i={i} id={id} label={label} state={!p ? "absent" : p.cierra ? "closes" : "open"} onPick={onPick} active={picked === id} />;
      })}
    </Canvas>
  );
}
