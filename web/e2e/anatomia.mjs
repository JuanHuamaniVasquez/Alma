// Capturas de la capa Anatomy para revisar el esqueleto desde varios ángulos: CREW=VEGA node e2e/anatomia.mjs → /tmp/claude-1000/ana_*.png
import puppeteer from "puppeteer-core";
const crew = process.env.CREW ?? "RIGEL";
const b = await puppeteer.launch({ executablePath: "/usr/bin/google-chrome", headless: "new", args: ["--no-sandbox", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
const p = await b.newPage(); await p.setViewport({ width: 1440, height: 900 });
await p.goto(`http://localhost:3000/?awake=1&crew=${crew}&layer=anatomy`, { waitUntil: "domcontentloaded" });
await new Promise((r) => setTimeout(r, 14000));
const snap = async (n) => { await new Promise((r) => setTimeout(r, 1200)); await p.screenshot({ path: `/tmp/claude-1000/ana_${n}.png` }); };
await snap("frente");
if (process.env.HOLO) { await p.evaluate(() => [...document.querySelectorAll("button")].find((x) => /^Hologram$/i.test(x.textContent.trim()))?.click()); await new Promise((r) => setTimeout(r, 800)); }
await p.mouse.move(720, 450); await p.mouse.down(); await p.mouse.move(830, 450, { steps: 10 }); await p.mouse.up(); await snap("lado0");
await p.mouse.move(720, 450); for (let i = 0; i < 4; i++) { await p.mouse.wheel({ deltaY: -320 }); await new Promise((r) => setTimeout(r, 100)); } await snap("zoom");
await p.mouse.move(720, 450); await p.mouse.down(); await p.mouse.move(830, 450, { steps: 10 }); await p.mouse.up(); await snap("lado");
await p.mouse.move(720, 450); await p.mouse.down(); await p.mouse.move(850, 450, { steps: 10 }); await p.mouse.up(); await snap("giro");
await b.close();
