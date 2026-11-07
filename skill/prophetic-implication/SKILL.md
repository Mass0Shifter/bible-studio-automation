---
name: prophetic-implication
description: Write and storyboard a book's "Prophetic Implication" film for Can You Behold Him, a whole-book look at how a Bible book points to Christ and salvation. Use for "do the Prophetic Implication of Jonah", "PI for Ruth" or "how does Esther point to Christ".
---

# Prophetic Implication — whole-book Christ & salvation film

Every book in the channel (Nâcham Media / **Can You Behold Him**) gets one **Prophetic Implication** (PI) video, alongside its verse-by-verse chapter films. It is a short, cinematic **teaching narration** that looks at the *whole book* and shows how it relates to **Christ and the salvation story**, point by point. Model: the user's Jonah PI and the Gemini workflow made from it (2026-08-24) — summarised in "Reference: Jonah" at the end.

A request like **"Prophetic Implication of Ruth"** means: run steps 1–6 below for that book, then stop for the user's review. Producing the film (pictures, voice, clips) only starts when the user says so, and it uses the chapter pipeline in `../SKILL.md`.

The user is not a developer: report in plain words. Never use Bible Director Studio's paid AI buttons. Never spend Flow credits without a yes.

## House rules (apply to every part)
- **Scripture quotes are KJV, word for word**, with the reference ("Matthew 12:40"). Check every quote against a KJV source (Bible Studio `BDS.verses(...)` for books in the app, or a KJV web text) — never quote from memory. (The Jonah sample used a modern translation; the channel standard is KJV — ask once if the user wants otherwise.)
- **Stay grounded.** Every claim that the book points to Christ must rest on one of:
  1. the **New Testament's own use** of the book (Jesus or an apostle citing it — strongest, say so: "Jesus Himself…");
  2. a **clear type/shadow** the church has long recognised (say "a picture of", "a shadow of");
  3. the book's **place in the salvation storyline** (covenant, promise, the line of the Messiah, God's grace to the nations).
  Don't invent hidden codes, numerology, dates or new doctrine. Where Christians read a passage differently, keep to what is widely held and word it modestly.
- **Depiction:** God the Father is never shown (light, glory or the effect of His presence instead). Jesus *may* be shown as the incarnate Son (the Jonah PI does), reverently, never mocked, and never with a stylised "face of God". Angels' faces stay hidden. No gore, no nudity. Violent or sexual themes are told in restrained images (silhouettes, aftermath, symbols).
- **Characters:** a named biblical character in a shot uses the existing **Character Library portrait** (Bible Studio) as a reference, the same way the chapter films do. Characters with no portrait yet are listed for the user in step 6.

## 1. Gather the book (no writing yet)
- The book's chapter summaries (from the chapter projects' exegesis in Bible Studio if they exist, otherwise read the KJV text), its main characters, setting and period, and the 3–8 key moments.
- The **New Testament references** to the book: direct quotes, allusions, and the people or events from it that the NT names (e.g. Jonah → Matthew 12:39–41, Luke 11:29–32; Ruth → Matthew 1:5; Esther has no direct quote, so say so honestly and use type/storyline instead).
- 3–5 **Christ connections**, each with its scripture support (from the list above). Note which kind of support each one has.

## 2. Write the PI narration (the script)
Length: **450–700 words ≈ 3–5 minutes** (Paz reads ~17 characters per second). Plain, warm, confident English, written to be heard. Shape (the Jonah PI):

