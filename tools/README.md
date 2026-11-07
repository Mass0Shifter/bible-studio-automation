# tools — assembly scripts and assets (copy of PC `Desktop\Bible Studio\_tools\`)

| File | What it does |
|---|---|
| `fit_edit.py` | Builds the clean chapter film from a plan: fits each clip to its verse window (trim / slow / lead), dissolves, voiceover, music, calm 3 s ending. Re-run until it prints `wrote …`. |
| `finish.py` | Adds intro, verse subtitles (lower third), logo and badge → final film + .srt files. |
| `overlay.py` | Drawing helpers for the lower third / subtitles used by finish.py. |
| `grab.sh` | Helper to copy downloads into the chapter folder. |
| `fonts/` | Cormorant Garamond (subtitles). |
| `references/` | Logo, lower third, badge, intro-card template, layout examples, PROMPTS.md. **(pending upload — PC connection dropped)** |
| `git-bundles/` | Backup of the app repo's unmerged branch `feature/verse-timed-edit` (has these scripts' history). **(pending upload)** |

On the PC these files must also exist in `Desktop\Bible Studio\_tools\` (scripts use relative paths like `../../_tools/references`). This repo is the source of truth: when a script changes, update both.
