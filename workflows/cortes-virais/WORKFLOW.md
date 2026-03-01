---
name: Cortes Virais
description: Transforma entrevistas/podcasts do YouTube em 5-7 cortes verticais (9:16) de 60-90s prontos para Reels, Shorts e TikTok — com hook teaser e legendas dinâmicas
icon: "🎬"
---

# Cortes Virais — Reels & Shorts de Alto Engajamento

Transforma uma entrevista/podcast longo do YouTube em **5-7 cortes verticais (9:16) de 60-90 segundos**, com **hook teaser** nos primeiros 3s e **legendas dinâmicas** palavra-por-palavra com destaque amarelo.

## When to Use

- User says `/cortes-virais` or asks to create vertical cuts from a YouTube video
- User wants to create Reels, Shorts, or TikToks from a long interview/podcast
- User provides a YouTube URL and wants viral clips extracted

---

## Sources & Integracoes

Ao ativar este workflow, verifique quais sources estao disponiveis na sessao (listadas em `<sources>` no system prompt) e adapte o fluxo. **Nunca referencie uma integracao que o usuario nao tem configurada.**

**Source de AI com vision e transcricao** (ex: `googleai`, `openai`, ou qualquer source com capacidade de `analyze_image`, `summarize_url`, `transcribe_media`):
- **Com source de AI**: Transcrever diretamente da URL do YouTube (sem download), analise visual de frames para crop inteligente, QC automatizado com visao
- **Sem source de AI**: Usar Whisper local para transcricao rough (requer download completo), crop manual ou center-crop, QC manual pelo usuario

**Source de web scraping** (ex: `apify`, ou qualquer source com capacidade de extrair transcricoes do YouTube):
- Fallback para transcricao rough quando source de AI nao esta disponivel
- Buscar captions automaticas do YouTube

**Source de armazenamento em nuvem** (ex: `google-workspace`, `google-drive`, ou qualquer source com acesso a Drive/storage):
- Oferecer upload dos cortes finais para Drive/storage
- Na Phase 5, perguntar: "Quer que eu faca upload dos cortes para o Drive?"
- **Se NAO existe**: Entregar apenas caminhos locais, nao mencionar upload

**Ferramentas locais obrigatorias** (nao sao sources — sao CLI tools):
- `yt-dlp`, `ffmpeg`, `ffprobe`, `python3`, `whisper-cli`, `ggml-medium.bin`
- Phase 0 valida todas antes de iniciar

---

## Sub-Agent Strategy

This workflow processes large media files and runs multi-step pipelines. **Use Task sub-agents aggressively** to optimize cost, speed, and context management.

### Why Sub-Agents Matter Here

| Problem | Without sub-agents | With sub-agents |
|---------|--------------------|-----------------|
| Transcript analysis (5000+ words) | Floods main context, expensive Opus tokens | Sonnet agent reads transcript, returns only cut definitions |
| Visual frame analysis (6 cuts x 5-8 frames) | 30-48 analyze_image calls clogging main thread | Parallel agents per cut, main context receives only crop_profile.json |
| ffmpeg processing (6 cuts) | Sequential, slow, errors pollute context | Parallel bash agents, main gets only success/fail + file paths |
| QC frame validation | 12-18 image analysis calls in main | Batch in sub-agent, main gets pass/fail summary |

### Model Selection Guide

| Task | Model | Reason |
|------|-------|--------|
| Rough transcript for cut selection | **sonnet** | Reads summarize_url output, proposes cuts — structured JSON |
| Per-segment transcription (whisper) | **haiku** | Runs transcribe_segment.sh — pure bash execution |
| Scene detection + crop analysis (analyze_image calls) | **sonnet** | Two-pass visual analysis — scene classification + detailed per-scene crop |
| Crop preview rendering (ffmpeg) | **haiku** | Pure ffmpeg commands to render 1080x1920 preview images |
| ffmpeg command execution | **haiku** | Just running bash commands — cheapest model, no reasoning needed |
| Cut processing (process_cut.sh) | **haiku** | Bash execution with no creative decisions |
| QC validation | **sonnet** | Needs to interpret image analysis results and make reframe decisions |
| Camera switch detection logic | **sonnet** | Comparing frame analyses and making crop map decisions |
| User-facing summary + presentation | **opus** (main) | Main context handles user interaction and final decisions only |

### Parallelism Map

```
Phase 0:  Sequential (fast checks, no sub-agents needed)
Phase 1:  Setup only — NO download yet
Phase 2:  Single MCP call (source de AI: summarize_url) — transcribes from YouTube URL, no download
Phase 3:  Sub-agent (sonnet) for transcript analysis + cut selection + scoring
Phase 3:  Sub-agent (haiku) for timestamp refinement (boundary snapping via whisper-medium)
Phase 3a: Download ONLY needed segments (yt-dlp --download-sections) — 75% less bandwidth
Phase 3b: PARALLEL sub-agents (sonnet) — 1 per cut for visual frame analysis
Phase 4:  Sub-agent (haiku) for per-segment whisper-medium transcription (sequential — GPU-bound)
Phase 4:  PARALLEL sub-agents (haiku) — 2-3 cuts per agent for ffmpeg processing
Phase 5:  PARALLEL sub-agents (sonnet) — 1 per cut for QC frame validation
```

### Dispatch Pattern

When launching sub-agents, follow this pattern:

1. **Bundle context tightly** — Give the sub-agent only the data it needs (file paths, cut JSON, specific frames). Never dump the full transcript or full conversation.
2. **Expect structured output** — Tell the agent to return JSON or a specific format. Don't let it narrate.
3. **Launch in parallel** — Use a single message with multiple Task tool calls for independent work.
4. **Keep main context clean** — The main thread (Opus) should only see: user messages, sub-agent results (JSON), and decision points. Never raw ffmpeg logs or raw transcripts.

**Example: Parallel visual analysis for 6 cuts**
```
# Single message with 6 Task calls:
Task(sonnet): "Analyze frames for corte1: {frame paths}. Return crop_map JSON."
Task(sonnet): "Analyze frames for corte2: {frame paths}. Return crop_map JSON."
Task(sonnet): "Analyze frames for corte3: {frame paths}. Return crop_map JSON."
Task(sonnet): "Analyze frames for corte4: {frame paths}. Return crop_map JSON."
Task(sonnet): "Analyze frames for corte5: {frame paths}. Return crop_map JSON."
Task(sonnet): "Analyze frames for corte6: {frame paths}. Return crop_map JSON."
# All 6 run simultaneously. Main receives 6 JSON results.
```

**Example: Parallel ffmpeg processing for 6 cuts**
```
# Single message with 3 Task calls (2 cuts each):
Task(haiku): "Run process_cut.sh for corte1 and corte2. Return file paths and durations."
Task(haiku): "Run process_cut.sh for corte3 and corte4. Return file paths and durations."
Task(haiku): "Run process_cut.sh for corte5 and corte6. Return file paths and durations."
```

---

## Phase 0: Environment & Source Validation

**Goal**: Verify all dependencies and AI sources BEFORE starting any work. This avoids wasted time downloading a 2GB video only to discover transcription tools are unavailable.

### Step 0a — Validate CLI Tools

Run all checks in parallel:

```bash
which yt-dlp && yt-dlp --version
which ffmpeg && ffmpeg -version | head -1
which ffprobe && ffprobe -version | head -1
python3 --version
which whisper-cli && whisper-cli --version 2>&1 | head -1
ls -la ~/.local/share/whisper-models/ggml-medium.bin 2>/dev/null || echo "MISSING: ggml-medium.bin"
```

If any tool is missing, install before proceeding:

| Tool | Check | Install |
|------|-------|---------|
| yt-dlp | `which yt-dlp` | `brew install yt-dlp` |
| ffmpeg | `which ffmpeg` | `brew install ffmpeg` |
| ffprobe | `which ffprobe` | (comes with ffmpeg) |
| Python 3 | `python3 --version` | `brew install python` |
| whisper-cli | `which whisper-cli` | `brew install whisper-cpp` |
| ggml-medium.bin | `ls ~/.local/share/whisper-models/ggml-medium.bin` | `curl -L "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin" -o ~/.local/share/whisper-models/ggml-medium.bin` |

> **CRITICAL**: The `ggml-medium.bin` model (1.5GB) is essential for subtitle quality. The `base` model produces systematic errors on proper nouns (CEO → "se ou"). Always verify the medium model is downloaded before starting.

### Step 0b — Validate AI Sources (Transcription & Vision)

Check which AI sources are available in the current session. This determines the transcription strategy and visual analysis capability.

**Check the `<sources>` tag in the session state.** Look for:

