// Captura ampliada (×3) de una región: node e2e/zoom.mjs "<ruta>" salida.png x y ancho alto   (diagnóstico de la figura)
import puppeteer from "puppeteer-core";
const [ruta, out, x, y, w, h] = process.argv.slice(2);
const b = await puppeteer.launch({ executablePath: "/usr/bin/google-chrome", headless: "new", args: ["--no-sandbox", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
const p = await b.newPage(); await p.setViewport({ width: 1440, height: 900, deviceScaleFactor: 3 });
await p.goto("http://localhost:3000" + ruta, { waitUntil: "domcontentloaded" });
await p.waitForFunction(() => document.body.innerText.length > 200, { timeout: 40000 });
await p.waitForFunction(() => !document.body.innerText.includes("Loading NASA Z-2"), { timeout: 60000 }).catch(() => {});
await new Promise((r) => setTimeout(r, 9000));
await p.screenshot({ path: out, clip: { x: +x, y: +y, width: +w, height: +h } });
await b.close();
