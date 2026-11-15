"use client";
import { useMemo } from "react";
import * as THREE from "three";

/** Un tripulante del universo SIMULADO: personaje FICTICIO y estilizado (nunca una persona real). Se construye aquí con formas simples: sin modelos ni licencias de terceros. */
export type CrewLook = { indicativo: string; rol: string; color: string; piel: string; pelo: string; peinado: string; complexion: number };

/** Dónde se «toca» cada indicador oficial sobre la figura de interior (pies en y=0, altura ≈ 1,8; frente = +z). */
export const ANCHORS_IVA: Record<string, [number, number, number]> = {
  "sueño": [0, 1.82, 0.02], "ánimo": [-0.1, 1.7, 0.1], temperatura: [0, 1.53, 0.07], fc: [-0.09, 1.28, 0.14], "presión": [0.29, 1.27, 0.05], glucosa: [0, 0.98, 0.14],
};

const UNIFORM = "#b9b3a2", UNIFORM_DARK = "#8f8a7a", BOOT = "#2a211b";   // traje de vuelo gris cálido (claro, para destacar sobre el fondo)

function tag(text: string): THREE.CanvasTexture {
  const c = document.createElement("canvas"); c.width = 192; c.height = 56;
  const g = c.getContext("2d")!;
  g.fillStyle = "#e9e0cc"; g.fillRect(0, 0, 192, 56);
  g.fillStyle = "#1d1a16"; g.font = "bold 26px monospace"; g.textAlign = "center"; g.textBaseline = "middle"; g.fillText(text, 96, 29);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}

function Mat({ c, r = 0.85 }: { c: string; r?: number }) { return <meshStandardMaterial color={c} roughness={r} metalness={0} />; }

