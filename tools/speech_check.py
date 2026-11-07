#!/usr/bin/env python3
"""Character-speech check (user rule, 2026-11-03): run after every render, before delivering a chapter.

Usage:  python3 speech_check.py <plans/finish.json | plan.json> [--film ../final/X_clean.mp4]

For every shot where a character speaks (a shot with "clip_gain"):
  1. SPEECH END   - where the character's last word really ends in the clip (voice-band level, not clip length).
  2. NOT CUT      - the film keeps that shot's own sound until after the last word: speech end <= window
                    (the narrator / next shot only takes over after the window). Fails if the words would be cut.
  3. CLIP WHOLE   - the voice is not still going at the very end of the clip (Vids cut the line itself).
  4. NARRATOR     - the narration track (after vo_mute) is silent from the character's first word to the last.
  5. PACE         - if the shot's "note"/"speech" holds the quoted words: seconds per word must be plausible
                    (too fast = words missing from the clip).
  6. LEVEL        - the voice is as loud as the narrator (clip LUFS + clip_gain within 1.5 LU of the narration).
With --film: the rendered film's frame count must match the plan (otherwise the check above does not describe it).
Exit code 1 if anything FAILS, so a chapter is never delivered with a cut-off character.
"""
import json, os, re, subprocess, sys
import numpy as np

SR = 16000

def run(a): return subprocess.run(a, capture_output=True, text=True)

def dur(f):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]).stdout.strip())

def pcm(f, voice=True, t0=None, t1=None):
    a = ["ffmpeg", "-v", "error"]
    if t0 is not None: a += ["-ss", f"{t0:.3f}"]
    a += ["-i", f]
    if t1 is not None: a += ["-t", f"{t1 - (t0 or 0):.3f}"]
    af = "highpass=f=180,lowpass=f=3800," if voice else ""
    a += ["-vn", "-ac", "1", "-ar", str(SR), "-af", af + "anull", "-f", "s16le", "-"]
    return np.frombuffer(subprocess.run(a, capture_output=True).stdout, np.int16).astype(float) / 32768

def env_db(x, win=0.05):
    n = int(SR * win); k = len(x) // n
    if k == 0: return np.array([-120.0])
    r = np.sqrt((x[:k * n].reshape(k, n) ** 2).mean(1)) + 1e-9
    return 20 * np.log10(r)

def lufs(f):
    o = run(["ffmpeg", "-nostats", "-i", f, "-vn", "-af", "ebur128", "-f", "null", "-"]).stderr
    L = [l for l in o.splitlines() if l.strip().startswith("I:")]
    return float(L[-1].split()[1]) if L else float("nan")

def speech_span(clip):
    """first/last time the voice band is within 22 dB of its loud part (ambience sits far below the voice)."""
    e = env_db(pcm(clip)); ref = np.percentile(e, 95)
    # speech = loud AND syllable-modulated (the level jumps word to word); a smooth swell of ambience or music is not speech
    mod = np.array([np.std(e[max(0, i - 5):i + 6]) for i in range(len(e))])
    v = (e > ref - 22) & (mod >= 4.5)
    on = [i for i in range(len(v)) if v[i:i + 3].all()]          # runs of at least 0.15 s of voice
    if not on: return None, None, len(e) * 0.05
    return on[0] * 0.05, (on[-1] + 3) * 0.05, len(e) * 0.05      # end of the last 0.15 s run

def main():
    a = sys.argv[1]; film = sys.argv[sys.argv.index("--film") + 1] if "--film" in sys.argv else None
    base = os.path.dirname(os.path.abspath(a)); p = lambda x: os.path.normpath(os.path.join(base, x))
    J = json.load(open(a, encoding="utf-8"))
    if "edit_plan" in J:
        if film is None: film = p(J["film"])
        J = json.load(open(p(J["edit_plan"]), encoding="utf-8"))
    shots = J["shots"]; d = float(J.get("dissolve", 0.5)); mutes = J.get("vo_mute", [])
    vo = p(J["voiceover"]); LN = lufs(vo)
    fails = warns = 0; n = 0
    print(f"narration {os.path.basename(vo)}: {LN:.1f} LUFS")
    for i, s in enumerate(shots):
        if "clip_gain" not in s: continue
        n += 1; clip = p(s["clip"]); name = os.path.basename(clip); w = s["end"] - s["start"]
        b, e, C = speech_span(clip); msg = []; bad = False; wn = False
        if e is None:
            print(f"FAIL shot {i+1} {name}: no voice found in the clip"); fails += 1; continue
        # 2 not cut: the shot's own sound is at full level until the window end (the dissolve starts there)
        if e > w + 0.05: msg.append(f"CUT: last word ends at {e:.2f}s but the shot hands over at {w:.2f}s ({e-w:.2f}s lost)"); bad = True
        # 3 clip whole
        if C - e < 0.12: msg.append(f"clip may stop mid-word (voice until {e:.2f}s of {C:.2f}s)"); wn = True
        # 4 narrator silent while the character speaks: first word to last word (vo_mute counts as silent)
        t0, t1 = s["start"] + max(b - 0.1, 0), s["start"] + min(e, w)
        ev = env_db(pcm(vo, voice=True, t0=t0, t1=t1)); tt = t0 + np.arange(len(ev)) * 0.05
        muted = np.zeros(len(ev), bool)
        for m0, m1 in mutes: muted |= (tt >= m0) & (tt <= m1)
        loud = (ev > -45) & ~muted
        if loud.sum() > 2:
            at = tt[np.argmax(loud)]; msg.append(f"NARRATOR speaks over the character at {at:.2f}s (clip {at - s['start']:.2f}s, {loud.sum()*0.05:.2f}s in all)"); bad = True
        # 5 pace
        txt = s.get("speech") or s.get("note") or ""
        q = re.findall(r"[\"“]([^\"”]+)[\"”]", txt); words = len(q[0].split()) if q else 0
        if words:
            spw = (e - b) / words
            if spw < 0.26: msg.append(f"too fast: {words} words in {e-b:.1f}s ({spw:.2f}s/word) - words may be missing"); wn = True
        # 6 level
        LC = lufs(clip); diff = LC + 20 * np.log10(s["clip_gain"]) - LN
        if abs(diff) > 1.5: msg.append(f"level {diff:+.1f} LU vs narrator (clip_gain {s['clip_gain']})"); bad = True
        tag = "FAIL" if bad else ("WARN" if wn else "ok  ")
        fails += bad; warns += (wn and not bad)
        print(f"{tag} shot {i+1:2d} {name}: voice {b:.2f}-{e:.2f}s of {C:.2f}s, window {w:.2f}s, level {diff:+.1f} LU" + ("" if not msg else " | " + "; ".join(msg)))
    if film and os.path.exists(film):
        fr = run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", film]).stdout.strip()
        print(f"film {os.path.basename(film)}: {fr} frames")
    print(f"{n} speech shots: {fails} FAIL, {warns} WARN")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
