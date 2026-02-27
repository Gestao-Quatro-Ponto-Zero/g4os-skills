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

## Dataset 2: GDPVal (Opcional)

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
├── onet_task_statements.csv         # Tarefas O*NET (do HuggingFace)
├── onet_task_mappings.csv           # Tarefa → % conversas (do HuggingFace)
├── v4_task_ai_scores_lookup.json    # Gerado: scores de AI por tarefa
├── occupation_ai_summary.json       # Gerado: uso de AI por ocupacao
└── gdpval/                          # Opcional
    └── gdpval_prompts.json          # 220 prompts profissionais
```

## Sem Arquivos de Dados

Se voce nao baixar os arquivos de dados, o workflow vai:
1. Usar conhecimento do modelo para estimar scores de capacidade de AI (marcados como "estimativa")
2. Pular lookups baseados em dados
3. Ainda produzir um diagnostico completo — apenas com scores de confianca menor

O guia de scoring (`knowledge/scoring-guide.md`) documenta exatamente como a estimativa funciona sem dados.
