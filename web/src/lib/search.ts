// Buscador de La Bóveda: puro (sin dependencias), determinista y probado (`pnpm test:unit`). Interpreta lo que se ESCRIBE o se DICE y lo convierte
// en una intención: buscar con filtros, abrir un acta, ir a una sala, verificar todo, limpiar o pedir ayuda. Lo que no entiende NO lo inventa.

export type Outcome = "refuted" | "sustained" | "mixed" | "inconclusive" | "partial" | "not_replicated" | "not_run" | "no_data";
export type Doc = { acta: string; ejecutada: boolean; title: string; summary: string; outcome: Outcome; data: string; tags: string[] };
export type Filters = { outcome: Outcome[]; estado: "executed" | "sealed" | null; data: "real" | "simulated" | null };
export type Intent =
  | { type: "search"; query: string; filters: Filters }
  | { type: "open"; id: string | null; spoken: string }
  | { type: "goto"; room: string }
  | { type: "verify" } | { type: "clear" } | { type: "help" } | { type: "empty" };
export type Hit = { doc: Doc; score: number };

export const OUTCOME_LABEL: Record<Outcome, string> = { refuted: "Refuted", sustained: "Sustained", mixed: "Mixed", inconclusive: "Inconclusive", partial: "Partial", not_replicated: "Not replicated", not_run: "Sealed, not run", no_data: "No data" };
export const ROOMS: Record<string, { path: string; words: string[] }> = {
  medical: { path: "/", words: ["medical module", "medical", "crew", "astronaut", "home"] }, machine: { path: "/machine", words: ["machine room", "machine", "residual"] },
  kill: { path: "/kill", words: ["the leak", "leak room", "kill demo", "demo"] }, vault: { path: "/vault", words: ["vault"] }, foundry: { path: "/foundry", words: ["foundry", "cards"] },
  storm: { path: "/storm", words: ["storm", "sun", "solar weather"] }, budget: { path: "/budget", words: ["budget", "ledger", "books"] }, capsule: { path: "/capsule", words: ["capsule", "capsules"] },
};

const NUMW: Record<string, string> = { zero: "0", oh: "0", one: "1", two: "2", three: "3", four: "4", five: "5", six: "6", seven: "7", eight: "8", nine: "9", ten: "10", eleven: "11", twelve: "12", thirteen: "13", fourteen: "14", fifteen: "15", sixteen: "16", seventeen: "17", eighteen: "18", nineteen: "19", twenty: "20" };
const STOP = new Set("a an the me my show find search for about with on of and or please can you could would give display list all any that were was which what who where is are to in at it its this these those experiment experiments act acts test tests result results one ones them there look looking want need tell see get open go take run ran into from".split(" "));
const SYN: Record<string, string[]> = {
  storm: ["solar", "geomagnetic", "kp", "space", "weather"], storms: ["solar", "geomagnetic", "kp", "space", "weather"], solar: ["geomagnetic", "kp", "storm"], sun: ["solar", "geomagnetic"],
  heart: ["pulse", "hrv", "heart"], pulse: ["heart", "hrv"], hrv: ["heart", "variability"], tired: ["tiredness", "fatigue"], fatigue: ["tiredness"], sleeping: ["sleep"], slept: ["sleep"],
  mood: ["tension", "anxiety", "self-report"], stress: ["tension", "anxiety"], leaks: ["leak"], leaking: ["leak"], conservation: ["mass", "balance"], mass: ["conservation", "balance"],
  fail: ["refuted"], failed: ["refuted"], failures: ["refuted"], failure: ["refuted"], wrong: ["refuted"], negative: ["refuted"], null: ["refuted"], worked: ["sustained"], passed: ["sustained"], confirmed: ["sustained"],
  fake: ["replication", "adversary"], cheat: ["adversary"], evade: ["adversary", "evasion"], hidden: ["leak", "blind"], water: ["water", "flow"],
};

export function emptyFilters(): Filters { return { outcome: [], estado: null, data: null }; }
export const hasFilters = (f: Filters) => f.outcome.length > 0 || f.estado !== null || f.data !== null;

