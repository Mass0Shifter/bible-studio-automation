#!/usr/bin/env python3
"""God's voice treatment for the narration (user rule, 2026-10-30).

When God (or the LORD) speaks, the narrator's Paz voice is altered so it sounds divine:
slightly deeper (pitch -1.3 semitones, tempo unchanged), a soft sub-octave layer underneath,
warm low end, and a hall reverb whose tail rings on briefly after the words.
The narrator's own lines ("And God said unto Abraham,") stay plain Paz.

Usage:  python3 divine_voice.py in.wav spans.json out.wav [voice=god|angel|gabriel|michael] [--preview preview.wav start end]
  spans.json = [[start_s, end_s], ...]  (seconds in in.wav, God's words only)
Settings can be tuned in PRESET below.
"""
import sys, json, subprocess, wave, os, tempfile
import numpy as np

# Voices (user rule, 2026-11-04): "god" for God / the LORD; "angel" for any unnamed angel (Genesis 19);
# "gabriel" and "michael" for those named angels. Choose with  voice=angel  on the command line.
VOICES = {
    "god":     dict(pitch=0.87, sub=0.32, low_shelf_db=5.0, high_shelf_db=-2.0, reverb_s=4.5, wet=1.0, gain_db=2.5, chorus=0.0),
    # unnamed angels: lighter than God - a little deeper than Paz, airy shimmer (chorus), bright, shorter hall
    "angel":   dict(pitch=0.95, sub=0.10, low_shelf_db=2.0, high_shelf_db=2.5, reverb_s=3.0, wet=0.75, gain_db=1.5, chorus=0.45),
    # Gabriel, the herald: clear and bright, ringing, a touch more presence than other angels
    "gabriel": dict(pitch=0.97, sub=0.05, low_shelf_db=1.0, high_shelf_db=3.5, reverb_s=3.6, wet=0.85, gain_db=2.0, chorus=0.55),
    # Michael, the archangel who fights: deeper and firmer, strong low body, tighter hall
    "michael": dict(pitch=0.90, sub=0.22, low_shelf_db=4.0, high_shelf_db=0.5, reverb_s=2.8, wet=0.7, gain_db=2.5, chorus=0.25),
}
PRESET = dict(pitch=0.87,       # 0.87 = -2.4 semitones (clearly deeper; v1 of 2026-10-30 at -1.3 st was too subtle for the user)
              sub=0.32,         # level of the octave-down layer (gives a big, resonant body)
              low_shelf_db=5.0, # warmth at ~180 Hz
              reverb_s=4.5,     # hall / temple length (user asked twice for more echo, 2026-10-30)
              wet=1.0,          # reverb level (0.55 -> 0.85 -> 1.0)
              gain_db=2.5,      # God's words this much louder than the narrator (user: 'a bit more louder')
              gain_match=True)

def rd(p):
    w = wave.open(p); sr = w.getframerate(); ch = w.getnchannels()
    a = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, ch).astype(np.float32) / 32768
    w.close(); return a, sr

def wr(p, a, sr):
    a = np.clip(a, -1, 1); w = wave.open(p, 'wb'); w.setnchannels(a.shape[1]); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((a * 32767).astype(np.int16).tobytes()); w.close()

def make_ir(path, sr, length):
    rng = np.random.default_rng(7); n = int(length * sr); t = np.arange(n) / sr
    env = np.exp(-t * 6.9 / length)                      # -60 dB at `length`
    ir = rng.standard_normal((n, 2)) * env[:, None]
    k = 6; ir = np.apply_along_axis(lambda x: np.convolve(x, np.ones(k) / k, 'same'), 0, ir)   # soften highs
    ir[:int(0.012 * sr)] = 0                              # pre-delay
    for d, g in ((0.019, .5), (0.031, .38), (0.047, .3), (0.063, .22)):   # early reflections
        ir[int(d * sr), 0] += g; ir[int((d + 0.004) * sr), 1] += g
    ir /= np.sqrt((ir ** 2).sum(0)).max()
    wr(path, ir * 0.9, sr)

