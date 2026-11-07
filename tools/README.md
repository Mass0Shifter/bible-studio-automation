# Production helper scripts (copies from the PC)

Synced 2026-11-07 from `C:\Users\USER\Bible Studio\_tools\` (Oct–Nov PC). The working copies live on the PC; this folder is the backup and reference. How each one is used is in `skill/SKILL.md`.

| File | What it does |
|---|---|
| `fit_edit.py` | Builds the chapter film from a plan: clips fitted to verse windows, dissolves, narration, music, badge over the Vids watermark. Speaking clips are never slowed (trimmed / last frame held). |
| `speech_fit.py` | Before fit_edit: extends a speaking shot's window past the character's last word and sets `clip_gain` so the character is as loud as the narrator. |
| `speech_check.py` | After rendering: fails if a character is cut off, the narrator talks over a character, or the levels differ by more than 1.5 LU. Required before delivery. |
| `film_check.py` | After rendering: checks lip-sync of every speaking shot in the finished film (fails above 0.05 s). |
| `finish.py` + `overlay.py` | Intro, subtitles (lower third), logo, calm ending → `_final.mp4`; also the `_clean.mp4`. |
| `divine_voice.py` | Voice treatment for God (`voice=god`, default) and angels (`voice=angel`, `gabriel`, `michael`) over given time spans of the narration. |
| `chatgpt_queue.js` | Paste into a ChatGPT tab in project "Ai Bible Imagery": generates a list of shot pictures one chat per scene, saves them in the browser (IndexedDB). v5 clears the composer first. |
| `flow_queue.js` | Paste into a Google Flow project tab: uploads start frames and queues clips (only when the user approves Flow credits). |
| `win/winrun.py`, `win/watcher.bat`, `win/run_chapter2.bat` | Render natively on Windows with CapCut's ffmpeg + the NVIDIA encoder: drop a job file `"<n> <plan base>"` into `win\queue\`; the watcher runs speech_fit → fit_edit → finish → speech_check → film_check. |