export function CrewMesh({ look }: { look: CrewLook }) {
  const w = look.complexion;
  const nameTag = useMemo(() => tag(look.indicativo), [look.indicativo]);
  const HY = 1.7;                                                       // centro de la cabeza
  const arm = 0.25 * w + 0.045;
  return (
    <group>
      {/* piernas y botas */}
      {[-1, 1].map((s) => (
        <group key={s}>
          <mesh position={[s * 0.09, 0.66, 0]}><capsuleGeometry args={[0.088, 0.32, 6, 16]} /><Mat c={UNIFORM} /></mesh>
          <mesh position={[s * 0.09, 0.28, 0.005]}><capsuleGeometry args={[0.07, 0.34, 6, 16]} /><Mat c={UNIFORM} /></mesh>
          <mesh position={[s * 0.09, 0.055, 0.045]} rotation={[Math.PI / 2, 0, 0]}><capsuleGeometry args={[0.07, 0.11, 6, 16]} /><Mat c={BOOT} r={0.6} /></mesh>
        </group>
      ))}
      {/* pelvis, cinturón y torso */}
      <mesh position={[0, 0.93, 0]} scale={[w * 1.05, 0.8, 0.78]}><sphereGeometry args={[0.175, 24, 16]} /><Mat c={UNIFORM} /></mesh>
      <mesh position={[0, 1.0, 0]} scale={[w * 1.05, 1, 0.78]}><cylinderGeometry args={[0.172, 0.172, 0.035, 28]} /><Mat c={UNIFORM_DARK} /></mesh>
      <mesh position={[0, 1.2, 0]} scale={[w * 1.1, 1, 0.74]}><capsuleGeometry args={[0.165, 0.3, 8, 24]} /><Mat c={UNIFORM} /></mesh>
      <mesh position={[0, 1.41, 0]} rotation={[0, 0, Math.PI / 2]} scale={[1, 1, 0.9]}><capsuleGeometry args={[0.068, 0.3 * w, 8, 20]} /><Mat c={UNIFORM} /></mesh>   {/* línea de hombros */}
      {/* brazos con franja del color del tripulante, y manos */}
      {[-1, 1].map((s) => (
        <group key={s}>
          <mesh position={[s * arm, 1.25, 0]} rotation={[0, 0, s * 0.05]}><capsuleGeometry args={[0.058, 0.26, 6, 16]} /><Mat c={UNIFORM} /></mesh>
          <mesh position={[s * (arm + 0.003), 1.35, 0]} rotation={[0, 0, s * 0.05]}><cylinderGeometry args={[0.0605, 0.0605, 0.04, 20]} /><Mat c={look.color} r={0.7} /></mesh>
          <mesh position={[s * (arm + 0.03), 0.99, 0.02]} rotation={[0, 0, s * 0.1]}><capsuleGeometry args={[0.05, 0.26, 6, 16]} /><Mat c={UNIFORM} /></mesh>
          <mesh position={[s * (arm + 0.05), 0.81, 0.03]}><sphereGeometry args={[0.056, 16, 12]} /><Mat c={look.piel} r={0.7} /></mesh>
        </group>
      ))}
      {/* cuello, cuello de la prenda y cabeza */}
      <mesh position={[0, 1.55, 0]}><cylinderGeometry args={[0.042, 0.048, 0.08, 16]} /><Mat c={look.piel} r={0.7} /></mesh>
      <mesh position={[0, 1.52, 0]} rotation={[Math.PI / 2, 0, 0]}><torusGeometry args={[0.062, 0.016, 10, 28]} /><Mat c={look.color} r={0.7} /></mesh>
      <group position={[0, HY, 0]}>
        <mesh scale={[0.92, 1.12, 1]}><sphereGeometry args={[0.108, 32, 24]} /><Mat c={look.piel} r={0.65} /></mesh>
        {[-1, 1].map((s) => (
          <group key={s}>
            <mesh position={[s * 0.097, -0.005, 0]}><sphereGeometry args={[0.019, 12, 10]} /><Mat c={look.piel} r={0.65} /></mesh>
            <mesh position={[s * 0.036, 0.012, 0.094]} scale={[1, 0.85, 0.5]}><sphereGeometry args={[0.0115, 12, 10]} /><meshStandardMaterial color="#1b1510" roughness={0.3} /></mesh>
            <mesh position={[s * 0.036, 0.042, 0.095]} rotation={[0, 0, -s * 0.12]}><boxGeometry args={[0.03, 0.0065, 0.006]} /><Mat c={look.pelo} /></mesh>
          </group>
        ))}
        <mesh position={[0, -0.012, 0.104]} scale={[1, 1.25, 1]}><sphereGeometry args={[0.0145, 12, 10]} /><Mat c={look.piel} r={0.6} /></mesh>
        <mesh position={[0, -0.04, 0.094]} rotation={[0, 0, Math.PI]}><torusGeometry args={[0.02, 0.0035, 6, 16, Math.PI]} /><meshStandardMaterial color="#8a4a3f" roughness={0.6} /></mesh>
        {/* cabello según el peinado */}
        {look.peinado !== "bald" && (
          <mesh position={[0, 0.012, -0.01]} scale={[0.97, 1.08, 1.0]}><sphereGeometry args={[look.peinado === "buzz" ? 0.102 : 0.108, 28, 18, 0, Math.PI * 2, 0, Math.PI * (look.peinado === "buzz" ? 0.46 : 0.56)]} /><Mat c={look.pelo} r={0.9} /></mesh>
        )}
        {look.peinado === "bun" && <mesh position={[0, 0.115, -0.05]}><sphereGeometry args={[0.04, 14, 12]} /><Mat c={look.pelo} r={0.9} /></mesh>}
        {look.peinado === "long" && <mesh position={[0, -0.07, -0.075]} scale={[1, 1, 0.55]}><capsuleGeometry args={[0.085, 0.16, 6, 16]} /><Mat c={look.pelo} r={0.9} /></mesh>}
      </group>
      {/* placa con el indicativo (pecho derecho) y su subrayado de color */}
      <mesh position={[0.1 * w, 1.27, 0.118 * 1.0 + 0.012]}><planeGeometry args={[0.1, 0.03]} /><meshStandardMaterial map={nameTag} roughness={0.8} /></mesh>
      <mesh position={[0.1 * w, 1.247, 0.118 + 0.012]}><planeGeometry args={[0.1, 0.006]} /><meshBasicMaterial color={look.color} /></mesh>
    </group>
  );
}
