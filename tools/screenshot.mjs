/**
 * screenshot.mjs
 * Takes a full-page screenshot of a URL using Puppeteer.
 *
 * Usage:
 *   node tools/screenshot.mjs                              → screenshots http://localhost:3000
 *   node tools/screenshot.mjs http://localhost:3000        → same
 *   node tools/screenshot.mjs http://localhost:3000 hero   → saves as screenshot-N-hero.png
 *
 * Screenshots are saved to .tmp/screenshots/ with auto-incremented filenames.
 * Existing files are never overwritten.
 */

import puppeteer from "puppeteer";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const OUTPUT_DIR = path.join(ROOT, ".tmp", "screenshots");

// Ensure output directory exists
fs.mkdirSync(OUTPUT_DIR, { recursive: true });

const url = process.argv[2] || "http://localhost:3000";
const label = process.argv[3] || null;

// Find next available screenshot number
function nextFilename(label) {
  let n = 1;
  while (true) {
    const name = label ? `screenshot-${n}-${label}.png` : `screenshot-${n}.png`;
    if (!fs.existsSync(path.join(OUTPUT_DIR, name))) return name;
    n++;
  }
}

const filename = nextFilename(label);
const outPath = path.join(OUTPUT_DIR, filename);

console.log(`[INFO] Screenshotting ${url} ...`);

const browser = await puppeteer.launch({
  headless: "new",
  args: ["--no-sandbox", "--disable-setuid-sandbox"],
});

const page = await browser.newPage();

// Desktop viewport
await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 2 });

await page.goto(url, { waitUntil: "networkidle0", timeout: 30000 });

// Wait for fonts and images to settle
await new Promise((r) => setTimeout(r, 800));

await page.screenshot({ path: outPath, fullPage: true });

await browser.close();

console.log(`[OK]   Saved → .tmp/screenshots/${filename}`);
