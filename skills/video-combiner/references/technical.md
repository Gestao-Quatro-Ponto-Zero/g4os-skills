# Video Combiner — Technical Reference

## Dependencies

### whisper-cpp
```bash
# Check
which whisper-cli

# Install
brew install whisper-cpp
```

### Whisper Model
```bash
MODEL_PATH="$HOME/.local/share/whisper-models/ggml-medium.bin"

# Check
test -f "$MODEL_PATH" && echo "OK"

# Download (~1.5GB)
mkdir -p "$(dirname "$MODEL_PATH")"
curl -L -o "$MODEL_PATH" \
  "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin"
```

### ffmpeg
```bash
which ffmpeg  # Usually pre-installed on macOS via brew
```

## Working Directory

All processing happens in: `~/.workspace-mcp/attachments/video-combiner/`

Files must be under the user's home directory (`$HOME/`) for Drive upload (MCP sandbox restriction).

## FFmpeg Recipes

### 1. Concatenation (no re-encode, instant)

Create a concat list file:
```
file '/path/to/hook.mov'
file '/path/to/body.mov'
file '/path/to/cta.mov'
```

```bash
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy output.mov
```

### 2. Audio Extraction for Whisper

```bash
ffmpeg -y -i input.mov -ar 16000 -ac 1 -c:a pcm_s16le output.wav
```

### 3. Crop + Scale + Burn Subtitles

All cropped versions use: `-c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p -c:a aac -b:a 192k`

**16:9 (1920x1080)** — YouTube, landscape ads:
```bash
ffmpeg -y -i input.mov -vf "scale=1920:1080,ass=subs_16x9.ass" \
  -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p -c:a aac -b:a 192k output_16x9.mov
```

**9:16 (1080x1920)** — Stories, Reels, TikTok:
```bash
ffmpeg -y -i input.mov -vf "crop=ih*9/16:ih,scale=1080:1920,ass=subs_9x16.ass" \
  -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p -c:a aac -b:a 192k output_9x16.mov
```

**4:5 (1080x1350)** — Instagram/Facebook feed:
```bash
ffmpeg -y -i input.mov -vf "crop=ih*4/5:ih,scale=1080:1350,ass=subs_4x5.ass" \
  -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p -c:a aac -b:a 192k output_4x5.mov
```

**1:1 (1080x1080)** — Instagram square:
```bash
ffmpeg -y -i input.mov -vf "crop=ih:ih,scale=1080:1080,ass=subs_1x1.ass" \
  -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p -c:a aac -b:a 192k output_1x1.mov
```

## Whisper Transcription

```bash
whisper-cli \
  -m ~/.local/share/whisper-models/ggml-medium.bin \
  -l pt \
  -osrt \
  --max-len 40 \
  --split-on-word \
  -of output_prefix \
  input.wav
```

- `-l pt` for Portuguese (change as needed)
- `--max-len 40` keeps subtitle segments short (~2s each)
- `--split-on-word` avoids mid-word breaks
- Output: `output_prefix.srt`

## ASS Subtitle Templates

### Format-specific parameters

| Format | PlayResX | PlayResY | FontSize | Outline | MarginV | Line Breaks |
|--------|----------|----------|----------|---------|---------|-------------|
| 16:9   | 1920     | 1080     | 72       | 4       | 60      | No          |
| 9:16   | 1080     | 1920     | 58       | 3.5     | 180     | Yes (\N)    |
| 4:5    | 1080     | 1350     | 58       | 3.5     | 100     | No          |
| 1:1    | 1080     | 1080     | 56       | 3.5     | 80      | No          |

### ASS Header Template

```
[Script Info]
Title: {title}
ScriptType: v4.00+
PlayResX: {play_res_x}
PlayResY: {play_res_y}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font},{font_size},{primary_color},&H000000FF,{outline_color},{back_color},{bold},0,0,0,100,100,0,0,{border_style},{outline},{shadow},{alignment},{margin_l},{margin_r},{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
```

### ASS Color Format

ASS uses `&HAABBGGRR` format (NOT RGB):
- White: `&H00FFFFFF`
- Black: `&H00000000`
- Yellow: `&H0000FFFF`
- Red: `&H000000FF`
- Semi-transparent black bg: `&H80000000`

### Default Style Values

```
Font: Arial Black
Bold: -1 (true)
PrimaryColour: &H00FFFFFF (white)
OutlineColour: &H00000000 (black)
BackColour: &H80000000 (semi-transparent black)
BorderStyle: 1 (outline + shadow)
Shadow: 0
Alignment: 2 (bottom center)
MarginL: 40 (16:9) / 30 (vertical)
MarginR: 40 (16:9) / 30 (vertical)
```

### Line Break Strategy for 9:16

For narrow vertical videos, long lines must be broken. Strategy:
- Find the midpoint of each subtitle text
- Break at the nearest word boundary using `\N`
- Keep both lines roughly equal length

## Naming Convention

```
VARIACAO_H{hook_num}_B{body_num}_C{cta_num}_{format}[_SUB].mov
```

Examples:
- `VARIACAO_H1_B3_C2_16x9_SUB.mov`
- `VARIACAO_H7_B6_C2_9x16_SUB.mov`

## Drive Folder Structure

```
Source Folder/
├── HOOKS/          (or "Hooks", case-insensitive match)
├── BODYS/          (or "Bodys", "Bodies")
├── CTAS/           (or "CTAs", "Ctas")
└── VARIACOES FINAIS/  (or user-specified destination)
```

When listing Drive folders, match subfolder names case-insensitively and look for these patterns:
- Hook(s): contains "hook"
- Body/Bodies: contains "body" or "bodies"
- CTA(s): contains "cta"
- Output: contains "variacao", "final", or "output"
