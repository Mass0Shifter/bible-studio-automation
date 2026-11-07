#!/usr/bin/env python3
"""Check a rendered clean film against its plan: frame count, lip-sync of every speech shot (clip frame at 3 s vs film),
and speech loudness in the film vs the narration just before it.   Usage: film_check.py plans/finish.json"""
import json, os, subprocess, sys
import numpy as np
a = sys.argv[1]; base = os.path.dirname(os.path.abspath(a)); p = lambda x: os.path.normpath(os.path.join(base, x))
F = json.load(open(a)); P = json.load(open(p(F["edit_plan"]))); film = p(P["output"]); sh = P["shots"]; t0 = sh[0]["start"]
def fr(f, t):
    o = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", f, "-frames:v", "1", "-s", "160x90", "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout
    return np.frombuffer(o, np.uint8).astype(float)
def L(t, d):
    o = subprocess.run(["ffmpeg", "-nostats", "-ss", f"{t:.3f}", "-t", f"{d:.3f}", "-i", film, "-vn", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    l = [x for x in o.splitlines() if x.strip().startswith("I:")]; return float(l[-1].split()[1]) if l else float("nan")
n = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", film], capture_output=True, text=True).stdout.strip()
print(f"{os.path.basename(film)}: {n} frames = {int(n)/24:.2f}s")
BAD = 0
for i, s in enumerate(sh):
    if "clip_gain" not in s: continue
    st = s["start"] - t0; c = p(s["clip"]); w = s["end"] - s["start"]; offs = []
    for ct in (1.5, w / 2, w - 0.6):                     # early, middle and late in the shot: a slowed clip drifts
        a3 = fr(c, ct)
        if not a3.size: continue
        offs.append(min((np.abs(a3 - fr(film, st + ct + d)).mean(), d) for d in (-0.125, -0.083, -0.042, 0, 0.042, 0.083, 0.125))[1])
    ls = L(st + 0.6, max(w - 1.0, 1.0)); ln = L(max(st - 6.5, 0), 6.0)
    bad = any(abs(o) > 0.05 for o in offs)               # lip-sync is the hard rule here (level is checked by speech_check.py)
    warn = abs(ls - ln) > 2.5                             # the 6 s before may hold a music swell or the divine voice: a hint only
    BAD += bad
    print(f"{'FAIL' if bad else ('WARN' if warn else 'ok  ')} shot {i+1:2d} {os.path.basename(c)}: sync offsets {', '.join(f'{o:+.3f}' for o in offs)}s | film loudness speech {ls:.1f} vs narration before {ln:.1f} LUFS")
print(f"film check: {BAD} FAIL"); sys.exit(1 if BAD else 0)
