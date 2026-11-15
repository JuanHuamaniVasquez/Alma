import puppeteer from "puppeteer-core";
const b = await puppeteer.launch({ executablePath: "/usr/bin/google-chrome", headless: "new", args: ["--no-sandbox", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
const p = await b.newPage(); await p.setViewport({ width: 1366, height: 900 });
await p.goto("http://localhost:3000/foundry?awake=1", { waitUntil: "domcontentloaded" });
await p.waitForSelector('[data-testid="nursery"]', { timeout: 40000 });
await p.evaluate(() => document.querySelector('ol[aria-label^="How a hypothesis"]').scrollIntoView());
await new Promise((r) => setTimeout(r, 1500));
await p.screenshot({ path: "/tmp/claude-1000/nur.png" });
await b.close();
