# Referencia METR Horizon — Capacidade de IA por Duracao de Tarefa

## O que e o METR Horizon

O METR Horizon e um benchmark que mede a capacidade de modelos de IA em completar tarefas de duracao crescente. A metrica central e o **horizonte de tempo**: a duracao maxima de tarefa (em horas de trabalho humano especialista) que o modelo consegue completar com determinada taxa de sucesso.

**Metricas-chave:**
- **p80 Horizon**: Duracao maxima em que o modelo acerta ≥80% das tarefas — **alta confiabilidade**
- **p50 Horizon**: Duracao maxima em que o modelo acerta ≥50% das tarefas — **confiabilidade moderada**

**Analogia pratica**: Se uma tarefa leva X horas para um humano, e X esta dentro do p80 horizon do modelo, a IA provavelmente consegue fazer essa tarefa com >80% de sucesso.

**O que o METR testa**: Tarefas reais executadas em computador — pesquisa, analise, codigo, processamento de dados, escrita, automacao. Tarefas fisicas, presenciais ou que exigem interacao humana em tempo real nao fazem parte do benchmark.

## Tabela de Modelos (METR Horizon v1.1)

Ordenados por data de lancamento. Horizontes em **horas de trabalho humano**.

| Modelo | Lancamento | Score Medio | p80 (h) | p80 CI | p50 (h) | p50 CI | SOTA? |
|--------|-----------|-------------|---------|--------|---------|--------|-------|
| GPT-2 | Fev 2019 | 0.10 | 0.006 | — | 0.04 | — | ✅ |
| davinci-002 | Mai 2020 | 0.16 | 0.03 | [0.01, 0.06] | 0.15 | [0.07, 0.25] | ✅ |
| GPT-3.5 Turbo | Mar 2022 | 0.21 | 0.17 | [0.05, 0.29] | 0.60 | [0.23, 0.99] | ✅ |
| GPT-4 | Mar 2023 | 0.29 | 0.89 | [0.35, 2.57] | 3.99 | [1.96, 7.91] | ✅ |
| GPT-4 (Nov 2023) | Nov 2023 | 0.29 | 0.78 | [0.29, 2.33] | 4.04 | [1.95, 8.19] | ✅ |
| Claude 3 Opus | Mar 2024 | 0.29 | 0.64 | [0.19, 2.01] | 3.95 | [1.68, 8.64] | — |
| GPT-4 Turbo | Abr 2024 | 0.27 | 0.93 | [0.43, 2.23] | 3.73 | [1.94, 6.74] | — |
| GPT-4o | Mai 2024 | 0.34 | 1.27 | [0.55, 2.78] | 6.99 | [3.85, 12.41] | ✅ |
| Claude 3.5 Sonnet | Jun 2024 | 0.40 | 1.67 | [0.58, 4.50] | 11.40 | [5.44, 22.52] | ✅ |
| o1-preview | Set 2024 | 0.45 | 4.42 | [1.98, 9.25] | 20.33 | [11.61, 33.15] | ✅ |
| Claude 3.5 Sonnet v2 | Out 2024 | 0.45 | 2.60 | [0.91, 7.25] | 20.52 | [9.87, 40.41] | ✅ |
| o1 | Dez 2024 | 0.51 | 7.09 | [2.94, 17.34] | 38.83 | [21.69, 67.22] | ✅ |
| Claude 3.7 Sonnet | Fev 2025 | 0.56 | 12.09 | [4.54, 29.33] | 60.39 | [33.39, 107.30] | ✅ |
| o3 | Abr 2025 | 0.64 | 29.98 | [14.93, 56.86] | 119.73 | [72.98, 191.58] | ✅ |
| Claude 4 Opus | Mai 2025 | 0.62 | 20.43 | [8.69, 42.47] | 100.37 | [60.37, 163.28] | — |
| GPT-5 | Ago 2025 | 0.69 | 38.31 | [18.56, 70.31] | 203.01 | [114.21, 406.74] | ✅ |
| Claude 4.1 Opus | Ago 2025 | 0.62 | 23.46 | [10.50, 47.72] | 100.47 | [60.11, 158.02] | — |
| Gemini 3 Pro | Nov 2025 | 0.71 | 54.14 | [26.50, 105.52] | 224.33 | [136.87, 387.48] | ✅ |
| GPT-5.1 Codex Max | Nov 2025 | 0.71 | 50.63 | [26.95, 87.14] | 223.71 | [135.21, 395.14] | — |
| Claude Opus 4.5 | Nov 2025 | 0.73 | 49.43 | [20.88, 104.75] | 293.00 | [160.54, 638.62] | ✅ |
| GPT-5.2 | Dez 2025 | 0.75 | 66.00 | [32.16, 133.01] | 352.25 | [191.32, 862.34] | ✅ |
| **Claude Opus 4.6** | **Fev 2026** | **0.79** | **69.87** | **[26.21, 169.70]** | **718.81** | **[319.32, 3949.75]** | **✅** |
| GPT-5.3 Codex | Fev 2026 | 0.75 | 54.74 | [22.73, 123.22] | 349.53 | [192.05, 858.33] | — |

### Notas sobre a tabela

- **SOTA** = State of the Art no momento do lancamento (melhor score no benchmark naquela data)
- **CI** = Intervalo de confianca. Ranges largos indicam incerteza — a performance real pode variar significativamente
- Modelos Anthropic/Google usam scaffold `metr_agents/react`; modelos OpenAI usam `triframe_inspect/triframe_agent`
- Benchmark version: METR-Horizon-v1.1 (exceto GPT-2 e davinci-002 que usam v1.0)

## Mapeamento Ferramenta → Modelo de Referencia

