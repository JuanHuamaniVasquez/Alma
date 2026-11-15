import Link from "next/link";

export default function NotFound() {
  return (
    <div className="absolute inset-0 grid place-items-center">
      <div className="text-center">
        <p className="font-display text-7xl">No such room.</p>
        <p className="mt-3 font-mono text-[11px] uppercase tracking-[0.25em] text-ink-faint">The ship has eight rooms. This is not one of them.</p>
        <Link href="/" className="mt-8 inline-block border border-ink-dim px-4 py-2 font-mono text-[11px] uppercase tracking-[0.2em] hover:border-ink">Back to the Medical Module</Link>
      </div>
    </div>
  );
}
