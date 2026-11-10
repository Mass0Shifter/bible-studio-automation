# Genesis 22: dialogue narration (Abraham + Isaac speak their own words on screen; God's and the angel's words =
# narrator with divine/angel voice, done by divine_voice.py -> Genesis_22_voiceover_divine.wav) + edit plan + Vids clip queue.
# Timings: ElevenLabs STT (g22_stt.json) -> stt_align.py -> windows.json, words.json.
import json, wave, math, re, numpy as np
A = '../audio/Genesis_22_voiceover_divine.wav'
w = wave.open(A); sr = w.getframerate(); ch = w.getnchannels(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, ch); w.close()
END = len(a) / sr
WIN = {x['verse']: (x['start'], x['end']) for x in json.load(open('windows.json'))}
W = json.load(open('words.json')); V = dict(json.load(open('verses.json')))
norm = lambda t: re.sub(r'[^a-z]', '', t.lower())
def quote(v, text):           # times of an exact run of words inside verse v
    ws = [x for x in W if x['verse'] == v]; t = [norm(x) for x in text.split()]
    for i in range(len(ws) - len(t) + 1):
        if [norm(x['w']) for x in ws[i:i + len(t)]] == t:
            allw = W.index(ws[i]); j = W.index(ws[i + len(t) - 1])
            pe = W[allw - 1]['e'] if allw else 0.0; ns = W[j + 1]['s'] if j + 1 < len(W) else END
            return dict(start=ws[i]['s'], end=ws[i + len(t) - 1]['e'], prev_end=pe, next_start=ns, text=text, verse=v)
    raise SystemExit('quote not found: %s %s' % (v, text))
ABR = "an aged, gentle, deep male voice"; ISA = "a clear, warm young man's voice, gentle and trusting"
Q = {'abr1': quote(1, 'Behold, here I am.'),
     'abr5': quote(5, 'Abide ye here with the ass; and I and the lad will go yonder and worship, and come again to you,'),
     'isa7a': quote(7, 'My father:'), 'abr7': quote(7, 'Here am I, my son.'),
     'isa7b': quote(7, 'Behold the fire and the wood: but where is the lamb for a burnt offering?'),
     'abr8': quote(8, 'My son, God will provide himself a lamb for a burnt offering:'),
     'abr11': quote(11, 'Here am I.')}
json.dump(Q, open('quotes.json', 'w'), indent=1)
cut = lambda q: round(Q[q]['prev_end'] + min(0.06, (Q[q]['start'] - Q[q]['prev_end']) / 2), 2)   # narration stops right after the framing words
aft = lambda q: round((Q[q]['end'] + Q[q]['next_start']) / 2, 2)
def wl(t): return len(t.split())
SPK = {'v01b': ('Abraham', ABR, 'abr1'), 'v05b': ('Abraham', ABR, 'abr5'), 'v07b': ('Isaac', ISA, 'isa7a'), 'v07d': ('Abraham', ABR, 'abr7'),
       'v07f': ('Isaac', ISA, 'isa7b'), 'v08b': ('Abraham', ABR, 'abr8'), 'v11b': ('Abraham', ABR, 'abr11')}
SPK = {k: (n, vo, Q[q]['text'].rstrip(',:;')) for k, (n, vo, q) in SPK.items()}
SPLEN = {k: max(4, min(15, math.ceil(wl(v[2]) / 2.6 + 1.6))) for k, v in SPK.items()}
LEAD = 0.6
SEQ = [('v01', 1, 'lead', (WIN[1][0], cut('abr1'))), ('v01b', 1, 'sp', None),
       ('v02', 2, 'o', WIN[2]), ('v03', 3, 'o', WIN[3]), ('v04', 4, 'o', WIN[4]),
       ('v05', 5, 'lead', (WIN[5][0], cut('abr5'))), ('v05b', 5, 'sp', None), ('v06', 6, 'o', WIN[6]),
       ('v07', 7, 'lead', (WIN[7][0], cut('isa7a'))), ('v07b', 7, 'sp', None), ('v07c', 7, 'lead', (aft('isa7a'), cut('abr7'))), ('v07d', 7, 'sp', None),
       ('v07e', 7, 'lead', (aft('abr7'), cut('isa7b'))), ('v07f', 7, 'sp', None),
       ('v08', 8, 'lead', (WIN[8][0], cut('abr8'))), ('v08b', 8, 'sp', None), ('v08c', 8, 'o', (aft('abr8'), WIN[8][1])),
       ('v09', 9, 'o', WIN[9]), ('v10', 10, 'o', WIN[10]), ('v11', 11, 'lead', (WIN[11][0], cut('abr11'))), ('v11b', 11, 'sp', None),
       ('v12', 12, 'o', WIN[12]), ('v13', 13, 'o', WIN[13]), ('v14', 14, 'o', WIN[14]), ('v15', 15, 'o', (WIN[15][0], WIN[16][1])),
       ('v17', 17, 'o', WIN[17]), ('v18', 18, 'o', WIN[18]), ('v19', 19, 'o', WIN[19]), ('v20', 20, 'o', WIN[20]),
       ('v21', 21, 'o', (WIN[21][0], WIN[22][1])), ('v23', 23, 'o', WIN[23]), ('v24', 24, 'o', (WIN[24][0], END))]
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
nv = np.concatenate(out); o = wave.open('../audio/Genesis_22_voiceover_dialogue.wav', 'wb'); o.setnchannels(ch); o.setsampwidth(2); o.setframerate(sr); o.writeframes(nv.tobytes()); o.close()
json.dump(win, open('windows_dialogue22.json', 'w'), indent=1)
shots = []
for x in win:
    s = dict(verse=x['verse'], clip=f"../video/Genesis_22_{x['shot']}.mp4", start=x['start'], end=x['end'], method='auto')
    if x.get('speech'): s['clip_gain'] = 1.3; s['note'] = x['speaker'] + ' speaks his own words'
    shots.append(s)
