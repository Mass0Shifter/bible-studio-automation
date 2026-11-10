"""Extend a music track to a target length by repeating a middle section with a crossfade at matching spots
(the way the user's films have been done by hand: e.g. Esther PI 0-100 s + 40 s-end, 5 s crossfade).

Usage: python3 extend_music.py <in.wav> <out.wav> <target_seconds> [--xfade 5]
Finds a jump point A (later) and a re-entry point B (earlier) whose loudness (1 s RMS) and the 6 s around them
match best, so the join is smooth; repeats until the length >= target. The track's own ending is kept.
"""
import subprocess, sys
import numpy as np

def rms_profile(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', '8000', '-f', 's16le', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(float) / 32768
    n = len(x) // 8000
    return np.array([20 * np.log10(np.sqrt(np.mean(x[i * 8000:(i + 1) * 8000] ** 2)) + 1e-9) for i in range(n)])

def best_jump(r, need, L, xf):
    """A, B (seconds) with A - B ≈ need + xf, A in the middle-late part, matching loudness around both."""
    best = None
    for A in range(int(L * 0.35), int(L * 0.85)):
        B = int(round(A - (need + xf)))
        if B < max(8, L * 0.12): continue
        w = 3
        if A + w >= len(r) or B - w < 0: continue
        d = np.mean(np.abs(r[A - w:A + w] - r[B - w:B + w]))
        quiet = (r[A] + r[B]) / 2           # prefer quieter joins a little
        score = d + 0.05 * (quiet + 40)
        if best is None or score < best[0]: best = (score, A, B)
    return best

def main(a):
    src, out, target = a[0], a[1], float(a[2])
    xf = float(a[a.index('--xfade') + 1]) if '--xfade' in a else 5.0
    L = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', src]))
    if L >= target:
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-c:a', 'pcm_s16le', out], check=True); print('long enough', L); return
    r = rms_profile(src)
    # one repeat covers at most ~60 % of the track; use as many repeats as needed
    reps = int(np.ceil((target - L) / (L * 0.55)))
    need = (target - L) / reps + 0.5
    found = best_jump(r, need, L, xf)
    if not found: raise SystemExit('no join found')
    _, A, B = found
    # build: [0:A] + reps × [B:A] + [B:end], each join an acrossfade of xf seconds
    parts = [(0, A)] + [(B, A)] * (reps - 1) + [(B, None)]
    f = []
    for i, (s, e) in enumerate(parts):
        f.append(f"[0]atrim={s}" + (f":{e}" if e is not None else '') + f",asetpts=N/SR/TB[p{i}]")
    cur = '[p0]'
    for i in range(1, len(parts)):
        f.append(f"{cur}[p{i}]acrossfade=d={xf}:c1=tri:c2=tri[x{i}]"); cur = f'[x{i}]'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-filter_complex', ';'.join(f), '-map', cur, '-c:a', 'pcm_s16le', out], check=True)
    D = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out]))
    print(f"{out}: {D:.1f}s (from {L:.1f}s; join at {A}s -> back to {B}s, {reps} repeat(s), {xf}s crossfade)")

if __name__ == '__main__':
    main(sys.argv[1:])
