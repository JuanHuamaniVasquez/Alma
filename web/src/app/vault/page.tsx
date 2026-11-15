"use client";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useAlma } from "@/components/Alma";
import { Room } from "@/components/Room";
import { HashArt } from "@/components/HashArt";
import { Stamp } from "@/components/Stamp";
import { get, word, type Acta } from "@/lib/api";
import { closest, emptyFilters, hasFilters, OUTCOME_LABEL, parse, ROOMS, search, type Doc, type Filters, type Outcome } from "@/lib/search";

const PAGE = 8;
const SPOKEN: Record<Outcome, string> = { refuted: "refuted", sustained: "sustained", mixed: "mixed results", inconclusive: "inconclusive", partial: "partial", not_replicated: "not replicated", not_run: "sealed, not yet run", no_data: "no data" };
const ROOM_SAID: Record<string, string> = { medical: "the Medical Module", machine: "the Machine Room", kill: "the Leak", vault: "the Vault", foundry: "the Foundry", storm: "the Storm", budget: "the Budget", capsule: "the Capsule" };
const EXAMPLES = ["refuted experiments", "solar storms", "open FB-020", "not run yet", "real data, sustained", "go to the foundry"];
const OUTCOME_ORDER: Outcome[] = ["refuted", "sustained", "mixed", "inconclusive", "partial", "not_replicated", "not_run"];
const verdicts = (v: unknown): [string, string][] => (v && typeof v === "object" ? Object.entries(v as Record<string, unknown>).filter(([, x]) => typeof x === "string").map(([k, x]) => [k, word(x as string)]) : []);

type SR = { lang: string; interimResults: boolean; continuous: boolean; onresult: (e: any) => void; onerror: (e: any) => void; onend: () => void; start: () => void; stop: () => void };

