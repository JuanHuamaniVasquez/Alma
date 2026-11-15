"use client";
import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import { Pager, usePaged } from "@/components/Pager";
import { Room } from "@/components/Room";
import { Stamp } from "@/components/Stamp";
import { get, type Astronautas, type Entorno, type Frontera, type Osdr, type Tierra } from "@/lib/api";

/** 09 · THE FRONTIER — lo que la nave sabe AHORA (datos reales NASA/NOAA), lo que NASA ya publicó de cuerpos de astronautas, y lo que probamos más allá del reto (con sus nulos). */
export default function Frontier() {
  const [env, setEnv] = useState<Entorno | null>(null);
  const [astro, setAstro] = useState<Astronautas | null>(null);
  const [osdr, setOsdr] = useState<Osdr | null>(null);
  const [fr, setFr] = useState<Frontera | null>(null);
  const [tierra, setTierra] = useState<Tierra | null>(null);
  useEffect(() => { get<Tierra>("/api/tierra/").then(setTierra); }, []);
  const trail = useRef<[number, number][]>([]);
  const [, bump] = useState(0);
  useEffect(() => {
    const load = () => get<Entorno>("/api/entorno/").then((d) => { if (d?.iss.disponible && d.iss.lat != null && d.iss.lon != null) { trail.current = [...trail.current.slice(-40), [d.iss.lon, d.iss.lat]]; } setEnv(d); bump((x) => x + 1); });
    load(); const id = setInterval(load, 30000);
    get<Astronautas>("/api/astronautas/").then(setAstro); get<Osdr>("/api/osdr/").then(setOsdr); get<Frontera>("/api/frontera/").then(setFr);
    return () => clearInterval(id);
  }, []);
  return (
    <Room voice="frontier" scroll hero="frontier" heroFocus="50% 14%">
      <div className="mx-auto max-w-6xl px-10 pb-24 pt-10">
        <h1 className="font-display text-5xl leading-tight">What the ship knows<br /><span className="text-ink-dim">right now, and what we dared to test.</span></h1>
        <p className="mt-4 max-w-2xl text-ink-dim">Three things on this page are real and from NASA or NOAA: live space around the crew, blood counts of real astronauts, and the catalogue of everything NASA has opened about spaceflown human bodies. The rest are experiments we sealed before running — including the ones that failed.</p>
        {env && <LiveEnvironment env={env} trail={trail.current} tierra={tierra} />}
        {astro?.ejecutada && <RealAstronauts a={astro} />}
        {osdr && <Atlas o={osdr} />}
        <Tiles fr={fr} />
        <Gaps />
      </div>
    </Room>
  );
}

function Section({ title, banner, children, id }: { title: string; banner?: "REAL" | "SIMULADO"; children: React.ReactNode; id?: string }) {
  return <section className="mt-16" id={id}><div className="flex items-baseline gap-4 border-b border-line pb-3"><h2 className="font-display text-3xl">{title}</h2>{banner && <Stamp banner={banner} />}</div>{children}</section>;
}

