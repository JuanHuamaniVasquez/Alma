"use client";
import { useEffect, useRef, useState } from "react";
import { get } from "@/lib/api";
import { Stamp } from "./Stamp";

type Ecg = { banner: "REAL" | "SIMULADO"; fuente: string; doi: string; licencia: string; aviso: string; fs_envio: number; duracion_s: number; latidos_s: number[];
  base: { media: number; sd: number; ventana_s: number }; tendencia: { t: number; lpm: number; rmssd: number; z: number; bandera: string }[];
  calidad: { referencia: number; detectados: number; sensibilidad: number; ppv: number }; regla: string };
type Win = { t0: number; fs_envio: number; y: number[] };
type Expected = { nota: string; items: { indicador: string | null; titulo: string; n: string; en_vuelo: string; referencia: string; lectura: string; fuente: string; doi: string | null; url: string }[] };
type Link = { fuente: string; url: string; retardo_min: [number, number]; retardo_cita: string; interrupciones_cita: string; banner: "REAL" | "SIMULADO"; paquete: { alarmas_activas_con_recibo: number; recibos_de_verde: number; contenido: string } };
const WIN = 20;

/** M6.9 · Monitor de constantes (estilo cabecera de la ISS del reto) con un ECG REAL en reproducción a tiempo real. Pulso y variabilidad salen de NUESTRO detector sobre esa señal. */
export function VitalsMonitor({ onClose }: { onClose: () => void }) {
  const [ecg, setEcg] = useState<Ecg | null>(null);
  const [win, setWin] = useState<Win | null>(null);
  const [tab, setTab] = useState<"live" | "expected" | "link">("live");
  const [exp, setExp] = useState<Expected | null>(null);
  const [link, setLink] = useState<Link | null>(null);
  const [online, setOnline] = useState(true);
  const [delay, setDelay] = useState(12);
  const [now, setNow] = useState(300);                       // segundo de reproducción (arranca tras la línea base de 5 min)
  const cv = useRef<HTMLCanvasElement>(null);
  const t0 = useRef<{ wall: number; pos: number }>({ wall: 0, pos: 300 });
  useEffect(() => { get<Ecg>("/api/ecg/").then(setEcg); get<Expected>("/api/esperado/").then(setExp); get<Link>("/api/enlace/").then(setLink); }, []);
  useEffect(() => { t0.current = { wall: performance.now(), pos: now }; /* eslint-disable-next-line */ }, [win?.t0]);
  const wstart = Math.floor(now / WIN) * WIN;
  useEffect(() => { get<Win>(`/api/ecg/?t=${wstart}&dur=${WIN}`).then(setWin); }, [wstart]);
  useEffect(() => {                                           // reloj de reproducción
    const id = setInterval(() => setNow((n) => { const nx = n + 0.1; return nx >= (ecg?.duracion_s ?? 1800) - 1 ? 300 : nx; }), 100);
    return () => clearInterval(id);
  }, [ecg]);
  useEffect(() => {                                           // dibujo: la señal pasa de derecha a izquierda; 8 s visibles
    const c = cv.current; if (!c || !win || !ecg) return;
    const ctx = c.getContext("2d"); if (!ctx) return;
    const W = c.width, H = c.height, vis = 8, fs = win.fs_envio;
    ctx.clearRect(0, 0, W, H);
    ctx.strokeStyle = "rgba(239,232,218,.07)"; ctx.lineWidth = 1;
    for (let s = 0; s <= vis; s++) { ctx.beginPath(); ctx.moveTo((s / vis) * W, 0); ctx.lineTo((s / vis) * W, H); ctx.stroke(); }
    ctx.strokeStyle = "#efe8da"; ctx.lineWidth = 1.6; ctx.beginPath();
    let first = true;
    for (let k = 0; k < W; k++) {
      const ts = now - vis + (k / W) * vis, i = Math.round((ts - win.t0) * fs);
      if (i < 0 || i >= win.y.length) { first = true; continue; }
      const y = H / 2 - win.y[i] * (H * 0.34);
      if (first) { ctx.moveTo(k, y); first = false; } else ctx.lineTo(k, y);
    }
    ctx.stroke();
    ctx.fillStyle = "#ffb45c";                                // marcas de las ondas R que detectó nuestro algoritmo
    for (const b of ecg.latidos_s) { if (b > now - vis && b <= now) { const k = ((b - (now - vis)) / vis) * W, i = Math.round((b - win.t0) * fs); if (i >= 0 && i < win.y.length) { ctx.beginPath(); ctx.arc(k, H / 2 - win.y[i] * (H * 0.34) - 9, 2.6, 0, 7); ctx.fill(); } } }
  }, [now, win, ecg]);
  if (!ecg) return null;
  const cur = [...ecg.tendencia].reverse().find((d) => d.t <= now) ?? ecg.tendencia[0];
  const flags = ecg.tendencia.filter((d) => d.bandera === "sorpresa");
  const TW = 340, TH = 64, lo = Math.min(...ecg.tendencia.map((d) => d.lpm)) - 4, hi = Math.max(...ecg.tendencia.map((d) => d.lpm)) + 4;
  const tx = (t: number) => (t / ecg.duracion_s) * TW, ty = (v: number) => TH - ((v - lo) / (hi - lo)) * TH;
  return (
    <aside className="slot-in fixed right-6 top-16 z-30 w-[26rem] max-w-[92vw] border border-ink-faint/30 bg-[#0f0d0b]/95 p-4 font-mono text-ink backdrop-blur" aria-label="Vitals monitor" data-testid="vitals-monitor">
      <div className="flex items-center justify-between"><span className="text-[10px] uppercase tracking-[0.2em] text-ink-faint">Vitals monitor · ECG lead II</span><button onClick={onClose} aria-label="Close monitor" className="text-ink-faint hover:text-ink">×</button></div>
      <div className="mt-2 flex gap-4 text-[10px] uppercase tracking-[0.18em]" role="tablist" aria-label="Monitor views">
        {([["live", "Live"], ["expected", "Expected in flight"], ["link", "Earth link"]] as const).map(([k, t]) => (
          <button key={k} role="tab" aria-selected={tab === k} onClick={() => setTab(k)} className={`border-b pb-0.5 ${tab === k ? "border-ink text-ink" : "border-transparent text-ink-faint hover:text-ink-dim"}`}>{t}</button>))}
      </div>
      {tab === "expected" && exp && (
        <div className="mt-3 space-y-3" data-testid="expected-tab">
          {exp.items.map((it) => (
            <div key={it.titulo} className="border-t border-ink-faint/25 pt-2 normal-case tracking-normal">
              <p className="font-display text-xl">{it.titulo}</p>
              <p className="mt-0.5 text-[11px] leading-snug text-ink">{it.en_vuelo}.</p>
              <p className="mt-0.5 text-[10px] leading-snug text-ink-dim">{it.referencia}. {it.lectura}</p>
              <p className="mt-0.5 text-[9px] text-ink-faint">{it.n} · {it.fuente}{it.doi ? ` · doi:${it.doi}` : ""}</p>
            </div>))}
          <p className="text-[9px] leading-snug text-ink-faint normal-case tracking-normal">Group averages from published studies, not predictions for any person.</p>
        </div>
      )}
      {tab === "link" && link && (
        <div className="mt-3 normal-case tracking-normal" data-testid="link-tab">
          <div className="flex items-center justify-between"><p className="text-[10px] uppercase tracking-[0.18em] text-ink-faint">Link to Earth</p>
            <button onClick={() => setOnline(!online)} aria-pressed={online} className="border border-ink-faint/50 px-3 py-1 text-[10px] uppercase tracking-[0.18em] hover:text-ink" style={{ color: online ? "var(--color-ink-dim)" : "var(--color-signal)" }}>{online ? "connected" : "no contact"}</button></div>
          <label className="mt-3 block text-[10px] uppercase tracking-[0.16em] text-ink-faint">one-way delay · {delay} min (published range {link.retardo_min[0]}–{link.retardo_min[1]} min)
            <input type="range" min={link.retardo_min[0]} max={link.retardo_min[1]} value={delay} onChange={(e) => setDelay(Number(e.target.value))} className="mt-1 w-full accent-[#ffb45c]" aria-label="One-way delay in minutes" /></label>
          <p className="mt-3 text-[12px] leading-snug text-ink">{online ? `A question to ground control is answered after about ${2 * delay} minutes.` : "Ground cannot answer. The Guardian keeps deciding on board."}</p>
          <ul className="mt-2 space-y-1 text-[11px] leading-snug text-ink-dim">
            <li>· Every alarm carries its own receipt: the rule, the seed, the sealed hash. The crew can check it without Earth.</li>
            <li>· {link.paquete.alarmas_activas_con_recibo} active alarms with receipts and {link.paquete.recibos_de_verde} green receipts are {online ? "sent as they happen" : "queued for the next window"} — {link.paquete.contenido}.</li>
            <li>· {online ? "No queue." : "Queue grows until contact returns; disruptions can last days to months."}</li>
          </ul>
          <p className="mt-3 text-[9px] leading-snug text-ink-faint">“{link.retardo_cita}.” — {link.fuente}</p>
        </div>
      )}
      <canvas ref={cv} width={640} height={150} className={`mt-2 w-full bg-black/40 ${tab === "live" ? "" : "hidden"}`} aria-label="Live ECG trace" />
      {tab === "live" && (<>
      <div className="mt-3 grid grid-cols-3 gap-3">
        <div><p className="text-[9px] uppercase tracking-[0.18em] text-ink-faint">pulse</p><p className="font-display text-4xl leading-none" style={{ color: cur.bandera === "sorpresa" ? "var(--color-signal)" : undefined }}>{Math.round(cur.lpm)}<span className="ml-1 text-[10px] text-ink-faint">bpm</span></p></div>
        <div><p className="text-[9px] uppercase tracking-[0.18em] text-ink-faint">HRV · RMSSD</p><p className="font-display text-4xl leading-none">{Math.round(cur.rmssd)}<span className="ml-1 text-[10px] text-ink-faint">ms</span></p></div>
        <div><p className="text-[9px] uppercase tracking-[0.18em] text-ink-faint">state</p><p className="mt-1 text-[12px] uppercase tracking-[0.12em]" style={{ color: cur.bandera === "sorpresa" ? "var(--color-signal)" : "var(--color-ink-dim)" }}>{cur.bandera === "sorpresa" ? "surprise" : "inside own band"}</p></div>
      </div>
      <svg viewBox={`0 0 ${TW} ${TH}`} className="mt-3 w-full" role="img" aria-label="Pulse trend with personal baseline band">
        <rect x={tx(0)} width={tx(ecg.base.ventana_s) - tx(0)} y={0} height={TH} fill="#efe8da" opacity="0.06" />
        <rect x={0} width={TW} y={ty(ecg.base.media + 2 * ecg.base.sd)} height={ty(ecg.base.media - 2 * ecg.base.sd) - ty(ecg.base.media + 2 * ecg.base.sd)} fill="#efe8da" opacity="0.10" />
        <polyline fill="none" stroke="#efe8da" strokeWidth="1" points={ecg.tendencia.map((d) => `${tx(d.t + 5)},${ty(d.lpm)}`).join(" ")} />
        {flags.map((d) => <circle key={d.t} cx={tx(d.t + 5)} cy={ty(d.lpm)} r="1.6" fill="var(--color-signal)" />)}
        <line x1={tx(now)} x2={tx(now)} y1={0} y2={TH} stroke="#ffb45c" strokeWidth="1" />
      </svg>
      <p className="mt-1 text-[9px] uppercase tracking-[0.14em] text-ink-faint">shaded band = ±2σ of this person&apos;s first 5 min (a display rule, not a preregistered test) · {flags.length} of {ecg.tendencia.length} windows flagged</p>
      <div className="mt-3 flex items-start justify-between gap-3 border-t border-ink-faint/25 pt-3"><p className="text-[10px] leading-snug text-ink-dim normal-case tracking-normal">{ecg.aviso} Beat detector vs human annotation: {(100 * ecg.calidad.sensibilidad).toFixed(2)}% found, {(100 * ecg.calidad.ppv).toFixed(2)}% correct (n = {ecg.calidad.referencia}). A flag is a surprise, not an alarm: it has no receipt, no stated power, and its rule was not preregistered. Nothing here is shown green: green is reserved for receipts.</p><Stamp banner={ecg.banner} /></div>
      <p className="mt-2 text-[9px] text-ink-faint">{ecg.fuente} · doi:{ecg.doi} · {ecg.licencia}</p>
      </>)}
    </aside>
  );
}
