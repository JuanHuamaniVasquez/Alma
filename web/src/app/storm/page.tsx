"use client";
import { useEffect, useState } from "react";
import { Room } from "@/components/Room";
import { Stamp } from "@/components/Stamp";
import { useAlma } from "@/components/Alma";
import { get, type Banner, type Entorno, type Frontera, type Scenario, type SpaceEvent } from "@/lib/api";

const SUN = [
  { id: "suvi195", name: "Corona · 195 Å", anim: true, note: "GOES-19 SUVI · hot plasma, ~1.2 million K" },
  { id: "suvi304", name: "Chromosphere · 304 Å", anim: true, note: "GOES-19 SUVI · cooler plasma, ~50,000 K" },
  { id: "lasco", name: "Coronagraph", anim: true, note: "SOHO LASCO C2 · outer corona; ejections of plasma drift outward" },
  { id: "rot", name: "Rotation · 14 days", anim: true, note: "SDO HMI · one frame per day at 12:00 UTC: sunspots travel across the disc as the Sun turns (≈25 days at its equator)" },
  { id: "hmi", name: "Surface · now", anim: false, note: "SDO HMI · one frame: sunspots change over days", live: "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMIIC.jpg", local: "/sun/latest_1024_HMIIC.jpg" },
] as const;
type Cuadro = { archivo: string; ts_utc: string; dir?: string };
const rutaCuadro = (c: Cuadro) => `${c.dir ?? "/sun/anim"}/${c.archivo}`;
const G1 = 5; // NOAA G1 (tormenta geomagnética menor): Kp ≥ 5. Regla de color: solo por encima de este umbral hay naranja (S-15).