def process(inp, spans, out, P=PRESET):
    dry, sr = rd(inp); ch = dry.shape[1]; n = len(dry)
    mask = np.zeros(n, np.float32); r = int(0.03 * sr)
    for s, e in spans:
        a, b = int(s * sr), min(n, int(e * sr)); mask[a:b] = 1
        mask[max(0, a - r):a] = np.maximum(mask[max(0, a - r):a], np.linspace(0, 1, a - max(0, a - r)))
        mask[b:b + r] = np.maximum(mask[b:b + r], np.linspace(1, 0, len(mask[b:b + r])))
    td = tempfile.mkdtemp(); src = os.path.join(td, 'god_src.wav'); ir = os.path.join(td, 'ir.wav'); g = os.path.join(td, 'god.wav')
    wr(src, dry * mask[:, None], sr); make_ir(ir, sr, P['reverb_s'])
    fc = (f"[0:a]asplit=2[a][b];"
          f"[a]rubberband=pitch={P['pitch']}:formant=shifted[v];"
          f"[b]rubberband=pitch=0.5,lowpass=f=700,volume={P['sub']}[s];"
          f"[v][s]amix=inputs=2:normalize=0,lowshelf=f=180:g={P['low_shelf_db']},highshelf=f=7000:g={P.get('high_shelf_db', -2)}"
          + (f",chorus=0.7:0.9:45|62:{P['chorus']}|{P['chorus'] * 0.8:.3f}:0.25|0.33:2|2.6" if P.get('chorus', 0) > 0 else "") + "[m];"
          f"[m]asplit=2[d][w0];[w0][1:a]afir=dry=0:wet=1[w];[w]volume={P['wet']}[wv];"
          f"[d][wv]amix=inputs=2:normalize=0[o]")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-i', ir, '-filter_complex', fc, '-map', '[o]',
                    '-ar', str(sr), '-ac', str(ch), '-c:a', 'pcm_s16le', g], check=True)
    god, _ = rd(g); god = np.pad(god, ((0, max(0, n - len(god))), (0, 0)))[:n]
    if P['gain_match'] and mask.sum() > 0:
        m = mask > 0.5
        k = np.sqrt((dry[m] ** 2).mean() / max(1e-9, (god[m] ** 2).mean())) * 10 ** (P.get('gain_db', 0) / 20); god *= k
    outa = dry * (1 - mask[:, None]) + god
    t = 0.75; m = np.abs(outa) > t   # soft limiter so the louder voice never clips (peak stays under -1 dBFS)
    outa[m] = np.sign(outa[m]) * (t + 0.14 * np.tanh((np.abs(outa[m]) - t) / 0.14))
    wr(out, outa, sr)
    return out

if __name__ == '__main__':
    inp, sp, out = sys.argv[1:4]
    spans = json.load(open(sp)) if sp.endswith('.json') else json.loads(sp)
    P = dict(PRESET)
    for a in sys.argv[4:]:
        if a.startswith('voice='): P.update(VOICES[a.split('=', 1)[1]])
    for a in sys.argv[4:]:
        if a.startswith('voice='): continue
        if '=' in a and not a.startswith('--'): k, v = a.split('='); P[k] = float(v)   # e.g. pitch=0.85 wet=0.6
    process(inp, spans, out, P); print('wrote', out, P)
    if '--preview' in sys.argv:
        i = sys.argv.index('--preview'); pv, s, e = sys.argv[i + 1], sys.argv[i + 2], sys.argv[i + 3]
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', s, '-to', e, '-i', inp, '-ss', s, '-to', e, '-i', out, '-filter_complex',
                        '[0:a]apad=pad_dur=1[a0];[a0][1:a]concat=n=2:v=0:a=1', pv], check=True)
        print('preview (before, then after)', pv)