/** 04 · THE VAULT — «Can this be faked?» Actas selladas con su hash; ahora se buscan escribiendo o HABLANDO, y ALMA responde y te lleva a lo que pides. */
export default function Vault() {
  const router = useRouter();
  const { sayClips, stop: stopAlma } = useAlma();
  const [actas, setActas] = useState<Acta[] | null>(null);
  const [q, setQ] = useState("");
  const [f, setF] = useState<Filters>(emptyFilters());
  const [page, setPage] = useState(1);
  const [open, setOpen] = useState<string | null>(null);
  const [res, setRes] = useState<Record<string, "busy" | "err" | { ok: boolean; hash: string }>>({});
  const [heard, setHeard] = useState("");
  const [micState, setMicState] = useState<"idle" | "listening" | "unsupported" | string>("idle");
  const rec = useRef<SR | null>(null);
  const rows = useRef<Record<string, HTMLElement | null>>({});

  useEffect(() => { get<{ actas: Acta[] }>("/api/actas/").then((d) => setActas(d?.actas ?? [])); }, []);
  useEffect(() => { const C = (window as any).SpeechRecognition ?? (window as any).webkitSpeechRecognition; if (!C) setMicState("unsupported"); }, []);

  const docs: (Doc & { raw: Acta })[] = useMemo(() => (actas ?? []).filter((a) => a.en).map((a) => ({ acta: a.acta, ejecutada: a.ejecutada, title: a.en!.title, summary: a.en!.summary, outcome: a.en!.outcome as Outcome, data: a.en!.data, tags: a.en!.tags, raw: a })), [actas]);
  const hits = useMemo(() => search(q, f, docs), [q, f, docs]);
  const pages = Math.max(1, Math.ceil(hits.length / PAGE));
  const shown = hits.slice((page - 1) * PAGE, page * PAGE);
  useEffect(() => { if (page > pages) setPage(1); }, [pages, page]);

  /** «Verifícalo tú mismo»: baja los bytes EXACTOS del acta, recalcula su SHA-256 con WebCrypto en TU navegador y lo compara con el hash sellado antes de correr. */
  const verifyOne = useCallback(async (a: Acta) => {
    setRes((r) => ({ ...r, [a.acta]: "busy" }));
    try {
      const x = await fetch(`/api/actas/${a.acta}/archivo/`);
      if (!x.ok) throw new Error("no file");
      const d = await crypto.subtle.digest("SHA-256", await x.arrayBuffer());
      const hash = [...new Uint8Array(d)].map((b) => b.toString(16).padStart(2, "0")).join("");
      setRes((r) => ({ ...r, [a.acta]: { ok: hash === a.hash_sha256, hash } }));
    } catch { setRes((r) => ({ ...r, [a.acta]: "err" })); }
  }, []);
  const verifyAll = useCallback(() => { setRes({}); (actas ?? []).forEach((a) => verifyOne(a)); }, [actas, verifyOne]);       // las 21, no solo la página visible
  const checked = Object.values(res).filter((x): x is { ok: boolean; hash: string } => typeof x === "object");

  const say = useCallback((keys: string[], text: string, done?: () => void) => sayClips(keys, text, done), [sayClips]);
  const idPart = (d: Doc) => [`id_${d.acta}`, `o_${d.outcome}`];
  const idText = (d: Doc) => `${d.acta}, ${SPOKEN[d.outcome]}`;

  /** Ejecuta lo escrito o dicho: busca, abre, navega, verifica, limpia o ayuda; y ALMA lo cuenta con su vocabulario cerrado. */
  const run = useCallback((raw: string) => {
    const it = parse(raw, docs);
    setHeard(raw.trim());
    switch (it.type) {
      case "empty": say(["heard_nothing"], "I did not catch that. You can type instead."); return;
      case "help": say(["help"], "You can say: show refuted experiments, find solar storms, open F B zero two zero, verify everything, or go to the foundry."); return;
      case "clear": setQ(""); setF(emptyFilters()); setPage(1); setOpen(null); say(["cleared"], "Showing the whole vault."); return;
      case "verify": verifyAll(); say(["verifying"], "Recomputing every hash in your browser."); return;
      case "goto": { const r = ROOMS[it.room]; say(["going", `room_${it.room}`], `Going to ${ROOM_SAID[it.room]}.`, () => router.push(r.path)); return; }
      case "open": {
        const d = it.id ? docs.find((x) => x.acta === it.id) : undefined;
        if (!d) { say(["no_id"], `There is no experiment with that number (${it.spoken}).`); return; }
        setQ(""); setF(emptyFilters()); setOpen(d.acta);
        const idx = docs.findIndex((x) => x.acta === d.acta); setPage(Math.floor(idx / PAGE) + 1);
        setTimeout(() => rows.current[d.acta]?.scrollIntoView({ behavior: "smooth", block: "center" }), 120);
        say(["opening", ...idPart(d)], `Opening ${idText(d)}.`); return;
      }
      case "search": {
        setQ(it.query); setF(it.filters); setPage(1); setOpen(null);
        const h = search(it.query, it.filters, docs), n = h.length;
        if (n === 0) {
          const c = closest(it.query || raw, docs);
          if (c.length) say(["none", "closest", ...c.flatMap((d, i) => (i ? ["and"] : []).concat(idPart(d)))], `I found nothing like that in the vault. The closest are ${c.map(idText).join(", and ")}.`);
          else say(["none", "try"], "I found nothing like that in the vault. Try a topic, a verdict, or an experiment number.");
          return;
        }
        const top = h.slice(0, 3).map((x) => x.doc);
        const head = [`i_found`, `n_${n}`, n === 1 ? "experiment" : "experiments"], headT = `I found ${n} experiment${n === 1 ? "" : "s"}.`;
        if (!it.query) { say(head, headT); return; }               // solo filtros: cuenta y no «el mejor»
        const keys = [...head, "best", ...idPart(top[0]), ...top.slice(1).flatMap((d, i) => (i === 0 ? ["then"] : ["and"]).concat(idPart(d)))];
        say(keys, `${headT} The best match is ${idText(top[0])}.${top.length > 1 ? ` Then ${top.slice(1).map(idText).join(", and ")}.` : ""}`);
      }
    }
  }, [docs, say, router, verifyAll]);

  // ---- voz: reconocimiento del navegador (en Chrome lo procesa el servicio de Google; escribir funciona sin red)
  const listen = () => {
    const C = (window as any).SpeechRecognition ?? (window as any).webkitSpeechRecognition;
    if (!C) return;
    if (micState === "listening") { rec.current?.stop(); return; }
    stopAlma();                                                      // ALMA se calla para no oírse a sí misma
    const r: SR = new C(); r.lang = "en-US"; r.interimResults = true; r.continuous = false;
    let final = "";
    r.onresult = (e: any) => { let interim = ""; for (const res of e.results) { if (res.isFinal) final += res[0].transcript; else interim += res[0].transcript; } setHeard(final || interim); };
    r.onerror = (e: any) => setMicState(e.error === "not-allowed" ? "Microphone permission was denied." : e.error === "network" ? "The browser's speech service is unreachable (it needs internet). You can type." : e.error === "no-speech" ? "idle" : `Speech error: ${e.error}`);
    r.onend = () => { setMicState((s) => (s === "listening" ? "idle" : s)); run(final); };
    rec.current = r; setMicState("listening"); setHeard(""); r.start();
  };

  const toggle = <T,>(arr: T[], v: T) => (arr.includes(v) ? arr.filter((x) => x !== v) : [...arr, v]);
  const ran = actas?.filter((a) => a.ejecutada).length ?? 0;
  return (
    <Room voice="actas" scroll>
      <div className="mx-auto max-w-6xl px-10 pt-9">
        <h1 className="font-display text-5xl leading-tight">Sealed before it ran.</h1>
        <p className="mt-3 max-w-xl text-ink-dim">Each experiment is hashed with SHA-256 before execution. Anyone can recompute the hash from the act file. Failures sit in the same book as successes.</p>

        {/* buscador: escribe o habla */}
        <div className="mt-7">
          <div className="flex items-stretch gap-0 border border-ink-faint focus-within:border-ink">
            <input value={q} onChange={(e) => { setQ(e.target.value); setPage(1); }} onKeyDown={(e) => { if (e.key === "Enter") run(q); }} aria-label="Search the vault"
              placeholder={`Search ${actas?.length ?? 21} experiments — type, or press the mic and say “show refuted experiments”`}
              className="min-w-0 flex-1 bg-transparent px-4 py-3 font-sans text-[15px] text-ink placeholder:text-ink-faint focus:outline-none" />
            {(q || hasFilters(f)) && <button onClick={() => run("clear")} aria-label="Clear search" className="px-3 font-mono text-[11px] uppercase tracking-[0.18em] text-ink-faint hover:text-ink">clear</button>}
            <button onClick={listen} disabled={micState === "unsupported"} aria-pressed={micState === "listening"} aria-label={micState === "listening" ? "Stop listening" : "Search by voice"}
              className={`grid w-14 place-items-center border-l border-ink-faint transition-colors disabled:opacity-30 ${micState === "listening" ? "bg-signal text-bg" : "text-ink-dim hover:text-ink"}`}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden><rect x="9" y="3" width="6" height="12" rx="3" /><path d="M5 11a7 7 0 0 0 14 0M12 18v3" /></svg>
            </button>
          </div>
          <p className="mt-2 min-h-[1.2rem] font-mono text-[10.5px] uppercase tracking-[0.14em] text-ink-faint" role="status">
            {micState === "listening" ? <span className="text-signal">listening… say what you want to find, open or visit</span>
              : micState === "unsupported" ? "voice search is not available in this browser — typing works everywhere"
              : micState !== "idle" ? <span className="text-signal">{micState}</span>
              : heard ? <>heard: “{heard}”</> : "voice uses your browser's speech recognition (Chrome sends the audio to Google); ALMA answers with her own voice"}
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            {EXAMPLES.map((x) => <button key={x} onClick={() => run(x)} className="border border-ink-faint px-2.5 py-1 font-mono text-[10.5px] tracking-[0.08em] text-ink-dim transition-colors hover:border-ink hover:text-ink">“{x}”</button>)}
            <button onClick={() => run("help")} className="px-2 py-1 font-mono text-[10.5px] uppercase tracking-[0.16em] text-ink-faint underline underline-offset-4 hover:text-ink">what can I say</button>
          </div>
        </div>

        {/* filtros */}
        <div className="mt-6 flex flex-wrap items-center gap-x-6 gap-y-3 border-t border-line pt-4 font-mono text-[10.5px] uppercase tracking-[0.14em]">
          <div className="flex flex-wrap items-center gap-2"><span className="text-ink-faint">outcome</span>
            {OUTCOME_ORDER.map((o) => <button key={o} onClick={() => { setF({ ...f, outcome: toggle(f.outcome, o) }); setPage(1); }} aria-pressed={f.outcome.includes(o)}
              className={`border px-2 py-1 transition-colors ${f.outcome.includes(o) ? (o === "refuted" ? "border-signal bg-signal text-bg" : "border-ink bg-ink text-bg") : "border-ink-faint text-ink-dim hover:border-ink"}`}>{OUTCOME_LABEL[o]}</button>)}</div>
          <div className="flex items-center gap-2"><span className="text-ink-faint">data</span>
            {(["real", "simulated"] as const).map((d) => <button key={d} onClick={() => { setF({ ...f, data: f.data === d ? null : d }); setPage(1); }} aria-pressed={f.data === d}
              className={`border px-2 py-1 transition-colors ${f.data === d ? "border-ink bg-ink text-bg" : "border-ink-faint text-ink-dim hover:border-ink"}`}>{d}</button>)}</div>
          <div className="flex items-center gap-2"><span className="text-ink-faint">state</span>
            {([["executed", "executed"], ["sealed", "sealed, not run"]] as const).map(([k, t]) => <button key={k} onClick={() => { setF({ ...f, estado: f.estado === k ? null : k }); setPage(1); }} aria-pressed={f.estado === k}
              className={`border px-2 py-1 transition-colors ${f.estado === k ? "border-ink bg-ink text-bg" : "border-ink-faint text-ink-dim hover:border-ink"}`}>{t}</button>)}</div>
        </div>

        <div className="mt-5 flex flex-wrap items-center justify-between gap-4">
          <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-ink-faint" role="status">{actas ? `${hits.length} of ${actas.length} shown · ${ran} executed, once each` : "loading…"}</p>
          {actas && (
            <div className="flex items-center gap-4">
              <span className="font-mono text-[10.5px] uppercase tracking-[0.14em] text-ink-faint">{checked.length ? `${checked.filter((x) => x.ok).length} of ${checked.length} recomputed hashes match — computed in this browser` : "recompute every hash here, not on our server"}</span>
              <button onClick={verifyAll} className="border border-ink-dim px-3 py-1.5 font-mono text-[10.5px] uppercase tracking-[0.18em] transition-colors hover:border-ink hover:text-ink">Verify all {actas.length} yourself</button>
            </div>
          )}
        </div>

        {/* lista en filas (un libro de registro, no tarjetas) */}
        <ul className="mt-4 divide-y divide-line border-y border-line">
          {shown.map(({ doc, score }) => {
            const a = (doc as Doc & { raw: Acta }).raw, isOpen = open === a.acta;
            return (
              <li key={a.acta} ref={(el) => { rows.current[a.acta] = el; }} className={`transition-colors ${isOpen ? "bg-ink/[0.05]" : "hover:bg-ink/[0.025]"}`}>
                <button onClick={() => setOpen(isOpen ? null : a.acta)} aria-expanded={isOpen} className="grid w-full grid-cols-[11.5rem_1fr_auto] items-center gap-6 px-3 py-4 text-left">
                  <span className="flex items-center gap-3"><HashArt hash={a.hash_sha256} /><span className="font-display text-[1.7rem] leading-none">{a.acta}</span></span>
                  <span><span className="block text-[15px] font-medium text-ink">{doc.title}</span><span className="mt-1 block text-[13px] leading-snug text-ink-dim">{doc.summary}</span></span>
                  <span className="flex flex-col items-end gap-1.5 font-mono text-[10.5px] uppercase tracking-[0.14em]">
                    <span className={doc.outcome === "refuted" ? "text-signal" : doc.outcome === "sustained" ? "text-ok" : "text-ink-dim"}>{OUTCOME_LABEL[doc.outcome]}</span>
                    <span className="text-ink-faint">{doc.data === "real" ? "real data" : doc.data === "simulated" ? "simulated" : doc.data === "none" ? "no data" : "real + simulated"}</span>
                  </span>
                </button>
                {isOpen && (
                  <div className="grid gap-3 px-3 pb-5 pl-[13.5rem] font-mono text-[11px] leading-relaxed text-ink-dim">
                    <p className="break-all"><span className="text-ink">{a.hash_sha256.slice(0, 16)}</span>{a.hash_sha256.slice(16)}</p>
                    <p className="uppercase tracking-[0.12em] text-ink-faint">{a.registrada_utc.replace("T", " ").replace("Z", " UTC")} · seed {a.semillas.join(", ")} · {a.ejecutada ? "executed once" : "sealed, not yet run"}</p>
                    {verdicts(a.veredictos).length > 0 && <p className="flex flex-wrap gap-x-4 gap-y-1 uppercase tracking-[0.1em]">{verdicts(a.veredictos).map(([k, v]) => <span key={k} className={v === "REFUTED" ? "text-signal" : ""}>{k.replace(/_/g, " ")} {v}</span>)}</p>}
                    <div className="flex flex-wrap items-center gap-3">{a.banner && <Stamp banner={a.banner.startsWith("REAL") && !a.banner.includes("SIMUL") ? "REAL" : "SIMULADO"} />}<Verify r={res[a.acta]} onRun={() => verifyOne(a)} /></div>
                  </div>
                )}
                {!isOpen && <Verify r={res[a.acta]} onRun={() => verifyOne(a)} compact />}
                <span hidden>{score}</span>
              </li>
            );
          })}
          {actas && hits.length === 0 && (
            <li className="px-3 py-10 text-ink-dim"><p className="font-display text-3xl">Nothing here matches.</p><p className="mt-2 text-sm">{(() => { const c = closest(q, docs); return c.length ? <>Closest: {c.map((d) => <button key={d.acta} onClick={() => run(`open ${d.acta}`)} className="mr-3 underline underline-offset-4 hover:text-ink">{d.acta}</button>)}</> : "Try a topic, a verdict, or an experiment number."; })()}</p></li>
          )}
        </ul>

        {pages > 1 && (
          <nav aria-label="Pages" className="mt-5 flex items-center justify-center gap-5 font-mono text-[11px] uppercase tracking-[0.18em]">
            <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1} className="text-ink-dim hover:text-ink disabled:opacity-30">← prev</button>
            {Array.from({ length: pages }, (_, i) => <button key={i} onClick={() => setPage(i + 1)} aria-current={page === i + 1} className={`px-1 ${page === i + 1 ? "border-b border-ink text-ink" : "text-ink-faint hover:text-ink-dim"}`}>{i + 1}</button>)}
            <button onClick={() => setPage(Math.min(pages, page + 1))} disabled={page === pages} className="text-ink-dim hover:text-ink disabled:opacity-30">next →</button>
          </nav>
        )}
      </div>
    </Room>
  );
}

