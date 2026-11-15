"use client";
import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
import { AlmaDock, useAlma } from "@/components/Alma";
import { DayTicks } from "@/components/DayTicks";
import { IndicatorSlip, Receipt } from "@/components/Receipt";
import { useShip } from "@/components/Ship";
import { BUDGETS, get, INDICATOR_NAMES, type CrewMember, type CrewPayload, type Indicator, type LedgerDay, type LedgerDays } from "@/lib/api";

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
      <SuitScene ledger={ledger} picked={picked} onPick={pickRing} mode={mode} indicators={indsCrew} pickedInd={pickedInd} onPickInd={pickInd} onTapSuit={() => { const k = outfit === "eva" ? "suit" : who ? `crew-${who.indicativo}` : "suit"; if (has(k)) say(k, true); }}
        outfit={outfit} look={who ?? FALLBACK} holo={holo} layer={layer} helmet={helmet} />
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
            <button key={m} role="tab" aria-selected={outfit === m} onClick={() => setOutfit(m)} className={`border-b pb-0.5 transition-colors ${outfit === m ? "border-ink text-ink" : "border-transparent text-ink-faint hover:text-ink-dim"}`}>{t}</button>
          ))}
        </div>
        {outfit === "eva" && (
          <div className="mt-3 flex gap-4 font-mono text-[10px] uppercase tracking-[0.2em]" role="tablist" aria-label="Helmet">
            {([[true, "Helmet on"], [false, "Helmet off"]] as const).map(([m, t]) => (
              <button key={t} role="tab" aria-selected={helmet === m} onClick={() => setHelmet(m)} className={`border-b pb-0.5 transition-colors ${helmet === m ? "border-ink text-ink" : "border-transparent text-ink-faint hover:text-ink-dim"}`}>{t}</button>
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
        <div className="mt-3 flex gap-4 font-mono text-[10px] uppercase tracking-[0.2em]" role="tablist" aria-label="Display">
          {([[true, "Hologram"], [false, "Solid"]] as const).map(([m, t]) => (
            <button key={t} role="tab" aria-selected={holo === m} onClick={() => setHolo(m)} className={`border-b pb-0.5 transition-colors ${holo === m ? "border-ink text-ink" : "border-transparent text-ink-faint hover:text-ink-dim"}`}>{t}</button>
          ))}
        </div>
        <p className="mt-3 font-mono text-[9.5px] uppercase leading-relaxed tracking-[0.16em] text-ink-faint">
          {outfit === "eva" ? "NASA Z-2 prototype suit · NASA 3D Resources" : "Generated fictional character"}<br />not a real person · body states = stand-in<br /><span className="text-ink-dim">Drag to rotate · scroll or pinch to zoom · tap to hear ALMA</span>
        </p>
      </nav>
      {mode === "body" && pickedInd && <IndicatorSlip crewName={who?.indicativo} ind={indsCrew.find((i) => i.indicador === pickedInd)} name={INDICATOR_NAMES[pickedInd]} onClose={() => setPickedInd(null)} onSent={() => get<{ indicadores: Indicator[] }>("/api/indicadores/").then((d) => setInds(d?.indicadores ?? []))} />}
      {mode === "books" && picked && ledger && <Receipt line={line} label={label} day={ledger.dia_habitat} banner={ledger.banner} onClose={() => setPicked(null)} />}
      {mode === "books" && day != null && <DayTicks days={days} day={day} open={open} onPick={setDay} />}
      <AlmaDock room={mode === "body" ? "indicadores" : day != null ? `libro-${day}` : undefined} />
    </div>
  );
}
