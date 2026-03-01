# Playbook Reference — Cortes Virais

## Conceito Central

Cada corte segue a estrutura **HOOK TEASER + CORPO**:

- **HOOK (2-3.5s)**: O trecho MAIS polêmico/impactante do segmento. É um corte seco que funciona como teaser — vem de OUTRO momento (o "money shot"). Não é o começo do segmento.
- **CORPO (57-88s)**: O segmento completo, começando do início natural da conversa. Não continua de onde o hook parou.
- **TOTAL (60-90s)**: Hook + Corpo concatenados. Os 3 primeiros segundos são de alto impacto.

## Filosofia de Seleção — Otimizar para Métricas de Plataforma

As plataformas de vídeo curto (Reels, Shorts, TikTok) rankeiam por 3 métricas, nesta ordem:

1. **Retenção 3 segundos** — % que não swipa. Decide se o vídeo é distribuído.
2. **Like/view ratio** — Ressonância emocional. Decide o alcance após distribuição inicial.
3. **Share/view ratio** — Viralidade. Decide se ultrapassa a bolha de seguidores.

**Regra de ouro**: 4 cortes matadores > 7 cortes medianos. Nunca fazer padding pra atingir um número.

### Arquétipos de Hook (por efetividade)

| Arquétipo | Exemplo | Por que funciona |
|-----------|---------|-----------------|
| Contradição | "Eu era de esquerda e hoje..." | Quebra expectativa — viewer precisa de resolução |
| Claim audaciosa | "Toda empresa deveria demitir o RH" | Ultraje = atenção instantânea |
| Número chocante | "R$50 milhões de prejuízo" | Concreto, visceral, "como?!" |
| Confronto direto | "Você está completamente errado" | Conflito = engagement. Viewer toma lado |
| Vulnerabilidade | "Eu quase quebrei a empresa" | Humaniza + tensão |
| Violação de status | "CEO que ganha salário mínimo" | Disrupção de expectativa social |
| Pensamento cortado | "O problema do Brasil é que..." (cut) | Open loop clássico |

**O hook DEVE criar um open loop** — uma pergunta que o viewer não consegue responder sem assistir.

### Scoring Obrigatório (1-10)

Cada corte recebe 3 notas:
- `retention_3s`: O hook é impossível de scrollar? (mínimo 7)
- `like_ratio`: O segmento gera identificação ou "aha"?
- `share_ratio`: A pessoa vai mandar pra alguém?
- **Total mínimo: 20/30**

### O que faz um bom segmento (corpo)
1. **Paga a promessa do hook** — Se o hook disse "R$50M de prejuízo", o corpo DEVE explicar como/por quê
2. Arco narrativo completo (começo → desenvolvimento → conclusão) em 57-88s
3. Conteúdo auto-contido — não precisa de contexto anterior
4. **Escalação emocional** — energia no minuto 1:00 > energia no 0:15. Build-up, não flat
5. **Densidade de frases quotáveis** — segmentos com 2-3 frases compartilháveis >> 1
6. **Potencial de polarização** — opiniões que dividem geram mais comentários que unanimidade

### O que NÃO selecionar
- Conselhos genéricos ("trabalhe duro", "tenha foco") — zero share
- Preâmbulos longos antes de chegar no ponto — mata retenção
- Entrevistador e entrevistado concordando — boring
- Delivery monótona sem variação de energia — swipe

## Refinamento de Timestamps

### Por que refinar
Timestamps da transcrição rough são nível parágrafo — imprecisão de 0.5-2s. Um hook que começa 0.3s tarde perde a primeira palavra. Um body que termina no meio de frase soa amador.

### Regras de Snap

| Boundary | Regra | Lógica |
|----------|-------|--------|
| hook_start | Início da primeira palavra da frase. Incluir 0.1-0.3s de respiro antes se existir. | Entrada limpa |
| hook_end | Fim da última palavra + 0.05-0.15s de silêncio. Para open loops, cortar no fim da última palavra completa — a abruptidão É o hook. | Saída sem clipar fonema |
| body_start | Início da frase/pensamento. Micro-pausa ou respiro 0.1-0.2s antes da primeira palavra. | Não parece que entrou no meio da conversa |
| body_end | Fim de frase completa. Preferir: (1) ponto final, (2) pausa dramática, (3) punchline, (4) frase de conclusão forte. + 0.2-0.4s trailing silence. | Saída intencional |

### Validações de Áudio
- **Hook volume**: `mean_volume` deve ser > -30 dB. Abaixo disso = momento errado
- **Hook duration**: 1.5-3.5s. Fora disso, ajustar
- **Transição hook→body**: Não pode ter salto de volume abrupto. Se energias são muito diferentes, usar fade-in de 0.1s no body
- **Body end — preferir punchline**: Se há frase forte ±5s do body_end proposto, ajustar pra TERMINAR nela. Última impressão importa.

