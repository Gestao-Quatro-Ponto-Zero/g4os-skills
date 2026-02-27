---
name: "Video Combiner"
description: "Combine Hook + Body + CTA video segments into all possible variations with auto-generated subtitles and multiple aspect ratios. Use when user says: 'combinar videos', 'gerar variacoes de ads', 'video combiner', 'montar criativos', or needs to create ad variations from video segments organized in folders (Hook/Body/CTA structure)."
---

# Video Combiner

Automates the creation of ad video variations by combining Hook + Body + CTA segments with subtitles in multiple aspect ratios.

## Workflow

### Phase 1: Setup Interview

Collect these inputs from the user (ask one topic at a time):

**1. Source folder**
Ask: "Qual a pasta com os videos? (link do Drive ou caminho local)"
- If Drive link: extract folder ID, use `list_drive_items` to find subfolders matching Hook/Body/CTA patterns
- If local path: scan for subfolders

**2. Subtitle preferences**
Ask: "Como quer as legendas?" and show defaults:
- **Fonte**: Arial Black (bold)
- **Cor**: Branco com borda preta
- **Posicao**: Parte inferior (bottom center)
- **Tamanho da borda**: 4px (landscape) / 3.5px (vertical)

Then ask: "Quer manter o padrao ou customizar? Se customizar, pode ajustar: fonte, peso (bold/regular), cor do texto, cor da borda, posicao no video (altura), tamanho da borda."

**3. Output formats**
Ask: "Quais formatos?" and show options:
- 16:9 (1920x1080) — YouTube, landscape ads
- 9:16 (1080x1920) — Stories, Reels, TikTok
- 4:5 (1080x1350) — Instagram/Facebook feed
- 1:1 (1080x1080) — Instagram square

Default: all formats the user originally mentioned.

**4. Destination**
Ask: "Onde salvar os videos finais?" — look for existing output folder in the source, or ask for destination.

### Phase 2: Dependency Check

Before processing, verify (install if missing):

```bash
# 1. ffmpeg
which ffmpeg || echo "INSTALL: brew install ffmpeg"

# 2. whisper-cli
which whisper-cli || echo "INSTALL: brew install whisper-cpp"

# 3. Whisper model
test -f ~/.local/share/whisper-models/ggml-medium.bin || echo "DOWNLOAD model"
```

If whisper-cli is missing, install: `brew install whisper-cpp`
If model is missing, download:
```bash
mkdir -p ~/.local/share/whisper-models
curl -L -o ~/.local/share/whisper-models/ggml-medium.bin \
  "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin"
```

### Phase 3: Inventory & Preview

1. List all videos in each subfolder (Hook, Body, CTA)
2. Show inventory table with file names and count
3. Calculate total combinations: `hooks x bodys x ctas x formats`
4. Show estimate to user

### Phase 4: Test Run

**Always generate 1 test combination first.** Pick the smallest files to minimize processing time.

1. Download source videos if from Drive (to `~/.workspace-mcp/attachments/video-combiner/`)
2. Run the batch script in test mode:
   ```bash
   python3 {skill_dir}/scripts/batch_combine.py \
     --hooks-dir /path/to/hooks \
     --bodys-dir /path/to/bodys \
     --ctas-dir /path/to/ctas \
     --output-dir ~/.workspace-mcp/attachments/video-combiner/output \
     --formats 16x9 9x16 4x5 \
     --language pt \
     --test
   ```
3. Present test results with `filecard` for each format
4. **Ask for feedback**: "Confere o enquadramento, legendas e timing. Quer ajustar algo antes de processar todas as combinacoes?"

### Phase 5: Batch Processing

After user approves the test:

1. If source is Drive, download ALL videos to local temp dirs
2. Run batch script without `--test` flag
3. Monitor progress (the script prints progress per combination)
4. Upload results to destination folder

For Drive upload:
- Use `create_drive_file` with `fileUrl=file://` and `mime_type=video/quicktime`
- Files must be under the user's home directory (`$HOME/`) due to MCP sandbox restrictions
- Organize by format in subfolders if total > 50 files

### Phase 6: Summary

Present final summary:
- Total videos created
- Total size
- Any errors
- Link to output folder

## Config Reference

For subtitle style customization and FFmpeg recipes, see [references/technical.md](references/technical.md).

## Batch Script

The Python script at [scripts/batch_combine.py](scripts/batch_combine.py) handles all processing. It accepts either CLI args or a JSON config file.

Quick reference:
```bash
# Dry run (show combinations only)
python3 scripts/batch_combine.py --hooks-dir H --bodys-dir B --ctas-dir C --output-dir O --dry-run

# Test (1 combination)
python3 scripts/batch_combine.py --hooks-dir H --bodys-dir B --ctas-dir C --output-dir O --test

# Full batch
python3 scripts/batch_combine.py --config config.json

# Without subtitles
python3 scripts/batch_combine.py --hooks-dir H --bodys-dir B --ctas-dir C --output-dir O --no-subs
```

## Important Notes

- Concatenation works WITHOUT re-encode only when all source videos share the same codec, resolution, and framerate. If they differ, fall back to re-encoding the concat step.
- For Drive sources, download all videos first to avoid repeated API calls during batch processing.
- The 9:16 crop assumes the subject is centered. If not, the user needs to adjust crop positioning.
- Language defaults to `pt` (Portuguese). Ask user if content is in another language.
