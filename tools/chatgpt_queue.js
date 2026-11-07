// Bible Director Studio — ChatGPT image queue (paste into a chatgpt.com tab opened on the project
// "Ai Bible Imagery": https://chatgpt.com/g/g-p-6a7336d84f948191ba98f1852cc326d1/project ).
// Specs:  localStorage[`__bds_specs_${TAG}`] = JSON [{key, v, scene, refs:[idbKey...], prompt}]
// State:  localStorage[`__bds_q_${TAG}`]     = {key: 'ok'|'refused'|'error:...'}
// Images: IndexedDB '__bds' v2, store 'kv', under spec.key (reference portraits are read from there too).
// Start:  __q.run('g17')            (one new chat per scene; skips keys already 'ok')
//         __q.run('g17', ['g17_v05'])  (only these keys; clear their state first with __q.reset('g17',[...]))
// Status: __q.status('g17')
// Tip: after loading once, the source is also kept in localStorage.__qsrc -> eval(localStorage.__qsrc) in any chatgpt.com tab.
(() => {
// v2 (2026-10-30, fixed during Genesis 17): ChatGPT keeps hidden <main> elements of earlier chats, so all
// detection is scoped to the VISIBLE <main>; the image must sit AFTER the latest "You said:" turn; image
// v4 (2026-10-31, Genesis 18): new-turn detection by data-turn-key (see turnKey) — fixes 'message did not appear' on the 5th+ message of a chat.
// v3: waits until the previous answer is idle before pasting; requires the new user turn to appear; ignores images whose src existed before sending.
// generation shows "Creating image NN%" without a Stop button, so that text counts as busy (old code
// marked slow images as 'refused' and could hand the late image to the next key).
const sl = ms => new Promise(r => setTimeout(r, ms));
const PROJECT = '/g/g-p-6a7336d84f948191ba98f1852cc326d1/project';
const db = () => new Promise((res, rej) => { const o = indexedDB.open('__bds', 2);
  o.onupgradeneeded = () => { if (!o.result.objectStoreNames.contains('kv')) o.result.createObjectStore('kv'); };
  o.onsuccess = () => res(o.result); o.onerror = () => rej(o.error); });
const idb = async k => { const d = await db(); return new Promise((res, rej) => { const q = d.transaction('kv').objectStore('kv').get(k); q.onsuccess = () => res(q.result); q.onerror = () => rej(q.error); }); };
const idbPut = async (k, v) => { const d = await db(); return new Promise((res, rej) => { const t = d.transaction('kv', 'readwrite'); t.objectStore('kv').put(v, k); t.oncomplete = () => res(true); t.onerror = () => rej(t.error); }); };
const vm = () => [...document.querySelectorAll('main')].find(m => m.offsetParent) || document.body;
const editor = () => [...document.querySelectorAll('[contenteditable="true"]')].find(e => e.offsetParent);
const sendBtn = () => [...document.querySelectorAll('button[aria-label="Send"]')].find(b => b.offsetParent);
const stopping = () => [...document.querySelectorAll('button')].some(b => b.offsetParent && /^Stop/i.test(b.getAttribute('aria-label') || ''));
const users = () => [...vm().querySelectorAll('span')].filter(e => e.childElementCount === 0 && e.textContent.trim() === 'You said:');
const lastUser = () => users().pop();
// v4: ChatGPT virtualizes older turns (data-virtualized-turn-content), so the count of "You said:" stops growing after ~5 turns;
// detect the new user turn by the data-turn-key of the LAST user turn instead of by counting.
const turnKey = () => { const u = lastUser(); const t = u && u.closest('[data-turn-key]'); return t ? t.getAttribute('data-turn-key') : (u ? 'n' + users().length : ''); };
let seen = new Set();   // v3: srcs present before sending; an image counts only if it is NEW (fixes v25 receiving v24's picture)
const imgs = () => { const u = lastUser(); return [...vm().querySelectorAll('img')].filter(i => i.naturalWidth >= 512 && /Generated image/i.test(i.alt || '') && !seen.has(i.currentSrc || i.src) && (!u || (u.compareDocumentPosition(i) & 4))); };
const tail = () => { const u = lastUser(), m = vm(); if (!u) return ''; const r = document.createRange(); r.setStartAfter(u); r.setEndAfter(m.lastChild); return r.toString(); };
const busy = () => stopping() || /Creating image|Generating image|\b\d{1,3}%/i.test(tail().split('ChatGPT said:').pop());
const chips = () => [...document.querySelectorAll('button')].filter(b => /^Remove /.test(b.getAttribute('aria-label') || '')).length;
const st = tag => JSON.parse(localStorage[`__bds_q_${tag}`] || '{}');
const setSt = (tag, k, v) => { const s = st(tag); s[k] = v; localStorage[`__bds_q_${tag}`] = JSON.stringify(s); };
const log = m => { (window.__qlog = window.__qlog || []).push(new Date().toISOString().slice(11, 19) + ' ' + m); };
async function newChat() {
  const a = [...document.querySelectorAll('a')].find(a => (a.getAttribute('href') || '').endsWith(PROJECT));
  if (a) a.click(); else history.pushState({}, '', PROJECT);
  for (let i = 0; i < 30 && !(editor() && location.pathname.endsWith('/project')); i++) await sl(500);
  await sl(1500);
}
async function attach(keys) {
  if (!keys.length) return;
  const ed = editor(); const form = ed.closest('form') || document;
  const inp = [...form.querySelectorAll('input[type=file]')].find(i => i.multiple && !i.accept) || [...document.querySelectorAll('input[type=file]')].find(i => i.multiple && !i.accept);
  const dt = new DataTransfer();
  for (const k of keys) { const b = await idb(k); if (!b) throw 'missing ref ' + k; dt.items.add(new File([b], k + '.png', { type: 'image/png' })); }
  const before = chips(); inp.files = dt.files; inp.dispatchEvent(new Event('change', { bubbles: true }));
  for (let i = 0; i < 40 && chips() < before + keys.length; i++) await sl(500);
  await sl(6000);
}
async function one(tag, sp) {
  for (let i = 0; i < 100 && busy(); i++) await sl(3000);   // v3: never paste while the previous answer is still generating
  const ed = editor(); ed.focus();
  // v5 (2026-11-04, Genesis 19): ChatGPT can restore another tab's unsent draft into a fresh composer -> clear it first
  document.execCommand('selectAll', false); document.execCommand('delete', false); await sl(300);
  await attach(sp.refs || []);
  const dt = new DataTransfer(); dt.setData('text/plain', sp.prompt);
  editor().dispatchEvent(new ClipboardEvent('paste', { clipboardData: dt, bubbles: true, cancelable: true }));
  await sl(1200);
  const k0 = turnKey(); seen = new Set([...vm().querySelectorAll('img')].map(i => i.currentSrc || i.src));
  for (let i = 0; i < 60 && !(sendBtn() && !sendBtn().disabled); i++) await sl(500);
  sendBtn().click(); log('sent ' + sp.key);
  for (let i = 0; i < 60 && turnKey() === k0; i++) await sl(500);
  if (turnKey() === k0) throw 'message did not appear';
  const t0 = Date.now(); let idleSince = 0; await sl(8000);
  while (Date.now() - t0 < 8 * 60e3) {
    const b = busy();
    if (imgs().length && !b) break;
    if (b) idleSince = 0; else if (!idleSince) idleSince = Date.now();
    if (!b && idleSince && Date.now() - idleSince > 25e3 && Date.now() - t0 > 45e3 && !imgs().length) {
      setSt(tag, sp.key, 'refused: ' + tail().split('ChatGPT said:').pop().slice(0, 200).trim()); log('refused ' + sp.key); return; }
    await sl(3000);
  }
  if (!imgs().length) { setSt(tag, sp.key, 'error: timeout'); log('timeout ' + sp.key); return; }
  await sl(3000);
  const im = imgs().pop();
  const blob = await (await fetch(im.currentSrc || im.src)).blob();
  await idbPut(sp.key, blob); setSt(tag, sp.key, 'ok'); log(`ok ${sp.key} ${blob.size} ${location.pathname}`);
}
async function run(tag, only) {
  if (window.__qrunning) return 'already running';
  window.__qrunning = true; window.__qstop = false;
  try {
    const specs = JSON.parse(localStorage[`__bds_specs_${tag}`]);
    let scene = null;
    for (const sp of specs) {
      if (window.__qstop) break;
      if (only && !only.includes(sp.key)) continue;
      if (st(tag)[sp.key] === 'ok') continue;
      if (sp.scene !== scene || only) { await newChat(); scene = sp.scene; }
      try { await one(tag, sp); } catch (e) { setSt(tag, sp.key, 'error: ' + e); log('error ' + sp.key + ' ' + e); await newChat(); scene = null; }
      await sl(2000);
    }
  } finally { window.__qrunning = false; log('done'); }
}
window.__q = { run, idb, idbPut, status: tag => ({ running: !!window.__qrunning, state: st(tag), log: (window.__qlog || []).slice(-8) }),
  reset: (tag, keys) => { const s = st(tag); keys.forEach(k => delete s[k]); localStorage[`__bds_q_${tag}`] = JSON.stringify(s); },
  stop: () => { window.__qstop = true; } };
return 'queue ready';
})();
