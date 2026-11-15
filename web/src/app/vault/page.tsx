"use client";
import { useEffect, useRef, useState } from "react";
import { Room } from "@/components/Room";
import { Stamp } from "@/components/Stamp";
import { get, word, type Acta } from "@/lib/api";

const verdicts = (v: unknown): [string, string][] =>
  v && typeof v === "object" ? Object.entries(v as Record<string, unknown>).filter(([, x]) => typeof x === "string").map(([k, x]) => [k, word(x as string)]) : [];

/** 03 · THE VAULT — «Can this be faked?» Cada acta se selló con su hash ANTES de correr; los fallos están en el mismo libro que los aciertos. */
export default function Vault() {
  const [actas, setActas] = useState<Acta[] | null>(null);
  const [runAll, setRunAll] = useState(0);
  const [tally, setTally] = useState<Record<string, boolean>>({});
  useEffect(() => { get<{ actas: Acta[] }>("/api/actas/").then((d) => setActas(d?.actas ?? [])); }, []);
  const ran = actas?.filter((a) => a.ejecutada).length ?? 0;
  return (
    <Room voice="actas" scroll>
      <div className="mx-auto max-w-6xl px-10 pt-10">
        <h1 className="font-display text-5xl leading-tight">Sealed before it ran.</h1>
        <p className="mt-3 max-w-xl text-ink-dim">Each experiment is hashed with SHA-256 before execution. Anyone can recompute the hash from the act file. Failures sit in the same book as successes.</p>
        <p className="mt-5 font-mono text-[11px] uppercase tracking-[0.2em] text-ink-faint">{actas ? `${actas.length} preregistered · ${ran} executed, once each` : "loading…"}</p>
        {actas && (
          <div className="mt-6 flex flex-wrap items-center gap-5">
            <button onClick={() => { setTally({}); setRunAll((n) => n + 1); }} className="border border-ink-dim px-4 py-2 font-mono text-[11px] uppercase tracking-[0.2em] transition-colors hover:border-ink hover:text-ink">Verify all {actas.length} yourself</button>
            <span className="font-mono text-[10.5px] uppercase tracking-[0.16em] text-ink-faint">
              {Object.keys(tally).length ? `${Object.values(tally).filter(Boolean).length} of ${Object.keys(tally).length} recomputed hashes match — SHA-256 computed in this browser, not on our server` : "downloads each act's exact bytes and recomputes its SHA-256 here"}
            </span>
          </div>
        )}
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
              <Verify a={a} runAll={runAll} onResult={(ok) => setTally((t) => ({ ...t, [a.acta]: ok }))} />
              {a.banner && <div className="mt-2.5"><Stamp banner={a.banner.startsWith("REAL") && !a.banner.includes("SIMUL") ? "REAL" : "SIMULADO"} /></div>}
            </li>
          ))}
        </ul>
      </div>
    </Room>
  );
}

/** «Verifícalo tú mismo»: baja los bytes EXACTOS del acta, recalcula su SHA-256 con WebCrypto en TU navegador y lo compara con el hash sellado antes de correr. */
function Verify({ a, runAll, onResult }: { a: Acta; runAll: number; onResult: (ok: boolean) => void }) {
  const [r, setR] = useState<null | "busy" | "err" | { ok: boolean; hash: string }>(null);
  const first = useRef(true);
  const run = async () => {
    setR("busy");
    try {
      const res = await fetch(`/api/actas/${a.acta}/archivo/`);
      if (!res.ok) throw new Error("no file");
      const d = await crypto.subtle.digest("SHA-256", await res.arrayBuffer());
      const hash = [...new Uint8Array(d)].map((b) => b.toString(16).padStart(2, "0")).join("");
      setR({ ok: hash === a.hash_sha256, hash }); onResult(hash === a.hash_sha256);
    } catch { setR("err"); }
  };
  useEffect(() => { if (first.current) { first.current = false; return; } run(); }, [runAll]); // eslint-disable-line react-hooks/exhaustive-deps
  return (
    <div className="mt-2.5 font-mono text-[10.5px] leading-relaxed">
      {r === null || r === "err" ? (
        <button onClick={run} className="uppercase tracking-[0.16em] text-ink-dim underline underline-offset-4 hover:text-ink">{r === "err" ? "could not verify — retry" : "recompute this hash in your browser"}</button>
      ) : r === "busy" ? <span className="uppercase tracking-[0.16em] text-ink-faint">recomputing…</span> : (
        <p className={r.ok ? "text-ok" : "text-signal"}>
          {r.ok ? "✓ MATCH — recomputed here: " : "✗ DOES NOT MATCH — recomputed here: "}<span className="break-all text-ink-dim">{r.hash}</span>
        </p>
      )}
    </div>
  );
}