| Tool | Purpose | Priority |
|------|---------|----------|
| **whisper-cli + ggml-medium.bin** (local) | Per-segment word-level transcription for subtitles | **P0 — Primary** |
| **source de AI** `analyze_image` (ex: `googleai`, `openai`) | Visual frame analysis for intelligent crop | **P0 — Primary** |
| **source de AI** `summarize_url` (ex: `googleai`, `openai`) | Rough transcript from YouTube URL for cut selection | **P1 — For cut selection** |
| **source de AI** `transcribe_media` (ex: `googleai`, `openai`) | Short segment re-transcription if Whisper fails | **P2 — Fallback** |
| **source de web scraping** YouTube transcript actors (ex: `apify`) | Get captions for cut selection | **P3 — Fallback** |

> **LESSON LEARNED**: `transcribe_media` via source de AI pode retornar erros em arquivos de audio grandes (>20MB). So funciona de forma confiavel em segmentos curtos (<5 min). Whisper medium localmente com Metal GPU e mais rapido e confiavel para transcricao por segmento.

**Decision matrix:**

```
TRANSCRIPTION (for subtitle generation):
  IF whisper-cli exists AND ggml-medium.bin exists:
    → subtitle_method = "whisper_medium_local"  (ALWAYS PREFERRED)
  ELSE:
    → INSTALL whisper-cli + download ggml-medium.bin before proceeding
    → This is a HARD REQUIREMENT for subtitle quality

ROUGH TRANSCRIPT (for cut selection only):
  IF existe source de AI com capacidade de vision e transcricao (ex: `googleai`, `openai`, ou qualquer source com tools como `analyze_image`, `summarize_url`, `transcribe_media`):
    → rough_transcript_method = "ai_source_summarize_url"
  ELSE IF existe source de web scraping/automacao (ex: `apify`, ou qualquer source com capacidade de buscar transcricoes do YouTube):
    → rough_transcript_method = "scraping_source_youtube_transcript"
  ELSE:
    → rough_transcript_method = "whisper_base_local" (fast, lower quality OK)

VISION (for crop analysis):
  IF existe source de AI com capacidade de vision e transcricao (ex: `googleai`, `openai`, ou qualquer source com tools como `analyze_image`, `summarize_url`, `transcribe_media`):
    → vision_available = true
  ELSE:
    → vision_available = false
    → Warn user: "Running without AI vision — crop will use center-crop heuristic"
```

Save the resolved capabilities to `{output-dir}/capabilities.json`:
```json
{
  "subtitle_method": "whisper_medium_local",
  "rough_transcript_method": "ai_source_summarize_url",
  "vision_available": true,
  "ai_vision_active": true,
  "web_scraping_active": true,
  "whisper_cli_installed": true,
  "whisper_medium_model": "~/.local/share/whisper-models/ggml-medium.bin",
  "tools": {
    "yt_dlp": "2024.12.13",
    "ffmpeg": "7.1.1",
    "python": "3.11.x",
    "whisper_cli": "0.4.3"
  }
}
```

**Report to user** with a quick summary:

```jsonrender
{"root":"c","elements":{"c":{"type":"Card","props":{"title":"Environment Check","subtitle":"Cortes Virais"},"children":["g"]},"g":{"type":"Grid","props":{"columns":2},"children":["m1","m2","m3","m4"]},"m1":{"type":"Stat","props":{"label":"Transcription","value":"AI Source","description":"Word-level timestamps via transcribe_media"}},"m2":{"type":"Stat","props":{"label":"Visual Analysis","value":"Active","description":"analyze_image for intelligent crop"}},"m3":{"type":"Stat","props":{"label":"CLI Tools","value":"All OK","description":"yt-dlp, ffmpeg, ffprobe, Python 3"}},"m4":{"type":"Stat","props":{"label":"Fallback","value":"Whisper","description":"Local fallback if AI source fails"}}}}
```

---

## Structure of Each Cut

| Part | Duration | Description |
|------|----------|-------------|
| **HOOK (Teaser)** | 2-3.5s | The MOST controversial/impactful phrase from the segment. Works as a teaser — a hard cut from another moment. |
| **BODY** | 57-88s | The complete segment, starting from the natural beginning. Does NOT continue from where the hook ended. |
| **TOTAL** | 60-90s | Hook + Body concatenated. First 3 seconds are high-impact. |

> **KEY CONCEPT: Hook as Teaser**
> The hook is NOT the beginning of the segment. It's a hard cut from the "money shot" — the most provocative phrase. After the hook, the video goes back to the beginning of the segment like a movie teaser. This guarantees the first 3 seconds are instantly engaging.

---

## Phase 1: Setup

### Step 1 — Receive the YouTube URL

Get the YouTube URL from the user. Optionally they may specify:
- Focus on a specific guest (name + description)
- Number of cuts (default: 5-7)
- Language for subtitles (default: Portuguese Brazilian)
- Any specific moments they want included

### Step 2 — Create Output Directory

Create a working directory inside the session:
```
{sessionPath}/cortes-virais/{video-slug}/
```

Where `{video-slug}` is derived from the video title (lowercase, hyphens, no special chars).

> **NO DOWNLOAD YET.** The video is NOT downloaded in Phase 1. A source de AI (se disponivel) transcreve diretamente da URL do YouTube. We only download the specific segments we need AFTER selecting cuts (Step 7a). This saves 60-80% of download time and disk space for long videos.

---

## Phase 2: Transcription from URL (No Download Needed)

**Goal**: Get a sentence-level transcript with timestamps directly from the YouTube URL. No video download required — source de AI (ex: Google AI) reads the video from the URL. This transcript is used ONLY for cut selection; final subtitles come from per-segment Whisper medium in Phase 4.

> **KEY INSIGHT**: The transcript comes BEFORE the download. Uma source de AI com `summarize_url` pode transcrever diretamente da URL do YouTube. We only download the specific segments we need after selecting cuts — saving 60-80% bandwidth on long podcasts.

### Step 5 — Sentence-Level Transcript for Cut Selection

The goal here is sentence-level timestamps for content analysis and cut boundary definition. Word-level is not needed — Whisper medium handles that later for the selected cuts only.

#### Method 1: Source de AI — `summarize_url` (Fastest — requires source de AI ativa com esta capacidade)

```
summarize_url({
  url: "{youtube-url}",
  prompt: "Transcreva este vídeo FRASE POR FRASE em português brasileiro, com timestamp no início de cada frase.

Formato OBRIGATÓRIO — uma frase por linha:
[MM:SS] Frase exata dita pelo speaker.
[MM:SS] Próxima frase.

Regras:
- Cada linha = UMA frase completa (até o ponto final, interrogação, ou pausa longa)
- Timestamp [MM:SS] no início de CADA frase — sem exceção
- Transcrição literal — não resuma, não parafraseie, não omita nada
- Inclua TUDO: falas do entrevistador, do entrevistado, interjeições, risos
- Se houver mais de um speaker, indique quem fala quando mudar: [MM:SS] (Entrevistador) Frase...
- Não agrupe múltiplas frases sob um único timestamp
- Vá do início ao fim do vídeo, sem pular trechos

Preciso da transcrição completa para identificar os melhores momentos para cortes de Reels."
})
```

**Advantages**: No download needed, fast, handles any length. Sentence-level timestamps are precise enough to define cut boundaries (±2-3s) which get refined in Step 6b.
**Limitations**: No word-level timestamps — that's fine, Whisper medium handles word-level in Phase 4 only for the selected cuts.

#### Method 2: Source de web scraping — YouTube Transcript (requires source de web scraping ativa)

If source de AI is unavailable or the URL approach fails:

```
search-actors({ query: "youtube transcript captions" })
call-actor({ actorId: "{best-actor-id}", input: { "url": "{youtube-url}", "language": "pt" } })
```

**Advantages**: Gets YouTube's auto-captions with sentence-level timestamps.

#### Method 3: Whisper-cli base (local — REQUIRES full download)

If no AI sources are available, we MUST download the full video first (this is the only method that requires it):

```bash
# Download full video (fallback only — Methods 1 and 2 don't need this)
bash {workflow-dir}/scripts/download.sh "{youtube-url}" "{output-dir}"

# Quick transcription with base model (fast but lower quality)
whisper-cli -m ~/.local/share/whisper-models/ggml-base.bin \
  -l pt -oj -f "{output-dir}/audio.wav" -of "{output-dir}/transcript_rough"
```

> **NOTE**: If Method 3 was used (full download), skip Step 7a (segment download) — you already have the full video as `original.mp4`.

### Step 5e — Save Rough Transcript

Save the rough transcript as `{output-dir}/transcript_rough.txt` (or `.json` if structured).

This is used ONLY for Phase 3 (cut selection). The final subtitles come from per-segment transcription in Phase 4.

---

## Phase 3: Analysis & Cut Selection

### Step 6 — Analyze Content and Select Cuts

