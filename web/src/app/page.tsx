"use client";
import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
import { AlmaDock, useAlma } from "@/components/Alma";
import { DayTicks } from "@/components/DayTicks";
import { IndicatorSlip, Receipt } from "@/components/Receipt";
import { useShip } from "@/components/Ship";
import { BUDGETS, get, INDICATOR_NAMES, type Indicator, type LedgerDay, type LedgerDays } from "@/lib/api";

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
  const { say, has } = useAlma();

  useEffect(() => {
    get<LedgerDays>("/api/libro/dias/").then(async (d) => {
      if (!d || d.ultimo == null) return;
      const q = new URLSearchParams(window.location.search);   // ?day=11&pick=aire: enlaces profundos (capturas, grabaciones)
      setDays(d.dias); setDay(d.dias.includes(Number(q.get("day"))) ? Number(q.get("day")) : d.ultimo);
      if (q.get("pick")) setTimeout(() => setPicked(q.get("pick")), 400);
      if (q.get("mode") === "body") { setMode("body"); if (q.get("ind")) setTimeout(() => setPickedInd(q.get("ind")), 400); }
      const all = await Promise.all(d.dias.map((n) => get<LedgerDay>(`/api/libro/dia/${n}/`)));
      setOpen(new Set(all.filter((x): x is LedgerDay => !!x && !x.cierra).map((x) => x.dia_habitat)));
    });
  }, []);
  useEffect(() => { get<{ indicadores: Indicator[] }>("/api/indicadores/").then((d) => setInds(d?.indicadores ?? [])); }, []);
  useEffect(() => { if (day != null) get<LedgerDay>(`/api/libro/dia/${day}/`).then(setLedger); setPicked(null); }, [day]);
  useEffect(() => { if (mode === "books" && day != null && has(`libro-${day}`)) say(`libro-${day}`); }, [day, mode, has(`libro-${day ?? 0}`)]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { if (mode === "body" && has("indicadores")) say("indicadores"); setPicked(null); setPickedInd(null); }, [mode, has("indicadores")]); // eslint-disable-line react-hooks/exhaustive-deps

  const label = BUDGETS.find(([id]) => id === picked)?.[1] ?? "";
  const line = ledger?.habitat.find((h) => h.presupuesto_id === picked) ?? null;
  return (
    <div className="absolute inset-0" style={{ background: "radial-gradient(60% 70% at 50% 42%, #2a2018 0%, #14110e 55%, #0d0c0b 100%)" }}>
      <SuitScene ledger={ledger} picked={picked} onPick={setPicked} mode={mode} indicators={inds} pickedInd={pickedInd} onPickInd={setPickedInd} />
      <div role="tablist" aria-label="View" className="absolute left-1/2 top-5 z-20 flex -translate-x-1/2 gap-6 font-mono text-[11px] uppercase tracking-[0.22em]">
        {([["books", "Books"], ["body", "Body"]] as const).map(([m, t]) => (
          <button key={m} role="tab" aria-selected={mode === m} onClick={() => setMode(m)} className={`border-b pb-1 transition-colors ${mode === m ? "border-ink text-ink" : "border-transparent text-ink-faint hover:text-ink-dim"}`}>{t}</button>
        ))}
      </div>
      <p className="pointer-events-none absolute left-6 top-6 max-w-xs font-mono text-[10px] uppercase leading-relaxed tracking-[0.2em] text-ink-faint">
        Crew member · NASA Z-2 prototype suit<br />model: NASA 3D Resources · not a real person
      </p>
      {mode === "body" && pickedInd && <IndicatorSlip ind={inds.find((i) => i.indicador === pickedInd)} name={INDICATOR_NAMES[pickedInd]} onClose={() => setPickedInd(null)} />}
      {mode === "books" && picked && ledger && <Receipt line={line} label={label} day={ledger.dia_habitat} banner={ledger.banner} onClose={() => setPicked(null)} />}
      {mode === "books" && day != null && <DayTicks days={days} day={day} open={open} onPick={setDay} />}
      <AlmaDock room={mode === "body" ? "indicadores" : day != null ? `libro-${day}` : undefined} />
    </div>
  );
}
