"use client";
import { useEffect, useState } from "react";
import { Room } from "@/components/Room";
import { Stamp } from "@/components/Stamp";
import { get, type Capsule } from "@/lib/api";

function download(c: Capsule, i: number) {
  const url = URL.createObjectURL(new Blob([JSON.stringify(c, null, 2)], { type: "application/json" }));
  Object.assign(document.createElement("a"), { href: url, download: `alma-capsule-${i + 1}-${c.preregistro.hash.slice(0, 8)}.json` }).click();
  URL.revokeObjectURL(url);
}

/** 08 · THE CAPSULE — «Can I take this with me?» El veredicto exportable. Los LÍMITES van primero: sin ellos no hay cápsula. */
export default function CapsulePage() {
  const [cs, setCs] = useState<Capsule[] | null>(null);
  useEffect(() => { get<{ capsulas: Capsule[] }>("/api/capsulas/").then((d) => setCs(d?.capsulas ?? [])); }, []);
  return (
    <Room scroll>
      <div className="mx-auto max-w-5xl px-10 pt-10">
        <h1 className="font-display text-5xl leading-tight">A verdict you can carry.</h1>
        <p className="mt-3 max-w-2xl text-ink-dim">Each capsule packs a resolved hypothesis: the protocol, the exact numbers, the rule that would have killed it, the preregistration hash — and, first of all, its limits. No limits, no capsule.</p>
        <div className="mt-9 space-y-8">
          {cs?.map((c, i) => (
            <article key={i} className="bg-paper px-8 pb-6 pt-6 text-paper-ink shadow-[0_24px_50px_-14px_rgb(0_0_0/.8)]">
              <div className="flex items-start justify-between gap-6">
                <p className={`font-mono text-[11px] font-medium uppercase tracking-[0.2em] ${c.veredicto.toUpperCase().startsWith("REFUTED") ? "text-[#c2410c]" : ""}`}>{c.veredicto}</p>
                <Stamp banner={c.banner} />
              </div>
              <p className="mt-4 bg-paper-ink px-4 py-3 text-[13px] leading-relaxed text-paper"><b className="mr-2 font-mono text-[10px] uppercase tracking-[0.2em]">limits</b>{c.limites}</p>
              <p className="mt-4 font-display text-2xl leading-snug">{c.hipotesis}</p>
              <p className="mt-3 font-mono text-[10px] uppercase tracking-[0.16em] text-paper-dim">what would have killed it</p>
              <p className="text-[13px] font-medium">{c.senal_refutadora}</p>
              <p className="mt-3 text-[12.5px] leading-snug text-paper-dim">{c.prueba_protocolo}</p>
              <dl className="mt-4 grid grid-cols-[repeat(auto-fill,minmax(11rem,1fr))] gap-x-6 gap-y-2 border-t border-dashed border-paper-dim/50 pt-3 font-mono text-[11px]">
                {Object.entries(c.numeros).filter(([k]) => k !== "data_sha256").map(([k, v]) => (
                  <div key={k}><dt className="text-[9.5px] uppercase tracking-[0.12em] text-paper-dim">{k.replace(/_/g, " ")}</dt><dd>{typeof v === "number" ? (Math.abs(v) < 0.01 && v !== 0 ? v.toExponential(2) : +v.toFixed(4)) : v}</dd></div>
                ))}
              </dl>
              <div className="mt-5 flex flex-wrap items-center justify-between gap-3 font-mono text-[10px] uppercase tracking-[0.12em] text-paper-dim">
                <span className="break-all">preregistered sha256 {c.preregistro.hash} · seed {c.preregistro.semilla}</span>
                <button onClick={() => download(c, i)} className="border border-paper-ink px-3 py-1.5 text-paper-ink transition-colors hover:bg-paper-ink hover:text-paper">Download capsule · JSON</button>
              </div>
            </article>
          ))}
        </div>
      </div>
    </Room>
  );
}