> **SUB-AGENT**: Dispatch a `Task(model: sonnet, subagent_type: general-purpose)` to analyze the transcript. The transcript can be 5000+ words — too large and expensive for the main Opus context. The sub-agent reads transcript.json, applies the selection criteria below, and returns ONLY the cuts JSON array. Main context never sees the raw transcript.

Read the full transcript and identify 5-7 high-engagement segments.

#### Platform Metrics — The Selection Must Optimize For These (in order)

| # | Metric | What it means | What drives it |
|---|--------|---------------|----------------|
| 1 | **3-second retention** | % of viewers who don't swipe away | Hook quality — the first 3s must create an irresistible "open loop" |
| 2 | **Like/view ratio** | Emotional resonance | Segments that trigger identification, "aha moments", or admiration |
| 3 | **Share/view ratio** | Virality | Controversy, polarization, or utility so high people screenshot + forward |

#### Hook Selection — BE AGGRESSIVE

The hook is the single most important element. A mediocre body with a killer hook outperforms a great body with a weak hook.

**Hook archetypes that retain (ranked by effectiveness):**

| Archetype | Example | Why it works |
|-----------|---------|--------------|
| **Contradiction** | "Eu era de esquerda e hoje..." | Breaks expectation — viewer needs resolution |
| **Bold claim** | "Toda empresa deveria demitir o RH" | Outrageous enough to demand context |
| **Shocking number** | "R$50 milhões de prejuízo" | Concrete, visceral, makes viewer say "como?!" |
| **Direct confrontation** | "Você está completamente errado" | Conflict = attention. Viewer picks a side |
| **Vulnerability** | "Eu quase quebrei a empresa" | Humanizes + creates tension |
| **Status violation** | "CEO que ganha salário mínimo" | Disrupts social expectations |
| **Unfinished thought** | "O problema do Brasil é que..." (cut) | Classic open loop — forces viewer to stay |

**Hook rules:**
- The hook MUST create an **open loop** — a question the viewer can't answer without watching
- Prefer hooks that are **mid-sentence or mid-thought** — the incompleteness is the retention mechanism
- Audio energy must be HIGH — raised voice, emphasis, fast speech. Flat-energy hooks lose to the next scroll
- If the hook text could be a tweet that gets 10K likes, it's a good hook
- **Test**: Would you stop scrolling for this? If not, it's not good enough. Find a better one.

#### Body Selection — Complete Narratives That Deliver

**Body selection criteria (in priority order):**

1. **Payoff for the hook** — The body MUST deliver on the hook's promise. If the hook says "R$50M de prejuízo", the body must explain how/why
2. **Self-contained arc** — Beginning → development → conclusion in 57-88s. No dangling references to "what I said before"
3. **Emotional escalation** — The segment should build to a climax, not start strong and fade. Energy at 75% of the body should be higher than at 25%
4. **Quotable density** — Segments with 2-3 shareable phrases >> segments with 1. More quotable moments = more like/share potential
5. **Polarization potential** — Prefer opinions that split the audience. Unanimity doesn't generate comments. Controversy does

**What makes a BAD cut (avoid):**
- Generic advice anyone could give ("trabalhe duro", "tenha foco")
- Long preambles before getting to the point
- Segments that need prior context to make sense
- Monotone delivery with no energy variation
- Agreements between interviewer and guest (boring — find disagreements)

#### Scoring Each Cut

For each proposed cut, the sub-agent MUST score it on the three metrics:

```json
[
  {
    "name": "corte1_tema",
    "title": "TITULO DESCRITIVO EM CAPS",
    "hook_start": 1726.07,
    "hook_end": 1729.11,
    "body_start": 1719.56,
    "body_end": 1790.12,
    "hook_text": "The exact text of the hook phrase",
    "body_summary": "Brief description of what this segment covers",
    "scores": {
      "retention_3s": 9,
      "like_ratio": 7,
      "share_ratio": 8,
      "total": 24
    },
    "hook_archetype": "bold_claim",
    "polarization_axis": "Anti-RH provocação — divide quem é de RH vs operação"
  }
]
```

**Scoring rubric (1-10):**

| Score | retention_3s | like_ratio | share_ratio |
|-------|-------------|------------|-------------|
| 9-10 | Impossible to scroll past. Open loop is irresistible | "This changed how I think" | People will DM this to 3+ friends |
| 7-8 | Very strong hook, clear tension | Strong identification or "aha" | Shareable opinion or useful framework |
| 5-6 | Decent hook but predictable | Mildly interesting | Might share if asked |
| 3-4 | Weak hook, no open loop | Generic content | No share impulse |
| 1-2 | Would scroll past immediately | Forgettable | Zero virality |

**Minimum thresholds:**
- Every cut must have `retention_3s >= 7`
- Total score must be >= 20 out of 30
- If no 7 cuts meet this bar, propose fewer cuts but higher quality
- **NEVER pad the list with mediocre cuts just to reach 7** — 4 bangers >> 7 mid

**Rules:**
- Hook: 2-3.5 seconds (the "money shot" phrase)
- Body: 57-88 seconds (complete segment from natural beginning)
- Total: 60-90 seconds
- The hook CAN come from within the body segment or from another moment
- The body starts from the BEGINNING of the segment, not from where the hook ends
- **Rank cuts by total score** — present the highest-scoring first

### Step 6b — Refine Timestamps (Boundary Snapping)

> **WHY THIS MATTERS**: Rough transcript timestamps are paragraph-level — off by 0.5-2s. A hook that starts 0.3s too late misses the first word. A body that ends mid-sentence sounds amateur. Precise boundaries are the difference between "pro edit" and "rough draft".

The goal: snap every start/end point to a **clean audio boundary** — start of a word, end of a breath, or a natural micro-pause.

> **SUB-AGENT**: Use `Task(model: haiku, subagent_type: Bash)` to extract boundary clips and run whisper-medium on them. Returns word-level timestamps for each boundary zone. Then a `Task(model: sonnet)` refines the timestamps using the word data.

#### 6b-1. Extract Boundary Zones

For each cut, extract short audio clips around each proposed boundary point (±3s):

```bash
# For each cut, extract 4 boundary zones:
# 1. Hook start zone (hook_start - 1s to hook_start + 4s)
# 2. Hook end zone (hook_end - 1s to hook_end + 2s)
# 3. Body start zone (body_start - 2s to body_start + 3s)
# 4. Body end zone (body_end - 3s to body_end + 2s)

for boundary in hook_start hook_end body_start body_end; do
  ffmpeg -y -ss {boundary - padding_before} -to {boundary + padding_after} \
    -i "{output-dir}/original.mp4" -vn -acodec pcm_s16le -ar 16000 -ac 1 \
    "{output-dir}/boundary_{name}_{boundary}.wav"
done
```

#### 6b-2. Transcribe Boundary Zones with Whisper Medium

Run whisper-medium on each boundary clip to get exact word timestamps:

```bash
whisper-cli -m ~/.local/share/whisper-models/ggml-medium.bin \
  -l pt -ojf -f "{output-dir}/boundary_{name}_{boundary}.wav" \
  -of "{output-dir}/boundary_{name}_{boundary}"
```

This gives word-level timestamps with ~50ms precision — enough to snap to word boundaries.

#### 6b-3. Snap Rules

Apply these rules to refine each timestamp:

| Boundary | Snap Rule | Rationale |
|----------|-----------|-----------|
| **hook_start** | Snap to **start of the first word** of the hook phrase. If there's a breath/pause 0.1-0.3s before, include it (sounds more natural). Never start mid-word. | Clean entry — viewer hears a complete phrase |
| **hook_end** | Snap to **end of the last word** + 0.05-0.15s of trailing silence. For "open loop" hooks that cut mid-thought, snap to **end of the last complete word** before the cut point — the abruptness IS the hook. | Clean exit without clipping the last phoneme |
| **body_start** | Snap to the **start of the sentence/thought**. Look for the nearest micro-pause or breath BEFORE the first word. Include 0.1-0.2s of "room tone" before speech starts. | Natural entry — doesn't feel like it started mid-conversation |
| **body_end** | Snap to **end of a complete sentence or thought**. Prefer ending on: (1) a period/full stop, (2) a dramatic pause, (3) a punchline, (4) a strong concluding phrase. Add 0.2-0.4s of trailing silence. | Clean exit — feels intentional, not chopped |

**Additional refinement rules:**

- **Hook→Body audio energy match**: If the hook has high energy (loud, fast) and the body starts quiet, add a 0.1s fade-in on the body to smooth the transition. If both are similar energy, hard cut is fine.
- **Body end — prefer the punchline**: If the transcript shows a strong phrase near the proposed body_end (±5s), adjust body_end to END on that phrase. Last impression matters.
- **Duration re-check**: After refinement, verify total duration (hook + body) is still 60-90s. If not, prefer trimming the body end rather than the body start (keep the opening intact).

