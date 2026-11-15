"use client";
import { useState } from "react";

/** Paginación mínima y accesible: «‹ 2/5 ›». `usePaged` parte una lista en páginas y recuerda la actual (vuelve a 1 si cambia el filtro). */
export function usePaged<T>(items: T[], size: number) {
  const [page, setPage] = useState(0);
  const pages = Math.max(1, Math.ceil(items.length / size));
  const cur = Math.min(page, pages - 1);
  return { slice: items.slice(cur * size, cur * size + size), page: cur, pages, setPage, total: items.length, reset: () => setPage(0) };
}

export function Pager({ page, pages, setPage, total, label = "items" }: { page: number; pages: number; setPage: (p: number) => void; total: number; label?: string }) {
  if (pages <= 1) return <p className="mt-3 font-mono text-[10px] uppercase tracking-[0.16em] text-ink-faint">{total} {label}</p>;
  const btn = "px-2 py-0.5 text-ink-dim transition-colors hover:text-ink disabled:opacity-25 disabled:hover:text-ink-dim";
  return (
    <nav className="mt-3 flex items-center gap-1 font-mono text-[10px] uppercase tracking-[0.16em] text-ink-faint" aria-label={`${label} pages`}>
      <button className={btn} disabled={page === 0} onClick={() => setPage(page - 1)} aria-label="Previous page">‹</button>
      <span aria-live="polite">{page + 1} / {pages}</span>
      <button className={btn} disabled={page >= pages - 1} onClick={() => setPage(page + 1)} aria-label="Next page">›</button>
      <span className="ml-2 normal-case tracking-normal">{total} {label}</span>
    </nav>
  );
}
