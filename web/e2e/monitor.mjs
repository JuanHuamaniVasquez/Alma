// Capturas del monitor de constantes (3 pestañas): node e2e/monitor.mjs
import puppeteer from "puppeteer-core";
const b = await puppeteer.launch({ executablePath: "/usr/bin/google-chrome", headless: "new", args: ["--no-sandbox", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
const p = await b.newPage(); await p.setViewport({ width: 1440, height: 900 });
await p.goto("http://localhost:3000/?awake=1&crew=VEGA&monitor=1", { waitUntil: "domcontentloaded" });
await p.waitForSelector('[data-testid="vitals-monitor"]', { timeout: 40000 });
const tab = async (t) => p.evaluate((t) => [...document.querySelectorAll('[role="tab"]')].find((x) => x.innerText.trim().toLowerCase() === t).click(), t);
await new Promise((r) => setTimeout(r, 2500));
await tab("expected in flight"); await p.waitForSelector('[data-testid="expected-tab"]'); await new Promise((r) => setTimeout(r, 2500));
await p.screenshot({ path: "/tmp/claude-1000/mon_exp.png", clip: { x: 800, y: 40, width: 640, height: 700 } });
await tab("earth link"); await p.waitForSelector('[data-testid="link-tab"]');
await p.evaluate(() => [...document.querySelectorAll("button")].find((x) => /connected/i.test(x.innerText)).click());
await new Promise((r) => setTimeout(r, 800));
await p.screenshot({ path: "/tmp/claude-1000/mon_link.png", clip: { x: 800, y: 40, width: 640, height: 700 } });
console.log("texto esperado ok:", await p.evaluate(() => document.body.innerText.includes("0 to 22") || document.body.innerText.includes("0–22")));
await b.close();
