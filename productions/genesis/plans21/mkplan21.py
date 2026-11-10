# Genesis 21: dialogue narration (Sarah, Hagar, Abimelech, Abraham speak their own words on screen; God's words v12-13 =
# narrator with divine voice, the angel's words v17-18 = angel voice, by divine_voice.py -> Genesis_21_voiceover_divine.wav)
# + edit plan + Vids clip queue. Timings: ElevenLabs STT (g21_stt.json) -> stt_align.py -> windows.json, words.json.
# Verse 34 was missing from the Vids export: recorded separately (Genesis_21_v34.mp4) and appended -> Genesis_21_voiceover_full.wav.
import json, wave, math, re, numpy as np
A = '../audio/Genesis_21_voiceover_divine.wav'
w = wave.open(A); sr = w.getframerate(); ch = w.getnchannels(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, ch); w.close()
END = len(a) / sr
WIN = {x['verse']: (x['start'], x['end']) for x in json.load(open('windows.json'))}
W = json.load(open('words.json')); V = dict(json.load(open('verses.json')))
norm = lambda t: re.sub(r'[^a-z]', '', t.lower())
def quote(v, text):
    ws = [x for x in W if x['verse'] == v]; t = [norm(x) for x in text.split()]
    for i in range(len(ws) - len(t) + 1):
        if [norm(x['w']) for x in ws[i:i + len(t)]] == t:
            allw = W.index(ws[i]); j = W.index(ws[i + len(t) - 1])
            pe = W[allw - 1]['e'] if allw else 0.0; ns = W[j + 1]['s'] if j + 1 < len(W) else END
            return dict(start=ws[i]['s'], end=ws[i + len(t) - 1]['e'], prev_end=pe, next_start=ns, text=text, verse=v)
    raise SystemExit('quote not found: %s %s' % (v, text))
SAR = "a warm, joyful elderly woman's voice"; HAG = "a soft, broken, grieving woman's voice"; ABI = "a firm, measured, mature royal baritone voice"; ABR = "an aged, gentle, deep male voice"
Q = {'s6': quote(6, 'God hath made me to laugh, so that all that hear will laugh with me.'),
     's7': quote(7, 'Who would have said unto Abraham, that Sarah should have given children suck? for I have born him a son in his old age.'),
     's10': quote(10, 'Cast out this bondwoman and her son: for the son of this bondwoman shall not be heir with my son, even with Isaac.'),
     'h16': quote(16, 'Let me not see the death of the child.'),
     'a22': quote(22, 'God is with thee in all that thou doest:'),
     'a23a': quote(23, 'Now therefore swear unto me here by God that thou wilt not deal falsely with me, nor with my son, nor with my son’s son:'),
     'a23b': quote(23, 'but according to the kindness that I have done unto thee, thou shalt do unto me, and to the land wherein thou hast sojourned.'),
     'b24': quote(24, 'I will swear.'),
     'a26': quote(26, 'I wot not who hath done this thing: neither didst thou tell me, neither yet heard I of it, but to day.'),
     'a29': quote(29, 'What mean these seven ewe lambs which thou hast set by themselves?'),
     'b30': quote(30, 'For these seven ewe lambs shalt thou take of my hand, that they may be a witness unto me, that I have digged this well.')}
json.dump(Q, open('quotes.json', 'w'), indent=1)
cut = lambda q: round(Q[q]['prev_end'] + min(0.06, (Q[q]['start'] - Q[q]['prev_end']) / 2), 2)
aft = lambda q: round((Q[q]['end'] + Q[q]['next_start']) / 2, 2)
SPK = {'v06b': ('Sarah', SAR, 's6'), 'v07b': ('Sarah', SAR, 's7'), 'v10b': ('Sarah', SAR, 's10'), 'v16b': ('Hagar', HAG, 'h16'),
       'v22b': ('Abimelech', ABI, 'a22'), 'v23': ('Abimelech', ABI, 'a23a'), 'v23b': ('Abimelech', ABI, 'a23b'), 'v24b': ('Abraham', ABR, 'b24'),
       'v26b': ('Abimelech', ABI, 'a26'), 'v29b': ('Abimelech', ABI, 'a29'), 'v30b': ('Abraham', ABR, 'b30')}
