"use client";
import { useEffect, useMemo, useState } from "react";
import { Room } from "@/components/Room";
import { Stamp } from "@/components/Stamp";
import { BUDGETS, get, type AlarmasApi, type EProcess, type VerdesApi, type ResidualPoint, type Residuals } from "@/lib/api";

const W = 1000, H = 170, MID = H / 2, PX = 20, CLAMP = 3.8; // 20 px por σ; la cinta cubre ±3,8σ
const H_CUSUM = 10.01;
const label = (id: string) => BUDGETS.find(([b]) => b === id)?.[1] ?? id;

/** 02 · MACHINE ROOM — «What did the engine see?» Lo prometido (el manifiesto) frente a lo observado: dos cintas de sismógrafo. */
export default function MachineRoom() {
  const [r, setR] = useState<Residuals | null>(null);
  const [ep, setEp] = useState<EProcess | null>(null);
  const [al, setAl] = useState<AlarmasApi | null>(null);
  const [vd, setVd] = useState<VerdesApi | null>(null);
  useEffect(() => { get<AlarmasApi>("/api/alarmas/").then(setAl); get<VerdesApi>("/api/verdes/").then(setVd); }, []);
  useEffect(() => { get<EProcess>("/api/eproceso/").then(setEp); }, []);
  const [pick, setPick] = useState<{ id: string; i: number } | null>(null);
  useEffect(() => {
    get<Residuals>("/api/residuo/?limite=500").then((d) => {
      setR(d);
      const q = new URLSearchParams(window.location.search).get("pick");           // ?pick=aire:10 → enlace profundo (capturas)
      if (q) { const [id, i] = q.split(":"); setTimeout(() => setPick({ id, i: Number(i) }), 400); }
    });
  }, []);
  const tapes = useMemo(() => {
    const by: Record<string, ResidualPoint[]> = {};
    r?.habitat.forEach((p) => (by[p.presupuesto_id] ??= []).push(p));
    const order = (id: string) => BUDGETS.findIndex(([b]) => b === id);
    return Object.entries(by).sort(([a], [b]) => order(a) - order(b)).map(([id, pts]) => [id, pts.sort((a, b) => a.ts_utc.localeCompare(b.ts_utc))] as const);
  }, [r]);
  const sel = pick ? tapes.find(([id]) => id === pick.id)?.[1][pick.i] : undefined;
  return (
    <Room voice="residuo" scroll hero="machine" heroFocus="50% 35%">
      <div className="mx-auto max-w-6xl px-10 pt-10">
        <h1 className="font-display text-5xl leading-tight">What was promised.<br /><span className="text-ink-dim">What was observed.</span></h1>
        <p className="mt-4 max-w-2xl text-ink-dim">Each tape is one book. The straight line is the manifest&apos;s promise; the shaded lane is two sigma of its own uncertainty. Where the trace leaves the lane, the gap lights up.</p>
        {r && !tapes.length && <p className="mt-10 font-mono text-xs uppercase tracking-widest text-ink-faint">No residual stream loaded. The absence is data; nothing is drawn.</p>}
        <div className="mt-10 space-y-9">
          {tapes.map(([id, pts]) => (
            <section key={id}>
              <div className="mb-2 flex items-baseline gap-4">
                <h2 className="font-display text-3xl">{label(id)}</h2>
                <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink-faint">{pts.length} days · residual in σ of the manifest</span>
              </div>
              <Tape pts={pts} sel={pick?.id === id ? pick.i : -1} onPick={(i) => setPick({ id, i })} />
            </section>
          ))}
        </div>
        {al && vd && <ReceiptsCard al={al} vd={vd} />}
        {ep && <EProcessCard ep={ep} />}
        {sel && pick && <Slip p={sel} day={pick.i + 1} name={label(pick.id)} onClose={() => setPick(null)} />}
      </div>
    </Room>
  );
}

