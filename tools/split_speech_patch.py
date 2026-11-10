"""Patch a chapter's mkplanNN.py so the listed character-speech shots are split into two clips each
(<key> = first half, <key>2 = second half), because Google Flow clips are at most 10 s (user choice 10 Nov 2026).
Usage: python3 split_speech_patch.py mkplan23.py v08b v11 v13b v15
Idempotent: a file that already has the SPLIT block is left alone.
"""
import sys

BLOCK1 = '''
# ---- split long speech shots into two Flow clips (max 10 s each) — split_speech_patch.py, 10 Nov 2026
SPLIT_KEYS = {keys}
SPLIT = {{}}
for _k in SPLIT_KEYS:
    _who, _vo, _txt = SPK[_k]; _w = _txt.split(); _n = len(_w); _mid = _n / 2
    _c = [i for i in range(3, _n - 2) if re.search(r"[,;:]$", _w[i - 1])]
    _cut = min(_c, key=lambda i: abs(i - _mid)) if _c and min(abs(i - _mid) for i in _c) <= _n * 0.3 else (_n + 1) // 2
    SPK[_k] = (_who, _vo, ' '.join(_w[:_cut])); SPK[_k + '_2'] = (_who, _vo, ' '.join(_w[_cut:])); SPLIT[_k] = _k + '_2'
SPLEN = {{k: max(4, min(10 if (k in SPLIT or k in SPLIT.values()) else 15, math.ceil(wl(v[2]) / 2.6 + 1.6))) for k, v in SPK.items()}}
'''
BLOCK2 = '''_seq = []
for _e in SEQ:
    _seq.append(_e)
    if _e[0] in SPLIT: _seq.append((SPLIT[_e[0]],) + tuple(_e[1:]))
SEQ = _seq
'''
BLOCK3 = '''for _k, _k2 in SPLIT.items():
    ACT[_k2] = ACT[_k].replace('speaks', 'continues speaking')
'''

def main(path, keys):
    s = open(path, encoding='utf-8').read()
    if 'SPLIT_KEYS' in s:
        print('already patched'); return
    L = s.split('\n')
    i = next(n for n, l in enumerate(L) if l.startswith('SPLEN = {k:'))
    L.insert(i + 1, BLOCK1.format(keys=repr(keys)))
    j = next(n for n, l in enumerate(L) if l.startswith('out = []'))
    L.insert(j, BLOCK2)
    k = next(n for n, l in enumerate(L) if l.startswith('q = []'))
    L.insert(k, BLOCK3)
    s = '\n'.join(L)
    if 'import' in s and ' re' not in s.split('\n', 10)[4] and 'import json, wave, math, re' not in s:
        s = s.replace('import json, wave, math,', 'import json, wave, math, re,', 1)
    open(path, 'w', encoding='utf-8').write(s)
    print('patched', path, keys)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:])
