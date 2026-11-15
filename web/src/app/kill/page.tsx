"use client";
import { useEffect, useState } from "react";
import { Room } from "@/components/Room";
import { Stamp } from "@/components/Stamp";
import { get, type DemoKill } from "@/lib/api";

const MAX = 6; // la cinta va de 0 a 6σ

/** 02 · THE LEAK — la demo kill: el mismo día, los mismos datos, dos detectores. Uno compara contra el manifiesto; el otro, contra una ley. */
export default function Kill() {
  const [d, setD] = useState<DemoKill | null>(null);
  const [leak, setLeak] = useState(false);
  useEffect(() => { get<DemoKill>("/api/demo-kill/").then(setD); if (new URLSearchParams(window.location.search).has("leak")) setLeak(true); }, []);
  if (!d) return <Room><p className="p-10 font-mono text-xs uppercase tracking-widest text-ink-faint">FB-005-D1 has not been executed. Nothing is shown.</p></Room>;
  const day = leak ? d.fuga : d.control;
  const a = Math.abs(day.A_manifiesto.z), b = Math.abs(day.B_ley.residuo_kg) / day.B_ley.sigma_propagada_kg;
  const closes = day.B_ley.veredicto === "CIERRA";
  return (
    <Room voice="demo_kill" scroll hero="leak" heroFocus="50% 30%">
      <div className="mx-auto max-w-6xl px-10 pt-10">
        <h1 className="font-display text-5xl leading-tight">Same day. Same data.<br /><span className="text-ink-dim">Two detectors.</span></h1>
        <div className="mt-6 flex items-center gap-5">
          <button onClick={() => setLeak((v) => !v)} className={`border px-4 py-2 font-mono text-[11px] uppercase tracking-[0.2em] transition-colors ${leak ? "border-signal bg-signal text-bg" : "border-ink-dim text-ink hover:border-ink"}`}>
            {leak ? `Leak injected · ${day.fuga_kg.toFixed(2)} kg — remove` : "Inject a 0.30 kg leak"}
          </button>
          <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink-faint">simulated day · not astronaut data</span>
        </div>
        <div className="mt-10 grid min-h-[21rem] grid-cols-2 gap-0 border-t border-line">
          <Column kicker="A · against the manifest" title="What the plan says should happen" big={`${a.toFixed(2)}σ`} sigma={a} alarm={day.A_manifiesto.alarma}
            verdict={day.A_manifiesto.alarma ? "ALARM" : "NO ALARM"} note={leak ? "The manifest sees a perfectly ordinary day." : "A quiet day, as expected."} />
          <Column kicker="B · against the law" title="What conservation of mass says must hold" big={`${day.B_ley.residuo_kg >= 0 ? "+" : "−"}${Math.abs(day.B_ley.residuo_kg).toFixed(3)} kg`} sigma={b} alarm={!closes} left
            verdict={closes ? "THE LOOP CLOSES" : "THE LOOP DOES NOT CLOSE"} note={closes ? "Inside the propagated uncertainty." : `Beyond ${2}σ of its own uncertainty (${day.B_ley.sigma_propagada_kg.toFixed(3)} kg): an investigation opens.`} />
        </div>
        <footer className="mt-6 flex flex-wrap items-center gap-x-6 gap-y-2 border-t border-line pt-4 font-mono text-[10px] uppercase tracking-[0.14em] text-ink-dim">
          <span>Preregistered {d.acta}</span><span className="text-ink">sha256 {d.hash_acta}</span>
          <span>registered {d.acta_registrada_utc.replace("T", " ").replace("Z", " UTC")}</span>
          <span>run {d.ts_ejecucion_utc.replace("T", " ").replace("Z", " UTC")}</span><span>seed {d.semilla}</span>
          <Stamp banner="SIMULADO" />
        </footer>
      </div>
    </Room>
  );
}

function Column({ kicker, title, big, sigma, alarm, verdict, note, left }: { kicker: string; title: string; big: string; sigma: number; alarm: boolean; verdict: string; note: string; left?: boolean }) {
  return (
    <section className={`px-10 pt-8 ${left ? "border-l border-line" : ""}`}>
      <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-ink-faint">{kicker}</p>
      <p className="mt-1 text-sm text-ink-dim">{title}</p>
      <p className={`mt-7 font-display text-[5.5rem] leading-none transition-colors duration-700 ${alarm ? "text-signal" : "text-ink"}`}>{big}</p>
      <div className="relative mt-10 h-px bg-ink-faint">
        {[0, 1, 2, 3, 4, 5, 6].map((t) => <span key={t} className="absolute top-0 h-2 w-px bg-ink-faint" style={{ left: `${(t / MAX) * 100}%` }} />)}
        <span className="absolute -top-3 h-6 w-[2px] bg-warn" style={{ left: `${(2 / MAX) * 100}%` }} />
        <span className="absolute -top-8 -translate-x-1/2 font-mono text-[9px] uppercase tracking-widest text-warn" style={{ left: `${(2 / MAX) * 100}%` }}>2σ alarm line</span>
        <span className={`absolute -top-[7px] h-[15px] w-[15px] -translate-x-1/2 rotate-45 transition-all duration-1000 ease-out ${alarm ? "bg-signal" : "bg-ink"}`} style={{ left: `${Math.min(sigma / MAX, 1) * 100}%` }} />
      </div>
      <p className="mt-9 font-mono text-[12px] uppercase tracking-[0.2em]" style={{ color: alarm ? "var(--color-signal)" : "var(--color-ink)" }}>{verdict}</p>
      <p className="mt-2 max-w-sm text-sm leading-relaxed text-ink-dim">{note}</p>
    </section>
  );
}
