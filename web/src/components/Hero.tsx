"use client";
import { useEffect, useState } from "react";

type Credit = { nasa_id: string; titulo: string | null; centro: string | null; fecha: string; url: string };

/** Foto REAL de la Biblioteca de Imágenes de NASA como cabecera de sala (dominio público en general; siempre con su crédito y enlace; no implica respaldo de NASA). */
export function Hero({ room, focus = "50% 40%" }: { room: string; focus?: string }) {
  const [c, setC] = useState<Credit | null>(null);
  useEffect(() => { fetch("/nasa/credits.json").then((r) => r.json()).then((j: Record<string, Credit>) => setC(j[room] ?? null)).catch((e) => console.warn("NASA credits unavailable", e)); }, [room]);
  return (
    <figure className="relative h-60 w-full overflow-hidden border-b border-line" aria-label="NASA photograph">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={`/nasa/${room}.jpg`} alt={c?.titulo ?? "NASA photograph"} className="h-full w-full object-cover opacity-60" style={{ objectPosition: focus }} loading="lazy" />
      <div className="absolute inset-0 bg-gradient-to-t from-bg via-bg/30 to-bg/70" />
      {c && (
        <figcaption className="absolute bottom-2 right-5 max-w-[60%] text-right font-mono text-[9px] uppercase tracking-[0.14em] text-ink-faint">
          <a href={c.url} target="_blank" rel="noreferrer" className="hover:text-ink">NASA{c.centro ? ` / ${c.centro}` : ""} · {c.nasa_id} · {c.fecha.slice(0, 4)} ↗</a>
        </figcaption>
      )}
    </figure>
  );
}