const strip = (s: string) => s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
/** Normaliza lo escrito o dicho: minúsculas, sin acentos, signos fuera, «F B zero two zero» → «fb 020». */
export function normalize(raw: string): string {
  let t = strip(raw).replace(/[^a-z0-9\s-]/g, " ").replace(/\bf\s*b\b/g, "fb").replace(/\bfb\s*-\s*/g, "fb ");
  t = t.split(/\s+/).map((w) => (NUMW[w] ?? w)).join(" ");
  // «fb 0 2 0» o «fb 20» o «fb 5 d 1» → ids compactos
  t = t.replace(/\bfb\s+((?:\d\s*)+)(?=\b)/g, (_, d: string) => "fb" + d.replace(/\s+/g, ""));
  t = t.replace(/\b(fb\d+)\s*(?:-|\s)?\s*(d\s*1|d1)\b/g, "$1d1").replace(/\b(fb\d+)\s*(?:-|\s)?\s*(v\s*2|v2|version\s*2)\b/g, "$1v2").replace(/\b(fb\d+)\s+r\b/g, "$1r");
  return t.replace(/\s+/g, " ").trim();
}

const idKey = (acta: string) => { const m = acta.toLowerCase().match(/^fb-(\d+)(?:-(d1|v2)|(r))?$/); return m ? `fb${parseInt(m[1], 10)}${m[2] ?? m[3] ?? ""}` : acta.toLowerCase(); };
/** Busca el acta por el id dicho/escrito (tolera ceros: «fb 20» = FB-020). Sin sufijo: la base, y si no existe, la única que empiece así. */
export function findId(norm: string, docs: Doc[]): { id: string | null; spoken: string } | null {
  const m = norm.match(/\bfb(\d+)(d1|v2|r)?\b/);
  if (!m) return null;
  const spoken = `FB-${m[1].padStart(3, "0")}${m[2] ? (m[2] === "d1" ? "-D1" : m[2] === "v2" ? "-v2" : "R") : ""}`;
  const key = `fb${parseInt(m[1], 10)}${m[2] ?? ""}`;
  const exact = docs.find((d) => idKey(d.acta) === key);
  if (exact) return { id: exact.acta, spoken };
  if (!m[2]) { const prefix = docs.filter((d) => idKey(d.acta).startsWith(key)); if (prefix.length === 1) return { id: prefix[0].acta, spoken }; }
  return { id: null, spoken };
}

function roomIn(norm: string): string | null {
  for (const [k, r] of Object.entries(ROOMS)) for (const w of r.words) if (new RegExp(`\\b${w}\\b`).test(norm)) return k;
  return null;
}

export function parse(raw: string, docs: Doc[]): Intent {
  const n = normalize(raw);
  if (!n) return { type: "empty" };
  if (/\b(help|what can i say|what can you do|commands)\b/.test(n)) return { type: "help" };
  if (/^(please )?(clear|reset|start over|show (me )?(all|everything|the whole vault)|everything|all|whole vault)( filters| search)?$/.test(n)) return { type: "clear" };   // solo si es TODO lo que se dijo
  if (/\b(verify|recompute|check)\b.*\b(all|every|everything|hashes|hash|yourself)\b|\bverify\b/.test(n) && !/\bfb\d/.test(n)) return { type: "verify" };
  const id = findId(n, docs);
  if (id && /\b(open|show|go|take|display|read|tell|what is|explain|about)\b|^fb\d/.test(n) && n.replace(/\bfb\d+(d1|v2|r)?\b/, "").split(" ").filter((w) => w && !STOP.has(w)).length === 0) return { type: "open", ...id };
  if (/\b(go to|take me|open|navigate|switch to)\b/.test(n)) { const r = roomIn(n); if (r && r !== "vault") return { type: "goto", room: r }; }
  const f = emptyFilters();
  let rest = ` ${n} `;
  const take = (re: RegExp, fn: () => void) => { if (re.test(rest)) { fn(); rest = rest.replace(re, " "); } };
  take(/\bnot replicated\b|\bdid not replicate\b/g, () => f.outcome.push("not_replicated"));
  take(/\b(not (yet )?(been )?(run|executed|ran)( yet)?|sealed|pending|unrun|never ran|have not run|has not run)\b/g, () => { f.estado = "sealed"; });
  take(/\b(refuted|refute|refutes|failed|failures?|negative results?|nulls?)\b/g, () => f.outcome.push("refuted"));
  take(/\b(sustained|confirmed|worked|passed|successes?|successful)\b/g, () => f.outcome.push("sustained"));
  take(/\b(mixed)\b/g, () => f.outcome.push("mixed"));
  take(/\b(inconclusive|unclear|undecided)\b/g, () => f.outcome.push("inconclusive"));
  take(/\b(partial|partially)\b/g, () => f.outcome.push("partial"));
  take(/\b(executed|already ran|completed|finished)\b/g, () => { f.estado = "executed"; });
  take(/\b(real data|real|actual)\b/g, () => { f.data = "real"; });
  take(/\b(simulated|simulation|synthetic)\b/g, () => { f.data = "simulated"; });
  const words = rest.split(/\s+/).filter((w) => w && !STOP.has(w));
  return { type: "search", query: words.join(" "), filters: f };
}

