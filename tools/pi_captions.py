"""Prophetic Implication captions (user style, 10 Nov 2026): no lower-third bar, bold "flame" subtitles of at most
2 lines (<= 5 words per line) at a time timed to the STT words, the word being spoken
highlighted with a hotter flame (karaoke), plus the script's POINTS shown on screen:
  - main points ("One. The Hidden Hand — the God who is never named.") -> big centred title card (~4 s), then a small
    top-left label of the current point for the rest of the section;
  - sub-points (a shot whose narration starts with a short title sentence, "The Gallows.") -> medium title near the top (~3 s).
Writes an ASS subtitle file (burn with ffmpeg ass/subtitles filter, fontsdir = _tools/fonts).

Usage: python3 pi_captions.py <storyboard.json> <windows.json> <words.json> <out.ass> [--offset SECONDS] [--skip-scene 7]
  offset = seconds added to every time (e.g. the intro length when burning onto the final film; 0 for the clean film).
"""
import json, re, sys

ORD = {'One': 'ONE', 'Two': 'TWO', 'Three': 'THREE', 'Four': 'FOUR', 'Five': 'FIVE', 'Six': 'SIX', 'Seven': 'SEVEN'}
FONT = 'Cormorant Garamond'

def ts(t):
    t = max(t, 0); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def esc(t):
    return t.replace('{', '(').replace('}', ')').replace('\n', ' ')