#### 6b-4. Validate Hook Quality with Audio Preview

For hooks specifically, extract the refined 2-3.5s clip and verify:

```bash
# Extract refined hook audio
ffmpeg -y -ss {refined_hook_start} -to {refined_hook_end} \
  -i "{output-dir}/original.mp4" -vn -acodec pcm_s16le \
  "{output-dir}/hook_preview_{name}.wav"

# Check duration
ffprobe -v error -show_entries format=duration -of csv=p=0 "{output-dir}/hook_preview_{name}.wav"

# Check audio levels (hook should NOT be silent/low-energy)
ffmpeg -i "{output-dir}/hook_preview_{name}.wav" -af "volumedetect" -f null - 2>&1 | grep "mean_volume\|max_volume"
```

**Red flags:**
- `mean_volume` below -30 dB → hook audio too quiet, likely a bad hook moment
- Duration < 1.5s → hook too short, won't register
- Duration > 3.5s → hook too long, trim it

#### 6b-5. Validate Hook→Body Transition

The transition from hook teaser to body segment is critical. Extract a preview:

```bash
# Extract last 0.5s of hook + first 1s of body
ffmpeg -y -ss {refined_hook_end - 0.5} -to {refined_body_start + 1.0} \
  -i "{output-dir}/original.mp4" -vn -acodec pcm_s16le \
  "{output-dir}/transition_preview_{name}.wav"

# Check for audio discontinuity
ffmpeg -i "{output-dir}/transition_preview_{name}.wav" -af "silencedetect=n=-40dB:d=0.1" -f null - 2>&1
```

The transition should feel like a **deliberate editorial cut** — not a glitch. If there's an awkward volume jump or the body starts mid-word, adjust the body_start forward to the next clean entry point.

#### 6b-6. Update cuts.json with Refined Timestamps

```json
{
  "name": "corte1_tema",
  "hook_start": 1726.12,
  "hook_end": 1729.05,
  "body_start": 1719.48,
  "body_end": 1790.35,
  "hook_start_original": 1726.07,
  "hook_end_original": 1729.11,
  "body_start_original": 1719.56,
  "body_end_original": 1790.12,
  "refinement_notes": "hook_start snapped to start of 'Toda'. body_end extended 0.23s to include trailing pause after 'isso aí'.",
  "hook_audio_mean_db": -18.5,
  "total_duration_refined": 73.4
}
```

> **NOTE**: Keep original timestamps for reference. The `_original` fields let you debug if something sounds wrong after processing.

### Step 7 — Present Cuts to User

Show the proposed cuts ranked by total score, with the metric breakdown visible:

```datatable
{"columns":[{"key":"rank","label":"#"},{"key":"title","label":"Title"},{"key":"hook","label":"Hook (first 3s)"},{"key":"archetype","label":"Hook Type"},{"key":"retention","label":"Ret 3s","type":"number"},{"key":"like","label":"Like","type":"number"},{"key":"share","label":"Share","type":"number"},{"key":"total","label":"Score","type":"number"},{"key":"duration","label":"Duration","type":"number"}], "rows":[...]}
```

**For each cut, also show:**
- The hook archetype (contradiction, bold_claim, etc.)
- The polarization axis (what opinion split does this create?)
- Refinement notes (what timestamps were adjusted and why)

Wait for user approval. They may want to:
- Remove or add cuts
- Swap a hook for a more aggressive alternative
- Adjust timestamps
- Ask for bolder alternatives if scores are too low
- Prioritize certain topics

Save the approved cuts as `{output-dir}/cuts.json`.

---

## Phase 3a: Download Segments

**Goal**: Now that cuts are selected and timestamps refined, download ONLY the video segments we need — not the entire video. Each segment gets a ±1 minute buffer for safety.

> **WHY DOWNLOAD AFTER SELECTION**: A 90-min podcast is ~2GB. But 6 cuts of ~90s each = ~9 min of content. With ±1 min buffer per cut, we download ~18-24 min of video (or less if segments overlap and get merged). That's **~500MB instead of 2GB** — 75% savings in download time and disk space.

### Step 7a — Download Only Needed Segments

> **Skip this step if**: Method 3 (Whisper base) was used in Phase 2 — the full video was already downloaded.

```bash
bash {workflow-dir}/scripts/download_segments.sh \
  "{youtube-url}" "{output-dir}" "{output-dir}/cuts.json" 60
```

The script:
1. Reads `cuts.json` with the approved cuts and their timestamps
2. Computes download ranges: `min(hook_start, body_start) - 60s` to `max(hook_end, body_end) + 60s`
3. Merges overlapping ranges (if two cuts are <2 min apart, downloads as one segment)
4. Downloads each segment with `yt-dlp --download-sections` + `--force-keyframes-at-cuts`
5. Saves `segments/offset_map.json` — the timestamp translation map

**Output structure:**
```
{output-dir}/segments/
  corte1_tema.mp4          # Segment file for cut 1
  corte2_opiniao.mp4       # Segment file for cut 2
  group_1.mp4              # Merged segment (if cuts 3+4 overlap)
  offset_map.json          # Timestamp mapping
  ...
```

**offset_map.json** (critical for all subsequent steps):
```json
{
  "corte1_tema": {
    "file": "segments/corte1_tema.mp4",
    "download_start": 35.0,
    "download_end": 225.0,
    "buffer_secs": 60
  }
}
```

**TIMESTAMP RULE**: All timestamps in `cuts.json` are **absolute** (relative to the original full video). To use them with a segment file, subtract `download_start`:
```
segment_relative_time = absolute_time - offset_map[name].download_start
```

This offset calculation is needed for ALL subsequent ffmpeg commands (frame extraction, clip extraction, audio extraction, etc.).

### Step 7a-2 — Quick Format Check

Extract a reference frame from the first segment to verify video format:

```bash
ffmpeg -y -ss 5 -i "{output-dir}/segments/{first_segment}.mp4" -frames:v 1 -q:v 2 "{output-dir}/frame_check.jpg"
```

Verify:
- Resolution is 16:9 (1920x1080 or similar)
- Video quality is acceptable
- Note any persistent overlays (channel logo, lower thirds)

---

## Phase 3b: Per-Segment Visual Analysis (1fps Frame Scan)

**Goal**: Now that cuts are defined by the transcript, scan each segment visually at 1 frame per second to build a **frame-by-frame crop map**. This tells us exactly how to crop every second of every cut — handling camera switches, subject movement, and framing changes.

> **WHY THIS ORDER**: Transcript → Cut selection → Download segments → THEN visual analysis. We only analyze the ~6 minutes of selected segments, not the full 50+ minute video. This is 10x more efficient and 10x more precise.

### Step 7b — Extract 1fps Frames Per Segment

> **SUB-AGENT**: Use `Task(model: haiku, subagent_type: Bash)` to extract frames for all cuts in one batch. This is pure ffmpeg execution — no reasoning needed. Give the agent the list of cuts with timestamps and let it run all ffmpeg commands sequentially and return the frame counts per cut.

For each approved cut, extract frames at 1fps for the BODY segment using the **segment file** (not the full video):

```bash
# Read offset map to get the segment file and download_start for this cut
SEGMENT_FILE="{output-dir}/$(jq -r '."{name}".file' {output-dir}/segments/offset_map.json)"
OFFSET=$(jq -r '."{name}".download_start' {output-dir}/segments/offset_map.json)

# Convert absolute timestamps to segment-relative
BODY_START_REL=$(echo "{body_start} - $OFFSET" | bc)
BODY_END_REL=$(echo "{body_end} - $OFFSET" | bc)

# Create frames directory for this cut
mkdir -p "{output-dir}/frames/{name}"

# Extract 1 frame per second for the body segment
ffmpeg -y -ss $BODY_START_REL -to $BODY_END_REL -i "$SEGMENT_FILE" \
  -vf "fps=1" -q:v 2 "{output-dir}/frames/{name}/frame_%03d.jpg"
```

This produces ~60-90 frames per cut (one per second of the body segment). For 6 cuts, that's ~360-540 frames total — manageable for AI analysis.

Also extract frames for the hook:
```bash
HOOK_START_REL=$(echo "{hook_start} - $OFFSET" | bc)
HOOK_END_REL=$(echo "{hook_end} - $OFFSET" | bc)

mkdir -p "{output-dir}/frames/{name}_hook"
ffmpeg -y -ss $HOOK_START_REL -to $HOOK_END_REL -i "$SEGMENT_FILE" \
  -vf "fps=1" -q:v 2 "{output-dir}/frames/{name}_hook/frame_%03d.jpg"
```