SPK = {k: (n, vo, Q[q]['text'].rstrip(',:;')) for k, (n, vo, q) in SPK.items()}
wl = lambda t: len(t.split())
SPLEN = {k: max(4, min(15, math.ceil(wl(v[2]) / 2.6 + 1.6))) for k, v in SPK.items()}
LEAD = 0.6
J = lambda a_, b_: (WIN[a_][0], WIN[b_][1])
SEQ = [('v01', 1, 'o', J(1, 2), 1), ('v03', 3, 'o', J(3, 4), 3), ('v05', 5, 'o', WIN[5], 5),
       ('v06', 6, 'lead', (WIN[6][0], cut('s6')), 6), ('v06b', 6, 'sp', None, 6), ('v07', 7, 'lead', (WIN[7][0], cut('s7')), 6), ('v07b', 7, 'sp', None, 6),
       ('v08', 8, 'o', WIN[8], 8), ('v09', 9, 'o', WIN[9], 9), ('v10', 10, 'lead', (WIN[10][0], cut('s10')), 10), ('v10b', 10, 'sp', None, 10),
       ('v11', 11, 'o', WIN[11], 11), ('v12', 12, 'o', WIN[12], 12), ('v13', 13, 'o', WIN[13], 12), ('v14', 14, 'o', WIN[14], 14), ('v15', 15, 'o', WIN[15], 15),
       ('v16', 16, 'lead', (WIN[16][0], cut('h16')), 16), ('v16b', 16, 'sp', None, 16), ('v16c', 16, 'o', (aft('h16'), WIN[16][1]), 16),
       ('v17', 17, 'o', WIN[17], 17), ('v18', 18, 'o', WIN[18], 17), ('v19', 19, 'o', WIN[19], 19), ('v20', 20, 'o', J(20, 21), 20),
       ('v22', 22, 'lead', (WIN[22][0], cut('a22')), 22), ('v22b', 22, 'sp', None, 22), ('v23', 23, 'sp', None, 22), ('v23b', 23, 'sp', None, 22),
       ('v24', 24, 'lead', (WIN[24][0], cut('b24')), 24), ('v24b', 24, 'sp', None, 24), ('v25', 25, 'o', WIN[25], 24),
       ('v26', 26, 'lead', (WIN[26][0], cut('a26')), 24), ('v26b', 26, 'sp', None, 24), ('v27', 27, 'o', J(27, 28), 27),
       ('v29', 29, 'lead', (WIN[29][0], cut('a29')), 29), ('v29b', 29, 'sp', None, 29), ('v30', 30, 'lead', (WIN[30][0], cut('b30')), 29), ('v30b', 30, 'sp', None, 29),
       ('v31', 31, 'o', J(31, 32), 31), ('v33', 33, 'o', (WIN[33][0], END), 33)]
out = []; t = 0.0; win = []
def put(x):
    global t; out.append(x); t += len(x) / sr
for k, v, kind, d, pic in SEQ:
    s0 = t
    if kind == 'sp': put(np.zeros((int(round((SPLEN[k] - 0.5) * sr)), ch), np.int16))
    else:
        seg = a[int(round(d[0] * sr)):int(round(d[1] * sr))].copy(); n = int(0.02 * sr)
        seg[:n] = (seg[:n] * np.linspace(0, 1, n)[:, None]).astype(np.int16); seg[-n:] = (seg[-n:] * np.linspace(1, 0, n)[:, None]).astype(np.int16)
        put(seg)
        if kind == 'lead': put(np.zeros((int(LEAD * sr), ch), np.int16))
    x = dict(shot=k, verse=v, pic=pic, start=round(s0, 3), end=round(t, 3), duration=round(t - s0, 3))
    if kind == 'sp': x.update(speech=True, clip_len=SPLEN[k], speaker=SPK[k][0], words=SPK[k][2])
    else: x['clip_len'] = max(4, min(15, math.ceil(x['duration'] + 0.6)))
    win.append(x)
nv = np.concatenate(out); o = wave.open('../audio/Genesis_21_voiceover_dialogue.wav', 'wb'); o.setnchannels(ch); o.setsampwidth(2); o.setframerate(sr); o.writeframes(nv.tobytes()); o.close()
json.dump(win, open('windows_dialogue21.json', 'w'), indent=1)
shots = []
for x in win:
    s = dict(verse=x['verse'], clip=f"../video/Genesis_21_{x['shot']}.mp4", start=x['start'], end=x['end'], method='auto')
    if x.get('speech'): s['clip_gain'] = 1.3; s['note'] = x['speaker'] + ' speaks own words'
    shots.append(s)