## Transcrição — Arquitetura de Dois Estágios

> **LESSON LEARNED**: Transcrição é o passo mais crítico do workflow. Erros de transcrição viram erros visíveis nas legendas.

### Estágio 1: Transcrição Rough (para selecionar cortes)
- **Método**: Source de AI com `summarize_url` ou source de web scraping com captions do YouTube
- **Qualidade**: Paragraph-level OK — só precisa do conteúdo para identificar momentos
- **Velocidade**: Segundos (API call)

### Estágio 2: Transcrição Final (para legendas)
- **Método**: `whisper-cli -m ggml-medium.bin` por segmento
- **Qualidade**: Word-level com timestamps precisos
- **Velocidade**: ~15-30s por segmento de 90s no Apple Silicon (Metal GPU)
- **Modelo mínimo**: `medium` (1.5GB) — modelos menores (base, small) produzem erros em nomes próprios

### Erros Conhecidos do Whisper em PT-BR
| Input | Whisper base/small | Whisper medium |
|-------|-------------------|----------------|
| "CEO" | "se ou" / "seou" | "CEO" ✓ |
| "G4" | "já quatro" / "jiquatro" | "G4" ✓ |
| Música/silêncio | "Liziziziziz..." (alucinação) | Menos frequente |
| "Bolsa Família" | "bolsa famia" | "Bolsa Família" ✓ |

### Formato de Output do whisper-cli

```bash
whisper-cli -m "$MODEL" -l pt -ojf -f segment.wav -of output_prefix
```

Output `output_prefix.json`:
```json
{
  "transcription": [{
    "timestamps": {"from": "00:00:00,000", "to": "00:00:05,760"},
    "offsets": {"from": 0, "to": 5760},
    "text": " A tradução é o seguinte...",
    "tokens": [{
      "text": " A",
      "offsets": {"from": 0, "to": 90},
      "id": 316,
      "p": 0.194
    }, ...]
  }]
}
```

**Atenção**: `offsets` são em **milissegundos**. `timestamps` usam formato SRT com **vírgula** (`00:00:00,000`) não ponto. O script `transcribe_segment.sh` converte para o formato padrão `[{text, start, end}]` em segundos.

### Filtro de Alucinação
Após parsing, remover palavras com padrão repetitivo: se `texto[:2] * 5` está contido no texto, é alucinação.

## Especificações Técnicas das Legendas

### Arquivo ASS — Header
```
[Script Info]
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Style: Default,Arial Black,58,&H00FFFFFF,&H0000FFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,4.5,0,2,50,50,280,1
```

### Parâmetros
| Parâmetro | Valor | Razão |
|-----------|-------|-------|
| PlayResX/Y | 1080x1920 | Canvas vertical 9:16 |
| Fontname | Arial Black | Fonte bold legível em tela pequena |
| Fontsize | 52-58 | Legível em celular |
| PrimaryColour | `&H00FFFFFF` | Branco (padrão) |
| OutlineColour | `&H00000000` | Preto (contraste) |
| Outline | 4.5 | Espessura ideal |
| Alignment | 2 | Bottom center |
| **MarginV** | **280** | **Acima da UI do Instagram (180 é muito baixo — testado em produção)** |

### Highlight Dinâmico
- Palavra ativa: `\c&H00FFFF&` (amarelo BGR) + `\fscx110\fscy110` (110% escala)
- Demais palavras: `\c&HFFFFFF&` (branco) + `\fscx100\fscy100` (100% escala)
- TUDO EM CAIXA ALTA

### Agrupamento de Palavras
- 3-5 palavras por grupo
- Quebra em pausa > 0.35s
- Quebra em pontuação (. ? ! ,)

### Timestamps nas Legendas
Quando usando transcrição per-segment (whisper-medium), os timestamps no `_words.json` são **relativos ao início do segmento** (começam em 0). Passar `--start 0 --end {segment_duration}` para `generate_ass.py`.

## Cores ASS (formato BGR, NÃO RGB)
- `&H00FFFF&` = amarelo (B=00, G=FF, R=FF)
- `&H00FFFFFF&` = branco
- `&H00000000&` = preto

## Enquadramento 9:16

### Abordagem: Two-Pass Scene Detection

O crop é feito em duas passadas:

1. **Scene Detection (fast)** — a cada 5 frames (dos 1fps), classifica o tipo de cena e posição do speaker. Detecta onde a câmera muda.
2. **Detailed Per-Scene Analysis** — 2-3 frames por cena, análise detalhada de posição facial, gestos, overlays. Calcula crop filter em pixels.
3. **Rendered Crop Previews** — aplica o crop em frames reais e gera preview 1080x1920 para o usuário validar.
4. **User Validation** — usuário vê exatamente como o vídeo vai ficar e aprova ou ajusta.

### Scene Types

