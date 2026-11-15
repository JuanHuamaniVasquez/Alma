"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { Room } from "@/components/Room";
import { Stamp } from "@/components/Stamp";
import { get, word, type Fundicion, type Tarjeta } from "@/lib/api";

const COLS = [["en_prueba", "In test"], ["refutada", "Refuted"], ["sostenida", "Sustained"], ["sin_datos", "No data"]] as const;

/** 04 · THE FOUNDRY — «How is an idea born?» Cada tarjeta muestra, de entrada, qué la mataría. Lo que sobrevive se compila en un detector. */
export default function Foundry() {
  const [f, setF] = useState<Fundicion | null>(null);
  useEffect(() => { get<Fundicion>("/api/fundicion/").then(setF); }, []);
  const t = f?.tablero;
  return (
    <Room voice="fundicion" scroll>
      <div className="mx-auto max-w-7xl px-10 pt-10">
        <h1 className="font-display text-5xl leading-tight">Ideas are cheap.<br /><span className="text-ink-dim">Surviving them is the product.</span></h1>
        {t && <p className="mt-5 font-mono text-[11px] uppercase tracking-[0.2em] text-ink-faint">{t.nacidas} born · <span className="text-signal">{t.refutada} refuted</span> · {t.sostenida} sustained · {t.sin_datos} no data · {t.detectores_nuevos} compiled into a detector</p>}
        <div className="mt-3 flex items-center gap-4"><Stamp banner="REAL" /><span className="font-mono text-[10px] uppercase tracking-[0.16em] text-ink-faint">real wearable data from everyday people — not astronauts</span></div>
        <div className="mt-6 max-w-3xl border-l-2 border-ink-faint/40 pl-4 text-[13px] leading-snug text-ink-dim" data-testid="foundry-explainer">
          <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-ink-faint">What is this page?</p>
          <p className="mt-1">The Foundry is the ship&apos;s laboratory. Every card is one hypothesis about how the body reacts to the spacecraft — for example, <em>&quot;do sleep-poor days make people report tiredness the next day?&quot;</em> A card cannot exist without a real source, a mechanism, and <strong className="text-ink">the exact result that would kill it</strong>. Cards move left to right: <strong className="text-ink">in test → refuted or sustained</strong>, or <strong className="text-ink">no data</strong> when the public data to test it does not exist (we never fill that gap with invented numbers). A sustained card can become a new detector for the monitor.</p>
          <p className="mt-2">Cards on other pages come from the same method: real astronauts&apos; blood in <Link href="/frontier#astronauts" className="underline decoration-ink-faint hover:text-ink">The Frontier</Link>.</p>
        </div>
        <div className="mt-9 grid grid-cols-4 gap-5">
          {COLS.map(([estado, name]) => (
            <section key={estado}>
              <h2 className="border-b border-line pb-2 font-mono text-[11px] uppercase tracking-[0.22em] text-ink-dim">{name}</h2>
              <div className="mt-4 space-y-4">{f?.tarjetas.filter((c) => c.estado === estado).map((c) => <Card key={c.tarjeta_id} c={c} f={f} />)}</div>
            </section>
          ))}
        </div>
        {f?.faro.map((p) => p.en && (
          <aside key={p.id} className="mt-12 max-w-3xl border-l-2 border-warn pl-5">
            <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-warn">Public forecast {p.id} · probability {Math.round(p.probabilidad * 100)}% · closes {p.fecha_limite}</p>
            <p className="mt-2 font-display text-2xl leading-snug">{p.en.statement}</p>
            <p className="mt-2 text-sm text-ink-dim">{p.en.grading}</p>
            <p className="mt-2 break-all font-mono text-[10px] text-ink-faint">sealed {p.emitida_utc} · sha256 {p.sha256}</p>
          </aside>
        ))}
      </div>
    </Room>
  );
}

function Card({ c, f }: { c: Tarjeta; f: Fundicion }) {
  const e = c.en; if (!e) return null;
  const det = f.detectores.find((d) => d.tarjeta_id === c.tarjeta_id);
  return (
    <article className="bg-paper px-4 pb-4 pt-3.5 text-paper-ink shadow-[0_14px_30px_-14px_rgb(0_0_0/.8)]">
      <h3 className="font-display text-[1.45rem] leading-tight">{e.title}</h3>
      <p className="mt-2 text-[12.5px] leading-snug">{e.prediction}</p>
      <p className="mt-3 border-t border-dashed border-paper-dim/50 pt-2 font-mono text-[9.5px] uppercase tracking-[0.14em] text-paper-dim">what would kill it</p>
      <p className="text-[12.5px] font-medium leading-snug">{e.refuter}</p>
      <p className="mt-3 text-[12px] leading-snug text-paper-dim">{e.result}</p>
      {det?.en && <p className="mt-3 bg-paper-ink px-2 py-1.5 font-mono text-[10px] uppercase leading-snug tracking-[0.1em] text-paper">compiled → detector · {det.en.title}<br /><span className="normal-case tracking-normal text-paper/70">{det.en.limit}</span></p>}
      <p className="mt-3 flex justify-between font-mono text-[9px] uppercase tracking-[0.12em] text-paper-dim"><span>{word(c.estado)}</span><span>sha {c.preregistro_hash.slice(0, 8)}</span></p>
    </article>
  );
}
