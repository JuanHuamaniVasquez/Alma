"use client";
import { useEffect, useState } from "react";
import { Room } from "@/components/Room";
import { Stamp } from "@/components/Stamp";
import { get, word, type Acta } from "@/lib/api";

const verdicts = (v: unknown): [string, string][] =>
  v && typeof v === "object" ? Object.entries(v as Record<string, unknown>).filter(([, x]) => typeof x === "string").map(([k, x]) => [k, word(x as string)]) : [];

/** 03 · THE VAULT — «Can this be faked?» Cada acta se selló con su hash ANTES de correr; los fallos están en el mismo libro que los aciertos. */
export default function Vault() {
  const [actas, setActas] = useState<Acta[] | null>(null);
  useEffect(() => { get<{ actas: Acta[] }>("/api/actas/").then((d) => setActas(d?.actas ?? [])); }, []);
  const ran = actas?.filter((a) => a.ejecutada).length ?? 0;
  return (
    <Room voice="actas" scroll>
      <div className="mx-auto max-w-6xl px-10 pt-10">
        <h1 className="font-display text-5xl leading-tight">Sealed before it ran.</h1>
        <p className="mt-3 max-w-xl text-ink-dim">Each experiment is hashed with SHA-256 before execution. Anyone can recompute the hash from the act file. Failures sit in the same book as successes.</p>
        <p className="mt-5 font-mono text-[11px] uppercase tracking-[0.2em] text-ink-faint">{actas ? `${actas.length} preregistered · ${ran} executed, once each` : "loading…"}</p>
        <ul className="mt-8 grid grid-cols-2 gap-x-6 gap-y-3">
          {actas?.map((a) => (
            <li key={a.acta} className="border border-line bg-bg-2/60 px-5 py-4">
              <div className="flex items-baseline justify-between">
                <span className="font-display text-2xl">{a.acta}</span>
                <span className={`font-mono text-[10px] uppercase tracking-[0.18em] ${a.ejecutada ? "text-ink" : "text-ink-faint"}`}>{a.ejecutada ? "executed" : "sealed · not yet run"}</span>
              </div>
              <p className="mt-2 break-all font-mono text-[10.5px] leading-relaxed text-ink-dim"><span className="text-ink">{a.hash_sha256.slice(0, 16)}</span>{a.hash_sha256.slice(16)}</p>
              <p className="mt-1.5 font-mono text-[10px] uppercase tracking-[0.14em] text-ink-faint">{a.registrada_utc.replace("T", " ").replace("Z", " UTC")} · seed {a.semillas.join(", ")}</p>
              {verdicts(a.veredictos).length > 0 && (
                <p className="mt-2.5 flex flex-wrap gap-x-4 gap-y-1 font-mono text-[10.5px] uppercase tracking-[0.12em]">
                  {verdicts(a.veredictos).map(([k, v]) => <span key={k} className={v === "REFUTED" ? "text-signal" : "text-ink-dim"}>{k.replace(/_/g, " ")} {v}</span>)}
                </p>
              )}
              {a.banner && <div className="mt-2.5"><Stamp banner={a.banner.startsWith("REAL") && !a.banner.includes("SIMUL") ? "REAL" : "SIMULADO"} /></div>}
            </li>
          ))}
        </ul>
      </div>
    </Room>
  );
}
