# Stock Pick Analysis

Workflow completo de analise fundamentalista de acoes — valuation (DCF, Gordon, multiplos), peer comparison, sensitivity analysis, e recomendacao BUY/HOLD/SELL para horizontes de 12 meses e 5 anos.

## O que faz

Um comando (`/stock-pick`) que pesquisa uma empresa de ponta a ponta e entrega um relatorio estruturado de qualidade institucional.

| Etapa | O que resolve | Output |
|-------|---------------|--------|
| **Fundamentals** | "Quais sao os numeros dessa empresa?" | Overview financeiro, margens, crescimento, divida |
| **Valuation Models** | "Quanto vale essa acao?" | DCF, Gordon Growth, e/ou multiplos com premissas explicitas |
| **Peer Comparison** | "Como se compara com concorrentes?" | Tabela de multiplos (P/E, EV/EBITDA, P/B) vs peers do setor |
| **Sensitivity Analysis** | "E se as premissas mudarem?" | Tabelas de sensibilidade cruzando variaveis-chave |
| **Recommendation** | "Compro, seguro ou vendo?" | BUY/HOLD/SELL com tese para 12 meses e 5 anos |

## Como funciona

1. Usuario digita `/stock-pick` com ticker ou nome da empresa
2. Workflow pesquisa dados financeiros via web search
3. Roda modelos de valuation com premissas explicitas
4. Compara com peers do setor
5. Gera relatorio completo em Markdown com tabelas e graficos Mermaid

## Ideal para

- Avaliar acoes individuais (medio e longo prazo)
- Construir teses de investimento com base quantitativa
- Comparar empresas contra peers em multiplos
- Rodar DCF, Gordon Growth ou multiplos com tabelas de sensibilidade
- Produzir relatorio auto-contido para registro pessoal ou comite de investimentos

## Nao ideal para

- Startups pre-receita (sem cash flows para modelar)
- Empresas em distress/falencia (requer metodos especiais)
- Renda fixa, commodities ou derivativos
- Day-trading ou analise tecnica (foco e fundamentalista)

## Instalacao

Cole este prompt no G4 OS:

```
Instale o workflow "stock-pick" de https://github.com/Gestao-Quatro-Ponto-Zero/g4os-skills — clone o repo, copie workflows/stock-pick/ para o diretorio de workflows do meu G4 OS, e confirme que esta funcionando. Depois me apresente o que o workflow faz e como usar.
```

### Alternativa manual

```bash
git clone https://github.com/Gestao-Quatro-Ponto-Zero/g4os-skills.git
cp -r g4os-skills/workflows/stock-pick ~/.g4os/workspaces/my-workspace/workflows/
```

## Estrutura

```
stock-pick/
├── WORKFLOW.md              <- Instrucoes do workflow (o "cerebro")
├── README.md                <- Este arquivo
└── knowledge/               <- Bases de conhecimento para valuation
    ├── valuation-models.md       <- Modelos DCF, Gordon, multiplos
    ├── industry-metrics.md       <- Metricas-chave por setor
    └── sensitivity-framework.md  <- Framework de analise de sensibilidade
```

## Requisitos

- **G4 OS** (qualquer versao com suporte a workflows)
- **Acesso a web** (para pesquisar dados financeiros atualizados)

## Exemplos de uso

```
/stock-pick AAPL
> Analise completa da Apple com DCF, peers (MSFT, GOOG, META), e recomendacao

/stock-pick WEGE3
> Analise da WEG com multiplos do setor industrial brasileiro

/stock-pick "Nubank"
> Identifica ticker (NU), pesquisa e analisa
```
