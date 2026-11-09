---
name: bible-director-production
description: Produce a Bible chapter end-to-end in Bible Director Studio (biblestudio.nachamtns.com) when the user says things like "Create Genesis Chapter 6" — workspace, project, exegesis, characters, storyboard, ChatGPT images, Google Vids voiceover, video clips from Google Vids AI video (default, free) or Google Flow when the user says "using Flow", and Flow music.
---

# Bible Director Studio — chapter production

> Synced from the PC copy `Bible Studio\_tools\SKILL.md` on 2026-11-07. The media folder is `C:\Users\USER\Bible Studio` on the Oct–Nov PC and `Desktop\Bible Studio` on revivalist-hp — see `docs/ENVIRONMENT.md`. Helper scripts it names are in `tools/` of this repo.

The user (Nâcham Media) produces KJV Bible chapter films in their own app, **Bible Director Studio** (live: `https://biblestudio.nachamtns.com`, repo: `Mass0Shifter/bible-director-studio`, Laravel + Inertia). A request like **"Create Genesis Chapter 6"** means: run the pipeline below for that passage.

**Cost rule:** never use the app's paid AI buttons ("1-Click AI Exegesis", "1-Click AI Storyboard", "Render AI", "Synthesize Voiceover TTS", "Batch Render") — they spend API keys. Text JSON is written by Claude itself; images come from ChatGPT (subscription); voice from Google Vids; video clips from Google Vids AI video by default (free) or Google Flow when the user asks for Flow (subscription credits); music from Google Flow Music (subscription credits).

The user is not a developer: report progress in plain words, never ask them to run code. When the user asks for a partial run (e.g. "shots 2 and 3 then stop", "verses 1 and 2 then let me review"), do exactly that and stop for review. Never spend Flow credits beyond what was asked without a yes; never push to `main` without a yes.

## 0. Setup (every run)

1. **Browser.** Use the built-in browser pane (fall back to Claude in Chrome if the user asks). Tabs needed: Bible Studio, ChatGPT (`https://chatgpt.com`), Google Flow (`https://flow.google.com`), Google Vids (`https://docs.google.com/videos`), Google Flow Music (`https://www.flowmusic.app`). If a site shows a sign-in page, ask the user to sign in themselves — never type passwords. The pane does not open popups: anything with target=_blank loads in the same tab as a GET. The javascript tool times out after ~45 s: start long jobs without awaiting them and poll; keep the working tab in front (background tabs are throttled).
   **ChatGPT:** do all image, portrait and exegesis chats inside the ChatGPT project **"Ai Bible Imagery"** (`https://chatgpt.com/g/g-p-6a7336d84f948191ba98f1852cc326d1/project`) — new chat per character portrait and per storyboard scene. Never use the project "Can You Behold Him" (reserved for YouTube thumbnails).
2. **Load the bridge** in the Bible Studio tab (javascript tool):
   ```js
   delete window.BDS; await import('/bds-bridge.js?v=' + Date.now()); await BDS.help()
   ```
   If `/bds-bridge.js` 404s (not deployed yet) and the repo folder is linked, read `public/bds-bridge.js` from the repo and execute its contents in the tab instead. Re-load the bridge after any full page reload.
3. **Progress log.** Keep `automation/productions/<book>-<chapter>.md` in the repo folder (e.g. `genesis-6.md`: chat links, Flow/Vids/Music links, credits, decisions, lessons) — append one line per finished stage with project id, counts and anything that needs the user. This is the backup memory the user asked for; update it as you go, not only at the end.

Every bridge call throws a readable error on failure (validation errors, expired session, not signed in). Read it, fix, retry once; then tell the user.

## 1–2. Workspace + project

```js
const r = await BDS.setup('Create Genesis Chapter 6');   // parse → switch/create "The Book …" workspace → create project
r   // { parsed:{reference:'Genesis 6:1-22', title:'Genesis Chapter 6', …}, workspace:{name, created}, project:{id, existed} }
```
- The project list only shows the ACTIVE workspace, so always switch workspace before looking for a project (setup does this).
- Workspaces are named after books ("The Book Genesis", "The Book of Ruth and Jonah"). Matching is whole-word; a new workspace is created as "The Book of X" only when none matches — say so.
- If `project.existed` is true, a project for that exact passage already exists: **ask** whether to continue it or create a fresh one (`BDS.createProject(parsed, {force:true})`).
- Defaults: style `photorealistic_historical`, 16:9, the matching style anchor prompt. Override with `{style, aspect}` only if the user asks.

## 3. Exegesis (Claude writes the JSON — no API cost)

```js
const prompt = await BDS.exegesisPrompt(id)
```
Read the prompt and follow it exactly (character extraction rules, output schema). Write the JSON yourself, then:
```js
await BDS.importExegesis(id, json)   // returns project status incl. entities
```
If the user prefers ChatGPT for this, paste the prompt into a new ChatGPT chat, read the JSON reply from the page, and import that instead.

## 4. Characters — progressive profiles + portraits (BEFORE scene images)

Characters can look different across Scripture (Shem: infant in Genesis 5, adult in Genesis 6). The app stores this as **life stages** on each Workspace Library character (Character Library page, top menu → each character card → "Life Stages"). Each stage has its own age, attire, face, prompt anchor and portrait. Each project uses ONE stage per character (project → **Continuity & World Studio** tab → "Life stage in this passage" picker). The exegesis prompt asks for each character's `life_stage` in THIS passage and the importer creates/reuses the stage automatically.

1. After importing exegesis: `await BDS.projectCharacters(id)` → per character: `stageLabel`, `stageAge`, `promptAnchor`, `portrait`, `appearances` (storyboard shots showing them), `uploadKind` + `uploadId`.
   - Check each character's stage fits the passage (an infant description in a chapter where they are grown = wrong). If wrong or missing, tell the user and fix it in the Character Library (add/edit the stage) or switch the project's stage on the Continuity tab — do not silently edit.
2. Who gets a portrait: characters who physically **appear** (act/speak/are shown) in more than one shot or verse — not ones only mentioned. Skip crowds and God/the LORD (never depicted). `await BDS.charactersNeedingReference(id)` lists those whose current stage has no portrait (once a storyboard exists it keeps only those shown in 2+ shots).
   A character already portrayed at the same stage in an earlier chapter keeps that portrait — reuse, don't regenerate.
