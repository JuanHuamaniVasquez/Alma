"use client";
import dynamic from "next/dynamic";
import { VitalsMonitor } from "@/components/VitalsMonitor";
import { useEffect, useState } from "react";
import { AlmaDock, useAlma } from "@/components/Alma";
import { DayTicks } from "@/components/DayTicks";
import { IndicatorSlip, Receipt } from "@/components/Receipt";
import { useShip } from "@/components/Ship";
import { Stamp } from "@/components/Stamp";
import { BUDGETS, get, INDICATOR_NAMES, type CrewMember, type CrewPayload, type Entorno, type Indicator, type LedgerDay, type LedgerDays } from "@/lib/api";

const FALLBACK: CrewMember = { indicativo: "VEGA", rol: "Commander", color: "#d9a441", piel: "#e6b98f", pelo: "#2a1d14", peinado: "short", complexion: 1.04, estado: null };
const SuitScene = dynamic(() => import("@/components/SuitScene"), { ssr: false });

/** 01 · MEDICAL MODULE — «How am I, really?» La nave se ve calma; el abismo está al clic. */
export default function MedicalModule() {
  const [days, setDays] = useState<number[]>([]);
  const { day, setDay } = useShip();
  const [open, setOpen] = useState<Set<number>>(new Set());
  const [ledger, setLedger] = useState<LedgerDay | null>(null);
  const [picked, setPicked] = useState<string | null>(null);
  const [mode, setMode] = useState<"books" | "body">("books");
  const [inds, setInds] = useState<Indicator[]>([]);
  const [pickedInd, setPickedInd] = useState<string | null>(null);
  const [crew, setCrew] = useState<CrewMember[]>([]);
  const [sel, setSel] = useState(0);
  const [outfit, setOutfit] = useState<"iva" | "eva">("iva");
  const [holo, setHolo] = useState(false);
  const [helmet, setHelmet] = useState(true);
  const [monitor, setMonitor] = useState(false);
  const [env, setEnv] = useState<Entorno | null>(null);
  useEffect(() => { const l = () => get<Entorno>("/api/entorno/").then(setEnv); l(); const id = setInterval(l, 30000); return () => clearInterval(id); }, []);
  const [layer, setLayer] = useState<"uniform" | "body" | "anatomy">("uniform");
  const { say, has } = useAlma();

  useEffect(() => {
    get<LedgerDays>("/api/libro/dias/").then(async (d) => {
      if (!d || d.ultimo == null) return;
      const q = new URLSearchParams(window.location.search);   // ?day=11&pick=aire: enlaces profundos (capturas, grabaciones)
      setDays(d.dias); setDay(d.dias.includes(Number(q.get("day"))) ? Number(q.get("day")) : d.ultimo);
      if (q.get("pick")) setTimeout(() => setPicked(q.get("pick")), 400);
      if (q.get("out") === "eva") setOutfit("eva");
      if (q.get("holo") === "1") setHolo(true);
      if (q.get("layer") === "body" || q.get("layer") === "anatomy") setLayer(q.get("layer") as "body" | "anatomy");
      if (q.get("helmet") === "0") setHelmet(false);
      if (q.get("monitor") === "1") setMonitor(true);
      if (q.get("mode") === "body") { setMode("body"); if (q.get("ind")) setTimeout(() => setPickedInd(q.get("ind")), 400); }
      const all = await Promise.all(d.dias.map((n) => get<LedgerDay>(`/api/libro/dia/${n}/`)));
      setOpen(new Set(all.filter((x): x is LedgerDay => !!x && !x.cierra).map((x) => x.dia_habitat)));
    });
  }, []);
  useEffect(() => { get<CrewPayload>("/api/tripulacion/").then((d) => { const t = d?.tripulacion ?? []; setCrew(t); const q = new URLSearchParams(window.location.search).get("crew"); const i = t.findIndex((c) => c.indicativo === q); if (i >= 0) setSel(i); }); }, []);
  useEffect(() => { get<{ indicadores: Indicator[] }>("/api/indicadores/").then((d) => setInds(d?.indicadores ?? [])); }, []);
  useEffect(() => { if (day != null) get<LedgerDay>(`/api/libro/dia/${day}/`).then(setLedger); setPicked(null); }, [day]);
  useEffect(() => { if (mode === "books" && day != null && has(`libro-${day}`)) say(`libro-${day}`); }, [day, mode, has(`libro-${day ?? 0}`)]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { setPicked(null); setPickedInd(null); }, [mode]);                       // al cambiar de modo se cierran los recibos; NO al cargar la voz
  useEffect(() => { if (mode === "body" && has("indicadores")) say("indicadores"); }, [mode, has("indicadores")]); // eslint-disable-line react-hooks/exhaustive-deps

  const who = crew[sel];
  const indsCrew = inds.map((i) => (who?.estado && (i.indicador === "fc" || i.indicador === "sueño") ? { ...i, crew: who.estado[i.indicador as "fc" | "sueño"] as Indicator["crew"] } : i));
  const choose = (i: number) => { setSel(i); setPickedInd(null); const k = `crew-${crew[i].indicativo}`; if (has(k)) say(k, true); };
  const pickRing = (id: string) => {                      // tocar un anillo: recibo + ALMA lo explica (con libro: por día; sin libro: una sola frase)
    setPicked(id);
    const k = ledger?.habitat.some((h) => h.presupuesto_id === id) ? `ring-${id}-${day}` : `ring-${id}`;
    if (has(k)) say(k, true);
  };
  const pickInd = (id: string) => { setPickedInd(id); if (has(`ind-${id}`)) say(`ind-${id}`, true); };
  const label = BUDGETS.find(([id]) => id === picked)?.[1] ?? "";
  const line = ledger?.habitat.find((h) => h.presupuesto_id === picked) ?? null;
  return (
    <div className="absolute inset-0" style={{ background: "radial-gradient(60% 70% at 50% 42%, #2a2018 0%, #14110e 55%, #0d0c0b 100%)" }}>
      <SuitScene env={env} ledger={ledger} picked={picked} onPick={pickRing} mode={mode} indicators={indsCrew} pickedInd={pickedInd} onPickInd={pickInd} onTapSuit={() => { const k = outfit === "eva" ? "suit" : who ? `crew-${who.indicativo}` : "suit"; if (has(k)) say(k, true); }}
        outfit={outfit} look={who ?? FALLBACK} holo={holo} layer={layer} helmet={helmet} />
      {monitor && <VitalsMonitor onClose={() => setMonitor(false)} />}
      {who && <p className="pointer-events-none absolute inset-x-0 top-12 z-10 text-center font-display text-[1.6rem] leading-none" style={{ color: who.color }}>{who.indicativo} <span className="font-mono text-[10px] uppercase tracking-[0.25em] text-ink-faint">· {who.rol} · {outfit === "eva" ? "outside" : "inside"}</span></p>}
      <div role="tablist" aria-label="View" className="absolute left-1/2 top-4 z-20 flex -translate-x-1/2 gap-6 font-mono text-[11px] uppercase tracking-[0.22em]">
        {([["books", "Books"], ["body", "Body"]] as const).map(([m, t]) => (
          <button key={m} role="tab" aria-selected={mode === m} onClick={() => setMode(m)} className={`border-b pb-1 transition-colors ${mode === m ? "border-ink text-ink" : "border-transparent text-ink-faint hover:text-ink-dim"}`}>{t}</button>
        ))}
      </div>
      <nav aria-label="Crew" className="absolute left-6 top-6 z-20 w-56">
        <p className="mb-2 font-mono text-[10px] uppercase tracking-[0.22em] text-ink-faint">Crew of 5 · fictional</p>
        <ul className="space-y-1">
          {crew.map((c, i) => (
            <li key={c.indicativo}>
              <button onClick={() => choose(i)} aria-pressed={i === sel} className={`group flex w-full items-center gap-3 border-l-2 py-1 pl-3 text-left transition-colors ${i === sel ? "bg-ink/[0.06]" : "hover:bg-ink/[0.03]"}`} style={{ borderColor: c.color }}>
                <span className={`font-mono text-[12px] uppercase tracking-[0.18em] ${i === sel ? "text-ink" : "text-ink-dim group-hover:text-ink"}`}>{c.indicativo}</span>
                <span className="font-mono text-[9.5px] uppercase tracking-[0.12em] text-ink-faint">{c.rol}</span>
              </button>
            </li>
          ))}
        </ul>
        <div className="mt-4 flex gap-4 font-mono text-[10px] uppercase tracking-[0.2em]" role="tablist" aria-label="Where">
          {([["iva", "Inside"], ["eva", "Outside"]] as const).map(([m, t]) => (
            <button key={m} role="tab" aria-selected={outfit === m} onClick={() => { setOutfit(m); if (m === "eva" && layer === "body") setLayer("uniform"); }} className={`border-b pb-0.5 transition-colors ${outfit === m ? "border-ink text-ink" : "border-transparent text-ink-faint hover:text-ink-dim"}`}>{t}</button>
          ))}
        </div>
        {outfit === "eva" && (
          <div className="mt-3 flex gap-4 font-mono text-[10px] uppercase tracking-[0.2em]" role="tablist" aria-label="Helmet">
            {([[true, "Helmet on"], [false, "Helmet off"]] as const).map(([m, t]) => (
              <button key={t} role="tab" aria-selected={helmet === m} onClick={() => setHelmet(m)} className={`border-b pb-0.5 transition-colors ${helmet === m ? "border-ink text-ink" : "border-transparent text-ink-faint hover:text-ink-dim"}`}>{t}</button>
            ))}
          </div>
        )}
        {outfit === "eva" && (
          <div className="mt-3 flex gap-4 font-mono text-[10px] uppercase tracking-[0.2em]" role="tablist" aria-label="Outside layer">
            {([["uniform", "Suit"], ["anatomy", "Anatomy"]] as const).map(([m, t]) => (
              <button key={m} role="tab" aria-selected={layer === m} onClick={() => setLayer(m)} className={`border-b pb-0.5 transition-colors ${layer === m ? "border-ink text-ink" : "border-transparent text-ink-faint hover:text-ink-dim"}`}>{t}</button>
            ))}
          </div>
        )}
        {outfit === "iva" && (
          <div className="mt-3 flex gap-4 font-mono text-[10px] uppercase tracking-[0.2em]" role="tablist" aria-label="Layer">
            {([["uniform", "Uniform"], ["body", "Body"], ["anatomy", "Anatomy"]] as const).map(([m, t]) => (
              <button key={m} role="tab" aria-selected={layer === m} onClick={() => setLayer(m)} className={`border-b pb-0.5 transition-colors ${layer === m ? "border-ink text-ink" : "border-transparent text-ink-faint hover:text-ink-dim"}`}>{t}</button>
            ))}
          </div>
        )}
        <button onClick={() => setMonitor(!monitor)} aria-pressed={monitor} className={`mt-3 block border-b pb-0.5 font-mono text-[10px] uppercase tracking-[0.2em] transition-colors ${monitor ? "border-ink text-ink" : "border-transparent text-ink-faint hover:text-ink-dim"}`}>Vitals monitor · real ECG</button>
        <div className="mt-3 flex gap-4 font-mono text-[10px] uppercase tracking-[0.2em]" role="tablist" aria-label="Display">
          {([[true, "Hologram"], [false, "Solid"]] as const).map(([m, t]) => (
            <button key={t} role="tab" aria-selected={holo === m} onClick={() => setHolo(m)} className={`border-b pb-0.5 transition-colors ${holo === m ? "border-ink text-ink" : "border-transparent text-ink-faint hover:text-ink-dim"}`}>{t}</button>
          ))}
        </div>
        <p className="mt-3 font-mono text-[9.5px] uppercase leading-relaxed tracking-[0.16em] text-ink-faint">
          {outfit === "eva" ? "NASA Z-2 prototype suit · NASA 3D Resources" : "Generated fictional character"}<br />not a real person · body states = stand-in<br /><span className="text-ink-dim">{layer === "anatomy" ? "Organ colour = its receipt: green ok · orange alarm · grey no verified sensor. Tap an organ: heart = heart rate · brain = sleep, mood, temperature · pancreas = glucose · arm artery = pressure · " : ""}Drag to rotate · scroll or pinch to zoom · tap to hear ALMA</span>
        </p>
      </nav>
      {mode === "body" && pickedInd && <IndicatorSlip crewName={who?.indicativo} ind={indsCrew.find((i) => i.indicador === pickedInd)} name={INDICATOR_NAMES[pickedInd]} onClose={() => setPickedInd(null)} onSent={() => get<{ indicadores: Indicator[] }>("/api/indicadores/").then((d) => setInds(d?.indicadores ?? []))} />}
      {mode === "books" && picked && !line && (picked === "dosis" || picked === "ritmo") && env && <DriverSlip id={picked} env={env} onClose={() => setPicked(null)} />}
      {mode === "books" && picked && ledger && <Receipt line={line} label={label} day={ledger.dia_habitat} banner={ledger.banner} onClose={() => setPicked(null)} />}
      {mode === "books" && day != null && <DayTicks days={days} day={day} open={open} onPick={setDay} />}
      <AlmaDock room={mode === "body" ? "indicadores" : day != null ? `libro-${day}` : undefined} />
    </div>
  );
}


