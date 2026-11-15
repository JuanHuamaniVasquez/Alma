import puppeteer from "puppeteer-core";
const b = await puppeteer.launch({ executablePath: "/usr/bin/google-chrome", headless: "new", args: ["--no-sandbox", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
const p = await b.newPage(); await p.setViewport({ width: 1440, height: 1000 });
await p.goto("http://localhost:3000/budget?awake=1", { waitUntil: "domcontentloaded" });
await p.waitForSelector('[data-testid="privacy-book"]', { timeout: 30000 });
await p.evaluate(() => document.querySelector('[data-testid="privacy-book"]').scrollIntoView());
await new Promise((r) => setTimeout(r, 1500));
await p.screenshot({ path: "/tmp/claude-1000/p1.png" });
await b.close();