/** 06 · THE STORM — «What is the Sun doing right now?» Sol real (NASA SDO) y Kp real (NOAA SWPC). Nada simulado en esta sala. */
export default function Storm() {
  const [ev, setEv] = useState<SpaceEvent[] | null>(null);
  const [banner, setBanner] = useState<Banner>("REAL");
  const [sun, setSun] = useState(0);
  const [src, setSrc] = useState<string>("");
  const [frames, setFrames] = useState<Record<string, Cuadro[]>>({});
  const [i, setI] = useState(0);
  const [play, setPlay] = useState(true);
  const [radiacion, setRadiacion] = useState(false);
  const [env, setEnvP] = useState<Entorno | null>(null);
  useEffect(() => { const l = () => get<Entorno>("/api/entorno/").then(setEnvP); l(); const id = setInterval(l, 60000); return () => clearInterval(id); }, []);
  const [scale, setScale] = useState<string | null>(null);        // null = en vivo; "G1"…"G5" = escenario SIMULADO
  const [sc, setSc] = useState<Scenario | null>(null);
  const { say } = useAlma();
  useEffect(() => { const l = () => get<{ banner: Banner; eventos: SpaceEvent[] }>("/api/tormenta/?tipo=lectura_clima_espacial&con=kp").then((d) => { setEv(d?.eventos ?? []); if (d) setBanner(d.banner); }); l(); const id = setInterval(l, 600000); return () => clearInterval(id); }, []);   // el servidor vuelve a leer SWPC cada 10 min
  useEffect(() => { Promise.all([fetch("/sun/anim/manifest.json").then((r) => r.json()).catch(() => ({ canales: {} })), fetch("/sun/rot/manifest.json").then((r) => r.json()).catch(() => ({ cuadros: [] }))])
      .then(([a, r]) => setFrames({ ...(a.canales ?? {}), rot: (r.cuadros ?? []).map((c: Cuadro) => ({ ...c, dir: "/sun/rot" })) })); }, []);
  const canal = SUN[sun];
  const cuadros = canal.anim ? (frames[canal.id] ?? []) : [];
  useEffect(() => { setI(0); setSrc(canal.anim ? "" : canal.live); }, [sun]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { if (!cuadros.length) return; cuadros.forEach((c) => { const im = new Image(); im.src = rutaCuadro(c); }); }, [cuadros.length, sun]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { if (!play || cuadros.length < 2) return; const t = setInterval(() => setI((k) => (k + 1) % cuadros.length), 170); return () => clearInterval(t); }, [play, cuadros.length]);
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
      <div className={`mx-auto grid h-full max-w-6xl grid-cols-[minmax(0,34rem)_1fr] items-center gap-14 px-10 pb-28 pt-14 ${radiacion ? "invisible" : ""}`}>
        <figure className="relative" style={{ width: "min(100%, calc(100vh - 22rem))" }}>
          <div className={`relative aspect-square w-full overflow-hidden rounded-full shadow-[0_0_120px_10px_rgb(255_120_40/.18)] transition-opacity duration-700 ${scale ? "opacity-35" : ""}`}>
            {/* hotlink al último SDO; si no hay red, la instantánea local con su marca de tiempo */}
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={canal.anim ? (cuadros[i] ? rutaCuadro(cuadros[i]) : "") : src} alt={`NASA/NOAA Sun, ${canal.name}`} onError={() => { if (!canal.anim) setSrc(canal.local); }} className="h-full w-full scale-[1.12] object-cover" />
          </div>
          <figcaption className="mt-5 flex flex-wrap items-center gap-x-4 gap-y-1 font-mono text-[10px] uppercase tracking-[0.16em] text-ink-faint">
            <span>{canal.note}</span><span className="text-ink-dim">{scale ? "real images from the last 24 h — not part of the scenario" : canal.anim ? (cuadros[i] ? `real time-lapse · ${cuadros[i].ts_utc.slice(0, 16).replace("T", " ")} UTC · ${canal.id === "rot" ? "last 14 days" : "last 24 h"}` : "loading…") : "latest frame (live link; local snapshot if offline)"}</span>
          </figcaption>
          <div className="mt-3 flex flex-wrap items-center gap-x-5 gap-y-1">
            {canal.anim && cuadros.length > 1 && <button onClick={() => setPlay(!play)} aria-label={play ? "Pause time-lapse" : "Play time-lapse"} className="border border-ink-faint px-2 py-0.5 font-mono text-[10px] uppercase tracking-[0.2em] text-ink-dim hover:text-ink">{play ? "❚❚ pause" : "▶ play"}</button>}
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
          {!scale && env?.niveles && (
            <div className="mt-5 border-l-2 pl-4" style={{ borderColor: env.hay_aviso ? "var(--color-signal)" : "var(--color-line)" }}>
              <p className="flex flex-wrap items-center gap-x-5 gap-y-1 font-mono text-[11px] uppercase tracking-[0.16em]">
                {(["S", "R", "G"] as const).map((k) => { const n = env.niveles![k]; return <span key={k} title={`${n.nombre}: ${n.valor} ${n.unidad} · ${n.regla}`} className={n.aviso ? "text-signal" : "text-ink-dim"}>{n.etiqueta} <span className="normal-case tracking-normal text-ink-faint">{n.nombre.toLowerCase()}</span></span>; })}
              </p>
              {env.avisos_noaa?.mensajes?.[0] && <p className="mt-1 text-[12px] leading-snug text-ink-dim">NOAA, {env.avisos_noaa.mensajes[0].ts_utc.slice(5, 16).replace("T", " ")} UTC: <em>{env.avisos_noaa.mensajes[0].titular}</em></p>}
            </div>
          )}
          <div className="mt-4"><Stamp banner={scale && sc ? sc.banner : banner} /></div>
          <div className="mt-8 flex flex-wrap items-center gap-3 border-t border-line pt-5">
            <span className="mr-2 font-mono text-[10px] uppercase tracking-[0.2em] text-ink-faint">What if — simulate</span>
            {["G1", "G2", "G3", "G4", "G5"].map((g) => (
              <button key={g} onClick={() => setScale(scale === g ? null : g)} className={`border px-3 py-1.5 font-mono text-[11px] tracking-[0.16em] transition-colors ${scale === g ? "border-signal bg-signal text-bg" : "border-ink-faint text-ink-dim hover:border-ink hover:text-ink"}`}>{g}</button>
            ))}
            <button onClick={() => setRadiacion(!radiacion)} aria-expanded={radiacion} className="ml-auto border border-ink-faint px-3 py-1.5 font-mono text-[11px] uppercase tracking-[0.16em] text-ink-dim hover:border-ink hover:text-ink">{radiacion ? "close ✕" : "Is the Sun the only radiation?"}</button>
            {scale && <button onClick={() => setScale(null)} className="ml-2 font-mono text-[10px] uppercase tracking-[0.2em] text-ink-dim underline underline-offset-4 hover:text-ink">back to live</button>}
          </div>
        </section>
      </div>
      {radiacion && <RadiationPanel onClose={() => setRadiacion(false)} env={env} />}
    </Room>
  );
}