1. **Hook (2–3 sentences).** Name the common, shallow view of the book and overturn it: *"While the Book of Jonah is often treated as a children's story about a giant fish, it is actually one of the most radical, profound books in the Old Testament."* Then one line of what it really is.
2. **Thesis line.** *"When it comes to the grand story of salvation, <Book> operates as …"* (three short nouns: e.g. "a mirror, a prophecy, and a divine shock to the system").
3. **Transition.** *"Here is the breakdown of <Book>'s significance to redemptive history."*
4. **3–5 numbered points.** Each has:
   - a title with a subtitle in brackets: *"1. The 'Sign of Jonah' (The Resurrection Connection)"*;
   - 2–4 short labelled sub-points (*"The Descent and Ascent: …"*, *"The Prophet's Prejudice: …"*, *"The Salvation Link: …"*);
   - at least one KJV quote with its reference;
   - an explicit line tying it to Christ or the gospel. Where it fits, use the **"true and better"** contrast (*"Jesus was the true and better Jonah who…"*) or a **side-by-side contrast** (*"In the Storm: … The Sacrifice: … The Heart: …"*).
5. **Summary.** One paragraph headed "Summary": the book's message in the salvation story, ending on one memorable line (*"…salvation belongs to the Lord, and His grace is shockingly wider than our human borders."*).

Save it as `Prophetic Implications\<Book>\<Book>_PI_script.md` in the Bible Studio media folder on the PC, and send the user the script to read **before** storyboarding. A wrong claim is cheap to fix here and expensive later.