/* ---------- 1 · entorno en vivo ---------- */
function LiveEnvironment({ env, trail, tierra }: { env: Entorno; trail: [number, number][]; tierra: Tierra | null }) {
  const { iss, protones: p, rayosx: x, electrones: el, neutrones: nm } = env;
  return (
    <Section title="Live around the crew" banner={env.banner} id="live">
      <div className="mt-6 grid gap-8 lg:grid-cols-[1.35fr_1fr]">
        <div>
          {iss.disponible && iss.lat != null ? <IssMap iss={iss as Required<Pick<Entorno["iss"], "lat" | "lon" | "sol_lat" | "sol_lon">> & Entorno["iss"]} trail={trail} /> : <p className="font-mono text-xs uppercase tracking-widest text-ink-faint">ISS feed unavailable — nothing is filled in.</p>}
          {iss.disponible && <p className="mt-2 font-mono text-[11px] uppercase tracking-[0.16em] text-ink-dim">ISS · {iss.alt_km} km · {iss.vel_kms} km/s · <span style={{ color: iss.a_la_luz ? "#ffb45c" : "#9aa3b2" }}>{iss.a_la_luz ? "in sunlight — the crew sees day" : iss.visibilidad === "eclipsed" ? "in Earth's shadow — the crew sees night" : iss.visibilidad}</span></p>}
          <p className="mt-1 max-w-xl text-[12px] leading-snug text-ink-faint">The station circles Earth about every 90 minutes, so the crew lives through sixteen sunrises a day. That light cycle is the real driver of the Rhythm book.</p>
        </div>
        <div className="space-y-7">
          <div>
            <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-ink-faint">Energetic protons · GOES ≥10 MeV</p>
            {p.disponible && p.pfu != null ? (<>
              <p className="mt-1 font-display text-5xl leading-none">{p.pfu < 10 ? p.pfu.toFixed(2) : Math.round(p.pfu)}<span className="ml-2 font-mono text-[11px] text-ink-faint">pfu</span></p>
              <ProtonGauge pfu={p.pfu} />
              <p className="mt-1 text-[12px] text-ink-dim">{p.tormenta_s1_o_mas ? "A solar radiation storm (S1 or higher) is under way." : "Below the S1 radiation-storm threshold (10 pfu)."} Window peak {p.max_ventana_pfu?.toFixed(2)} pfu.</p>
            </>) : <p className="text-ink-faint">Unavailable.</p>}
          </div>
          <div>
            <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-ink-faint">Solar X-rays · flare class</p>
            {x.disponible ? <p className="mt-1 font-display text-5xl leading-none">{x.clase}<span className="ml-2 font-mono text-[11px] text-ink-faint">peak today {x.max_ventana}</span></p> : <p className="text-ink-faint">Unavailable.</p>}
          </div>
          <div>
            <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-ink-faint">Radiation belts · GOES electrons ≥2 MeV</p>
            {el?.disponible && el.pfu != null ? <p className="mt-1 font-display text-4xl leading-none">{Math.round(el.pfu).toLocaleString("en-US")}<span className="ml-2 font-mono text-[11px] text-ink-faint">pfu · {el.alerta_swpc ? "above" : "below"} the 1,000 pfu SWPC alert level</span></p> : <p className="text-ink-faint">Unavailable.</p>}
          </div>
          <div>
            <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-ink-faint">Cosmic rays · neutron monitor, Oulu</p>
            {nm?.disponible && nm.cps != null ? <p className="mt-1 font-display text-4xl leading-none">{nm.cps.toFixed(1)}<span className="ml-2 font-mono text-[11px] text-ink-faint">counts/s · {(nm.variacion_pct ?? 0) >= 0 ? "+" : ""}{nm.variacion_pct?.toFixed(2)} % vs 3-day median</span></p> : <p className="text-ink-faint">Unavailable.</p>}
            <p className="mt-1 text-[11px] leading-snug text-ink-faint">Proxies of the environment, not a dose measured on board. More in The Storm.</p>
          </div>
          {tierra?.disponible && tierra.imagen && (
            <figure className="flex items-center gap-4">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={tierra.imagen} alt="Earth as seen by NASA's EPIC camera" width={150} height={150} className="h-[150px] w-[150px] rounded-full object-cover" loading="lazy" />
              <figcaption className="text-[11px] leading-snug text-ink-faint"><span className="font-mono uppercase tracking-[0.16em] text-ink-dim">Earth, latest image</span><br />NASA EPIC camera on DSCOVR, 1.5 million km away · {tierra.fecha_utc?.slice(0, 16)} UTC</figcaption>
            </figure>
          )}
          <p className="text-[11px] leading-snug text-ink-faint">Sources: wheretheiss.at (orbit-derived position), NOAA SWPC GOES, NMDB / University of Oulu (neutron monitor). The ISS position is computed from orbital elements, not station telemetry. Updated every 30 s.</p>
        </div>
      </div>
    </Section>
  );
}

