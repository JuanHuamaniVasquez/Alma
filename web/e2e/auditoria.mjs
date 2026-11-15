// Capturas de TODAS las salas a 1366×768 para revisión visual: node e2e/auditoria.mjs  → /tmp/claude-1000/aud_<sala>.png
import puppeteer from "puppeteer-core";
const salas = [["home", "/?awake=1&crew=VEGA"], ["machine", "/machine?awake=1"], ["leak", "/kill?awake=1"], ["vault", "/vault?awake=1"], ["foundry", "/foundry?awake=1"], ["storm", "/storm?awake=1"], ["budget", "/budget?awake=1"], ["capsule", "/capsule?awake=1"], ["frontier", "/frontier?awake=1"]];
const b = await puppeteer.launch({ executablePath: "/usr/bin/google-chrome", headless: "new", args: ["--no-sandbox", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
const p = await b.newPage(); await p.setViewport({ width: +(process.env.W ?? 1366), height: +(process.env.H ?? 768), deviceScaleFactor: 1, isMobile: +(process.env.W ?? 1366) < 600 });
for (const [n, u] of salas) {
  await p.goto("http://localhost:3000" + u, { waitUntil: "domcontentloaded" });
  await new Promise((r) => setTimeout(r, n === "home" ? 11000 : 5000));
  await p.screenshot({ path: `/tmp/claude-1000/aud${process.env.SUF ?? ""}_${n}.png` });
}
await b.close();
