#!/bin/bash
# usage: CH="Genesis 7" SUB=video grab.sh <target-name> [timeout] [min-bytes]
# Takes the oldest finished media (named .mp4 or complete browser .tmp) in Downloads newer than ~/.mark
# whose content is not already in <chapter>/<SUB>/ (md5), copies it to <SUB>/<target>.mp4.
T="$1"; TO=${2:-160}; MIN=${3:-100000}; CH=${CH:-Genesis 7}; SUB=${SUB:-video}
D="$HOME/mnt/Downloads"; V="$HOME/mnt/Bible Studio/$CH/$SUB"; mkdir -p "$V"
for i in $(seq 1 $((TO/5))); do
  known=$(md5sum "$V"/*.mp4 "$V"/_v1/*.mp4 2>/dev/null | cut -d' ' -f1)
  while read -r ts f; do
    [ -z "$f" ] && continue
    s1=$(stat -c %s "$f" 2>/dev/null) || continue; sleep 2; s2=$(stat -c %s "$f" 2>/dev/null) || continue
    [ "$s1" = "$s2" ] && [ "$s1" -gt "$MIN" ] || continue
    ffprobe -v error -show_entries format=duration -of csv=p=0 "$f" >/dev/null 2>&1 || continue
    m=$(md5sum "$f" | cut -d' ' -f1); echo "$known" | grep -q "$m" && continue
    cp "$f" "$V/$T.mp4"; echo "OK $T <- $(basename "$f") $(ffprobe -v error -show_entries format=duration:stream=width,height -of csv=p=0 "$V/$T.mp4" | tr '\n' ' ')"; exit 0
  done < <(find "$D" -maxdepth 1 \( -name '*.mp4' -o -name '*.tmp' \) -newer $HOME/.mark -printf '%T@ %p\n' 2>/dev/null | sort -n)
  sleep 5
done
echo "WAITING $T"
