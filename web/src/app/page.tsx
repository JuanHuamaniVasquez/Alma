"use client";
import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
import { AlmaDock, useAlma } from "@/components/Alma";
import { Receipt } from "@/components/Receipt";
import { BUDGETS, get, type LedgerDay, type LedgerDays } from "@/lib/api";

const SuitScene = dynamic(() => import("@/components/SuitScene"), { ssr: false });

/** 01 · MEDICAL MODULE — «How am I, really?» La nave se ve calma; el abismo está al clic. */
export default function MedicalModule() {
  const [ledger, setLedger] = useState<LedgerDay | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [picked, setPicked] = useState<string | null>(null);
  const { say, has } = useAlma();

  useEffect(() => {
    get<LedgerDays>("/api/libro/dias/").then(async (d) => {
      if (d?.ultimo != null) setLedger(await get<LedgerDay>(`/api/libro/dia/${d.ultimo}/`));
      setLoaded(true);
    });
  }, []);
  useEffect(() => { if (loaded && has("libro")) say("libro"); }, [loaded]); // eslint-disable-line react-hooks/exhaustive-deps

  const label = BUDGETS.find(([id]) => id === picked)?.[1] ?? "";
  const line = ledger?.habitat.find((h) => h.presupuesto_id === picked) ?? null;
  return (
    <div className="absolute inset-0" style={{ background: "radial-gradient(60% 70% at 50% 42%, #2a2018 0%, #14110e 55%, #0d0c0b 100%)" }}>
      <SuitScene ledger={ledger} picked={picked} onPick={setPicked} />
      <p className="pointer-events-none absolute left-6 top-6 max-w-xs font-mono text-[10px] uppercase leading-relaxed tracking-[0.2em] text-ink-faint">
        Crew member · NASA Z-2 prototype suit<br />model: NASA 3D Resources · not a real person
      </p>
      {picked && ledger && <Receipt line={line} label={label} day={ledger.dia_habitat} banner={ledger.banner} onClose={() => setPicked(null)} />}
      <AlmaDock room="libro" />
    </div>
  );
}
