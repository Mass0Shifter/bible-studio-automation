---
name: bible-director-production
description: Produce a Bible chapter end-to-end in Bible Director Studio (biblestudio.nachamtns.com) when the user says things like "Create Genesis Chapter 6" — workspace, project, exegesis, characters, storyboard, ChatGPT images, Google Vids voiceover, video clips from Google Vids AI video (default, free) or Google Flow when the user says "using Flow", and Flow music.
---

# Bible Director Studio — chapter production

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

## 8. Export the voiceover to the PC

File → Download → MP4. Downloading needs the user's OK (state the file name first). Production folder on the PC: `Desktop\Bible Studio\<Book> <Chapter>\` with subfolders `audio\`, `images\`, `video\`, `music\`, `plans\`, `final\`. If that folder isn't connected to the session, ask for access to `Desktop\Bible Studio` once. Move the export to `audio\<Book>_<Chapter>_voiceover.mp4`.

## 9. Video clips — which engine (user rule, 2026-10-22)

- **Default = Google Vids AI video** (free, Omni, 1080p). "Generate Genesis 11" / "make the videos for chapter 11" → Vids (9V below).
- **Google Flow only when the user says so** ("… using Flow", "with Flow") → 9a–9c below (costs Flow credits; get the yes on the total first).
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
    5. In the fit_edit plan split the verse into two shots with the SAME `verse` number: the original clip up to just after the narrator's framing, then the speech clip with `"clip_gain": 1.3` (its own audio at full level instead of the 0.22 ambience); add plan-level `"vo_mute": [[start, end]]` (voiceover seconds) covering the narrator's reading of the quote, starting just after "And he said,". finish.py merges consecutive shots of the same verse into one subtitle span. Send the user a ~12 s preview of the moment.
- A "harmful content related to minors" refusal (refunded) can hit family scenes with youthful-looking sons: describe them as "grown, bearded men" and retry.
- If an image upload to Bible Studio returns 503, send it as JPEG (canvas → `image/jpeg` 0.93) — large PNGs get refused; always check the `{"success":true}` page.
- If Flow refuses a shot ("might violate our policies" — refunded), it is usually the start image itself (distress, crowds in chaos). Soften the prompt once; if it still fails, use a still-image push-in or make a calmer image.
- To change who is in a picture (e.g. only Noah's family at the ark), edit the start image in Flow's **Image** mode first (Nano Banana, 0 credits): add the shot image as ingredient, instruct what to keep and remove, then generate the clip from the edited image. In Image mode the Start-generation button needs a real click.
- **Start generation**. Two generations can run side by side; a 10s clip takes about 1–2 minutes.
- Download — **always 1080p (user rule, 2026-10-22).** Open the clip (click its tile → edit view) → ⋮ → **Download media → "1080p Upscaled"**. Flow first upscales the clip (toast "Upscaling your video… may take several minutes"), then the download starts by itself — this looks like a stall but is normal: **wait for it** (Genesis 10: ~45 s per clip, 1920×1080, ~11 Mb/s vs ~5 Mb/s at 720p; no extra credits). Run **one upscale at a time** (Flow asks not to start several): wait until the toast is gone and the file has landed before starting the next clip. Never fall back to "720p Original size" (the tile's right-click → Download is 720p — don't use it for the film). In the browser pane downloads land in Downloads as `<uuid>.tmp` files and may arrive out of order, so identify each clip by its **first frame**: compare it with the shot images (64×36 grayscale correlation; a match scores >0.95) — `automation/assemble/match_clips.py` does this — then copy to `video\<Book>_<Ch>_S<scene>_SH<shot>.mp4`. Always click Flow menu items by name, never by coordinates (one coordinate click once hit "Move to trash").
- A generation stuck at 99 % for more than ~10 minutes has failed silently: reload the project page and generate that shot again.
- Getting images into an existing Flow project: open the Start picker, `dragenter`+`dragover` on the element at the dialog's centre, wait ~0.7 s, then `dragenter`/`dragover`/`drop` again on the element now at that point (a drop overlay appears). Dropping on the tile grid does nothing.
- Optional hand-off back to Bible Studio: `uploadLink('shot_video', row.shotId)` + `senderScript(url, PICK_FLOW_VIDEO, row.fileStem)` in the Flow tab.

**9d. Fit the clips to the verses (free).** `python3 automation/assemble/fit_edit.py plan.json` (in the repo; on the user's PC the repo is `Dev Projects\bible-director-studio`, the media is `Desktop\Bible Studio`) renders an edit from a plan: voiceover, music, music gain, and per shot the clip + its verse window. For each shot it needs window + 0.5 s (the dissolve) and:
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

References (images + exact prompts): `automation/references/` in the repo, copies on the PC in `Desktop\Bible Studio\_tools\references\` — see `PROMPTS.md` there.

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

**11h. Render the finished film** with `Desktop\Bible Studio\_tools\finish.py` (repo: `automation/assemble/finish.py` + `overlay.py`; fonts in `_tools\fonts\`, images in `_tools\references\`). Plan `plans\finish.json` (Genesis 6):
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

## Pipeline state at a glance
`await BDS.project(id)` → hasExegesis, entities (hasReference), scenes, shots, shotsWithImage, shotsWithVideo. Use it to resume a half-finished production: skip any stage already done.

## Maintaining this skill
The bridge source is `automation/bridge/bds-bridge.src.js` in the repo; `node automation/bridge/build.mjs` rebuilds `public/bds-bridge.js`; pushing to `main` deploys to the live site (ask the user before pushing). When a UI selector or step changes, update this skill and `automation/README.md`.
