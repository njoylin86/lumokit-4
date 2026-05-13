import puppeteer from 'puppeteer';
const browser = await puppeteer.launch({ args: ['--no-sandbox'] });
const page = await browser.newPage();
await page.setViewport({ width: 1440, height: 900 });
await page.goto('http://localhost:8765/Akuttandv%C3%A5rd.html', { waitUntil: 'networkidle0' });
await new Promise(r => setTimeout(r, 1500));
await page.screenshot({ path: '.tmp/screenshots/header-zoom.png', clip: { x: 0, y: 38, width: 1440, height: 80 } });
await browser.close();
console.log('done');
