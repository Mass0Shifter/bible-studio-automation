# Genesis 23: dialogue narration (Abraham, an elder of the sons of Heth and Ephron speak their own words on screen)
# + edit plan + Vids clip queue. Timings: Vids caption track + pauses (g23_pseudo_stt.py) -> stt_align.py -> words.json,
# windows.json, then snap_windows.py (verse boundaries on real pauses). No God/angel speech in this chapter.
import json, wave, math, re, subprocess, numpy as np
A = '../audio/Genesis_23_voiceover.wav'
w = wave.open(A); sr = w.getframerate(); ch = w.getnchannels(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, ch); w.close()
END = len(a) / sr
WIN = {x['verse']: (x['start'], x['end']) for x in json.load(open('windows.json'))}
W = json.load(open('words.json')); V = dict(json.load(open('verses.json')))
r = subprocess.run(['ffmpeg', '-i', A, '-af', 'silencedetect=noise=-35dB:d=0.12', '-f', 'null', '-'], capture_output=True, text=True).stderr
PZ = list(zip([float(x) for x in re.findall(r'silence_start: ([\d.]+)', r)], [float(x) for x in re.findall(r'silence_end: ([\d.]+)', r)]))
norm = lambda t: re.sub(r'[^a-z]', '', t.lower())
def wpos(v, text):   # (start of first word, end of last word) of an exact word run in verse v
    ws = [x for x in W if x['verse'] == v]; t = [norm(x) for x in text.split()]
    for i in range(len(ws) - len(t) + 1):
        if [norm(x['w']) for x in ws[i:i + len(t)]] == t: return ws[i]['s'], ws[i + len(t) - 1]['e']
    raise SystemExit('quote not found: %s %s' % (v, text))
def pause_near(t, lim=0.9):   # centre of the real pause nearest to t
    c = [(s + e) / 2 for s, e in PZ if abs((s + e) / 2 - t) < lim]
    if not c: raise SystemExit('no pause near %.2f' % t)
    return round(min(c, key=lambda x: abs(x - t)), 2)
ABR = "an aged, gentle, deep male voice"; HET = "a dignified, weathered old man's voice, courteous and warm"; EPH = "a smooth, confident, courteous baritone voice"
q8 = 'If it be your mind that I should bury my dead out of my sight; hear me, and intreat for me to Ephron the son of Zohar,'
q9a = 'That he may give me the cave of Machpelah, which he hath, which is in the end of his field;'
q9b = 'for as much money as it is worth he shall give it me for a possession of a buryingplace amongst you.'
q13 = 'But if thou wilt give it, I pray thee, hear me: I will give thee money for the field; take it of me, and I will bury my dead there.'
CUT8 = pause_near(wpos(8, q8)[0] - 0.15); CUT13 = pause_near(wpos(13, q13)[0] - 0.15)
SPK = {'v04': ('Abraham', ABR, V[4]), 'v06': ('the white-bearded elder of the sons of Heth', HET, V[6]),
       'v08b': ('Abraham', ABR, q8), 'v09': ('Abraham', ABR, q9a), 'v09b': ('Abraham', ABR, q9b),
       'v11': ('Ephron', EPH, V[11]), 'v13b': ('Abraham', ABR, q13), 'v15': ('Ephron', EPH, V[15])}
wl = lambda t: len(t.split())
SPLEN = {k: max(4, min(15, math.ceil(wl(v[2]) / 2.6 + 1.6))) for k, v in SPK.items()}
LEAD = 0.6
SEQ = [('v01', 1, 'o', WIN[1]), ('v02', 2, 'o', WIN[2]), ('v03', 3, 'lead', WIN[3]), ('v04', 4, 'sp', None),
       ('v05', 5, 'lead', WIN[5]), ('v06', 6, 'sp', None), ('v07', 7, 'o', WIN[7]),
       ('v08', 8, 'lead', (WIN[8][0], CUT8)), ('v08b', 8, 'sp', None), ('v09', 9, 'sp', None), ('v09b', 9, 'sp', None),
       ('v10', 10, 'lead', WIN[10]), ('v11', 11, 'sp', None), ('v12', 12, 'o', WIN[12]),
       ('v13', 13, 'lead', (WIN[13][0], CUT13)), ('v13b', 13, 'sp', None), ('v14', 14, 'lead', WIN[14]), ('v15', 15, 'sp', None),
       ('v16', 16, 'o', WIN[16]), ('v17', 17, 'o', WIN[17]), ('v18', 18, 'o', WIN[18]), ('v19', 19, 'o', WIN[19]), ('v20', 20, 'o', (WIN[20][0], END))]
