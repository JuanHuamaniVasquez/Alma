"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { get, type Entorno, type LedgerDays } from "@/lib/api";
import { Stamp } from "./Stamp";
import { useShip } from "./Ship";

export const ROOMS = [
  { href: "/", n: "01", name: "Medical Module" },
  { href: "/machine", n: "02", name: "Machine Room" },
  { href: "/kill", n: "03", name: "The Leak" },
  { href: "/vault", n: "04", name: "The Vault" },
  { href: "/foundry", n: "05", name: "The Foundry" },
  { href: "/storm", n: "06", name: "The Storm" },
  { href: "/budget", n: "07", name: "The Budget" },
  { href: "/capsule", n: "08", name: "The Capsule" },
  { href: "/frontier", n: "09", name: "The Frontier" },
] as const;

const LEDGER_ROOMS = ["/", "/machine", "/kill", "/budget"]; // salas que muestran el universo simulado del hábitat; las demás llevan su propio sello

/** Cuatro grupos en vez de nueve enlaces sueltos: el qué-es-cada-cosa se lee de un vistazo. */
const GROUPS: { name: string; blurb: string; rooms: (typeof ROOMS)[number]["href"][] }[] = [
  { name: "Crew", blurb: "The five people and their bodies", rooms: ["/"] },
  { name: "Ship", blurb: "The habitat's books and engine", rooms: ["/machine", "/kill", "/budget"] },
  { name: "World", blurb: "What is happening around the crew", rooms: ["/storm", "/frontier"] },
  { name: "Lab", blurb: "Hypotheses, sealed records, results", rooms: ["/foundry", "/vault", "/capsule"] },
];
const roomOf = (href: string) => ROOMS.find((r) => r.href === href)!;

export function TopBar() {
  const path = usePathname(), router = useRouter();
  const [days, setDays] = useState<LedgerDays | null>(null);
  const { day } = useShip();
  const [checked, setChecked] = useState(false);
  const [live, setLive] = useState<boolean | null>(null);
  const [open, setOpen] = useState<string | null>(null);
  useEffect(() => { get<Entorno>("/api/entorno/").then((d) => setLive(!!d && (d.iss.disponible || d.protones.disponible))); }, []);
  useEffect(() => { get<LedgerDays>("/api/libro/dias/").then((d) => { setDays(d); setChecked(true); }); }, []);
  useEffect(() => { setOpen(null); }, [path]);
  useEffect(() => {
    const h = (e: KeyboardEvent) => {
      const i = ROOMS.findIndex((r) => r.href === window.location.pathname);          // se lee en el momento: una pulsación justo tras navegar no usa una ruta vieja
      if (e.key === "Escape") setOpen(null);
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      if (e.key === "ArrowRight" && i < ROOMS.length - 1) router.push(ROOMS[i + 1].href);
      if (e.key === "ArrowLeft" && i > 0) router.push(ROOMS[i - 1].href);
    };
    const c = (e: MouseEvent) => { if (!(e.target as HTMLElement).closest("[data-nav]")) setOpen(null); };
    window.addEventListener("keydown", h); window.addEventListener("click", c);
    return () => { window.removeEventListener("keydown", h); window.removeEventListener("click", c); };
  }, [path, router]);
  const here = GROUPS.find((g) => g.rooms.includes(path as never));
  return (
    <header className="absolute inset-x-0 top-0 z-40 flex h-11 items-center justify-between border-b border-line bg-bg/85 px-5 backdrop-blur" data-nav>
      <div className="flex items-baseline gap-7">
        <Link href="/" className="font-display text-[1.65rem] leading-none tracking-wide">ALMA</Link>
        <nav className="flex items-baseline gap-6 whitespace-nowrap font-mono text-[11px] uppercase tracking-[0.18em]" aria-label="Rooms">
          {GROUPS.map((g) => {
            const active = g === here, single = g.rooms.length === 1;
            if (single) return <Link key={g.name} href={g.rooms[0]} className={active ? "text-ink" : "text-ink-faint hover:text-ink-dim"}>{g.name}</Link>;
            return (
              <div key={g.name} className="relative">
                <button onClick={() => setOpen(open === g.name ? null : g.name)} aria-expanded={open === g.name} aria-haspopup="true" className={`${active ? "text-ink" : "text-ink-faint hover:text-ink-dim"} flex items-baseline gap-1.5 uppercase`}>
                  {g.name}<span aria-hidden className="text-[8px]">{open === g.name ? "▲" : "▼"}</span>
                  {active && <span className="hidden text-ink-dim normal-case tracking-normal lg:inline">· {roomOf(path).name.replace(/^The /, "")}</span>}
                </button>
                {open === g.name && (
                  <ul className="absolute left-0 top-7 z-50 w-64 border border-line bg-[#14110e]/98 py-2 shadow-[0_18px_40px_-10px_rgb(0_0_0/.8)]" role="menu">
                    <li className="px-4 pb-2 text-[9px] tracking-[0.16em] text-ink-faint">{g.blurb}</li>
                    {g.rooms.map((h) => { const r = roomOf(h); return (
                      <li key={h} role="none"><Link href={h} role="menuitem" className={`block px-4 py-2 hover:bg-white/5 ${path === h ? "text-ink" : "text-ink-dim"}`}><span className="mr-3 text-ink-faint">{r.n}</span>{r.name}</Link></li>); })}
                  </ul>
                )}
              </div>
            );
          })}
        </nav>
      </div>
      <div className="flex items-center gap-3 whitespace-nowrap font-mono text-[10px] uppercase tracking-[0.14em] text-ink-dim">
        {checked && !days && <span className="text-signal" title="Start the backend: uv run python backend/manage.py runserver">API offline</span>}
        {LEDGER_ROOMS.includes(path) && days && days.ultimo != null && <span className="hidden -rotate-1 border border-warn px-1.5 py-[1px] font-medium tracking-[0.16em] text-warn md:inline-block" title={`The habitat's air and water are a simulated universe · day ${day ?? days.ultimo}`}>Habitat simulated · day {day ?? days.ultimo}</span>}
        {live && <span className="inline-block border border-ok px-1.5 py-[1px] font-medium tracking-[0.16em] text-ok" title="Live NASA/NOAA feeds: ISS orbit, GOES protons and X-rays">● Live</span>}
      </div>
    </header>
  );
}
