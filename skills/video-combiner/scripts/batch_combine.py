#!/usr/bin/env python3
"""
Video Combiner — Batch processing script.
Combines Hook + Body + CTA video segments into all possible variations
with optional subtitle burning in multiple aspect ratios.

Usage:
    python3 batch_combine.py --config config.json
    python3 batch_combine.py --hooks-dir /path/to/hooks --bodys-dir /path/to/bodys --ctas-dir /path/to/ctas --output-dir /path/to/output

Config JSON format:
{
    "hooks_dir": "/path/to/hooks",
    "bodys_dir": "/path/to/bodys",
    "ctas_dir": "/path/to/ctas",
    "output_dir": "/path/to/output",
    "formats": ["16x9", "9x16", "4x5"],
    "subtitles": true,
    "whisper_model": "~/.local/share/whisper-models/ggml-medium.bin",
    "language": "pt",
    "subtitle_style": {
        "font": "Arial Black",
        "bold": true,
        "primary_color": "&H00FFFFFF",
        "outline_color": "&H00000000",
        "back_color": "&H80000000",
        "border_style": 1,
        "shadow": 0,
        "alignment": 2
    },
    "format_params": {
        "16x9": {"play_res_x": 1920, "play_res_y": 1080, "font_size": 72, "outline": 4, "margin_v": 60, "margin_lr": 40},
        "9x16": {"play_res_x": 1080, "play_res_y": 1920, "font_size": 58, "outline": 3.5, "margin_v": 180, "margin_lr": 30},
        "4x5":  {"play_res_x": 1080, "play_res_y": 1350, "font_size": 58, "outline": 3.5, "margin_v": 100, "margin_lr": 30},
        "1x1":  {"play_res_x": 1080, "play_res_y": 1080, "font_size": 56, "outline": 3.5, "margin_v": 80, "margin_lr": 30}
    }
}
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from itertools import product
from pathlib import Path


def find_videos(directory: str) -> list[dict]:
    """Find video files in a directory, sorted by name."""
    video_extensions = {'.mov', '.mp4', '.avi', '.mkv', '.webm', '.m4v'}
    videos = []
    for f in sorted(Path(directory).iterdir()):
        if f.suffix.lower() in video_extensions and not f.name.startswith('.'):
            # Extract number from filename for sorting
            nums = re.findall(r'\((\d+)\)', f.name)
            num = int(nums[-1]) if nums else 0
            videos.append({'path': str(f), 'name': f.stem, 'num': num})
    videos.sort(key=lambda x: x['num'])
    return videos


def concat_videos(hook_path: str, body_path: str, cta_path: str, output_path: str) -> bool:
    """Concatenate 3 videos without re-encoding."""
    concat_file = output_path + '.concat.txt'
    with open(concat_file, 'w') as f:
        f.write(f"file '{hook_path}'\n")
        f.write(f"file '{body_path}'\n")
        f.write(f"file '{cta_path}'\n")

    result = subprocess.run(
        ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_file, '-c', 'copy', output_path],
        capture_output=True, text=True
    )
    os.remove(concat_file)
    return result.returncode == 0


def extract_audio(video_path: str, wav_path: str) -> bool:
    """Extract audio as 16kHz mono WAV for Whisper."""
    result = subprocess.run(
        ['ffmpeg', '-y', '-i', video_path, '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le', wav_path],
        capture_output=True, text=True
    )
    return result.returncode == 0


def transcribe(wav_path: str, output_prefix: str, model_path: str, language: str = 'pt') -> str | None:
    """Transcribe audio with Whisper, returns path to .srt file."""
    result = subprocess.run(
        ['whisper-cli', '-m', model_path, '-l', language, '-osrt',
         '--max-len', '40', '--split-on-word', '-of', output_prefix, wav_path],
        capture_output=True, text=True
    )
    srt_path = output_prefix + '.srt'
    if result.returncode == 0 and os.path.exists(srt_path):
        return srt_path
    return None


def parse_srt(srt_path: str) -> list[dict]:
    """Parse SRT file into list of {start, end, text} dicts."""
    entries = []
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()

    blocks = re.split(r'\n\n+', content)
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            time_match = re.match(r'(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{3})', lines[1])
            if time_match:
                start = time_match.group(1).replace(',', '.')
                end = time_match.group(2).replace(',', '.')
                text = ' '.join(lines[2:]).strip()
                entries.append({'start': start, 'end': end, 'text': text})
    return entries


def time_to_ass(time_str: str) -> str:
    """Convert SRT time (HH:MM:SS.mmm) to ASS time (H:MM:SS.cc)."""
    parts = time_str.replace(',', '.').split(':')
    h, m = int(parts[0]), int(parts[1])
    s_parts = parts[2].split('.')
    s = int(s_parts[0])
    ms = int(s_parts[1]) if len(s_parts) > 1 else 0
    cs = ms // 10  # centiseconds
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def break_line_for_vertical(text: str) -> str:
    """Break text into 2 roughly equal lines for vertical video."""
    words = text.split()
    if len(words) <= 3:
        return text
    mid = len(text) // 2
    best_break = 0
    best_diff = len(text)
    pos = 0
    for i, word in enumerate(words[:-1]):
        pos += len(word) + 1
        diff = abs(pos - mid)
        if diff < best_diff:
            best_diff = diff
            best_break = i + 1
    line1 = ' '.join(words[:best_break])
    line2 = ' '.join(words[best_break:])
    return f"{line1}\\N{line2}"


def generate_ass(srt_entries: list[dict], config: dict, format_key: str) -> str:
    """Generate ASS subtitle content for a specific format."""
    style = config.get('subtitle_style', {})
    params = config.get('format_params', {})[format_key]
    needs_breaks = format_key == '9x16'

    font = style.get('font', 'Arial Black')
    bold = -1 if style.get('bold', True) else 0
    primary = style.get('primary_color', '&H00FFFFFF')
    outline_color = style.get('outline_color', '&H00000000')
    back_color = style.get('back_color', '&H80000000')
    border_style = style.get('border_style', 1)
    shadow = style.get('shadow', 0)
    alignment = style.get('alignment', 2)

    font_size = params['font_size']
    outline = params['outline']
    margin_v = params['margin_v']
    margin_lr = params['margin_lr']

    header = f"""[Script Info]
