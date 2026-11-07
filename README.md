# Bible Studio Automation

Progress tracker and production playbook for Nâcham Media's KJV Bible chapter films made in **Bible Director Studio**.

**AI agents: open `QUICK_BRIEF.md` first.** It tells you, at a glance, which books and chapters are done, what is blocked, and which single file to read next. Don't read the whole repo.

## Layout
- `QUICK_BRIEF.md` — one-page status + next actions (keep it short and current)
- `status.json` — every book/chapter: project ids, stage status, file lengths, todos
- `productions/<book>/<NN>.md` — detail per chapter (links, decisions, problems)
- `skill/SKILL.md` — the production skill ("Create Genesis Chapter 6"), `skill/PROMPTS.md`
- `skill/prophetic-implication/SKILL.md` — the whole-book "Prophetic Implication" film (script → storyboard → titles, thumbnails, tags, description)
- `references/` — logo, badge, intro template, subtitle bar, channel outro video (copies of the PC's `_tools\references\`)
- `tools/` — copies of the PC's helper scripts (fit_edit, finish, speech checks, ChatGPT/Flow queues, Windows render watcher)
- `docs/ENVIRONMENT.md` — PCs, folders, accounts, browser tools, limits
- `docs/LESSONS.md` — new lessons not yet merged into the skill

## Rules for updating
1. After each finished stage: update the chapter file and `status.json`.
2. At the end of a session: update `QUICK_BRIEF.md` (date, table, blockers, next actions).
3. Chapter media (audio, images, video) never go in this repo — they stay on the PC in the Bible Studio folder. Exception: the shared finishing files in `references/` (logo, badge, intro template, lower third, channel outro).
