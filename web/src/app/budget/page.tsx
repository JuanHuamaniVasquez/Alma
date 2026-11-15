"use client";
import { useEffect, useState } from "react";
import { DayTicks } from "@/components/DayTicks";
import { Room } from "@/components/Room";
import { useShip } from "@/components/Ship";
import { Stamp } from "@/components/Stamp";
import { BUDGETS, get, type LedgerDay, type LedgerDays } from "@/lib/api";

/** 07 · THE BUDGET — «Do the ship's books close?» Cuentas, nunca gráficas de personas. Un libro sin datos reales de ancla NO se simula: se muestra vacío. */
export default function Budget() {
  const { day, setDay } = useShip();
  const [days, setDays] = useState<number[]>([]);
  const [open, setOpen] = useState<Set<number>>(new Set());
  const [ledger, setLedger] = useState<LedgerDay | null>(null);
  useEffect(() => {
    get<LedgerDays>("/api/libro/dias/").then(async (d) => {
      if (!d || d.ultimo == null) return;
      setDays(d.dias); setDay(day ?? d.ultimo);
      const all = await Promise.all(d.dias.map((n) => get<LedgerDay>(`/api/libro/dia/${n}/`)));
      setOpen(new Set(all.filter((x): x is LedgerDay => !!x && !x.cierra).map((x) => x.dia_habitat)));
    });
  }, []); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { if (day != null) get<LedgerDay>(`/api/libro/dia/${day}/`).then(setLedger); }, [day]);
  const rows = BUDGETS.map(([id, name]) => ({ id, name, line: ledger?.habitat.find((h) => h.presupuesto_id === id) }));
  const nOpen = ledger ? Object.values(ledger.presupuestos).filter((p) => !p.cierra).length : 0, nBooks = ledger ? Object.keys(ledger.presupuestos).length : 0;
  return (
    <Room voice={day != null ? `libro-${day}` : undefined} scroll>
      <div className="mx-auto max-w-5xl px-10 pt-10">
        <h1 className="font-display text-5xl leading-tight">Do the ship&apos;s books close?</h1>
        <p className="mt-3 max-w-2xl text-ink-dim">Nine books, one rule: what comes in, minus what goes out, minus what is stored, must equal what was declared lost — within the manifest&apos;s own uncertainty. Where no real anchor exists, the book stays empty.</p>
        <div className="mt-9 bg-paper px-8 pb-7 pt-6 font-mono text-[12.5px] text-paper-ink shadow-[0_24px_50px_-14px_rgb(0_0_0/.8)]">
          <div className="flex items-baseline justify-between border-b border-paper-ink/60 pb-3">
            <span className="font-display text-3xl">Ledger · day {day ?? "—"}</span>
            {ledger && <Stamp banner={ledger.banner} />}
          </div>
          <table className="mt-3 w-full">
            <thead><tr className="text-left text-[10px] uppercase tracking-[0.16em] text-paper-dim">
              {["book", "expected", "observed", "residual", "blind below (2σ)", ""].map((h, i) => <th key={i} className={`pb-2 font-normal ${i > 0 ? "text-right" : ""}`}>{h}</th>)}
            </tr></thead>
            <tbody>
              {rows.map(({ id, name, line }) => (
                <tr key={id} className="border-t border-paper-dim/30 align-baseline">
                  <td className="py-2.5 font-display text-[1.35rem]">{name}</td>
                  {line ? (<>
                    <td className="text-right">{line.emision_esperada.toFixed(3)}</td><td className="text-right">{line.emision_observada.toFixed(3)}</td>
                    <td className={`text-right ${line.cierra ? "" : "font-medium"}`}>{line.residuo_contable >= 0 ? "+" : "−"}{Math.abs(line.residuo_contable).toFixed(3)}</td>
                    <td className="text-right">{(2 * line.incertidumbre_del_manifiesto).toFixed(3)} kg</td>
                    <td className={`pl-5 text-right text-[11px] uppercase tracking-[0.14em] ${line.cierra ? "" : "font-medium text-[#c2410c]"}`}>{line.cierra ? "closes" : "does not close"}</td>
                  </>) : <td colSpan={5} className="py-2.5 text-right text-[11px] uppercase tracking-[0.14em] text-paper-dim">no ledger · no public anchor yet · nothing simulated</td>}
                </tr>
              ))}
            </tbody>
          </table>
          <p className="mt-4 border-t border-paper-ink/60 pt-3 text-[11px]">{ledger ? `${nBooks} of 9 books exist; ${nOpen} do not close. “Blind below” is the smallest imbalance the manifest could ever notice — below it, a green means nothing.` : "No ledger loaded."}</p>
        </div>
      </div>
      {days.length > 0 && day != null && <DayTicks days={days} day={day} open={open} onPick={setDay} />}
    </Room>
  );
}
