import json, re
L = " High-budget 35mm film photograph, photorealistic biblical historical drama, natural atmospheric light, authentic period textiles, 16:9, no text."
A = " Keep every face and garment exactly as in the start image. No narration, no voiceover, no dialogue, no music, no text on screen. Natural ambient sound only."
def C(*names): return "".join(f"[Use existing character model for {n}] " for n in names)
S = []  # (scene_name, [(narration, ref, chars, image, anim)])
S.append(("Hook", [
 ("While the Book of Esther is often told as a royal love story, an orphan girl who wins the king's heart and becomes queen,", None, ["Esther","Ahasuerus"],
  C("Esther","Ahasuerus")+"Inside the Persian throne room of Shushan, King Ahasuerus places the royal crown on young Esther's head; jewelled pillars, purple and white hangings, warm golden-hour light through high windows, medium shot.",
  "Slow push-in on the crowning; silk hangings sway gently, dust motes drift in the light rays."),
 ("it is actually one of the most suspenseful rescue stories in all of Scripture.", None, [],
  "Dusk over the citadel of Shushan: royal couriers on swift horses gallop out of the great gate carrying sealed scrolls, dust rising, storm clouds gathering over the palace, wide shot, tense atmosphere.",
  "Drone pull-back from the gate as the horses ride out; dust trails and drifting clouds."),
 ("And it is the only book in the Bible where the name of God never appears, yet His hand is on every page.", None, [],
  "An ancient Hebrew scroll of Esther unrolled on a dark wooden table, lit by a single oil lamp, a soft beam of heavenly light falling across the written columns, macro close-up, chiaroscuro.",
  "Very slow push-in across the scroll; the lamp flame flickers, light rays shimmer softly."),
 ("When it comes to the grand story of salvation, Esther operates as a hidden hand, a royal mediator, and a great reversal.", None, ["Esther"],
  C("Esther")+"Queen Esther in royal apparel stands alone in a long marble palace corridor, half in shadow, half in a shaft of golden light, looking ahead with quiet resolve, wide shot, Rembrandt lighting.",
  "Slow tracking shot toward Esther; her veil and robe stir slightly, dust motes float in the light shaft."),
 ("Here is the breakdown of Esther's significance to redemptive history.", None, [],
  "Wide aerial view of the Persian palace of Shushan at golden hour, terraces, gardens and pillared halls, the river and city beyond, atmospheric haze.",
  "Slow drone fly-over toward the palace; palm fronds sway, warm haze drifts."),
]))
S.append(("One. The Hidden Hand", [
 ("One. The Hidden Hand — the God who is never named.", None, [],
  "A vast dark Persian palace hall at night, empty, one single beam of soft light falling from a high window across the marble floor, no figure, symbolic stillness, wide shot, volumetric light.",
  "Static camera, very slow push-in; dust motes drift through the beam of light."),
 ("The Silence. No prayer is quoted, and no miracle is shown.", None, [],
  "Night over Shushan: quiet rooftops and palace towers under a starry sky, a few oil lamps glowing in windows, moonlight, wide shot, hushed atmosphere.",
  "Slow pan across the rooftops; lamp flames flicker, a light night breeze moves a curtain."),
 ("Instead we find a sleepless king, a forgotten record, and a petition made at exactly the right moment.", None, ["Ahasuerus"],
  C("Ahasuerus")+"King Ahasuerus sits awake on his bed at night, restless, while a scribe reads to him from the book of the chronicles by lamplight, medium shot, warm candlelight and deep shadows.",
  "Slow push-in on the king's face; the scribe turns a page, lamp flame flickers."),
 ("The Providence. Mordecai trusts that deliverance will come,", None, ["Mordecai"],
  C("Mordecai")+"Mordecai in sackcloth with ashes sits by the king's gate at dawn, looking up toward the palace with steady faith, the first light touching his face, medium close-up.",
  "Slow push-in; morning light grows on his face, dust drifts in the gateway."),
 ("and he asks Esther, \"who knoweth whether thou art come to the kingdom for such a time as this?\"", "Esther 4:14", ["Esther"],
  C("Esther")+"Queen Esther in her palace chamber holds Mordecai's message on a small parchment, her face thoughtful and grave, lamplight and a window of evening light behind her, close-up.",
  "Very slow push-in on Esther's face; her veil stirs, lamp light flickers."),
 ("The Salvation Link. The God who seemed silent in Persia was quietly guarding the people through whom the Messiah would come.", None, [],
  "Jewish families in a Persian city street at dusk, an elder blessing children by a doorway, oil lamps lit, a golden thread of light across the evening sky above them, wide shot.",
  "Slow lateral dolly along the street; lamp flames flicker, garments move in a light breeze."),
 ("As the apostle Paul writes, \"all things work together for good to them that love God.\"", "Romans 8:28", [],
  "An elderly apostle writing a letter with a reed pen on parchment by lamplight in a simple stone room, seen from behind his shoulder, warm light, close-up on the writing hand.",
  "Slow push-in over the shoulder; the pen moves, the lamp flame flickers."),
]))
S.append(("Two. The Ancient Enemy", [
 ("Two. The Ancient Enemy — the war against the promised Seed.", None, [],
  "Dark storm clouds over an ancient desert battlefield at dusk, broken spears and banners in the sand, a distant ridge, ominous atmosphere, wide shot.",
  "Slow drone push over the battlefield; clouds roll, dust blows across the sand."),
 ("The Agagite. Haman is called \"the Agagite\", widely understood as a descendant of Agag, king of Amalek, Israel's oldest enemy.", None, ["Haman"],
  C("Haman")+"Haman in rich embroidered robes stands in a palace colonnade, cold and proud, looking down, hard side light and long shadows, low angle medium shot.",
  "Slow push-in from a low angle; his robe stirs, shadows shift slightly."),
 ("The Decree. He plots to destroy every Jew in the empire in a single day.", None, ["Haman"],
  C("Haman")+"Haman at a table by lamplight casting lots (Pur) from his hand onto a calendar scroll, his face lit from below, dark room, close-up.",
  "Static camera; the small lots tumble onto the scroll, the lamp flame flickers."),
 ("Had he succeeded, the line of promise would have been cut off.", None, [],
  "Royal Persian couriers on horseback racing out of Shushan in every direction carrying sealed decrees, roads stretching across the empire, dramatic dusk sky, wide aerial shot.",
  "Drone fly-over following the riders; dust trails rise behind the horses."),
 ("The Salvation Link. This is the long war first announced in Eden:", None, [],
  "The Garden of Eden at dusk: lush trees and a still stream, a serpent half hidden among the branches of a great tree, soft golden light fading, wide shot.",
  "Slow push-in toward the tree; leaves stir, the serpent's coil moves slightly."),
 ("\"I will put enmity between thee and the woman, and between thy seed and her seed.\"", "Genesis 3:15", [],
  "Close-up of a serpent coiled at the root of a tree in Eden, while a shaft of morning light breaks through the leaves onto the ground beside it, chiaroscuro, symbolic.",
  "Static camera; the light shaft slowly widens, leaves move in the breeze."),
 ("Esther shows that no decree of man can stop the Seed God has promised.", None, [],
  "A Persian royal decree scroll with a cracked wax seal lying on stone steps, morning light breaking across it, macro close-up, symbolic.",
  "Slow push-in on the broken seal; dust motes drift in the sunlight."),
 ("In the fulness of time, Christ was born from that very people.", None, ["Jesus"],
  "Bethlehem at night: Mary, a young Jewish mother, gently holds the newborn baby Jesus in a humble stone stable lit by a lamp, Joseph beside her, reverent and peaceful, medium shot, warm light.",
  "Very slow push-in; the lamp flame glows softly, straw moves slightly."),
]))
S.append(("Three. The Royal Mediator", [
 ("Three. The Royal Mediator — a picture of Christ.", None, ["Esther"],
  C("Esther")+"Queen Esther in royal apparel stands before the tall closed doors of the inner court, guards on either side, light under the doors, wide shot, tense stillness.",
  "Slow push-in toward Esther from behind; her robe and veil stir slightly."),
 ("The Risk. To approach the king uncalled meant death.", None, ["Ahasuerus"],
  C("Ahasuerus")+"King Ahasuerus on his high throne in the inner court, armed guards with spears lining the hall, stern atmosphere, low angle wide shot, shafts of light from high windows.",
  "Slow push-in along the line of guards toward the throne; dust drifts in the light."),
 ("Esther fasts three days, then goes: \"and if I perish, I perish.\"", "Esther 4:16", ["Esther"],
  C("Esther")+"Esther kneels in plain dark garments, fasting and praying alone in a dim chamber, a single candle burning, then rising with resolve, medium close-up, Rembrandt lighting.",
  "Static camera, very slow push-in; the candle flame flickers, Esther slowly lifts her head."),
 ("The Sceptre. \"The king held out to Esther the golden sceptre that was in his hand.", "Esther 5:2", ["Ahasuerus","Esther"],
  C("Ahasuerus","Esther")+"King Ahasuerus on his throne extends the golden sceptre toward Queen Esther standing in the court, his face softened, warm golden light, over-the-shoulder shot from behind Esther.",
  "Slow push-in; the sceptre glints, silk hangings sway gently."),
 ("So Esther drew near, and touched the top of the sceptre.\"", "Esther 5:2", ["Esther"],
  C("Esther")+"Close-up of Queen Esther's hand gently touching the golden top of the king's sceptre, her face in soft focus behind, warm light, macro detail.",
  "Static camera; her fingers touch the sceptre top, light glints on the gold."),
 ("The True and Better Esther. Esther risked her life for her people; Jesus gave His.", None, ["Jesus"],
  "Jesus on the cross on Golgotha seen from a distance at dusk, silhouetted against a dark sky with a break of golden light, reverent, no blood, no wounds visible, wide shot.",
  "Very slow push-in; clouds drift, the light behind the cross slowly grows."),
 ("Esther was received by grace, and through Christ we are invited:", None, ["Esther"],
  C("Esther")+"The great doors of the Persian throne room swing open and warm light floods out onto Queen Esther, who steps forward, welcomed, wide shot from behind her.",
  "Slow tracking forward with Esther; light spills through the opening doors."),
 ("\"Let us therefore come boldly unto the throne of grace, that we may obtain mercy, and find grace to help in time of need.\"", "Hebrews 4:16", [],
  "A heavenly throne of radiant light with no figure seen, only brilliance, and people from many nations walking toward it up broad steps, wide shot, volumetric light, symbolic, reverent.",
  "Slow push-in up the steps; light rays shimmer, robes move gently."),
]))
S.append(("Four. The Great Reversal", [
 ("Four. The Great Reversal — from sorrow to joy.", None, [],
  "Dawn breaking over the city of Shushan after a dark night, the first golden light sweeping across palace walls and rooftops, wide shot.",
  "Time-lapse feel: slow drone push as the sunlight spreads over the city."),
 ("The Gallows. \"So they hanged Haman on the gallows that he had prepared for Mordecai.\"", "Esther 7:10", [],
  "A tall wooden gallows standing empty in a courtyard, silhouetted against a stormy evening sky, no person on it, ominous, low angle wide shot.",
  "Static camera; storm clouds roll behind the gallows, a gust blows dust."),
 ("The Unchangeable Law. The king's first decree could not be undone,", None, ["Ahasuerus"],
  C("Ahasuerus")+"King Ahasuerus at a table of scrolls with scribes, his hand resting on a sealed decree, troubled expression, lamplit chamber, medium shot.",
  "Slow push-in; a scribe unrolls a scroll, lamp flames flicker."),
 ("so a second was written and sealed with the king's ring, a writing that \"may no man reverse.\"", "Esther 8:8", ["Mordecai"],
  C("Mordecai")+"Mordecai in royal blue and white apparel presses the king's signet ring into red wax on a new decree, scribes writing behind him, close-up on the seal, warm light.",
  "Static camera; the ring presses into the wax, a thin curl of candle smoke rises."),
 ("The Gospel Turn. The day meant for destruction became the month \"turned unto them from sorrow to joy.\"", "Esther 9:22", [],
  "Jewish families in Shushan celebrating with a joyful feast, sharing portions and gifts, lamps and garlands, children laughing, warm evening light, wide shot.",
  "Slow lateral dolly along the feast; lamp flames flicker, garments and garlands sway."),
 ("At the cross, the very weapon the enemy raised against the Son became the enemy's own defeat.", None, [],
  "An empty wooden cross on Golgotha at sunrise, golden light breaking through dark clouds behind it, reverent, wide shot, volumetric rays.",
  "Slow push-in toward the cross; clouds part and light rays spread."),
 ("Christ \"made a shew of them openly, triumphing over them in it.\"", "Colossians 2:15", [],
  "The garden tomb at sunrise with the great stone rolled away and bright light streaming from the open entrance, wide shot, triumphant and peaceful.",
  "Slow push-in toward the open tomb; light rays and mist drift out."),
 ("The sentence against us was real, but God wrote a better word, sealed in the blood of His Son.", None, [],
  "An old written decree scroll with a deep red wax seal lying at the foot of a wooden cross on stony ground, morning light falling on it, close-up, symbolic, no gore.",
  "Static camera, very slow push-in; light slowly brightens across the scroll."),
]))
S.append(("Summary", [
 ("Esther reminds us that even when God seems silent, He is never absent.", None, ["Esther"],
  C("Esther")+"Queen Esther at a palace window at night, looking up at a sky full of stars, moonlight on her face, peaceful, medium close-up.",
  "Slow push-in; stars twinkle, a light breeze moves her veil."),
 ("He raised up a queen for such a time as this, guarded the line of the promised Seed,", None, ["Esther","Mordecai"],
  C("Esther","Mordecai")+"Queen Esther seated in royal apparel in the throne room with Mordecai standing beside her in royal garments, warm golden light, dignified, medium wide shot.",
  "Slow push-in; banners and silk hangings sway gently."),
 ("and turned a day of death into a feast of joy.", None, [],
  "A joyful Purim feast in a lamplit courtyard, families sharing food and gifts with the poor, music-makers and dancing children, warm evening light, wide shot.",
  "Slow drone rise over the courtyard; lamp flames flicker, garments swirl."),
 ("And in Jesus, the true and better Mediator, the King's sceptre is held out to all who will come.", None, [],
  "A golden sceptre extended in radiant light toward a great crowd of people from many nations standing under the stars, wide shot, symbolic, reverent.",
  "Slow push-in through the crowd toward the light; light rays shimmer."),
 ("The hidden hand of God in Esther points us to the open, nail-scarred hands of Christ.", None, ["Jesus"],
  "Close-up of the open hands of Jesus held out in welcome, gentle healed nail scars on the palms, soft warm light, white robe sleeves, reverent, no blood.",
  "Static camera, very slow push-in; soft light rays move across the hands."),
]))
S.append(("Outro", [
 ("If this helped you see Christ in the Book of Esther, subscribe to Can You Behold Him, and behold the Word with us, book by book.", None, [],
  "Video: CAN_YOU_BEHOLD_HIM_OUTTRO.mp4 (channel outro — no picture or clip to make)", "Video: CAN_YOU_BEHOLD_HIM_OUTTRO.mp4 (channel outro — no picture or clip to make)"),
]))

