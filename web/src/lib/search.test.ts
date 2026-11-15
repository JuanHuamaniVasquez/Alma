// node --experimental-strip-types --test src/lib/search.test.ts   (pnpm test:unit)
import test from "node:test";
import assert from "node:assert/strict";
import { closest, emptyFilters, normalize, parse, search, type Doc } from "./search.ts";

const D = (acta: string, title: string, outcome: Doc["outcome"], tags: string[], summary = "A long enough summary of the experiment and its result here.", extra: Partial<Doc> = {}): Doc =>
  ({ acta, ejecutada: outcome !== "not_run", title, summary, outcome, data: "real", tags, ...extra });
const DOCS: Doc[] = [
  D("FB-005", "The Conservation Loop (full run)", "not_run", ["conservation", "leak"], "Sealed, not yet run.", { data: "simulated" }),
  D("FB-005-D1", "The Leak demo", "sustained", ["leak", "demo"], "One day with a hidden leak.", { data: "simulated" }),
  D("FB-014", "Solar storms, sleep and HRV", "refuted", ["solar storm", "geomagnetic", "kp", "sleep", "hrv"]),
  D("FB-015-v2", "Rebuilt replication of 10 of 10", "partial", ["replication", "8 of 10"], "Detection reached 8 of 10.", { data: "simulated" }),
  D("FB-020", "Variance channel on real data", "refuted", ["variance", "false alarms", "zigzag"]),
  D("FB-020-v2", "Robust variance channel", "inconclusive", ["variance", "robust", "mad"]),
  D("FB-003R", "Three witnesses", "mixed", ["triangulation", "witnesses"], "Who is wrong, world, sensor or human?", { data: "simulated" }),
];

test("normaliza ids dichos o escritos de varias formas", () => {
  for (const s of ["FB-020", "fb 20", "F B zero two zero", "f b twenty", "FB020"]) assert.equal(normalize(s).includes("fb020") || normalize(s).includes("fb20"), true, s);
  assert.equal(normalize("F B zero zero five D one"), "fb005d1");
  assert.equal(normalize("fb 20 version two"), "fb20v2");
});

test("abrir un acta por su número, con y sin ceros y sufijos", () => {
  const id = (t: string) => { const i = parse(t, DOCS); return i.type === "open" ? i.id : i.type; };
  assert.equal(id("open FB-020"), "FB-020");
  assert.equal(id("F B zero two zero"), "FB-020");
  assert.equal(id("show me fb twenty version two"), "FB-020-v2");
  assert.equal(id("open F B zero zero five D one"), "FB-005-D1");
  assert.equal(id("fb three r"), "FB-003R");
  assert.equal(id("open fb 99"), null);                    // no existe: se dice, no se inventa
});

test("filtros por veredicto, estado y tipo de datos, hablados en lenguaje natural", () => {
  const f = (t: string) => { const i = parse(t, DOCS); assert.equal(i.type, "search"); return i.type === "search" ? i : null!; };
  assert.deepEqual(f("show refuted experiments").filters.outcome, ["refuted"]);
  assert.deepEqual(f("which ones failed").filters.outcome, ["refuted"]);
  assert.deepEqual(f("show me everything that was sustained on real data").filters, { outcome: ["sustained"], estado: null, data: "real" });
  assert.equal(f("what has not been run yet").filters.estado, "sealed");
  assert.deepEqual(f("simulated and refuted").filters, { outcome: ["refuted"], estado: null, data: "simulated" });
  assert.equal(f("find solar storms").query, "solar storms");
});

test("comandos: ayuda, limpiar, verificar, ir a una sala", () => {
  assert.equal(parse("what can I say", DOCS).type, "help");
  assert.equal(parse("clear", DOCS).type, "clear");
  assert.equal(parse("verify everything", DOCS).type, "verify");
  assert.deepEqual(parse("go to the foundry", DOCS), { type: "goto", room: "foundry" });
  assert.deepEqual(parse("take me to the storm", DOCS), { type: "goto", room: "storm" });
  assert.equal(parse("   ", DOCS).type, "empty");
});

test("búsqueda por tema con sinónimos y erratas, ordenada por relevancia", () => {
  const r = (q: string, f = emptyFilters()) => search(q, f, DOCS).map((h) => h.doc.acta);
  assert.equal(r("solar storms")[0], "FB-014");
  assert.equal(r("geomagnetic")[0], "FB-014");
  assert.equal(r("variance")[0] === "FB-020" || r("variance")[0] === "FB-020-v2", true);
  assert.equal(r("varience")[0] === "FB-020" || r("varience")[0] === "FB-020-v2", true);   // una errata
  assert.equal(r("storm")[0], "FB-014");                                                        // sinónimo storm → solar
  assert.equal(r("leak").slice(0, 2).sort().join(","), "FB-005,FB-005-D1");
  assert.deepEqual(r("", { ...emptyFilters(), outcome: ["refuted"] }).sort(), ["FB-014", "FB-020"]);
  assert.deepEqual(r("variance", { ...emptyFilters(), outcome: ["refuted"] }), ["FB-020"]);
});

test("sin coincidencias no inventa: devuelve vacío y, aparte, lo más parecido", () => {
  assert.deepEqual(search("xylophone banana", emptyFilters(), DOCS), []);
  assert.deepEqual(closest("zzzz", DOCS), []);
  assert.equal(closest("conservation of mas", DOCS)[0].acta, "FB-005");       // «lo más parecido» por trigramas
});
