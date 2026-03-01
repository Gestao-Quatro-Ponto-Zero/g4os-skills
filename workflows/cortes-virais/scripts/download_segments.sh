#!/bin/bash
# Download only the needed segments from a YouTube video, with buffer.
# Usage: bash download_segments.sh "YOUTUBE_URL" "OUTPUT_DIR" "CUTS_JSON_PATH" [BUFFER_SECS]
#
# CUTS_JSON_PATH must be a JSON array with objects containing:
#   { "name": "corte1_tema", "hook_start": 100.0, "hook_end": 103.0, "body_start": 95.0, "body_end": 165.0 }
#
# Each cut produces: {OUTPUT_DIR}/segments/{name}.mp4
# Overlapping segments (within 2*BUFFER of each other) are merged into one download.
#
# Also saves {OUTPUT_DIR}/segments/offset_map.json with the mapping:
#   { "corte1_tema": { "file": "segments/corte1_tema.mp4", "download_start": 35.0, "download_end": 225.0 } }
# This offset_map is critical: all timestamps in the cut are ABSOLUTE (relative to original video).
# To use them with the segment file, subtract download_start.

set -euo pipefail

URL="$1"
OUTPUT_DIR="$2"
CUTS_JSON="$3"
BUFFER="${4:-60}"  # Default: 60 seconds buffer on each side

if [ -z "$URL" ] || [ -z "$OUTPUT_DIR" ] || [ -z "$CUTS_JSON" ]; then
  echo "Usage: bash download_segments.sh \"YOUTUBE_URL\" \"OUTPUT_DIR\" \"CUTS_JSON\" [BUFFER_SECS]"
  exit 1
fi

mkdir -p "$OUTPUT_DIR/segments"

echo "=== Calculating segment ranges (buffer: ${BUFFER}s) ==="

# Use Python to compute merged segments from cuts JSON
python3 -c "
import json, sys

cuts = json.load(open('$CUTS_JSON'))
buffer = $BUFFER

# Compute raw ranges for each cut (min of all starts - buffer, max of all ends + buffer)
ranges = []
for c in cuts:
    seg_start = max(0, min(c['hook_start'], c['body_start']) - buffer)
    seg_end = max(c['hook_end'], c['body_end']) + buffer
    ranges.append({'name': c['name'], 'start': seg_start, 'end': seg_end})

# Sort by start time
ranges.sort(key=lambda x: x['start'])

# Merge overlapping ranges
merged = []
for r in ranges:
    if merged and r['start'] <= merged[-1]['end']:
        # Overlap — merge into previous range, keep all names
        merged[-1]['end'] = max(merged[-1]['end'], r['end'])
        merged[-1]['names'].append(r['name'])
    else:
        merged.append({'start': r['start'], 'end': r['end'], 'names': [r['name']]})

# Build offset map and download commands
offset_map = {}
download_cmds = []
for i, m in enumerate(merged):
    # If merged group has 1 cut, use its name. If multiple, use group_N.
    if len(m['names']) == 1:
        filename = m['names'][0]
    else:
        filename = f\"group_{i+1}\"

    for name in m['names']:
        offset_map[name] = {
            'file': f\"segments/{filename}.mp4\",
            'download_start': m['start'],
            'download_end': m['end'],
            'buffer_secs': buffer
        }

    # Format timestamps for yt-dlp (seconds to MM:SS or HH:MM:SS)
    def fmt(s):
        h = int(s // 3600)
        m_val = int((s % 3600) // 60)
        sec = s % 60
        if h > 0:
            return f\"{h}:{m_val:02d}:{sec:05.2f}\"
        return f\"{m_val}:{sec:05.2f}\"

    download_cmds.append({
        'filename': filename,
        'start': fmt(m['start']),
        'end': fmt(m['end']),
        'start_sec': m['start'],
        'end_sec': m['end'],
        'names': m['names']
    })

# Save offset map
json.dump(offset_map, open('$OUTPUT_DIR/segments/offset_map.json', 'w'), indent=2)
print(f\"Offset map saved: {len(offset_map)} cuts across {len(download_cmds)} segment(s)\")

# Output download commands as JSON for bash to consume
json.dump(download_cmds, open('/tmp/download_cmds.json', 'w'))
print()
for cmd in download_cmds:
    names_str = ', '.join(cmd['names'])
    dur = cmd['end_sec'] - cmd['start_sec']
    print(f\"  {cmd['filename']}: {cmd['start']} -> {cmd['end']} ({dur:.0f}s) [{names_str}]\")
"

echo ""
echo "=== Downloading segments ==="

# Read download commands and execute
python3 -c "
import json, subprocess, sys

cmds = json.load(open('/tmp/download_cmds.json'))

for i, cmd in enumerate(cmds):
    filename = cmd['filename']
    start = cmd['start']
    end = cmd['end']
    names = ', '.join(cmd['names'])

    print(f\"\n--- Segment {i+1}/{len(cmds)}: {filename} ({start} -> {end}) ---\")
    print(f\"    Covers cuts: {names}\")

    outpath = '$OUTPUT_DIR/segments/' + filename + '.mp4'

    result = subprocess.run([
        'yt-dlp',
        '-f', 'bestvideo[height<=1080]+bestaudio',
        '--merge-output-format', 'mp4',
        '--download-sections', f'*{start}-{end}',
        '--force-keyframes-at-cuts',
        '-o', outpath,
        '--no-warnings',
        '$URL'
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f'ERROR downloading {filename}:', result.stderr[-500:] if result.stderr else 'unknown')
        sys.exit(1)

    # Verify file exists and get info
    probe = subprocess.run([
        'ffprobe', '-v', 'error',
        '-show_entries', 'stream=width,height',
        '-show_entries', 'format=duration',
        '-of', 'json', outpath
    ], capture_output=True, text=True)
    info = json.loads(probe.stdout)
    duration = float(info.get('format', {}).get('duration', 0))
    print(f'    OK: {outpath} ({duration:.1f}s)')
"

echo ""
echo "=== Extracting reference frame ==="
# Extract a frame from the first segment for format check
FIRST_SEG=$(ls "$OUTPUT_DIR/segments/"*.mp4 2>/dev/null | head -1)
if [ -n "$FIRST_SEG" ]; then
  ffmpeg -y -ss 5 -i "$FIRST_SEG" -frames:v 1 -q:v 2 "$OUTPUT_DIR/frame_check.jpg" 2>/dev/null
  echo "Reference frame: $OUTPUT_DIR/frame_check.jpg"
fi

echo ""
echo "=== Done ==="
echo "Segments: $OUTPUT_DIR/segments/"
echo "Offset map: $OUTPUT_DIR/segments/offset_map.json"
echo ""
echo "IMPORTANT: All cut timestamps are ABSOLUTE (relative to original video)."
echo "To convert to segment-relative: subtract offset_map[name].download_start"
