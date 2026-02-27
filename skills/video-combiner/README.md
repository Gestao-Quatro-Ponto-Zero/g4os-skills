# Video Combiner

Combina segmentos de video Hook + Body + CTA em todas as variacoes possiveis de ads com legendas automaticas em multiplos aspect ratios.

## O que faz

- Recebe pastas de video organizadas como Hook/Body/CTA
- Gera todas as combinacoes possiveis (ex: 7 hooks x 6 bodys x 3 CTAs = 126 variacoes)
- Transcreve audio automaticamente com Whisper e queima legendas
- Exporta em multiplos formatos: 16:9, 9:16, 4:5, 1:1
- Funciona com Google Drive ou arquivos locais

## Instalar

**Colar no G4 OS:**
```
Instale o skill "video-combiner" de https://github.com/Gestao-Quatro-Ponto-Zero/g4os-skills — clone o repo, copie skills/video-combiner/ para o diretorio de skills do meu G4 OS, instale as dependencias (brew install ffmpeg whisper-cpp), e confirme que esta funcionando.
```

**Ou via terminal:**
```bash
curl -sL https://raw.githubusercontent.com/Gestao-Quatro-Ponto-Zero/g4os-skills/main/install.sh | bash -s -- skills/video-combiner
```

### Dependencias

```bash
brew install ffmpeg whisper-cpp
```

## Uso

No G4 OS:

> "Combinar videos da pasta X" ou "Gerar variacoes de ads"

O skill guia voce por uma entrevista de setup, roda uma combinacao de teste para aprovacao, e depois processa tudo em lote.

## Arquivos

| Arquivo | Funcao |
|---------|--------|
| `SKILL.md` | Definicao do skill e fases do workflow |
| `icon.svg` | Icone de filmstrip |
| `references/technical.md` | Receitas FFmpeg, formato de legenda ASS, parametros de encoding |
| `scripts/batch_combine.py` | Script Python de processamento em lote (CLI standalone) |
