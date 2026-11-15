/** La huella visual de un hash SHA-256: una rejilla simétrica de 5×5 cuyas celdas salen de los bits del propio hash. Si el hash cambia un solo bit, el dibujo cambia: es la misma información, mirable. */
export function HashArt({ hash, size = 44, title }: { hash: string; size?: number; title?: string }) {
  const bytes = hash.match(/../g)?.map((h) => parseInt(h, 16)) ?? [];
  const cells: number[] = [];
  for (let y = 0; y < 5; y++) for (let x = 0; x < 3; x++) cells.push(bytes[y * 3 + x] ?? 0);
  const tono = (bytes[15] ?? 0) % 2 ? "#ffb45c" : "#efe8da";
  const on = (x: number, y: number) => cells[y * 3 + (x < 3 ? x : 4 - x)] % 2 === 1;
  const c = size / 5;
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} role="img" aria-label={title ?? `Visual fingerprint of SHA-256 ${hash.slice(0, 8)}`} className="shrink-0 border border-line bg-black/30">
      {Array.from({ length: 25 }, (_, i) => { const x = i % 5, y = Math.floor(i / 5); return on(x, y) ? <rect key={i} x={x * c + 1} y={y * c + 1} width={c - 2} height={c - 2} fill={tono} opacity={0.85} /> : null; })}
    </svg>
  );
}
