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
