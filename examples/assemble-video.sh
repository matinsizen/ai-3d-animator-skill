#!/usr/bin/env bash
# PRO 3D ANIMATOR — assemble captured frames into delivery files
# Usage:
#   bash assemble-video.sh frames scene.mp4 [--gif preview.gif]
# Env: FPS (default 30), GIF_FPS (default 12), GIF_W (default 560)
set -euo pipefail

DIR="${1:?frames directory}"; shift
OUT="${1:?output mp4}"; shift || true
GIF=""; [[ "${1:-}" == "--gif" ]] && GIF="${2:-}"

FPS="${FPS:-30}"

# 1) MP4 — H.264, yuv420p (universal playback), faststart (stream immediately)
ffmpeg -y -framerate "$FPS" -i "$DIR/f%04d.png" \
  -c:v libx264 -crf 17 -pix_fmt yuv420p -movflags +faststart "$OUT"

# 2) Optional GIF preview — palette per frame range, bayer dither (small + clean)
if [[ -n "$GIF" ]]; then
  ffmpeg -y -framerate "$FPS" -i "$DIR/f%04d.png" \
    -vf "fps=${GIF_FPS:-12},scale=${GIF_W:-560}:-1:flags=lanczos,split[a][b];[a]palettegen=stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4" \
    "$GIF"
  echo "gif → $GIF"
fi

echo "mp4 → $OUT"
echo "next: add sound with ffmpeg recipes from references/sound-design.md §3, then mux:"
echo "  ffmpeg -i $OUT -i mix.wav -c:v copy -c:a aac -b:a 192k -shortest final.mp4"
