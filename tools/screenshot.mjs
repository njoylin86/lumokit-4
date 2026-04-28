/**
 * screenshot.mjs
 * Takes a FULL-PAGE screenshot of a URL or a local HTML file.
 *
 * Usage:
 *   node tools/screenshot.mjs                                → http://localhost:3000
 *   node tools/screenshot.mjs http://localhost:3000          → same
 *   node tools/screenshot.mjs http://localhost:3000 hero     → .tmp/screenshots/screenshot-N-hero.png
 *   node tools/screenshot.mjs .tmp/hem_design.html           → .tmp/hem_design_screenshot.png
 *   node tools/screenshot.mjs .tmp/hem_design.html --mobile  → .tmp/hem_design_screenshot_mobile.png
 *
 * Flags:
 *   --mobile   Use mobile viewport (390x844, iPhone-ish). Default is desktop 1440x900.
 *
 * For local HTML files: screenshot saved next to source as `[name]_screenshot[_mobile].png`
 * (overwritten each run). For URLs: saved to .tmp/screenshots/ with auto-numbering.
 *
 * fullPage is always true — the entire scrolled page is captured so design
 * decisions can be made on the complete layout, not just the viewport.
 */

import puppeteer from "puppeteer";
import fs from "fs";
import path from "path";
import { fileURLToPath, pathToFileURL } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const OUTPUT_DIR = path.join(ROOT, ".tmp", "screenshots");

const args = process.argv.slice(2);
const mobile = args.includes("--mobile");
const positional = args.filter((a) => !a.startsWith("--"));
const arg   = positional[0] || "http://localhost:3000";
const label = positional[1] || null;

const viewport = mobile
  ? { width: 390, height: 844, deviceScaleFactor: 2, isMobile: true, hasTouch: true }
  : { width: 1440, height: 900, deviceScaleFactor: 2 };

// Detect whether arg is a local file or a URL
const isUrl = /^https?:\/\//i.test(arg);

let targetUrl;
let outPath;

const suffix = mobile ? "_mobile" : "";

if (isUrl) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  targetUrl = arg;

  // Auto-numbered filename so multiple runs don't overwrite each other
  let n = 1;
  while (true) {
    const base = label ? `screenshot-${n}-${label}` : `screenshot-${n}`;
    const candidate = path.join(OUTPUT_DIR, `${base}${suffix}.png`);
    if (!fs.existsSync(candidate)) { outPath = candidate; break; }
    n++;
  }
} else {
  const absPath = path.isAbsolute(arg) ? arg : path.join(ROOT, arg);
  if (!fs.existsSync(absPath)) {
    console.error(`[ERROR] Local file not found: ${absPath}`);
    process.exit(1);
  }
  targetUrl = pathToFileURL(absPath).href;
  // Save next to source as <stem>_screenshot[_mobile].png — overwrite each
  // run so the agent reading the file always sees the current state.
  const dir  = path.dirname(absPath);
  const stem = path.basename(absPath, path.extname(absPath));
  outPath = path.join(dir, `${stem}_screenshot${suffix}.png`);
}

console.log(`[INFO] Screenshotting ${targetUrl} ...`);

const browser = await puppeteer.launch({
  headless: "new",
  args: ["--no-sandbox", "--disable-setuid-sandbox"],
  protocolTimeout: 120000,
});

const page = await browser.newPage();
await page.setViewport(viewport);

try {
  await page.goto(targetUrl, { waitUntil: "networkidle2", timeout: 25000 });
} catch (e) {
  // Timeout OK — fonts/CDN assets may still be settling.
}

// Allow web fonts (Cormorant, Outfit) to fully render before capture.
await new Promise((r) => setTimeout(r, 4000));

await page.screenshot({ path: outPath, fullPage: true });

await browser.close();

const rel = path.relative(ROOT, outPath);
console.log(`[OK]   Saved → ${rel}`);
