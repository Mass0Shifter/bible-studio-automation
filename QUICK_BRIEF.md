# QUICK BRIEF — read this first, then only the files it points to

_Last updated: 2026-11-07 23:10 (Africa/Lagos) — reviewed Genesis 19–28 against the files on PC `C:\Users\USER\Bible Studio`._
Keep this file under ~150 lines. Update it at the end of every work session (and after each finished stage).

## What this repo is
Progress tracker + automation notes for **Bible Director Studio** chapter films (KJV). The app itself lives in a different repo (`Mass0Shifter/bible-director-studio`, live at https://biblestudio.nachamtns.com). This repo holds: what is done / not done, where every file and link is, and the production skill.

## Where to look
| Need | File |
|---|---|
| Machine-readable status of every chapter | `status.json` |
| Full detail on one chapter (links, ids, decisions, problems) | `productions/<book>/<NN>.md` |
| How to produce a chapter (the skill) | `skill/SKILL.md` (+ `skill/PROMPTS.md`) |
| Whole-book "Prophetic Implication" film | `skill/prophetic-implication/SKILL.md` |
| Lessons learned that are NOT yet in the skill | `docs/LESSONS.md` |
| Helper + assembly scripts, fonts (references images still to upload) | `tools/` (see `tools/README.md`) |
| Genesis 6 full production log (reference example) | `productions/genesis/06.md` |
| PC, folders, accounts, browser tabs, limits | `docs/ENVIRONMENT.md` |

## Pipeline stages (per chapter)
1 project → 2 exegesis → 3 portraits → 4 storyboard → 5 shot images (ChatGPT) → 6 voiceover (Vids, Paz) → 7 music (Flow Music) → 8 video clips (Vids AI video; Flow only if user says) → 9 fit edit → 10 intro/subtitles/logo → 11 final + clean films.

## Status at a glance
Legend: ✅ done · 🟡 partial · ⬜ not started · ❔ made before this repo, not audited

### Genesis (workspace "The Book Genesis")
| Ch | Story | Images | Voice | Music | Clips | Final | Note |
|---|---|---|---|---|---|---|---|
| 1–3 | ❔ | ❔ | ❔ | ❔ | ❔ | ❔ | not on the Oct–Nov PC — audit with `BDS.project(id)` |
| 4–18 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | final + clean films on the Oct–Nov PC (`C:\Users\USER\Bible Studio`); 7–18 passed the speech check 3–4 Nov |
| 19 | ✅ 38 shots | ✅ 38/38 | ✅ 5:48 ElevenLabs (Ralph) | ✅ 2 takes | ⬜ (prompts ready) | ⬜ | re-voiced with ElevenLabs; music to extend; clips next |
| 20 | ✅ 18 shots | ✅ 18/18 | ✅ 2:44 | ✅ 2 takes | ⬜ | ⬜ | pictures done |
| 21 | ✅ 21 shots | ✅ 21/21 | ✅ 4:07 | ✅ 2 takes | ⬜ | ⬜ | pictures done; Ishmael has no portrait (stored as "symbol") |
| 22 | ✅ 22 shots | ✅ 22/22 | ✅ 3:30 | ✅ 2 takes | ⬜ | ⬜ | pictures done |
| 23 | ✅ 20 shots | ✅ 20/20 | ✅ 2:44 | ✅ 1 take | ⬜ | ⬜ | Ephron portrait done |
| 24 | ✅ 40 shots | ⬜ 0/40 | ✅ 9:14 | ✅ 2 takes | ⬜ | ⬜ | portraits: Servant, Rebekah, Laban, Bethuel, Isaac(Adult); set Abraham stage=Elder |
| 25 | ✅ 24 shots | ⬜ 0/24 | ✅ 4:07 | ✅ 2 takes | ⬜ | ⬜ | portraits: Keturah, Rebekah(Adult), Esau, Jacob; set Abraham stage=Elder |
| 26 | ✅ 22 shots | ⬜ 0/22 | ✅ 4:37 | ⬜ | ⬜ | ⬜ | portraits: Isaac(Adult), Rebekah(Adult) |
| 27 | ✅ 26 shots | ⬜ 0/26 | 🟡 v21–46 inserted, v1–20 + export to do | ⬜ | ⬜ | ⬜ | remove wrong "Haran" (person) entity; Vids scene 5 may be doubled |
| 28 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | next |
| 29–50 | ⬜ | | | | | | |

### Other books
| Book | Chapters in app | Status |
|---|---|---|
| Ruth | 1–4 (+ whole-book project) | ❔ produced earlier — audit |
| Jonah | 1–4 (+ whole-book project) | ❔ produced earlier — audit |
| Esther | 1–10 projects exist | ch 9 ✅ final + clean (5:41); others ❔ audit |
| Everything else | — | ⬜ |

## Review 2026-11-07 night (files on PC `C:\Users\USER\Bible Studio`)
- Chapter folders on this PC are `C:\Users\USER\Bible Studio\Genesis NN` (not Desktop). Genesis 28 has no folder yet.
- Genesis 20–27 was made on the other PC (revivalist-hp) and transferred here by the user on 2026-11-07. Pictures for 20–23 are now complete in the app AND saved on this PC (2026-11-08).
- Genesis 25 + 26 .wav rebuilt from the mp4 (full length now). Genesis 28 folder created.
- Genesis 27 folder is empty (voiceover not exported, no music).

## Current decisions / blockers (2026-11-07)
- **User: no video generation for now.** Focus = storyboard, images, voiceover, music up to Genesis 28.
- **Google Vids AI-video quota used up** (durations locked at 3 s). Wait for reset; don't use Flow unless user says.
- **Flow price changed:** Omni 1.2 Flash = 3 credits/s at 720p (1/s at 360p). Old skill figure (~1.5/s) is wrong. Genesis 20+21 clips ≈ 750 credits at 720p — user has NOT approved.
- **ChatGPT image limit** resets ~5–7 h after it hits; it hit at ~04:00 and ~? on 2026-11-07. Images resume after reset.
- **Working rules:** max 3 chapters at once (lead + 2 agents); cycle the user's 5–7 Google accounts for Vids/Flow (see `docs/ENVIRONMENT.md`).
- **Claude 5-hour usage limit** stops background agents; max 3 agents at once (user rule).
- PC (`revivalist-hp`) keeps going offline — ask user to keep it plugged in and awake.

## Next actions (in order)
1. Genesis 27: finish voiceover v1–20, export; music.
2. Genesis 26: music; redo voiceover .wav.
3. Genesis 28: full storyboard + voiceover + music.
4. All missing portraits + shot images (Genesis 20–28) in ChatGPT project "Ai Bible Imagery".
5. Audit Genesis 1–3, Ruth, Jonah, Esther (except 9) and fill this table. Genesis 19: finish (see `productions/genesis/19.md`).
7. Prophetic Implication: test the new skill (`skill/prophetic-implication/SKILL.md`) on a book the user picks.
6. Video clips only when user says (Vids default).