out = []; t = 0.0; win = []
def put(x):
    global t; out.append(x); t += len(x) / sr
for k, v, kind, d in SEQ:
    s0 = t
    if kind == 'sp': put(np.zeros((int(round((SPLEN[k] - 0.5) * sr)), ch), np.int16))
    else:
        seg = a[int(round(d[0] * sr)):int(round(d[1] * sr))].copy(); n = int(0.02 * sr)
        seg[:n] = (seg[:n] * np.linspace(0, 1, n)[:, None]).astype(np.int16); seg[-n:] = (seg[-n:] * np.linspace(1, 0, n)[:, None]).astype(np.int16)
        put(seg)
        if kind == 'lead': put(np.zeros((int(LEAD * sr), ch), np.int16))
    x = dict(shot=k, verse=v, start=round(s0, 3), end=round(t, 3), duration=round(t - s0, 3))
    if kind == 'sp': x.update(speech=True, clip_len=SPLEN[k], speaker=SPK[k][0], words=SPK[k][2])
    else: x['clip_len'] = max(4, min(15, math.ceil(x['duration'] + 0.6)))
    win.append(x)
nv = np.concatenate(out); o = wave.open('../audio/Genesis_23_voiceover_dialogue.wav', 'wb'); o.setnchannels(ch); o.setsampwidth(2); o.setframerate(sr); o.writeframes(nv.tobytes()); o.close()
json.dump(win, open('windows_dialogue23.json', 'w'), indent=1)
shots = []
for x in win:
    s = dict(verse=x['verse'], clip=f"../video/Genesis_23_{x['shot']}.mp4", start=x['start'], end=x['end'], method='auto')
    if x.get('speech'): s['clip_gain'] = 1.3; s['note'] = x['speaker'] + ' speaks his own words'
    shots.append(s)
plan = {'voiceover': '../audio/Genesis_23_voiceover_dialogue.wav', 'music': '../music/Genesis_23_music.wav', 'music_gain_db': -9.8, 'ambient_gain': 0.22, 'dissolve': 0.5, 'outro': 3.0,
        'output': '../final/Genesis_23_clean.mp4', 'badge': {'image': '../../_tools/references/Radiant Golden Portal Emblem.png', 'cx': 1740, 'cy': 898, 'size': 150}, 'shots': shots}
json.dump(plan, open('genesis23_full.json', 'w'), indent=1)
# ---- Vids clip queue
R2 = 'https://pub-2993fb3bf56d45ffb3d678320781fe03.r2.dev/generated_shots/genesis-chapter-23-verse-'
IMG = dict(zip(range(1, 21), ('1-scene-1-shot-1-ozsmfl 2-scene-1-shot-2-qredew 3-scene-2-shot-1-drcz37 4-scene-2-shot-2-vokua0 5-scene-2-shot-3-jvasbr '
    '6-scene-2-shot-4-zghxu5 7-scene-2-shot-5-3nived 8-scene-2-shot-6-zcri6q 9-scene-2-shot-7-cfkvv6 10-scene-3-shot-1-gon92v 11-scene-3-shot-2-utnede '
    '12-scene-3-shot-3-dtdhpl 13-scene-3-shot-4-2yfkwp 14-scene-3-shot-5-zxklbf 15-scene-3-shot-6-xtnc5p 16-scene-3-shot-7-4qdurb 17-scene-4-shot-1-ygq3v5 '
    '18-scene-4-shot-2-3umujf 19-scene-4-shot-3-c3hqec 20-scene-4-shot-4-cb6mhc').split()))
