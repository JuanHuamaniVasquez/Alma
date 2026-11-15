"use client";
import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import type { Banner } from "@/lib/api";
import { Stamp } from "./Stamp";

type Entry = { id: string; texto: string; fuente: string; banner: Banner; audio: string };
type Ctx = { say: (key: string, force?: boolean) => void; stop: () => void; has: (key: string) => boolean; line: Entry | null; shown: string; speaking: boolean; muted: boolean; setMuted: (m: boolean) => void };
const AlmaCtx = createContext<Ctx>({ say() {}, stop() {}, has: () => false, line: null, shown: "", speaking: false, muted: false, setMuted() {} });
export const useAlma = () => useContext(AlmaCtx);

/**
 * La voz de ALMA. NO es un LLM: reproduce frases pre-generadas por el narrador determinista del backend
 * (plantilla + dato real + fuente). Los subtítulos están SIEMPRE visibles; el audio es un añadido.
 */
export function AlmaProvider({ children }: { children: React.ReactNode }) {
  const [book, setBook] = useState<Record<string, Entry>>({});
  const [line, setLine] = useState<Entry | null>(null);
  const [shown, setShown] = useState("");
  const [speaking, setSpeaking] = useState(false);
  const [awake, setAwake] = useState(false);
  const [muted, setMutedState] = useState(false);
  const audio = useRef<HTMLAudioElement | null>(null);
  const awakeRef = useRef(false);                       // ¿ya hubo un clic? Antes de él el navegador bloquea el audio
  const pending = useRef<string | null>(null);           // lo que ALMA quiso decir antes de despertar: se dice al despertar
  const current = useRef<{ key: string; t: number } | null>(null);
  const raf = useRef<number>(0);

  useEffect(() => { if (new URLSearchParams(window.location.search).has("awake")) { awakeRef.current = true; setAwake(true); } }, []); // ?awake salta la puerta (capturas, grabaciones)
  useEffect(() => { try { setMutedState(localStorage.getItem("alma-muted") === "1"); } catch { /* sin almacenamiento: sigue con sonido */ } }, []);
  const setMuted = useCallback((m: boolean) => { setMutedState(m); if (audio.current) audio.current.muted = m; try { localStorage.setItem("alma-muted", m ? "1" : "0"); } catch { /* idem */ } }, []);
  useEffect(() => { fetch("/voice/manifest.json").then((r) => (r.ok ? r.json() : {})).then(setBook).catch(() => setBook({})); }, []);

  const stop = useCallback(() => { cancelAnimationFrame(raf.current); audio.current?.pause(); setSpeaking(false); }, []);
  const say = useCallback((key: string, force = false) => {
    const e = book[key];
    if (!e) return;
    if (!awakeRef.current) { pending.current = key; setLine(e); setShown(e.texto); return; }   // sin gesto no se puede reproducir: se encola
    const c = current.current;
    if (!force && c && c.key === key && Date.now() - c.t < 1500) return;                     // doble disparo de efectos: no reiniciar la frase
    current.current = { key, t: Date.now() };
    stop(); setLine(e); setShown("");
    const a = new Audio(e.audio); a.muted = muted; audio.current = a;            // en silencio el audio corre igual: los subtítulos se sincronizan con él
    const tick = () => {
      const f = a.duration ? Math.min(1, a.currentTime / (a.duration * 0.96)) : 0;
      setShown(e.texto.slice(0, Math.ceil(e.texto.length * f)));
      if (!a.ended) raf.current = requestAnimationFrame(tick);
    };
    a.onplay = () => { setSpeaking(true); raf.current = requestAnimationFrame(tick); };
    a.onended = () => { setSpeaking(false); setShown(e.texto); };
    a.onerror = () => { setShown(e.texto); };                      // sin audio: el subtítulo aparece entero
    a.play().catch(() => setShown(e.texto));
  }, [book, stop, muted]);

  return (
    <AlmaCtx.Provider value={{ say, stop, has: (k) => k in book, line, shown, speaking, muted, setMuted }}>
      {children}
      {!awake && <WakeGate onWake={() => { awakeRef.current = true; setAwake(true); const k = pending.current; pending.current = null; if (k) say(k, true); }} />}
    </AlmaCtx.Provider>
  );
}

function WakeGate({ onWake }: { onWake: () => void }) {
  return (
    <button onClick={onWake} aria-label="Wake ALMA and enter the ship"
      className="fixed inset-0 z-50 flex cursor-pointer flex-col items-center justify-center gap-7 bg-bg text-ink">
      <div className="breathe h-16 w-16 rounded-full" style={{ background: "radial-gradient(circle at 35% 30%, #fff6e4, #e9b877 45%, #7a3a14 100%)", boxShadow: "0 0 60px 8px rgb(255 140 60 / .28)" }} />
      <div className="font-display text-7xl tracking-wide">ALMA</div>
      <div className="max-w-md px-6 text-center font-sans text-sm leading-relaxed text-ink-dim">
        A ship that keeps its own books. Every alarm carries its receipt; every claim, its preregistration.
      </div>
      <div className="font-mono text-[11px] uppercase tracking-[0.3em] text-ink-faint">Click to wake ALMA · sound on</div>
    </button>
  );
}

/** El orbe de ALMA + subtítulos. Siempre visible, abajo a la izquierda. `room` = clave de la línea de esta sala. */
export function AlmaDock({ room }: { room?: string }) {
  const { say, line, shown, speaking, has, muted, setMuted } = useAlma();
  const sound = <button onClick={() => setMuted(!muted)} aria-pressed={muted} className="pointer-events-auto text-ink-faint hover:text-ink">sound {muted ? "off" : "on"}</button>;
  const idle = !line;
  return (
    <div className="pointer-events-none absolute inset-x-0 bottom-0 z-20 bg-gradient-to-t from-bg from-55% via-bg/80 to-transparent pb-6 pl-6 pt-14"><div className="flex max-w-[54rem] items-end gap-4">
      <button onClick={() => room && say(room, true)} disabled={!room || !has(room)} aria-label="Ask ALMA to speak"
        className="pointer-events-auto relative mb-1 h-11 w-11 shrink-0 rounded-full outline-offset-4 disabled:opacity-40"
        style={{ background: "radial-gradient(circle at 35% 30%, #fff6e4, #e9b877 45%, #7a3a14 100%)",
                 boxShadow: speaking ? "0 0 38px 10px rgb(255 140 60 / .45)" : "0 0 22px 3px rgb(255 140 60 / .18)", transition: "box-shadow .4s" }}>
        <span className={speaking ? "absolute inset-0 animate-ping rounded-full bg-[#ffb36b]/25" : "breathe absolute inset-0 rounded-full"} />
      </button>
      <div className="min-h-[3.5rem]">
        {idle ? (
          <p className="flex gap-5 font-mono text-[11px] uppercase tracking-[0.22em] text-ink-faint"><span>ALMA · tap the light to listen</span>{sound}</p>
        ) : (
          <>
            <p aria-live="polite" className={`font-display text-[1.45rem] italic leading-snug text-ink ${speaking ? "caret" : ""}`}>{shown}</p>
            <p className="mt-2 flex items-center gap-3 font-mono text-[10px] uppercase tracking-[0.14em] text-ink-faint">
              <span>source · {line.fuente}</span><Stamp banner={line.banner} />{sound}
            </p>
          </>
        )}
      </div>
    </div></div>
  );
}
