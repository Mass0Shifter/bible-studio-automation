# CONTINUE.md — hand-over for the next Claude session

_Written 2026-11-10 03:40 (Africa/Lagos) by the session that ran 7–10 Nov. Copies: PC `C:\Users\USER\Bible Studio\continue.md` and repo `Mass0Shifter/bible-studio-automation/CONTINUE.md` (same text)._

Read this whole file first. Then `QUICK_BRIEF.md` (repo; partly out of date — this file wins), `skill/SKILL.md` (how a chapter is made), `docs/ENVIRONMENT.md` (accounts table), `docs/LESSONS.md`.

---

## 0. The user and the rules (do not break these)
- User is **not a developer** — report in plain, short words. Wants everything documented aggressively (repo + this PC) as backup memory.
- **Never type passwords. Never use the Bible Studio app's paid AI buttons.** No e-mail addresses, signed upload links or keys in the repo (it's public). Google accounts are called **A–E** (A = `docs.google.com/videos/u/0` … E = `u/4`).
- **Video order: Google Vids → Flow (Omni Flash 1.1, the cheaper one) → Grok Imagine** (grok.com/imagine, only when Vids AND Flow refuse the prompt; 720p, 15 s max; 1080p is not on the plan).
- Spending **Flow credits** needs a yes from the user (they approved the Vids→Flow→Grok order for refused clips only).
- Audio fallback: **ElevenLabs** (user has a subscription; ~18,100 credits left on 10 Nov; speech-to-text also costs credits). Default voice is Vids "Paz"; Genesis 19 used ElevenLabs "Ralph – Slow, Protective, Wise" (Eleven v4).
- **At most lead + 1 helper agent** now (user: "use one more agent instead of two"); never more than 3 chapters at once.
- Cycle the 5 Google accounts for Vids allowance and **re-check which ones have reset** before saying "out".
- Can't delete files on the PC (no delete permission) — move junk to `_to_delete\` instead.
- User's messages shouldn't stop the work; use your own judgement when they're away.

## 1. What is happening right now (10 Nov 03:40)
**Top priority: Esther — Prophetic Implication film** (whole-book "prophetic implication" film, user asked for it fast; Genesis 21 is paused for it).
Title chosen: **"The Book Where God Is Never Named (But He's Everywhere)"**. Script approved. Storyboard shown (7 scenes, 42 shots).

