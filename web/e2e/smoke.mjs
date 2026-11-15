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
await page.waitForFunction(() => !document.querySelector('button[aria-label^="Wake ALMA"]'), { timeout: 5000 });
check("la puerta se abre con un clic", true);
await esperar("p[aria-live]", 30000);
await dormir(1500);
check("ALMA muestra su subtítulo", (await page.$eval("p[aria-live]", (e) => e.textContent.length)) > 20);
const audio = await page.evaluate(() => window.__audio);
check("el audio de ALMA arranca tras el clic (política de autoplay)", audio.some((a) => a.ok && a.src.includes("/voice/")), JSON.stringify(audio));

// 2 · navegación con flechas
await page.keyboard.press("ArrowRight");
await page.waitForFunction(() => location.pathname === "/machine", { timeout: 8000 });
check("la flecha derecha va a Machine Room", true);
await page.keyboard.press("ArrowLeft");
await page.waitForFunction(() => location.pathname === "/", { timeout: 8000 });

// 3 · figura humana: modo Body, ánimo en 3 toques
await clicTexto("button", "Body");
await page.waitForSelector('button[aria-label^="Mood"]', { timeout: 20000 });
await page.evaluate(() => document.querySelector('button[aria-label^="Mood"]').click());
await esperarTexto("How do you feel right now?", 8000);
check("el marcador Mood abre su recibo", true);
const antes = await page.$eval('button[disabled], button:disabled', (e) => e.textContent.trim().toLowerCase()).catch(() => "");
check("«Send» está desactivado hasta elegir un valor", antes.startsWith("send"));
await dormir(700);
await page.click('[role="radio"][title="Good"]');
await page.evaluate(() => [...document.querySelectorAll("button")].find((b) => b.textContent.trim() === "Send").click());
await esperarTexto("Saved.", 8000);
check("el ánimo se envía con valor 4 y duración medida > 0", enviado?.valor === 4 && enviado.duracion_respuesta_s > 0 && /^crew-[0-9a-f]{8}$/.test(enviado.persona_id), JSON.stringify(enviado));
await page.evaluate(() => document.querySelector('button[aria-label^="Heart rate"]').click());
await esperarTexto("people with a baseline", 8000);
const t = await texto();
check("el recibo de frecuencia cardíaca declara su límite conocido", t.toLowerCase().includes("known limit") && t.toLowerCase().includes("not astronauts"));
await clicTexto("button", "Glucose").catch(() => {});
await page.evaluate(() => document.querySelector('button[aria-label^="Glucose"]').click());
await esperarTexto("The absence is data", 8000);
check("glucosa se declara bloqueada, no simulada", (await texto()).toLowerCase().includes("nothing is simulated"));

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

// 6 · Fundición y cápsulas
await page.goto(`${BASE}/foundry`, { waitUntil: "domcontentloaded" });
await page.waitForFunction(() => document.querySelectorAll("article").length === 5, { timeout: 30000 });
check("la Fundición muestra sus 5 tarjetas", true);
await page.goto(`${BASE}/capsule`, { waitUntil: "domcontentloaded" });
await page.waitForFunction(() => document.querySelectorAll("article").length === 3, { timeout: 30000 });
check("las 3 cápsulas llevan límites", (await page.$$eval("article", (a) => a.every((x) => x.innerText.toLowerCase().includes("limits")))));

check("sin errores de consola ni excepciones", errores.length === 0, errores.slice(0, 3).join(" | "));
await browser.close();
console.log(`\n${ok.length} comprobaciones OK`); ok.forEach((n) => console.log("  ✓", n));
if (fallos.length) { console.log(`\n${fallos.length} FALLOS`); fallos.forEach((n) => console.log("  ✗", n)); process.exit(1); }
