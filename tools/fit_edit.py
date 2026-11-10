#!/usr/bin/env python3
"""Fit Flow clips to the narration, verse by verse, and render the film.

Usage:  python3 fit_edit.py plan.json          (run it again whenever it says so - it resumes)

Plan (JSON, paths relative to the plan file):
{
  "voiceover": "../audio/Genesis_6_voiceover.wav",
  "music": "../music/Genesis_6_music.wav",   # optional "music_start"
  "music_gain_db": -11.2,       # bed level (user's standard; was -9.8 until 10 Nov 2026: "15 % lower, it competes with the voice")
  "ambient_gain": 0.22,         # clips' own natural sound
  "dissolve": 0.5,              # cross-dissolve between shots (seconds)
  "end_tail": 0.4,              # seconds kept after the last word (when there is no outro)
  "outro": 3.0,                 # calm ending: the last scene plays on ~3 s after the last verse, music fades out, fade to black
  "output": "../final/Genesis_6_final.mp4",
  "badge": {"image": "../../_tools/references/Radiant Golden Portal Emblem.png", "cx": 1740, "cy": 898, "size": 150},
                                # optional: the user's badge over Google Vids' watermark (lower right); a shot with "badge": false is left bare
  "shots": [ {"clip": "../video/Genesis_6_S01_SH01.mp4", "start": 0.0, "end": 6.13, "method": "auto"}, ... ]
}
start/end = the verse window in the voiceover (cut points are the middle of the pause after each verse).

Fitting each clip to its window (needed = window + dissolve, last shot window + tail):
  clip long enough            -> trim (keeps the start of the clip = the shot image)
  needed/clip <= 1.25         -> "slow": plays slower; <=6% by frame timing, more with motion interpolation (cached)
  longer                      -> "lead": holds the clip's first frame with a slow pull-out, then plays the clip
Rendering is done in small pieces (shot bodies + 0.5 s dissolves) that are joined at the end, so it works
inside a shell that stops long commands: each run renders for about BUDGET seconds and then asks to be re-run.
Work files live in ~/.fit_edit_work/<plan name>/ (outside the user's folders).
"""
import json, os, subprocess, sys, time, math, shutil, hashlib, re

W, H, FPS = 1920, 1080, 24
CHUNK = 2.5        # seconds of source per motion-interpolation chunk
BUDGET = float(os.environ.get("FE_BUDGET", 110))   # seconds of work per run (FE_BUDGET env overrides; 2026-11-08)
T0 = time.time()
CONF = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setsar=1"

FFMPEG_BIN = os.environ.get("FFMPEG_BIN", r"C:\Users\USER\AppData\Local\CapCut\Apps\9.5.0.4050\ffmpeg.exe" if os.name == "nt" else "ffmpeg")
VENC = ["-c:v", "h264_nvenc" if os.name == "nt" else "libx264", "-b:v", "8M", "-pix_fmt", "yuv420p", "-r", str(FPS), "-g", "48",
        "-video_track_timescale", "12288", "-an"]

def dur(p):
    try:
        return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                              "-of", "default=nw=1:nk=1", p]).strip())
    except Exception:
        r = subprocess.run([FFMPEG_BIN, "-i", p], capture_output=True, text=True, errors="ignore")
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", r.stderr)
        if m:
            return float(m.group(1))*3600 + float(m.group(2))*60 + float(m.group(3))
        raise RuntimeError(f"Could not get duration for {p}")

def ff(args):
    subprocess.run([FFMPEG_BIN, "-y", "-hide_banner", "-loglevel", "error"] + args, check=True)
def over():
    return time.time() - T0 > BUDGET
def again(msg):
    print(msg + " - run the same command again to continue."); sys.exit(3)

