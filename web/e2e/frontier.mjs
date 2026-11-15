// Capturas de la sala Frontier: node e2e/frontier.mjs
import puppeteer from "puppeteer-core";
const b = await puppeteer.launch({ executablePath: "/usr/bin/google-chrome", headless: "new", args: ["--no-sandbox", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
const p = await b.newPage(); await p.setViewport({ width: 1366, height: 1500 });
await p.goto("http://localhost:3000/frontier?awake=1", { waitUntil: "domcontentloaded" });
await p.waitForSelector("#live", { timeout: 40000 }); await p.waitForSelector("#astronauts", { timeout: 20000 }); await p.waitForSelector("#atlas", { timeout: 20000 });
await new Promise((r) => setTimeout(r, 1500));
await p.screenshot({ path: "/tmp/claude-1000/fr1.png" });
await p.evaluate(() => document.querySelector("#astronauts").scrollIntoView());
await new Promise((r) => setTimeout(r, 800));
await p.screenshot({ path: "/tmp/claude-1000/fr2.png" });
await b.close();
