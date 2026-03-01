#!/usr/bin/env python3
"""
Generate ASS subtitle files with dynamic word-by-word yellow highlighting.

Reads a word-level transcript JSON and produces an ASS file where:
- Words are grouped in chunks of 3-5
- The active word is highlighted in yellow with 110% scale
- All text is in UPPERCASE
- Font: Arial Black, size 52-58
- Position: bottom center with configurable margin

Usage:
    python3 generate_ass.py \
        --transcript transcript.json \
        --output hook.ass \
        --start 1726.07 \
        --end 1729.11 \
        --font-size 58 \
        --margin-v 180

Transcript JSON format (array of words):
    [
        {"text": "word", "start": 0.0, "end": 0.3},
        {"text": "another", "start": 0.35, "end": 0.7},
        ...
    ]
"""

import argparse
import json
import sys
import re


def format_ass_time(seconds: float) -> str:
    """Convert seconds to ASS time format: H:MM:SS.CC"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def group_words(words: list, max_per_group: int = 5, pause_threshold: float = 0.35) -> list:
    """
    Group words into display chunks of 3-5 words.
    Breaks on:
    - Max words per group reached
    - Pause > threshold between words
    - Punctuation (. ? ! ,)
    """
    groups = []
    current_group = []

    for i, word in enumerate(words):
        current_group.append(word)

        should_break = False

        # Max words reached
        if len(current_group) >= max_per_group:
            should_break = True

        # Punctuation at end of word
        if re.search(r'[.?!]$', word['text']):
            should_break = True

        # Comma — break if we have at least 2 words
        if word['text'].endswith(',') and len(current_group) >= 2:
            should_break = True

        # Pause before next word
        if not should_break and i + 1 < len(words):
            gap = words[i + 1]['start'] - word['end']
            if gap > pause_threshold and len(current_group) >= 2:
                should_break = True

        if should_break:
            groups.append(current_group)
            current_group = []

    # Remaining words
    if current_group:
        if groups and len(current_group) <= 2:
            # Merge small remainder with last group
            groups[-1].extend(current_group)
        else:
            groups.append(current_group)

    return groups


def generate_highlight_line(group_words_list: list, active_idx: int) -> str:
    """
    Generate ASS text line with the active word highlighted in yellow.
    Uses override tags for color and scale.
    """
    parts = []
    for i, word in enumerate(group_words_list):
        text = word['text'].upper()
        # Clean up any existing formatting
        text = text.strip()
        if not text:
            continue

        if i == active_idx:
            # Active word: yellow + 110% scale
            parts.append(
                r"{\c&H00FFFF&\fscx110\fscy110}" +
                text +
                r"{\c&HFFFFFF&\fscx100\fscy100}"
            )
        else:
            parts.append(text)

    return " ".join(parts)


def generate_ass(
    words: list,
    start_time: float,
    end_time: float,
    font_size: int = 58,
    margin_v: int = 180,
    font_name: str = "Arial Black",
) -> str:
    """Generate complete ASS subtitle content."""

    # Filter words within time range
    filtered = [w for w in words if w['end'] > start_time and w['start'] < end_time]

    if not filtered:
        print(f"WARNING: No words found between {start_time}s and {end_time}s", file=sys.stderr)
        # Return empty ASS file
        return _ass_header(font_name, font_size, margin_v) + "\n"

    # Adjust timestamps relative to clip start (clip starts at 0:00)
    for w in filtered:
        w['rel_start'] = max(0, w['start'] - start_time)
        w['rel_end'] = w['end'] - start_time

    # Group words
    groups = group_words(filtered)

    # Generate ASS header
    header = _ass_header(font_name, font_size, margin_v)

    # Generate events
    events = []
    for group in groups:
        for active_idx, active_word in enumerate(group):
            line_text = generate_highlight_line(group, active_idx)
            t_start = format_ass_time(active_word['rel_start'])
            t_end = format_ass_time(active_word['rel_end'])
            events.append(
                f"Dialogue: 0,{t_start},{t_end},Default,,0,0,0,,{line_text}"
            )

    return header + "\n".join(events) + "\n"


def _ass_header(font_name: str, font_size: int, margin_v: int) -> str:
    """Generate ASS file header with style definition."""
    return f"""[Script Info]
Title: Viral Cut Subtitles
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},&H00FFFFFF,&H0000FFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,4.5,0,2,50,50,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def main():
    parser = argparse.ArgumentParser(
        description="Generate ASS subtitles with dynamic word highlighting"
    )
    parser.add_argument(
        "--transcript", required=True,
        help="Path to transcript JSON file (array of {text, start, end})"
    )
    parser.add_argument(
        "--output", required=True,
        help="Output ASS file path"
    )
    parser.add_argument(
        "--start", type=float, required=True,
        help="Clip start time in seconds"
    )
    parser.add_argument(
        "--end", type=float, required=True,
        help="Clip end time in seconds"
    )
    parser.add_argument(
        "--font-size", type=int, default=58,
        help="Subtitle font size (default: 58)"
    )
    parser.add_argument(
        "--margin-v", type=int, default=280,
        help="Vertical margin from bottom (default: 280 — safe above Instagram UI)"
    )
    parser.add_argument(
        "--font-name", default="Arial Black",
        help="Font name (default: Arial Black)"
    )

    args = parser.parse_args()

    # Load transcript
    with open(args.transcript, 'r', encoding='utf-8') as f:
        transcript = json.load(f)

    # Handle different transcript formats
    words = []
    if isinstance(transcript, list):
        if transcript and isinstance(transcript[0], dict):
            if 'text' in transcript[0] and 'start' in transcript[0]:
                words = transcript
            elif 'word' in transcript[0]:
                # Alternative key name
                words = [
                    {'text': w.get('word', w.get('text', '')),
                     'start': w['start'],
                     'end': w['end']}
                    for w in transcript
                ]
    elif isinstance(transcript, dict):
        # Whisper format: {"segments": [{"words": [...]}]}
        if 'segments' in transcript:
            for seg in transcript['segments']:
                for w in seg.get('words', []):
                    words.append({
                        'text': w.get('word', w.get('text', '')).strip(),
                        'start': w['start'],
                        'end': w['end']
                    })
        # Simple format: {"words": [...]}
        elif 'words' in transcript:
            words = transcript['words']

    if not words:
        print("ERROR: Could not parse transcript. Expected array of {text, start, end}", file=sys.stderr)
        sys.exit(1)

    # Generate ASS content
    ass_content = generate_ass(
        words=words,
        start_time=args.start,
        end_time=args.end,
        font_size=args.font_size,
        margin_v=args.margin_v,
        font_name=args.font_name,
    )

    # Write output
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(ass_content)

    print(f"Generated: {args.output}")


if __name__ == "__main__":
    main()