plan = {'voiceover': '../audio/Genesis_21_voiceover_dialogue.wav', 'music': '../music/Genesis_21_music.wav', 'music_gain_db': -9.8, 'ambient_gain': 0.22, 'dissolve': 0.5, 'outro': 3.0,
        'output': '../final/Genesis_21_clean.mp4', 'badge': {'image': '../../_tools/references/Radiant Golden Portal Emblem.png', 'cx': 1740, 'cy': 898, 'size': 150}, 'shots': shots}
json.dump(plan, open('genesis21_full.json', 'w'), indent=1)
R2 = 'https://pub-2993fb3bf56d45ffb3d678320781fe03.r2.dev/generated_shots/genesis-chapter-21-verse-'
IMG = {1: '1-scene-1-shot-1-m4zmuw', 3: '3-scene-1-shot-2-uhc8tu', 5: '5-scene-1-shot-3-79lf03', 6: '6-scene-1-shot-4-lvah0s', 8: '8-scene-1-shot-5-bwllaf',
       9: '9-scene-2-shot-1-27m6qd', 10: '10-scene-2-shot-2-nrcg5b', 11: '11-scene-2-shot-3-bs9sed', 12: '12-scene-2-shot-4-ljru2b', 14: '14-scene-3-shot-1-uqbura',
       15: '15-scene-3-shot-2-txzj7q', 16: '16-scene-3-shot-3-nbm9fq', 17: '17-scene-4-shot-1-gvl49h', 19: '19-scene-4-shot-2-lcf2x8', 20: '20-scene-4-shot-3-qdaxxs',
       22: '22-scene-5-shot-1-pcxxxi', 24: '24-scene-5-shot-2-wrnbmv', 27: '27-scene-5-shot-3-utsh0s', 29: '29-scene-5-shot-4-hpcxk4', 31: '31-scene-5-shot-5-qs2ppm',
       33: '33-scene-6-shot-1-fbu4ue'}