| Step | State |
|---|---|
| Script | ✅ `Prophetic Implications\Esther\Esther_PI_script.md` (repo `productions/esther/PI_script.md`) |
| YouTube package (titles, thumbnails, tags, description) | ✅ `Esther_PI_youtube.md` — **chapter timestamps still estimates → replace** (see §3 step 7) |
| Storyboard | ✅ `Esther_PI_storyboard.md/.json` (42 shots; shot 42 = scene 7 outro) |
| App project | ✅ "Esther — Prophetic Implication" id `01a1bf45-9b32-724a-befe-008a6f896869` (workspace "The Book of Esther"; rows v1…v42 = shot order; file stems `Esther_1_1_10_3_S0n_SH0m`) |
| Pictures (ChatGPT) | 🟡 **running** — 34/41 in the app at 03:35; queue tag `ePI` in browser tab "chatgpt.com …ai-bible-imagery" (tab-8). Auto-uploader runs in the `chatgpt.com/robots.txt` tab (tab-2) and puts each finished picture into the app. Its upload links **expire ~04:30 on 10 Nov** — if pictures are still missing after that, see §2 "refresh links". Shot 42 (outro) needs no picture. |
| Intro card | ✅ `images\Esther_PI_INTRO.png` (also on r2 as `generated_shots/genesis-chapter-21-verse-1-scene-1-shot-1-a2m88k.png` — it was uploaded into a Genesis 21 slot only to get a public link) |
| Narration | ✅ `audio\Esther_PI_voiceover.wav/.mp4` 3:34.9 (Vids Paz, account B doc "Esther PI Narration") |
| Speech-to-text | ✅ `audio\Esther_PI_stt.json` (ElevenLabs) |
| Shot timings | ✅ `plans\windows.json` (42 shot windows, all aligned well), `plans\words.json`, `plans\shots_text.json` |
| Vids clip queue | ✅ built: `plans\vids_queue.json` by `plans\mkqueue.py` (34 clips, 215 s). **Not started yet.** Re-run `mkqueue.py` after updating `plans\imgs.json` with the last 7 pictures. |
| Music | 🟡 two takes in `music\_raw\` (take1 "Crown of Silk" 174 s, take2 "Beyond the Veil" 161 s). Needs extending to ~3:35 + ~10 s outro (repeat a middle section with acrossfade, like Genesis 19/20). Bed at −9.8 dB. |
| Clips / edit / finish | ⬜ |

## 2. How to pick up the Esther film — step by step
1. **Check pictures.** In a biblestudio.nachamtns.com tab:
   `const BDS=(await import('/bds-bridge.js?v='+Date.now())).default||window.BDS; const a=(await BDS.shots('01a1bf45-9b32-724a-befe-008a6f896869',{light:true})); a.filter(x=>!x.hasImage).map(x=>x.order)` (shots objects have `order, shotId, hasImage, imageUrl, fileStem`).
   - Missing ones still generating: look at tab-8 `__q.status('ePI')` (log lines `ok …`, `error …`). Retry errors with `__q.reset('ePI',[keys]); __q.run('ePI')`. Keys are `ePI_S<scene>_SH<shot>`.
   - Picture done in the queue but not in the app = upload link expired. **Refresh links**: in the app tab `BDS.uploadLink('shot_image', shotId)` gives a new signed link; put it into `localStorage.__LePI` (map key → [stem, link]) in the robots.txt tab, then `__upload({key: L[key]})` (code for `__upload` is in the session log of 10 Nov; it reads the picture from IndexedDB `__bds`/`kv`, converts to JPEG 0.93 and posts it through a hidden iframe form).
   - If the ChatGPT image limit hits: wait ~5–7 h, it resets.
2. **Update `plans\imgs.json`** (shot order → r2 path from `imageUrl`) and run `python3 mkqueue.py` in `Prophetic Implications\Esther\plans`.
3. **Vids clips** with `tools/vids_queue.js` (header of that file explains everything). Use account **B (u/1)** first (full on 9 Nov), then E, then re-check A, C, D. Open `docs.google.com/videos/u/1/create`, right panel → AI Video → Animate, load the source with the Trusted-Types trick (`trustedTypes.createPolicy('bds'+Date.now(),{createScript:s=>s}); eval(p.createScript(localStorage.__vqsrc))`), set `window.__vqtag='ePI'`, `window.__vq=<contents of vids_queue.json>`, `__vqueue.run()`. Clips download to `Downloads` as `<uuid>.tmp` or real name — match by size with `_tools\grab_tmp_by_size.py` and move to `Esther\video\Esther_PI_vNN.mp4`. Refused clips → Flow (Omni Flash 1.1) → Grok.
   - Also make an **intro animation** from the intro card (8 s, gentle push-in, light rays) — key `vINTRO`.
4. **Music**: extend the better take to ≈ 225 s (narration 214.9 s + outro). Save `music\Esther_PI_music.wav`.
5. **Plan + edit**: copy `Genesis 20\plans\mkplan20.py` as a model → `mkplanPI.py`: shots from `windows.json`, intro card + intro clip first, last shot = the channel outro `CAN_YOU_BEHOLD_HIM_OUTTRO.mp4` (same file Genesis 19/20 used) over shot 42's narration. Then `_tools\speech_fit.py` → `_tools\fit_edit.py` (re-run until it prints "wrote") → `_tools\finish.py` (re-run if cut off) → `_tools\film_check.py plans\finish.json`. **Subtitles: sentence subtitles with the KJV reference** from each shot's `ref` field (references are not spoken).
   - Keep each PC command ≤ ~170 s; the scripts are resumable (long background jobs on the PC get killed).
6. **Deliver** `final\Esther_PI_final.mp4` and `final\Esther_PI_clean.mp4` (clean = no subtitles), send to the user.
7. **YouTube chapters**: replace the estimated times in `Esther_PI_youtube.md` with real ones (scene starts in the final film = intro length + windows: Hook 0.0, One 30.0, Two 67.7, Three 109.5, Four 146.3, Summary 185.3 s of narration).
8. Update repo `productions/esther/PI.md`, `status.json`, `QUICK_BRIEF.md`, and this file.

## 3. After Esther: back to Genesis
- **Genesis 21** (paused): read `productions/genesis/21.md` "PAUSED" section — narration wav, STT, windows done; check verse 34 timing (came out 0.3 s); then quotes for divine/angel voices, `mkplan21` (copy of mkplan20.py), Vids queue, intro card + Paz intro line, music extend.
- **Genesis 22, 23**: pictures, voice, music done → clips + edit.
- **Genesis 24**: picture queue paused at 33/40. **25–27**: pictures 0; 26 needs music; 27 voiceover v1–20 + export + music. **28**: everything.
- Genesis 19 ✅ (6:05) and 20 ✅ (3:22) are finished — final + clean films in their `final\` folders.

## 4. Where things are
- PC folder: `C:\Users\USER\Bible Studio\` → `Genesis NN\` (audio, music, images, video, plans, final), `Prophetic Implications\Esther\`, `_tools\` (all scripts + SKILL.md copy). Downloads: `C:\Users\USER\Downloads`.
- Repo clone in the cloud session: `/home/claude/bible-studio-automation` (push with `git` — commit after every stage).
- App: https://biblestudio.nachamtns.com — bridge `await import('/bds-bridge.js?v='+Date.now())` (shots, verses, projectCharacters, uploadLink(kind,id), mediaLink). Upload from the PC: `curl -F "file=@x;filename=<stem>;type=..." "<signed link>"`.
- Public picture/video storage: `https://pub-2993fb3bf56d45ffb3d678320781fe03.r2.dev/` (generated_shots/, illustrations/, shot_videos/).
- ChatGPT project for scene pictures: "Ai Bible Imagery"; for thumbnails: "Can You Behold Him".
- Speech-to-text: ElevenLabs Speech to Text → paste an r2 link (page needs a 1500×900 window to show the link box) → Transcribe → open → Export → JSON → Download (`<title>_eng.json` in Downloads). Gemini can't do it from the browser pane.
- Browser pane tabs (10 Nov): app ×2, chatgpt.com ×2 (robots.txt uploader + project queue), ElevenLabs, Flow Music, Vids ×2. The pane holds ~9 tabs; use tabs_create, not preview_start.

## 5. Known problems and fixes
- PC goes to sleep / disconnects → ask the user to keep it awake and the Claude desktop app open.
- Claude 5-hour usage limit stops helper agents (one stopped 9 Nov with 9/41 Esther pictures; the queue kept running in the browser).
- Vids: after each clip the box collapses → Expand then Clear (script does it). "Exceeds your remaining quota" = account out; switch account.
- Vids refused "goes against our terms"/Flow "prominent people" (Genesis 20 v06) → Grok worked.
- ChatGPT tab blocks `eval` → paste the script source directly (or `(0,eval)(localStorage.__qsrc)` works on the robots.txt tab). Load reference pictures via `<img crossOrigin>` → canvas (toBlob hangs in background tabs).
- Large PNG uploads through the iframe form can fail silently → send JPEG 0.93.