def slow_cache(clip, k, work):
    """Motion-interpolated slow-down of a clip, rendered in 2.5 s chunks, two at a time; resumable."""
    import concurrent.futures as cf
    cache = os.path.join(work, f"{os.path.splitext(os.path.basename(clip))[0]}.{int(os.path.getmtime(clip))}.slow{int(round(k*1000))}.mp4")  # mtime in the name: a replaced clip (e.g. 720p -> 1080p) is re-slowed
    if os.path.exists(cache): return cache
    C = dur(clip); n = math.ceil(C / CHUNK)
    parts = [f"{cache}.p{j:02d}.mp4" for j in range(n)]
    venc_chunk = ["-c:v", "h264_nvenc", "-b:v", "8M"] if os.name == "nt" else ["-c:v", "libx264", "-preset", "veryfast", "-crf", "16"]
    def one(j):
        tmp = parts[j] + ".tmp.mp4"
        ff(["-ss", f"{j*CHUNK:.3f}", "-t", f"{CHUNK:.3f}", "-i", clip, "-an", "-vf",
            f"{CONF},setpts={k:.5f}*(PTS-STARTPTS),minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1"] +
            venc_chunk + [tmp])
        os.replace(tmp, parts[j])
    todo = [j for j in range(n) if not os.path.exists(parts[j])]
    with cf.ThreadPoolExecutor(max_workers=2) as ex:
        while todo:
            if over(): again(f"Slow-motion for {os.path.basename(clip)}: {n-len(todo)}/{n} chunks done")
            batch, todo = todo[:2], todo[2:]
            list(ex.map(one, batch))
    lst = cache + ".txt"
    with open(lst, "w") as f:
        for q in parts: f.write(f"file '{q.replace(chr(92), '/')}'\n")
    ff(["-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", cache + ".tmp.mp4"]); os.replace(cache + ".tmp.mp4", cache)
    for q in parts + [lst]: os.remove(q)
    return cache