PIC = {'v08b': 8, 'v09': 4, 'v09b': 8, 'v13b': 13}
img = lambda k, v: R2 + IMG[PIC.get(k, v)] + '.jpg'
K = " Keep every face, beard and garment exactly as in the start image. God is never shown: no figure, no face, no light-being. Everyone stays modestly and fully clothed. No violence. Sarah's body stays fully wrapped and still. No text on screen."
N = K + " No narration, no voiceover, no dialogue, no music. Natural ambient sound only."
S = lambda who, voice, q: K + f" {who} speaks with clear lip movement, in {voice}: \"{q}\" After the last word he falls silent and holds still. Only {who} speaks; no other voices, no narration, no music. Natural ambient sound underneath."
P = "Static camera, very slight slow push in. "
AB = "the white-bearded elder Abraham in the striped cream-and-brown hooded mantle"; HE = "the white-bearded elder of the sons of Heth in the dark blue robe"
EP = "Ephron the Hittite, the man with dark curly hair and short beard in the deep red robe"
ACT = {'v01': "Very slow pull back. Sunset over the hills of Hebron; olive trees and Abraham's lamplit tents below; a still, sorrowful calm.",
 'v02': "Very slow push in. Inside the lamplit tent Abraham sits beside Sarah, who lies peacefully at rest wrapped in cream cloth; he bows his head and weeps quietly.",
 'v03': "Slow tracking forward. Abraham, staff in hand, walks across the dusty square toward the elders of Heth seated by the city wall.",
 'v04': P + f"Among the elders by the city wall, {AB}, one hand on his chest, speaks humbly to the sons of Heth.",
 'v05': "Slow pan across the seated elders of Heth under the great tree; they turn toward Abraham, nodding respectfully.",
 'v06': P + f"Under the great tree, {HE} opens his hands warmly toward Abraham and speaks.",
 'v07': "Slow push in. Abraham bows low before the gathered people of the land; the elders watch with respect.",
 'v08': "Slow forward push. Abraham turns to the elders and gestures toward Ephron, who stands among them.",
 'v08b': P + f"{AB} gestures toward Ephron and speaks earnestly to the elders.",
 'v09': P + f"{AB}, one hand on his chest, speaks to the elders with quiet resolve.",
 'v09b': P + f"{AB} gestures toward Ephron and continues speaking calmly.",
 'v10': "Slow push in. At the city gate Ephron steps forward in his deep red robe before the crowd; Abraham waits.",
 'v11': P + f"At the city gate, {EP} spreads his arms generously toward Abraham and speaks.",
 'v12': "Slow push in. Abraham bows down to the ground before the people of the land at the city gate; Ephron watches.",
 'v13': "Slow forward push. Abraham rises and turns to Ephron, one hand raised.",
 'v13b': P + f"{AB} looks at Ephron, one hand raised, and speaks firmly but kindly.",
 'v14': "Slow push in. Ephron smiles and opens his hand toward Abraham; the elders lean in to listen.",
 'v15': P + f"{EP} places a hand on his chest, smiling, and speaks to Abraham.",
 'v16': "Slow push in. Abraham weighs silver on a balance at a table before Ephron and the elders; coins glint in the sun.",
 'v17': "Slow pan across the green field of Machpelah with its olive trees and the cave in the hillside; golden light.",
 'v18': "Slow push in. At the city gate Abraham and Ephron clasp hands to seal the agreement; the elders raise their hands as witnesses.",
 'v19': "Slow, reverent tracking shot. Abraham and his men carry Sarah's wrapped body on a bier into the cave of Machpelah at sunset.",
 'v20': "Very slow pull back. Abraham stands alone by the sealed cave in the warm sunset light, the field quiet and peaceful."}
q = []
for x in win:
    k = x['shot']; v = x['verse']
    pr = ACT[k] + (S(SPK[k][0], SPK[k][1], SPK[k][2]) if k in SPK else N)
    q.append(dict(key=k, len=x['clip_len'], img=img(k, v), name=f'Genesis_23_{k}.mp4', prompt=pr))
json.dump(q, open('vids23_queue.json', 'w'), ensure_ascii=False)
for x in win: print(f"{x['shot']:5} {x['start']:7.2f}-{x['end']:7.2f} {x['duration']:5.2f} clip {x['clip_len']}{'  '+x['speaker'] if x.get('speech') else ''}")
print('cuts v8 %.2f v13 %.2f' % (CUT8, CUT13), 'narration', round(len(nv) / sr, 2), 'clips', len(q), 'clip seconds', sum(i['len'] for i in q))
