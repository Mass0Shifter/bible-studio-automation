# Environment — PC, folders, accounts, tools

## PCs used
| Device | Windows user | Media folder | App repo clone | Notes |
|---|---|---|---|---|
| `revivalist-hp` (Windows, x64) — current (Nov 2026) | `ebubz` | `C:\Users\ebubz\Desktop\Bible Studio` | `C:\Users\ebubz\Desktop\Dev Projects\Bible Illustration\bible-director-studio` | Claude desktop app links it to cloud sessions. Goes to sleep / offline often. |
| earlier PC (Oct 2026) | `USER` | `C:\Users\USER\Desktop\Bible Studio` | `C:\Users\USER\Dev Projects\Kingdom Tools\bible-director-studio` | from older notes |

Connected-folder rules (Claude desktop): deleting files is off by default (move scrap to `_to_delete\`); `git commit` in a connected folder leaves lock files unless delete permission is granted — commit from a cloud clone instead.
Downloads land in `C:\Users\ebubz\Downloads` (often as `<uuid>.tmp`), then get copied into the chapter folder. Originals stay in Downloads.

## Chapter folder layout
`Desktop\Bible Studio\<Book> <Ch>\` → `audio\` `images\` `video\` `music\` `plans\` `final\`
Shared tools (copies in this repo's `tools/`): `Desktop\Bible Studio\_tools\` (finish.py, fit_edit.py, overlay.py, fonts\, references\ incl. logo, lower-third, badge, intro template, PROMPTS.md).

## Web tools (all in the Claude desktop **built-in browser pane**; user signs in himself)
| Tool | URL | Used for | Limits / cost |
|---|---|---|---|
| Bible Director Studio | https://biblestudio.nachamtns.com | projects, exegesis, storyboard, uploads (bridge `/bds-bridge.js`) | never press paid AI buttons |
| ChatGPT (Plus) | project **"Ai Bible Imagery"** https://chatgpt.com/g/g-p-6a7336d84f948191ba98f1852cc326d1/project | portraits + shot images | image cap per ~5–7 h; never use project "Can You Behold Him" (thumbnails) |
| Google Vids | https://docs.google.com/videos | voiceover (voice **Paz**), AI video clips (default, free) | AI-video quota per account; TTS fails on scripts > ~900 chars |
| Google Flow | https://flow.google.com | video clips only when user says "using Flow" | Omni 1.2 Flash: 3 credits/s @720p, 1/s @360p |
| Google Flow Music | https://www.flowmusic.app | instrumental score | download via clip `wav_url` |

Browser-pane sites approved for the pane: biblestudio.nachamtns.com, chatgpt.com, labs.google, flow.google.com, docs.google.com, accounts.google.com, flowmusic.app.

## GitHub
- App repo: `Mass0Shifter/bible-director-studio` (private). Push to `main` deploys the live site — ask the user first.
- This repo: `Mass0Shifter/bible-studio-automation` — **public** on GitHub, so never put e-mail addresses, passwords, signed upload links or API keys here. Google accounts are written as "Google account A/B/C/D" (the user knows which is which).

## Running agents
- User rule: at most **3** background agents at once.
- Agents sharing the one browser pane collide: each must open its own fresh tabs and only use its own tabIds; pane has a tab limit — close tabs when done.
- Claude plan has a 5-hour usage limit; agents stop with a 429 and must be resumed after the reset.

## Rendering on Windows (Oct–Nov PC)
The PC (i7-11800H, 16 threads, 16 GB, NVIDIA GPU) renders natively: `_tools\win\watcher.bat` watches `_tools\win\queue\*.job` and runs the whole render + checks; `winrun.py` wraps CapCut's ffmpeg (`AppData\Local\CapCut\Apps\<ver>\ffmpeg.exe`, no ffprobe/libx264 → emulated / h264_nvenc). The Linux VM shell (2 cores) is only for small jobs.
