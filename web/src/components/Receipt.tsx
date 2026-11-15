"use client";
import { useRef, useState } from "react";
import { CREW_STATE_EN, crewId, type Banner, type HabitatLine } from "@/lib/api";
import { Stamp } from "./Stamp";

const fmt = (x: number) => (x >= 0 ? "+" : "−") + Math.abs(x).toFixed(3);

/** El recibo: papel marfil que sale de una ranura. Nivel 2 de profundidad: los números reales y la regla que decidió el color. */
export function Receipt({ line, label, day, banner, onClose }: { line: HabitatLine | null; label: string; day: number; banner: Banner; onClose: () => void }) {
  const k = 2; // K_CIERRE (DC-04): cierra ⇔ |residuo| ≤ 2·σ del manifiesto
  return (
    <aside aria-label={`Receipt for ${label}`} className="absolute right-8 top-0 z-20 w-[22rem]">
      <div className="mx-4 h-[5px] rounded-b bg-black shadow-[0_2px_0_rgb(255_255_255/.06)]" />
      <div className="slot-in relative -mt-px rotate-[0.6deg] bg-paper px-6 pb-6 pt-5 font-mono text-[12px] leading-relaxed text-paper-ink shadow-[0_24px_50px_-12px_rgb(0_0_0/.7)]"
        style={{ clipPath: "polygon(0 0,100% 0,100% calc(100% - 7px),97% 100%,94% calc(100% - 7px),91% 100%,88% calc(100% - 7px),85% 100%,82% calc(100% - 7px),79% 100%,76% calc(100% - 7px),73% 100%,70% calc(100% - 7px),67% 100%,64% calc(100% - 7px),61% 100%,58% calc(100% - 7px),55% 100%,52% calc(100% - 7px),49% 100%,46% calc(100% - 7px),43% 100%,40% calc(100% - 7px),37% 100%,34% calc(100% - 7px),31% 100%,28% calc(100% - 7px),25% 100%,22% calc(100% - 7px),19% 100%,16% calc(100% - 7px),13% 100%,10% calc(100% - 7px),7% 100%,4% calc(100% - 7px),0 100%)" }}>
        <button onClick={onClose} aria-label="Close receipt" className="absolute right-4 top-3 text-paper-dim hover:text-paper-ink">×</button>
        <div className="flex items-baseline justify-between border-b border-dashed border-paper-dim/50 pb-3">
          <span className="font-display text-[1.7rem] leading-none">{label}</span>
          <span className="text-[10px] uppercase tracking-[0.18em] text-paper-dim">Day {day}</span>
        </div>
        {line ? (
          <>
            <dl className="mt-4 space-y-1.5">
              <Row k="expected (manifest)" v={line.emision_esperada.toFixed(3) + " kg"} />
              <Row k="observed" v={line.emision_observada.toFixed(3) + " kg"} />
              <Row k="residual" v={fmt(line.residuo_contable) + " kg"} strong />
              <Row k="manifest σ" v={line.incertidumbre_del_manifiesto.toFixed(3) + " kg"} />
            </dl>
            <p className="mt-4 border-t border-dashed border-paper-dim/50 pt-3 text-[11px]">
              <span className="uppercase tracking-[0.14em] text-paper-dim">rule </span>
              closes ⇔ |residual| ≤ {k}σ = {(k * line.incertidumbre_del_manifiesto).toFixed(3)} kg
            </p>
            <p className="mt-2 text-[11px] font-medium">
              {line.cierra ? "→ CLOSES: inside the stated uncertainty." : "→ DOES NOT CLOSE: a question, not a verdict."}
            </p>
          </>
        ) : (
          <p className="mt-4 text-[12px]">No ledger line exists for this book. <b>The absence is data:</b> nothing is drawn, nothing is invented.</p>
        )}
        <div className="mt-5 flex items-center justify-between">
          <span className="text-[10px] uppercase tracking-[0.14em] text-paper-dim">source · /api/libro · DC-04</span>
          <Stamp banner={banner} />
        </div>
      </div>
    </aside>
  );
}

function Row({ k, v, strong }: { k: string; v: string; strong?: boolean }) {
  return (
    <div className="flex justify-between gap-4"><dt className="text-paper-dim">{k}</dt><dd className={strong ? "font-medium" : ""}>{v}</dd></div>
  );
}

