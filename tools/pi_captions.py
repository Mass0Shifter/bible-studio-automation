"""Prophetic Implication captions (user style, 10 Nov 2026): no lower-third bar, bold "flame" subtitles of at most
5 words at a time timed to the STT words, plus the script's POINTS shown on screen:
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

def flame(t0, t1):
    """flicker of the glow layer: alternate blur/colour every 0.35 s"""
    out, k, d = '', 0, 350
    n = int((t1 - t0) * 1000 // d)
    for i in range(min(n, 40)):
        a, b = i * d, (i + 1) * d
        if i % 2 == 0: out += f"\\t({a},{b},\\blur14\\3c&H0030E0&)"
        else: out += f"\\t({a},{b},\\blur9\\3c&H0060FF&)"
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
            ev.append((4, st, e, 'PointGlow', r"{\fad(400,500)" + flame(st, e) + "}" + esc(title)))
            ev.append((6, st, e, 'Point', r"{\fad(400,500)}" + esc(title)))
            ev.append((6, st + 0.4, e, 'PointTag', r"{\fad(400,500)}" + esc(tag)))
            s['_skip_all'] = True
            continue
        if s['scene'] == 6 and (i == 0 or sb[i - 1]['scene'] != 6):     # summary section
            mains.append((st, 'IN SUMMARY'))
            e = st + 3.2
            ev.append((4, st, e, 'PointGlow', r"{\fad(400,500)" + flame(st, e) + "}IN SUMMARY"))
            ev.append((6, st, e, 'Point', r"{\fad(400,500)}IN SUMMARY"))
        m2 = re.match(r"^((?:The |A |An )?[A-Z][\w'’ ]{2,40}?)\.\s+\S", n)
        if m2 and len(m2.group(1).split()) <= 5 and s['scene'] in (2, 3, 4, 5):
            title = m2.group(1)
            e = st + 3.0
            ev.append((4, st, e, 'SubGlow', r"{\fad(300,400)" + flame(st, e) + "}" + esc(title.upper())))
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
        for w in ws:
            chunk.append(w)
            end_p = re.search(r"[.,;:?!—]['\"”’]?$", w['w'])
            if len(chunk) == 5 or (end_p and len(chunk) >= 2) or (end_p and re.search(r"[.?!]['\"”’]?$", w['w'])):
                chunks.append(chunk); chunk = []
        if chunk:
            if chunks and len(chunk) == 1 and len(chunks[-1]) < 5: chunks[-1] += chunk
            else: chunks.append(chunk)
        for j, c in enumerate(chunks):
            a0 = c[0]['s'] - 0.05
            nxt = chunks[j + 1][0]['s'] - 0.05 if j + 1 < len(chunks) else None
            b0 = nxt if nxt is not None and nxt - c[-1]['e'] < 0.8 else c[-1]['e'] + 0.35
            txt = esc(' '.join(x['w'] for x in c))
            ev.append((1, a0, b0, 'SubFlameGlow', r"{\fad(120,80)" + flame(a0, b0) + "}" + txt))
            ev.append((2, a0, b0, 'SubFlame', r"{\fad(120,80)}" + txt))
    hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: SubFlame,{FONT},92,&H0080EAFF,&H000000FF,&H00106CFF,&H00000000,-1,0,0,0,100,100,1,0,1,2.5,0,2,120,120,78,1
Style: SubFlameGlow,{FONT},92,&HFF000000,&H000000FF,&H0000A0FF,&H00000000,-1,0,0,0,100,100,1,0,1,9,0,2,120,120,78,1
Style: Point,{FONT},128,&H0070E6FF,&H000000FF,&H00106CFF,&H00000000,-1,0,0,0,100,100,6,0,1,3,0,5,100,100,0,1
Style: PointGlow,{FONT},128,&HFF000000,&H000000FF,&H0000A0FF,&H00000000,-1,0,0,0,100,100,6,0,1,14,0,5,100,100,0,1
Style: PointNum,{FONT},46,&H00B8E4F5,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,14,0,1,1.5,2,8,100,100,330,1
Style: PointTag,{FONT},58,&H00F0F6FF,&H000000FF,&H00000000,&H64000000,0,-1,0,0,100,100,1,0,1,2,2,2,100,100,330,1
Style: Sub,{FONT},74,&H0070E6FF,&H000000FF,&H00106CFF,&H00000000,-1,0,0,0,100,100,5,0,1,2.5,0,8,100,100,70,1
Style: SubGlow,{FONT},74,&HFF000000,&H000000FF,&H0000A0FF,&H00000000,-1,0,0,0,100,100,5,0,1,11,0,8,100,100,70,1
Style: Label,{FONT},40,&H0078D8F2,&H000000FF,&H00000000,&H78000000,-1,0,0,0,100,100,4,0,1,1.5,1.5,7,60,60,46,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [f"Dialogue: {L},{ts(s0 + off)},{ts(e0 + off)},{st},,0,0,0,,{t}" for L, s0, e0, st, t in sorted(ev, key=lambda x: (x[1], x[0]))]
    open(out, 'w', encoding='utf-8').write(hdr + "\n".join(lines) + "\n")
    print(f"{out}: {len(lines)} events, {len(mains)} main points, {sum(1 for e in ev if e[3]=='Sub')} sub-points, "
          f"{sum(1 for e in ev if e[3]=='SubFlame')} subtitle chunks")

if __name__ == '__main__':
    main(sys.argv[1:])