const tokens = (s: string) => strip(s).replace(/[^a-z0-9\s-]/g, " ").split(/\s+/).filter(Boolean);
function lev(a: string, b: string, max: number): number {
  if (Math.abs(a.length - b.length) > max) return max + 1;
  let prev = Array.from({ length: b.length + 1 }, (_, i) => i);
  for (let i = 1; i <= a.length; i++) { const cur = [i]; let best = i; for (let j = 1; j <= b.length; j++) { cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1)); best = Math.min(best, cur[j]); } if (best > max) return max + 1; prev = cur; }
  return prev[b.length];
}
const docTokens = (d: Doc) => ({ strong: new Set(tokens(`${d.title} ${d.tags.join(" ")} ${d.acta}`)), weak: new Set(tokens(`${d.summary} ${OUTCOME_LABEL[d.outcome]} ${d.data}`)) });
function termScore(term: string, t: { strong: Set<string>; weak: Set<string> }): number {
  let best = 0;
  for (const [set, w] of [[t.strong, 1], [t.weak, 0.55]] as const)
    for (const tok of set) {
      let s = 0;
      if (tok === term) s = 3; else if (term.length >= 3 && (tok.startsWith(term) || (tok.length >= 4 && term.startsWith(tok)))) s = 2;
      else if (term.length >= 5 && lev(term, tok, 1) <= 1) s = 1.6; else if (term.length >= 8 && lev(term, tok, 2) <= 2) s = 1.1;
      best = Math.max(best, s * w);
    }
  return best;
}

export function passes(d: Doc, f: Filters): boolean {
  if (f.outcome.length && !f.outcome.includes(d.outcome) && !(f.outcome.includes("not_run") && d.outcome === "no_data")) return false;
  if (f.estado === "executed" && !d.ejecutada) return false;
  if (f.estado === "sealed" && d.ejecutada) return false;
  if (f.data === "real" && !d.data.includes("real")) return false;
  if (f.data === "simulated" && !d.data.includes("simulated")) return false;
  return true;
}

/** Filtra y ordena por relevancia. Con consulta: exige al menos un término que case (exacto, prefijo o con una errata). Sin consulta: solo filtros. */
export function search(query: string, f: Filters, docs: Doc[]): Hit[] {
  const base = docs.filter((d) => passes(d, f));
  const terms = tokens(query);
  if (!terms.length) return base.map((doc) => ({ doc, score: 0 }));
  const out: Hit[] = [];
  for (const doc of base) {
    const t = docTokens(doc);
    let total = 0, matched = 0;
    for (const term of terms) {
      let s = termScore(term, t);
      for (const syn of SYN[term] ?? []) s = Math.max(s, termScore(syn, t) * 0.8);
      if (s > 0) { matched++; total += s; }
    }
    if (matched > 0) out.push({ doc, score: total + matched });
  }
  return out.sort((a, b) => b.score - a.score || a.doc.acta.localeCompare(b.doc.acta));
}

/** «Lo más parecido» cuando no hay coincidencias: similitud de trigramas entre la consulta y el texto de cada acta (sin filtros, para no devolver vacío). */
export function closest(query: string, docs: Doc[], n = 3): Doc[] {
  const tri = (s: string) => { const t = ` ${strip(s).replace(/[^a-z0-9]+/g, " ")} `; const set = new Set<string>(); for (let i = 0; i < t.length - 2; i++) set.add(t.slice(i, i + 3)); return set; };
  const q = tri(query);
  if (q.size < 3) return [];
  return docs.map((d) => { const x = tri(`${d.title} ${d.tags.join(" ")}`); let inter = 0; q.forEach((g) => { if (x.has(g)) inter++; }); return { d, s: inter / Math.sqrt(q.size * x.size) }; })
    .filter((r) => r.s > 0.12).sort((a, b) => b.s - a.s).slice(0, n).map((r) => r.d);
}
