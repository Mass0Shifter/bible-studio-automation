#!/usr/bin/env python3
"""Run a Bible Studio tool natively on Windows (all CPU cores + the NVIDIA encoder) with CapCut's ffmpeg.

Usage:  python winrun.py <tool.py> [args...]      e.g.  python winrun.py ..\\fit_edit.py genesis14_full.speechfit.json

CapCut ships ffmpeg.exe without ffprobe and without libx264. This launcher, for the tool it runs:
  - puts CapCut's ffmpeg folder first on PATH, so "ffmpeg" resolves;
  - answers the two ffprobe questions the tools ask (format duration, video frame count) with ffmpeg itself;
  - turns libx264 encodes into h264_nvenc ones of the same quality class (-crf N -> -cq N, constant quality).
On Linux it just runs the tool unchanged.
"""
import os, re, runpy, subprocess, sys

FFDIR = os.environ.get("CAPCUT_FFMPEG_DIR", r"C:\Users\USER\AppData\Local\CapCut\Apps\9.5.0.4050")
FF = os.path.join(FFDIR, "ffmpeg.exe")


def probe(args):
    """emulate:  ffprobe ... -show_entries format=duration ... FILE   /   ... stream=nb_read_packets ... FILE"""
    f = args[-1]; joined = " ".join(args)
    if "nb_read_packets" in joined or "nb_frames" in joined:
        r = _orig_run([FF, "-hide_banner", "-i", f, "-map", "0:v:0", "-c", "copy", "-f", "null", "-"],
                      capture_output=True, text=True, errors="ignore")
        m = re.findall(r"frame=\s*(\d+)", r.stderr)
        return (m[-1] if m else "0") + "\n"
    r = _orig_run([FF, "-hide_banner", "-i", f], capture_output=True, text=True, errors="ignore")
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", r.stderr)
    if not m: raise RuntimeError("no duration for " + f)
    return f"{int(m.group(1))*3600 + int(m.group(2))*60 + float(m.group(3)):.6f}\n"


def fix_encoder(a):
    if "libx264" not in a: return a
    out, i = [], 0
    while i < len(a):
        x = a[i]
        if x == "libx264": out.append("h264_nvenc")
        elif x == "-crf": out += ["-rc", "vbr", "-cq", a[i + 1], "-b:v", "0"]; i += 1
        elif x == "-preset": out += ["-preset", "p6"]; i += 1
        else: out.append(x)
        i += 1
    return out


_orig_run = subprocess.run
_orig_popen_init = subprocess.Popen.__init__


class _Done:   # minimal stand-in for a finished process
    def __init__(self, args, out, text): self.args, self.returncode = args, 0; self.stdout = out if text else out.encode(); self.stderr = "" if text else b""
    def check_returncode(self): pass


def _run(args, *a, **k):
    if isinstance(args, (list, tuple)) and args and os.path.basename(str(args[0])).lower().startswith("ffprobe"):
        text = k.get("text") or k.get("universal_newlines") or ("encoding" in k) or ("errors" in k)
        return _Done(args, probe(list(args)), bool(text))
    if isinstance(args, (list, tuple)) and args and os.path.basename(str(args[0])).lower() in ("ffmpeg", "ffmpeg.exe"):
        args = [FF] + fix_encoder(list(args[1:]))
    return _orig_run(args, *a, **k)


def _check_output(args, *a, **k):
    k.setdefault("stdout", subprocess.PIPE); k["check"] = True
    r = _run(args, *a, **k)
    return r.stdout


if os.name == "nt":
    os.environ["PATH"] = FFDIR + os.pathsep + os.environ.get("PATH", "")
    subprocess.run = _run
    subprocess.check_output = _check_output

if __name__ == "__main__":
    tool = os.path.abspath(sys.argv[1]); sys.argv = [tool] + sys.argv[2:]
    sys.path.insert(0, os.path.dirname(tool))
    runpy.run_path(tool, run_name="__main__")
