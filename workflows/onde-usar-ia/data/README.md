# Arquivos de Dados — Onde Usar IA

Este workflow usa dois datasets externos para scoring de capacidade de IA. O workflow **funciona sem eles** (usa estimativa do modelo), mas os scores ficam mais precisos com os dados.

## Setup Rapido

```bash
cd data/
./download.sh
```

Ou baixe manualmente seguindo as instrucoes abaixo.

## Dataset 1: Anthropic Economic Index (AEI)

Fonte: [Anthropic/EconomicIndex no HuggingFace](https://huggingface.co/datasets/Anthropic/EconomicIndex)
Licenca: CC-BY
Paper: [Which Economic Tasks are Performed with AI?](https://assets.anthropic.com/m/2e23255f1e84ca97/original/Economic_Tasks_AI_Paper.pdf)

### Arquivos necessarios

| Arquivo | Origem | Tamanho | Conteudo |
|---------|--------|---------|----------|
| `onet_task_statements.csv` | HuggingFace (release_2025_02_10/) | ~3.4 MB | Descricoes de tarefas por ocupacao O*NET |
| `onet_task_mappings.csv` | HuggingFace (release_2025_02_10/) | ~450 KB | % de conversas do Claude por tarefa |

### Download

```bash
# Tarefas O*NET (ocupacao → tarefas)
curl -L -o onet_task_statements.csv \
  "https://huggingface.co/datasets/Anthropic/EconomicIndex/raw/main/release_2025_02_10/onet_task_statements.csv"

# Mapeamento de tarefas (tarefa → % conversas)
curl -L -o onet_task_mappings.csv \
  "https://huggingface.co/datasets/Anthropic/EconomicIndex/raw/main/release_2025_02_10/onet_task_mappings.csv"
```

### Arquivos derivados (gerados pelo workflow)

Estes arquivos sao gerados no primeiro uso se voce tiver os dados brutos acima:

| Arquivo | Conteudo |
|---------|----------|
| `v4_task_ai_scores_lookup.json` | Scores de AI pre-computados por tarefa (chave em minusculo) |
| `occupation_ai_summary.json` | Media/max de uso de AI por ocupacao |

Para gera-los, execute o workflow e ele processa os CSVs em JSONs de lookup. Ou peca ao G4 OS: "Processe os dados do AEI em arquivos de lookup."

## Dataset 2: METR Horizon v1.1 (Incluido)

Fonte: METR Horizon Benchmark
Licenca: Dados publicos

| Arquivo | Tamanho | Conteudo |
|---------|---------|----------|
| `metr_horizon_v1_1.yaml` | ~12 KB | Horizontes de tempo p50/p80 por modelo de IA, com intervalos de confianca |

Este dataset e a **referencia primaria** para scoring de capacidade de IA. Ja esta incluido no repositorio — nao precisa de download.

O arquivo contem dados de ~25 modelos (de GPT-2 a Claude Opus 4.6) com metricas de horizonte de tempo — a duracao maxima de tarefa que cada modelo completa com 50% ou 80% de taxa de sucesso.

Ver `knowledge/metr-horizon-reference.md` para a tabela formatada e a metodologia de scoring.

## Dataset 3: GDPVal (Opcional)

Fonte: [OpenAI GDP Validation dataset](https://github.com/openai/evals)
Licenca: MIT

| Arquivo | Tamanho | Conteudo |
|---------|---------|----------|
| `gdpval/gdpval_prompts.json` | ~1.7 MB | 220 prompts profissionais reais de 44 ocupacoes |

Este dataset enriquece o guia de construcao de prompts com exemplos reais. O workflow funciona normalmente sem ele — o arquivo `prompt-building-guide.md` ja contem todos os exemplos.

## Estrutura Apos Setup

```
data/
├── README.md                        # Este arquivo
├── download.sh                      # Script de download
├── metr_horizon_v1_1.yaml           # METR Horizon v1.1 (incluido)
├── onet_task_statements.csv         # Tarefas O*NET (do HuggingFace)
├── onet_task_mappings.csv           # Tarefa → % conversas (do HuggingFace)
├── v4_task_ai_scores_lookup.json    # Gerado: scores de AI por tarefa
├── occupation_ai_summary.json       # Gerado: uso de AI por ocupacao
└── gdpval/                          # Opcional
    └── gdpval_prompts.json          # 220 prompts profissionais
```

## Sem Arquivos de Dados

Se voce nao baixar os arquivos AEI, o workflow vai:
1. Usar o **METR Horizon** (incluido) como referencia primaria para capacidade de IA — comparando duracao da tarefa com o horizonte do modelo
2. Pular validacao contra dados AEI
3. Ainda produzir um diagnostico completo com alta confianca para a dimensao de capacidade IA

O METR Horizon (`metr_horizon_v1_1.yaml`) ja esta incluido e e suficiente para scoring. Os dados AEI enriquecem a validacao mas nao sao obrigatorios.
