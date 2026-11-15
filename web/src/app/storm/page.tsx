"use client";
import { useEffect, useState } from "react";
import { Room } from "@/components/Room";
import { Stamp } from "@/components/Stamp";
import { useAlma } from "@/components/Alma";
import { get, type Banner, type Scenario, type SpaceEvent } from "@/lib/api";

const SUN = [
  { id: "193", name: "Corona · 193 Å", live: "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0193.jpg", local: "/sun/latest_1024_0193.jpg", note: "hot plasma, ~1.2 million K" },
  { id: "hmi", name: "Surface · sunspots", live: "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMIIC.jpg", local: "/sun/latest_1024_HMIIC.jpg", note: "visible-light intensity" },
] as const;
const G1 = 5; // NOAA G1 (tormenta geomagnética menor): Kp ≥ 5. Regla de color: solo por encima de este umbral hay naranja (S-15).

/** 06 · THE STORM — «What is the Sun doing right now?» Sol real (NASA SDO) y Kp real (NOAA SWPC). Nada simulado en esta sala. */
export default function Storm() {
  const [ev, setEv] = useState<SpaceEvent[] | null>(null);
  const [banner, setBanner] = useState<Banner>("REAL");
  const [sun, setSun] = useState(0);
  const [src, setSrc] = useState<string>(SUN[0].live);
  const [scale, setScale] = useState<string | null>(null);        // null = en vivo; "G1"…"G5" = escenario SIMULADO
  const [sc, setSc] = useState<Scenario | null>(null);
  const { say } = useAlma();
  useEffect(() => { get<{ banner: Banner; eventos: SpaceEvent[] }>("/api/tormenta/?tipo=lectura_clima_espacial").then((d) => { setEv(d?.eventos ?? []); if (d) setBanner(d.banner); }); }, []);
  useEffect(() => { setSrc(SUN[sun].live); }, [sun]);
  useEffect(() => { const q = new URLSearchParams(window.location.search).get("sim"); if (q) setScale(q); }, []);   // ?sim=G3 → enlace profundo
  useEffect(() => {
    if (!scale) { setSc(null); return; }
    get<Scenario>(`/api/tormenta/escenario/${scale}/`).then((d) => { setSc(d); say(`escenario-${scale}`); });
  }, [scale]); // eslint-disable-line react-hooks/exhaustive-deps
  const source = scale && sc ? sc.eventos : (ev ?? []);
  const kps = [...source].filter((e) => e.parametros.kp != null).sort((a, b) => a.ts_utc_inicio.localeCompare(b.ts_utc_inicio)).slice(-56);
  const now = kps.at(-1), peak = kps.reduce((m, e) => Math.max(m, e.parametros.kp ?? 0), 0);
  const storm = scale && sc ? true : (now?.parametros.kp ?? 0) >= G1;
  return (
    <Room voice={scale ? undefined : "tormenta"}>
      {scale && sc && <div className="absolute inset-x-0 top-0 z-10 border-b border-warn/60 bg-warn/10 py-1.5 text-center font-mono text-[11px] uppercase tracking-[0.3em] text-warn">SIMULATED UNIVERSE — DAY {sc.dia_habitat}</div>}
      <div className="mx-auto grid h-full max-w-6xl grid-cols-[minmax(0,34rem)_1fr] items-center gap-14 px-10 pb-28 pt-6">
        <figure className="relative">
          <div className={`relative aspect-square w-full overflow-hidden rounded-full shadow-[0_0_120px_10px_rgb(255_120_40/.18)] transition-opacity duration-700 ${scale ? "opacity-35" : ""}`}>
            {/* hotlink al último SDO; si no hay red, la instantánea local con su marca de tiempo */}
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={src} alt={`NASA Solar Dynamics Observatory, ${SUN[sun].name}`} onError={() => setSrc(SUN[sun].local)} className="h-full w-full scale-[1.12] object-cover" />
          </div>
          <figcaption className="mt-5 flex flex-wrap items-center gap-x-4 gap-y-1 font-mono text-[10px] uppercase tracking-[0.16em] text-ink-faint">
            <span>NASA / SDO · {SUN[sun].note}</span><span className="text-ink-dim">{scale ? "real image from today — not part of the scenario" : "latest frame (live link; local snapshot if offline)"}</span>
          </figcaption>
          <div className="mt-3 flex gap-5">
            {SUN.map((s, i) => <button key={s.id} onClick={() => setSun(i)} className={`font-mono text-[11px] uppercase tracking-[0.2em] ${i === sun ? "text-ink" : "text-ink-faint hover:text-ink-dim"}`}>{s.name}</button>)}
          </div>
        </figure>
        <section>
          <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-ink-faint">{scale ? `Simulated scenario ${scale} · planetary K index` : "Planetary K index · NOAA SWPC"}</p>
          <p className={`mt-3 font-display text-[8rem] leading-none ${storm ? "text-signal" : "text-ink"}`}>{scale && sc ? sc.pico_kp.toFixed(2) : now ? now.parametros.kp!.toFixed(2) : "—"}</p>
          <p className="mt-3 font-mono text-[12px] uppercase tracking-[0.18em]" style={{ color: storm ? "var(--color-signal)" : "var(--color-ink-dim)" }}>
            {scale && sc ? `Peak of a simulated ${scale} storm · threshold Kp ${sc.pico_kp}` : now ? (storm ? "Geomagnetic storm: at or above G1 (Kp 5)" : "Below storm level · G1 begins at Kp 5") : "No reading available · the absence is data"}
          </p>
          <div className="relative mt-10 h-32">
            <div className="absolute inset-x-0 border-t border-dashed border-warn/70" style={{ bottom: `${(G1 / 9) * 100}%` }}><span className="absolute -top-4 right-0 font-mono text-[9px] uppercase tracking-widest text-warn">storm line · Kp 5</span></div>
            <div className="absolute inset-0 flex items-end gap-[3px]">
              {kps.map((e) => { const k = e.parametros.kp!; return <span key={e.evento_id} title={`${e.ts_utc_inicio} · Kp ${k}`} className="flex-1" style={{ height: `${Math.max((k / 9) * 100, 2)}%`, background: k >= G1 ? "var(--color-signal)" : "var(--color-ink)", opacity: k >= G1 ? 1 : 0.55 }} />; })}
            </div>
          </div>
          {kps.length > 0 && <p className="mt-3 flex justify-between font-mono text-[9.5px] uppercase tracking-[0.14em] text-ink-faint"><span>{kps[0].ts_utc_inicio.slice(0, 10)}</span><span>peak Kp {peak.toFixed(2)} · {kps.length} readings, 3 h each</span><span>{now!.ts_utc_inicio.slice(0, 16).replace("T", " ")} UTC</span></p>}
          {now && <p className="mt-6 break-all font-mono text-[10px] leading-relaxed text-ink-faint">{scale && sc ? `recipe · ${sc.receta_en} · seed ${sc.semilla} · series sha256 ${now.hash_lectura_cruda}` : `source · NOAA SWPC · raw reading sha256 ${now.hash_lectura_cruda}`}</p>}
          <div className="mt-4"><Stamp banner={scale && sc ? sc.banner : banner} /></div>
          <div className="mt-8 flex flex-wrap items-center gap-3 border-t border-line pt-5">
            <span className="mr-2 font-mono text-[10px] uppercase tracking-[0.2em] text-ink-faint">What if — simulate</span>
            {["G1", "G2", "G3", "G4", "G5"].map((g) => (
              <button key={g} onClick={() => setScale(scale === g ? null : g)} className={`border px-3 py-1.5 font-mono text-[11px] tracking-[0.16em] transition-colors ${scale === g ? "border-signal bg-signal text-bg" : "border-ink-faint text-ink-dim hover:border-ink hover:text-ink"}`}>{g}</button>
            ))}
            {scale && <button onClick={() => setScale(null)} className="ml-2 font-mono text-[10px] uppercase tracking-[0.2em] text-ink-dim underline underline-offset-4 hover:text-ink">back to live</button>}
          </div>
        </section>
      </div>
    </Room>
  );
}
