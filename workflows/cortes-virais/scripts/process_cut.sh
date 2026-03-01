#!/bin/bash
# Process a single cut: extract clips, crop to vertical, burn subtitles, concatenate
#
# This script handles the SIMPLE PATH (no camera switches — single crop filter for the entire cut).
# For cuts WITH camera switches, the orchestrator handles multi-crop via the WORKFLOW.md Path B instructions.
#
# Usage: bash process_cut.sh <output-dir> <name> <hook_start> <hook_end> <body_start> <body_end> <workflow-dir> <transcript> [crop_filter] [margin_v]
#
# Arguments:
#   output-dir    Working directory with original.mp4
#   name          Cut identifier (e.g., corte1_tema)
#   hook_start    Hook start time in seconds
#   hook_end      Hook end time in seconds
#   body_start    Body start time in seconds
#   body_end      Body end time in seconds
#   workflow-dir  Path to the workflow directory (contains scripts/)
#   transcript    Path to transcript.json
#   crop_filter   (optional) ffmpeg crop filter, default: "crop=ih*9/16:ih"
#   margin_v      (optional) Subtitle vertical margin, default: 180

set -euo pipefail

OUTPUT_DIR="$1"
NAME="$2"
HOOK_START="$3"
HOOK_END="$4"
BODY_START="$5"
BODY_END="$6"
WORKFLOW_DIR="$7"
TRANSCRIPT="$8"
CROP_FILTER="${9:-crop=ih*9/16:ih}"
MARGIN_V="${10:-280}"

# Ensure OUTPUT_DIR is absolute
case "$OUTPUT_DIR" in
  /*) ;; # already absolute
  *) echo "ERROR: OUTPUT_DIR must be an absolute path, got: $OUTPUT_DIR"; exit 1 ;;
esac

ORIGINAL="$OUTPUT_DIR/original.mp4"
FINAL_DIR="$OUTPUT_DIR/final"
mkdir -p "$FINAL_DIR"

echo "=== Processing cut: $NAME ==="
echo "  Crop filter: $CROP_FILTER"
echo "  Subtitle margin: $MARGIN_V"

# --- Step 1: Extract hook and body clips ---
echo "  Extracting hook clip ($HOOK_START -> $HOOK_END)..."
ffmpeg -y -ss "$HOOK_START" -to "$HOOK_END" -i "$ORIGINAL" \
  -avoid_negative_ts make_zero \
  "$OUTPUT_DIR/${NAME}_hook.mp4" 2>/dev/null

echo "  Extracting body clip ($BODY_START -> $BODY_END)..."
ffmpeg -y -ss "$BODY_START" -to "$BODY_END" -i "$ORIGINAL" \
  -avoid_negative_ts make_zero \
  "$OUTPUT_DIR/${NAME}_body.mp4" 2>/dev/null

# --- Step 2: Generate ASS subtitles ---
echo "  Generating hook subtitles..."
python3 "$WORKFLOW_DIR/scripts/generate_ass.py" \
  --transcript "$TRANSCRIPT" \
  --output "$OUTPUT_DIR/${NAME}_hook.ass" \
  --start "$HOOK_START" \
  --end "$HOOK_END" \
  --font-size 58 \
  --margin-v "$MARGIN_V"

echo "  Generating body subtitles..."
python3 "$WORKFLOW_DIR/scripts/generate_ass.py" \
  --transcript "$TRANSCRIPT" \
  --output "$OUTPUT_DIR/${NAME}_body.ass" \
  --start "$BODY_START" \
  --end "$BODY_END" \
  --font-size 58 \
  --margin-v "$MARGIN_V"

# --- Step 3: Process hook (crop + subtitles) ---
echo "  Processing hook (crop + subtitles)..."
ffmpeg -y -i "$OUTPUT_DIR/${NAME}_hook.mp4" \
  -vf "${CROP_FILTER},scale=1080:1920,ass=$OUTPUT_DIR/${NAME}_hook.ass" \
  -c:v libx264 -preset fast -crf 23 -pix_fmt yuv420p \
  -c:a aac -b:a 128k -ar 44100 \
  "$OUTPUT_DIR/${NAME}_hook_proc.mp4" 2>/dev/null

# --- Step 4: Process body (crop + subtitles) ---
echo "  Processing body (crop + subtitles)..."
ffmpeg -y -i "$OUTPUT_DIR/${NAME}_body.mp4" \
  -vf "${CROP_FILTER},scale=1080:1920,ass=$OUTPUT_DIR/${NAME}_body.ass" \
  -c:v libx264 -preset fast -crf 23 -pix_fmt yuv420p \
  -c:a aac -b:a 128k -ar 44100 \
  "$OUTPUT_DIR/${NAME}_body_proc.mp4" 2>/dev/null

# --- Step 5: Concatenate hook + body ---
echo "  Concatenating hook + body..."
CONCAT_FILE="$OUTPUT_DIR/concat_${NAME}.txt"
echo "file '${NAME}_hook_proc.mp4'" > "$CONCAT_FILE"
echo "file '${NAME}_body_proc.mp4'" >> "$CONCAT_FILE"

cd "$OUTPUT_DIR"
ffmpeg -y -f concat -safe 0 -i "concat_${NAME}.txt" \
  -c copy "$FINAL_DIR/${NAME}_final.mp4" 2>/dev/null

# --- Step 6: Verify output ---
DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$FINAL_DIR/${NAME}_final.mp4")
echo "  Duration: ${DURATION}s"

# Extract QC frames at different points
echo "  Extracting QC frames..."
# Hook area (1.5s in)
ffmpeg -y -ss 1.5 -i "$FINAL_DIR/${NAME}_final.mp4" \
  -frames:v 1 -q:v 2 "$FINAL_DIR/${NAME}_qc_hook.jpg" 2>/dev/null

# Early body (5s in)
ffmpeg -y -ss 5 -i "$FINAL_DIR/${NAME}_final.mp4" \
  -frames:v 1 -q:v 2 "$FINAL_DIR/${NAME}_qc_body_early.jpg" 2>/dev/null

# Mid body (halfway through)
HALF=$(echo "$DURATION / 2" | bc -l 2>/dev/null || echo "30")
ffmpeg -y -ss "$HALF" -i "$FINAL_DIR/${NAME}_final.mp4" \
  -frames:v 1 -q:v 2 "$FINAL_DIR/${NAME}_qc_body_mid.jpg" 2>/dev/null

echo "=== Done: $FINAL_DIR/${NAME}_final.mp4 (${DURATION}s) ==="