function Tape({ pts, sel, onPick }: { pts: ResidualPoint[]; sel: number; onPick: (i: number) => void }) {
  const x = (i: number) => 30 + (i / Math.max(pts.length - 1, 1)) * (W - 60);
  const zs = pts.map((p) => Math.max(-CLAMP, Math.min(CLAMP, p.residuo / p.sigma_efectiva)));
  const y = (z: number) => MID - z * PX;
  const path = pts.map((_, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${y(zs[i]).toFixed(1)}`).join(" ");
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="Observed versus promised residual tape">
      <rect x="0" y={y(2)} width={W} height={4 * PX} fill="var(--color-ink)" opacity="0.045" />
      <line x1="0" x2={W} y1={y(2)} y2={y(2)} stroke="var(--color-ink)" strokeOpacity=".22" strokeDasharray="3 5" />
      <line x1="0" x2={W} y1={y(-2)} y2={y(-2)} stroke="var(--color-ink)" strokeOpacity=".22" strokeDasharray="3 5" />
      <line x1="0" x2={W} y1={MID} y2={MID} stroke="var(--color-ink)" strokeOpacity=".7" strokeWidth="1" />
      <text x="4" y={y(2) - 5} fill="var(--color-ink-faint)" fontSize="9" letterSpacing="2" fontFamily="var(--font-mono)">+2σ</text>
      <text x="4" y={y(-2) + 13} fill="var(--color-ink-faint)" fontSize="9" letterSpacing="2" fontFamily="var(--font-mono)">−2σ</text>
      {pts.map((p, i) => Math.abs(zs[i]) > 2 && <rect key={`g${i}`} x={x(i) - 3} width="6" y={Math.min(y(0), y(zs[i]))} height={Math.abs(y(zs[i]) - y(0))} fill="var(--color-signal)" opacity=".5" />)}
      <path d={path} fill="none" stroke="var(--color-ink)" strokeWidth="1.8" strokeLinejoin="round" />
      {pts.map((p, i) => {
        const flag = p.bandera !== "normal";
        return (
          <g key={i} onClick={() => onPick(i)} className="cursor-pointer">
            <circle cx={x(i)} cy={y(zs[i])} r="14" fill="transparent" />
            {flag ? <rect x={x(i) - 5} y={y(zs[i]) - 5} width="10" height="10" transform={`rotate(45 ${x(i)} ${y(zs[i])})`} fill="var(--color-signal)" />
                  : <circle cx={x(i)} cy={y(zs[i])} r={sel === i ? 4.5 : 2.6} fill={sel === i ? "var(--color-ink)" : "var(--color-bg)"} stroke="var(--color-ink)" strokeWidth="1.2" />}
            {flag && <text x={x(i) + 12} y={y(zs[i]) - 8} fill="var(--color-signal)" fontSize="10" letterSpacing="2" fontFamily="var(--font-mono)">SURPRISE · DAY {i + 1}</text>}
            <text x={x(i)} y={H - 4} textAnchor="middle" fill="var(--color-ink-faint)" fontSize="9" fontFamily="var(--font-mono)">{i + 1}</text>
          </g>
        );
      })}
    </svg>
  );
}

/** Recibo de una lectura: nivel 2 de profundidad. Una bandera de sorpresa NO es una alarma: aún no tiene regla preregistrada con recibo. */
function Slip({ p, day, name, onClose }: { p: ResidualPoint; day: number; name: string; onClose: () => void }) {
  const z = p.residuo / p.sigma_efectiva;
  return (
    <aside className="slot-in fixed right-8 top-16 z-30 w-[22rem] rotate-[0.5deg] bg-paper px-6 pb-6 pt-5 font-mono text-[12px] leading-relaxed text-paper-ink shadow-[0_24px_50px_-12px_rgb(0_0_0/.7)]">
      <button onClick={onClose} aria-label="Close receipt" className="absolute right-4 top-3 text-paper-dim hover:text-paper-ink">×</button>
      <div className="flex items-baseline justify-between border-b border-dashed border-paper-dim/50 pb-3">
        <span className="font-display text-[1.7rem] leading-none">{name}</span><span className="text-[10px] uppercase tracking-[0.18em] text-paper-dim">Day {day} · {p.ts_utc.slice(0, 10)}</span>
      </div>
      <dl className="mt-4 space-y-1.5">
        {([["promised", `${p.predicho.toFixed(3)} kg`], ["observed", `${p.observado.toFixed(3)} kg`], ["residual", `${p.residuo >= 0 ? "+" : "−"}${Math.abs(p.residuo).toFixed(3)} kg`],
          ["σ of manifest", `${p.sigma_efectiva.toFixed(3)} kg`], ["distance", `${Math.abs(z).toFixed(2)} σ`], ["CUSUM", `${Math.abs(p.cusum_acumulado).toFixed(2)} / ${H_CUSUM}`]] as const).map(([k, v]) => (
          <div key={k} className="flex justify-between gap-4"><dt className="text-paper-dim">{k}</dt><dd>{v}</dd></div>))}
      </dl>
      <p className="mt-4 border-t border-dashed border-paper-dim/50 pt-3 text-[11px]"><span className="uppercase tracking-[0.14em] text-paper-dim">rule </span>surprise ⇔ |residual| &gt; 2σ · drift ⇔ CUSUM ≥ {H_CUSUM}</p>
      <p className="mt-2 text-[11px] font-medium">→ {p.bandera === "normal" ? "NORMAL: inside the lane." : p.bandera === "sorpresa" ? "SURPRISE: a flag, not yet an alarm." : "DRIFT."}</p>
      <div className="mt-5 flex items-center justify-between"><span className="text-[10px] uppercase tracking-[0.14em] text-paper-dim">source · /api/residuo · DC-06</span><Stamp banner={p.banner} /></div>
    </aside>
  );
}

/** M6.1 · Una alarma con garantía matemática… y lo que midió la realidad. La curva es DEMOSTRATIVA (simulada); la tabla es de datos reales (LifeSnaps, no astronautas). */
function EProcessCard({ ep }: { ep: EProcess }) {
  const W2 = 700, H2 = 150, L = 34, n = ep.curva.length, X = (i: number) => L + (i / Math.max(n - 1, 1)) * (W2 - L - 14), Y = (m: number) => H2 - 22 - (Math.max(0, Math.min(2.3, Math.log10(Math.max(m, 1)))) / 2.3) * (H2 - 34);
  return (
    <section className="mt-16 max-w-4xl pb-16" data-testid="eprocess-card">
      <div className="flex items-baseline gap-4"><h2 className="font-display text-3xl">An alarm with a guarantee</h2><Stamp banner={ep.banner} /></div>
      <p className="mt-3 max-w-2xl text-ink-dim">Watch the evidence pile up. When it crosses {ep.umbral}, the alarm may fire — and the maths says a false alarm happens at most {Math.round(ep.alfa * 100)}% of the time, <em>if</em> the assumptions hold. This curve is a simulation: four quiet days, then a 3.2σ shift.</p>
      <svg viewBox={`0 0 ${W2} ${H2}`} className="mt-5 w-full" role="img" aria-label="Evidence process crossing the alarm threshold">
        <line x1={L} x2={W2 - 14} y1={Y(ep.umbral)} y2={Y(ep.umbral)} stroke="var(--color-signal)" strokeDasharray="4 5" /><text x={L + 4} y={Y(ep.umbral) - 5} fill="var(--color-signal)" fontSize="10" fontFamily="var(--font-mono)">ALARM · evidence ≥ {ep.umbral}</text>
        <line x1={L} x2={W2 - 14} y1={Y(1)} y2={Y(1)} stroke="var(--color-ink)" strokeOpacity=".4" /><text x={L - 6} y={Y(1) + 3} textAnchor="end" fill="var(--color-ink-faint)" fontSize="9" fontFamily="var(--font-mono)">1</text>
        <line x1={X(ep.escalon_dia - 1)} x2={X(ep.escalon_dia - 1)} y1={10} y2={H2 - 22} stroke="var(--color-ink)" strokeOpacity=".25" strokeDasharray="2 4" /><text x={X(ep.escalon_dia - 1) + 4} y={20} fill="var(--color-ink-faint)" fontSize="9" fontFamily="var(--font-mono)">change begins</text>
        <polyline fill="none" stroke="var(--color-ink)" strokeWidth="2" points={ep.curva.map((m, i) => `${X(i)},${Y(m)}`).join(" ")} />
        {ep.curva.map((m, i) => <circle key={i} cx={X(i)} cy={Y(m)} r={m >= ep.umbral ? 4 : 2.4} fill={m >= ep.umbral ? "var(--color-signal)" : "var(--color-ink)"} />)}
        {ep.curva.map((_, i) => <text key={i} x={X(i)} y={H2 - 6} textAnchor="middle" fill="var(--color-ink-faint)" fontSize="9" fontFamily="var(--font-mono)">{i + 1}</text>)}
      </svg>
      {ep.ejecutada && ep.entrenamiento && (
        <div className="mt-6 bg-paper px-6 py-5 font-mono text-[12px] text-paper-ink shadow-[0_24px_50px_-14px_rgb(0_0_0/.8)]">
          <p className="font-display text-2xl">What reality said</p>
          <p className="mt-1 text-[11px] text-paper-dim">Real wearable data, everyday people, not astronauts · sealed record {ep.hash_acta?.slice(0, 8)}…</p>
          <table className="mt-3 w-full text-right"><thead><tr className="text-left text-[10px] uppercase tracking-[0.14em] text-paper-dim"><th className="font-normal">safety margin (s)</th><th className="text-right font-normal">false alarms (asked ≤1%)</th><th className="text-right font-normal">sensitivity at 2σ</th></tr></thead>
            <tbody>{Object.entries(ep.entrenamiento).map(([s, v]) => (
              <tr key={s} className={`border-t border-paper-dim/30 ${ep.s === Number(s) ? "font-medium" : ""}`}><td className="py-1.5 text-left">{s}{ep.s === Number(s) ? " · chosen" : ""}</td><td className={v.fpr_entrenamiento > 0.011 ? "text-[#c2410c]" : ""}>{(100 * v.fpr_entrenamiento).toFixed(2)}% ({v.k}/{v.n})</td><td>{Math.round(100 * v.potencia_h2)}%</td></tr>))}</tbody></table>
          <p className="mt-3 border-t border-paper-ink/60 pt-3 text-[11px]">Taken at face value (s = 1) the guarantee failed fivefold on real data. Widening it until it holds costs sensitivity (99% → 71%). The out-of-sample check had only 5 windows: inconclusive. The method is not ours; the measured gap is.</p>
        </div>
      )}
    </section>
  );
}


/** Recibos: lo que el sistema promete de cada alarma y de cada verde. Solo AGREGADOS (sin ids ni valores personales: los recibos individuales existen en la API). */
function ReceiptsCard({ al, vd }: { al: AlarmasApi; vd: VerdesApi }) {
  const act = al.alarmas.filter((a) => a.estado === "activa");
  const plantilla = (act[0]?.regla_exacta ?? "").replace(/mu=[-\d.e]+/, "mu=‹personal›").replace(/sigma=[-\d.e]+/, "sigma=‹personal›").replace(/ phi=[-\d.e]+/, "").replace(/ x0=[-\d.e]+/, "");
  const v = vd.cuerpo_agregado;
  return (
    <section className="mt-16 max-w-4xl" data-testid="receipts-card">
      <div className="flex items-baseline gap-4"><h2 className="font-display text-3xl">Every colour carries a receipt</h2><Stamp banner={al.banner} /></div>
      <p className="mt-3 max-w-2xl text-ink-dim">The ship never shows an alarm or a green without the exact rule behind it. Here is the count, never the person: these are everyday wearers, not astronauts.</p>
      <div className="mt-6 grid gap-8 md:grid-cols-2">
        <div><p className="font-mono text-[10px] uppercase tracking-[0.2em] text-ink-faint">Active alarms</p><p className="mt-1 font-display text-5xl leading-none">{act.length}<span className="ml-2 font-mono text-[11px] text-ink-faint">each with rule · seed · hash</span></p>
          {plantilla && <p className="mt-3 break-words font-mono text-[11px] leading-relaxed text-ink-dim">{plantilla}</p>}
          <p className="mt-2 font-mono text-[10px] uppercase tracking-[0.14em] text-ink-faint">sealed in act {act[0]?.hash_preregistro.slice(0, 8)}… · seed {act[0]?.semilla}</p></div>
        <div><p className="font-mono text-[10px] uppercase tracking-[0.2em] text-ink-faint">Green receipts</p><p className="mt-1 font-display text-5xl leading-none">{v.por_estado.verde ?? 0}<span className="ml-2 font-mono text-[11px] text-ink-faint">of {v.recibos}</span></p>
          <p className="mt-3 text-[13px] leading-snug text-ink-dim">A green says how small a change it could have seen — here {v.mde_sigma_mediana.toFixed(2)}σ at the median — and how many days stood behind it (average coverage {Math.round(100 * v.cobertura_media)}%). {v.por_estado.sin_datos_suficientes ?? 0} receipts say <em>not enough data</em> instead: absence is its own state.</p></div>
      </div>
    </section>
  );
}
