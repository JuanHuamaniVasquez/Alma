// Capturas de las salas para el README (docs/screenshots/). Requiere API :8000 y vitrina :3000. Uso: pnpm screenshots
import puppeteer from "puppeteer-core";
import { mkdirSync } from "node:fs";

const OUT = new URL("../../docs/screenshots/", import.meta.url).pathname;
mkdirSync(OUT, { recursive: true });
const SHOTS = [
  ["01-medical-module", "/?awake=1&day=11&pick=aire&crew=LYRA"], ["02-body-indicators", "/?awake=1&mode=body&ind=fc&crew=RIGEL"], ["03-machine-room", "/machine?awake=1&pick=aire:10"],
  ["04-the-leak", "/kill?awake=1&leak=1"], ["05-the-vault", "/vault?awake=1"], ["06-the-foundry", "/foundry?awake=1"], ["07-the-storm", "/storm?awake=1"],
  ["08-the-budget", "/budget?awake=1"], ["09-the-capsule", "/capsule?awake=1"], ["10-the-frontier", "/frontier?awake=1"], ["11-anatomy", "/?awake=1&crew=VEGA&layer=anatomy"],
];
const b = await puppeteer.launch({ executablePath: process.env.CHROME ?? "/usr/bin/google-chrome", headless: "new", args: ["--no-sandbox", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
for (const [name, path] of SHOTS) {
  const p = await b.newPage(); await p.setViewport({ width: 1440, height: 900 });
  await p.goto("http://localhost:3000" + path, { waitUntil: "domcontentloaded" });
  await p.waitForFunction(() => document.body.innerText.length > 200, { timeout: 40000 });
  if (path.startsWith("/?")) await p.waitForFunction(() => !document.body.innerText.includes("Loading NASA Z-2"), { timeout: 60000 }).catch(() => {});
  await new Promise((r) => setTimeout(r, path.startsWith("/?") ? 3500 : 1800));
  await p.addStyleTag({ content: "div.pointer-events-none.absolute.inset-x-0.bottom-0 { display: none !important; }" });   // sin la banda de subtítulos de ALMA
  await p.screenshot({ path: `${OUT}${name}.jpg`, type: "jpeg", quality: 84 });
  console.log("✓", name);
  await p.close();
}
await b.close();
