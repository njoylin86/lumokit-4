import puppeteer from "puppeteer";
const url = process.argv[2] || "https://swordfish.templweb.com/";
const out = process.argv[3] || "/home/njoylin/projects/htdocs/lumokit-4/.tmp/screenshots/hero-zoom.png";
const browser = await puppeteer.launch({ headless: "new", args: ["--no-sandbox"] });
const page = await browser.newPage();
await page.setViewport({ width: 1440, height: 900 });
await page.evaluateOnNewDocument(() => {
  try {
    localStorage.setItem("lumoPremiumTourSeen", "1");
    localStorage.setItem("premiumTourSeen", "1");
    localStorage.setItem("lumoPopupSeen", "1");
  } catch(e) {}
});
await page.goto(url, { waitUntil: "networkidle2", timeout: 60000 });
await page.evaluate(() => {
  document.querySelectorAll('[aria-label*="Stäng" i], [class*="close" i], [data-close]').forEach(el => {
    try { el.click(); } catch(e) {}
  });
  document.querySelectorAll('[class*="popup" i], [class*="modal" i], [class*="tour" i], [class*="overlay" i]').forEach(el => {
    if (!['A','BUTTON','SECTION','MAIN'].includes(el.tagName)) el.style.display = 'none';
  });
});
await new Promise(r => setTimeout(r, 800));
// If a hero buttons container exists, screenshot just that
const btns = await page.$(".hb-buttons");
if (btns) {
  const box = await btns.boundingBox();
  const pad = 40;
  await page.screenshot({
    path: out,
    clip: {
      x: Math.max(0, box.x - pad),
      y: Math.max(0, box.y - pad),
      width: box.width + pad * 2,
      height: box.height + pad * 2,
    },
  });
} else {
  await page.screenshot({ path: out, fullPage: false });
}
await browser.close();
console.log("Saved:", out);
