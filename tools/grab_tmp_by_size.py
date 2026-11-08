# Copy Vids clip downloads (<uuid>.tmp in Downloads) into a chapter's video folder, matching by exact byte size.
# usage: python3 grab_tmp_by_size.py "<Downloads dir>" "<video dir>" <prefix> "key size" ...
import os, sys, shutil
dl, out, prefix = sys.argv[1], sys.argv[2], sys.argv[3]
want = {}
for kv in sys.argv[4:]:
    k, s = kv.split(); want[int(s)] = k
for f in os.listdir(dl):
    if not f.endswith('.tmp'): continue
    p = os.path.join(dl, f); sz = os.path.getsize(p)
    if sz in want:
        dst = os.path.join(out, f'{prefix}_{want[sz]}.mp4')
        if not os.path.exists(dst): shutil.copyfile(p, dst); print('copied', want.pop(sz), f)
        else: want.pop(sz)
print('missing:', list(want.values()))