/** Recibo de un indicador oficial del reto (estado agregado de la cohorte; nunca ids ni valores). Lo bloqueado se declara, no se simula. */
export function IndicatorSlip({ ind, name, onClose, onSent, crewName }: { ind: import("@/lib/api").Indicator | undefined; name: string; onClose: () => void; onSent: () => void; crewName?: string }) {
  if (ind?.canal === "autorreporte") return <MoodSlip ind={ind} name={name} onClose={onClose} onSent={onSent} />;
  const blocked = !ind || !!ind.bloqueado;
  const n = ind?.personas_con_linea_base ?? 0;
  return (
    <aside aria-label={`Receipt for ${name}`} className="absolute right-8 top-0 z-20 w-[22rem]">
      <div className="mx-4 h-[5px] rounded-b bg-black shadow-[0_2px_0_rgb(255_255_255/.06)]" />
      <div className="slot-in relative -mt-px rotate-[0.6deg] bg-paper px-6 pb-6 pt-5 font-mono text-[12px] leading-relaxed text-paper-ink shadow-[0_24px_50px_-12px_rgb(0_0_0/.7)]">
        <button onClick={onClose} aria-label="Close receipt" className="absolute right-4 top-3 text-paper-dim hover:text-paper-ink">×</button>
        <div className="flex items-baseline justify-between border-b border-dashed border-paper-dim/50 pb-3">
          <span className="font-display text-[1.7rem] leading-none">{name}</span>
          <span className="text-[10px] uppercase tracking-[0.18em] text-paper-dim">official indicator</span>
        </div>
        {blocked ? (
          <p className="mt-4 text-[12px]"><b>No data.</b> {ind?.bloqueado ?? "Not loaded."} <b>The absence is data</b>: nothing is drawn, nothing is invented.</p>
        ) : (
          <>
            {ind!.crew && crewName && (
              <p className="mt-4 bg-paper-ink px-3 py-2 text-[11.5px] leading-snug text-paper"><b className="uppercase tracking-[0.12em]">{crewName}</b> · {CREW_STATE_EN[ind!.crew]}.<br /><span className="text-paper/70">Stand-in: an anonymous everyday person's state, not an astronaut's.</span></p>
            )}
            <dl className="mt-4 space-y-1.5">
              <Row k="people with a baseline" v={String(n)} />
              <Row k="green with receipt" v={String(ind!.verde)} />
              <Row k="alarm with receipt" v={String(ind!.alarma)} strong={(ind!.alarma ?? 0) > 0} />
              <Row k="too few days to say" v={String(ind!.sin_datos_suficientes)} />
              <Row k="window coverage" v={ind!.cobertura_media != null ? `${Math.round(ind!.cobertura_media * 100)} %` : "—"} />
            </dl>
            <p className="mt-4 border-t border-dashed border-paper-dim/50 pt-3 text-[11px]">
              <span className="uppercase tracking-[0.14em] text-paper-dim">a green means </span>
              it could have seen a drop of ≥ {ind!.mde_sigma_mediana}σ with {Math.round((ind!.potencia_declarada ?? 0) * 100)} % power, given the days observed — nothing more.
            </p>
            <p className="mt-2 text-[11px]"><span className="uppercase tracking-[0.14em] text-paper-dim">dot colour </span>orange ⇔ at least one active alarm with a receipt; sage otherwise.</p>
            {ind!.indicador === "fc" && <p className="mt-2 text-[11px] font-medium">Known limit: daily pulse is autocorrelated, and this detector raised false alarms in 7 of 144 real pulse windows (act FB-009). Treat an alarm as a question.</p>}
          </>
        )}
        <div className="mt-5 flex items-center justify-between">
          <span className="text-[10px] uppercase tracking-[0.14em] text-paper-dim">{blocked ? "source · /api/indicadores" : "everyday people · not astronauts"}</span>
          <Stamp banner={blocked ? "REAL" : (ind!.banner ?? "REAL")} />
        </div>
      </div>
    </aside>
  );
}


const MOODS = ["Very low", "Low", "Okay", "Good", "Very good"];