Quando o usuario mencionar qual ferramenta de IA usa, mapear para o modelo de referencia:

| Ferramenta | Modelo de referencia (Mar 2026) | p80 (h) | p50 (h) |
|------------|-------------------------------|---------|---------|
| ChatGPT Plus / Pro / Enterprise | GPT-5.2 | 66 | 352 |
| ChatGPT com Codex | GPT-5.3 Codex | 55 | 350 |
| Claude Pro / G4 OS | Claude Opus 4.6 | 70 | 719 |
| Gemini Advanced | Gemini 3 Pro | 54 | 224 |
| Microsoft Copilot | GPT-5.1 (est.) | 51 | 224 |
| "Qualquer" / "Nao sei" | Frontier (Claude Opus 4.6) | 70 | 719 |

## Escala de Capacidade IA

Dado **T** = tempo estimado por ocorrencia da tarefa (em horas de trabalho humano), e **p80** e **p50** do modelo de referencia:

| Score | Condicao | Interpretacao |
|------:|----------|---------------|
| **5** | T ≤ 2h, tarefa digital, estruturada ou repetitiva | Bem dentro do horizonte de todos os modelos atuais. IA completa sozinha com alta taxa de sucesso |
| **4** | T ≤ 2h digital (com julgamento), OU T entre 2-12h digital | Dentro do horizonte da maioria dos modelos. IA faz bem com supervisao leve |
| **3** | T entre 12h e p80 do modelo, digital | Dentro do p80 do modelo. IA consegue, mas precisa de setup e orquestracao estruturada |
| **2** | T entre p80 e p50 do modelo, OU tarefa com forte componente relacional/contextual | No limite ou alem do horizonte de alta confiabilidade. IA ajuda parcialmente, humano lidera |
| **1** | T > p50 do modelo OU tarefa nao-digital (fisica, presencial) | Alem do horizonte. Ineficaz para automacao end-to-end |

### Pre-condicao: Tarefa Digital

O METR Horizon mede tarefas executadas em computador. **Pre-filtro obrigatorio:**

- ✅ Tarefa executada primariamente em computador (email, planilha, sistema, codigo, texto, dados)
- ❌ Tarefa que exige presenca fisica (visita a cliente, trabalho manual, producao)
- ❌ Tarefa que exige interacao humana em tempo real como componente CENTRAL (negociacao presencial, coaching 1:1, lideranca de equipe ao vivo)
- ⚠️ Tarefas hibridas: avaliar a parte digital separadamente (ex: "preparar apresentacao" = digital ✅ / "apresentar para diretoria" = presencial ❌)

**Se a tarefa nao e digital → Score maximo = 2** (IA pode ajudar na preparacao, mas nao na execucao).

### Modificadores Qualitativos

Apos calcular o score base por duracao, aplicar modificadores:

| Fator | Modificador | Exemplo |
|-------|------------|---------|
| Repetitiva / padronizada | +1 (max 5) | Classificar tickets, preencher formularios |
| Dados estruturados disponiveis | +0.5 (max 5) | Planilha ou banco de dados como input |
| Requer contexto organizacional profundo | -1 | Decisoes politicas, historico de cliente longo |
| Requer criatividade original | -0.5 | Design grafico original, estrategia inedita |
| Regulamentado / compliance-heavy | -0.5 | Laudos medicos, contratos regulados |
| Multi-step com dependencias externas | -1 | Precisa de aprovacao de terceiros no meio |

**Score final IA = clamp(score_base + modificadores, 1, 5)**

## Exemplos Praticos

| Atividade | Tempo/vez | Digital? | Score base | Modificadores | Score final |
|-----------|----------|----------|-----------|---------------|-------------|
| Classificar tickets N0 | 5min | ✅ | 5 | +1 (repetitiva) | **5** |
| Redigir email de follow-up | 15min | ✅ | 5 | +1 (repetitiva) | **5** |
| Analisar planilha de vendas | 2h | ✅ | 5 | +0.5 (dados estruturados) | **5** |
| Preparar proposta comercial | 3h | ✅ | 4 | -0.5 (contexto org) | **3.5** |
| Criar estrategia de marketing Q2 | 20h | ✅ | 3 | -0.5 (criatividade) | **2.5** |
| Desenvolver feature completa | 40h | ✅ | 3 | — | **3** |
| Negociar contrato presencialmente | 4h | ❌ | max 2 | -1 (relacional) | **1** |
| Visitar cliente | 4h | ❌ | max 2 | — | **1** |
| Migrar sistema legado | 200h | ✅ | 2 | -1 (deps externas) | **1** |

## Tendencia: Tempo de Duplicacao

O horizonte p50 **dobra a cada ~129 dias** (estimativa desde 2023, CI: 105-157 dias).

Implicacoes praticas:
- A cada ~4 meses, a IA consegue completar tarefas 2x mais longas/complexas
- Tarefas com Score 2-3 hoje provavelmente serao Score 4-5 em 6-12 meses
- Cadencia recomendada para revisitar o diagnostico: **a cada 6 meses**
- Score ≤ 2 nao significa "nunca" — significa "ainda nao com confianca"

## Fonte dos Dados

- Benchmark: **METR Horizon v1.1** (long_tasks commit: `799cc9c`)
- Scaffolds: `metr_agents/react` (Anthropic/Google) e `triframe_inspect/triframe_agent` (OpenAI)
- Doubling time (from 2023): **128.7 dias** (CI: 105-157)
- Ultimo modelo incluido: Claude Opus 4.6 e GPT-5.3 Codex (Fev 2026)
- Data de referencia: **Marco 2026**
- Proxima revisao recomendada: **Setembro 2026** (~3 doubling periods)
- Dados brutos: `data/metr_horizon_v1_1.yaml`
