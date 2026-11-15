// Prueba de humo de extremo a extremo con clics reales (Chrome local sin interfaz). Requiere API :8000 y vitrina :3000 en marcha.
// El POST del ánimo se INTERCEPTA: esta prueba no escribe en la base. Uso:  node e2e/smoke.mjs   (o: pnpm e2e)
import puppeteer from "puppeteer-core";

const BASE = process.env.BASE ?? "http://localhost:3000";
const fallos = [], ok = [];
const check = (nombre, cond, extra = "") => (cond ? ok.push(nombre) : fallos.push(`${nombre} ${extra}`.trim()));
const dormir = (ms) => new Promise((r) => setTimeout(r, ms));

const browser = await puppeteer.launch({
  executablePath: process.env.CHROME ?? "/usr/bin/google-chrome", headless: "new",
  args: ["--no-sandbox", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--window-size=1440,900"],
});
const page = await browser.newPage();
await page.setViewport({ width: 1440, height: 900 });
const errores = [];
page.on("pageerror", (e) => errores.push(String(e)));
page.on("console", (m) => { if (m.type() === "error" && !/Failed to load resource|favicon|net::ERR/.test(m.text())) errores.push(m.text()); });
await page.evaluateOnNewDocument(() => {                         // registra cada reproducción de audio y si el navegador la aceptó
  window.__audio = [];
  const play = HTMLMediaElement.prototype.play;
  HTMLMediaElement.prototype.play = function () {
    const r = play.call(this);
    r.then(() => window.__audio.push({ src: this.src, ok: true }), (e) => window.__audio.push({ src: this.src, ok: false, e: String(e) }));
    return r;
  };
});
await page.evaluateOnNewDocument(() => {                         // SpeechRecognition falso: devuelve lo que se le pida en window.__say
  class FakeSR { start() { setTimeout(() => { const t = window.__say ?? ""; this.onresult?.({ results: [Object.assign([{ transcript: t }], { isFinal: true })] }); this.onend?.(); }, 150); } stop() { this.onend?.(); } }
  window.webkitSpeechRecognition = FakeSR; window.SpeechRecognition = FakeSR;   // Chrome recientes exponen también el nombre estándar
});
let enviado = null;
await page.setRequestInterception(true);
page.on("request", (req) => {
  if (req.method() === "POST" && req.url().endsWith("/api/animo/")) { enviado = JSON.parse(req.postData() ?? "{}"); req.respond({ status: 201, contentType: "application/json", body: '{"ok":true}' }); } else req.continue();
});
const esperar = (sel, t = 60000) => page.waitForSelector(sel, { timeout: t });
const texto = () => page.evaluate(() => document.body.innerText);
const esperarTexto = (txt, t = 30000) => page.waitForFunction((x) => document.body.innerText.toLowerCase().includes(x.toLowerCase()), { timeout: t }, txt);   // innerText ya trae las mayúsculas del CSS
const clicTexto = (tag, t) => page.evaluate((tag, t) => { const el = [...document.querySelectorAll(tag)].find((e) => e.textContent.trim().toLowerCase().startsWith(t.toLowerCase())); if (!el) return false; el.click(); return true; }, tag, t);

// 1 · puerta de ALMA y primera voz
await page.goto(BASE, { waitUntil: "domcontentloaded" });
await esperar('button[aria-label^="Wake ALMA"]');
await page.click('button[aria-label^="Wake ALMA"]');
await page.waitForFunction(() => !document.querySelector('button[aria-label^="Wake ALMA"]'), { timeout: 20000 });
check("la puerta se abre con un clic", true);
await esperar("p[aria-live]", 30000);
await page.waitForFunction(() => (document.querySelector("p[aria-live]")?.textContent.length ?? 0) > 20, { timeout: 15000 }).then(() => check("ALMA muestra su subtítulo", true), () => check("ALMA muestra su subtítulo", false));   // el subtítulo crece con el audio: con carga alta tarda
await page.waitForFunction(() => window.__audio.some((a) => a.ok && a.src.includes("/voice/")), { timeout: 15000 }).catch(() => {});
const audio = await page.evaluate(() => window.__audio);
check("el audio de ALMA arranca tras el clic (política de autoplay)", audio.some((a) => a.ok && a.src.includes("/voice/")), JSON.stringify(audio));

// 2 · navegación con flechas
await page.keyboard.press("ArrowRight");
await page.waitForFunction(() => location.pathname === "/machine", { timeout: 8000 });
check("la flecha derecha va a Machine Room", true);
await page.keyboard.press("ArrowLeft");
await page.waitForFunction(() => location.pathname === "/", { timeout: 8000 });

// 2b · la tripulación de 5: elegir, dentro / fuera
await page.waitForFunction(() => document.querySelectorAll('nav[aria-label="Crew"] ul button').length === 5, { timeout: 15000 }).catch(() => {});   // el roster llega de la API
const nCrew = await page.$$eval('nav[aria-label="Crew"] ul button', (b) => b.length);
check("la tripulación muestra 5 personajes", nCrew === 5, String(nCrew));
await page.evaluate(() => document.querySelectorAll('nav[aria-label="Crew"] ul button')[1].click());
await page.waitForFunction(() => document.querySelectorAll('nav[aria-label="Crew"] ul button')[1].getAttribute("aria-pressed") === "true", { timeout: 25000 });
await clicTexto("button", "Outside");
await esperarTexto("NASA Z-2 prototype suit", 8000);
check("«Outside» cambia al traje Z-2 y sigue rotulado «not a real person»", (await texto()).toLowerCase().includes("not a real person"));
await clicTexto("button", "Inside");
await esperarTexto("Generated fictional character", 8000);

// 3 · figura humana: modo Body, ánimo en 3 toques
await clicTexto("button", "Body");
await page.waitForSelector('button[aria-label^="Mood"]', { timeout: 20000 });
await page.evaluate(() => document.querySelector('button[aria-label^="Mood"]').click());
await esperarTexto("How do you feel right now?", 8000);
check("el marcador Mood abre su recibo", true);
const antes = await page.$eval('button[disabled], button:disabled', (e) => e.textContent.trim().toLowerCase()).catch(() => "");
check("«Send» está desactivado hasta elegir un valor", antes.startsWith("send"));
await dormir(700);
await page.evaluate(() => document.querySelector('[role="radio"][title="Good"]').click());   // clic de DOM: el recibo se anima (inclinado y recortado) y un clic por coordenadas puede errar
await page.waitForFunction(() => { const b = [...document.querySelectorAll("button")].find((x) => x.textContent.trim() === "Send"); return b && !b.disabled; }, { timeout: 5000 });   // esperar a que el valor elegido habilite «Send»
await page.evaluate(() => [...document.querySelectorAll("button")].find((b) => b.textContent.trim() === "Send").click());
await esperarTexto("Saved.", 8000);
check("el ánimo se envía con valor 4 y duración medida > 0", enviado?.valor === 4 && enviado.duracion_respuesta_s > 0 && /^crew-[0-9a-f]{8}$/.test(enviado.persona_id), JSON.stringify(enviado));
const hablo0 = (await page.evaluate(() => window.__audio)).length;
await page.evaluate(() => document.querySelector('button[aria-label^="Heart rate"]').click());
await page.waitForFunction((n) => window.__audio.length > n, { timeout: 15000 }, hablo0).then(() => check("tocar el marcador de frecuencia cardíaca hace hablar a ALMA", true), () => check("tocar el marcador de frecuencia cardíaca hace hablar a ALMA", false));
await esperarTexto("people with a baseline", 8000);
const t = await texto();
check("el recibo de frecuencia cardíaca declara su límite conocido", t.toLowerCase().includes("known limit") && t.toLowerCase().includes("not astronauts") && t.toLowerCase().includes("stand-in"));
await clicTexto("button", "Glucose").catch(() => {});
await page.evaluate(() => document.querySelector('button[aria-label^="Glucose"]').click());
await esperarTexto("The absence is data", 8000);
check("glucosa se declara bloqueada, no simulada", (await texto()).toLowerCase().includes("nothing is simulated"));

// 3b · subtítulos: se pueden apagar y el texto sigue disponible para lectores de pantalla (sr-only)
await clicTexto("button", "subtitles on");
await page.waitForFunction(() => [...document.querySelectorAll("button")].some((b) => b.textContent.trim() === "subtitles off"), { timeout: 5000 });
await page.waitForFunction(() => { const e = document.querySelector("p[aria-live]"); return e && getComputedStyle(e).position === "absolute" && e.textContent.length > 0; }, { timeout: 8000 }).then(() => check("«subtitles off» oculta el texto a la vista pero lo deja en el DOM", true), () => check("«subtitles off» oculta el texto a la vista pero lo deja en el DOM", false));
await clicTexto("button", "subtitles off");

// 4 · la demo kill
await page.goto(`${BASE}/kill`, { waitUntil: "domcontentloaded" });
await esperarTexto("Inject a 0.30 kg leak", 30000);
await clicTexto("button", "Inject a 0.30");
await esperarTexto("+0.260 kg", 8000);
const k = await texto();
const kl = k.toLowerCase();
check("la fuga: el manifiesto no alarma y la ley sí", kl.includes("no alarm") && kl.includes("the loop does not close"));

// 5 · La Tormenta: escenario simulado
await page.goto(`${BASE}/storm`, { waitUntil: "domcontentloaded" });
await esperarTexto("What if", 30000);
await clicTexto("button", "G3");
await esperarTexto("SIMULATED UNIVERSE — DAY", 10000);
check("el escenario G3 se rotula UNIVERSO SIMULADO", (await texto()).includes("7.00"));
await clicTexto("button", "back to live");
await page.waitForFunction(() => !document.body.innerText.toLowerCase().includes("simulated universe — day"), { timeout: 8000 });
check("volver a «live» quita el banner simulado", true);

// 5b · La Bóveda: «verifícalo tú mismo» recalcula en el navegador el SHA-256 de cada acta
await page.goto(`${BASE}/vault`, { waitUntil: "domcontentloaded" });
await esperarTexto("Verify all", 30000);
await clicTexto("button", "Verify all");
await page.waitForFunction(() => { const m = document.body.innerText.match(/(\d+) of (\d+) recomputed hashes match/i); return m && m[1] === m[2] && Number(m[2]) >= 20; }, { timeout: 60000 }).then(() => check("las actas recalculadas en el navegador coinciden TODAS con su hash sellado", true), async () => check("las actas recalculadas en el navegador coinciden TODAS con su hash sellado", false, (await texto()).match(/\d+ of \d+ recomputed[^\n]*/i)?.[0] ?? "sin resultado"));

// 5c · La Bóveda: buscar escribiendo y HABLANDO; ALMA responde con su voz y navega
const filas = () => page.$$eval("ul.divide-y > li", (l) => l.length);
const sonados = () => page.evaluate(() => window.__audio.length);
await page.goto(`${BASE}/vault`, { waitUntil: "domcontentloaded" });
await esperar('button[aria-label^="Wake ALMA"]');
await page.click('button[aria-label^="Wake ALMA"]');                  // recarga = puerta otra vez: sin clic real el navegador no deja sonar
await esperarTexto("of 25 shown", 30000);
await page.type('input[aria-label="Search the vault"]', "solar storms");
await page.keyboard.press("Enter");
await esperarTexto("I found", 8000).catch(() => {});
check("escribir «solar storms» encuentra FB-014 y ALMA responde", (await texto()).includes("FB-014") && (await filas()) >= 1);
await page.evaluate(() => { window.__say = "show refuted experiments"; document.querySelector('button[aria-label="Search by voice"]').click(); });
await page.waitForFunction(() => /\b2 of 25 shown/i.test(document.body.innerText), { timeout: 8000 }).then(() => check("por voz: «show refuted experiments» filtra a los 2 refutados", true), () => check("por voz: «show refuted experiments» filtra a los 2 refutados", false));
await page.evaluate(() => { window.__say = "open F B zero two zero"; document.querySelector('button[aria-label="Search by voice"]').click(); });
await page.waitForFunction(() => document.querySelector('li button[aria-expanded="true"]')?.innerText.includes("FB-020"), { timeout: 8000 }).then(() => check("por voz: «open F B zero two zero» abre el acta FB-020", true), () => check("por voz: «open F B zero two zero» abre el acta FB-020", false));
const sonadosAntes = await sonados();
await page.evaluate(() => { window.__say = "find xylophone banana"; document.querySelector('button[aria-label="Search by voice"]').click(); });
await esperarTexto("I found nothing like that", 8000).catch(() => {});
{ const t1 = (await texto()).toLowerCase(); const habló = await page.waitForFunction((n) => window.__audio.length > n, { timeout: 8000 }, sonadosAntes).then(() => true, () => false);
  check("lo que no existe: ALMA dice «nothing like that» y habla", t1.includes("nothing here matches") && habló, `texto=${t1.includes("nothing here matches")} audio=${habló}`); }
await page.evaluate(() => { window.__say = "go to the foundry"; document.querySelector('button[aria-label="Search by voice"]').click(); });
await page.waitForFunction(() => location.pathname === "/foundry", { timeout: 20000 }).then(() => check("por voz: «go to the foundry» te lleva a La Fundición", true), () => check("por voz: «go to the foundry» te lleva a La Fundición", false));

// 6 · Fundición y cápsulas
await page.goto(`${BASE}/foundry`, { waitUntil: "domcontentloaded" });
await page.waitForFunction(() => document.querySelectorAll("article").length === 5, { timeout: 30000 });
check("la Fundición muestra sus 5 tarjetas", true);
await page.goto(`${BASE}/capsule`, { waitUntil: "domcontentloaded" });
await page.waitForFunction(() => document.querySelectorAll("article").length === 3, { timeout: 30000 });
check("las 3 cápsulas llevan límites", (await page.$$eval("article", (a) => a.every((x) => x.innerText.toLowerCase().includes("limits")))));

// M6.9–M6.11 · monitor de constantes con ECG REAL, «esperado en vuelo» con cita y modo sin contacto
await page.goto(`${BASE}/?awake=1&monitor=1`, { waitUntil: "domcontentloaded" });
await esperar('[data-testid="vitals-monitor"]', 60000);
await esperarTexto("not an astronaut", 20000);
check("el monitor muestra un ECG REAL y dice que no es un astronauta", (await page.evaluate(() => document.body.innerText.toLowerCase())).includes("real data"));
await clicTexto("button", "Expected in flight");
await esperarTexto("6.09 h per night", 15000);
check("«Expected in flight» cita a Barger 2014 con su DOI", (await page.evaluate(() => document.body.innerText)).includes("10.1016/S1474-4422(14)70122-X"));
await clicTexto("button", "Earth link"); await clicTexto("button", "connected");
await esperarTexto("Ground cannot answer", 10000);
check("sin contacto: el Guardián sigue decidiendo a bordo y cita el retardo de NASA", (await page.evaluate(() => document.body.innerText)).includes("0 to 22 minutes"));

// M7 · datos REALES de NASA/NOAA: anillos con driver en vivo, sala Frontier (entorno, astronautas reales, atlas OSDR) y Fundición explicada
await page.goto(`${BASE}/?awake=1`, { waitUntil: "domcontentloaded" });
await esperarTexto("protons · live", 60000);
check("los anillos Dose y Rhythm muestran datos REALES en vivo (no «no ledger»)", (await page.evaluate(() => document.body.innerText.toLowerCase())).includes("sunlight · live") || (await page.evaluate(() => document.body.innerText.toLowerCase())).includes("shadow · live"));
await page.goto(`${BASE}/frontier?awake=1`, { waitUntil: "domcontentloaded" });
await esperar("#live", 60000); await esperar("#astronauts", 30000); await esperar("#atlas", 30000);
const ft = await page.evaluate(() => document.body.innerText.toLowerCase());
check("The Frontier: entorno en vivo, astronautas reales y atlas OSDR", ft.includes("live around the crew") && ft.includes("real astronauts") && ft.includes("osd-569") && ft.includes("1 of 28"));
await page.goto(`${BASE}/foundry?awake=1`, { waitUntil: "domcontentloaded" });
await esperar('[data-testid="foundry-explainer"]', 30000);
check("la Fundición explica qué es", (await page.evaluate(() => document.body.innerText.toLowerCase())).includes("what is this page?"));

check("sin errores de consola ni excepciones", errores.length === 0, errores.slice(0, 3).join(" | "));
await browser.close();
console.log(`\n${ok.length} comprobaciones OK`); ok.forEach((n) => console.log("  ✓", n));
if (fallos.length) { console.log(`\n${fallos.length} FALLOS`); fallos.forEach((n) => console.log("  ✗", n)); process.exit(1); }
