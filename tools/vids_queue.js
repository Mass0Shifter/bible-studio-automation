// Bible Director Studio — Google Vids AI-video queue (paste into a Vids doc tab, e.g. "Genesis 19 Clips";
// open the right panel → AI Video → Animate first). Written 2026-11-08 (Genesis 19).
// Load:   window.__vq = [{key:'v01', img:'<image url readable from docs.google.com>', len:8, prompt:'...', name:'Genesis_19_v01.mp4'}, ...]
// Run:    __vqueue.run()           (skips keys already 'ok' in localStorage.__vq_state_<tag>)
// Status: __vqueue.status()
// Each finished clip is downloaded to the PC's Downloads folder under its name (move it into <Book> <Ch>\video\).
(() => {
const sl = ms => new Promise(r => setTimeout(r, ms));
const TAG = () => (window.__vqtag || 'default');
const st = () => JSON.parse(localStorage['__vq_state_' + TAG()] || '{}');
const setSt = (k, v) => { const s = st(); s[k] = v; localStorage['__vq_state_' + TAG()] = JSON.stringify(s); };
const log = m => (window.__vqlog = window.__vqlog || []).push(new Date().toISOString().slice(11, 19) + ' ' + m);
const ed = () => document.querySelector('[contenteditable=true][aria-label^="Add your image"]');
const gen = () => [...document.querySelectorAll('button[aria-label="Generate"]')].find(b => b.offsetParent);
const chip = () => [...document.querySelectorAll('button')].find(b => /^Generation settings/.test(b.getAttribute('aria-label') || ''));
const vids = () => [...document.querySelectorAll('video')].map(v => v.currentSrc || v.src).filter(Boolean);
const panelText = () => (document.querySelector('[aria-label="AI video clip"]') || document.body).innerText;
async function clear() {
  // after a clip finishes the composer collapses: Expand it, then Clear (brings back the image file input)
  const x = [...document.querySelectorAll('button[aria-label="Expand"]')].find(b => b.offsetParent);
  if (x && !document.querySelector('input[type=file][accept*="image/png"]')) { x.click(); await sl(1500); }
  const c = [...document.querySelectorAll('button')].find(b => b.offsetParent && b.innerText.trim() === 'Clear');
  if (c) { c.click(); await sl(1500); }
  if (!document.querySelector('input[type=file][accept*="image/png"]')) throw 'composer not ready (no image input)';
}
async function setImg(url, name) {
  const b = await (await fetch(url)).blob();
  const inp = document.querySelector('input[type=file][accept*="image/png"]');
  const dt = new DataTransfer(); dt.items.add(new File([b], name, { type: b.type || 'image/png' }));
  inp.files = dt.files; inp.dispatchEvent(new Event('change', { bubbles: true }));
  await sl(4000);
}
async function setPrompt(p) {
  const e = ed(); e.focus(); document.execCommand('selectAll'); document.execCommand('delete');
  document.execCommand('insertText', false, p); await sl(600);
}
async function setLen(s) {
  chip().click(); await sl(900);
  const r = document.querySelector('input[type=range][aria-label="Video duration"]');
  Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(r, String(s));
  r.dispatchEvent(new Event('input', { bubbles: true })); r.dispatchEvent(new Event('change', { bubbles: true }));
  await sl(500);
  document.activeElement && document.activeElement.blur();
  document.body.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, bubbles: true }));
  await sl(700);
  return chip().getAttribute('aria-label');
}
async function save(src, name) {
  const b = await (await fetch(src, { credentials: 'include' })).blob();
  const a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = name;
  document.body.appendChild(a); a.click(); a.remove(); return b.size;
}
async function one(it) {
  await clear();
  await setImg(it.img, it.key + '.png');
  await setPrompt(it.prompt);
  const c = await setLen(it.len);
  if (!new RegExp('\\b' + it.len + ' seconds').test(c)) throw 'length not set: ' + c;
  const before = new Set(vids());
  const g = gen(); if (!g || g.disabled) throw 'generate disabled';
  g.click(); log('gen ' + it.key + ' ' + it.len + 's');
  const t0 = Date.now(); let src = null; await sl(10000);
  const busy = () => [...document.querySelectorAll('button')].some(b => b.offsetParent && b.innerText.trim() === 'Cancel');
  let idle = 0;
  while (Date.now() - t0 < 8 * 60e3) {
    const nv = vids().filter(s => !before.has(s) && /usercontent/.test(s));
    if (!busy() && nv.length) { src = nv[nv.length - 1]; break; }
    if (!busy()) { idle += 5; if (idle >= 25) {
      const m = (document.body.innerText.match(/[^\n]*(can.t|couldn.t|unable|policy|violat|limit|quota|try again)[^\n]*/i) || ['no clip appeared'])[0];
      throw 'refused: ' + m.slice(0, 160); } } else idle = 0;
    await sl(5000);
  }
  if (!src) throw 'timeout';
  await sl(2000);
  const size = await save(src, it.name);
  return size;
}
async function run(only) {
  if (window.__vqrunning) return 'already running';
  window.__vqrunning = true; window.__vqstop = false;
  try {
    for (const it of window.__vq) {
      if (window.__vqstop) break;
      if (only && !only.includes(it.key)) continue;
      if (st()[it.key] === 'ok') continue;
      try { const sz = await one(it); setSt(it.key, 'ok'); log('ok ' + it.key + ' ' + sz); }
      catch (e) { setSt(it.key, 'error: ' + e); log('error ' + it.key + ' ' + e); if (/limit|quota/i.test(String(e))) break; }
      await sl(3000);
    }
  } finally { window.__vqrunning = false; log('done'); }
}
window.__vqueue = { run, one, clear, setImg, setPrompt, setLen, save, status: () => ({ running: !!window.__vqrunning, state: st(), log: (window.__vqlog || []).slice(-6) }), stop: () => { window.__vqstop = true; }, reset: keys => { const s = st(); keys.forEach(k => delete s[k]); localStorage['__vq_state_' + TAG()] = JSON.stringify(s); } };
return 'vids queue ready';
})();