> **OFFSET RULE**: Always read `offset_map.json` and subtract `download_start` before any ffmpeg `-ss`/`-to` on a segment file. This applies to ALL subsequent steps.

### Step 7c — Scene Detection: Fast First Pass (requires `vision_available = true`)

> **DESIGN PRINCIPLE**: Don't guess the crop from a few samples — DETECT where the camera angle changes, THEN analyze each scene precisely. Two-pass approach: fast scene detection → detailed per-scene analysis → rendered crop previews → user validates.

> **SUB-AGENTS (PARALLEL)**: Launch **one `Task(model: sonnet, subagent_type: general-purpose)` per cut**. Each sub-agent runs both the scene detection pass AND the detailed analysis, then returns a complete crop_map + preview frame paths.

#### 7c-1. Sparse Scene Scan (every 5th frame)

From the 1fps frames extracted in Step 7b, take every 5th frame for a fast scan. For a 70s body segment, that's ~14 frames instead of 70.

```bash
# List every 5th frame for the scene detection pass
ls "{output-dir}/frames/{name}/frame_"*.jpg | awk 'NR % 5 == 1'
```

Analyze each sparse frame with a lightweight prompt focused ONLY on scene classification:

```
analyze_image({
  filePath: "{frame_path}",
  prompt: "Classify this video frame for scene detection. Return ONLY a JSON object:
{
  \"scene_type\": \"close_up_single\" | \"close_up_two\" | \"wide_two\" | \"wide_group\" | \"cutaway\" | \"screen_share\",
  \"primary_face_x_pct\": 50,
  \"num_faces\": 1,
  \"has_overlay\": false
}
scene_type: close_up_single = one face fills >40% of frame. close_up_two = two faces each >25%. wide_two = two people but smaller in frame. wide_group = 3+ people. cutaway = B-roll/graphics. screen_share = presentation/screen.
primary_face_x_pct: horizontal position of the MAIN SPEAKER's face as % from left edge (0=far left, 100=far right).
Be precise on primary_face_x_pct — off by 10% means the crop cuts off half their face."
})
```

#### 7c-2. Detect Scene Boundaries

Compare consecutive scene scan results. A **scene change** occurs when:
- `scene_type` changes (e.g., `close_up_single` → `wide_two`)
- `primary_face_x_pct` shifts by >15 percentage points
- `num_faces` changes

For each detected change:
1. Note the frame numbers of the last "before" frame and first "after" frame
2. The switch happened somewhere between them (within a 5-second window)

```json
{
  "scenes_detected": [
    {"from_frame": 1, "to_frame": 35, "scene_type": "close_up_single", "face_x": 48},
    {"from_frame": 36, "to_frame": 70, "scene_type": "wide_two", "face_x": 30}
  ],
  "switch_points": [{"between_frames": [35, 36], "approx_second": 35}]
}
```

#### 7c-3. Pinpoint Scene Switches (±2s dense scan)

For each detected switch point, analyze the frames around it at 1fps (they were already extracted in Step 7b):

```bash
# Frames 33-38 (around the switch at ~35s)
for f in frame_033.jpg frame_034.jpg frame_035.jpg frame_036.jpg frame_037.jpg frame_038.jpg; do
  analyze_image(...)
done
```

This pinpoints the exact second of each camera switch (±0.5s precision).

#### 7c-4. Detailed Per-Scene Crop Analysis

Now that scene boundaries are known, analyze **2-3 representative frames from each scene** with a detailed prompt:

```
analyze_image({
  filePath: "{frame_path}",
  prompt: "This frame is from a podcast/interview video (16:9) that will be cropped to vertical 9:16 for Reels.

The 9:16 crop takes a vertical strip from the center of the 16:9 frame — the strip width is 56.25% of frame height.

Analyze and return a JSON:
{
  \"layout_description\": \"Close-up of male guest speaking, slightly left of center\",
  \"primary_speaker_face_x_pct\": 45,
  \"primary_speaker_face_y_pct\": 35,
  \"secondary_face_x_pct\": null,
  \"face_width_pct\": 20,
  \"gesture_space_needed\": \"left\",
  \"has_lower_third\": false,
  \"lower_third_height_pct\": 0,
  \"background_clutter\": \"minimal\",
  \"recommended_crop_center_x_pct\": 45,
  \"crop_confidence\": \"high\"
}

CRITICAL details:
- primary_speaker_face_x_pct: precise horizontal center of the speaker's face (0-100). This DIRECTLY becomes the crop center.
- face_width_pct: how wide the face is relative to frame. If >35%, it's a very tight close-up — crop must be precise.
- gesture_space_needed: if speaker is gesturing, which side needs more room (left/right/both/none).
- recommended_crop_center_x_pct: WHERE to center the 9:16 crop. Consider face position, gestures, and any text overlays.
- crop_confidence: 'high' if the face is clearly centered and crop is obvious, 'medium' if there are trade-offs, 'low' if the scene is difficult (very wide shot, multiple speakers, etc.)."
})
```

#### 7c-5. Calculate Exact ffmpeg Crop Filters Per Scene

Convert `recommended_crop_center_x_pct` to ffmpeg crop filter:

```python
# The 9:16 crop takes a strip of width = height * 9/16
# In a 1920x1080 video: crop_width = 1080 * 9/16 = 607.5 pixels
# The crop X offset = (frame_width - crop_width) * (center_pct / 100) - (crop_width / 2)
# But clamped to valid range [0, frame_width - crop_width]

def calc_crop_filter(center_x_pct, frame_w=1920, frame_h=1080):
    crop_w = frame_h * 9 / 16  # 607.5 for 1080p
    # Convert percentage to pixel position
    face_x = frame_w * center_x_pct / 100
    # Center the crop on the face
    crop_x = max(0, min(face_x - crop_w / 2, frame_w - crop_w))
    crop_x = int(crop_x)
    return f"crop={int(crop_w)}:{frame_h}:{crop_x}:0"

# center (50%) → "crop=607:1080:656:0" ≈ "crop=ih*9/16:ih"
# left (30%) →   "crop=607:1080:269:0"
# right (70%) →  "crop=607:1080:1043:0"
```

> **NOTE**: Using pixel-precise crop filters instead of the generic `crop=ih*9/16:ih` (which always centers). Pixel precision means the speaker's face is exactly centered in the vertical frame, even when they're off-center in the original 16:9.

#### 7c-6. Build the Crop Map

For each cut, combine scenes into a crop_map:

```json
{
  "name": "corte1_ceo",
  "scenes": [
    {
      "from_sec": 0, "to_sec": 35,
      "scene_type": "close_up_single",
      "crop": "crop=607:1080:656:0",
      "crop_center_x_pct": 50,
      "confidence": "high",
      "reason": "Close-up centered on guest"
    },
    {
      "from_sec": 35, "to_sec": 70,
      "scene_type": "wide_two",
      "crop": "crop=607:1080:269:0",
      "crop_center_x_pct": 30,
      "confidence": "medium",
      "reason": "Wide shot — guest on left third, interviewer on right. Crop follows guest."
    }
  ],
  "hook_crop": "crop=607:1080:656:0",
  "has_camera_switch": true,
  "subtitle_margin_v": 280,
  "has_lower_thirds": false
}
```

### Step 7d — Render Crop Preview Frames

**This is the key quality step.** Instead of trusting the AI's crop numbers blindly, render the actual 9:16 crop on sample frames and validate visually.

> **SUB-AGENT**: Use `Task(model: haiku, subagent_type: Bash)` to render all preview frames in one batch (pure ffmpeg, no reasoning). Returns file paths.

For each cut, render 3-5 preview frames showing exactly what the viewer will see:

```bash
mkdir -p "{output-dir}/crop_previews/{name}"

# For each scene in the crop_map, render 2 preview frames
for scene in crop_map:
    # Pick frames from the middle of each scene
    mid_sec = (scene.from_sec + scene.to_sec) / 2
    frame_num = int(mid_sec) + 1  # frame_001.jpg = second 0

    # Apply the scene's crop filter + scale to 1080x1920
    ffmpeg -y -i "{output-dir}/frames/{name}/frame_{frame_num:03d}.jpg" \
      -vf "{scene.crop},scale=1080:1920" \
      "{output-dir}/crop_previews/{name}/scene{i}_sec{mid_sec:.0f}.jpg"
done

# Also render hook crop preview
ffmpeg -y -i "{output-dir}/frames/{name}_hook/frame_001.jpg" \
  -vf "{hook_crop},scale=1080:1920" \
  "{output-dir}/crop_previews/{name}/hook.jpg"
```

Each preview is a 1080x1920 image — exactly what the final vertical video will look like at that moment.

### Step 7e — User Validates Crop Framing

**MANDATORY USER CHECKPOINT.** Show the rendered crop previews and get explicit approval before processing.

