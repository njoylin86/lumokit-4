import puppeteer from "puppeteer";
const url = process.argv[2] || "https://swordfish.templweb.com/";
const browser = await puppeteer.launch({ headless: "new", args: ["--no-sandbox"] });
const page = await browser.newPage();
await page.setViewport({ width: 1440, height: 900 });
await page.evaluateOnNewDocument(() => {
  try {
    localStorage.setItem("lumoPremiumTourSeen", "1");
    localStorage.setItem("premiumTourSeen", "1");
  } catch(e) {}
});
await page.goto(url, { waitUntil: "networkidle2", timeout: 60000 });
// Walk every <style> and find rules that match our element
const out = await page.evaluate(() => {
  const target = document.querySelector(".hb-buttons .btn-ghost");
  if (!target) return { error: "no target" };
  const hits = [];
  for (const sheet of document.styleSheets) {
    let rules;
    try { rules = sheet.cssRules; } catch(e) { continue; }
    if (!rules) continue;
    for (const r of rules) {
      if (!r.selectorText) continue;
      const parts = r.selectorText.split(",").map(s => s.trim());
      for (const p of parts) {
        try {
          if (target.matches(p)) {
            hits.push({
              sheet: sheet.href || (sheet.ownerNode?.id || "inline"),
              fullSelector: r.selectorText,
              matchingPart: p,
              cssText: r.style.cssText,
            });
          }
        } catch(e) {}
      }
    }
  }
  return hits;
});
console.log(JSON.stringify(out, null, 2));
await browser.close();
