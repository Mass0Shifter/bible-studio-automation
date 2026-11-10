# Genesis 23: word times without speech-to-text. Vids caption track (from 33.9 s; scene 1 has none) gives chunk times;
# inside each chunk (and for scene 1) words are spread over the SPEECH time (pauses from silencedetect removed) by
# letter count, and a word ending in punctuation is snapped to a real pause if one is within 0.7 s.
# Output: g23_stt.json in ElevenLabs shape -> stt_align.py.
import json, re, subprocess
WAV = '../audio/Genesis_23_voiceover.wav'
def pauses(db=-35, d=0.12):
    r = subprocess.run(['ffmpeg', '-i', WAV, '-af', f'silencedetect=noise={db}dB:d={d}', '-f', 'null', '-'], capture_output=True, text=True).stderr
    s = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', r)]; e = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', r)]
    return list(zip(s, e + [9e9] * (len(s) - len(e))))
P = pauses()
def ts(t): h, m, s = t.split(':'); return int(h) * 3600 + int(m) * 60 + float(s.replace(',', '.'))
cap = []
for b in open('g23_captions.srt', encoding='utf-8').read().strip().split('\n\n'):
    L = b.strip().split('\n'); a, z = L[1].split(' --> '); cap.append((ts(a), ts(z), ' '.join(L[2:]).split()))
V = json.load(open('verses.json'))
first_cap_words = cap[0][2]
# scene-1 words = KJV text before the first captioned word ("Hear us" = verse 6)
pre = [w for v, t in V if v < 6 for w in t.split()]
END = float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',WAV],capture_output=True,text=True).stdout)
post = [w for v, t in V if v >= 16 for w in t.split()]   # last scene (v16-20) also has no captions
chunks = [(0.0, cap[0][0], pre)] + cap + [(cap[-1][1], END, post)]
def speech_between(a, b):   # list of (s,e) speech spans in [a,b]
    out = []; t = a
    for ps, pe in P:
        if pe <= a or ps >= b: continue
        if ps > t: out.append((t, min(ps, b)))
        t = max(t, pe)
    if t < b: out.append((t, b))
    return [x for x in out if x[1] - x[0] > 0.02]
words = []
for a, b, ws in chunks:
    sp = speech_between(a, b)
    if not sp: sp = [(a, b)]
    tot = sum(e - s for s, e in sp); wt = [len(re.sub(r'[^A-Za-z]', '', w)) + 1 for w in ws]; W = sum(wt)
    def at(f):   # fraction of speech -> absolute time
        x = f * tot
        for s, e in sp:
            if x <= e - s + 1e-9: return s + x
            x -= e - s
        return sp[-1][1]
    c = 0; tw = []
    for w, k in zip(ws, wt):
        tw.append([w, at(c / W), at((c + k) / W)]); c += k
    # snap punctuation to nearby pauses
    for i, (w, s, e) in enumerate(tw):
        if re.search(r'[,.;:?!"]$', w) and i + 1 < len(tw):
            near = [(ps, pe) for ps, pe in P if a < ps < b and abs(ps - e) < 0.7]
            if near:
                ps, pe = min(near, key=lambda p: abs(p[0] - e)); tw[i][2] = ps; tw[i + 1][1] = pe
    for w, s, e in tw: words.append(dict(text=w, start_time=round(s, 3), end_time=round(max(e, s + 0.05), 3)))
json.dump({'segments': [{'words': words}]}, open('g23_stt.json', 'w'))
print(len(words), 'words;', len(P), 'pauses; last', words[-1])