For each cut, present the previews using the Read tool (which renders images inline):

```
For each cut:
  1. Show the HOOK preview (cropped 9:16)
  2. Show 1-2 BODY scene previews (one per scene if camera switches)
  3. Note the scene boundaries and confidence levels
```

Present as a structured review:

```
**Corte 1: "MULHER CEO"** (70s, 1 scene, high confidence)
[Show hook preview image]
[Show body mid-point preview image]
Crop: center (50%) — guest centered in close-up throughout.

**Corte 3: "ESQUERDISTA"** (84s, 2 scenes, medium confidence)
[Show body scene 1 preview (0-35s)]
[Show body scene 2 preview (35-84s)]
Crop: Scene 1 center → Scene 2 left-third (camera switches to wide shot at ~35s).
⚠️ Medium confidence on scene 2 — guest slightly off-center in wide shot.
```

**Ask the user:**
> "Aqui estão os previews de crop para cada corte. Verifique se o rosto do speaker está bem enquadrado em cada cena. Algum ajuste necessário?"

**User may respond with:**
- "Corte 3, cena 2 — puxa mais pra esquerda" → adjust `crop_center_x_pct` by -5 to -10, re-render preview
- "Corte 5 — speaker sai do frame" → need to re-analyze with different crop strategy
- "Tudo OK" → proceed

> **WHY MANUAL VALIDATION**: AI vision is ~90% accurate on face position, but 10% error on a 1080px-wide crop means ~108px off — enough to clip half a face. 30 seconds of human review catches what AI misses.

### Step 7f — Generate Final crop_profile.json

After user approval, save the definitive crop profile:

```json
{
  "video_resolution": "1920x1080",
  "analysis_method": "two_pass_scene_detection",
  "subtitle_margin_v": 280,
  "user_validated": true,
  "cuts": {
    "corte1_ceo": {
      "hook_crop": "crop=607:1080:656:0",
      "has_camera_switch": false,
      "crop_confidence": "high",
      "scenes": [
        {"from_sec": 0, "to_sec": 70, "crop": "crop=607:1080:656:0", "scene_type": "close_up_single"}
      ]
    },
    "corte3_esquerdista": {
      "hook_crop": "crop=607:1080:656:0",
      "has_camera_switch": true,
      "crop_confidence": "medium",
      "scenes": [
        {"from_sec": 0, "to_sec": 35, "crop": "crop=607:1080:656:0", "scene_type": "close_up_single"},
        {"from_sec": 35, "to_sec": 84, "crop": "crop=607:1080:269:0", "scene_type": "wide_two"}
      ]
    }
  }
}
```

### Step 7g — Handle Camera Switches in ffmpeg

For cuts WITH camera switches (multiple scenes in `crop_profile.json`), the body is split at switch points, cropped separately, then concatenated:

```bash
# Split body at the scene change second
ffmpeg -y -ss $BODY_START_REL -to $(echo "$BODY_START_REL + $SWITCH_SEC" | bc) \
  -i "$SEGMENT_FILE" "{output-dir}/{name}_body_part0.mp4"
ffmpeg -y -ss $(echo "$BODY_START_REL + $SWITCH_SEC" | bc) -to $BODY_END_REL \
  -i "$SEGMENT_FILE" "{output-dir}/{name}_body_part1.mp4"

# Crop each part with its scene-specific filter
ffmpeg -y -i "{output-dir}/{name}_body_part0.mp4" \
  -vf "{scene0_crop},scale=1080:1920" \
  -c:v libx264 -preset fast -crf 23 -pix_fmt yuv420p \
  -c:a aac -b:a 128k -ar 44100 "{output-dir}/{name}_body_part0_proc.mp4"

ffmpeg -y -i "{output-dir}/{name}_body_part1.mp4" \
  -vf "{scene1_crop},scale=1080:1920" \
  -c:v libx264 -preset fast -crf 23 -pix_fmt yuv420p \
  -c:a aac -b:a 128k -ar 44100 "{output-dir}/{name}_body_part1_proc.mp4"

# Concatenate: hook + body_part0 + body_part1
```

> **NOTE**: Most podcast cuts (80%+) will have a single scene with no switch. The split-crop-concat path only activates when Step 7c detected a genuine camera change.

### Step 7h — Fallback: No Vision Available

If `vision_available = false`:

1. For each cut, render a **center-crop preview** using the default filter:
```bash
ffmpeg -y -i "{output-dir}/frames/{name}/frame_030.jpg" \
  -vf "crop=ih*9/16:ih,scale=1080:1920" \
  "{output-dir}/crop_previews/{name}/default_center.jpg"
```

2. Show the center-crop preview to the user inline (Read tool renders images)

3. Ask: "Esse é o crop padrão (centro). O speaker está bem enquadrado? Se não, me diz pra qual lado ajustar (esquerda/direita) e eu recalculo."

4. If user says "esquerda": use `crop=ih*9/16:ih:0:0` (left-third)
5. If user says "direita": use `crop=ih*9/16:ih:iw-ih*9/16:0` (right-third)
6. Re-render preview with the new crop for confirmation

7. Save to `crop_profile.json` — even without AI, the user validated it

### Step 7i — Adjust Subtitle Position

Based on visual analysis results:
- Default: `subtitle_margin_v = 280` (safe for Instagram UI)
- If `has_lower_thirds` is true AND lower thirds are in the bottom: increase to 320-360
- If lower thirds are in the upper area: keep at 280
- If the video has a persistent bottom banner/watermark: increase to 350+

Save the final `subtitle_margin_v` to `crop_profile.json`.

---

## Phase 4: Generate Cuts

### Step 8 — Extract Clips from Segments

For each cut, extract the hook and body clips from the **segment file** (not the full video):

```bash
# Read offset map
SEGMENT_FILE="{output-dir}/$(jq -r '."{name}".file' {output-dir}/segments/offset_map.json)"
OFFSET=$(jq -r '."{name}".download_start' {output-dir}/segments/offset_map.json)

# Convert to segment-relative timestamps
HOOK_START_REL=$(echo "{hook_start} - $OFFSET" | bc)
HOOK_END_REL=$(echo "{hook_end} - $OFFSET" | bc)
BODY_START_REL=$(echo "{body_start} - $OFFSET" | bc)
BODY_END_REL=$(echo "{body_end} - $OFFSET" | bc)

# Hook (2-3.5s teaser)
ffmpeg -y -ss $HOOK_START_REL -to $HOOK_END_REL -i "$SEGMENT_FILE" -c copy "{output-dir}/{name}_hook.mp4"

# Body (complete segment)
ffmpeg -y -ss $BODY_START_REL -to $BODY_END_REL -i "$SEGMENT_FILE" -c copy "{output-dir}/{name}_body.mp4"
```

If timestamps aren't precise with `-c copy`, re-extract without it (slower but exact):
```bash
ffmpeg -y -ss $HOOK_START_REL -to $HOOK_END_REL -i "$SEGMENT_FILE" "{output-dir}/{name}_hook.mp4"
```

> **SEGMENT vs ORIGINAL**: All ffmpeg commands from this point use `$SEGMENT_FILE` with relative timestamps. If Method 3 fallback was used (full download), use `original.mp4` with absolute timestamps instead.

### Step 8b — Per-Segment Transcription with Whisper Medium (for Subtitles)

> **THIS IS THE KEY STEP FOR SUBTITLE QUALITY.** The rough transcript from Phase 2 was for cut selection. Now we transcribe each segment with the `medium` model for accurate word-level timestamps that become the actual on-screen subtitles.
>
> **LESSON LEARNED**: Using base/small Whisper models or mlx-whisper on the full video produces systematic errors on proper nouns (CEO → "se ou", G4 → "já quatro") and hallucinations on intro music. The medium model on short segments (<90s) is fast on Apple Silicon and much more accurate.
>
> **SUB-AGENT**: Use `Task(model: haiku, subagent_type: Bash)` to transcribe all segments in sequence (Whisper loads the model once and is GPU-bound, so parallelism has limited benefit here). The agent runs `transcribe_segment.sh` for each cut and returns the word count per segment.

For each approved cut, extract the segment audio and transcribe with whisper-medium.

**Use the segment file with relative timestamps:**

```bash
# Read offset map
SEGMENT_FILE="{output-dir}/$(jq -r '."{name}".file' {output-dir}/segments/offset_map.json)"
OFFSET=$(jq -r '."{name}".download_start' {output-dir}/segments/offset_map.json)
BODY_START_REL=$(echo "{body_start} - $OFFSET" | bc)
BODY_END_REL=$(echo "{body_end} - $OFFSET" | bc)

bash {workflow-dir}/scripts/transcribe_segment.sh \
  "{output-dir}" "{name}" $BODY_START_REL $BODY_END_REL "$SEGMENT_FILE"
```

