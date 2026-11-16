// Comprueba que tocar un órgano en la capa Anatomy selecciona su indicador: barre una rejilla sobre el torso y exige que algún clic cambie el texto de la ficha. node e2e/organo.mjs
import puppeteer from "puppeteer-core";
const b = await puppeteer.launch({ executablePath: "/usr/bin/google-chrome", headless: "new", args: ["--no-sandbox", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
const p = await b.newPage(); await p.setViewport({ width: 1440, height: 900 });
await p.goto("http://localhost:3000/?awake=1&crew=VEGA&layer=anatomy", { waitUntil: "domcontentloaded" });
await new Promise((r) => setTimeout(r, 14000));
const texto = () => p.evaluate(() => document.body.innerText);
const base = await texto(); let hit = null;
for (let y = 300; y <= 560 && !hit; y += 26) for (let x = 640; x <= 790 && !hit; x += 18) {
  await p.mouse.click(x, y); await new Promise((r) => setTimeout(r, 350));
  const t = await texto(); if (t !== base && /heart|brain|pancreas|pressure|temperature|sleep|mood|glucose/i.test(t.replace(base, ""))) hit = [x, y];
}
console.log(hit ? `órgano tocado en ${hit}` : "NINGÚN órgano respondió"); await p.screenshot({ path: "/tmp/claude-1000/o1.png" }); await b.close(); process.exit(hit ? 0 : 1);