plan = {'voiceover': '../audio/Genesis_22_voiceover_dialogue.wav', 'music': '../music/Genesis_22_music.wav', 'music_gain_db': -9.8, 'ambient_gain': 0.22, 'dissolve': 0.5, 'outro': 3.0,
        'output': '../final/Genesis_22_clean.mp4', 'badge': {'image': '../../_tools/references/Radiant Golden Portal Emblem.png', 'cx': 1740, 'cy': 898, 'size': 150}, 'shots': shots}
json.dump(plan, open('genesis22_full.json', 'w'), indent=1)
# ---- Vids clip queue (pictures: verse -> r2 image; speech shots use the closest picture of the speaker)
R2 = 'https://pub-2993fb3bf56d45ffb3d678320781fe03.r2.dev/generated_shots/'
IMG = {1: '1-scene-1-shot-1-eegnl4.png', 2: '2-scene-1-shot-2-srtckn.png', 3: '3-scene-2-shot-1-igbs74.png', 4: '4-scene-2-shot-2-xrjm48.png',
       5: '5-scene-2-shot-3-rhpq5v.png', 6: '6-scene-2-shot-4-s0hy3f.png', 7: '7-scene-2-shot-5-h8oef6.png', 8: '8-scene-2-shot-6-b6yndu.png',
       9: '9-scene-3-shot-1-xvwxly.png', 10: '10-scene-3-shot-2-z2muyn.png', 11: '11-scene-3-shot-3-0w7m06.png', 12: '12-scene-3-shot-4-q5jrd0.png',
       13: '13-scene-3-shot-5-ah6ki5.png', 14: '14-scene-3-shot-6-jhqucf.png', 15: '15-scene-4-shot-1-bas8u6.png', 17: '17-scene-4-shot-2-9xvulr.png',
       18: '18-scene-4-shot-3-hxpnlm.jpg', 19: '19-scene-4-shot-4-zjfobh.jpg', 20: '20-scene-5-shot-1-om72vx.jpg', 21: '21-scene-5-shot-2-hv4pmq.jpg',
       23: '23-scene-5-shot-3-gfyzfh.jpg', 24: '24-scene-5-shot-4-hkwlgf.jpg'}