> **NOTE**: `transcribe_segment.sh` receives segment-relative timestamps. If using the full video fallback (`original.mp4`), pass absolute timestamps directly.

This script:
1. Extracts the segment audio (body range + 1s padding on each side)
2. Also extracts the hook audio separately
3. Runs `whisper-cli -m ggml-medium.bin` on each
4. Parses the JSON output into `{text, start, end}` word array
5. Filters hallucination artifacts (words with >5 consecutive identical characters)
6. Saves `{name}_words.json` with timestamps relative to segment start

**Model path**: `~/.local/share/whisper-models/ggml-medium.bin`

**If whisper-cli is not installed:**
```bash
brew install whisper-cpp
```

**If ggml-medium.bin is not downloaded:**
```bash
mkdir -p ~/.local/share/whisper-models
curl -L "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin" \
  -o ~/.local/share/whisper-models/ggml-medium.bin
```

### Step 9 — Generate ASS Subtitles

Use the Python script to generate subtitle files with dynamic word-by-word highlighting.

**IMPORTANT**: The `--start` and `--end` passed to `generate_ass.py` should be `0` and `segment_duration` (not absolute timestamps), because the per-segment transcript has timestamps relative to the segment start.

```bash
# Read segment duration
BODY_DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "{output-dir}/{name}_body.mp4")
HOOK_DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "{output-dir}/{name}_hook.mp4")

# Generate body subtitles
python3 {workflow-dir}/scripts/generate_ass.py \
  --transcript "{output-dir}/{name}_body_words.json" \
  --output "{output-dir}/{name}_body.ass" \
  --start 0 \
  --end "$BODY_DUR" \
  --font-size 58 \
  --margin-v 280

# Generate hook subtitles
python3 {workflow-dir}/scripts/generate_ass.py \
  --transcript "{output-dir}/{name}_hook_words.json" \
  --output "{output-dir}/{name}_hook.ass" \
  --start 0 \
  --end "$HOOK_DUR" \
  --font-size 58 \
  --margin-v 280
```

> **NOTE**: Default `margin-v` is now 280 (was 180). Testing showed 180 is too close to Instagram's bottom UI overlay. 280 places subtitles safely above the interaction buttons.

The script:
- Filters words within the time range
- Groups words into chunks of 3-5 (breaking on pauses > 0.35s or punctuation)
- Generates ASS events with `\c&H00FFFF&` highlight for the active word
- Applies `\fscx110\fscy110` scale effect on the active word
- Uses ALL CAPS for all text

### Step 9b — Present Transcripts for User Review

**MANDATORY USER CHECKPOINT.** The subtitles become the most visible element of the final video — any transcription error is permanently baked in. Show the transcript to the user BEFORE generating the final ASS files.

#### 9b-1. Build Readable Transcript Summary Per Cut

For each cut, read the `{name}_body_words.json` and `{name}_hook_words.json`, then present the text:

```python
import json

words = json.load(open("{output-dir}/{name}_body_words.json"))
full_text = " ".join(w["text"].strip() for w in words)
word_count = len(words)
duration = words[-1]["end"] - words[0]["start"] if words else 0
```

#### 9b-2. Present All Transcripts in a Single Review Block

Show ALL cut transcripts at once for efficient review. Format:

```
**REVISÃO DE LEGENDAS — Confira antes de processar os vídeos**

---
**Corte 1: "MULHER CEO"** (72s, 187 palavras)

🎣 HOOK (2.8s):
"TODA EMPRESA DEVERIA DEMITIR O RH"

📝 BODY (69s):
"A TRADUÇÃO É O SEGUINTE: QUANDO EU COMECEI A EMPRESA, EU TINHA UMA ÁREA DE RH TRADICIONAL.
AVALIAÇÃO DE DESEMPENHO, PLANO DE CARGOS E SALÁRIOS, AQUELE NEGÓCIO TODO.
E AÍ UM DIA EU OLHEI E FALEI: ISSO NÃO FUNCIONA. CEO NENHUM OLHA AQUELE RELATÓRIO.
..."

⚠️ Flags:
- "CEO" aparece 3x — verificar se está correto (Whisper erra em anglicismos)
- Nomes próprios detectados: nenhum
---

**Corte 2: "PREJUÍZO DE 50 MILHÕES"** (65s, 162 palavras)
...
```

**Auto-flag rules** (highlight potential issues):
- Words that look like proper nouns (capitalized in source, may be wrong)
- Numbers and currency values (Whisper often garbles "R$50 milhões" → "r50 milhões")
- English words in Portuguese context (CEO, startup, feedback, etc.)
- Very short words (<2 chars) that might be Whisper artifacts
- Repeated phrases that might be hallucinations

#### 9b-3. Ask for Corrections

> "Verifique as legendas acima. Alguma correção necessária? Exemplos:
> - 'Corte 1: troca se ou por CEO'
> - 'Corte 3: troca já quatro por G4'
> - 'Tudo OK, pode processar'"

**Wait for user response.** Do NOT proceed to video encoding until user confirms.

#### 9b-4. Apply Corrections

If user provides corrections:

1. Edit the `{name}_body_words.json` file directly — find the wrong word and replace the `text` field
2. Regenerate the ASS file for that cut only:
```bash
python3 {workflow-dir}/scripts/generate_ass.py \
  --transcript "{output-dir}/{name}_body_words.json" \
  --output "{output-dir}/{name}_body.ass" \
  --start 0 --end "$BODY_DUR" --font-size 58 --margin-v 280
```
3. Show the corrected text for confirmation
4. Repeat until user says "OK"

> **LESSON LEARNED**: Whisper base pode transformar anglicismos em erros sistematicos (ex: "CEO" → "se ou") — erros que ficariam permanentemente visiveis em cada frame do video. 30 segundos de revisao do usuario previne legendas erradas embaracosas.

### Step 9c — Final Subtitle Verification (automated)

After user approves the transcript text, run automated checks on the generated `.ass` files:

```bash
# Verify ASS file is valid (has events, correct format)
for name in {all_cut_names}; do
  EVENTS=$(grep -c "^Dialogue:" "{output-dir}/{name}_body.ass")
  echo "$name: $EVENTS subtitle events"
  [ "$EVENTS" -lt 5 ] && echo "WARNING: $name has very few subtitle events — check transcript"
done
```

Also verify the ALL CAPS formatting and highlight tags are present:
```bash
# Check that yellow highlight tags exist
grep -c "\\\\c&H00FFFF&" "{output-dir}/{name}_body.ass"
```

### Step 10 — Process Each Cut (Crop + Subtitles + Concatenate)

> **SUB-AGENTS (PARALLEL)**: Launch `Task(model: haiku, subagent_type: Bash)` agents — **2 cuts per agent** for optimal parallelism. Haiku is the right choice here: these agents just execute bash scripts (process_cut.sh), no creative reasoning needed. For 6 cuts → 3 parallel haiku agents. Each agent receives: output-dir, cut names/timestamps, crop filters from crop_profile.json, and the script path. Each returns: file paths and durations of completed cuts.
>
> **Why haiku?** process_cut.sh is a deterministic pipeline — extract, subtitle, crop, encode, concat. The agent just runs commands and checks exit codes. Sonnet/Opus would be wasted here.

**Before processing**, read `{output-dir}/crop_profile.json` to get the crop strategy for each cut:

```python
import json
crop_profile = json.load(open("{output-dir}/crop_profile.json"))
cut_info = crop_profile["cuts"][name]
margin_v = crop_profile.get("subtitle_margin_v", 280)
has_switch = cut_info.get("has_camera_switch", False)
scenes = cut_info.get("scenes", [])
```

#### Path A: No Camera Switch (single crop — most common)

When `has_camera_switch == false`, there's 1 scene. Use the unified script:

```bash
bash {workflow-dir}/scripts/process_cut.sh \
  "{output-dir}" "{name}" {hook_start} {hook_end} {body_start} {body_end} \
  "{workflow-dir}" "{output-dir}/transcript.json" \
  "{scenes[0].crop}" {margin_v}
```

The script handles: extract → subtitle → crop → encode → concat → QC frames.

#### Path B: Camera Switch Detected (multi-crop segment)

When `has_camera_switch == true`, the body needs to be split at switch points, cropped separately, then concatenated:

