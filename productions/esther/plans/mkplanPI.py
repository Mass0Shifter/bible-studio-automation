# Esther Prophetic Implication: edit plan (fit_edit.py) + finishing plan (finish.py).
# Shots 1-41 = Vids clips ../video/Esther_PI_vNN.mp4 on the narration windows (windows.json, from ElevenLabs STT);
# shot 42 = channel outro CAN_YOU_BEHOLD_HIM_OUTTRO.mp4 (10 s, played whole) under the "subscribe" line.
# Subtitles: one sentence per shot + its KJV reference in brackets (references are not spoken) -> plain_subs.
import json, os
sb = json.load(open('../Esther_PI_storyboard.json')); win = json.load(open('windows.json'))
OUT = '../../../_tools/references/CAN_YOU_BEHOLD_HIM_OUTTRO.mp4'
shots = []
for n, (s, w) in enumerate(zip(sb, win), 1):
    if n == 42:
        shots.append(dict(verse=42, clip=OUT, start=w['start'], end=round(w['start'] + 10.0, 3), method='trim', badge=False, note='channel outro'))
    else:
        shots.append(dict(verse=n, clip=f'../video/Esther_PI_v{n:02d}.mp4', start=w['start'], end=w['end'], method='auto'))
plan = {'voiceover': '../audio/Esther_PI_voiceover.wav', 'music': '../music/Esther_PI_music.wav', 'music_gain_db': -9.8, 'ambient_gain': 0.22,
        'dissolve': 0.5, 'end_tail': 0.4, 'output': '../final/Esther_PI_clean.mp4',
        'badge': {'image': '../../../_tools/references/Radiant Golden Portal Emblem.png', 'cx': 1740, 'cy': 898, 'size': 150}, 'shots': shots}
json.dump(plan, open('esther_pi_full.json', 'w'), indent=1)
subs = []
for n, s in enumerate(sb, 1):
    t = s['narration'].strip()
    if s.get('ref'): t += f" ({s['ref']})"
    subs.append([n, t])
json.dump(subs, open('subs.json', 'w'), ensure_ascii=False, indent=0)
fin = {'film': '../final/Esther_PI_clean.mp4', 'edit_plan': 'esther_pi_full.json', 'verses': 'subs.json', 'plain_subs': True,
       'reference': 'The Book of Esther', 'intro_video': '../video/Esther_PI_INTRO.mp4', 'intro_voice': '../audio/Esther_PI_intro_voice.wav',
       'intro_card': '../images/Esther_PI_INTRO.png', 'intro_restore': [[0.70, 1.0]], 'intro_min': 6.0, 'intro_max': 8.0, 'intro_loop': False,
       'bar_opacity': 0.8, 'references': '../../../_tools/references', 'fonts': '../../../_tools/fonts', 'output': '../final/Esther_PI_final.mp4',
       'badge': plan['badge']}
json.dump(fin, open('finish.json', 'w'), indent=1)
miss = [x['clip'] for x in shots if not os.path.exists(x['clip'])]
print(len(shots), 'shots; film ≈', round(shots[-1]['end'] - shots[0]['start'] + 0.4, 1), 's; missing clips:', len(miss))
