"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { Room } from "@/components/Room";
import { Stamp } from "@/components/Stamp";
import { Pager, usePaged } from "@/components/Pager";
import { get, word, type Fundicion, type Tarjeta, type Vivero, type ViveroCand } from "@/lib/api";

const COLS = [["en_prueba", "In test"], ["refutada", "Refuted"], ["sostenida", "Sustained"], ["sin_datos", "No data"]] as const;

/** 04 · THE FOUNDRY — «How is an idea born?» Cada tarjeta muestra, de entrada, qué la mataría. Lo que sobrevive se compila en un detector. */
export default function Foundry() {
  const [f, setF] = useState<Fundicion | null>(null);
  const [v, setV] = useState<Vivero | null>(null);
  useEffect(() => { get<Fundicion>("/api/fundicion/").then(setF); get<Vivero>("/api/vivero/").then(setV); }, []);
  const t = f?.tablero;
  return (
    <Room voice="fundicion" scroll hero="foundry" heroFocus="50% 72%">
      <div className="mx-auto max-w-7xl px-10 pt-10">
        <h1 className="font-display text-5xl leading-tight">Ideas are cheap.<br /><span className="text-ink-dim">Surviving them is the product.</span></h1>
        {t && <p className="mt-5 font-mono text-[11px] uppercase tracking-[0.2em] text-ink-faint">{t.nacidas} born · <span className="text-signal">{t.refutada} refuted</span> · {t.sostenida} sustained · {t.sin_datos} no data · {t.detectores_nuevos} compiled into a detector</p>}
        <div className="mt-3 flex items-center gap-4"><Stamp banner="REAL" /><span className="font-mono text-[10px] uppercase tracking-[0.16em] text-ink-faint">real wearable data from everyday people — not astronauts</span></div>
        <div className="mt-6 max-w-3xl border-l-2 border-ink-faint/40 pl-4 text-[13px] leading-snug text-ink-dim" data-testid="foundry-explainer">
          <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-ink-faint">What is this page?</p>
          <p className="mt-1">The Foundry is the ship&apos;s laboratory. Every card is one hypothesis about how the body reacts to the spacecraft — for example, <em>&quot;do sleep-poor days make people report tiredness the next day?&quot;</em> A card cannot exist without a real source, a mechanism, and <strong className="text-ink">the exact result that would kill it</strong>. Cards move left to right: <strong className="text-ink">in test → refuted or sustained</strong>, or <strong className="text-ink">no data</strong> when the public data to test it does not exist (we never fill that gap with invented numbers). A sustained card can become a new detector for the monitor.</p>
          <p className="mt-2">Cards on other pages come from the same method: real astronauts&apos; blood in <Link href="/frontier#astronauts" className="underline decoration-ink-faint hover:text-ink">The Frontier</Link>.</p>
        </div>
        {v && <Pipeline v={v} f={f} />}
        {v && <Nursery v={v} />}
        <h2 className="mt-14 font-display text-3xl">Verdicts</h2>
        <p className="mt-1 max-w-2xl text-[13px] text-ink-dim">Hypotheses that were sealed and tested. Three per column; use the arrows.</p>
        <div className="mt-5 grid grid-cols-4 gap-5">
          {COLS.map(([estado, name]) => <Column key={estado} estado={estado} name={name} f={f} />)}
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


function Column({ estado, name, f }: { estado: string; name: string; f: Fundicion | null }) {
  const items = f?.tarjetas.filter((c) => c.estado === estado) ?? [];
  const pg = usePaged(items, 3);
  return (
    <section>
      <h2 className="border-b border-line pb-2 font-mono text-[11px] uppercase tracking-[0.22em] text-ink-dim">{name} <span className="text-ink-faint">· {items.length}</span></h2>
      <div className="mt-4 space-y-4">{f && pg.slice.map((c) => <Card key={c.tarjeta_id} c={c} f={f} />)}</div>
      {items.length > 0 && <Pager {...pg} label="cards" />}
    </section>
  );
}

/** La cadena de montaje de una idea, con lo que ya hay en cada estación (todo leído de la API). */
function Pipeline({ v, f }: { v: Vivero; f: Fundicion | null }) {
  const t = f?.tablero;
  const steps: [string, string, string][] = [
    [String(v.n_mecanismos), "mechanisms in the library", "each with a published anchor"],
    [String(v.candidatos.length), "hypotheses generated", `${v.n_listos} ready · ${v.n_bloqueados} blocked by missing data`],
    [t ? String(t.nacidas) : "…", "sealed and tested", "hash published before running"],
    [t ? String(t.refutada + t.sostenida) : "…", "reached a verdict", t ? `${t.refutada} refuted · ${t.sostenida} sustained` : ""],
    [t ? String(t.detectores_nuevos) : "…", "became a detector", "only a sustained card can"],
  ];
  return (
    <ol className="mt-10 grid grid-cols-5 gap-0 border-y border-line" aria-label="How a hypothesis travels through the lab">
      {steps.map(([n, a, b], i) => (
        <li key={a} className={`relative px-4 py-4 ${i ? "border-l border-line" : ""}`}>
          <p className="font-display text-5xl leading-none">{n}</p>
          <p className="mt-2 font-mono text-[10px] uppercase tracking-[0.16em] text-ink-dim">{a}</p>
          <p className="mt-1 text-[11px] leading-snug text-ink-faint">{b}</p>
          {i < steps.length - 1 && <span aria-hidden className="absolute -right-2 top-1/2 z-10 -translate-y-1/2 bg-bg px-0.5 text-ink-faint">›</span>}
        </li>
      ))}
    </ol>
  );
}

const NURSERY_TABS = [["listo", "Ready to seal"], ["bloqueado", "Blocked: data missing"], ["ya_probada", "Already tested"]] as const;

/** El VIVERO: hipótesis que el generador de la Fundición propone cruzando mecanismos con los datos reales que existen. Son candidatos, no resultados. */
function Nursery({ v }: { v: Vivero }) {
  const [tab, setTab] = useState<ViveroCand["estado"]>("listo");
  const items = v.candidatos.filter((c) => c.estado === tab);
  const pg = usePaged(items, 3);
  return (
    <section className="mt-12" aria-label="The nursery" data-testid="nursery">
      <div className="flex items-baseline gap-4 border-b border-line pb-2"><h2 className="font-display text-3xl">The nursery</h2><Stamp banner={v.banner} /></div>
      <p className="mt-2 max-w-3xl text-[13px] leading-snug text-ink-dim">The lab generates hypotheses by crossing {v.n_mecanismos} mechanisms from the literature with the real data it holds. It never looks at a result to decide what to ask. Each candidate says what it would cost, what would kill it, and — when the data does not exist — exactly what is missing. Nothing here has been tested.</p>
      <div className="mt-4 flex gap-5 font-mono text-[10px] uppercase tracking-[0.18em]" role="tablist" aria-label="Nursery filter">
        {NURSERY_TABS.map(([k, t]) => { const n = v.candidatos.filter((c) => c.estado === k).length; return (
          <button key={k} role="tab" aria-selected={tab === k} onClick={() => { setTab(k); pg.reset(); }} className={`border-b pb-0.5 ${tab === k ? "border-ink text-ink" : "border-transparent text-ink-faint hover:text-ink-dim"}`}>{t} · {n}</button>); })}
      </div>
      <div className="mt-5 grid grid-cols-3 gap-5">{pg.slice.map((c) => <Candidate key={c.id} c={c} />)}</div>
      <Pager {...pg} label="hypotheses" />
    </section>
  );
}

function Candidate({ c }: { c: ViveroCand }) {
  const bloqueado = c.estado === "bloqueado";
  return (
    <article className={`border border-dashed p-4 ${bloqueado ? "border-ink-faint/50" : "border-ink-dim/70"}`}>
      <p className="font-mono text-[9.5px] uppercase tracking-[0.16em]" style={{ color: bloqueado ? "var(--color-signal)" : "#d8d0c0" }}>{bloqueado ? "blocked · needs data that does not exist" : c.estado === "ya_probada" ? `already tested · ${c.ya_probada_en}` : "ready to seal"}</p>
      <h3 className="mt-1 font-display text-[1.45rem] leading-tight">{c.titulo}</h3>
      <p className="mt-2 text-[12.5px] leading-snug text-ink-dim">{c.en.mechanism}</p>
      <p className="mt-3 font-mono text-[9.5px] uppercase tracking-[0.14em] text-ink-faint">what would kill it</p>
      <p className="text-[12px] leading-snug">{c.en.kill}</p>
      <p className="mt-3 font-mono text-[9.5px] uppercase tracking-[0.14em] text-ink-faint">price</p>
      <p className="text-[12px] leading-snug text-ink-dim">{c.en.price} {c.en.compute}</p>
      <p className="mt-3 flex flex-wrap gap-x-3 font-mono text-[9px] uppercase tracking-[0.12em] text-ink-faint">{c.fuentes.map((f) => <span key={f.id} title={f.nombre}>{f.tipo} {f.id}</span>)}</p>
      <p className="mt-2 text-[11.5px] italic leading-snug text-ink-dim">Next: {c.en.next}</p>
    </article>
  );
}