| Type | Descrição | Crop típico |
|------|-----------|-------------|
| `close_up_single` | 1 rosto >40% do frame | Centralizado no rosto |
| `close_up_two` | 2 rostos >25% cada | Crop no speaker ativo |
| `wide_two` | 2 pessoas, frame amplo | Crop no guest (geralmente esquerda) |
| `wide_group` | 3+ pessoas | Crop no speaker, pode precisar de ajuste dinâmico |
| `cutaway` | B-roll, gráficos | Center crop padrão |
| `screen_share` | Apresentação/tela | Center crop, margin_v pode precisar de ajuste |

### Crop Filter — Pixel Precision

Em vez do genérico `crop=ih*9/16:ih` (sempre centralizado), usamos filtros com offset em pixels:

```python
def calc_crop_filter(center_x_pct, frame_w=1920, frame_h=1080):
    crop_w = int(frame_h * 9 / 16)  # 607 para 1080p
    face_x = frame_w * center_x_pct / 100
    crop_x = max(0, min(int(face_x - crop_w / 2), frame_w - crop_w))
    return f"crop={crop_w}:{frame_h}:{crop_x}:0"
```

| Posição | center_x_pct | Filtro resultado |
|---------|-------------|-----------------|
| Centro | 50% | `crop=607:1080:656:0` |
| Esquerda | 30% | `crop=607:1080:269:0` |
| Direita | 70% | `crop=607:1080:1043:0` |

### crop_profile.json Schema (v2)

```json
{
  "video_resolution": "1920x1080",
  "analysis_method": "two_pass_scene_detection",
  "subtitle_margin_v": 280,
  "user_validated": true,
  "cuts": {
    "corte_name": {
      "hook_crop": "crop=607:1080:656:0",
      "has_camera_switch": false,
      "crop_confidence": "high",
      "scenes": [
        {
          "from_sec": 0, "to_sec": 70,
          "crop": "crop=607:1080:656:0",
          "scene_type": "close_up_single"
        }
      ]
    }
  }
}
```

### Processamento com Troca de Câmera

Quando `has_camera_switch = true`:
1. Dividir o body nos pontos de troca de cena
2. Cropar cada parte com seu filtro específico (pixel-precise)
3. Concatenar: hook + body_part0 + body_part1 + ...

### Crop Preview Rendering

Antes de processar os vídeos, o workflow renderiza previews 1080x1920 para cada cena:
```bash
ffmpeg -y -i frame.jpg -vf "{scene_crop},scale=1080:1920" preview.jpg
```
O usuário vê exatamente o que o viewer vai ver e aprova ou pede ajuste.

## Revisão de Legendas pelo Usuário

### Checkpoint Obrigatório

Após transcrição per-segment com Whisper medium, o texto de TODOS os cortes é apresentado ao usuário ANTES de gerar os arquivos ASS finais.

### Formato de Apresentação
- Hook text em destaque (é o que aparece nos primeiros 3s)
- Body text completo em CAPS (como vai aparecer no vídeo)
- Flags automáticos: anglicismos (CEO, startup), números, nomes próprios
- Contagem de palavras e duração

### Fluxo
1. Transcrição Whisper medium → `_words.json`
2. Apresentar texto de todos os cortes ao usuário
3. Usuário corrige erros ("troca X por Y no corte N")
4. Editar `_words.json` → regenerar `.ass`
5. Confirmar → processar vídeos

### Por que é obrigatório
Em testes de produção, "CEO" virou "se ou" nas legendas ao usar Whisper base. Se não tivesse revisão manual, ficaria eternizado no vídeo. Com Whisper medium é raro, mas 30s de review previne 100% dos erros visíveis.

## Specs Finais dos Vídeos
| Parâmetro | Valor |
|-----------|-------|
| Resolução | 1080x1920 |
| Codec vídeo | H.264 (libx264) |
| Codec áudio | AAC 128kbps, 44.1kHz |
| CRF | 23 |
| Preset | fast |
| Pixel format | yuv420p |

## Erros Conhecidos e Lições

| Problema | Causa | Fix |
|----------|-------|-----|
| Google AI 500/524 em audio >20MB | Limite de tamanho do serviço de AI | Usar whisper-cli local |
| "CEO" → "se ou" nas legendas | Whisper base/small não conhece anglicismos | Usar modelo medium |
| Alucinação "Liziziz..." | Música/silêncio no início do áudio | Filtro de padrão repetitivo no parser |
| MarginV 180 sob UI do Instagram | Muito baixo | Default 280 |
| `mkdir /final` → read-only filesystem | Path relativo sem $OUTPUT_DIR | Validar paths absolutos |
| SRT comma `00:00:00,000` → float crash | `float()` não aceita vírgula | Usar campo `offsets` (milissegundos) |
| Context collapse após processar transcript | 5000+ palavras no contexto principal | Nunca colocar transcript no main context — usar sub-agents |