3. For each: `await BDS.characterPortraitPrompt(projectEntityId, id)` (= the stage's prompt anchor exactly as the Copy Prompt button gives it, plus one framing line) → new chat inside the ChatGPT project "Ai Bible Imagery" → wait for the image.
4. Upload it against that character (and stage): Studio tab `const url = await BDS.uploadLink(c.uploadKind, c.uploadId)`; run `BDS.senderScript(url, PICK_CHATGPT_IMAGE, '<Name>_<Stage>')` in the ChatGPT tab; read the `{"success":true…}` page; navigate back. The portrait appears on the Character Library card's stage and on every project using that stage. Never click "Render Benchmark Portrait" (paid AI).
5. Show the user the portraits and let them reject any before generating scene images.

`PICK_CHATGPT_IMAGE` (last generated image in the chat — verified 2026-10-12: ChatGPT shows finished images as `blob:` URLs with alt "Generated image 1", 1672×941 PNG for 16:9):
```js
[...document.querySelectorAll('main img')].filter(i => i.naturalWidth >= 512 && !/avatar|profile/i.test(i.alt||'')).map(i => i.currentSrc || i.src).pop()
```

## 5. Storyboard (Claude writes the JSON)

```js
const sp = await BDS.storyboardPrompt(id)
```
Follow it exactly. Hard rule from the prompt: **gapless verse coverage** — every verse from first to last appears in exactly one shot, in order (single verses or ranges). Before importing, check coverage yourself. Then:
```js
await BDS.importStoryboard(id, json)
const rows = await BDS.shots(id)   // per shot: order, scene, shot, verse, narration, speaker, imagePrompt, motionPrompt, referenceLinks, hasImage, hasVideo, fileStem
```
Report scenes/shots count and the verse map to the user.

## 6. Shot images in ChatGPT

For each row with `!hasImage`, in order (`row.characters` lists the characters in the shot with their stage and `portrait` URL):
1. Paste `row.imagePrompt` into ChatGPT (one chat per scene inside "Ai Bible Imagery" keeps the look consistent; start a new chat for a new scene).
   **Character continuity:** if `row.characters` includes a character with a `portrait`, attach that portrait before sending: Studio tab `await BDS.mediaLink(portraitUrl)` (signed, CORS-open link) → in the ChatGPT tab load it into an `<img crossOrigin="anonymous">`, draw it on a canvas, `canvas.toBlob` → `new File([...], '<Name>.png')` → put it into ChatGPT's general file input (`input[type=file][multiple]` without an `accept` filter) via DataTransfer and fire `change`; wait for the attachment chip. Start the prompt with: "Reference image attached: this is <Name>. Keep his face, hair, beard and build exactly; generate a new 16:9 scene image:".
   Verified method: focus the composer (`#prompt-textarea`, or `[contenteditable="true"]` if that id is missing) and dispatch a `paste` ClipboardEvent carrying the prompt as `text/plain` (typing would send on the first newline); then click the **Send** button (find "Send").
2. Wait for the image to finish: poll until the chat has one more `main img` ≥512px wide and no Stop button is showing; don't re-send.
3. Studio tab: `url = await BDS.uploadLink('shot_image', row.shotId)`; run `BDS.senderScript(url, PICK_CHATGPT_IMAGE, row.fileStem)` in the ChatGPT tab, read the `{"success":true…}` page, navigate back to the chat.
   Do NOT use fetch() from the ChatGPT tab to Bible Studio — ChatGPT's Content-Security-Policy blocks it ("Failed to fetch").
4. Every ~5 shots, re-check with `BDS.shots(id, {light:true})` and log progress.

**Genealogies — every man must look different (user rule, 2026-10-19).** In family-line chapters (Genesis 5, 10, 11, 25, 36, 1 Chronicles…) ChatGPT tends to give every patriarch the same face, beard and striped robe, so viewers cannot tell father from son. Before generating, write a short **look card** for each named man and add it to every prompt he appears in: robe colour + pattern (e.g. deep indigo plain wool / rust-red with black bands / undyed cream with a green sash), headwear (none / leather headband / wrapped turban / hood), beard and hair (length, colour, braided or not), age and build, one distinguishing detail (staff, scar, necklace). No two consecutive generations share a robe colour or headwear. Add to the prompt: "His face must be clearly different from the previous generation's man (<name>)." Keep the same look card for the same man in every shot of the chapter. Applies to future productions (Genesis 5 was made before this rule and stays as is).

**Deaths ("and he died").** ChatGPT and Flow refuse deathbed scenes with grief or tears ("guardrails around violence", "harmful content"). Use: "<Name>, a very old patriarch, sits contentedly / rests peacefully with eyes gently closed and a faint smile; his family sits calmly around him; warm, serene, dignified; no injury, no distress, no tears." A sitting-on-a-bench-at-sunset version passes most reliably. If Flow refuses the clip, calm the start image in Flow Image mode (family calm and smiling, no tears) and retry.

**Unclothed figures.** Flow refuses Eden images where Adam and Eve are bare ("sexual content"). Dress them first in Flow Image mode: "Keep the scene and people unchanged, dress them modestly in simple soft brown animal-skin tunics."

**Uploading from ChatGPT without leaving the chat:** do the form POST from `https://chatgpt.com/robots.txt` in a spare tab (same origin, so the IndexedDB image store is readable; light page). Images harvested from chats are kept in IndexedDB (e.g. `g5imgs`) keyed by verse.
If ChatGPT hits a usage limit, stop, log where you stopped, and tell the user when it says it resets.

## 7. Voiceover in Google Vids (voice: Paz)

```js
const plan = await BDS.voiceoverPlan(id, 5)   // 22 verses → scenes 1-5, 6-10, 11-15, 16-22 (last scene takes the remainder)
```
Exact KJV text only — no headings, verse numbers or added words.
1. Google Vids → Blank vid → **Landscape**. Title it with the project title (e.g. "Genesis Chapter 6"). If the side panel is hidden in the narrow pane, emulate a 1600×950 viewport (resize tool) while working in Vids, and reset it afterwards.
2. Add one Vids scene per plan entry — **Ctrl+M** adds a scene (the + button misfires).
3. Voiceover panel → **Current scene** → click the "Enter…" script field, then type (the real input is hidden) that entry's `script` → voice **Change → Paz (Breathy, low pitch) → Select** → **Insert voiceover**. Move to the next scene (› arrow) and repeat.
4. Confirm the timeline shows one voiceover clip per scene and the total duration looks right.
5. **Name the doc for this chapter (user rule, 2026-11-04).** When reusing an older Vids doc (e.g. a copy of an earlier chapter's), rename it first via the title box (aria "Rename") to `<Book> <Ch> Narration` — never leave names like "Copy of Genesis 10 Intro". Vids also auto-saves its own download named after the doc, so the doc name must say which chapter it is.
6. **Length cap:** a Vids scene export stops at the scene length (53 s in the reused doc) and silently cuts longer narration. Keep each recorded part ≤ ~620 characters (≈ 35–40 s at Paz's ~17 chars/s), and check every export: audio duration well under the video length and silence at the end. After "Replace", confirm the panel no longer shows **"Voiceover outdated"** and the timeline clip starts with the new words before exporting — otherwise the export still holds the previous part.

## 8. Export the voiceover to the PC

File → Download → MP4. Downloading needs the user's OK (state the file name first). Production folder on the PC: `C:\Users\USER\Bible Studio\<Book> <Chapter>\` with subfolders `audio\`, `images\`, `video\`, `music\`, `plans\`, `final\`. If that folder isn't connected to the session, ask for access to `C:\Users\USER\Bible Studio` once. Move the export to `audio\<Book>_<Chapter>_voiceover.mp4`.

## 9. Video clips — which engine (user rule, 2026-10-22)

- **Order (user rule, 2026-11-07): Google Vids → Google Flow → Grok Imagine.** Use Vids AI video first (free, Omni, 1080p; 9V). When Vids can't (quota used up on every signed-in Google account, or it refuses), use Google Flow with **Omni Flash 1.1** (9F; tell the user the credit total first). Only when Omni Flash rejects the prompt/start image, use Grok Imagine (see "Fallback tools").
- Cycle the user's signed-in Google accounts (5–7) for Vids quota and Flow credits before moving down the order; keep the per-account table in `docs/ENVIRONMENT.md`.
- 9a (measuring the verses) and 9d (fitting the clips) are the same for both engines. Character-speech, death-scene and unclothed-figure rules apply to both.

**9V. Generate in Google Vids (default, no credits).** Tested 2026-10-22 on Genesis 10 shots.
1. Open a separate Vids doc for the chapter's clips, titled `<Book> <Ch> Clips` (not the voiceover doc). Right panel → **AI Video** → **Animate** tab. Settings chip at the bottom: model **Omni** (the only one), **1080p**, **Landscape**, duration slider **3–10 s in 1 s steps** (finer than Flow).
2. Clip length per shot = `ceil(window + 0.5)`, clamped to 3–10 s; a verse longer than ~10.5 s gets 10 s and is slowed in 9d, as with Flow.
3. Per shot (JS in the Vids tab plus two real clicks):
   - **Clear** (bottom right of the composer) to empty the previous prompt and picture.
   - Start picture: fetch the shot's Bible Studio `imageUrl` (the r2 URL is readable from docs.google.com) → `new File([blob], '<fileStem>.png')` → set it on `input[type=file][accept*="image/png"]` with a DataTransfer and dispatch `change`. The thumbnail appears in the composer.
   - Prompt: focus the contenteditable whose aria-label is "Add your image, then describe what should happen in your video." → `document.execCommand('insertText', false, prompt)`. Same prompt style as Flow (camera move, action, "Keep every face, beard and garment exactly as in the start image. No narration, no voiceover, no dialogue, no music, no text on screen. Natural ambient sound only.").
   - Length: click the settings chip (`Omni • 1080p • ▭ • 10s`), set `input[type=range][aria-label="Video duration"]` with the native value setter + `input`/`change` events, Escape, and **check the chip now shows the right `• Ns`** before generating.
   - Click the blue ↑ arrow (real click). A 6 s clip took ~95 s; the panel shows a % counter, then the toast "Your generated video is ready for preview".
4. **Save each clip immediately** — Vids warns "Videos that aren't inserted will be discarded when you close this tab", and there is no Download item on a clip (⋮ only has Remove). The finished clip is a `<video>` in the panel with a `https://contribution-qw.usercontent.google.com/download?...` src: remember the srcs seen before generating, find the new one, `fetch(src, {credentials:'include'})` → blob → `<a download="<fileStem>.mp4">` click. It lands in Downloads as `<uuid>.tmp`: copy it to `video\<Book>_<Ch>_<fileStem>.mp4` right away (or identify by first frame with `match_clips.py`). Result: exactly the requested length, 1920×1080, ~10–11 Mb/s, with the clip's own natural sound, Google's small sparkle **watermark in the lower right** (covered with the user's badge, step 6). Optionally click **Insert** afterwards so the clip is also kept in the Vids doc as a backup.
5. Work through the shots one at a time (one generation shows in the panel at a time; ~1.5 min per clip → about 50–60 min for 32 shots). If Vids refuses a prompt or a daily limit message appears, tell the user and offer Flow for the remaining shots.
6. **Cover the Vids watermark (default for Vids-made films).** Raw Vids clips carry Google's small sparkle watermark in the lower right (centre ≈ x 1740, y 898 on 1920×1080, ~75 px). Put the user's badge over it in both films: add to the edit plan (9d) **and** to `finish.json` (11)
   `"badge": {"image": "../../_tools/references/Radiant Golden Portal Emblem.png", "cx": 1740, "cy": 898, "size": 150}`
   (repo copy: `automation/references/Radiant Golden Portal Emblem.png`). `fit_edit.py` overlays it on every shot (a shot with `"badge": false` — e.g. a Flow clip mixed in — stays bare); `finish.py` draws it again on top of the subtitle bar and stops the verse text column 30 px short of it so captions never run under it. Check one frame at full size: the sparkle must be completely hidden. Flow-made films don't get the badge (no watermark) unless the user asks.
7. Then 9d (fit_edit), finishing (11) as usual.

## 9F. Video clips in Google Flow (only when the user asks for Flow)

Flow is `https://flow.google.com` (Google Flow, model **Omni 1.1 Flash**). One Flow project per chapter, named after the project (e.g. "Genesis 6").

**9a. Measure the verses first (free, before spending credits).** The Vids voiceover is the clock. On the PC:
`ffmpeg -i audio/<Book>_<Ch>_voiceover.wav -af silencedetect=noise=-38dB:d=0.35 -f null -`
Pauses ≈0.8 s are verse/paragraph ends; 0.3–0.6 s are commas inside a verse. Map them to verses using word counts (Paz reads ≈0.27 s per word incl. pauses). Each shot's window = from the middle of the pause before its verse to the middle of the pause after it. Write the windows into the plan file (9d). Genesis 6 scene 1: v1 0–6.13, v2 6.13–13.08, v3 13.08–22.62, v4 22.62–35.03.

**9b. Pick the clip length per verse.** Omni Flash offers 4s / 6s / 8s / 10s (8s = 12 credits, 10s = 15 credits — about 1.5 credits per second). Choose the shortest length ≥ window + 0.5 s; anything longer than 10 s gets a 10s clip and is stretched for free in the edit (9d). Short verses use 4s/6s clips and save credits. Tell the user the total credits before generating and get a yes.

**9c. Generate.**
- Get the shot images into Flow: in the Bible Studio tab `await BDS.mediaLink(row.imageUrl)` for each shot (signed, CORS-open); in the Flow project tab fetch them into `File`s named `<fileStem>.png` and dispatch `dragenter`/`dragover`/`drop` DragEvents (with a DataTransfer holding the files) on `document.elementFromPoint(innerWidth/2, innerHeight*0.45)` — dropping on `main` does nothing. They appear as image tiles named after the files.
- Prompt bar: **Start** → pick the shot image (the picker list re-orders; check the thumbnail before generating). After picking, wait ~2.5 s before typing the prompt (Flow clears the box when the start frame loads), and read the settings chip back before every Generate (a length click sometimes doesn't register). Settings chip (`Video · 720p · 8s · x1`) → Video, **Frames**, 16:9, **Omni 1.1 Flash**, 720p, length from 9b, x1. The chip shows the credit cost.
- Prompt = the shot's motion prompt (`row.motionPrompt`, without the `[ANIMATION & MOTION PROMPT]` header) + the audio rule:
  - normally append *"No narration, no voiceover, no dialogue. Natural ambient sound only."*
  - if the shot is first-person speech (`row.speaker` is a character, or the narration is a quoted line that character speaks), append *`<Character> speaks: "<exact quoted KJV words>"`* and nothing else spoken. God/the LORD is never shown speaking on screen.
  - **Character speech (user rule, verified on Genesis 4:9, 2026-10-19).** When a human character's own words are quoted, the CHARACTER says them on screen in Flow's own generated voice (the user wants the character to have his own voice) and the narrator is silent for those words. The narrator keeps the framing ("And he said,") and anything God says. Steps:
    1. Find the quote in the voiceover: `silencedetect=n=-35dB:d=0.12` over the verse window; note where the narrator's framing ends and the quote starts/ends.
    2. Make a close-up start image of the speaker (Flow Image mode from the shot image: "same man, same face and clothing, medium close-up chest up, face clearly lit, mouth closed, looking slightly off to the side as if answering someone unseen").
    3. Generate a 6s clip (Frames, start = the close-up): *"Static camera, slight slow push in. <Name> … answers <tone>, in a low, rough adult male voice, with clear lip movement: "<exact KJV words>" After the line he … looks away. He speaks only this one line, once. No narrator, no other voices, no music. Natural ambient wind only."*
    4. Download; `silencedetect=n=-30dB:d=0.15` on the clip to find where the speech starts; pre-trim the clip so the speech starts ≈0.3–0.4 s after the cut (`ffmpeg -ss <t> … -c:v libx264 -crf 16 -c:a aac` → `<Book>_<Ch>_S<x>_SH<y>b.mp4`).
    5. In the fit_edit plan split the verse into two shots with the SAME `verse` number: the original clip up to just after the narrator's framing, then the speech clip with `"clip_gain": 1.3` (placeholder — its own audio at full level instead of the 0.22 ambience; `speech_fit.py` replaces it, see below); add plan-level `"vo_mute": [[start, end]]` (voiceover seconds) covering the narrator's reading of the quote, starting just after "And he said,". finish.py merges consecutive shots of the same verse into one subtitle span. Send the user a ~12 s preview of the moment.
- A "harmful content related to minors" refusal (refunded) can hit family scenes with youthful-looking sons: describe them as "grown, bearded men" and retry.
- If an image upload to Bible Studio returns 503, send it as JPEG (canvas → `image/jpeg` 0.93) — large PNGs get refused; always check the `{"success":true}` page.
- If Flow refuses a shot ("might violate our policies" — refunded), it is usually the start image itself (distress, crowds in chaos). Soften the prompt once; if it still fails, use a still-image push-in or make a calmer image.
- To change who is in a picture (e.g. only Noah's family at the ark), edit the start image in Flow's **Image** mode first (Nano Banana, 0 credits): add the shot image as ingredient, instruct what to keep and remove, then generate the clip from the edited image. In Image mode the Start-generation button needs a real click.
- **Start generation**. Two generations can run side by side; a 10s clip takes about 1–2 minutes.
- Download — **always 1080p (user rule, 2026-10-22).** Open the clip (click its tile → edit view) → ⋮ → **Download media → "1080p Upscaled"**. Flow first upscales the clip (toast "Upscaling your video… may take several minutes"), then the download starts by itself — this looks like a stall but is normal: **wait for it** (Genesis 10: ~45 s per clip, 1920×1080, ~11 Mb/s vs ~5 Mb/s at 720p; no extra credits). Run **one upscale at a time** (Flow asks not to start several): wait until the toast is gone and the file has landed before starting the next clip. Never fall back to "720p Original size" (the tile's right-click → Download is 720p — don't use it for the film). In the browser pane downloads land in Downloads as `<uuid>.tmp` files and may arrive out of order, so identify each clip by its **first frame**: compare it with the shot images (64×36 grayscale correlation; a match scores >0.95) — `automation/assemble/match_clips.py` does this — then copy to `video\<Book>_<Ch>_S<scene>_SH<shot>.mp4`. Always click Flow menu items by name, never by coordinates (one coordinate click once hit "Move to trash").
- A generation stuck at 99 % for more than ~10 minutes has failed silently: reload the project page and generate that shot again.
- Getting images into an existing Flow project: open the Start picker, `dragenter`+`dragover` on the element at the dialog's centre, wait ~0.7 s, then `dragenter`/`dragover`/`drop` again on the element now at that point (a drop overlay appears). Dropping on the tile grid does nothing.
- Optional hand-off back to Bible Studio: `uploadLink('shot_video', row.shotId)` + `senderScript(url, PICK_FLOW_VIDEO, row.fileStem)` in the Flow tab.

**9d. Fit the clips to the verses (free).** `python3 automation/assemble/fit_edit.py plan.json` (in the repo; on the user's PC the repo is `Dev Projects\Kingdom Tools\bible-director-studio`, the media is `C:\Users\USER\Bible Studio`) renders an edit from a plan: voiceover, music, music gain, and per shot the clip + its verse window. For each shot it needs window + 0.5 s (the dissolve) and:
- clip long enough → trim (keeps the start of the clip, which is the shot image);
- up to 25 % short → **slow**: plays the clip slower with motion interpolation (e.g. 10s → 12.4s at 0.81× speed);
- more than 25 % short → **lead**: holds the clip's first frame with a slow pull-out for the missing seconds, then plays the clip (seamless because the clip starts on that frame);
- a shot can force `"method": "slow"` or `"lead"`. A verse more than ~5 s longer than a 10s clip: generate a second angle (new ChatGPT image as start frame) or use Flow's extend — costs credits, ask first.
Plans live in `<Book> <Ch>\plans\` next to the media. The script renders piece by piece (shot bodies and 0.5 s dissolves as separate files in `~/.fit_edit_work/`, joined at the end) so a 3-minute chapter works in a shell that stops commands after ~3 minutes: keep re-running `python3 fit_edit.py plan.json` until it prints `wrote …` (Genesis 6: ~7 runs). A shot with no Flow clip (e.g. Flow refused the image) can use a still clip made from its image with a slow push-in (`ffmpeg -loop 1 … zoompan`, plus silent audio). The PC shell stops commands after ~3 minutes, so slow-motion is rendered in short chunks into a cached `<clip>.slow<NNNN>.mp4`: if the script says "run the same command again", do so — it continues where it stopped. Connected PC folders don't allow deleting files: move scrap files into `<Book> <Ch>\_to_delete\` and tell the user.

## 10. Music + final assembly

1. From the exegesis themes and the chapter's mood, write one instrumental brief (tempo, instruments, emotional arc, "Instrumental only, no vocals, no choir words, no lyrics", length ≈ voiceover length, "keep the midrange gentle and leave space for the voice").
   - Google Flow Music is its own site: `https://www.flowmusic.app` (separate sign-in — ask the user). Click **New session**, type the brief into "Let's create…", press the send arrow. The Producer writes a sound prompt and renders in ~30–60 s; the session is titled from the brief.
   - Download: the track's ⋯ → Download → WAV menu did not save a file in the browser pane. Instead read the clip's `wav_url` from the `POST /__api/clips` response (network log; `storage.googleapis.com/producer-app-public/clips/<clip_id>.wav`), then in the Flow Music tab: `fetch(wav_url).then(r=>r.blob())` → blob link with `download='<Book>_<Chapter>_music.wav'` → click. Copy from Downloads to `music\`.
   - Tracks come out around 2:50; if the voiceover is longer, extend by repeating a middle section with a crossfade so the track's own ending closes the film (Genesis 6: 0–82 s + 60 s–end, 4 s `acrossfade`).
2. Assemble on the PC with `automation/assemble/fit_edit.py` (device shell) — one plan covering every shot (9d): clips from `video\` in shot order, fitted to their verse windows, conformed to 1920×1080/24fps with 0.5 s dissolves, the Vids voiceover as the narration track, music underneath with fades at **−9.8 dB** gain on the Flow Music track (the user's standard after reviewing Genesis 6 — −13.5 dB and −12.1 dB were too low; the mix lands ≈ −17 LUFS), the clips' own natural sound low underneath (`ambient_gain` 0.22). For a character-speech shot the clip's own audio carries the spoken words: per-shot `"clip_gain"` (default = `ambient_gain`) and plan-level `"vo_mute"` (see 9c, Character speech). Output `final\<Book>_<Chapter>_final.mp4`.
3. Send the user the final file and a short summary; finish the log.

## 11. Intro, subtitles and logo (finishing)

References (images + exact prompts): `references/` in the bible-studio-automation repo (also `automation/references/` in the app repo), copies on the PC in `C:\Users\USER\Bible Studio\_tools\references\` — see `PROMPTS.md` there.

**11a. Two films per chapter (always).** `final\<Book>_<Ch>_clean.mp4` = the chapter film alone (no intro, no subtitles, no logo — the backup the user cuts other content from) and `final\<Book>_<Ch>_final.mp4` = intro + film with subtitles and logo. Deliver both.

**Intro — which kind.** Chapter 1 of a book → **book intro** (35–50 s). Chapters 2+ → **chapter intro** (3–6 s; the card can be held/stretched to 6 s). The intro plays before the chapter film and has no subtitles and no logo.

**11b. Intro card (ChatGPT, project "Ai Bible Imagery").** The template also lives in the user's ChatGPT chat "Placeholder Bible Layout" (`https://chatgpt.com/c/6ad1cc13-2c1c-83ea-89b2-6a7a626bbd5f`, image "Generated image 1"): open it, draw that image on a canvas, keep it as a JPEG data URL in `localStorage`, then in a new chat in the project rebuild it as a File (decode with `atob` — `fetch(dataURL)` is blocked by ChatGPT's CSP) and put it, with the characters' portraits (Bible Studio `BDS.mediaLink` → `<img crossOrigin>` → canvas → File), into the general file input. Attach `intro-card-template.png` and ask ChatGPT to fill it for this book/chapter, matching the template's layout, gold typography and colours exactly:
- title "THE BOOK OF" + book name; chapter intro: "CHAPTER <N>" under it; book intro: a tagline instead (e.g. "The Story of Ruth, Naomi & Boaz") — no chapter line;
- the two silhouettes become the chapter's main characters (their Character Library portraits/stages attached for likeness; God is never depicted); background fitting the chapter's setting;
- the four facts: AUTHOR, CHAPTERS (book's chapter count), SETTING, PERIOD (+ footnote "*Approximate historical period; exact dating is uncertain." when dating is uncertain);
- one key KJV line from the chapter (chapter intro) or verse 1:1 (book intro) with the reference under it, a few words highlighted in gold.
Examples: `chapter-intro-example-ruth-2.jpg`, `book-intro-example-ruth.jpg`. **Proofread every word on the card before animating** (the Ruth 2 example has "exsct" for "exact") — regenerate until spelling, reference and facts are right. Save as `images\<Book>_<Ch>_INTRO.png` (canvas → blob-link download → copy from Downloads).
- **Getting the card into Flow (works without the user):** Bible Studio Character Library → add a temporary stage "Temp Card <Book><Ch>" to any character of the book's workspace (`POST /workspace/entities/{id}/stages {label}` with X-XSRF-TOKEN; the stage id is in `history.state.page.props.entities[].stages` — that needs the book's workspace active, so switch to it and **switch back to the user's previous workspace afterwards**), upload the card with `uploadLink('stage_reference', stageId)` from a chatgpt.com tab, `BDS.mediaLink(image_url)`, drop it into Flow, then `DELETE /entity-stages/{id}`.
- Older fallback: the user drags `images\<Book>_<Ch>_INTRO.png` into the Flow window (ChatGPT blocks clipboard copy and Flow can't read the PC). Planned fix: an `asset` upload kind in Bible Studio's AutomationController so the card goes ChatGPT → Bible Studio → Flow by itself (needs a deploy — ask first).

**11c. Intro animation (Flow).** Frames, start frame = the card, Omni 1.1 Flash — chapter intro 4 s or 6 s; book intro **10 s** (the longest clip, looped), prompt = the intro animation prompt in `PROMPTS.md` (static camera, only leaves/dust/haze move, text untouched) + "No narration, no voiceover, no dialogue. Natural ambient sound only." Check the frames at full size: Flow can garble small text (Genesis 6: the footnote became "esact"). The camera is still, so `finish.py` pastes the card's own static strip back over the clip (`intro_restore` bands over plain background only — e.g. the footnote band `[[0.925, 1.0]]`). Book intro: the 10 s clip is looped under the 35–50 s narration as a ping-pong (forward then backward) so there is no jump.

**11d. Intro voice (Google Vids, Paz).**
- Chapter intro script: "The Book of <Book>… Chapter <Number in words>." (e.g. "The Book of Ruth… Chapter Two.")
- Book intro script: Claude writes it with the book intro prompt in `PROMPTS.md` (60–100 words, facts exactly as on the card), then adds "… Chapter One."
- Put it as **scene 1** of the chapter's Vids voiceover so there is one export and one voice; 9a's pause detection finds where the intro ends. (A separate Vids doc also works.)

**11e. Subtitles.** One block per verse, prefixed `[V<n>]`, exact KJV text. Timings = the verse windows measured in 9a (start of the verse's speech → end of its speech), so subtitles and pictures change together. Write `final\<Book>_<Ch>.srt` (also useful for YouTube). If a verse needs more than 3 lines on the bar, split it at a pause in the voice into two blocks: "[V2] First part…" then "[V2] …second part". Fallback: the user's Gemini SRT prompt in `PROMPTS.md`.

**11f. Look of the subtitles** (match `subtitle-layout-example-jonah-2.png`, 1920×1080):
- `lower-third.png` across the bottom (bar ≈ y 810–1060) at **80 % opacity**, so the picture shows through the bar while the verse is read (the verse text and reference stay fully solid; `overlay.base_overlay(..., bar_opacity=0.80)`);
- left block: "<BOOK> <CH>:<FIRST>-<LAST>" (e.g. "JONAH 2:1-10") in gold, uppercase, and "KING JAMES VERSION" in small white capitals under it, left of the gold divider;
- verse text: font **Cormorant Garamond**, white, left-aligned right of the divider, up to 3 lines;
- the reference block and bar stay up for the whole chapter film; the verse text changes per verse (not over the intro).

**11h. Render the finished film** with `C:\Users\USER\Bible Studio\_tools\finish.py` (repo: `automation/assemble/finish.py` + `overlay.py`; fonts in `_tools\fonts\`, images in `_tools\references\`). Plan `plans\finish.json` (Genesis 6):
```json
{"film": "../final/Genesis_6_clean.mp4", "edit_plan": "genesis6_full.json", "verses": "verses.json",
 "reference": "Genesis 6:1-22", "intro_video": "../video/Genesis_6_INTRO.mp4", "intro_voice": "../audio/Genesis_6_intro_voice.wav",
 "intro_card": "../images/Genesis_6_INTRO.png", "intro_restore": [[0.925, 1.0]],
 "intro_min": 5.0, "intro_max": 6.0, "intro_loop": false, "bar_opacity": 0.80,
 "references": "../../_tools/references", "fonts": "../../_tools/fonts", "output": "../final/Genesis_6_final.mp4"}
```
`verses.json` = `[[1, "And it came to pass…"], …]` from `BDS.verses(id)` with line breaks collapsed. Re-run `python3 finish.py finish.json` until it prints `wrote …` (Genesis 6: 3 runs). It also writes `<Book>_<Ch>_final.srt` (timed for the finished film) and `<Book>_<Ch>_clean.srt` (clean film) for YouTube captions. The intro voice is trimmed to the speech (`silencedetect`) and starts 0.5 s into the intro; the intro fades to black and the film fades in. The clean film is fit_edit's output, named `<Book>_<Ch>_clean.mp4`.

**11i. Calm ending (every film).** The film never stops on the last word. After the last verse the last scene keeps playing for about 3 s (`"outro": 3.0` in the fit_edit plan — the user wants 2–4 s): the end of the last clip is stretched if it is too short (slowed up to 1.4×, then its last frame held), the narration is over, the music fades out, and the picture fades to black over the last 1.5 s. In the finished film the lower third and verse fade away (0.6 s) as soon as the last verse ends, the **logo stays**, and picture + logo fade to black together. The clean film has the same 3 s ending (no logo).

**11g. Logo.** `logo-can-you-behold-him.png` top-right (≈ 270 px wide, ≈ 25 px from the top and right edges) at **40 % opacity**, over the whole chapter film.

## Exact timings — speech-to-text (user tip 2026-11-09)
Verse windows and the start/end of each quoted line come from a transcript **with word times**, aligned to the KJV text by `tools/stt_align.py` (`python3 stt_align.py stt.json verses.json narration.wav <dir>`; `from stt_align import find`).
- **First choice: Gemini** (gemini.google.com) in one of the user's signed-in Google accounts — free, no ElevenLabs credits. Upload the narration audio and ask: "Transcribe this audio word by word. Return only JSON: {\"segments\":[{\"words\":[{\"text\":\"...\",\"start_time\":seconds,\"end_time\":seconds}]}]}". Check a few word times against pauses (`silencedetect`) before trusting them.
- Gemini note (9 Nov): from the browser pane Gemini could not be given the file — its page blocks fetching r2 and it cannot read media links ("I encountered an error"). It works only if the user drags the audio into Gemini themselves.
- **Fallback: ElevenLabs Speech to Text** (very precise, costs plan credits): pass the narration by link — upload it as a black-picture mp4 into a shot's video slot (curl from the PC to `BDS.uploadLink('shot_video', shotId)`), read the r2 link from the project page, paste it under "URL", Transcribe, then Export → JSON (timestamps on) → Downloads.

## Fallback tools — Grok video and ElevenLabs voice (user rule, 2026-11-07)

Use these **only when the normal tool fails** and the user's subscription for them is signed in (check in the browser pane; if it isn't, tell the user — never type passwords).

**Video: Grok Imagine** (`https://grok.com/imagine`) — third choice after Vids and Flow, for a shot whose clip **Omni Flash rejects** (Vids or Flow refuses the prompt / start image, even after one softened retry). Don't use it for shots that work in Vids/Flow.
- Same inputs as 9V/9F: the shot picture as the start image + the motion prompt + the audio rule (no narration; character speech only as the exact quoted KJV words).
- Download the clip, name it `video\<Book>_<Ch>_S<scene>_SH<shot>.mp4` like the others, and note in the chapter log which shots came from Grok (they have their own look and possibly a watermark — check the corners and cover with the badge if needed).
- Flow default model is **Omni Flash 1.1** (cheaper) — user rule 2026-11-07.

**Voice: ElevenLabs** (subscription) — when Google Vids refuses narration text (e.g. Genesis 19 v4–5, v8) or cannot record a chapter, or when the user asks for it. Genesis 19 is being voiced with ElevenLabs (user decision 2026-11-07).
- Use one voice for the WHOLE chapter (don't mix Paz and ElevenLabs inside one chapter). Note the voice name + settings in the chapter log so later chapters can match.
- Exact KJV text, no verse numbers; record in parts of a few verses, download each as MP3/WAV into `audio\`, join into `audio\<Book>_<Ch>_voiceover.wav`, then measure verse windows (9a) as usual. God's and angels' lines still get `divine_voice.py` afterwards.
- Watch the subscription's character quota; tell the user before a chapter would run it out.

## Pipeline state at a glance
`await BDS.project(id)` → hasExegesis, entities (hasReference), scenes, shots, shotsWithImage, shotsWithVideo. Use it to resume a half-finished production: skip any stage already done.

## Maintaining this skill
The bridge source is `automation/bridge/bds-bridge.src.js` in the repo; `node automation/bridge/build.mjs` rebuilds `public/bds-bridge.js`; pushing to `main` deploys to the live site (ask the user before pushing). When a UI selector or step changes, update this skill and `automation/README.md`.

## Lip-sync and speaking clips (user rule + fix, 2026-10-28)

- **Speaking clips play at their full natural length.** Never trim a character's speech clip into its words, never slow it, never squeeze it into the original narration's timing. The narration waits for the character: after the plan is built, run `python3 ../../_tools/speech_fit.py <plan>.json` → it writes `<plan>.speechfit.json`, a narration `*_speechfit.wav` with extra silence in each speech window (later shots shift; the film gets longer — that is fine) and, if needed, a longer music bed. Point `finish.json` → `"edit_plan"` at the `.speechfit.json` plan and render that.
- **Frame-exact edit (bug fixed).** Before 2026-10-28 `fit_edit.py` rendered every 0.5 s dissolve as 13 frames instead of 12, so the picture drifted ~0.04 s behind the sound at every cut (≈1 s late by the speaking scenes at the end of Genesis 12–14 — the user saw it as bad lip-sync). It now cuts on whole frames. Check after every render: the clean film's video frame count / 24 must equal the planned length (last end − first start + outro), and a speech clip's frame at 3 s must match the film at window start + 3 s (offset 0.00 s).

**Characters are never cut off (user rule, 2026-11-03 — required).** The narrator must never start while a character is still speaking, and a character's line must never be clipped at a dissolve or at the end of the film. Two tools enforce it:
- `speech_fit.py` measures where each speaking clip's last word really ends (voice band, syllable-modulated, so a swell of crowd or music after the line does not count) and makes the window run past it (the narration waits). If the voice runs to the very end of the clip it prints a WARNING: Vids cut the line itself — listen, and regenerate the clip longer (e.g. 10 s) if a word is missing.
- `speech_check.py <plans/finish.json>` — **run it after every render and before delivering** (exit code 1 = do not deliver). Per speaking shot it reports voice start/end, window, level vs narrator, and FAILs on: last word after the hand-over (CUT), narrator audible between the character's first and last word, level more than 1.5 LU off the narrator. WARNs on a clip whose voice reaches its very end, or a pace faster than 0.26 s/word when the shot's "speech"/"note" holds the quoted words. Put the exact quoted words in each speech shot's `"speech"` field so the pace check runs. Paste its summary line into the production log.

**A speaking clip is never slowed (fix, 2026-11-04).** When speech_fit lengthens a speech window past the clip (to keep the last word), fit_edit must hold the clip's last frame, not stretch the clip — stretching drifted the lips 1–3 frames and slowed the voice (Genesis 12/13 first re-render). fit_edit.py now forces `trim` (play at 1×, hold last frame) for every shot with `clip_gain`. After every render also run `film_check.py plans/finish.json`: it compares each speech clip with the film early, middle and late in the shot and FAILs on any offset over 1 frame (the loudness column there is only a hint).

**Render on Windows, not in the Linux shell (2026-11-04).** The device shell is a small Linux VM (2 cores, 3.8 GB, 10 GB disk); the PC itself has an i7-11800H (16 threads), 16 GB and an NVIDIA GPU. `_tools\win\watcher.bat` runs on Windows (start it once by double-clicking it in File Explorer — Explorer is click-only for Claude; leave its window open). It starts one render per job file dropped into `_tools\win\queue\` (text `"<chapter> <plan base>"`, e.g. `12 genesis12_full`, CRLF), each running `run_chapter2.bat`: speech_fit → fit_edit (loop) → finish (loop) → speech_check → film_check, logging to `Genesis N\rerender_speechcheck.log`. `winrun.py` adapts the tools to CapCut's ffmpeg (no ffprobe, no libx264 → NVENC; finish.py's silence detection falls back to its own PCM scan because CapCut's silencedetect prints "invalid"). A whole chapter takes ~5–15 min; 3–4 at once is fine. Write the job file from the device shell; check the logs from there.

**Same volume for characters and narrator (user rule, 2026-11-02 — required).** A character's spoken words must be exactly as loud as the narrator. Vids speech clips come out about 5–7 dB quieter than the Vids narration (Esther 9: −24 to −26.5 LUFS vs −19.3 LUFS), so a fixed `clip_gain` (the old 1.3) leaves the characters ≈4 dB too quiet. `speech_fit.py` now measures each speaking clip's integrated loudness and the narration's, and sets that shot's `clip_gain` = 10^((narrator − clip)/20) in the `.speechfit.json` plan (printed per shot). Always render from the `.speechfit.json`. Check after rendering: the film's loudness over each speech window should be within ±1 LU of a nearby narrated stretch of the same length. Only `"speech_loudness_match": false` in the plan turns this off — never do that without the user asking.

## Lessons from Genesis 11 (2026-10-24)

- **Before generating clips, re-read section 9:** Vids is the default engine; Flow only when the user says so. (Genesis 11 was made in Flow by mistake — ~400 credits.)
- **Genealogy chapters (X lived N years and begat Y; X lived after … and begat sons and daughters):** give every patriarch his own look and keep it from chapter to chapter (Genesis 10/11: Arphaxad indigo robe + sheepskin + staff, Salah rust-red headcloth/robe, Eber long braid + saffron sash, Peleg curly hair + olive-green tunic, Joktan sky-blue; Reu hooded brown-cream mantle, Serug bare curly greying head + cream shawl, Nahor striped turban, Terah dark turban + white beard, Abram hooded sand mantle). Two pictures per generation: (1) "begat" = the father, at the age the text gives, holding his newborn son with his wife; (2) "lived after … sons and daughters" = the father older among his family with the grown son (in his own colours) beside him. Vary the setting per generation (valley with the ark far off, river reeds, barley field, sheepfold, canal, lamplit house, well, pergola, Ur rooftop with the ziggurat …). Review a contact sheet: the same face must not appear as two different men.
- **Portraits for men with no portrait:** attach the earlier chapter's picture of him and ask for "a character reference portrait of <NAME> as a younger man, about N years old … same face … same clothing". Upload them with `BDS.uploadCharacterReference(workspaceEntityId, blob)` from the Bible Studio tab — the signed `entity_reference` upload link answered "No image file … received" for these.
- **Child in a grief scene → ChatGPT refuses** ("guardrails around … teens and children"). Show the child as a young man/woman instead (Haran's son Lot at Haran's death).
- **A verse much longer than 10 s** (v31, 17.7 s): make a second picture for its second half (the arrival at Haran), split the window at a verse-internal pause, give both plan entries the same `"verse"` so they share one subtitle. Put `"verse": n` on every plan entry once any verse has two shots.
- **Getting a ChatGPT-only picture into Flow** (an extra shot or the intro card has no Bible Studio slot): upload it into a shot's slot temporarily (signed `shot_image` link), fetch it in the Flow tab with that shot's media link, drop it into Flow, then upload the real shot picture back and check its size.
- **Uploading from ChatGPT without leaving the chat:** open `https://chatgpt.com/robots.txt` in a spare tab (no CSP there), read the PNG from ChatGPT's IndexedDB, `fetch(signedUploadUrl, {method:'POST', body: formData, mode:'no-cors'})` — many files in one call (~15–20 s each); verify with `BDS.shots()` that each `imageUrl` changed.
- **Saving ChatGPT pictures to the PC:** blob link `download` from the robots.txt tab; files land in Downloads (sometimes as `.tmp`) — match them by exact byte size.
- **Flow queue:** keep the composer in Video mode before picking a Start frame (in Image mode there is no Start slot). A clip whose start picture was still uploading can be skipped ("notfound") — after a batch, count the video tiles and re-run any missing shot. "Generation timed out" tiles are refunded: press Retry.
- **Flow 1080p downloads in bulk:** in a second Flow tab open each clip with `history.pushState` + `popstate` to `/project/<id>/edit/<clipId>`, ⋮ → Download media → "1080p Upscaled" (match the menu text with `/1080p\s*Upscaled/` — it has a line break), wait while the "Upscaling your video" toast is up (~60–70 s), next. Identify the downloads by first-frame match against the 720p clips (`~/hd_match.py` pattern) — or skip 720p entirely and download 1080p first.
- **fit_edit slow-motion cache** is now keyed by the clip's mtime too, so replacing a clip (e.g. 720p → 1080p) re-renders its slow-motion.

## Lessons from Genesis 15 (2026-10-29)

- **Vids AI-video quota.** When the duration slider in the AI video settings is locked at 3 s (`input[type=range][aria-label="Video duration"]` is `disabled`), hover it: the tooltip "Exceeds your remaining quota" means the Vids allowance is used up (Genesis 14 used ~233 s the day before). Don't generate 3 s clips to "use it up": stop clip work, tell the user, and offer to wait for the reset or use Flow (only with their yes and a credit total).
- **ChatGPT composer changed:** the editor is a `[contenteditable="true"]` without the `#prompt-textarea` id (pick the visible one — a hidden copy also exists) and the send button is `button[aria-label="Send"]` (no `data-testid`). Take the file input from the visible editor's own `form`.
- **Short narrator lead-ins before a character speaks** ("And Abram said," ≈ 0.7 s): give them their own picture (a/b shots, e.g. v02a by the fire looking up → v02b the speaking close-up) and add a 0.9 s beat of silence after the lead-in in the dialogue narration, so the a-shot is on screen ~2 s instead of flashing past.
- **Verse timing without captions:** Vids sometimes embeds no captions for the last voiceover scene. A list verse (Kenites, Kenizzites …) can be split by counting the "s"-ending phrases in a high-frequency-energy scan (each name ends in s/z) plus the pauses (`-35 dB / 0.12 s`).
- **Flow Music wav links:** install a `window.fetch` wrapper in the Flow Music tab, click another session and back (SPA) — the `POST /__api/clips` response carries `https://storage.googleapis.com/producer-app-public/clips/<id>.wav` for each take; fetch it in that tab and save via a blob link.
- **Flow UI (2026-10-29).** The composer is a ProseMirror box ("What do you want to create?"); settings chip `Video · 720p · 10s … x1` (aria-label "Settings trigger") holds radio buttons Image/Video, Frames/Ingredients, 16:9, Omni 1.1 Flash, 360p/720p, 4s/6s/8s/10s, x1–x4 — plain JS `.click()` on them works. "Start" opens "Select a frame image" with a **Search assets** box: type the file name, click the `button.asset-item` whose `.asset-title` matches (that sets the frame; once filled the slot is `button[aria-label="Image ingredient"]`). Submit = `button[aria-label="Start generation"]`. Submitting one clip every ~35 s worked for 25 clips in a row.
- **Flow 1080p in bulk from a second tab:** clip id = the UUID in the grid thumbnail `…/image/<id>` (in a freshly loaded tab the thumbnails use `/asb/…` URLs instead, so collect ids in the tab where you generated). Edit view `/project/<pid>/edit/<id>` (pushState + popstate, going via the project page each time; wait until the `<video>` src contains the id — after many quick pushStates the view went black and needed a reload) → the `download` button → menu item `/1080p\s*Upscaled/` → wait while "Upscaling your video" is on screen (45–240 s). Share the id list between the two Flow tabs through `localStorage` (same origin).

## Lessons from Genesis 16 (2026-10-30)
- **Vids on Google account A**: 720p only (1080p greyed out), ~70 s of free clip quota, up to 3 clips queued. When the duration slider locks at 3 s with "Exceeds your remaining quota", switch the rest of the chapter to Flow on Google account B. Plan for a mixed film: 720p Vids clips are scaled up by fit_edit.
- **Badge only where the Vids watermark is**: put `"badge": false` on every Flow shot (in mkplan.py keep a `VIDS` set of the shots made in Vids).
- **Flow 1080p downloads**: do one clip at a time with a FULL page load of `/project/<pid>/edit/<id>` (not pushState, not the Previous/Next buttons), click `download` → menuitem "1080p Upscaled", wait until "Upscaling your video" disappears (~30–60 s). The grid thumbnails no longer carry the id in their src; click the tile and read `location.href`.
- **Intro card animation in Flow**: 6 s, 10 credits; prompt "keep the title card's composition and text exactly; camera still; only the background moves". intro_restore [[0.775,0.985]] still fits.
- **Two helper agents**: one did images + uploads (ChatGPT queue runner in its own tab), the other did music + intro card. Two ChatGPT runners in the same origin race on localStorage; treat the IndexedDB blobs as the truth.
- **Music**: let speech_fit run once on the untrimmed take to learn the film length, then trim to film + ~1 s with a ~9 s fade, and run speech_fit again.

## God's voice — divine treatment (user rule, 2026-10-30)
- Whenever God / the LORD / the angel of the LORD speaks, His words in the narration get the "divine voice"; the narrator's lead-ins ("And God said unto Abraham,") stay plain Paz.
- Tool: `python3 ../../_tools/divine_voice.py ../audio/<Book>_<Ch>_voiceover_full.wav god_spans_orig.json ../audio/<Book>_<Ch>_voiceover_divine.wav` — `god_spans_orig.json` = [[start,end],…] in the full export (start = end of the pause before God's words − 0.05 s, end = start of the pause after + 0.08 s; find them from the Vids captions + `silencedetect -35dB 0.12`). mkplan.py then cuts the dialogue narration from the *divine* wav (the intro voice from the plain one).
- Approved settings (defaults in the script): pitch 0.87 (−2.4 semitones, tempo kept), sub-octave layer 0.32, low shelf +5 dB, 4.5 s hall reverb at wet 1.0, God's words +2.5 dB over the narrator, soft limiter. The user asked twice for more echo and once for louder — don't go back to subtler settings. Send a short before/after preview only if the settings change.
- With much divine speech the film lands ≈ −16 LUFS (vs −18.6 before); that is fine.

## Angels' voices (user rule, 2026-11-04)
- When an angel speaks, his words in the narration get an **angel voice** (like God's divine voice, but its own sound); the narrator's lead-ins stay plain Paz.
- `divine_voice.py ... voice=<name>` picks the preset: **`angel`** for any angel who is not named (generic — Genesis 19's two angels), **`gabriel`** when Gabriel speaks, **`michael`** when Michael speaks, **`god`** (default) for God / the LORD / the angel of the LORD.
- Presets (in `VOICES` in the script): angel = pitch 0.95, light sub-octave, bright shelf +2.5 dB, airy chorus shimmer, 3 s hall, +1.5 dB; gabriel = clear herald, brightest (+3.5 dB), longer 3.6 s ring; michael = deeper (0.90) with strong low body, firmer and tighter 2.8 s hall, +2.5 dB.
- Keep the spans for each voice in separate files (e.g. `angel_spans_orig.json`, `god_spans_orig.json`) and run the script once per voice, the second run on the first run's output.
- The first time a new preset is used in a chapter, send the user a short before/after preview.

## Lessons from Genesis 17 (2026-10-30)
- **Accounts.** Clip engines in order: Vids on any account with quota (all free accounts so far are 720p only, ~70 s/day; Google account C added 2026-10-30), then Flow. User rule: animate every shot (no still-picture shortcuts to save credits); when Flow credits run out, stop and tell the user — they sign in to another Flow account (Google account D, 600 credits, added 2026-10-30). Never pick accounts on accounts.google.com yourself (blocked) — ask the user.
- **Tools now in `_tools/`:** `chatgpt_queue.js` (ChatGPT image queue: specs in localStorage, images to IndexedDB, one chat per scene), `flow_queue.js` (Flow: upload r2 images by drag-drop, settings, start frame via "Search assets" + item + **"Add to prompt"**, prompt via execCommand — never selectAll the page, it deletes the start-frame chip), `divine_voice.py`.
- **Flow out of credits** shows as the Generate button staying disabled (no message). Check the balance in the profile menu ("N Google Flow credits").
- **Flow downloads:** files now arrive with real names (`<Title>_<id>_1080p.mp4`). Get clip ids by clicking each tile under the sidebar **Videos** filter (viewport 1600×6000) with history.back between; in the edit view use the `Download media` button → "1080p Upscaled". A full navigate per id; after a navigate, `eval` of a stored function works only on a freshly loaded page.
- **Vids auto-saver:** give every download a unique file name — same-name downloads were silently dropped.
- **Hidden browser pane:** when the desktop app is minimised, screenshots freeze and timers slow to ~1/min. Read the page with JS and click at element positions; queues still run, just slower.
- **Music too short:** speech_fit's extension can stop short; extend by hand (e.g. 0–127 s + 80 s–end, 5 s crossfade, fade-out) to film length + 1 s.
- **PC disk:** `~/.fit_edit_work` grows by GBs per chapter — delete finished chapters' folders there when the session disk is full (scratch files, not the user's).
- Background jobs on the PC shell don't survive; run fit_edit/finish in the foreground repeatedly.

## Lessons from Genesis 18 (2026-10-31)
- **Engine order (user rule):** make clips in **Google Vids first**; switch to Flow only when Vids says the limit is reached. glorifymichaels Vids gives **1080p** (settings button "Generation settings: Omni, 720p…" → `720p` button → menuitemradio `1080p`) and made 46 clips in one day without hitting a limit.
- **Vids AI clip runner (JS, Vids tab, viewport 1600×950):** open "Generate an AI video clip" → `Animate` tab. Per clip: press `[aria-label="Expand"]` if shown, press `Clear` if shown (an attached image hides the file input), put the picture into `input[type=file][accept*=png]` via DataTransfer (fetch the r2 URL), wait 6 s, set `input[type=range][aria-label="Video duration"]` with the native value setter + input/change events, select the contenteditable prompt box's own contents and `execCommand('insertText')`, then click `Generate` with pointerdown/mousedown/pointerup/mouseup/click. Result = the **last** `<video>` in the panel; save with fetch → blob → `<a download="g18_vids_<key>_<time>.mp4">` (unique names). Keep the runner in the tab only — it is lost when the pane reloads; rebuild it from these notes.
- Vids clips have a faint ✦ sparkle watermark bottom-right → list every Vids shot in `plans/vids_shots.json` (mkplan reads it) so the badge covers it.
- `take_clips.py` looks at Downloads **newest first** (a remade clip wins), keys are `picture|seconds`, so two clips from the same picture must have different lengths.
- Intro card via Vids: footnote text gets garbled and the sparkle lands in the footer — intro_restore [[0.775,0.985]] pastes the real card strip back; always check one full-size frame.
- Slot trick still works from chatgpt.com: IndexedDB `__bds`/`kv` keeps `g18_card`, `g18_v01` etc. across pane restarts → form POST to the shot's signed upload link, then upload the main picture back and compare sizes.
- PC can drop offline mid-run: everything is resumable — re-run take_clips, then fit_edit/finish until they print "wrote".

- **ChatGPT in two tabs at once (2026-11-04, Genesis 19):** a fresh composer can restore the other tab's unsent draft, so a second tab's message got another picture's prompt glued in front. `chatgpt_queue.js` v5 clears the composer before pasting; still prefer one generating tab at a time.
- **Flow upload into a new, empty project (2026-11-04):** drag-drop does nothing there. `flow_queue.js` `upload()` now opens the asset picker's **Upload media** button, catches the file input it creates (its `click` is suppressed so no OS dialog opens) and sets the files on it.
- **Blob downloads from the browser pane** arrive as `<uuid>.tmp` in Downloads first and are renamed a little later; Downloads also holds hundreds of old `.tmp` files, so wait for the named file (or match the exact byte size) rather than waiting for "no .tmp left".