Title: Video Subtitles {format_key}
ScriptType: v4.00+
PlayResX: {params['play_res_x']}
PlayResY: {params['play_res_y']}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font},{font_size},{primary},&H000000FF,{outline_color},{back_color},{bold},0,0,0,100,100,0,0,{border_style},{outline},{shadow},{alignment},{margin_lr},{margin_lr},{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for entry in srt_entries:
        start = time_to_ass(entry['start'])
        end = time_to_ass(entry['end'])
        text = entry['text']
        if needs_breaks:
            text = break_line_for_vertical(text)
        events.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")

    return header + '\n'.join(events) + '\n'


def render_format(input_video: str, ass_content: str, output_path: str, format_key: str) -> bool:
    """Render a specific aspect ratio with burned subtitles."""
    # Write ASS file
    ass_path = output_path + '.ass'
    with open(ass_path, 'w', encoding='utf-8') as f:
        f.write(ass_content)

    # Build ffmpeg filter
    crop_map = {
        '16x9': 'scale=1920:1080',
        '9x16': 'crop=ih*9/16:ih,scale=1080:1920',
        '4x5': 'crop=ih*4/5:ih,scale=1080:1350',
        '1x1': 'crop=ih:ih,scale=1080:1080',
    }
    vf = f"{crop_map[format_key]},ass={ass_path}"

    result = subprocess.run(
        ['ffmpeg', '-y', '-i', input_video, '-vf', vf,
         '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', '-pix_fmt', 'yuv420p',
         '-c:a', 'aac', '-b:a', '192k', output_path],
        capture_output=True, text=True
    )
    # Clean up ASS file
    if os.path.exists(ass_path):
        os.remove(ass_path)
    return result.returncode == 0


def render_nosub(input_video: str, output_path: str, format_key: str) -> bool:
    """Render a specific aspect ratio WITHOUT subtitles."""
    crop_map = {
        '16x9': 'scale=1920:1080',
        '9x16': 'crop=ih*9/16:ih,scale=1080:1920',
        '4x5': 'crop=ih*4/5:ih,scale=1080:1350',
        '1x1': 'crop=ih:ih,scale=1080:1080',
    }

    result = subprocess.run(
        ['ffmpeg', '-y', '-i', input_video, '-vf', crop_map[format_key],
         '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', '-pix_fmt', 'yuv420p',
         '-c:a', 'aac', '-b:a', '192k', output_path],
        capture_output=True, text=True
    )
    return result.returncode == 0


def process_combination(hook: dict, body: dict, cta: dict, config: dict, output_dir: str) -> dict:
    """Process a single Hook+Body+CTA combination."""
    name = f"VARIACAO_H{hook['num']}_B{body['num']}_C{cta['num']}"
    results = {'name': name, 'files': {}, 'errors': []}

    # Step 1: Concatenate
    concat_path = os.path.join(output_dir, f"{name}_raw.mov")
    if not concat_videos(hook['path'], body['path'], cta['path'], concat_path):
        results['errors'].append('Concatenation failed')
        return results

    formats = config.get('formats', ['16x9'])
    do_subs = config.get('subtitles', True)
    srt_entries = None

    # Step 2: Transcribe (if subtitles enabled)
    if do_subs:
        wav_path = os.path.join(output_dir, f"{name}.wav")
        srt_prefix = os.path.join(output_dir, name)
        if extract_audio(concat_path, wav_path):
            srt_path = transcribe(wav_path, srt_prefix, config['whisper_model'], config.get('language', 'pt'))
            if srt_path:
                srt_entries = parse_srt(srt_path)
                os.remove(srt_path)
            else:
                results['errors'].append('Transcription failed')
            os.remove(wav_path)
        else:
            results['errors'].append('Audio extraction failed')

    # Step 3: Render each format
    for fmt in formats:
        output_path = os.path.join(output_dir, f"{name}_{fmt}_SUB.mov" if do_subs and srt_entries else f"{name}_{fmt}.mov")

        if do_subs and srt_entries:
            ass_content = generate_ass(srt_entries, config, fmt)
            success = render_format(concat_path, ass_content, output_path, fmt)
        else:
            success = render_nosub(concat_path, output_path, fmt)

        if success:
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            results['files'][fmt] = {'path': output_path, 'size_mb': round(size_mb, 1)}
        else:
            results['errors'].append(f'Render failed for {fmt}')

    # Clean up raw concat
    if os.path.exists(concat_path):
        os.remove(concat_path)

    return results


def main():
    parser = argparse.ArgumentParser(description='Video Combiner — Batch processor')
    parser.add_argument('--config', help='Path to JSON config file')
    parser.add_argument('--hooks-dir', help='Path to hooks directory')
    parser.add_argument('--bodys-dir', help='Path to bodys directory')
    parser.add_argument('--ctas-dir', help='Path to CTAs directory')
    parser.add_argument('--output-dir', help='Path to output directory')
    parser.add_argument('--formats', nargs='+', default=['16x9', '9x16', '4x5'], help='Output formats')
    parser.add_argument('--no-subs', action='store_true', help='Skip subtitle generation')
    parser.add_argument('--language', default='pt', help='Audio language (default: pt)')
    parser.add_argument('--test', action='store_true', help='Process only first combination as test')
    parser.add_argument('--dry-run', action='store_true', help='Show combinations without processing')
    args = parser.parse_args()

    # Load config
    if args.config:
        with open(args.config) as f:
            config = json.load(f)
    else:
        config = {
            'hooks_dir': args.hooks_dir,
            'bodys_dir': args.bodys_dir,
            'ctas_dir': args.ctas_dir,
            'output_dir': args.output_dir,
            'formats': args.formats,
            'subtitles': not args.no_subs,
            'language': args.language,
            'whisper_model': os.path.expanduser('~/.local/share/whisper-models/ggml-medium.bin'),
            'subtitle_style': {
                'font': 'Arial Black',
                'bold': True,
                'primary_color': '&H00FFFFFF',
                'outline_color': '&H00000000',
                'back_color': '&H80000000',
                'border_style': 1,
                'shadow': 0,
                'alignment': 2,
            },
            'format_params': {
                '16x9': {'play_res_x': 1920, 'play_res_y': 1080, 'font_size': 72, 'outline': 4, 'margin_v': 60, 'margin_lr': 40},
                '9x16': {'play_res_x': 1080, 'play_res_y': 1920, 'font_size': 58, 'outline': 3.5, 'margin_v': 180, 'margin_lr': 30},
                '4x5':  {'play_res_x': 1080, 'play_res_y': 1350, 'font_size': 58, 'outline': 3.5, 'margin_v': 100, 'margin_lr': 30},
                '1x1':  {'play_res_x': 1080, 'play_res_y': 1080, 'font_size': 56, 'outline': 3.5, 'margin_v': 80, 'margin_lr': 30},
            }
        }

    # Expand paths
    config['whisper_model'] = os.path.expanduser(config.get('whisper_model', '~/.local/share/whisper-models/ggml-medium.bin'))

    # Discover videos
    hooks = find_videos(config['hooks_dir'])
    bodys = find_videos(config['bodys_dir'])
    ctas = find_videos(config['ctas_dir'])

    print(f"\n=== Video Combiner ===")
    print(f"Hooks: {len(hooks)} videos")
    print(f"Bodys: {len(bodys)} videos")
    print(f"CTAs:  {len(ctas)} videos")

    combinations = list(product(hooks, bodys, ctas))
    total = len(combinations)
    formats_count = len(config['formats'])
    print(f"Total combinations: {total}")
    print(f"Output formats: {', '.join(config['formats'])}")
    print(f"Total output files: {total * formats_count}")
    print(f"Subtitles: {'Yes' if config.get('subtitles') else 'No'}")

    if args.dry_run:
        print("\n--- Dry Run (first 10) ---")
        for h, b, c in combinations[:10]:
            print(f"  VARIACAO_H{h['num']}_B{b['num']}_C{c['num']}")
        if total > 10:
            print(f"  ... and {total - 10} more")
        return

    # Create output directory
    output_dir = config.get('output_dir', './output')
    os.makedirs(output_dir, exist_ok=True)

    # Process
    if args.test:
        combinations = combinations[:1]
        print("\n--- TEST MODE: Processing 1 combination ---")

    manifest = []
    for i, (h, b, c) in enumerate(combinations, 1):
        print(f"\n[{i}/{len(combinations)}] Processing H{h['num']} + B{b['num']} + C{c['num']}...")
        result = process_combination(h, b, c, config, output_dir)
        manifest.append(result)

        if result['errors']:
            print(f"  ERRORS: {', '.join(result['errors'])}")
        for fmt, info in result['files'].items():
            print(f"  {fmt}: {info['size_mb']} MB — {os.path.basename(info['path'])}")

    # Write manifest
    manifest_path = os.path.join(output_dir, 'manifest.json')
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest saved to: {manifest_path}")

    # Summary
    total_files = sum(len(r['files']) for r in manifest)
    total_errors = sum(len(r['errors']) for r in manifest)
    total_size = sum(info['size_mb'] for r in manifest for info in r['files'].values())
    print(f"\n=== Summary ===")
    print(f"Files created: {total_files}")
    print(f"Total size: {total_size:.1f} MB")
    print(f"Errors: {total_errors}")


if __name__ == '__main__':
    main()