/** Un anillo con DRIVER real (no es un libro: no se puede cerrar porque nada se declara perdido). */
function DriverSlip({ id, env, onClose }: { id: string; env: Entorno; onClose: () => void }) {
  const dose = id === "dosis";
  return (
    <aside className="slot-in fixed right-8 top-16 z-30 w-[22rem] rotate-[0.5deg] bg-paper px-6 pb-6 pt-5 font-mono text-[12px] leading-relaxed text-paper-ink shadow-[0_24px_50px_-12px_rgb(0_0_0/.7)]" aria-label="Live driver">
      <button onClick={onClose} aria-label="Close" className="absolute right-4 top-3 text-paper-dim hover:text-paper-ink">×</button>
      <p className="border-b border-dashed border-paper-dim/50 pb-3 font-display text-[1.7rem] leading-none">{dose ? "Dose" : "Rhythm"} · live driver</p>
      {dose ? (<>
        <p className="mt-3">Energetic protons at the GOES satellites: <strong>{env.protones.pfu?.toFixed(2)} pfu</strong>. Radiation storm S1 begins at {env.protones.umbral_s1_pfu} pfu: {env.protones.tormenta_s1_o_mas ? "it has begun." : "not now."}</p>
        <p className="mt-2 text-[11px]">Solar X-rays: flare class {env.rayosx.clase ?? "unavailable"}.</p>
      </>) : (<>
        <p className="mt-3">The ISS is {env.iss.a_la_luz ? "in sunlight" : "in Earth's shadow"} at {env.iss.alt_km} km: the crew&apos;s light and dark cycle comes from the orbit itself (about sixteen sunrises a day).</p>
      </>)}
      <p className="mt-3 border-t border-dashed border-paper-dim/50 pt-3 text-[11px]">This is an <em>input</em> from the world, not a balance: a book needs something declared lost to check against, and no public record gives that for a crewed cabin. Real feed, {id === "dosis" ? "NOAA SWPC GOES" : "wheretheiss.at (orbit-derived)"}.</p>
      <div className="mt-4 flex justify-end"><Stamp banner="REAL" /></div>
    </aside>
  );
}
