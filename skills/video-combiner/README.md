# Video Combiner

Combine Hook + Body + CTA video segments into all possible ad variations with auto-generated subtitles in multiple aspect ratios.

## What it does

- Takes video folders organized as Hook/Body/CTA
- Generates all possible combinations (e.g., 7 hooks x 6 bodies x 3 CTAs = 126 variations)
- Auto-transcribes audio with Whisper and burns subtitles
- Outputs in multiple formats: 16:9, 9:16, 4:5, 1:1
- Works with Google Drive or local files

## Install

```bash
curl -sL https://raw.githubusercontent.com/Gestao-Quatro-Ponto-Zero/g4os-skills/main/install.sh | bash -s -- skills/video-combiner
```

### Dependencies

```bash
brew install ffmpeg whisper-cpp
```

## Usage

In G4 OS:

> "Combinar videos da pasta X" or "Gerar variacoes de ads"

The skill walks you through a setup interview, runs a test combination for approval, then batch-processes everything.

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Skill definition and workflow phases |
| `icon.svg` | Film strip icon |
| `references/technical.md` | FFmpeg recipes, ASS subtitle format, encoding params |
| `scripts/batch_combine.py` | Python batch processing script (standalone CLI) |
