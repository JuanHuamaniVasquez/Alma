"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { get, type LedgerDays } from "@/lib/api";
import { Stamp } from "./Stamp";
import { useShip } from "./Ship";

export const ROOMS = [
  { href: "/", n: "01", name: "Medical Module" },
  { href: "/kill", n: "02", name: "The Leak" },
  { href: "/vault", n: "03", name: "The Vault" },
  { href: "/foundry", n: "04", name: "The Foundry" },
] as const;

export function TopBar() {
  const path = usePathname(), router = useRouter();
  const [days, setDays] = useState<LedgerDays | null>(null);
  const { day } = useShip();
  useEffect(() => { get<LedgerDays>("/api/libro/dias/").then(setDays); }, []);
  useEffect(() => {
    const i = ROOMS.findIndex((r) => r.href === path);
    const h = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight" && i < ROOMS.length - 1) router.push(ROOMS[i + 1].href);
      if (e.key === "ArrowLeft" && i > 0) router.push(ROOMS[i - 1].href);
    };
    window.addEventListener("keydown", h); return () => window.removeEventListener("keydown", h);
  }, [path, router]);
  return (
    <header className="absolute inset-x-0 top-0 z-30 flex h-11 items-center justify-between border-b border-line bg-bg/80 px-5 backdrop-blur">
      <div className="flex items-baseline gap-8">
        <span className="font-display text-[1.65rem] leading-none tracking-wide">ALMA</span>
        <nav className="flex gap-6 font-mono text-[11px] uppercase tracking-[0.18em]">
          {ROOMS.map((r) => (
            <Link key={r.href} href={r.href} className={path === r.href ? "text-ink" : "text-ink-faint hover:text-ink-dim"}>
              <span className="mr-2 text-ink-faint">{r.n}</span>{r.name}
            </Link>
          ))}
        </nav>
      </div>
      <div className="flex items-center gap-4 font-mono text-[11px] uppercase tracking-[0.18em] text-ink-dim">
        {days?.ultimo != null ? <span>Day {day ?? days.ultimo}</span> : <span className="text-ink-faint">No ledger loaded</span>}
        {days && days.ultimo != null && <Stamp banner={days.banner} />}
      </div>
    </header>
  );
}
