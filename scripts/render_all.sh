#!/bin/bash
set -e
cd "$(dirname "$0")"
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf

while IFS=$'\t' read -r idx photo textfile fontsize shadow border borderw; do
  echo "=== video $idx ==="
  ffmpeg -nostdin -y -loop 1 -framerate 60 -i "$photo" \
    -f lavfi -i "anullsrc=channel_layout=stereo:sample_rate=44100" \
    -filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,scale=4320:7680:flags=lanczos,zoompan=z='1+0.08*on/359':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=360:s=1080x1920:fps=60,drawtext=fontfile=${FONT}:textfile=${textfile}:fontsize=${fontsize}:fontcolor=white:line_spacing=4:borderw=${borderw}:bordercolor=black@${border}:shadowcolor=black@${shadow}:shadowx=4:shadowy=4:text_align=C+M:x=(w-text_w)/2:y=(h-text_h)/2:alpha='if(lt(t\,0.5)\,0\,if(lt(t\,0.9)\,(t-0.5)/0.4\,1))'[v]" \
    -map "[v]" -map 1:a -t 6 -r 60 \
    -c:v libx264 -profile:v high -pix_fmt yuv420p -preset medium -crf 18 \
    -c:a aac -ar 44100 -ac 2 -b:a 192k -shortest \
    "seg${idx}_v3.mp4" 2>&1 | tail -2

  printf "file 'seg%s_v3.mp4'\nfile 'outro.mp4'\n" "$idx" > "list${idx}_v3.txt"
  ffmpeg -nostdin -y -f concat -safe 0 -i "list${idx}_v3.txt" -c copy "ege_video_${idx}_v3.mp4" 2>&1 | tail -2
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "ege_video_${idx}_v3.mp4")
  echo "video $idx duration: $dur"
done < plan.tsv