## 3. Shot-by-shot storyboard
Split the approved script into **Scenes** (hook = Scene 1, one scene per numbered point, Summary = last scene) and then **Shots**.
- **No shot over 10–12 s of narration (≈ 20–25 words)** — the video generators' limit. Split long sentences at a comma or clause; keep scripture quotes word for word (a long quote may span two shots).
- Every word of the script appears in exactly one shot, in order.
- Estimated duration = words ÷ 2.3 (≈ Paz's pace), rounded, written "~Ns".

For every shot:
```
Scene <n>: <Scene name>

Shot <n.m> (~<s>s)
Narration: "<exact words>"
Image Prompt: "<prompt>"
Animation Prompt: "<prompt>"
```
- **Image Prompt:** when a named character is in the shot, start with `[Use existing character model for <Name>]`, then environment, action, lighting (golden hour, Rembrandt, chiaroscuro, moonlight, volumetric), camera (wide, medium, close-up, macro, low angle, over-the-shoulder), atmosphere. End with the channel's look: *"High-budget 35mm film photograph, photorealistic biblical historical drama, natural atmospheric light, authentic period textiles, 16:9, no text."* Teaching lines without a story moment get symbolic images (a scroll in a light beam, a map with a glowing route, a tomb with a sliver of light, a crowd from many nations under the stars).
- **Animation Prompt:** one camera move (slow push-in, drone fly-over, slow pan, tilt, tracking, static) + one or two natural movements (fabric in wind, dust motes, waves, smoke, light rays). Add: *"Keep every face and garment exactly as in the start image. No narration, no voiceover, no dialogue, no music, no text on screen. Natural ambient sound only."*

Save as `<Book>_PI_storyboard.md` next to the script, and also as `<Book>_PI_storyboard.json` (`[{scene, shot, est_s, narration, image_prompt, animation_prompt, characters:[...]}]`) so the chapter tools can use it.

## 4. Titles and thumbnails
**5 YouTube titles**: curiosity-driven, honest (no clickbait that the video doesn't deliver), under ~60 characters, e.g. *"The Hidden Secret of Jonah (It's Not About the Fish)"*, *"Why Jesus Called Himself 'Jonah'"*, *"Jonah vs. Jesus: The Shocking Comparison"*. For each, one **thumbnail image prompt**: high contrast (dark blue vs blinding gold, fire vs night), one clear focal point, dramatic light, split-screen or symmetrical comparisons work well. Same depiction rules. Thumbnails are made in the ChatGPT project **"Can You Behold Him"** (reserved for thumbnails), never in "Ai Bible Imagery".

## 5. YouTube tags
Three groups: **Broad Biblical** (Bible animation, Old Testament stories, AI Bible animation, Gospel explained, Redemptive history …), **Specific/Theological** for this book (Book of <Book> explained, <key type> , <NT reference>, <Book> and Jesus …), then one comma-separated **"Copy & Paste" block** with all of them (keep it under YouTube's 500-character limit).

## 6. YouTube description
- The chosen title on top.
- Hook paragraph (2–3 sentences, the myth-vs-reality turn).
- One paragraph on what the viewer will discover (name the points).
- Call to action: like, subscribe for more verse-by-verse cinematic animations.
- **🎬 Video Chapters** with timestamps from the storyboard: 0:00 at Scene 1, each scene starts at the sum of the estimated shot durations before it (replace them with the real ones once the voiceover exists).
- **📱 Connect & Support** and **⚠️ About This Channel** blocks, with the channel name *Can You Behold Him* filled in; leave `[Insert Link]` placeholders unless the user has given the links.
- 5–8 hashtags (#BookOf<Book> #BibleAnimation #Gospel …).

Put steps 4–6 in `<Book>_PI_youtube.md`. Then report: where the files are, the 5 titles, the characters that need portraits, and ask whether to start production.

## 7. Production (only when the user says so)
Same pipeline as the chapter films (`../SKILL.md`), with these differences:
- **Bible Studio:** project in the book's workspace titled `<Book> — Prophetic Implication`; storyboard rows from the JSON (one row per shot; the narration is the shot text, not a verse).
- **Pictures:** ChatGPT project "Ai Bible Imagery", the Image Prompt + the named characters' portraits attached (the `[Use existing character model for X]` tag means: attach X's Character Library portrait).
- **Voice:** Google Vids, voice **Paz**, one scene of the script per Vids scene, each part ≤ ~620 characters (a Vids scene export stops at the scene length). Quoted words of Jesus or God are read by the narrator (this is teaching, not drama), with no divine-voice treatment unless the user asks.
- **Clips:** Google Vids AI video (default) from the Animation Prompts; Flow only if the user says so.
- **Music:** Flow Music, a reflective, building score; same −9.8 dB mix.
- **Finishing:** intro card (as in the chapter films, with the title "THE BOOK OF <BOOK>" and "PROPHETIC IMPLICATION" in place of the chapter line), logo, calm 3 s ending. Subtitles: show the narration sentence by sentence (there are no verse numbers); when a KJV quote is on screen, add its reference.
- Deliver `<Book>_PI_final.mp4` and `<Book>_PI_clean.mp4`.

## Reference: Jonah (the model)
- **Hook:** children's story about a fish → radical book, a critique of religious exclusivity and a preview of the Gospel.
- **Thesis:** "a mirror, a prophecy, and a divine shock to the system."
- **1. The "Sign of Jonah" (The Resurrection Connection):** Matthew 12:40; Jonah 2's descent to "the belly of hell" and being brought up → Christ's death, burial and rising on the third day.
- **2. The Scandal of Global Grace:** Nineveh, capital of Israel's most brutal enemy; Jonah 4:2 shows he fled because he knew God is gracious; salvation is not bound by ethnicity or past wickedness.
- **3. The Contrast of Two Saviors:** in the storm (Jonah's disobedience caused it; Jesus calmed it, Mark 4); the sacrifice (thrown into the sea to save the sailors → the true and better Jonah); the heart (Jonah on a hill wanting the city to burn; Jesus wept over Jerusalem and died to save it).
- **Summary:** God relentlessly pursues rebels, both the pagan city and His own prophet; "salvation belongs to the Lord, and His grace is shockingly wider than our human borders."
- **Storyboard:** 5 scenes, 34 shots of 4–11 s; symbolic shots for teaching lines (scroll, map, tomb, crosses, the Earth bathed in gold).
- **Titles:** "The Hidden Secret of Jonah (It's Not About the Fish)", "Why Jesus Called Himself 'Jonah'", "The Dark Truth About the Book of Jonah", "Jonah vs. Jesus: The Shocking Comparison", "The Most Misunderstood Book in the Bible".
- **Description chapters:** 0:00 The Real Story of Jonah · 0:39 The Sign of Jonah · 1:25 The Scandal of Global Grace · 2:00 The Contrast of Two Saviors · 2:36 The Ultimate Message of Salvation.
