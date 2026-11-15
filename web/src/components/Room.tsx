"use client";
import { useEffect } from "react";
import { AlmaDock, useAlma } from "./Alma";
import { Hero } from "./Hero";
import { Origins } from "./Origins";

/** Marco común de una sala: fondo, voz de la sala al entrar, y ALMA abajo a la izquierda. */
export function Room({ voice, children, scroll = false, hero, heroFocus }: { voice?: string; children: React.ReactNode; scroll?: boolean; hero?: string; heroFocus?: string }) {
  const { say, has } = useAlma();
  const ready = voice ? has(voice) : false;
  useEffect(() => { if (voice && ready) say(voice); }, [voice, ready]); // eslint-disable-line react-hooks/exhaustive-deps
  const fondo = { background: "radial-gradient(70% 60% at 50% 30%, #231b14 0%, #14110e 60%, #0d0c0b 100%)" };
  if (scroll) {                                   // sala de lectura: el contenido se desplaza SOBRE la barra de ALMA, nunca por debajo (M3.8)
    return (
      <div className="absolute inset-0 flex flex-col" style={fondo}>
        <div className="relative min-h-0 flex-1 overflow-y-auto">{hero && <Hero room={hero} focus={heroFocus} />}{children}<div className="h-8" /></div>
        <AlmaDock room={voice} docked />
        <Origins />
      </div>
    );
  }
  return (
    <div className="absolute inset-0" style={fondo}>
      {children}
      <AlmaDock room={voice} />
      <Origins />
    </div>
  );
}
