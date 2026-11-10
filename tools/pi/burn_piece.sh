#!/bin/bash
# render one 12 s caption piece: one.sh <index>
cd "$HOME/mnt/Bible Studio/Prophetic Implications/Esther"
F="$HOME/mnt/Bible Studio/_tools/fonts"; i=$1; s=$((i*12))
o=_check/full/c$(printf %02d $i).mp4
[ -f $o ] && { echo skip $i; exit 0; }
ffmpeg -v error -y -ss $s -t 12 -i final/Esther_PI_clean.mp4 -loop 1 -i _check/logo.png -filter_complex "[0:v]setpts=PTS+$s/TB,ass=plans/pi_clean.ass:fontsdir='$F',setpts=PTS-$s/TB[v];[v][1:v]overlay=0:0:shortest=1:enable='lt(t,$(python3 -c "print(208.05-$s)"))',format=yuv420p[o]" -map "[o]" -map 0:a -c:v libx264 -preset veryfast -crf 18 -r 24 -c:a aac -b:a 192k -ar 48000 $o.tmp.mp4 && mv $o.tmp.mp4 $o && echo done $i
