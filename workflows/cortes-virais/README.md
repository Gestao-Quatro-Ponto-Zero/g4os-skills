# Cortes Virais

Transforma entrevistas e podcasts do YouTube em **5-7 cortes verticais (9:16)** de 60-90 segundos, prontos para Reels, Shorts e TikTok — com **hook teaser** nos primeiros 3s e **legendas dinamicas** palavra-por-palavra com destaque amarelo.

## O que faz

1. Recebe uma URL do YouTube
2. Transcreve o conteudo (via source de AI ou Whisper local)
3. Analisa e seleciona os momentos mais virais com scoring (retention, like, share)
4. Baixa apenas os segmentos necessarios (~75% menos banda)
5. Detecta trocas de camera e calcula crop inteligente por cena
6. Gera legendas ASS com highlight dinamico (palavra ativa em amarelo)
7. Processa os cortes verticais (1080x1920) com qualidade de publicacao

## Arquivos

| Arquivo | Funcao |
|---------|--------|
| `WORKFLOW.md` | Instrucoes completas do workflow (5 fases) |
| `knowledge/playbook-reference.md` | Referencia rapida: hooks, scoring, specs tecnicas |
| `scripts/download.sh` | Fallback: download completo do video |
| `scripts/download_segments.sh` | Download inteligente por segmentos |
| `scripts/transcribe_segment.sh` | Transcricao per-segment com Whisper medium |
| `scripts/generate_ass.py` | Geracao de legendas ASS com highlight dinamico |
| `scripts/process_cut.sh` | Pipeline de processamento por corte |

## Requisitos

- **macOS** (Apple Silicon recomendado para Whisper com Metal GPU)
- `yt-dlp` — download de video do YouTube
- `ffmpeg` / `ffprobe` — processamento de video e audio
- `python3` — scripts de legendas e processamento
- `whisper-cli` + `ggml-medium.bin` — transcricao word-level para legendas

### Instalacao dos requisitos

```bash
brew install yt-dlp ffmpeg python whisper-cpp
mkdir -p ~/.local/share/whisper-models
curl -L "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin" \
  -o ~/.local/share/whisper-models/ggml-medium.bin
```

## Instalacao do Workflow

**Opcao A** — Cole no G4 OS:
```
Instale o workflow "cortes-virais" de https://github.com/Gestao-Quatro-Ponto-Zero/g4os-skills — clone o repo, copie workflows/cortes-virais/ para o diretorio de workflows do meu G4 OS, e confirme que esta funcionando.
```

**Opcao B** — Terminal:
```bash
curl -sL https://raw.githubusercontent.com/Gestao-Quatro-Ponto-Zero/g4os-skills/main/install.sh | bash -s -- workflows/cortes-virais
```

**Opcao C** — Manual:
```bash
git clone https://github.com/Gestao-Quatro-Ponto-Zero/g4os-skills.git
cp -r g4os-skills/workflows/cortes-virais ~/.g4os/workspaces/<workspace>/workflows/
```

## Uso

Apos instalado, use `/cortes-virais` no G4 OS e forneca a URL do YouTube.
