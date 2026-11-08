# Align KJV verses to ElevenLabs Speech-to-Text word timings.
# usage: python3 stt_align.py <stt.json> <verses.json> <narration.wav> <out_dir>   -> out_dir/windows.json + out_dir/words.json
# Then find(words, verse, first_words, last_words) gives a quote's start/end (import this file).
import json, re, difflib, subprocess, sys
norm = lambda t: re.sub(r'[^a-z]', '', t.lower())
def align(stt, verses, wav):
    V = json.load(open(verses))
    W = [w for s in json.load(open(stt))['segments'] for w in s['words'] if w['text'].strip()]
    sw = [norm(w['text']) for w in W]
    kw = [(v, i, x) for v, t in V for i, x in enumerate(t.split()) if norm(x)]
    sm = difflib.SequenceMatcher(None, [norm(x[2]) for x in kw], sw, autojunk=False)
    tm = [None] * len(kw)
    for a, b, n in sm.get_matching_blocks():
        for j in range(n): tm[a + j] = (W[b + j]['start_time'], W[b + j]['end_time'])
    for i in range(len(tm)):
        if tm[i] is None:
            p = next((tm[j] for j in range(i - 1, -1, -1) if tm[j]), (0, 0)); q = next((tm[j] for j in range(i + 1, len(tm)) if tm[j]), p)
            tm[i] = (p[1], max(p[1], q[0]))
    words = [dict(verse=v, i=i, w=x, s=round(tm[k][0], 3), e=round(tm[k][1], 3)) for k, (v, i, x) in enumerate(kw)]
    END = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', wav], capture_output=True, text=True).stdout)
    first, last = {}, {}
    for x in words: first.setdefault(x['verse'], x['s']); last[x['verse']] = x['e']
    vs = sorted(first); out = []
    for n, v in enumerate(vs):
        st = 0.0 if n == 0 else round((last[vs[n - 1]] + first[v]) / 2, 2)
        en = END if n == len(vs) - 1 else round((last[v] + first[vs[n + 1]]) / 2, 2)
        out.append(dict(verse=v, start=st, end=en))
    unmatched = sum(1 for t in tm if t is None)
    return words, out, END
def find(words, v, a, b):
    ws = [w for w in words if w['verse'] == v]; t = [norm(w['w']) for w in ws]
    A = [norm(x) for x in a]; B = [norm(x) for x in b]
    ia = next(i for i in range(len(t)) if t[i:i + len(A)] == A)
    ib = next(i for i in range(ia, len(t)) if t[i:i + len(B)] == B) + len(B) - 1
    return dict(start=ws[ia]['s'], end=ws[ib]['e'], prev_end=ws[ia - 1]['e'] if ia else None, next_start=ws[ib + 1]['s'] if ib + 1 < len(ws) else None)
if __name__ == '__main__':
    stt, verses, wav, od = sys.argv[1:5]
    words, out, END = align(stt, verses, wav)
    json.dump(words, open(od + '/words.json', 'w')); json.dump(out, open(od + '/windows.json', 'w'), indent=0)
    V = dict(json.load(open(verses)))
    for o in out: print(o['verse'], o['start'], o['end'], round(o['end'] - o['start'], 1), round(len(V[o['verse']]) / max(0.1, o['end'] - o['start']), 1))
