#!/usr/bin/env node
/* Screenshot a still frame of a demo page. Usage:
   node scripts/screenshot.mjs <url> <out.png> [w] [h] [t] */
import { chromium } from 'playwright';

const [url, out, w = '1280', h = '720', t = '1.2'] = process.argv.slice(2);
const browser = await chromium.launch({
  args: ['--enable-unsafe-swiftshader', '--use-gl=angle', '--use-angle=swiftshader'],
});
const page = await browser.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: 1 });
page.on('pageerror', e => { console.error('[pageerror]', e.message); process.exitCode = 1; });
page.on('console', m => { if (m.type() === 'error') console.error('[console]', m.text()); });
const sep = url.includes('?') ? '&' : '?';
await page.goto(`${url}${sep}still=1&t=${t}&res=${w}x${h}`, { waitUntil: 'networkidle', timeout: 90_000 });
await page.waitForFunction('window.__ready === true', null, { timeout: 60_000 });
await page.waitForTimeout(250);
await page.screenshot({ path: out });
await browser.close();
console.log('shot →', out);