```bash
# 1. Extract and subtitle the hook (single crop as always)
ffmpeg -y -ss {hook_start} -to {hook_end} -i original.mp4 {name}_hook.mp4
python3 generate_ass.py --transcript transcript.json --output {name}_hook.ass --start {hook_start} --end {hook_end} --margin-v {margin_v}
ffmpeg -y -i {name}_hook.mp4 \
  -vf "{hook_crop},scale=1080:1920,ass={name}_hook.ass" \
  -c:v libx264 -preset fast -crf 23 -pix_fmt yuv420p \
  -c:a aac -b:a 128k -ar 44100 {name}_hook_proc.mp4

# 2. For each crop_map segment, extract → crop → encode
#    crop_map: [{from_sec: 0, to_sec: 42, crop: "..."}, {from_sec: 42, to_sec: 84, crop: "..."}]
for i, zone in enumerate(crop_map):
    abs_start = body_start + zone.from_sec
    abs_end = body_start + zone.to_sec

    # Extract segment
    ffmpeg -y -ss {abs_start} -to {abs_end} -i original.mp4 {name}_body_part{i}.mp4

    # Generate subtitles for this segment
    python3 generate_ass.py --transcript transcript.json --output {name}_body_part{i}.ass --start {abs_start} --end {abs_end} --margin-v {margin_v}

    # Crop + encode
    ffmpeg -y -i {name}_body_part{i}.mp4 \
      -vf "{zone.crop},scale=1080:1920,ass={name}_body_part{i}.ass" \
      -c:v libx264 -preset fast -crf 23 -pix_fmt yuv420p \
      -c:a aac -b:a 128k -ar 44100 {name}_body_part{i}_proc.mp4

# 3. Concatenate: hook + body_part0 + body_part1 + ...
echo "file '{name}_hook_proc.mp4'" > concat_{name}.txt
for i in range(len(crop_map)):
    echo "file '{name}_body_part{i}_proc.mp4'" >> concat_{name}.txt

ffmpeg -y -f concat -safe 0 -i concat_{name}.txt -c copy final/{name}_final.mp4
```

> **NOTE**: Camera switches are uncommon in well-produced podcasts with dedicated close-ups. Most cuts will take Path A (single crop). Path B only activates when the 1fps analysis in Step 7c detects a layout change mid-segment.

**Technical Specs:**
| Parameter | Value |
|-----------|-------|
| Resolution | 1080x1920 (9:16 vertical) |
| Video Codec | H.264 (libx264) |
| Audio Codec | AAC 128kbps, 44.1kHz |
| CRF | 23 |
| Preset | fast |
| Pixel Format | yuv420p |
| Subtitle Font | Arial Black, size 58 |
| Subtitle Color | White (#FFFFFF) with yellow highlight (#FFFF00) |
| Outline | Black, thickness 4.5 |

---

## Phase 5: Quality Check & Delivery

### Step 11 — Quality Check (Automated + Visual)

> **SUB-AGENT**: Launch a single `Task(model: sonnet, subagent_type: general-purpose)` to run ALL QC checks — both automated (ffprobe duration checks) and visual (analyze_image on QC frames). The agent receives the list of final video paths and QC frame paths, runs all validations, and returns a structured JSON report: `{cuts: [{name, duration, duration_ok, framing_rating, needs_reframe, reframe_suggestion}]}`. Main context only sees the summary and acts on any NEEDS_REFRAME results.

#### 11a. Automated Checks (always run)

```bash
# Check duration for each cut
for f in "{output-dir}/final/"*_final.mp4; do
  name=$(basename "$f" _final.mp4)
  duration=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
  echo "$name: ${duration}s"
done
```

Verify: all durations between 60-90 seconds. Flag any outside this range.

#### 11b. Visual QC with AI (requires `vision_available = true`)

The `process_cut.sh` script already extracts QC frames. Analyze them com a source de AI (ex: Google AI):

```
analyze_image({
  filePath: "{output-dir}/final/{name}_qc_hook.jpg",
  prompt: "This is a frame from a vertical video (1080x1920) for Instagram Reels. Check:
1. Is the main speaker's face visible and well-framed? (not cut off at edges)
2. Are the subtitles at the bottom visible and readable? (white text with black outline)
3. Is there any important content being cut off by the vertical crop?
4. Is the image quality acceptable? (not blurry, not too dark)
5. Rate the framing quality: GOOD, ACCEPTABLE, or NEEDS_REFRAME.
If NEEDS_REFRAME, suggest which direction to shift the crop (left/right/up/down)."
})
```

Do this for both `_qc_hook.jpg` and `_qc_body.jpg` for each cut.

**If any cut gets `NEEDS_REFRAME`:**
1. Determine the new crop filter based on the suggestion
2. Re-process ONLY that cut with the adjusted crop
3. Re-validate

#### 11c. Visual QC Fallback (no AI vision)

If `vision_available = false`, show the QC frames to the user inline using the Read tool and ask for manual confirmation.

#### Quality Checklist

| Item | Criterion | Auto-check | Visual-check |
|------|-----------|------------|--------------|
| Duration | 60-90 seconds | `ffprobe` duration | — |
| Hook | First 3s are impactful | — | Watch first 3s |
| Subtitles | Large, readable, no edge clipping | — | `analyze_image` on QC frame |
| Highlight | Active word in yellow tracks speech | — | Watch playback |
| Framing | Subject centered in frame | — | `analyze_image` on QC frame |
| Audio | Clear audio, no abrupt cuts | — | Listen to transitions |
| Transition | Hook → Body without artifact | — | `analyze_image` at ~3s mark |
| File playback | Plays on social media | `ffprobe` codec/pix_fmt | — |

### Step 12 — Deliver Results

Present the final cuts to the user:

1. **Summary table** with all cuts (title, duration, file path)
2. **File cards** for each final video
3. **QC frames** as image previews for spot-checking

```datatable
{"columns":[{"key":"num","label":"#"},{"key":"title","label":"Title"},{"key":"hook","label":"Hook"},{"key":"duration","label":"Duration"},{"key":"file","label":"File"}], "rows":[...]}
```

For each cut:
```filecard
{"type":"file_download","path":"{output-dir}/final/{name}_final.mp4","filename":"{title}.mp4","mimeType":"video/mp4","size":{bytes},"sizeHuman":"{size}"}
```

### Step 13 — Iterate

The user may want to:
- Adjust a hook (different phrase)
- Change subtitle style (color, size, position)
- Re-crop a specific cut (different framing)
- Add/remove cuts
- Trim a cut (shorten body)

For adjustments, only re-process the affected cut — don't redo the entire pipeline.

---

## Error Recovery

### Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Imprecise timestamps with `-c copy` | Keyframe alignment | Re-extract without `-c copy` |
| Subtitles desynchronized | Wrong time offset | Verify `--start` matches the clip's start time exactly |
| Video won't play on social media | Missing `yuv420p` | Always include `-pix_fmt yuv420p` |
| ffmpeg hangs | Preset too slow | Use `-preset fast`, not `slow` |
| Crop cuts off subject | Subject not centered | Extract frame, check position, adjust crop filter |
| Audio gap at hook→body transition | Stream mismatch | Re-encode both with same audio params before concat |

### Fallback for Transcription

If no service provides word-level timestamps:
1. Get paragraph-level transcript from source de AI (ex: Google AI)
2. Use `forced alignment` with a tool like `aeneas` or `gentle` to get word timestamps
3. Or use Whisper locally (slower but reliable)

---

## Anti-Patterns — DO NOT DO THESE

### NEVER generate videos from scratch with AI
The cuts must be CLIPS from the original video. Use ffmpeg to extract, not AI to generate.

### NEVER make hooks longer than 3.5 seconds
The hook must be 2-3.5s. Longer hooks lose the instant-impact effect.

### NEVER use small subtitle fonts
In vertical 1080x1920 video, use font size 52-58. Size 18-20 is illegible on phones.

### NEVER continue the body from where the hook ends
The hook is a TEASER. The body restarts from the beginning of the segment.

### NEVER skip `-pix_fmt yuv420p`
Without this, videos may not play in browsers and social media apps.

### NEVER use `-preset slow`
On machines with limited cores, use `-preset fast`. Slow can freeze.

### NEVER process all cuts sequentially when sub-agents are available
Use parallel Task agents to process 2-3 cuts simultaneously.

---

## Reference Commands

### Download
```bash
yt-dlp -f "bestvideo+bestaudio" --merge-output-format mp4 -o "{output}/original.mp4" "URL"
```

### Extract clip
```bash
ffmpeg -y -ss START -to END -i video.mp4 -c copy clip.mp4
```

### Crop to vertical + subtitles
```bash
ffmpeg -y -i clip.mp4 \
  -vf "crop=ih*9/16:ih,scale=1080:1920,ass=subs.ass" \
  -c:v libx264 -preset fast -crf 23 -pix_fmt yuv420p \
  -c:a aac -b:a 128k output.mp4
```

### Concatenate clips
```bash
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy final.mp4
```

### Check duration
```bash
ffprobe -v error -show_entries format=duration -of csv=p=0 final.mp4
```

### Extract QC frame
```bash
ffmpeg -ss 1.5 -i final.mp4 -frames:v 1 -q:v 2 check.jpg
```