# ---- spoken text from the approved script, for the word-order check
src = open('PI_script.md').read().split('\n---')[0]
spoken = []
for line in src.splitlines():
    line = line.strip()
    if not line or line.startswith('# '): continue
    m = re.match(r'## (\d)\. (.+?) \((.+)\)$', line)
    if m:
        n = ['One','Two','Three','Four'][int(m.group(1))-1]; spoken.append(f"{n}. {m.group(2)} — {m.group(3).lower()}."); continue
    if line == '## Summary': continue
    line = re.sub(r'\*\*(.+?):\*\*', r'\1.', line)
    line = re.sub(r'\s*\((?:[1-3] )?[A-Z][a-z]+ \d+:\d+\)', '', line)
    spoken.append(line)
norm = lambda t: re.sub(r'[^a-z0-9]+', ' ', t.lower().replace('’',"'")).split()
want = norm(' '.join(spoken))
got = norm(' '.join(sh[0] for _, shots in S for sh in shots))
if want != got:
    for i,(a,b) in enumerate(zip(want,got)):
        if a!=b: print('MISMATCH at', i, want[i-5:i+8], got[i-5:i+8]); break
    print('len', len(want), len(got)); raise SystemExit(1)

out = []; md = ["# The Book of Esther — Prophetic Implication: storyboard", "",
  "Narration = the approved script (Esther_PI_script.md), every word in order. Scripture references are not spoken; they are shown with the quote in the subtitles (field `ref`). Estimated time = words ÷ 2.3.", ""]