K = " Keep every face, beard and garment exactly as in the start image. God is never shown: no figure, no face, no light-being; the angel is never shown, only soft light. Everyone stays modestly and fully clothed. No violence. No text on screen."
N = K + " No narration, no voiceover, no dialogue, no music. Natural ambient sound only."
S = lambda who, voice, q: K + f" {who} speaks with clear lip movement, in {voice}: \"{q}\" After the last word {('she' if who in ('Sarah', 'Hagar') else 'he')} falls silent and holds still. Only {who} speaks; no other voices, no narration, no music. Natural ambient sound underneath."
P = "Static camera, very slight slow push in. "
SA = "the older woman Sarah with grey-streaked hair in the cream striped hooded shawl"; HA = "Hagar, the woman in the rust-red dress and sand-coloured headscarf"
AM = "King Abimelech with the gold circlet, dark beard, dark blue robe and red sash"; AB = "the white-bearded elder Abraham in the striped brown hooded robe"
ACT = {'v01': "Very slow push in. Inside the tent Sarah cradles her newborn son Isaac while Abraham leans close with tender joy.",
 'v03': "Slow push in. Abraham lifts the swaddled baby Isaac up in the tent, beaming with wonder; Sarah smiles beside him.",
 'v05': "Very slow push in on the aged Abraham's joyful face as he holds the sleeping infant against his cheek.",
 'v06': "Slow push in. Sarah, holding baby Isaac, laughs with the women of the camp around her.",
 'v06b': P + f"{SA}, holding baby Isaac close, laughs and speaks joyfully to the women around her.",
 'v07': "Slow push in. Sarah hugs baby Isaac and looks around at the smiling women.",
 'v07b': P + f"{SA}, holding baby Isaac, speaks with joyful wonder to the women.",
 'v08': "Slow pan across the great feast in the camp: tables of fruit and bread, guests laughing, Sarah holding the weaned child Isaac, Abraham raising his hands.",
 'v09': "Slow push in. At the feast the youth Ishmael smirks and points at little Isaac; Sarah notices, her face hardening; Hagar stands behind.",
 'v10': "Slow forward push. In the lamplit tent at sunset Sarah turns to Abraham, one hand raised toward the camp outside.",
 'v10b': P + f"{SA}, in the lamplit tent at sunset, speaks firmly to Abraham, her hand gesturing toward the camp.",
 'v11': "Very slow push in. Abraham leans on his staff, grieved, eyes lowered, in the dusk.",
 'v12': "Very slow push in. Night: Abraham stands alone outside the tents under a vast starry sky, listening, face lifted.",
 'v13': "Very slow pull back. Night: Abraham stands still under the stars, at peace, the desert silent around him.",
 'v14': "Slow push in. Early morning: Abraham places bread and a skin of water on Hagar's shoulder; Ishmael stands beside her; Abraham's face is sorrowful.",
 'v15': "Slow push in. In the desert Hagar lays the exhausted youth Ishmael in the shade of a shrub; the water skin lies empty.",
 'v16': "Slow push in. Hagar sits alone on a rock a distance away in the wilderness, hands clasped at her mouth.",
 'v16b': P + f"{HA}, sitting alone in the wilderness, hands clasped, speaks through tears.",
 'v16c': "Very slow push in. Hagar bows her head and weeps in the empty wilderness.",
 'v17': "Slow push in. Soft golden light breaks through the clouds over the wilderness; Hagar rises and lifts her face toward the sky; Ishmael lies nearby.",
 'v18': "Slow push in. In the soft light Hagar takes Ishmael's hand and helps him up.",
 'v19': "Slow push in. At a stone well Hagar holds the water skin to Ishmael's lips; he drinks deeply.",
 'v20': "Slow pan. Grown Ishmael draws his bow in the wilderness; behind him Hagar welcomes a young Egyptian woman by the tents.",
 'v22': "Slow forward push. By the well Abimelech and his armoured captain Phichol come to Abraham, Abimelech opening his hands.",
 'v22b': P + f"{AM}, by the well with his captain Phichol, opens his hands and speaks to Abraham.",
 'v23': P + f"{AM} speaks earnestly to Abraham by the well, one hand raised as if asking an oath.",
 'v23b': P + f"{AM} continues speaking calmly to Abraham, hand open toward the land around them.",
 'v24': "Slow push in. Abraham, staff in hand, turns to Abimelech by the well.",
 'v24b': P + f"{AB}, staff in hand, answers Abimelech by the well.",
 'v25': "Slow push in. Abraham points to the well and speaks to Abimelech, troubled; Abimelech lifts his hands.",
 'v26': "Slow push in. Abimelech turns to Abraham with open, apologetic hands.",
 'v26b': P + f"{AM} opens his hands apologetically and speaks to Abraham.",
 'v27': "Slow pan. Abraham sets seven ewe lambs apart by the well; servants lead sheep and oxen to Abimelech; the two men stand together.",
 'v29': "Slow push in. Abimelech looks at the seven ewe lambs and turns to Abraham, curious.",
 'v29b': P + f"{AM} gestures toward the seven ewe lambs and asks Abraham.",
 'v30': "Slow push in. Abraham lays his hand on the lambs and looks at Abimelech.",
 'v30b': P + f"{AB}, hand on the lambs beside the well, answers Abimelech.",
 'v31': "Slow pull back. Abimelech and Phichol mount and ride away from Beer-sheba with their men; dust rises.",
 'v33': "Very slow push in. Sunset: Abraham kneels beside a young tamarisk tree he has planted, arms raised in worship; the camp behind."}
q = []
for x in win:
    k = x['shot']
    pr = ACT[k] + (S(SPK[k][0], SPK[k][1], SPK[k][2]) if k in SPK else N)
    q.append(dict(key=k, len=x['clip_len'], img=R2 + IMG[x['pic']] + '.jpg', name=f'Genesis_21_{k}.mp4', prompt=pr))
json.dump(q, open('vids21_queue.json', 'w'), ensure_ascii=False)
for x in win: print(f"{x['shot']:5} {x['start']:7.2f}-{x['end']:7.2f} {x['duration']:5.2f} clip {x['clip_len']}{'  '+x['speaker'] if x.get('speech') else ''}")
print('narration', round(len(nv) / sr, 2), 'clips', len(q), 'clip seconds', sum(i['len'] for i in q))
