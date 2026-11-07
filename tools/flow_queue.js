// Bible Director Studio — Google Flow clip queue (paste into the Flow project tab, flow.google.com/project/<id>).
// 1) __fq.upload([{name:'Genesis_17_v01.png', url:'https://pub-...r2.dev/...png'}, ...])   (r2 links are readable from Flow)
//    (open the asset picker first — Start / Image ingredient — so the "Upload media" button exists; drag-drop is only the fallback)
// 2) __fq.run([{key, img:'Genesis_17_v01.png', len:4|6|8|10, prompt}], {gapMs:35000})       (not awaited; poll __fq.status())
//    Settings per clip: Video · Frames · 16:9 · 720p · <len>s · x1.  Start frame = the asset whose title is `img`.
//    Stops by itself when Flow says the credits are used up (status.stopped = 'credits'): tell the user, they sign in to another account.
(() => {
const sl = ms => new Promise(r => setTimeout(r, ms));
const vis = e => e && e.offsetParent;
const log = m => { (window.__fqlog = window.__fqlog || []).push(new Date().toISOString().slice(11, 19) + ' ' + m); };
const st = () => JSON.parse(localStorage.__flow_q || '{}');
const setSt = (k, v) => { const s = st(); s[k] = v; localStorage.__flow_q = JSON.stringify(s); };
async function drop(files) {
  const dt = new DataTransfer(); files.forEach(f => dt.items.add(f));
  const fire = (el, t) => el.dispatchEvent(new DragEvent(t, { bubbles: true, cancelable: true, dataTransfer: dt }));
  let el = document.elementFromPoint(innerWidth / 2, innerHeight * 0.45); fire(el, 'dragenter'); fire(el, 'dragover'); await sl(800);
  el = document.elementFromPoint(innerWidth / 2, innerHeight * 0.45); fire(el, 'dragenter'); fire(el, 'dragover'); fire(el, 'drop');
}
async function upload(items) {
  const fs = [];
  for (const it of items) { const b = await (await fetch(it.url)).blob(); fs.push(new File([b], it.name, { type: 'image/png' })); }
  // 2026-11-04 (Genesis 19): drag-drop does nothing in a new, empty project. Use the picker's "Upload media" button instead:
  // catch the file input it creates (its click is suppressed, so no OS dialog opens) and hand it the files.
  const btn = document.querySelector('button[aria-label="Upload media"]');
  if (btn) {
    let cap = null; const oc = HTMLInputElement.prototype.click;
    HTMLInputElement.prototype.click = function () { cap = this; };
    try { btn.click(); await sl(800); } finally { HTMLInputElement.prototype.click = oc; }
    if (cap) { const dt = new DataTransfer(); fs.forEach(f => dt.items.add(f)); cap.files = dt.files; cap.dispatchEvent(new Event('change', { bubbles: true })); log('uploaded ' + fs.length); return fs.length; }
  }
  await drop(fs); log('dropped ' + fs.length); return fs.length;   // older layout: needs the asset picker closed
}
const radio = label => { const r = [...document.querySelectorAll('[role=radio]')].find(e => vis(e) && e.innerText.trim().replace(/\s+/g, ' ').split(' ').pop() === label); if (r && r.getAttribute('aria-checked') !== 'true') r.click(); return !!r; };
const chip = () => document.querySelector('[aria-label="Settings trigger"]');
const isOpen = () => [...document.querySelectorAll('[role=radio]')].some(vis);
async function settings(len) {   // the chip toggles the panel: open it only if closed, close it only if open
  for (let i = 0; i < 3; i++) {
    if (!isOpen()) { chip().click(); await sl(900); }
    radio('Video'); await sl(300); radio('Frames'); radio('16:9'); radio('720p'); radio(len + 's'); radio('x1'); await sl(400);
    if (isOpen()) { chip().click(); await sl(600); }
    if (new RegExp('Video\\s*·\\s*720p\\s*·\\s*' + len + 's').test(chip().innerText)) return true;
  }
  throw 'settings chip shows ' + chip().innerText.replace(/\s+/g, ' ');
}
async function pickStart(name) {   // 2026-10-30: picker items show the file name in .asset-title; a clicked item must be confirmed with "Add to prompt"
  const isOpen = () => [...document.querySelectorAll('button.asset-item')].some(vis);
  const ingSet = () => [...document.querySelectorAll('button[aria-label="Image ingredient"]')].some(vis);
  for (let k = 0; k < 3 && !isOpen(); k++) {
    const ing = [...document.querySelectorAll('button[aria-label="Image ingredient"]')].find(vis);
    const st = [...document.querySelectorAll('button')].find(b => vis(b) && b.innerText.trim() === 'Start');
    (st || ing).click(); await sl(1800);
  }
  const box = [...document.querySelectorAll('input')].find(i => vis(i) && /Search assets/i.test(i.placeholder || ''));
  if (box) { box.focus(); box.select(); document.execCommand('insertText', false, name.replace(/\.png$/, '')); box.dispatchEvent(new Event('input', { bubbles: true })); await sl(2000); }
  let it = null;
  for (let i = 0; i < 12 && !it; i++) { it = [...document.querySelectorAll('button.asset-item')].find(b => vis(b) && (b.querySelector('.asset-title') || b).innerText.trim() === name); if (!it) await sl(1000); }
  if (!it) throw 'asset not found ' + name;   // a freshly dropped image needs ~1 min of processing first
  it.click(); await sl(1500);
  if (isOpen()) { const add = [...document.querySelectorAll('button')].find(b => vis(b) && /Add to prompt/.test(b.innerText)); if (add) { add.click(); await sl(2500); } }
  if (!ingSet()) throw 'start frame not set ' + name;
}
async function prompt(text) {   // never selectAll the page: that also deletes the start-frame chip
  const ed = [...document.querySelectorAll('.ProseMirror')].find(vis);
  ed.focus();
  if (ed.innerText.trim()) { const rg = document.createRange(); rg.selectNodeContents(ed); const s = getSelection(); s.removeAllRanges(); s.addRange(rg); document.execCommand('delete'); }
  document.execCommand('insertText', false, text); await sl(800);
  if (!ed.innerText.includes(text.slice(0, 40))) throw 'prompt not inserted';
}
const creditsGone = () => /not enough credits|out of credits|insufficient credits|run out of credits|no credits|credits left: 0|upgrade to (continue|keep)/i.test(document.body.innerText);
async function one(c) {   // order matters: settings -> start frame -> wait 3 s (Flow clears the box when the frame loads) -> prompt
  await settings(c.len); await pickStart(c.img); await sl(3000); await prompt(c.prompt); await sl(1000);
  const go = document.querySelector('button[aria-label="Start generation"]');
  if (![...document.querySelectorAll('button[aria-label="Image ingredient"]')].some(vis)) throw 'start frame lost';
  if (!go || go.disabled) throw 'generate button disabled';
  go.click(); await sl(5000);
  if (creditsGone()) return 'credits';
  return 'submitted';
}
async function run(list, opt = {}) {
  if (window.__fqrunning) return 'already running';
  window.__fqrunning = true; window.__fqstop = false; window.__fqstopped = null;
  try {
    for (const c of list) {
      if (window.__fqstop) break;
      if (st()[c.key] === 'submitted') continue;
      try { const r = await one(c); setSt(c.key, r); log(r + ' ' + c.key + ' ' + c.len + 's');
        if (r === 'credits') { window.__fqstopped = 'credits'; break; } }
      catch (e) { setSt(c.key, 'error: ' + e); log('error ' + c.key + ' ' + e); }
      await sl(opt.gapMs || 35000);
    }
  } finally { window.__fqrunning = false; log('done'); }
}
window.__fq = { upload, run, one, settings, pickStart, prompt, creditsGone,
  status: () => ({ running: !!window.__fqrunning, stopped: window.__fqstopped, state: st(), log: (window.__fqlog || []).slice(-6) }),
  reset: keys => { const s = st(); keys.forEach(k => delete s[k]); localStorage.__flow_q = JSON.stringify(s); }, stop: () => { window.__fqstop = true; } };
return 'flow queue ready';
})();