function Spark({ v, umbral }: { v: number[]; umbral?: number }) {
  if (v.length < 2) return null;
  const lo = Math.min(...v, umbral ?? Infinity), hi = Math.max(...v, umbral ?? -Infinity), r = hi - lo || 1;
  const y = (x: number) => 30 - ((x - lo) / r) * 28 - 1;
  const d = v.map((x, i) => `${i ? "L" : "M"}${((i / (v.length - 1)) * 200).toFixed(1)},${y(x).toFixed(1)}`).join(" ");
  return (
    <svg viewBox="0 0 200 30" className="mt-2 h-8 w-full" preserveAspectRatio="none" aria-hidden>
      {umbral != null && <line x1="0" x2="200" y1={y(umbral)} y2={y(umbral)} stroke="var(--color-warn)" strokeDasharray="3 3" strokeWidth="0.8" />}
      <path d={d} fill="none" stroke="var(--color-ink)" strokeWidth="1.2" vectorEffect="non-scaling-stroke" />
    </svg>
  );
}

const fmt = (x: number | undefined, d = 1) => (x == null ? "—" : x.toLocaleString("en-US", { maximumFractionDigits: d }));

/** Respuesta honesta a «¿es el Sol la única radiación?»: no. Los valores en vivo vienen de /api/entorno/ (NOAA SWPC GOES y NMDB/Oulu); las referencias son literatura citada, no mediciones de ALMA. */
function RadiationPanel({ onClose, env }: { onClose: () => void; env: Entorno | null }) {
  const [fr, setFr] = useState<Frontera | null>(null);
  useEffect(() => { get<Frontera>("/api/frontera/").then(setFr); }, []);
  const f29 = fr?.fichas.find((f) => f.id === "FB-029")?.numeros;
  const p = env?.protones, e = env?.electrones, n = env?.neutrones;
  const filas = [
    { t: "Solar particle events", sub: "episodic · hours to days", ok: !!p?.disponible, que: "Protons accelerated by flares and shock waves. Rare, but the only source that can deliver a harmful dose quickly; NASA limits the dose from a single event to 250 mSv.",
      live: p?.disponible ? `${fmt(p.pfu, 2)} pfu now · S1 storm begins at ${p.umbral_s1_pfu} pfu · ${p.tormenta_s1_o_mas ? "STORM" : "quiet"}` : null, serie: p?.serie, umbral: p?.umbral_s1_pfu, fuente: "GOES protons ≥10 MeV · NOAA SWPC" },
    { t: "Trapped radiation (Earth's belts)", sub: "every orbit · South Atlantic Anomaly", ok: !!e?.disponible, que: "Protons and electrons held by Earth's magnetic field; for a crew in low orbit the South Atlantic Anomaly passes are a main part of the dose. We read the belts' ELECTRONS at geostationary orbit: a proxy of belt activity, not the dose inside the ISS.",
      live: e?.disponible ? `${fmt(e.pfu, 0)} pfu now · SWPC alert level ${fmt(e.umbral_swpc_pfu, 0)} pfu · ${e.alerta_swpc ? "ABOVE alert level" : "below"}` : null, serie: e?.serie, umbral: e?.umbral_swpc_pfu, fuente: "GOES electrons ≥2 MeV · NOAA SWPC" },
    { t: "Galactic cosmic rays", sub: "always on · strongest at solar minimum", ok: !!n?.disponible, que: "Fast protons and heavy nuclei from outside the solar system: a constant background that shielding stops poorly; it matters most beyond the magnetosphere. A ground neutron monitor sees their echo in the atmosphere: a proxy, not a dose.",
      live: n?.disponible ? `${fmt(n.cps, 1)} counts/s at ${n.estacion} · ${(n.variacion_pct ?? 0) >= 0 ? "+" : ""}${fmt(n.variacion_pct, 2)} % vs the 3-day median` : null, serie: n?.serie, umbral: undefined, fuente: "Neutron monitor · NMDB / University of Oulu" },
    { t: "Secondary radiation", sub: "inside the hull", ok: false, que: "Neutrons and fragments produced when the particles above hit the station walls and the body itself.", live: null, serie: undefined, umbral: undefined, fuente: "" },
  ];
  return (
    <aside role="dialog" aria-label="Space radiation sources" className="fixed inset-x-0 bottom-24 top-14 z-40 overflow-y-auto bg-bg px-6 py-8 md:px-14">
      <div className="mx-auto max-w-5xl">
        <div className="flex items-start justify-between gap-6">
          <h2 className="font-display text-[2.4rem] leading-tight text-ink">The Sun is not the only radiation.</h2>
          <button onClick={onClose} className="shrink-0 font-mono text-[11px] uppercase tracking-[0.2em] text-ink-dim underline underline-offset-4 hover:text-ink">close</button>
        </div>
        <p className="mt-3 max-w-3xl text-[15px] leading-relaxed text-ink-dim">A crew is exposed to four kinds. Three are read live below from real instruments; none of them is a dose measured inside a spacecraft, so ALMA shows the environment, not an exposure. The fourth is not modelled.</p>
        {env?.avisos_noaa?.mensajes && env.avisos_noaa.mensajes.length > 0 && (
          <div className="mt-6 border border-line p-5">
            <h3 className="font-mono text-[10px] uppercase tracking-[0.2em] text-ink-faint">What NOAA said in the last 72 hours · official text, not an ALMA detection</h3>
            <ul className="mt-3 space-y-1.5 text-[13.5px] text-ink-dim">
              {env.avisos_noaa.mensajes.map((m) => <li key={m.codigo + m.ts_utc}><span className="mr-3 font-mono text-[10.5px] text-ink-faint">{m.ts_utc.slice(5, 16).replace("T", " ")} UTC · {m.codigo}</span>{m.titular}</li>)}
            </ul>
            <p className="mt-3 font-mono text-[9.5px] uppercase tracking-[0.14em] text-ink-faint">source · NOAA SWPC alerts.json · raw reading sha256 {env.avisos_noaa.hash_lectura_cruda?.slice(0, 16)}…</p>
          </div>
        )}
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          {filas.map((f) => (
            <article key={f.t} className="border border-line p-5">
              <h3 className="font-display text-[1.35rem] text-ink">{f.t}</h3>
              <p className="mt-1 font-mono text-[10px] uppercase tracking-[0.16em] text-ink-faint">{f.sub}</p>
              <p className="mt-3 text-[14px] leading-relaxed text-ink-dim">{f.que}</p>
              {f.live ? (<><p className="mt-3 font-mono text-[11px] tracking-[0.04em] text-ink">{f.live}</p><Spark v={f.serie ?? []} umbral={f.umbral} /><p className="font-mono text-[9.5px] uppercase tracking-[0.14em] text-ink-faint">LIVE · REAL · {f.fuente}{f.umbral != null ? " · dashed = threshold" : ""}</p>
                {f.t === "Galactic cosmic rays" && f29 && <p className="mt-3 border-t border-line pt-3 text-[12.5px] leading-snug text-ink-dim">Sealed test FB-029: our CUSUM on this monitor caught {f29.sens_pct}% of {f29.n_eventos} severe storms (chance: {f29.azar_pct}%), a median {Math.abs(f29.adelanto_h)} h <em>after</em> the storm index reached storm level. It confirms a storm; it does not forecast one.</p>}</>)
                : <p className="mt-3 font-mono text-[10px] uppercase tracking-[0.14em] text-warn">{f.fuente ? "source unavailable right now — the absence is data" : "not modelled"}</p>}
            </article>
          ))}
        </div>
        <p className="mt-6 font-mono text-[10px] leading-relaxed tracking-[0.04em] text-ink-faint">
          Reference values (published, not measured by ALMA): career limit 600 mSv and 250 mSv per solar particle event, NASA-STD-3001 as summarised in the{" "}
          <a className="underline" href="https://www.nasa.gov/sites/default/files/atoms/files/radiation_protection_technical_brief_ochmo.pdf" target="_blank" rel="noreferrer">NASA OCHMO radiation brief</a>; an ISS crew receives roughly 80 mSv in six months at solar maximum and 160 mSv at solar minimum, per the{" "}
          <a className="underline" href="https://www.sidc.be/article/radiation-space" target="_blank" rel="noreferrer">Royal Observatory of Belgium (SIDC)</a>. {n?.reconocimiento}
        </p>
      </div>
    </aside>
  );
}
