#!/usr/bin/env python3
"""Let every character-speech clip play at its full natural length (user rule, 2026-10-28).

Usage:  python3 speech_fit.py plan.json            -> writes plan.speechfit.json (+ new narration / music files)

For each shot with "clip_gain" (a character speaking his own words) the window becomes the clip's real length
minus the dissolve (last shot: minus the outro tail), so the clip is never trimmed into its speech, never slowed
and never scrubbed. The narration (already silent in that window) gets exactly that much more (or less) silence at
the end of the window, and every later shot moves by the same amount, so the film simply gets longer.
The music bed is extended (a middle section repeated with crossfades) if it would end too early.
"""
import json, os, sys, wave, subprocess
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from speech_check import speech_span

def dur(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]).strip())
def rd(f):
    w = wave.open(f); n = w.getnframes(); ch = w.getnchannels(); sr = w.getframerate()
    a = np.frombuffer(w.readframes(n), dtype=np.int16).reshape(-1, ch).copy(); return a, sr, ch
def wr(f, a, sr, ch):
    w = wave.open(f, "wb"); w.setnchannels(ch); w.setsampwidth(2); w.setframerate(sr); w.writeframes(a.astype(np.int16).tobytes()); w.close()

plan_path = sys.argv[1]; base = os.path.dirname(os.path.abspath(plan_path)); p = lambda x: os.path.join(base, x)
P = json.load(open(plan_path, encoding="utf-8")); d = float(P.get("dissolve", 0.5)); tail = float(P.get("outro", 0) or P.get("end_tail", 0.4))
vo, sr, ch = rd(p(P["voiceover"]))
shots = P["shots"]; n = len(shots); shift = 0.0; edits = []   # (time in ORIGINAL narration, +seconds or -seconds)
for i, s in enumerate(shots):
    s["start"] = round(s["start"] + shift, 3); s["end"] = round(s["end"] + shift, 3)
    if "clip_gain" not in s: continue
    C = dur(p(s["clip"])); w = s["end"] - s["start"]
    want = C - (d if i < n - 1 else tail)
    if i == n - 1: want = max(want, w)            # the last shot also carries the calm ending; never shorten it
    # never cut a character off (user rule, 2026-11-03): the window must run past the last spoken word,
    # measured in the clip itself (speech_check.speech_span), not taken from the clip length
    _, last_word, _ = speech_span(p(s["clip"]))
    if last_word is not None and last_word > want + 0.05:      # same tolerance as speech_check.py
        print(f"shot {i+1} {os.path.basename(s['clip'])}: last word ends at {last_word:.2f}s -> window {want:.2f}s -> {last_word + 0.15:.2f}s")
        want = last_word + 0.15
    if last_word is not None and C - last_word < 0.12:
        print(f"WARNING shot {i+1} {os.path.basename(s['clip'])}: the voice runs to the very end of the clip - Vids may have cut the line; listen, regenerate longer if so")
    delta = round(want - w, 3)
    if abs(delta) < 0.02: continue
    at = s["end"] - shift                            # window end in the original narration
    if delta < 0:                                    # only cut silence: check the stretch is really quiet
        a0, a1 = int((at + delta) * sr), int(at * sr); seg = vo[a0:a1].astype(float)
        if seg.size and 20 * np.log10(np.sqrt((seg ** 2).mean()) / 32768 + 1e-9) > -45:
            print(f"shot {i+1}: window end not silent, not shortening"); continue
    edits.append((at, delta)); s["end"] = round(s["end"] + delta, 3); shift += delta
    print(f"shot {i+1} {os.path.basename(s['clip'])}: clip {C:.2f}s, window {w:.2f}s -> {want:.2f}s ({delta:+.2f}s)")
# rebuild the narration
out, last = [], 0
for at, delta in edits:
    k = int(round(at * sr))
    if delta > 0:
        out.append(vo[last:k]); out.append(np.zeros((int(round(delta * sr)), ch), np.int16)); last = k
    else:
        out.append(vo[last:k + int(round(delta * sr))]); last = k
out.append(vo[last:]); nv = np.concatenate(out)
vo_name = os.path.splitext(P["voiceover"])[0] + "_speechfit.wav"; wr(p(vo_name), nv, sr, ch); P["voiceover"] = vo_name
total = shots[-1]["end"] - shots[0]["start"] + tail
print(f"narration {len(vo)/sr:.2f}s -> {len(nv)/sr:.2f}s; film about {total:.2f}s (+{shift:.2f}s)")
# music long enough?
mus = p(P["music"]); M = dur(mus); ms = float(P.get("music_start", 0))
if M - ms < total + 0.5:
    need = total + 4 - (M - ms); m, msr, mch = rd(mus) if mus.endswith(".wav") else (None, None, None)
    if m is None: sys.exit("music is not a wav; extend it by hand")
    # repeat the stretch of music that starts where the narration first gets longer, so later moods stay in step
    first = (edits[0][0] - shots[0]["start"] + ms) if edits else (M - ms) * 0.45
    cf = 2 * msr; L = int(need * msr) + cf; x = int(first * msr)
    fade = np.linspace(0, 1, cf)[:, None]
    head = m[:x + L].astype(float); rest = m[x:].astype(float)
    j2 = np.concatenate([head[:-cf], head[-cf:] * (1 - fade) + rest[:cf] * fade, rest[cf:]])   # = M + L - 2 s
    mn = os.path.splitext(P["music"])[0] + "_speechfit.wav"; wr(p(mn), np.clip(j2, -32768, 32767), msr, mch); P["music"] = mn
    print(f"music {M:.2f}s -> {len(j2)/msr:.2f}s")
# speech loudness = narrator loudness (user rule, 2026-11-02): each speaking clip gets the clip_gain that puts its own
# voice at the narrator's integrated loudness, so characters are never quieter (or louder) than the narration.
def lufs(f):
    o = subprocess.run(["ffmpeg", "-nostats", "-i", f, "-vn", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float([l for l in o.splitlines() if l.strip().startswith("I:")][-1].split()[1])
if P.get("speech_loudness_match", True):
    LN = lufs(p(P["voiceover"]))
    for i, s in enumerate(shots):
        if "clip_gain" not in s: continue
        LC = lufs(p(s["clip"])); g = round(10 ** ((LN - LC) / 20), 3)
        print(f"shot {i+1} {os.path.basename(s['clip'])}: voice {LC:.1f} LUFS, narrator {LN:.1f} LUFS -> clip_gain {s['clip_gain']} -> {g}")
        s["clip_gain"] = g
P["output"] = P["output"]
op = os.path.splitext(plan_path)[0] + ".speechfit.json"; json.dump(P, open(op, "w", encoding="utf-8"), indent=1); print("wrote", op)
