import type { Banner } from "@/lib/api";
import { BANNER_EN } from "@/lib/api";

/** Sello de goma: REAL (salvia) o SIMULADO (ámbar). Obligatorio en toda vista y en todo recibo (mandamiento 3). */
export function Stamp({ banner, className = "", compact = false }: { banner: Banner; className?: string; compact?: boolean }) {
  const c = banner === "REAL" ? "text-ok border-ok" : "text-warn border-warn";
  return (
    <span className={`inline-block -rotate-2 select-none border px-1.5 py-[1px] font-mono text-[10px] font-medium uppercase tracking-[0.16em] ${c} ${className}`}>
      {compact ? (banner === "REAL" ? "REAL" : "SIMULATED") : BANNER_EN[banner]}
    </span>
  );
}
