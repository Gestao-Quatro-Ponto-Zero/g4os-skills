# RFM Analysis

Analise de segmentacao de clientes com scoring RFM (Recency, Frequency, Monetary), clustering K-Means, e insights acionaveis para campanhas de marketing.

## O que faz

- **Auto-detecta colunas** de qualquer CSV/XLSX transacional
- **Entrevista de contexto** — pergunta sobre produto, campanha e objetivo antes de rodar
- **RFM scoring** (quintis 1-5) com **11 segmentos** mapeados (Champions, At Risk, Lost, etc.)
- **K-Means clustering** com K auto-otimizado via metodo do cotovelo
- **Renderizacao nativa** no G4 OS — dashboards, datatables e checklists de acao direto no chat
- **Dataset de exemplo incluso** — 10K transacoes de e-commerce para demo imediata (100K completo via download script)

## Instalacao

```bash
curl -sL https://raw.githubusercontent.com/Gestao-Quatro-Ponto-Zero/g4os-skills/main/install.sh | bash -s -- skills/rfm-analysis
```

Ou cole no G4 OS:

```
Instale o skill "rfm-analysis" de https://github.com/Gestao-Quatro-Ponto-Zero/g4os-skills — clone o repo, copie skills/rfm-analysis/ para o diretorio de skills do meu G4 OS, confirme que pandas e scikit-learn estao instalados, e teste que esta funcionando.
```

## Uso

Digite `/rfm-analysis` no G4 OS e:

1. **Anexe um CSV/XLSX** com dados transacionais, ou
2. **Rode sem arquivo** para usar o dataset de exemplo (10K transacoes e-commerce)

O skill guia voce pelo mapeamento de colunas, coleta contexto do negocio, e apresenta resultados com:

- Dashboard de KPIs
- Tabela de segmentos ordenavel
- Barras de saude dos segmentos
- Perfis dos clusters K-Means
- Concentracao de receita
- Checklists de acoes recomendadas por prioridade

## Dependencias

- Python 3.8+
- `pandas`, `numpy`, `scikit-learn`, `plotly`, `openpyxl`

```bash
pip install pandas numpy scikit-learn plotly openpyxl
```

## Datasets de Exemplo

| Dataset | Linhas | Clientes | Descricao |
|---------|--------|----------|-----------|
| [ecommerce_sales_data.csv](datasets/ecommerce_sales_data.csv) | 10,000 (sample) | ~1,800 | E-commerce multi-categoria. 7 categorias, 1 ano de transacoes. Fonte: [Kaggle](https://www.kaggle.com/datasets/thedevastator/unlock-profits-with-e-commerce-sales-data). Rode `datasets/download_full.sh` para o dataset completo (100K). |

## Estrutura

```
rfm-analysis/
├── SKILL.md                              # Definicao do skill
├── README.md                             # Este arquivo
├── icon.svg                              # Icone para a UI
├── scripts/
│   └── rfm_analysis.py                   # Motor RFM + clustering
└── datasets/
    ├── ecommerce_sales_data.csv          # Dataset de exemplo (10K rows sample)
    └── download_full.sh                  # Script para baixar dataset completo (100K)
```
