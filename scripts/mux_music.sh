#!/bin/bash
set -e
cd "$(dirname "$0")"
mkdir -p final

get_dur() { ffprobe -v error -show_entries format=duration -of csv=p=0 "$1"; }

VIDEO_DUR=$(get_dur ege_video_14_v3.mp4)

while IFS=$'\t' read -r idx track; do
  audio="audio/track${track}.m4a"
  adur=$(get_dur "$audio")
  target=$(python3 -c "print(min($VIDEO_DUR, $adur))")
  echo "video $idx <- track$idx track=$track adur=$adur target=$target"
  ffmpeg -nostdin -y -i "ege_video_${idx}_v3.mp4" -i "$audio" \
    -map 0:v -map 1:a -t "$target" \
    -c:v libx264 -profile:v high -pix_fmt yuv420p -preset medium -crf 18 -r 60 \
    -c:a aac -ar 44100 -ac 2 -b:a 192k \
    "final/ege_video_${idx}.mp4" 2>&1 | tail -2
  fdur=$(get_dur "final/ege_video_${idx}.mp4")
  echo "video $idx final duration: $fdur (track $track)"
done < music_assign.tsv
