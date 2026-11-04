#!/usr/bin/env node
/**
 * PRO 3D ANIMATOR — headless deterministic frame capture (Path A export)
 *
 * Renders every frame of a Three.js scene (the starter template or any scene
 * exposing window.__seek(t)) with software WebGL, at exact fps/resolution —
 * no dropped frames, no realtime races. Then assemble with examples/assemble-video.sh.
 *
 * Setup:
 *   npm i -D playwright && npx playwright install chromium --with-deps
 * Usage:
 *   node render-frames.mjs ./scene.html --out frames --w 1920 --h 1080 --fps 30 --secs 8
 *   node render-frames.mjs https://example.com/scene.html --secs 8
 */
import { chromium } from 'playwright';
import { mkdirSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const arg = (name, dflt) => {
  const i = process.argv.indexOf('--' + name);
  return i > -1 ? process.argv[i + 1] : dflt;
};

const url = process.argv[2] ?? './scene.html';
const out = arg('out', 'frames');
const w = parseInt(arg('w', '1920'), 10);
const h = parseInt(arg('h', '1080'), 10);
const fps = parseInt(arg('fps', '30'), 10);
const secs = parseFloat(arg('secs', '8'));

const fullUrl = /^https?:/.test(url) ? url : pathToFileURL(resolve(url)).href;
const sep = fullUrl.includes('?') ? '&' : '?';
const pageUrl = `${fullUrl}${sep}still=1&res=${w}x${h}`;

mkdirSync(out, { recursive: true });

const browser = await chromium.launch({
  args: ['--enable-unsafe-swiftshader', '--use-gl=angle', '--use-angle=swiftshader'],
});
const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
page.on('pageerror', e => { console.error('[pageerror]', e.message); process.exitCode = 1; });

await page.goto(pageUrl, { waitUntil: 'networkidle', timeout: 120_000 });
await page.waitForFunction('window.__ready === true', null, { timeout: 60_000 });

const total = Math.round(fps * secs);
for (let i = 0; i < total; i++) {
  const t = i / fps;
  await page.evaluate(tt => window.__seek(tt), t);
  await page.screenshot({ path: `${out}/f${String(i).padStart(4, '0')}.png` });
  if (i % 30 === 0) console.log(`frame ${i}/${total}`);
}

await browser.close();
console.log(`done → ${total} frames in ${out}/
next:
  bash examples/assemble-video.sh ${out} scene.mp4 --gif preview.gif
  # then add sound: see references/sound-design.md §3`);