function useLand(): string[] {
  const [d, setD] = useState<string[]>([]);
  useEffect(() => { fetch("/data/land110.json").then((r) => r.json()).then((j: { polys: number[][][][] }) => setD(j.polys.map((p) => p.map((ring) => "M" + ring.map(([lo, la]) => `${((lo + 180) / 360 * 720).toFixed(1)},${((90 - la) / 180 * 360).toFixed(1)}`).join("L") + "Z").join(" ")))).catch((e) => console.warn("land110.json unavailable: the map shows no continents", e)); }, []);
  return d;
}

function IssMap({ iss, trail }: { iss: { lat: number; lon: number; sol_lat: number; sol_lon: number }; trail: [number, number][] }) {
  const W = 720, H = 360, X = (lon: number) => ((lon + 180) / 360) * W, Y = (lat: number) => ((90 - lat) / 180) * H;
  const night = useMemo(() => {                                // terminador: tan φ = −cos(λ−λ☉)/tan δ☉  (δ☉ = latitud subsolar)
    const d = Math.max(Math.abs(iss.sol_lat), 0.5) * Math.sign(iss.sol_lat || 1) * Math.PI / 180, pts: string[] = [];
    for (let lon = -180; lon <= 180; lon += 3) { const lat = Math.atan(-Math.cos(((lon - iss.sol_lon) * Math.PI) / 180) / Math.tan(d)) * 180 / Math.PI; pts.push(`${X(lon)},${Y(lat)}`); }
    const pole = iss.sol_lat > 0 ? Y(-90) : Y(90);
    return `${pts.join(" ")} ${X(180)},${pole} ${X(-180)},${pole}`;
  }, [iss.sol_lat, iss.sol_lon]);                              // eslint-disable-line react-hooks/exhaustive-deps
  const sol = ((iss.sol_lon + 180) % 360 + 360) % 360 - 180;
  const land = useLand();
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full border border-line bg-[#0f0d0b]" role="img" aria-label="Where the ISS is, with the day–night line">
      {land.map((d, i) => <path key={i} d={d} fill="#2a2620" stroke="#efe8da" strokeOpacity=".28" strokeWidth=".5" fillRule="evenodd" />)}
      <polygon points={night} fill="#000" opacity="0.58" />
      {[-150, -120, -90, -60, -30, 0, 30, 60, 90, 120, 150].map((l) => <line key={l} x1={X(l)} x2={X(l)} y1={0} y2={H} stroke="#efe8da" strokeOpacity=".07" />)}
      {[-60, -30, 0, 30, 60].map((l) => <line key={l} y1={Y(l)} y2={Y(l)} x1={0} x2={W} stroke="#efe8da" strokeOpacity={l === 0 ? 0.18 : 0.07} />)}
      <circle cx={X(sol)} cy={Y(iss.sol_lat)} r="7" fill="#ffb45c" /><text x={X(sol) + 11} y={Y(iss.sol_lat) + 4} fill="#ffb45c" fontSize="10" fontFamily="var(--font-mono)">SUN</text>
      {trail.length > 1 && <polyline points={trail.map(([lo, la]) => `${X(lo)},${Y(la)}`).join(" ")} fill="none" stroke="#efe8da" strokeOpacity=".5" strokeDasharray="2 3" />}
      <circle cx={X(iss.lon)} cy={Y(iss.lat)} r="9" fill="none" stroke="#efe8da" /><circle cx={X(iss.lon)} cy={Y(iss.lat)} r="3.5" fill="#efe8da" />
      <text x={X(iss.lon) + 13} y={Y(iss.lat) - 8} fill="#efe8da" fontSize="11" fontFamily="var(--font-mono)">ISS</text>
    </svg>
  );
}

