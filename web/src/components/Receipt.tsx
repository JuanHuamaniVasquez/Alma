"use client";
import type { Banner, HabitatLine } from "@/lib/api";
import { Stamp } from "./Stamp";

const fmt = (x: number) => (x >= 0 ? "+" : "−") + Math.abs(x).toFixed(3);

/** El recibo: papel marfil que sale de una ranura. Nivel 2 de profundidad: los números reales y la regla que decidió el color. */
export function Receipt({ line, label, day, banner, onClose }: { line: HabitatLine | null; label: string; day: number; banner: Banner; onClose: () => void }) {
  const k = 2; // K_CIERRE (DC-04): cierra ⇔ |residuo| ≤ 2·σ del manifiesto
  return (
    <aside aria-label={`Receipt for ${label}`} className="absolute right-8 top-0 z-20 w-[22rem]">
      <div className="mx-4 h-[5px] rounded-b bg-black shadow-[0_2px_0_rgb(255_255_255/.06)]" />
      <div className="slot-in relative -mt-px rotate-[0.6deg] bg-paper px-6 pb-6 pt-5 font-mono text-[12px] leading-relaxed text-paper-ink shadow-[0_24px_50px_-12px_rgb(0_0_0/.7)]"
        style={{ clipPath: "polygon(0 0,100% 0,100% calc(100% - 7px),97% 100%,94% calc(100% - 7px),91% 100%,88% calc(100% - 7px),85% 100%,82% calc(100% - 7px),79% 100%,76% calc(100% - 7px),73% 100%,70% calc(100% - 7px),67% 100%,64% calc(100% - 7px),61% 100%,58% calc(100% - 7px),55% 100%,52% calc(100% - 7px),49% 100%,46% calc(100% - 7px),43% 100%,40% calc(100% - 7px),37% 100%,34% calc(100% - 7px),31% 100%,28% calc(100% - 7px),25% 100%,22% calc(100% - 7px),19% 100%,16% calc(100% - 7px),13% 100%,10% calc(100% - 7px),7% 100%,4% calc(100% - 7px),0 100%)" }}>
        <button onClick={onClose} aria-label="Close receipt" className="absolute right-4 top-3 text-paper-dim hover:text-paper-ink">×</button>
        <div className="flex items-baseline justify-between border-b border-dashed border-paper-dim/50 pb-3">
          <span className="font-display text-[1.7rem] leading-none">{label}</span>
          <span className="text-[10px] uppercase tracking-[0.18em] text-paper-dim">Day {day}</span>
        </div>
        {line ? (
          <>
            <dl className="mt-4 space-y-1.5">
              <Row k="expected (manifest)" v={line.emision_esperada.toFixed(3) + " kg"} />
              <Row k="observed" v={line.emision_observada.toFixed(3) + " kg"} />
              <Row k="residual" v={fmt(line.residuo_contable) + " kg"} strong />
              <Row k="manifest σ" v={line.incertidumbre_del_manifiesto.toFixed(3) + " kg"} />
            </dl>
            <p className="mt-4 border-t border-dashed border-paper-dim/50 pt-3 text-[11px]">
              <span className="uppercase tracking-[0.14em] text-paper-dim">rule </span>
              closes ⇔ |residual| ≤ {k}σ = {(k * line.incertidumbre_del_manifiesto).toFixed(3)} kg
            </p>
            <p className="mt-2 text-[11px] font-medium">
              {line.cierra ? "→ CLOSES: inside the stated uncertainty." : "→ DOES NOT CLOSE: a question, not a verdict."}
            </p>
          </>
        ) : (
          <p className="mt-4 text-[12px]">No ledger line exists for this book. <b>The absence is data:</b> nothing is drawn, nothing is invented.</p>
        )}
        <div className="mt-5 flex items-center justify-between">
          <span className="text-[10px] uppercase tracking-[0.14em] text-paper-dim">source · /api/libro · DC-04</span>
          <Stamp banner={banner} />
        </div>
      </div>
    </aside>
  );
}

function Row({ k, v, strong }: { k: string; v: string; strong?: boolean }) {
  return (
    <div className="flex justify-between gap-4"><dt className="text-paper-dim">{k}</dt><dd className={strong ? "font-medium" : ""}>{v}</dd></div>
  );
}
