# Genesis 20: dialogue narration (Abraham + Abimelech speak their own words on screen; God's words = narrator with divine voice)
# + edit plan + Vids clip queue. Timings from ElevenLabs Speech-to-Text (g20_stt.json -> words.json, windows.json, quotes.json).
import json, wave, math, numpy as np
A = '../audio/Genesis_20_voiceover_divine.wav'
w = wave.open(A); sr = w.getframerate(); ch = w.getnchannels(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, ch); w.close()
END = len(a) / sr
WIN = {x['verse']: (x['start'], x['end']) for x in json.load(open('windows.json'))}
Q = json.load(open('quotes.json'))
V = dict(json.load(open('verses.json')))
cut = lambda q: round(Q[q]['start'] - 0.08, 2)            # narration stops just before the quote
aft = lambda q: round((Q[q]['end'] + (Q[q]['next_start'] or Q[q]['end'])) / 2, 2)
ABR = "an aged, gentle, deep male voice"; ABI = "a firm, measured, mature royal baritone voice"
def wl(t): return len(t.split())
SPK = {'v02': ('Abraham', ABR, 'She is my sister:'),
       'v04b': ('Abimelech', ABI, 'Lord, wilt thou slay also a righteous nation?'),
       'v05': ('Abimelech', ABI, V[5]),
       'v09b': ('Abimelech', ABI, 'What hast thou done unto us? and what have I offended thee, that thou hast brought on me and on my kingdom a great sin? thou hast done deeds unto me that ought not to be done.'),
       'v10b': ('Abimelech', ABI, 'What sawest thou, that thou hast done this thing?'),
       'v11b': ('Abraham', ABR, 'Because I thought, Surely the fear of God is not in this place; and they will slay me for my wife’s sake.'),
       'v12': ('Abraham', ABR, V[12]), 'v13': ('Abraham', ABR, V[13]),
       'v15b': ('Abimelech', ABI, 'Behold, my land is before thee: dwell where it pleaseth thee.'),
       'v16b': ('Abimelech', ABI, 'Behold, I have given thy brother a thousand pieces of silver: behold, he is to thee a covering of the eyes, unto all that are with thee, and with all other:')}
SPLEN = {k: max(3, min(15, math.ceil(wl(v[2]) / 2.6 + 1.2))) for k, v in SPK.items()}
LEAD = 0.6
SEQ = [('v01', 1, 'o', WIN[1]), ('v02a', 2, 'lead', (WIN[2][0], cut('abr_v2'))), ('v02', 2, 'sp', None), ('v02c', 2, 'o', (aft('abr_v2'), WIN[2][1])),
       ('v03', 3, 'o', WIN[3]), ('v04', 4, 'lead', (WIN[4][0], cut('abi_v4'))), ('v04b', 4, 'sp', None), ('v05', 5, 'sp', None),
       ('v06', 6, 'o', WIN[6]), ('v07', 7, 'o', WIN[7]), ('v08', 8, 'o', WIN[8]), ('v09', 9, 'lead', (WIN[9][0], cut('abi_v9'))), ('v09b', 9, 'sp', None),
       ('v10', 10, 'lead', (WIN[10][0], cut('abi_v10'))), ('v10b', 10, 'sp', None), ('v11', 11, 'lead', (WIN[11][0], cut('abr_v11'))), ('v11b', 11, 'sp', None),
       ('v12', 12, 'sp', None), ('v13', 13, 'sp', None), ('v14', 14, 'o', WIN[14]), ('v15', 15, 'lead', (WIN[15][0], cut('abi_v15'))), ('v15b', 15, 'sp', None),
       ('v16', 16, 'lead', (WIN[16][0], cut('abi_v16'))), ('v16b', 16, 'sp', None), ('v16c', 16, 'o', (aft('abi_v16'), WIN[16][1])),
       ('v17', 17, 'o', WIN[17]), ('v18', 18, 'o', (WIN[18][0], END))]
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
    else: x['clip_len'] = max(3, min(15, math.ceil(x['duration'] + 0.6)))
    win.append(x)
nv = np.concatenate(out); o = wave.open('../audio/Genesis_20_voiceover_dialogue.wav', 'wb'); o.setnchannels(ch); o.setsampwidth(2); o.setframerate(sr); o.writeframes(nv.tobytes()); o.close()
json.dump(win, open('windows_dialogue20.json', 'w'), indent=1)
shots = []
for x in win:
    s = dict(verse=x['verse'], clip=f"../video/Genesis_20_{x['shot']}.mp4", start=x['start'], end=x['end'], method='auto')
    if x.get('speech'): s['clip_gain'] = 1.3; s['note'] = x['speaker'] + ' speaks his own words'
    shots.append(s)
plan = {'voiceover': '../audio/Genesis_20_voiceover_dialogue.wav', 'music': '../music/Genesis_20_music.wav', 'music_gain_db': -9.8, 'ambient_gain': 0.22, 'dissolve': 0.5, 'outro': 3.0,
        'output': '../final/Genesis_20_clean.mp4', 'badge': {'image': '../../_tools/references/Radiant Golden Portal Emblem.png', 'cx': 1740, 'cy': 898, 'size': 150}, 'shots': shots}
