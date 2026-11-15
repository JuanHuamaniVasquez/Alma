"use client";
import { usePathname } from "next/navigation";
import { useState } from "react";

/** «¿Qué es real aquí?» — procedencia de lo que se ve en cada sala, en dos listas. Mantener alineado con docs/politica-de-datos.md (fuentes S-xx y simulados X-xx). */
const MAP: Record<string, { real: string[]; sim: string[] }> = {
  "/": { real: ["Heart-rate and sleep states: everyday people (LifeSnaps, not astronauts), one anonymous stand-in per crew member", "Mood reports typed on this demo", "NASA Z-2 suit model (NASA 3D Resources)"], sim: ["The five crew members and their 3D bodies (fictional)", "The habitat's air and water books (simulated universe)", "Anatomy: illustrative, not a scan"] },
  "/machine": { real: ["The detection rules (2σ, CUSUM) and their maths"], sim: ["The habitat's consumption stream (simulated universe)"] },
  "/kill": { real: ["The preregistered hash, published before the run"], sim: ["The hidden leak and the 400 runs (simulated)"] },
  "/vault": { real: ["Every sealed record, its SHA-256 and its date", "Results on real wearable data (LifeSnaps, not astronauts)"], sim: ["Records tagged simulated or real+simulated say so on their row"] },
  "/foundry": { real: ["Sources: DOIs, NTRS reports, NASA OSDR identifiers", "Outcomes of tests run on real data"], sim: ["Cards that depend on missing data stay blocked, never filled in"] },
  "/storm": { real: ["The Sun: NASA SDO imagery", "Planetary Kp index: NOAA SWPC, live"], sim: ["The G1–G5 scenarios (clearly marked)"] },
  "/budget": { real: ["Privacy counts: derived from the real stand-in states, with noise", "NASA planning figures for air and water"], sim: ["The habitat's air and water ledger (simulated universe); the other seven books are empty on purpose"] },
  "/capsule": { real: ["Results exported from preregistered tests on real data"], sim: ["Anything produced by simulation is labelled on its own capsule"] },
};

export function Origins() {
  const path = usePathname() ?? "/";
  const [open, setOpen] = useState(false);
  const m = MAP[path];
  if (!m) return null;
  return (
    <div className="absolute bottom-4 right-6 z-30 text-right font-mono text-[10px] uppercase tracking-[0.18em]">
      {open && (
        <div className="mb-2 w-[22rem] max-w-[86vw] border border-ink-faint/40 bg-[#14110e]/95 p-4 text-left normal-case tracking-normal text-ink-dim backdrop-blur" role="dialog" aria-label="What is real here">
          <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink">Real</p>
          <ul className="mb-3 mt-1 space-y-1 text-[12px] leading-snug">{m.real.map((t) => <li key={t}>· {t}</li>)}</ul>
          <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-[#ffb45c]">Simulated</p>
          <ul className="mt-1 space-y-1 text-[12px] leading-snug">{m.sim.map((t) => <li key={t}>· {t}</li>)}</ul>
        </div>
      )}
      <button onClick={() => setOpen(!open)} aria-expanded={open} className="border-b border-ink-faint/60 pb-0.5 text-ink-faint transition-colors hover:text-ink">{open ? "Close" : "What is real here?"}</button>
    </div>
  );
}
