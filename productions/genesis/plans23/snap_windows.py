# snap verse boundaries in windows.json to the centre of the nearest real pause (>=0.3 s) within 1.2 s
import json, re, subprocess
r = subprocess.run(['ffmpeg', '-i', '../audio/Genesis_23_voiceover.wav', '-af', 'silencedetect=noise=-35dB:d=0.3', '-f', 'null', '-'], capture_output=True, text=True).stderr
P = list(zip([float(x) for x in re.findall(r'silence_start: ([\d.]+)', r)], [float(x) for x in re.findall(r'silence_end: ([\d.]+)', r)]))
w = json.load(open('windows.json'))
for i in range(len(w) - 1):
    b = w[i]['end']; c = [((s + e) / 2) for s, e in P if abs((s + e) / 2 - b) < 1.2]
    if c:
        nb = round(min(c, key=lambda x: abs(x - b)), 2); print(f"v{w[i]['verse']}/{w[i+1]['verse']}: {b} -> {nb}"); w[i]['end'] = w[i + 1]['start'] = nb
    else: print(f"v{w[i]['verse']}/{w[i+1]['verse']}: {b} (no pause near!)")
json.dump(w, open('windows.json', 'w'), indent=0)
