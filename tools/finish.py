#!/usr/bin/env python3
"""Turn the clean chapter film into the finished film: intro + subtitles + lower third + logo.

Usage:  python3 finish.py finish.json        (re-run whenever it says so - it resumes)

finish.json (paths relative to it):
{
  "film": "../final/Genesis_6_clean.mp4",          # clean film from fit_edit.py (no intro/subtitles/logo)
  "edit_plan": "genesis6_full.json",                # the fit_edit plan: verse windows + voiceover
  "verses": "verses.json",                          # [[1, "And it came to pass ..."], ...] exact KJV text
  "reference": "Genesis 6:1-22",                    # shown left of the bar
  "intro_video": "../video/Genesis_6_INTRO.mp4",    # animated intro card (Flow); optional
  "intro_voice": "../audio/Genesis_6_intro_voice.wav",
  "intro_min": 3.0, "intro_max": 6.0,               # chapter intro 3-6 s (book intro: set both to the narration length + 1.5)
  "intro_loop": false,                              # book intro: true = ping-pong loop the clip under long narration
  "references": "../../_tools/references",          # lower-third.png, logo-can-you-behold-him.png
  "fonts": "../../_tools/fonts",                    # CormorantGaramond_*.ttf
  "output": "../final/Genesis_6_final.mp4"
}
Writes also <output>.srt (timed for the finished film) and a clean-film .srt next to the clean film.
Subtitle timing = the verse windows of the edit (they change with the pictures). A verse that needs more than
3 lines is split ("[V16] start…" / "[V16] …end") at the voice pause nearest to the split point.
"""
import json, os, subprocess, sys, time, hashlib, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import overlay

FPS = 24
BUDGET = int(os.environ.get("FIN_BUDGET", 110))
T0 = time.time()
VENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), "-g", "48",
        "-video_track_timescale", "12288", "-an"]

def ff(args): subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + args, check=True)
def dur(p): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", p]).strip())
def over(): return time.time() - T0 > BUDGET
def again(msg): print(msg + " - run the same command again to continue."); sys.exit(3)
def ts(t):
    t = max(t, 0); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s - int(s)) * 1000)) % 1000:03d}"

def silences(audio):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", audio, "-af", "silencedetect=noise=-38dB:d=0.25", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    st, res = None, []
    try:
        for ln in out.splitlines():
            if "silence_start:" in ln: st = float(ln.split("silence_start:")[1].split()[0])
            if "silence_end:" in ln and st is not None: res.append((st + float(ln.split("silence_end:")[1].split()[0])) / 2); st = None
        return res
    except ValueError:   # some ffmpeg builds (CapCut's on Windows) print "invalid" timestamps: measure the pauses ourselves
        return silences_pcm(audio)

def silences_pcm(audio, noise_db=-38.0, min_len=0.25):
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", audio, "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
    x = np.abs(np.frombuffer(raw, np.int16).astype(float) / 32768)
    n = 160; k = len(x) // n; peak = x[:k * n].reshape(k, n).max(1)      # 10 ms blocks, loudest sample (as silencedetect)
    quiet = peak < 10 ** (noise_db / 20); res, i = [], 0
    while i < k:
        if quiet[i]:
            j = i
            while j < k and quiet[j]: j += 1
            if (j - i) * 0.01 >= min_len: res.append((i + j) * 0.005)
            i = j
        else: i += 1
    return res

