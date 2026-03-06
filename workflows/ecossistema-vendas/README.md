# Ecossistema de Vendas

Workflow interativo com 3 ferramentas práticas para construir um ecossistema de vendas, baseado na aula do Alfredo Soares (G4 GE, Fev 2026).

## O que faz

Um comando (`/ecossistema-vendas`) que diagnostica e guia o usuário por 3 ferramentas:

| Ferramenta | O que resolve | Output |
|------------|---------------|--------|
| **Matriz de Canais** | "Não sei quais canais priorizar" | Matriz 2x2 interativa (HTML) com canais classificados em 4 quadrantes |
| **Budget 70/20/10** | "Meu budget não tem regra clara" | Análise de alocação atual vs ideal com plano de realocação |
| **Comp Plan Designer** | "Preciso redesenhar o comp plan" | Calculadora interativa (HTML) com aceleradores e simulação de cenários |

## Como funciona

1. Usuário digita `/ecossistema-vendas`
2. Workflow identifica a necessidade (ou faz diagnóstico rápido)
3. Coleta dados via **entrevista guiada**, **import de planilha**, ou **demo com dados fictícios**
4. Roda análise e gera artefatos interativos
5. Oferece o próximo módulo lógico

### 3 modos de input

- **Demo** — Dados fictícios realistas (B2B SaaS, E-commerce, ou Serviços/Educação). Perfeito para entender o framework sem ter dados.
- **Entrevista** — Coleta via conversa guiada. Aceita respostas aproximadas ("gasto uns R$50K em Meta").
- **Import** — CSV, XLSX ou JSON com mapeamento automático de colunas.

## Frameworks da aula aplicados

- **Matriz de Priorização 2x2** (Slide 47) — Validação × Potencial de Receita → Escalar / Apostar / Manter / Explorar
- **Regra 70/20/10** (Slide 49) — 70% Escala / 20% Aceleração / 10% Descoberta, com subdivisão interna
- **4 Eixos de Canal** (Slide 48) — Maior LTV, Menor CAC, Mais Escala, Menor Ciclo
- **Aceleradores de Comissão** (Slide 71) — 0-70%=0x, 71-85%=0.5x, 86-99%=0.7x, 100-119%=1x, 120%+=1.5x
- **Hunter vs Farmer** (Slide 57) — Estrutura de time com perfis complementares
- **OTE e Incentivos por Prazo** (Slides 68-70) — Curto/Médio/Longo prazo

## Instalação

### Opção 1: Copiar manualmente

```bash
# Clone o repo
git clone https://github.com/g4educacao/g4os-skills.git

# Copie o workflow para seu G4 OS
cp -r g4os-skills/workflows/ecossistema-vendas ~/.g4os/workspaces/my-workspace/workflows/
```

### Opção 2: Script de instalação

```bash
curl -s https://raw.githubusercontent.com/g4educacao/g4os-skills/main/install.sh | bash
```

## Estrutura

```
ecossistema-vendas/
├── WORKFLOW.md              ← Instruções do workflow (o "cérebro")
├── README.md                ← Este arquivo
├── knowledge/               ← Referências e guias
│   ├── framework-reference.md    ← Resumo dos 80 slides da aula
│   ├── channel-scoring-guide.md  ← Como pontuar canais (benchmarks por segmento)
│   └── comp-plan-guide.md        ← Aceleradores, OTE, contests em detalhe
├── scripts/                 ← Scripts Python para cálculos e visualizações
│   ├── channel_matrix.py         ← Gera matriz 2x2 interativa (HTML)
│   ├── budget_allocator.py       ← Analisa alocação e gera report (HTML)
│   └── comp_plan.py              ← Simulador de comp plan (HTML + .md)
└── datasets/                ← Dados demo por segmento
    ├── demo-b2b-saas.json        ← 12 canais, R$500K budget, 12 vendedores
    ├── demo-ecommerce.json       ← 10 canais, R$200K budget, 6 pessoas
    └── demo-servicos-educacao.json ← 10 canais, R$300K budget, 10 pessoas
```

## Requisitos

- **G4 OS** (qualquer versão com suporte a workflows)
- **Python 3** (para os scripts de visualização — sem dependências externas)

## Exemplos de uso

```
/ecossistema-vendas
> "Quero priorizar meus canais de marketing"
→ Roda Matriz de Canais

/ecossistema-vendas
> "Preciso montar o comp plan do time de vendas"
→ Roda Comp Plan Designer

/ecossistema-vendas
> "Quero ver como funciona com um exemplo"
→ Oferece demo B2B SaaS, E-commerce, ou Serviços
```

## Referência

Baseado na aula "Ecossistema de Vendas" — Alfredo Soares, G4 GE, Fevereiro 2026.