function ProtonGauge({ pfu }: { pfu: number }) {
  const W = 360, lo = -1, hi = 5, X = (v: number) => ((Math.log10(Math.max(v, 0.1)) - lo) / (hi - lo)) * W;
  return (
    <svg viewBox={`0 0 ${W} 34`} className="mt-3 w-full max-w-sm" role="img" aria-label="Proton flux on a log scale against the S1 threshold">
      <rect x="0" y="12" width={W} height="6" fill="#efe8da" opacity=".12" /><rect x={X(10)} y="12" width={W - X(10)} height="6" fill="var(--color-signal)" opacity=".35" />
      <line x1={X(10)} x2={X(10)} y1="6" y2="24" stroke="var(--color-signal)" /><text x={X(10) + 4} y="9" fill="var(--color-signal)" fontSize="9" fontFamily="var(--font-mono)">S1 · 10 pfu</text>
      <circle cx={X(pfu)} cy="15" r="5" fill="#efe8da" />
      {[0.1, 1, 10, 100, 1000, 10000, 100000].map((v) => <text key={v} x={X(v)} y="32" fontSize="8" fill="#8a8174" textAnchor="middle" fontFamily="var(--font-mono)">{v >= 1000 ? `${v / 1000}k` : v}</text>)}
    </svg>
  );
}

