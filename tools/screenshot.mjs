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
  protocolTimeout: 120000,
});

const page = await browser.newPage();

// Desktop viewport
await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 2 });

try {
  await page.goto(url, { waitUntil: "networkidle2", timeout: 25000 });
} catch (e) {
  // Timeout OK — Tailwind CDN may still be processing
}

// Give Tailwind CDN time to inject styles
await new Promise((r) => setTimeout(r, 4000));

await page.screenshot({ path: outPath, fullPage: false });

await browser.close();

console.log(`[OK]   Saved → .tmp/screenshots/${filename}`);