PIC = {'v07c': 7, 'v07d': 7, 'v07e': 7, 'v07f': 7, 'v08b': 7, 'v11b': 12}
img = lambda k, v: R2 + 'genesis-chapter-22-verse-' + IMG[PIC.get(k, v)]
K = " Keep every face, beard and garment exactly as in the start image. God is never shown: no figure, no face, no light-being. Everyone stays modestly and fully clothed. No violence, no blood, the knife is never used. No text on screen."
N = K + " No narration, no voiceover, no dialogue, no music. Natural ambient sound only."
S = lambda who, voice, q: K + f" {who} speaks with clear lip movement, in {voice}: \"{q}\" After the last word he falls silent and holds still. Only {who} speaks; no other voices, no narration, no music. Natural ambient sound underneath."
P = "Static camera, very slight slow push in. "
AB = "the white-bearded elder Abraham in the striped brown hooded robe"; IS = "the young man Isaac with dark curly hair and short beard, in the cream tunic with green sash"
ACT = {'v01': "Very slow push in. Night at the tent door: Abraham looks up toward the starry sky, hands lifting, listening in awe as cool light falls on his face.",
 'v01b': P + f"Night at the tent door: {AB} lifts his face toward the sky and answers.",
 'v02': "Very slow push in on Abraham's troubled face in the dim tent; behind him Isaac sleeps peacefully; the oil lamp flickers.",
 'v03': "Slow pan. Before dawn Abraham saddles the donkey; servants bind split wood; Isaac lifts a bundle; breath and dust in the cold blue light.",
 'v04': "Slow forward push. On the third day Abraham shades his eyes and gazes at the distant mountain; Isaac and the servants stop beside him; warm wind.",
 'v05': "Slow, gentle push in. Abraham turns to his two young servants beside the donkey, one hand raised.",
 'v05b': P + f"{AB} turns to the two young servants beside the donkey, one hand open, and speaks calmly.",
 'v06': "Slow tracking forward. Isaac carries the bundle of wood on his back; Abraham walks beside him holding the fire pot and his staff; the two climb together.",
 'v07': "Very slow push in. Walking side by side, Isaac turns his head toward his father.",
 'v07b': P + f"Walking beside his father, {IS} turns his head toward him and speaks.",
 'v07c': "Very slow push in. Abraham turns his face toward his son.",
 'v07d': P + f"{AB} turns his face toward his son and answers tenderly.",
 'v07e': "Very slow push in. Isaac shifts the wood on his back and looks at his father.",
 'v07f': P + f"{IS}, the wood on his back, looks at his father and asks.",
 'v08': "Slow forward push. On the rocky path Abraham walks beside Isaac.",
 'v08b': P + f"{AB}, walking beside Isaac, answers him quietly and steadily.",
 'v08c': "Slow pull back. Father and son walk on together up the rocky mountain path in the golden light.",
 'v09': "Slow push in. On the mountain top Abraham kneels by the stone altar; Isaac lies still and trusting on the wood; evening light.",
 'v10': "Very slow push in. Abraham stands beside the altar, his arm raised toward the sky, the sun low behind; Isaac lies calmly on the wood. No knife shown striking.",
 'v11': "Slow crane down. Golden light breaks through the clouds over the altar; Abraham freezes and looks up toward the sky.",
 'v11b': P + f"{AB}, kneeling by the altar beside Isaac, looks up toward the light and answers.",
 'v12': "Very slow push in. Abraham gently rests his hand on Isaac's shoulder; relief and tears in his eyes; warm light.",
 'v13': "Slow pan. Abraham reaches into the thicket where a ram is caught by its horns; Isaac sits free by the altar; thin smoke rises.",
 'v14': "Slow pull back. Abraham and Isaac stand together beside the smoking altar at sunset, looking out over the mountains.",
 'v15': "Very slow push in. Abraham bows low to the ground beside the altar in golden light from the sky; Isaac kneels nearby.",
 'v17': "Very slow pull back. Night: Abraham stands alone on the hilltop under a vast sky full of stars; the distant sea glimmers.",
 'v18': "Slow push in. Abraham and Isaac stand side by side at sunset, peaceful, the valley glowing below.",
 'v19': "Slow tracking backward. Abraham, Isaac and the young servants with the donkey walk home down the road toward Beer-sheba.",
 'v20': "Slow push in. Under a tent awning a messenger tells Abraham the news with open hands; Abraham listens, nodding.",
 'v21': "Slow pan across Nahor's busy family camp by the river: herdsmen, sheep, tents, children.",
 'v23': "Slow push in. A young woman, Rebekah, draws water at the well while an older kinsman watches; sheep nearby.",
 'v24': "Slow pull back. A wide family camp at sunset: tents, a cooking fire, children running, flocks resting."}
q = []
for x in win:
    k = x['shot']; v = x['verse']
    pr = ACT[k] + (S(SPK[k][0], SPK[k][1], SPK[k][2]) if k in SPK else N)
    q.append(dict(key=k, len=x['clip_len'], img=img(k, v), name=f'Genesis_22_{k}.mp4', prompt=pr))
json.dump(q, open('vids22_queue.json', 'w'), ensure_ascii=False)
for x in win: print(f"{x['shot']:5} {x['start']:7.2f}-{x['end']:7.2f} {x['duration']:5.2f} clip {x['clip_len']}{'  '+x['speaker']+': '+x['words'] if x.get('speech') else ''}")
print('narration', round(len(nv) / sr, 2), 'clips', len(q), 'clip seconds', sum(i['len'] for i in q))
