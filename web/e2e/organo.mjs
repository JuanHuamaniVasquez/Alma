// Comprueba que tocar un órgano en la capa Anatomy selecciona su indicador: node e2e/organo.mjs
import puppeteer from "puppeteer-core";
const b = await puppeteer.launch({ executablePath: "/usr/bin/google-chrome", headless: "new", args: ["--no-sandbox", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
const p = await b.newPage(); await p.setViewport({ width: 1440, height: 900 });
await p.goto("http://localhost:3000/?awake=1&crew=VEGA&layer=anatomy", { waitUntil: "domcontentloaded" });
await new Promise((r) => setTimeout(r, 14000));
const before = await p.evaluate(() => document.body.innerText.length);
await p.mouse.click(690, 341);
await new Promise((r) => setTimeout(r, 2500));
await p.screenshot({ path: "/tmp/claude-1000/o1.png" });
console.log("texto antes/después", before, await p.evaluate(() => document.body.innerText.length));
await b.close();
