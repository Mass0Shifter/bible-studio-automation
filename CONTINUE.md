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

## 1. What is happening right now (10 Nov 12:50) — PAUSED by the user
- **Esther Prophetic Implication: FINISHED & user-approved** — `Prophetic Implications\Esther\final\Esther_PI_final.mp4` (3:44, new PI caption style) + `_clean.mp4`. New style = no bar, bold white subtitles with black outline (≤2 lines × 5 words), spoken word highlighted in the badge's gold, gold point cards, sub-point titles without glow, no logo over the outro. How to render: `skill/prophetic-implication/SKILL.md` (end) + `tools/pi_captions.py`, `tools/pi/burn_piece.sh`, Windows job `CAT <Book>`.
- **Music is now −11.2 dB everywhere** (chapters too). **Voice: always Paz in Vids**; ElevenLabs only if Vids refuses.
- **Genesis 22–23–21 clips: PAUSED.** Helper was running the Vids queue (tag `g22`) on account **u/5 Precious Chikezie** (doc "Genesis 15 Clips", browser tab-5); g22 had reached v11 at 12:47. Check `productions/genesis/22.md` for the exact done/left list. Other accounts' Vids quota was used up on 10 Nov (u/0, u/1, u/4); u/2 has no AI video; u/3's duration slider is locked. Resume = reload vids_queue.js in a Vids doc with content, `__vqtag='g22'`, run (finished keys are skipped), then g23, g21.
- Windows render watcher (`_tools\win\watcher.bat`) must be open for renders.

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
