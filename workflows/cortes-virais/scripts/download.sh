#!/bin/bash
# FALLBACK: Download FULL YouTube video and extract audio for transcription.
# Only use this when Google AI / Apify are unavailable and Whisper base is needed
# for the rough transcript (Method 3 in the workflow).
#
# For the normal flow, use download_segments.sh instead — it downloads only
# the needed segments after cut selection, saving 60-80% bandwidth.
#
# Usage: bash download.sh "YOUTUBE_URL" "OUTPUT_DIR"

set -euo pipefail

URL="$1"
OUTPUT_DIR="$2"

if [ -z "$URL" ] || [ -z "$OUTPUT_DIR" ]; then
  echo "Usage: bash download.sh \"YOUTUBE_URL\" \"OUTPUT_DIR\""
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

echo "=== Downloading video ==="
yt-dlp -f "bestvideo[height<=1080]+bestaudio" \
  --merge-output-format mp4 \
  -o "$OUTPUT_DIR/original.mp4" \
  "$URL"

echo "=== Video info ==="
ffprobe -v error \
  -show_entries stream=width,height,codec_name \
  -show_entries format=duration \
  -of json \
  "$OUTPUT_DIR/original.mp4"

echo "=== Extracting audio for transcription ==="
ffmpeg -y -i "$OUTPUT_DIR/original.mp4" \
  -vn -acodec pcm_s16le -ar 16000 -ac 1 \
  "$OUTPUT_DIR/audio.wav"

echo "=== Extracting reference frame (at 30s) ==="
ffmpeg -y -ss 30 -i "$OUTPUT_DIR/original.mp4" \
  -frames:v 1 -q:v 2 \
  "$OUTPUT_DIR/frame_check.jpg"

echo "=== Done ==="
echo "Video: $OUTPUT_DIR/original.mp4"
echo "Audio: $OUTPUT_DIR/audio.wav"
echo "Frame: $OUTPUT_DIR/frame_check.jpg"