tot = 0
for si, (name, shots) in enumerate(S, 1):
    md += [f"## Scene {si}: {name}", ""]
    for hi, (nar, ref, chars, img, anim) in enumerate(shots, 1):
        w = len(nar.split()); est = round(w / 2.3); tot += w / 2.3
        outro = img.startswith('Video:')
        ip = img if outro else img + L
        ap = anim if outro else anim + A
        out.append(dict(scene=si, scene_name=name, shot=f"{si}.{hi}", est_s=est, words=w, narration=nar, ref=ref, image_prompt=ip, animation_prompt=ap, characters=chars))
        md += [f"### Shot {si}.{hi} (~{est}s)", f"Narration: \"{nar}\"" + (f"  \n_Reference on screen: {ref}_" if ref else ""), f"Image Prompt: \"{ip}\"", f"Animation Prompt: \"{ap}\"", ""]
mx = max(o['words'] for o in out)
md += ["---", f"**{len(S)} scenes, {len(out)} shots, estimated narration ≈ {int(tot//60)}:{int(round(tot%60)):02d}** (longest shot {mx} words).",
       "Characters with Character Library portraits used: Esther, Mordecai, Haman, Ahasuerus. Jesus appears reverently (birth, cross from a distance, open hands with healed scars, empty tomb) — no gore. God is never shown (light / an empty radiant throne only). The apostle Paul (Shot 2.7) has no portrait: shown from behind."]
open('./Esther_PI_storyboard.md','w').write('\n'.join(md)+'\n')
json.dump(out, open('./Esther_PI_storyboard.json','w'), ensure_ascii=False, indent=1)
print('scenes', len(S), 'shots', len(out), 'total_s', round(tot,1), 'longest', mx, [ (o['shot'],o['words']) for o in out if o['words']>25])
