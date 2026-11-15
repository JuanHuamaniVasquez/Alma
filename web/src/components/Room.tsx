"use client";
import { useEffect } from "react";
import { AlmaDock, useAlma } from "./Alma";
import { Provenance } from "./Provenance";

/** Marco común de una sala: fondo, voz de la sala al entrar, y ALMA abajo a la izquierda. */
export function Room({ voice, children, scroll = false }: { voice?: string; children: React.ReactNode; scroll?: boolean }) {
  const { say, has } = useAlma();
  const ready = voice ? has(voice) : false;
  useEffect(() => { if (voice && ready) say(voice); }, [voice, ready]); // eslint-disable-line react-hooks/exhaustive-deps
  return (
    <div className={`absolute inset-0 ${scroll ? "overflow-y-auto pb-44" : ""}`} style={{ background: "radial-gradient(70% 60% at 50% 30%, #231b14 0%, #14110e 60%, #0d0c0b 100%)" }}>
      {children}
      <AlmaDock room={voice} />
      <Provenance />
    </div>
  );
}