json.dump(plan, open('genesis20_full.json', 'w'), indent=1)
# ---- Vids clip queue
R2 = 'https://pub-2993fb3bf56d45ffb3d678320781fe03.r2.dev/generated_shots/'
IMG = dict(zip(range(1, 19), "mefcch in01vo isjqrt n8migm ogb14k crxawd 1ucxlx m2efti ltc9li enhbwh 1ut7od ptwqdh jrxye7 4lpy3n kgxs5w htrhyc fmlrty zecvde".split()))
SC = {1: 1, 2: 1, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 3, 9: 3, 10: 3, 11: 3, 12: 3, 13: 3, 14: 4, 15: 4, 16: 4, 17: 4, 18: 4}
SH = {1: 1, 2: 2, 3: 1, 4: 2, 5: 3, 6: 4, 7: 5, 8: 1, 9: 2, 10: 3, 11: 4, 12: 5, 13: 6, 14: 1, 15: 2, 16: 3, 17: 4, 18: 5}
img = lambda v: R2 + f"genesis-chapter-20-verse-{v}-scene-{SC[v]}-shot-{SH[v]}-{IMG[v]}.jpg"
K = " Keep every face, beard and garment exactly as in the start image. God is never shown: no figure, no face, no light-being. Everyone stays modestly and fully clothed. No violence. No text on screen."
N = K + " No narration, no voiceover, no dialogue, no music. Natural ambient sound only."
S = lambda who, voice, q: K + f" {who} speaks with clear lip movement, in {voice}: \"{q}\" After the last word he falls silent and holds still. Only {who} speaks; no other voices, no narration, no music. Natural ambient sound underneath."
P = "Static camera, very slight slow push in. "
ACT = {'v01': "Slow forward push. Abraham and Sarah travel with their household, pack animals and tents through the dry southern country toward the low earth-plastered town of Gerar.",
 'v02a': "Slow forward push. In Gerar's shaded courtyard Abraham stands beside Sarah before the king's officials.",
 'v02': P + "In Gerar's shaded courtyard Abraham, beside Sarah, turns to the royal officials and speaks.",
 'v02c': "Slow, gentle pan. Royal attendants respectfully lead Sarah away across the courtyard toward the king's house; Abraham watches, still.",
 'v03': "Very slow push in. Night in a restrained royal chamber: Abimelech lies troubled in sleep beside a flickering clay oil lamp; a cold stillness fills the room.",
 'v04': "Very slow push in on Abimelech's face in the lamplight as he stirs in the dream, eyes lifting toward the empty darkness.",
 'v04b': P + "Abimelech, in the lamplit chamber within the dream, looks up into the empty darkness and pleads.",
 'v05': P + "Abimelech, an open palm near his chest, earnestly explains his innocence in the lamplit chamber, looking into the empty darkness.",
 'v06': "Very slow push in. Abimelech listens, still and sober, lamp and cool night light on his face; he lowers his eyes.",
 'v07': "Slow pull back. The solitary king in his chamber sits up, resolve growing on his face, the closed doorway beyond him; the lamp flame steadies.",
 'v08': "Slow forward push. Early morning council: Abimelech stands before his gathered servants recounting the dream; they exchange worried, fearful glances in the dawn light.",
 'v09': "Slow forward push. In the courtyard Abimelech faces Abraham, firm but controlled.",
 'v09b': P + "Abimelech confronts Abraham in the courtyard, firm but controlled, hand open in question.",
 'v10': "Very slow push in. Abimelech studies Abraham, brows intent.",
 'v10b': P + "Close on Abimelech, brows intent, asking Abraham his final question.",
 'v11': "Very slow push in. Abraham lowers his eyes, then lifts his head to answer.",
 'v11b': P + "Abraham answers with a troubled, candid face, the king listening in soft background.",
 'v12': P + "Abraham, composed and reflective, explains his relationship to Sarah.",
 'v13': P + "Abraham, one weathered hand opening, recounts his earlier agreement with Sarah.",
 'v14': "Slow, gentle pan. In the open courtyard Abimelech's servants lead sheep and oxen to Abraham; Sarah is brought back to stand dignified at Abraham's side.",
 'v15': "Slow forward push. Abimelech turns toward the sunlit land beyond Gerar.",
 'v15b': P + "Abimelech gestures toward the sunlit land beyond Gerar, offering it to Abraham.",
 'v16': "Slow forward push. Abimelech turns respectfully toward Sarah; bundles of weighed silver lie on a low table.",
 'v16b': P + "Abimelech addresses Sarah respectfully beside the weighed silver, Abraham nearby.",
 'v16c': "Slow, gentle push in. Sarah lowers her veiled head with quiet dignity; Abraham places a hand on the silver.",
 'v17': "Slow forward push. Abraham prays with bowed head in the quiet courtyard; Abimelech and his household stand reverently; then warm light, mothers holding infants.",
 'v18': "Very slow pull back. Quiet exterior of Abimelech's household in warm late light, curtains stirring, the courtyard coming to rest."}
q = []
for x in win:
    k = x['shot']; v = x['verse']
    pr = ACT[k] + (S(SPK[k][0], SPK[k][1], SPK[k][2]) if k in SPK else N)
    q.append(dict(key=k, len=x['clip_len'], img=img(v), name=f'Genesis_20_{k}.mp4', prompt=pr))
json.dump(q, open('vids20_queue.json', 'w'), ensure_ascii=False)
for x in win: print(f"{x['shot']:5} {x['start']:7.2f}-{x['end']:7.2f} {x['duration']:5.2f} clip {x['clip_len']}{'  '+x['speaker'] if x.get('speech') else ''}")
print('narration', round(len(nv) / sr, 2), 'clips', len(q), 'clip seconds', sum(i['len'] for i in q))
