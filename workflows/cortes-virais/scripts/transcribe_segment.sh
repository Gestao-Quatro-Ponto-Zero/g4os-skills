#!/bin/bash
# Transcribe a video segment with whisper-cli medium model
# Extracts audio, transcribes, parses JSON → word-level timestamps
#
# Usage: bash transcribe_segment.sh <output-dir> <name> <body_start> <body_end> <video_path> [hook_start] [hook_end]
#
# Outputs:
#   {output-dir}/{name}_segment.wav     — segment audio
#   {output-dir}/{name}_medium.json     — raw whisper-cli JSON output
#   {output-dir}/{name}_body_words.json — parsed word-level timestamps [{text, start, end}]
#   {output-dir}/{name}_hook_words.json — (if hook timestamps provided)

set -euo pipefail

OUTPUT_DIR="$1"
NAME="$2"
BODY_START="$3"
BODY_END="$4"
VIDEO_PATH="$5"
HOOK_START="${6:-}"
HOOK_END="${7:-}"

MODEL="${WHISPER_MODEL:-$HOME/.local/share/whisper-models/ggml-medium.bin}"

# Validate model exists
if [ ! -f "$MODEL" ]; then
  echo "ERROR: Whisper medium model not found at $MODEL"
  echo "Download with: curl -L https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin -o $MODEL"
  exit 1
fi

# Validate whisper-cli exists
if ! command -v whisper-cli &>/dev/null; then
  echo "ERROR: whisper-cli not found. Install with: brew install whisper-cpp"
  exit 1
fi

echo "=== Transcribing segment: $NAME ==="
echo "  Body: ${BODY_START}s -> ${BODY_END}s"
echo "  Model: $MODEL"

# --- Step 1: Extract body segment audio ---
echo "  Extracting body audio..."
ffmpeg -y -ss "$BODY_START" -to "$BODY_END" -i "$VIDEO_PATH" \
  -vn -acodec pcm_s16le -ar 16000 -ac 1 \
  "$OUTPUT_DIR/${NAME}_segment.wav" 2>/dev/null

# --- Step 2: Transcribe body with whisper-cli medium ---
echo "  Transcribing body with whisper medium..."
cd "$OUTPUT_DIR"
whisper-cli -m "$MODEL" -l pt -ojf -f "${NAME}_segment.wav" -of "${NAME}_medium" 2>&1 | tail -3

# --- Step 3: Parse whisper JSON → word-level timestamps ---
echo "  Parsing word-level timestamps..."
python3 -c "
import json, sys, re

input_file = sys.argv[1]
output_file = sys.argv[2]

with open(input_file) as f:
    data = json.load(f)

words = []
for seg in data.get('transcription', []):
    tokens = seg.get('tokens', [])
    current_word = ''
    word_start = None

    for tok in tokens:
        text = tok.get('text', '')

        # Skip special tokens
        if text.startswith('[') and text.endswith(']'):
            continue

        # Parse timestamp — handle both 'HH:MM:SS,mmm' (SRT) and millisecond offsets
        offsets = tok.get('offsets', {})
        ts_from = offsets.get('from', 0)
        ts_to = offsets.get('to', 0)

        # offsets are in milliseconds
        start_sec = ts_from / 1000.0
        end_sec = ts_to / 1000.0

        # Whisper tokens may be subwords — accumulate into words
        if text.startswith(' ') or not current_word:
            # New word boundary
            if current_word.strip():
                words.append({
                    'text': current_word.strip(),
                    'start': round(word_start, 3),
                    'end': round(prev_end, 3)
                })
            current_word = text
            word_start = start_sec
        else:
            current_word += text

        prev_end = end_sec

    # Flush last word in segment
    if current_word.strip():
        words.append({
            'text': current_word.strip(),
            'start': round(word_start, 3),
            'end': round(prev_end, 3)
        })

# --- Post-processing ---

# Filter hallucination artifacts (repeated characters like 'Liziziziziz...')
filtered = []
for w in words:
    text = w['text']
    # Detect repeated patterns: same 2-3 char substring repeated 3+ times
    is_hallucination = False
    if len(text) > 10:
        for pat_len in range(1, 4):
            pat = text[:pat_len]
            if pat * 5 in text:
                is_hallucination = True
                break
    if not is_hallucination:
        filtered.append(w)
    else:
        print(f'  WARNING: Filtered hallucination: \"{text[:30]}...\"')

# Remove empty words
filtered = [w for w in filtered if w['text'].strip()]

with open(output_file, 'w') as f:
    json.dump(filtered, f, ensure_ascii=False, indent=2)

print(f'  Parsed {len(filtered)} words')

# Key phrases spot-check
for w in filtered:
    if any(kw in w['text'].upper() for kw in ['CEO', 'G4', 'BOLSA', 'FAMÍLIA']):
        print(f'  {w[\"start\"]:8.2f}  {w[\"text\"]}')
" "$OUTPUT_DIR/${NAME}_medium.json" "$OUTPUT_DIR/${NAME}_body_words.json"

# --- Step 4: Handle hook transcription (if provided) ---
if [ -n "$HOOK_START" ] && [ -n "$HOOK_END" ]; then
  echo "  Extracting hook audio..."
  ffmpeg -y -ss "$HOOK_START" -to "$HOOK_END" -i "$VIDEO_PATH" \
    -vn -acodec pcm_s16le -ar 16000 -ac 1 \
    "$OUTPUT_DIR/${NAME}_hook_segment.wav" 2>/dev/null

  echo "  Transcribing hook with whisper medium..."
  cd "$OUTPUT_DIR"
  whisper-cli -m "$MODEL" -l pt -ojf -f "${NAME}_hook_segment.wav" -of "${NAME}_hook_medium" 2>&1 | tail -3

  echo "  Parsing hook word timestamps..."
  python3 -c "
import json, sys

input_file = sys.argv[1]
output_file = sys.argv[2]

with open(input_file) as f:
    data = json.load(f)

words = []
for seg in data.get('transcription', []):
    tokens = seg.get('tokens', [])
    current_word = ''
    word_start = None

    for tok in tokens:
        text = tok.get('text', '')
        if text.startswith('[') and text.endswith(']'):
            continue

        offsets = tok.get('offsets', {})
        start_sec = offsets.get('from', 0) / 1000.0
        end_sec = offsets.get('to', 0) / 1000.0

        if text.startswith(' ') or not current_word:
            if current_word.strip():
                words.append({'text': current_word.strip(), 'start': round(word_start, 3), 'end': round(prev_end, 3)})
            current_word = text
            word_start = start_sec
        else:
            current_word += text
        prev_end = end_sec

    if current_word.strip():
        words.append({'text': current_word.strip(), 'start': round(word_start, 3), 'end': round(prev_end, 3)})

filtered = [w for w in words if w['text'].strip() and not (len(w['text']) > 10 and w['text'][:2] * 5 in w['text'])]

with open(output_file, 'w') as f:
    json.dump(filtered, f, ensure_ascii=False, indent=2)

print(f'  Parsed {len(filtered)} hook words')
" "$OUTPUT_DIR/${NAME}_hook_medium.json" "$OUTPUT_DIR/${NAME}_hook_words.json"
fi

echo "=== Done: $NAME transcription ==="