/** Resultado de la verificación de un acta (el cálculo vive en el padre, para que «verify all» no dependa de qué página se ve). */
function Verify({ r, onRun, compact }: { r: "busy" | "err" | { ok: boolean; hash: string } | undefined; onRun: () => void; compact?: boolean }) {
  if (compact) return r && typeof r === "object" ? <p className={`px-3 pb-2 pl-[13.5rem] font-mono text-[10.5px] ${r.ok ? "text-ok" : "text-signal"}`}>{r.ok ? "✓ MATCH — recomputed in your browser" : "✗ DOES NOT MATCH"}</p> : null;
  return (
    <div className="font-mono text-[10.5px] leading-relaxed">
      {r === undefined || r === "err" ? <button onClick={onRun} className="uppercase tracking-[0.16em] text-ink-dim underline underline-offset-4 hover:text-ink">{r === "err" ? "could not verify — retry" : "recompute this hash in your browser"}</button>
        : r === "busy" ? <span className="uppercase tracking-[0.16em] text-ink-faint">recomputing…</span>
        : <p className={r.ok ? "text-ok" : "text-signal"}>{r.ok ? "✓ MATCH — recomputed here: " : "✗ DOES NOT MATCH — recomputed here: "}<span className="break-all text-ink-dim">{r.hash}</span></p>}
    </div>
  );
}