def main(path):
    base = os.path.dirname(os.path.abspath(path)); p = lambda x: os.path.join(base, x)
    F = json.load(open(path, encoding="utf-8"))
    E = json.load(open(p(F["edit_plan"]), encoding="utf-8"))
    verses = dict((int(n), t) for n, t in json.load(open(p(F["verses"]), encoding="utf-8")))
    refs, fonts = p(F["references"]), p(F["fonts"])
    film = p(F["film"]); film_len = dur(film)
    work = os.path.join(os.path.expanduser("~"), ".finish_work", hashlib.md5((json.dumps(F, sort_keys=True) + str(os.path.getmtime(film)) + str(os.path.getsize(film))).encode()).hexdigest()[:10])
    os.makedirs(work, exist_ok=True)
    t0 = E["shots"][0]["start"]
    vo_pauses = [x - t0 for x in silences(p(E["voiceover"]))]

    if F.get("badge"):   # keep the verse text clear of the badge (lower right)
        overlay.TEXT_R = min(overlay.TEXT_R, int(F["badge"].get("cx", 1740) - F["badge"].get("size", 150) / 2) - 30)
    # ---- subtitle blocks on the film timeline
    blocks = []
    spans = []   # consecutive shots of the same verse (e.g. a dialogue shot) share one subtitle span
    for k, s in enumerate(E["shots"]):
        n = s.get("verse", k + 1)
        if spans and spans[-1][0] == n: spans[-1][2] = s["end"]
        else: spans.append([n, s["start"], s["end"]])
    for k, (n, sa, sb) in enumerate(spans):
        a, b = sa - t0, sb - t0
        if k == len(spans) - 1 and film_len - b < 0.5: b = film_len   # no outro in the film: last subtitle runs to the end
        pre = "" if F.get("plain_subs") else f"[V{n}]"   # plain_subs: sentence subtitles (Prophetic Implication films), no verse number
        text = f"{pre} {verses[n]}".strip()
        if overlay.fits(text, fonts):
            blocks.append((a, b, text)); continue
        parts, ratios = overlay.split_verse(pre, verses[n], fonts)
        parts = [x.strip() for x in parts]
        cuts = []
        for r in ratios:
            guess = a + (b - a) * r
            near = [x for x in vo_pauses if a + 1 < x < b - 1]
            cuts.append(min(near, key=lambda x: abs(x - guess)) if near and min(abs(x - guess) for x in near) < 2.0 else guess)
        bounds = [a] + cuts + [b]
        for i, t in enumerate(parts): blocks.append((bounds[i], bounds[i + 1], t))

    # ---- intro length
    has_intro = bool(F.get("intro_video"))
    intro_len = 0.0
    if has_intro:
        voice_len = dur(p(F["intro_voice"]))
        intro_len = min(max(voice_len + 0.5 + 1.0, F.get("intro_min", 3.0)), F.get("intro_max", 6.0)) if not F.get("intro_loop") else voice_len + 0.5 + 1.5
        intro_len = round(intro_len * FPS) / FPS

    # ---- SRT files
    def srt(offset):
        return "\n".join(f"{i+1}\n{ts(a+offset)} --> {ts(b+offset)}\n{t}\n" for i, (a, b, t) in enumerate(blocks))
    out = p(F["output"])
    open(os.path.splitext(out)[0] + ".srt", "w", encoding="utf-8").write(srt(intro_len))
    open(os.path.splitext(film)[0] + ".srt", "w", encoding="utf-8").write(srt(0.0))
    print(f"{len(blocks)} subtitle blocks; intro {intro_len:.2f}s")

    # ---- overlay images
    # "badge": the user's badge over Google Vids' watermark (lower right) - drawn on top of the bar too,
    # and the verse text column stops short of it
    B = F.get("badge"); bimg = None
    if B:
        from PIL import Image as _I
        bs = int(B.get("size", 150)); bx = int(B.get("cx", 1740) - bs / 2); by = int(B.get("cy", 898) - bs / 2)
        bimg = _I.open(p(B["image"])).convert("RGBA").resize((bs, bs), _I.LANCZOS)
        overlay.TEXT_R = min(overlay.TEXT_R, bx - 30)
    base_png = os.path.join(work, "base.png")
    if not os.path.exists(base_png): overlay.base_overlay(refs, fonts, F["reference"], bar_opacity=F.get("bar_opacity", 0.80)).save(base_png)
    from PIL import Image
    for i, (a, b, t) in enumerate(blocks):
        f = os.path.join(work, f"ov_{i:03d}.png")
        if os.path.exists(f): continue
        img = Image.open(base_png).convert("RGBA"); lay, _ = overlay.verse_layer(t, fonts); img.alpha_composite(lay)
        if bimg: img.alpha_composite(bimg, (bx, by))
        img.save(f)

    # ---- video pieces
    names = []
    if has_intro:
        o = os.path.join(work, "intro.mp4"); names.append(o)
        if not os.path.exists(o):
            iv = p(F["intro_video"])
            # Flow sometimes garbles small text while animating: paste the card's own static strip(s) back on top.
            # "intro_restore": [[y0, y1], ...] as fractions of the height, taken from "intro_card" (plain background only).
            if F.get("intro_card") and F.get("intro_restore"):
                fixed = os.path.join(work, "intro_fixed.mp4")
                if not os.path.exists(fixed):
                    card = p(F["intro_card"]); fl = ["[0:v]scale=1920:1080,setsar=1[v0]", "[1:v]scale=1920:1080,format=rgba[c]"]
                    cur = "[v0]"
                    for j, (y0, y1) in enumerate(F["intro_restore"]):
                        Y0, Y1 = int(1080 * y0), int(1080 * y1)
                        fl.append(f"[c]crop=1920:{Y1-Y0}:0:{Y0}[s{j}]" if j == len(F["intro_restore"]) - 1 else f"[c]split[c][cc{j}];[cc{j}]crop=1920:{Y1-Y0}:0:{Y0}[s{j}]")
                        fl.append(f"{cur}[s{j}]overlay=0:{Y0}[o{j}]"); cur = f"[o{j}]"
                    ff(["-i", iv, "-loop", "1", "-i", card, "-filter_complex", ";".join(fl) + f";{cur}null[v]",
                        "-map", "[v]", "-map", "0:a?", "-shortest", "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-c:a", "copy", fixed + ".tmp.mp4"])
                    os.replace(fixed + ".tmp.mp4", fixed)
                iv = fixed
            if F.get("intro_loop"):
                g = (f"[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps={FPS},setsar=1,split[a][b];[b]reverse[r];[a][r]concat=n=2:v=1:a=0,"
                     f"loop=loop=-1:size=32767,trim=0:{intro_len:.3f},setpts=PTS-STARTPTS,fade=t=in:st=0:d=0.4,fade=t=out:st={intro_len-0.5:.3f}:d=0.5[v]")
            else:
                g = (f"[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps={FPS},setsar=1,tpad=stop_mode=clone:stop_duration=6,"
                     f"trim=0:{intro_len:.3f},setpts=PTS-STARTPTS,fade=t=in:st=0:d=0.4,fade=t=out:st={intro_len-0.5:.3f}:d=0.5[v]")
            ff(["-i", iv, "-filter_complex", g, "-map", "[v]"] + VENC + [o + ".tmp.mp4"]); os.replace(o + ".tmp.mp4", o)
    fr = [round(a * FPS) for a, _, _ in blocks] + [round(blocks[-1][1] * FPS)]
    for i in range(len(blocks)):
        o = os.path.join(work, f"film_{i:03d}.mp4"); names.append(o)
        if os.path.exists(o): continue
        if over(): again(f"Rendered {i}/{len(blocks)} subtitle pieces")
        start, count = fr[i] / FPS, fr[i + 1] - fr[i]
        ff(["-ss", f"{start:.4f}", "-i", film, "-i", os.path.join(work, f"ov_{i:03d}.png"),
            "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]", "-map", "[v]", "-frames:v", str(count)] + VENC + [o + ".tmp.mp4"])
        os.replace(o + ".tmp.mp4", o)
    # ---- outro: after the last verse the bar + subtitle fade away (0.6 s), the logo stays, the scene plays on,
    #      then picture and logo fade to black together
    end_fr = round(film_len * FPS)
    if end_fr - fr[-1] > 6:
        o = os.path.join(work, "outro.mp4"); names.append(o)
        if not os.path.exists(o):
            logo_png = os.path.join(work, "logo.png")
            if not os.path.exists(logo_png): overlay.logo_layer(refs).save(logo_png)
            count = end_fr - fr[-1]; L = count / FPS; fade = min(1.5, L / 2)
            g = (f"[1:v]format=rgba,fade=t=out:st=0:d=0.6:alpha=1[s];[0:v][2:v]overlay=0:0[a];[a][s]overlay=0:0,"
                 f"fade=t=out:st={L-fade:.3f}:d={fade:.3f},format=yuv420p[v]")
            ff(["-ss", f"{fr[-1]/FPS:.4f}", "-i", film, "-loop", "1", "-framerate", str(FPS), "-i", os.path.join(work, f"ov_{len(blocks)-1:03d}.png"),
                "-loop", "1", "-framerate", str(FPS), "-i", logo_png, "-filter_complex", g, "-map", "[v]", "-frames:v", str(count)] + VENC + [o + ".tmp.mp4"])
            os.replace(o + ".tmp.mp4", o)

    # ---- audio: intro voice (+ the intro clip's own sound, low) then the film's audio
    aud = os.path.join(work, "audio.m4a")
    if not os.path.exists(aud):
        if has_intro:
            ia = p(F["intro_voice"])
            g = (f"[0:a]aresample=48000,aformat=channel_layouts=stereo,adelay=500|500,apad,atrim=0:{intro_len:.3f}[iv];"
                 f"[1:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.18,apad,atrim=0:{intro_len:.3f},afade=t=out:st={intro_len-0.5:.3f}:d=0.5[ia];"
                 f"[iv][ia]amix=inputs=2:duration=first:normalize=0[i];"
                 f"[2:a]aresample=48000,aformat=channel_layouts=stereo[f];[i][f]concat=n=2:v=0:a=1[a]")
            ff(["-i", ia, "-i", p(F["intro_video"]), "-i", film, "-filter_complex", g, "-map", "[a]", "-c:a", "aac", "-b:a", "192k", aud + ".tmp.m4a"])
        else:
            ff(["-i", film, "-vn", "-c:a", "aac", "-b:a", "192k", aud + ".tmp.m4a"])
        os.replace(aud + ".tmp.m4a", aud)

    lst = os.path.join(work, "pieces.txt")
    with open(lst, "w") as f:
        for q in names: f.write(f"file '{q}'\n")
    tmp = os.path.join(work, "final.mp4")
    ff(["-f", "concat", "-safe", "0", "-i", lst, "-i", aud, "-map", "0:v", "-map", "1:a", "-c", "copy", "-shortest", "-movflags", "+faststart", tmp])
    shutil.copyfile(tmp, out + ".tmp.mp4"); os.replace(out + ".tmp.mp4", out)
    print(f"wrote {out} ({dur(out):.2f}s = intro {intro_len:.2f}s + film {film_len:.2f}s)")

if __name__ == "__main__":
    main(sys.argv[1])
