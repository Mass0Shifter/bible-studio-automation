# Finishing references — intros, subtitles, logo

Reference images in this folder (copies on the PC: `Desktop\Bible Studio\_tools\references\`):

| File | What it is |
|---|---|
| `intro-card-template.png` | Blank intro title card (silhouettes, "BIBLEBOOK", "CHAPTER X", AuthorName…). ChatGPT fills it in for each book/chapter. |
| `chapter-intro-example-ruth-2.jpg` | Finished **chapter** intro card (Ruth 2): the template filled with the chapter's characters, book facts and a key verse. |
| `book-intro-example-ruth.jpg` | Finished **book** intro card (Ruth): no "Chapter X" line, a tagline instead ("The Story of Ruth, Naomi & Boaz"). |
| `lower-third.png` | Transparent lower-third bar the verse subtitles sit on. |
| `logo-can-you-behold-him.png` | Transparent channel logo, placed top-right at 40 % opacity. |
| `subtitle-layout-example-jonah-2.png` | How a finished frame looks: bar, reference block on the left, verse text, logo top-right. |

## Intro animation prompt (Google Flow, start frame = the finished card, 6 s)

> A static animation keeping the original title card's composition, typography, and text exactly as they are. The camera remains completely still. Only animate the natural elements within the background landscape: the leaves on the trees rustle gently in the breeze, faint environmental dust particles float softly in the golden sunset light, and subtle atmospheric haze drifts across the distant hills. No sudden movements, no character animations, keeping everything clean and solemn.

## Book intro narration prompt (Claude writes it; ChatGPT is the fallback)

> Create a short, cinematic introduction for the biblical book [BOOK NAME], designed specifically for voiceover narration.
> Follow this exact structure and style:
> The Book of [BOOK NAME].
> [A short subtitle/tagline describing the central story, characters, or theme of the book.]
>
> Author: [Author or Unknown].
> [Number] Chapters.
> Setting: [Primary setting(s)].
> Period: [Approximate historical period].
>
> This is the story of [BOOK NAME]—[write 1 powerful, cinematic sentence introducing the central character(s), conflict, journey, or message of the book].
>
> Style requirements:
> Keep it concise: approximately 60–100 words.
> Use a cinematic, biblical, documentary-style tone.
> Make it sound natural when spoken aloud.
> Focus on the main story and central theme of the book.
> Make the final sentence feel dramatic and intriguing, encouraging the listener to continue.
> Use historically and biblically accurate information.
> Do not invent details that are uncertain; when authorship or dating is disputed, say "Unknown" or "approximately" as appropriate.
> Avoid academic or overly complicated language.
> Do not summarize the entire book.
> Do not include chapter-by-chapter details.
> Keep the formatting exactly like the example, including bold headings and the blockquote sections.
> Do not add explanations before or after the finished introduction.

The narration then ends with "… Chapter One." and the chapter film starts.

## Subtitle prompt (the user's Gemini method — fallback only)

> Please generate an SRT file aligned with the attached audio. The text must be (BookName) Chapter (X) from the King James Version (KJV). Structure the subtitles strictly verse by verse, placing one entire verse per subtitle block. Additionally, prefix every verse with [VX], where X is the corresponding verse number (for example: [V1] Now it came to pass...). Ensure the timestamps match the pacing of the audio.

Default instead: Claude builds the SRT itself from the exact KJV verses (`BDS.verses`) and the verse timings measured from the voiceover pauses — the same timings the edit uses.
