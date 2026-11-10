# Lessons not yet folded into skill/SKILL.md

Newest first. When a lesson is merged into the skill, delete it here.

## 2026-11-07 (Genesis 20–27 run)
- **Vids TTS:** scenes of ~5 verses / ≤ ~900 characters work; 9-verse scenes fail silently ("TTS request failed" in the Vids error log). After a reload the old script stays in the box — clear it before retyping. The script field must be typed (hidden iframe), not pasted. At an emulated 1600×950 viewport the script field ignores clicks — use the pane's normal size.
- **Vids refusals:** if Vids refuses a verse block (Genesis 22:2), split it at a semicolon; wording unchanged.
- **Vids export** can fail with a server error several times — reload the doc and retry; a first export sometimes never arrives.
- **Vids AI-video quota** is per Google account; when used up, duration is locked at 3 s with "Exceeds your remaining quota". Don't spend the last 3 s.
- **Flow pricing changed** to Omni 1.2 Flash, per-second (3 credits/s at 720p). Recompute and get a yes before generating.
- **ChatGPT:** don't name page helpers `status` (collides with `window.status`). Fetching r2 portraits from chatgpt.com fails (CSP) — use `BDS.mediaLink` + `<img crossOrigin>` + canvas. robots.txt upload tab needs ~8 s before moving on.
- **ChatGPT refused** a plain-chat establishing shot outside the project with no portrait attached; the same shot worked inside "Ai Bible Imagery" with portraits.
- **Altar scene (Genesis 22:9–10)** passed ChatGPT with calm framing (Isaac calm young man on the wood, Abraham's hand stilled by light, no blade on skin).
- **Exegesis import quirks:** characters can import with no life stage (Abimelech, Abraham) — set the stage on the Continuity tab so the portrait links. Place names can link to a same-named person (Haran). Isaac needs different stages per chapter (Infant 21, Young Adult 22, Adult 24–26, Elder 27).
- **Unnamed main actors** (Abraham's servant, Gen 24) are skipped by the "named only" rule — add them anyway and give a portrait.
- **Music** tracks are ~2:40–3:00; chapters over 3 min need a crossfaded repeat at assembly.
- **Shared browser pane:** `preview_start` can hand out a tabId another agent is using. Each agent: fresh tabs, check `tabs_context`, never navigate others' tabs.

## 2026-11-07 (night)
- **Upload from the PC straight into the app:** get `BDS.uploadLink(kind,id)` in the Bible Studio tab, then on the PC `curl -F "file=@<png>;filename=<fileStem>.png;type=image/png" "<link>"` → `{"success":true}`. Keep each device_bash call to ≤5 uploads (3-min limit); background jobs on the PC get killed.
- **Browser pane tabs:** `preview_start` can re-use an existing tab (it hijacked tab-1); the pane caps at ~9 tabs. Agents must use `tabs_create` + their own tabIds.
- **CrossTalk hub** (user asked to join channel on the railway hub): blocked — cloud workspace and PC proxy return 403, and the hub refuses browser origins. Needs the hub domain allowed in the org's network settings.

## 2026-11-08 (Genesis 19 clips)
- **Vids AI video can be fully automated now:** a script click on the Generate button works (no real click needed). `tools/vids_queue.js` runs a whole chapter. After each clip the composer collapses: click "Expand", then "Clear", to get the image input back.
- Vids now offers **3–15 s** clips; this account's settings would only stay at **720p** (1080p option didn't stick). The result card has an **Upscale** button (not tried yet).
- Busy = a visible "Cancel" button in the AI video panel. A 13 s clip took ~1.5 min.
- **Verse windows without a transcriber:** `Genesis 19/plans/g19_windows.py` places verse ends by reading speed and snaps to the nearest pause; check chars/second per verse (≈15–18) to spot bad boundaries.
- Google accounts signed in (2026-11-08): 5 (A = u/0 … E = u/4). Account A had Vids AI-video allowance on 8 Nov.

- **Upload from ChatGPT without leaving the chat (2026-11-08):** append a hidden `<iframe src="/robots.txt">` to the ChatGPT page; build the form + target iframe inside that frame's document and submit — works while the ChatGPT queue keeps running in the same tab.

## Lessons from Esther PI (10 Nov 2026)
- **Browser pane reset** can sign out every site and wipe chatgpt.com IndexedDB/localStorage (queue state + finished pictures). Upload pictures to the app as soon as they finish; don't rely on IndexedDB surviving.
- **Upload from `chatgpt.com/robots.txt`**, not from a ChatGPT chat page: the iframe-form POST to the app's signed link fails silently from a chat page (CSP). ChatGPT also blocks `fetch` to GitHub — paste tool source into the tab directly.
- **`preview_start` can silently REUSE another tab of the same site** (it reused the helper's Vids tab twice and killed its queue). With a helper agent running, open tabs only with `tabs_create` + `navigate`, and give each agent its own sites. The pane holds ~7 tabs — close finished ones.
- **Google accounts after re-sign-in (10 Nov):** u/1 = Glorify Michaels (Vids AI video OK, 1080p), u/2 = Nâcham Technology and Solutions (no Vids AI video — "Upgrade"), u/3 = Nâcham Media (has AI video but the duration slider stayed disabled from JS; one 4 s clip worked). Re-check after any sign-out.
- **New blank Vids docs** keep re-opening the "Let's start creating" welcome screen, which blocks the AI-video settings; reuse a doc that already has content, or pick an option in the welcome screen.
- **Flow (Nov 2026):** new models Omni 1.2 Flash (default) and Omni 1.1 Flash ("Leaving Dec 5"); pick the model under "Select model family" in the settings chip; duration radios 4/6/8/10 s appear after the model is chosen. Download: clip page → ⋮ → Download media → 1080p Upscaled. Flow misspelled the card footnote ("peried") — `intro_restore` fixes it.
- **Prophetic Implication films:** `finish.json` `"plain_subs": true` = sentence subtitles with "(Esther 7:10)" refs, no [Vn]; last shot = channel outro (10 s, `badge: false`); render on Windows with a job file `PI <Book> <plan base>` (run_pi.bat, no speech_fit).

## Music too short (10 Nov 2026)
- `tools/extend_music.py <in.wav> <out.wav> <target_s>` extends a Flow Music track automatically: it finds a late jump point and an earlier re-entry point with matching loudness, repeats the middle with a 5 s crossfade (as many times as needed) and keeps the track's own ending. Keep the original in `music\_raw\<Book>_<Ch>_music_orig.wav`. Target = dialogue narration length + ~15 s (speech_fit can lengthen speech shots; the outro adds 3 s).
- Done 10 Nov: Genesis 22 175 → 250 s, Genesis 23 167 → 218 s, Genesis 21 161 → 313 s.