def main(plan_path):
    base = os.path.dirname(os.path.abspath(plan_path))
    P = json.load(open(plan_path, encoding="utf-8"))
    p = lambda x: os.path.join(base, x)
    d = float(P.get("dissolve", 0.5))
    # "outro": seconds the last scene keeps playing after the last verse (calm ending; music fades, picture fades to black)
    outro = float(P.get("outro", 0)); tail = outro if outro else float(P.get("end_tail", 0.4))
    end_fade = 1.5 if outro else 0.8
    shots = P["shots"]; n = len(shots)
    # work folder per plan name; every piece is named after a hash of what it depends on, so changing one
    # shot (or the ending) only re-renders the pieces that changed
    tag = os.path.splitext(os.path.basename(plan_path))[0]
    work = os.path.join(os.path.expanduser("~"), ".fit_edit_work", tag); os.makedirs(work, exist_ok=True)
    # badge over Google Vids' watermark (lower right): scaled once, overlaid on every shot that has it
    B = P.get("badge"); bpng = None; BX = BY = 0
    if B:
        bs = int(B.get("size", 150)); BX = int(B.get("cx", 1740) - bs / 2); BY = int(B.get("cy", 898) - bs / 2)
        bpng = os.path.join(work, f"badge_{bs}.png")
        ff(["-i", p(B["image"]), "-vf", f"scale={bs}:{bs}:flags=lanczos,format=rgba", bpng])
    has_b = lambda i: bool(B) and shots[i].get("badge", True)

    # ---- plan each shot
    # frame-exact timeline (2026-10-28): every boundary is a whole frame, so picture and sound never drift apart
    D = int(round(d * FPS)); d = D / FPS; TF = int(round(tail * FPS))
    t0_ = shots[0]["start"]
    FB = [int(round((s["start"] - t0_) * FPS)) for s in shots] + [int(round((shots[-1]["end"] - t0_) * FPS))]
    S = []
    for i, s in enumerate(shots):
        clip = p(s["clip"]); C = dur(clip); wf = FB[i + 1] - FB[i]; w = wf / FPS
        need = (wf + (D if i < n - 1 else TF)) / FPS
        m = s.get("method", "auto")
        if m == "auto" and "clip_gain" in s:
            m = "trim"   # a speaking clip is NEVER slowed (lip-sync and voice pitch): play it at 1x, hold its last frame if the window is longer
        if m == "auto":
            if i == n - 1 and outro:   # the ending: stretch the end of the last clip, never a still lead-in
                m = "trim" if C >= need - 0.15 else "slow"
            else:
                m = "trim" if C >= need - 0.15 else ("slow" if need / C <= 1.25 else "lead")
        k = min(need / C, 1.4) if m == "slow" else 1.0   # beyond 1.4x the last frame is simply held
        S.append(dict(clip=clip, C=C, w=w, wf=wf, nf=wf + (D if i < n - 1 else TF), need=need, m=m, k=k, lead=max(need - C, 0) if m == "lead" else 0))
    for i, s in enumerate(S):
        note = {"trim": "trim", "slow": f"slow x{1/s['k']:.2f}", "lead": f"still lead-in {s['lead']:.2f}s"}[s["m"]]
        print(f"shot {i+1:2d}: window {s['w']:.2f}s, clip {s['C']:.1f}s -> {note}")
    # slow-motion caches (only for slow-downs over 6%)
    for s in S:
        if s["m"] == "slow" and s["k"] > 1.06: s["src"] = slow_cache(s["clip"], s["k"], work)

    def vsrc(i, idx, lab):
        """filter text turning input #idx into the fitted shot i, labelled [lab]"""
        s = S[i]
        if s["m"] == "slow" and s["k"] > 1.06:
            return f"[{idx}:v]{CONF},tpad=stop_mode=clone:stop_duration={s['need']:.3f},trim=0:{s['need']:.3f},setpts=PTS-STARTPTS,fps={FPS},settb=1/{FPS}[{lab}]"
        if s["m"] == "slow":
            return f"[{idx}:v]{CONF},setpts={s['k']:.5f}*PTS,fps={FPS},tpad=stop_mode=clone:stop_duration={s['need']:.3f},trim=0:{s['need']:.3f},setpts=PTS-STARTPTS,fps={FPS},settb=1/{FPS}[{lab}]"
        if s["m"] == "lead":
            fr = int(round(s["lead"] * FPS))
            return (f"[{idx}:v]{CONF},split[c{lab}][f{lab}];[f{lab}]trim=end_frame=1,loop=loop={fr}:size=1,setpts=N/{FPS}/TB,"
                    f"scale={W*2}:{H*2},zoompan=z='1.08-0.08*on/{max(fr-1,1)}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},setsar=1[l{lab}];"
                    f"[l{lab}][c{lab}]concat=n=2:v=1:a=0,tpad=stop_mode=clone:stop_duration={s['need']:.3f},trim=0:{s['need']:.3f},setpts=PTS-STARTPTS,fps={FPS},settb=1/{FPS}[{lab}]")
        return f"[{idx}:v]{CONF},tpad=stop_mode=clone:stop_duration={s['need']:.3f},trim=0:{s['need']:.3f},setpts=PTS-STARTPTS,fps={FPS},settb=1/{FPS}[{lab}]"
    def inp(i): return S[i].get("src", S[i]["clip"])

    # ---- video pieces: body_i, then dissolve_i (shot i -> i+1)
    pieces = []
    for i in range(n):
        a = D if i > 0 else 0; b = S[i]["wf"] if i < n - 1 else S[i]["nf"]   # frame numbers
        pieces.append(("body", i, a, b))
        if i < n - 1: pieces.append(("mix", i, None, None))
    def key(*parts):
        return hashlib.md5(json.dumps(["framefix1"] + [str(x) for x in parts]).encode()).hexdigest()[:10]
    def sig(i):
        s = S[i]; return (s["clip"], os.path.getmtime(s["clip"]), round(s["need"], 3), s["m"], round(s["k"], 4), round(s["lead"], 3))
    names = []
    for kind, i, a, b in pieces:
        k_ = key(kind, sig(i), a, b, i == 0, i == n - 1, end_fade, has_b(i), B) if kind == "body" else key(kind, sig(i), sig(i + 1), d, has_b(i) or has_b(i + 1), B)
        out = os.path.join(work, f"{kind}_{i:02d}_{k_}.mp4"); names.append(out)
        if os.path.exists(out): continue
        if over(): again(f"Rendered {len([x for x in names[:-1]])}/{len(pieces)} pieces")
        if kind == "body":
            fx = ""
            if i == 0: fx += ",fade=t=in:st=0:d=0.5"
            if i == n - 1: fx += f",fade=t=out:st={(b-a)/FPS-end_fade:.3f}:d={end_fade}"
            if has_b(i):
                g = vsrc(i, 0, "F") + f";[F]trim=start_frame={a}:end_frame={b},setpts=PTS-STARTPTS,fps={FPS},settb=1/{FPS}[pre];[pre][1:v]overlay={BX}:{BY}:shortest=1{fx}[v]"
                ff(["-i", inp(i), "-loop", "1", "-i", bpng, "-filter_complex", g, "-map", "[v]", "-frames:v", str(b - a)] + VENC + [out + ".tmp.mp4"])
            else:
                g = vsrc(i, 0, "F") + f";[F]trim=start_frame={a}:end_frame={b},setpts=PTS-STARTPTS,fps={FPS},settb=1/{FPS}{fx}[v]"
                ff(["-i", inp(i), "-filter_complex", g, "-map", "[v]", "-frames:v", str(b - a)] + VENC + [out + ".tmp.mp4"])
        else:
            g = (vsrc(i, 0, "A") + ";" + vsrc(i + 1, 1, "B") +
                 f";[A]trim=start_frame={S[i]['wf']}:end_frame={S[i]['wf']+D},setpts=PTS-STARTPTS,fps={FPS},settb=1/{FPS}[x];"
                 f"[B]trim=start_frame=0:end_frame={D},setpts=PTS-STARTPTS,fps={FPS},settb=1/{FPS}[y];"
                 f"[x][y]xfade=transition=fade:duration={d}:offset=0" + (f"[m];[m][2:v]overlay={BX}:{BY}:shortest=1[v]" if has_b(i) or has_b(i + 1) else "[v]"))
            ff(["-i", inp(i), "-i", inp(i + 1)] + (["-loop", "1", "-i", bpng] if has_b(i) or has_b(i + 1) else []) + ["-filter_complex", g, "-map", "[v]", "-frames:v", str(D)] + VENC + [out + ".tmp.mp4"])
        os.replace(out + ".tmp.mp4", out)

    # ---- audio: narration + music bed + clips' ambience
    total = (FB[n] - FB[0] + TF) / FPS
    t0 = shots[0]["start"]
    audio = os.path.join(work, "audio_" + key(json.dumps(P, sort_keys=True), [sig(i) for i in range(n)]) + ".m4a")
    if not os.path.exists(audio):
        args, fl = [], []
        for i, s in enumerate(S):
            args += ["-i", s["clip"]]
            base_a = f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,volume={shots[i].get('clip_gain', P.get('ambient_gain', 0.22))}"
            if s["m"] == "slow":
                fl.append(f"{base_a},atempo={1/s['k']:.5f},apad,atrim=0:{s['need']:.3f},asetpts=PTS-STARTPTS[a{i}]")
            elif s["m"] == "lead":
                fl.append(f"{base_a},asplit[x{i}][y{i}];[x{i}]atrim=0:{s['lead']:.3f}[xa{i}];[xa{i}][y{i}]acrossfade=d=0.3,apad,atrim=0:{s['need']:.3f},asetpts=PTS-STARTPTS[a{i}]")
            else:
                fl.append(f"{base_a},apad,atrim=0:{s['need']:.3f},asetpts=PTS-STARTPTS[a{i}]")
        cur = "[a0]"
        for i in range(1, n):
            fl.append(f"{cur}[a{i}]acrossfade=d={d}[ax{i}]"); cur = f"[ax{i}]"
        vi = n; mi = n + 1
        args += ["-i", p(P["voiceover"]), "-i", p(P["music"])]
        ms = float(P.get("music_start", 0.0))
        fl.append(f"{cur}apad,atrim=0:{total:.3f},volume=1[amb]")
        fl.append(f"[{vi}:a]aresample=48000,aformat=channel_layouts=stereo,atrim={t0:.3f}:{t0+total:.3f},asetpts=PTS-STARTPTS,apad,atrim=0:{total:.3f}" + "".join(f",volume=enable='between(t,{a-t0:.3f},{b-t0:.3f})':volume=0" for a, b in P.get("vo_mute", [])) + "[vo]")
        fl.append(f"[{mi}:a]aresample=48000,aformat=channel_layouts=stereo,atrim={ms:.3f}:{ms+total:.3f},asetpts=PTS-STARTPTS,"
                  f"volume={P.get('music_gain_db',-11.2)}dB,afade=t=in:st=0:d=1.5,afade=t=out:st={max(total-max(3, outro),0):.3f}:d={max(3, outro)}[mus]")
        fl.append("[vo][amb][mus]amix=inputs=3:duration=first:normalize=0,alimiter=limit=0.95[aout]")
        ff(args + ["-filter_complex", ";".join(fl), "-map", "[aout]", "-c:a", "aac", "-b:a", "192k", audio + ".tmp.m4a"])
        os.replace(audio + ".tmp.m4a", audio)

    # ---- join
    lst = os.path.join(work, "pieces.txt")
    with open(lst, "w") as f:
        for q in names: f.write(f"file '{q.replace(chr(92), '/')}'\n")
    out = p(P["output"]); os.makedirs(os.path.dirname(out), exist_ok=True)
    tmp = os.path.join(work, "final.mp4")
    ff(["-f", "concat", "-safe", "0", "-i", lst, "-i", audio, "-map", "0:v", "-map", "1:a", "-c", "copy", "-shortest", "-movflags", "+faststart", tmp])
    shutil.copyfile(tmp, out + ".tmp.mp4"); os.replace(out + ".tmp.mp4", out)
    print(f"wrote {out} ({dur(out):.2f}s, expected {total:.2f}s)")

if __name__ == "__main__":
    main(sys.argv[1])
