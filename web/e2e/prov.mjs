import puppeteer from "puppeteer-core";
const b = await puppeteer.launch({ executablePath: "/usr/bin/google-chrome", headless: "new", args: ["--no-sandbox", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
const p = await b.newPage(); await p.setViewport({ width: 1440, height: 900 });
await p.goto("http://localhost:3000/storm?awake=1", { waitUntil: "domcontentloaded" });
await p.waitForFunction(() => [...document.querySelectorAll("button")].some((x) => /real here/i.test(x.innerText)), { timeout: 30000 });
await p.evaluate(() => [...document.querySelectorAll("button")].find((x) => /real here/i.test(x.innerText)).click());
await new Promise((r) => setTimeout(r, 1500));
await p.screenshot({ path: "/tmp/claude-1000/pv.png" });
await b.close();