/* ---------- 2 · astronautas reales (Inspiration4) ---------- */
const LINES: [string, string, string][] = [["abs_lymphocytes", "Lymphocytes", "#ffb45c"], ["abs_neutrophils", "Neutrophils", "#d98a8f"], ["nlr", "Neutrophil/lymphocyte ratio", "#9fbf9f"], ["wbc", "White cells", "#c9c1b2"], ["hb", "Haemoglobin", "#7f7a70"], ["plt", "Platelets", "#a99bd4"]];
function RealAstronauts({ a }: { a: Astronautas }) {
  const ts = a.tiempos ?? [], t = a.tabla ?? {};
  const W = 640, H = 230, L = 44, B = 28, X = (i: number) => L + (i / Math.max(ts.length - 1, 1)) * (W - L - 130), Y = (v: number) => H - B - ((v + 40) / 70) * (H - B - 14);
  const ends = LINES.map(([id]) => ({ id, y: Y(t[`${id}|${ts[ts.length - 1]}`]?.mediana_cambio_pct ?? 0) })).sort((a, b) => a.y - b.y);
  const labelY: Record<string, number> = {};
  ends.forEach((e, i) => { labelY[e.id] = Math.max(e.y + 3, i ? labelY[ends[i - 1].id] + 11 : 0); });                  // separa las etiquetas finales (≥ 11 px)
  const outside = Object.values(t).reduce((s, v) => s + v.arriba + v.abajo, 0), total = Object.values(t).reduce((s, v) => s + v.n - v.sin_datos - v.sospechoso, 0);
  return (
    <Section title="Real astronauts' blood" banner={a.banner} id="astronauts">
      <p className="mt-4 max-w-3xl text-ink-dim">Four real astronauts of the SpaceX Inspiration4 mission gave three blood samples before flight and four after landing — all public in NASA&apos;s open science archive (OSD-569). We treated each person like the ship treats its own crew: a personal baseline, then a band. Here is the median change from each person&apos;s own baseline.</p>
      <div className="mt-6 grid gap-8 lg:grid-cols-[1.4fr_1fr]">
        <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="Median change from personal baseline after landing">
          {[-40, -20, 0, 20].map((g) => <g key={g}><line x1={L} x2={W - 130} y1={Y(g)} y2={Y(g)} stroke="#efe8da" strokeOpacity={g === 0 ? 0.5 : 0.1} /><text x={L - 6} y={Y(g) + 3} textAnchor="end" fontSize="9" fill="#8a8174" fontFamily="var(--font-mono)">{g > 0 ? "+" : ""}{g}%</text></g>)}
          {ts.map((tt, i) => <text key={tt} x={X(i)} y={H - 8} textAnchor="middle" fontSize="10" fill="#8a8174" fontFamily="var(--font-mono)">{tt}</text>)}
          {(() => { return null; })()}
          {LINES.map(([id, name, col], li) => {
            const pts = ts.map((tt, i) => ({ i, v: t[`${id}|${tt}`]?.mediana_cambio_pct })).filter((p): p is { i: number; v: number } => p.v != null);
            const hi = id === "abs_lymphocytes";
            return <g key={id}><polyline fill="none" stroke={col} strokeWidth={hi ? 2.6 : 1.4} strokeOpacity={hi ? 1 : 0.75} points={pts.map((p) => `${X(p.i)},${Y(p.v)}`).join(" ")} />
              {pts.map((p) => <circle key={p.i} cx={X(p.i)} cy={Y(p.v)} r={hi ? 3.5 : 2} fill={col} />)}
              {pts.length > 0 && <text x={X(pts[pts.length - 1].i) + 8} y={labelY[id]} fontSize="9" fill={col} fontFamily="var(--font-mono)">{name.split(" ")[0]}</text>}</g>;
          })}
        </svg>
        <div className="space-y-4 text-[13px] leading-snug text-ink-dim">
          <p><span className="font-display text-4xl text-ink">{(t["abs_lymphocytes|R+1"]?.mediana_cambio_pct ?? 0) > 0 ? "+" : "−"}{Math.abs(Math.round(t["abs_lymphocytes|R+1"]?.mediana_cambio_pct ?? 0))}%</span> median change in lymphocytes on landing day…</p>
          <p><span className="font-display text-4xl text-ink">{outside} of {total}</span> person-measurements left their personal band. <em>Why?</em> With only three baseline samples the band is so wide it could not see a change that size. <strong className="text-ink">No alarm is not no effect</strong> — the rule the ship applies to itself everywhere.</p>
          {a.conciliacion && <p><span className="font-display text-4xl text-ink">{a.conciliacion.filas} of {a.conciliacion.de_filas}</span> blood counts did not add up with themselves (absolute count ≠ percentage × white cells): a likely data-entry error in a public NASA file, found just by checking the book against itself.</p>}
        </div>
      </div>
      <p className="mt-3 text-[11px] text-ink-faint">Sealed tests FB-024 (hash {a.hash_acta?.slice(0, 8)}…) and FB-025 (pooling the group's variation: bands about 30% narrower, floor still near ±70% — the same cards are in <Link href="/foundry" className="underline decoration-ink-faint hover:text-ink">The Foundry</Link>), predictions published even where wrong. Four civilians, none sampled in flight: a method case study, not a clinical finding. {a.aviso}</p>
    </Section>
  );
}

/* ---------- 3 · atlas OSDR ---------- */
function Atlas({ o }: { o: Osdr }) {
  const crew = o.estudios.filter((e) => e.tipo === "crew"), cells = o.n - crew.length;
  const [all, setAll] = useState(false);
  const shown0 = all ? o.estudios : crew;
  const pg = usePaged(shown0, 8);
  const shown = pg.slice;
  return (
    <Section title="What NASA has opened about spaceflown human bodies" banner="REAL" id="atlas">
      <p className="mt-4 max-w-3xl text-ink-dim">{o.n} studies in NASA&apos;s Open Science Data Repository involve human samples and spaceflight: {crew.length} come from crew (astronauts, mission simulations), {cells} are human cells or tissue flown to space. Nearly all are molecular — gene expression, proteins, microbiome. <strong className="text-ink">None is a continuous record of vital signs</strong>, which is why heart rate, glucose and pressure stay blocked here instead of being invented.</p>
      <div className="mt-4 flex gap-4 font-mono text-[10px] uppercase tracking-[0.18em]">
        {([[false, `Crew studies · ${crew.length}`], [true, `All · ${o.n}`]] as const).map(([k, t]) => <button key={t} onClick={() => { setAll(k); pg.reset(); }} aria-pressed={all === k} className={`border-b pb-0.5 ${all === k ? "border-ink text-ink" : "border-transparent text-ink-faint hover:text-ink-dim"}`}>{t}</button>)}
      </div>
      <ul className="mt-4 grid gap-x-8 gap-y-3 md:grid-cols-2">
        {shown.map((e) => (
          <li key={e.accession} className="border-t border-line pt-2">
            <a href={e.url} target="_blank" rel="noreferrer" className="font-mono text-[11px] uppercase tracking-[0.14em] text-ink-dim hover:text-ink">{e.accession}{e.mision ? ` · ${e.mision}` : ""}{e.liberado ? ` · ${e.liberado.slice(0, 4)}` : ""} ↗</a>
            <p className="mt-0.5 text-[13px] leading-snug">{e.titulo}</p>
            <p className="mt-0.5 font-mono text-[9px] uppercase tracking-[0.14em] text-ink-faint">{e.ensayos.slice(0, 3).join(" · ")}</p>
          </li>
        ))}
      </ul>
      <Pager {...pg} label="studies" />
      <p className="mt-3 text-[11px] text-ink-faint">Catalogue captured {o.capturado_utc.slice(0, 10)} from the OSDR search API. {o.nota}</p>
    </Section>
  );
}

/* ---------- 4 · lo que probamos (honesto) ---------- */
type Tile = { id: string; title: string; verdict: "held" | "failed" | "mixed" | "measured" | "open"; head: string; body: string; where: string; href: string; hash?: string | null };
function Tiles({ fr }: { fr: Frontera | null }) {
  const n = (id: string) => fr?.fichas.find((f) => f.id === id);
  const v = (id: string): Tile["verdict"] => n(id)?.verdict ?? "open";
  const x = (id: string, k: string) => n(id)?.numeros[k];
  const tiles: Tile[] = [
    { id: "FB-021", title: "An alarm with a guarantee", verdict: v("FB-021"), hash: n("FB-021")?.hash, head: x("FB-021", "fpr_s1_pct") != null ? `${x("FB-021", "fpr_s1_pct")}% false alarms, asked ≤1%` : "—", body: `A false-alarm bound that holds under daily peeking, tried on real wearables. Widening it until it holds costs sensitivity (${x("FB-021", "pot_s1_pct") ?? "?"}% → ${x("FB-021", "pot_elegido_pct") ?? "?"}% at 2σ).`, where: "Machine Room", href: "/machine" },
    { id: "FB-022", title: "Body or sensor?", verdict: v("FB-022"), hash: n("FB-022")?.hash, head: x("FB-022", "exactitud_pct") != null ? `classifier right ${x("FB-022", "exactitud_pct")}% of the time` : "—", body: `Temperature, breathing and HRV really do move with resting pulse out of sample. The rule to tell a broken sensor from a changed body flagged ${x("FB-022", "reales_marcados_pct") ?? "?"}% of untouched real data.`, where: "Notes in the Vault", href: "/vault" },
    { id: "FB-023", title: "Who is breathing extra?", verdict: v("FB-023"), hash: n("FB-023")?.hash, head: x("FB-023", "mejor_pct") != null ? `${x("FB-023", "mejor_pct")}% at best (simulated)` : "—", body: "Splitting the cabin's CO₂ into bodies works only if people sleep at different hours (chance when they sleep together), and is weaker than predicted.", where: "The Budget", href: "/budget" },
    { id: "ε", title: "Privacy as a budget", verdict: "measured", head: "5 people can't hide in an average", body: "With a crew of five, an exact average plus one subtraction names someone. Every number that leaves spends privacy; when it is gone, nothing more is published. Checked by a test, not by a sealed act.", where: "The Budget", href: "/budget" },
    { id: "FB-024", title: "Real astronauts' blood", verdict: v("FB-024"), hash: n("FB-024")?.hash, head: x("FB-024", "filas") != null ? `${x("FB-024", "filas")} of ${x("FB-024", "de")} blood counts don't add up` : "—", body: `A personal band on four real astronauts could not see a ${Math.abs(x("FB-024", "linfocitos_r1_pct") ?? 0)}% lymphocyte fall. Pooling the group's variation (FB-025) narrows it, yet the floor stays near ±${x("FB-025", "piso_linfocitos_pct") ?? "?"}%.`, where: "above", href: "#astronauts" },
    { id: "ECG", title: "Vitals monitor · real ECG", verdict: v("ECG"), head: x("ECG", "sensibilidad_pct") != null ? `${x("ECG", "sensibilidad_pct")}% of beats found` : "needs the local ECG file", body: `Our R-peak detector against ${x("ECG", "referencia")?.toLocaleString("en-US") ?? "?"} human-annotated beats of a real ECG: ${x("ECG", "hallados")?.toLocaleString("en-US") ?? "?"} found, none invented. Includes 'expected in flight' (with DOIs) and an Earth-link switch.`, where: "Medical Module", href: "/" },
  ];
  const col = { held: "#d8d0c0", failed: "var(--color-signal)", mixed: "#ffb45c", measured: "#c9c1b2", open: "#8a8174" } as const;
  const lab = { held: "all held", failed: "none held", mixed: "mixed", measured: "measured", open: "open" } as const;
  return (
    <Section title="What we tested beyond the brief" id="lab">
      <p className="mt-4 max-w-3xl text-ink-dim">Each idea was sealed with a hash before it ran. Numbers and labels below are read from the sealed record, not typed: <em>all held</em> = every hypothesis held, <em>none held</em> = none did, <em>mixed</em> = the rest. (No green here: green is reserved for receipts.)</p>
      <div className="mt-6 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
        {tiles.map((t) => (
          <article key={t.id} className="flex flex-col border border-line p-5">
            <div className="flex items-baseline justify-between"><span className="font-mono text-[10px] uppercase tracking-[0.2em] text-ink-faint">{t.id}{t.hash ? ` · ${t.hash}…` : ""}</span><span className="font-mono text-[10px] uppercase tracking-[0.2em]" style={{ color: col[t.verdict] }}>{lab[t.verdict]}</span></div>
            <h3 className="mt-2 font-display text-2xl leading-tight">{t.title}</h3>
            <p className="mt-2 font-display text-xl" style={{ color: col[t.verdict] }}>{t.head}</p>
            <p className="mt-2 flex-1 text-[13px] leading-snug text-ink-dim">{t.body}</p>
            {t.href.startsWith("#") ? <a href={t.href} className="mt-3 font-mono text-[10px] uppercase tracking-[0.18em] text-ink-faint hover:text-ink">See it · {t.where} →</a> : <Link href={t.href} className="mt-3 font-mono text-[10px] uppercase tracking-[0.18em] text-ink-faint hover:text-ink">See it · {t.where} →</Link>}
          </article>
        ))}
      </div>
    </Section>
  );
}

function Gaps() {
  return (
    <Section title="What nobody can open — and what we do instead">
      <ul className="mt-5 max-w-3xl space-y-3 text-[14px] leading-snug text-ink-dim">
        <li><strong className="text-ink">Continuous astronaut vitals.</strong> NASA does not publish heart-rate, glucose or blood-pressure streams of crew. Those indicators stay blocked; the monitor runs on a real ECG of a civilian patient, labelled as such.</li>
        <li><strong className="text-ink">A crewed habitat&apos;s air and water, person by person.</strong> No public record exists. The habitat is simulated, and every screen that uses it says so; its numbers come from NASA planning figures.</li>
        <li><strong className="text-ink">What we use instead:</strong> live space weather and the ISS orbit; real astronaut blood counts; NASA&apos;s published flight facts with citations; and wearable data of everyday people, always marked as not astronauts.</li>
      </ul>
    </Section>
  );
}