def flame(t0, t1, gold=False):
    """flicker of the glow layer: alternate blur/colour every 0.35 s"""
    out, k, d = '', 0, 350
    n = int((t1 - t0) * 1000 // d)
    for i in range(min(n, 40)):
        a, b = i * d, (i + 1) * d
        c1, c2 = ('&H0040D8FF&', '&H0000A8F5&') if gold else ('&H0030E0&', '&H0060FF&')
        bl = (20, 13) if gold else (14, 9)
        if i % 2 == 0: out += f"\\t({a},{b},\\blur{bl[0]}\\3c{c1})"
        else: out += f"\\t({a},{b},\\blur{bl[1]}\\3c{c2})"
    return out

def main(a):
    sb = json.load(open(a[0], encoding='utf-8')); win = json.load(open(a[1])); words = json.load(open(a[2], encoding='utf-8'))
    out = a[3]; off = 0.0; skip = {7}
    if '--offset' in a: off = float(a[a.index('--offset') + 1])
    if '--skip-scene' in a: skip = {int(x) for x in a[a.index('--skip-scene') + 1].split(',')}
    film_end = win[-1]['end']
    ev = []          # (layer, start, end, style, text)
    # ---- points
    mains = []       # (start, label)
    for i, s in enumerate(sb):
        n = s['narration'].strip(); st = win[i]['start']
        m = re.match(r"^(One|Two|Three|Four|Five|Six|Seven)\.\s+(.+?)\s+—\s+(.+?)\.?$", n)
        if m:
            num, title, tag = ORD[m.group(1)], m.group(2).upper(), m.group(3)
            mains.append((st, f"{num} · {title}"))
            e = min(st + 4.2, win[i + 1]['start'] - 0.1 if i + 1 < len(win) else st + 4.2)
            ev.append((5, st, e, 'PointNum', r"{\fad(400,500)}" + f"POINT {num}"))
            ev.append((4, st, e, 'PointGlow', r"{\fad(400,500)\3a&H40&" + flame(st, e, gold=True) + "}" + esc(title)))
            ev.append((6, st, e, 'Point', r"{\fad(400,500)}" + esc(title)))
            ev.append((6, st + 0.4, e, 'PointTag', r"{\fad(400,500)}" + esc(tag)))
            s['_skip_all'] = True
            continue
        if s['scene'] == 6 and (i == 0 or sb[i - 1]['scene'] != 6):     # summary section
            mains.append((st, 'IN SUMMARY'))
            e = st + 3.2
            ev.append((4, st, e, 'PointGlow', r"{\fad(400,500)\3a&H40&" + flame(st, e, gold=True) + "}IN SUMMARY"))
            ev.append((6, st, e, 'Point', r"{\fad(400,500)}IN SUMMARY"))
        m2 = re.match(r"^((?:The |A |An )?[A-Z][\w'’ ]{2,40}?)\.\s+\S", n)
        if m2 and len(m2.group(1).split()) <= 5 and s['scene'] in (2, 3, 4, 5):
            title = m2.group(1)
            e = st + 3.0
            pass   # sub-point titles: no glow (user 10 Nov)
            ev.append((6, st, e, 'Sub', r"{\fad(300,400)}" + esc(title.upper())))
            s['_skip_n'] = len(title.split())
    # current-point label, top-left, after each main card until the next main point
    for k, (st, lab) in enumerate(mains):
        e = mains[k + 1][0] if k + 1 < len(mains) else min(film_end, next((w['start'] for w, s in zip(win, sb) if s['scene'] in skip), film_end))
        ev.append((3, st + 4.0, e - 0.2, 'Label', r"{\fad(500,300)}" + esc(lab)))
    # ---- subtitles: <= 5 words, break at punctuation, timed by the STT words
    by = {}
    for w in words: by.setdefault(w['verse'], []).append(w)
    for v, ws in by.items():
        s = sb[v - 1]
        if s['scene'] in skip or s.get('_skip_all'): continue
        ws = sorted(ws, key=lambda x: x['i'])[s.get('_skip_n', 0):]
        chunk = []
        chunks = []
        # chunks of up to 2 lines (<= 5 words per line, <= 10 words), ending at sentence ends / long pauses
        chunks = []
        for w in ws:
            if chunk and (w['s'] - chunk[-1]['e'] > 0.7): chunks.append(chunk); chunk = []
            chunk.append(w)
            if len(chunk) == 10 or re.search(r"[.?!]['\"”’]?$", w['w']) or (len(chunk) >= 6 and re.search(r"[,;:—]['\"”’]?$", w['w'])):
                chunks.append(chunk); chunk = []
        if chunk:
            if chunks and len(chunk) <= 2 and len(chunks[-1]) + len(chunk) <= 10: chunks[-1] += chunk
            else: chunks.append(chunk)
        for j, c in enumerate(chunks):
            a0 = c[0]['s'] - 0.05
            nxt = chunks[j + 1][0]['s'] - 0.05 if j + 1 < len(chunks) else None
            b0 = nxt if nxt is not None and nxt - c[-1]['e'] < 0.8 else c[-1]['e'] + 0.35
            # line break: 1 line up to 5 words; else split near the middle, preferring a comma
            n = len(c); br = None
            if n > 5:
                mid = n / 2; cands = [k for k in range(2, n - 1) if re.search(r"[,;:—]['\"”’]?$", c[k - 1]['w']) and abs(k - mid) <= 2]
                br = min(cands, key=lambda k: abs(k - mid)) if cands else (n + 1) // 2
                br = max(n - 5, min(br, 5))
            def text(hot=None, glow_only=False):
                out = []
                for k, x in enumerate(c):
                    wd = esc(x['w'])
                    if glow_only: wd = (r"{\alpha&H50&}" + wd + r"{\alpha&HFF&}") if k == hot else wd
                    elif k == hot: wd = r"{\1c&H00F4FFFF&\3c&H00106AB4&\bord3.5\shad0}" + wd + r"{\r}"
                    out.append(wd)
                    if br is not None and k == br - 1: out.append(r"\N")
                return ' '.join(out).replace(r" \N ", r"\N")
            pass   # (no orange glow behind plain words: black outline only — user 10 Nov)
            # karaoke: one event per spoken word; the current word gets a hotter fill and its own big flame glow
            for k, x in enumerate(c):
                ws0 = a0 if k == 0 else x['s']
                ws1 = c[k + 1]['s'] if k + 1 < n else b0
                if ws1 <= ws0: continue
                fin = r"\fad(120,0)" if k == 0 else ""
                fout = r"\fad(0,80)" if k == n - 1 else ""
                ev.append((2, ws0, ws1, 'SubFlame', "{" + fin + fout + "}" + text(hot=k)))
                ev.append((0, ws0, ws1, 'HotGlow', r"{\alpha&HFF&" + fin + fout + flame(ws0, ws1, gold=True) + "}" + text(hot=k, glow_only=True)))
    hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: SubFlame,{FONT},90,&H00FFFFFF,&H000000FF,&H00000000,&H96000000,-1,0,0,0,100,100,1.5,0,1,5,2.5,2,120,120,78,1
Style: SubFlameGlow,{FONT},90,&HFF000000,&H000000FF,&H0000A0FF,&H00000000,-1,0,0,0,100,100,1,0,1,9,0,2,120,120,78,1
Style: HotGlow,{FONT},90,&H0060D8FF,&H000000FF,&H0000B0FF,&H00000000,-1,0,0,0,100,100,1,0,1,13,0,2,120,120,78,1
Style: Point,{FONT},128,&H00F4FFFF,&H000000FF,&H00106AB4,&H00000000,-1,0,0,0,100,100,6,0,1,3,0,5,100,100,0,1
Style: PointGlow,{FONT},128,&HFF000000,&H000000FF,&H0000B0FF,&H00000000,-1,0,0,0,100,100,6,0,1,14,0,5,100,100,0,1
Style: PointNum,{FONT},56,&H00A8F0FF,&H000000FF,&H00102040,&H96000000,-1,0,0,0,100,100,14,0,1,1.2,3,8,100,100,322,1
Style: PointTag,{FONT},68,&H00FFFFFF,&H000000FF,&H00102040,&H96000000,-1,-1,0,0,100,100,1,0,1,1.2,3,2,100,100,322,1
Style: Sub,{FONT},74,&H00F4FFFF,&H000000FF,&H00106AB4,&H96000000,-1,0,0,0,100,100,5,0,1,3,2.5,8,100,100,70,1
Style: SubGlow,{FONT},74,&HFF000000,&H000000FF,&H0000B0FF,&H00000000,-1,0,0,0,100,100,5,0,1,11,0,8,100,100,70,1
Style: Label,{FONT},50,&H0090ECFF,&H000000FF,&H00102040,&H96000000,-1,0,0,0,100,100,4,0,1,1.2,3,7,60,60,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [f"Dialogue: {L},{ts(s0 + off)},{ts(e0 + off)},{st},,0,0,0,,{t}" for L, s0, e0, st, t in sorted(ev, key=lambda x: (x[1], x[0]))]
    open(out, 'w', encoding='utf-8').write(hdr + "\n".join(lines) + "\n")
    print(f"{out}: {len(lines)} events, {len(mains)} main points, {sum(1 for e in ev if e[3]=='Sub')} sub-points, "
          f"{sum(1 for e in ev if e[3]=='SubFlame')} word events")

if __name__ == '__main__':
    main(sys.argv[1:])
