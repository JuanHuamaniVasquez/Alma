"use client";
/** Una marca por día del libro: calma sin ejes. El día con algún libro abierto se marca en naranja señal (regla: |residuo| > 2σ). */
export function DayTicks({ days, day, open, onPick }: { days: number[]; day: number; open: Set<number>; onPick: (d: number) => void }) {
  return (
    <nav aria-label="Ledger day" className="absolute bottom-7 left-1/2 z-20 flex -translate-x-1/2 items-end gap-[7px]">
      {days.map((d) => (
        <button key={d} onClick={() => onPick(d)} aria-label={`Day ${d}`} aria-current={d === day} className="group flex flex-col items-center gap-1.5">
          <span className="font-mono text-[9px] tracking-widest text-ink-faint opacity-0 transition-opacity group-hover:opacity-100">{d}</span>
          <span className={`block w-[3px] transition-all ${d === day ? "h-5" : "h-3 group-hover:h-4"} ${open.has(d) ? "bg-signal" : d === day ? "bg-ink" : "bg-ink-faint"}`} />
        </button>
      ))}
    </nav>
  );
}