/** Ánimo en 3 toques (1: abrir el marcador · 2: elegir · 3: enviar). El tiempo de respuesta se MIDE aquí (DC-02) y es dato. Sin texto libre. */
function MoodSlip({ ind, name, onClose, onSent }: { ind: import("@/lib/api").Indicator; name: string; onClose: () => void; onSent: () => void }) {
  const t0 = useRef(performance.now());
  const [val, setVal] = useState<number | null>(null);
  const dur = useRef<number | null>(null);
  const [state, setState] = useState<"idle" | "sending" | "sent" | string>("idle");
  const pick = (v: number) => { if (dur.current == null) dur.current = (performance.now() - t0.current) / 1000; setVal(v); };
  const send = async () => {
    if (val == null || dur.current == null) return;
    setState("sending");
    try {
      const r = await fetch("/api/animo/", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ persona_id: crewId(), valor: val, duracion_respuesta_s: Math.round(dur.current * 100) / 100 }) });
      if (r.ok) { setState("sent"); onSent(); } else setState(r.status === 429 ? "Too soon: one report every 10 seconds." : "Could not save the report.");
    } catch { setState("API offline: nothing was saved."); }
  };
  const dist = ind.distribucion ?? {}, max = Math.max(1, ...Object.values(dist));
  return (
    <aside aria-label={`Receipt for ${name}`} className="absolute right-8 top-0 z-20 w-[22rem]">
      <div className="mx-4 h-[5px] rounded-b bg-black shadow-[0_2px_0_rgb(255_255_255/.06)]" />
      <div className="slot-in relative -mt-px rotate-[0.6deg] bg-paper px-6 pb-6 pt-5 font-mono text-[12px] leading-relaxed text-paper-ink shadow-[0_24px_50px_-12px_rgb(0_0_0/.7)]">
        <button onClick={onClose} aria-label="Close receipt" className="absolute right-4 top-3 text-paper-dim hover:text-paper-ink">×</button>
        <div className="flex items-baseline justify-between border-b border-dashed border-paper-dim/50 pb-3">
          <span className="font-display text-[1.7rem] leading-none">{name}</span><span className="text-[10px] uppercase tracking-[0.18em] text-paper-dim">3 touches</span>
        </div>
        {state === "sent" ? (
          <p className="mt-4 text-[12px]"><b>Saved.</b> Your answer is one real data point in a self-report channel. It carries no name and no free text; only the value and how long you took.</p>
        ) : (
          <>
            <p className="mt-4 font-display text-[1.25rem] leading-snug">How do you feel right now?</p>
            <div className="mt-3 grid grid-cols-5 gap-1.5" role="radiogroup" aria-label="Mood, 1 to 5">
              {MOODS.map((m, i) => (
                <button key={m} role="radio" aria-checked={val === i + 1} onClick={() => pick(i + 1)} title={m}
                  className={`border py-2 text-[13px] transition-colors ${val === i + 1 ? "border-paper-ink bg-paper-ink text-paper" : "border-paper-dim/60 hover:border-paper-ink"}`}>{i + 1}</button>
              ))}
            </div>
            <p className="mt-1 flex justify-between text-[9.5px] uppercase tracking-[0.1em] text-paper-dim"><span>very low</span><span>very good</span></p>
            <button onClick={send} disabled={val == null || state === "sending"} className="mt-4 w-full border border-paper-ink py-2 text-[11px] uppercase tracking-[0.2em] transition-colors enabled:hover:bg-paper-ink enabled:hover:text-paper disabled:opacity-35">
              {state === "sending" ? "Sending…" : "Send"}
            </button>
            {state !== "idle" && state !== "sending" && <p role="alert" className="mt-2 text-[11px] font-medium text-[#c2410c]">{state}</p>}
          </>
        )}
        <div className="mt-5 border-t border-dashed border-paper-dim/50 pt-3">
          <p className="text-[10px] uppercase tracking-[0.14em] text-paper-dim">{ind.reportes ?? 0} reports so far{ind.duracion_mediana_s != null ? ` · median answer ${ind.duracion_mediana_s} s` : ""}</p>
          <div className="mt-2 flex h-8 items-end gap-1.5">
            {[1, 2, 3, 4, 5].map((k) => <span key={k} className="flex-1 bg-paper-ink/70" style={{ height: `${Math.max(((dist[String(k)] ?? 0) / max) * 100, 4)}%` }} title={`${k}: ${dist[String(k)] ?? 0}`} />)}
          </div>
          <p className="mt-2 text-[10.5px] text-paper-dim">No detector yet: a self-report has no colour of its own, so this dot stays neutral.</p>
        </div>
        <div className="mt-4 flex items-center justify-between"><span className="text-[10px] uppercase tracking-[0.14em] text-paper-dim">DC-02 · self-reported · not astronauts</span><Stamp banner="REAL" /></div>
      </div>
    </aside>
  );
}
