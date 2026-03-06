# Mentalidade de Growth

Workflow interativo com 3 ferramentas para destravar crescimento. Baseado na aula do **Bruno Nardon** (Mentalidade de Growth, G4 GE Fev 2026).

## Ferramentas

| Ferramenta | Slug | O que faz |
|------------|------|-----------|
| **Escada de Valor** | `escada` | Mapeia produtos do mais barato ao mais caro, identifica gaps e sugere novos degraus para aumentar LTV |
| **Diagnóstico de Maturidade** | `maturidade` | Avalia 4 áreas (Marketing, Comercial, TI, Operações), identifica gargalo e recomenda foco |
| **Análise RFV** | `rfv` | Segmenta base de clientes com as 11 categorias do Nardon (Campeões → Perdidos) |

## Instalação no G4 OS

Cole no chat do G4 OS:

```
Instale o workflow "Mentalidade de Growth" do repositório g4os-skills: https://github.com/Gestao-Quatro-Ponto-Zero/g4os-skills/tree/main/workflows/mentalidade-growth
```

O G4 OS vai:
1. Baixar todos os arquivos (WORKFLOW.md, scripts, knowledge, datasets)
2. Instalar em `~/.g4os/workspaces/my-workspace/workflows/mentalidade-growth/`
3. Disponibilizar o comando `/mentalidade-growth`

## Como Usar

```
/mentalidade-growth
```

O workflow detecta automaticamente o que você precisa:
- Pediu "escada de valor" ou "LTV" → roda o módulo Escada
- Pediu "maturidade" ou "gargalo" → roda o Diagnóstico
- Pediu "rfv" ou "segmentar clientes" → roda a Análise RFV
- Pediu genérico → oferece diagnóstico rápido para escolher

### 3 Modos de Dados

1. **Demo** — sem dados? Rode com exemplos (B2B SaaS, E-commerce, Educação)
2. **Entrevista** — sabe do negócio mas não tem planilha? Coletamos conversando
3. **Import** — tem CSV/XLSX? Importe direto

## Estrutura

```
mentalidade-growth/
├── WORKFLOW.md              # Instruções completas do workflow
├── README.md                # Este arquivo
├── knowledge/
│   ├── growth-phases.md     # 5 fases de crescimento
│   ├── maturity-framework.md # Framework de maturidade + vantagem competitiva
│   └── value-ladder-guide.md # Escada de valor + 4 alavancas de LTV
├── scripts/
│   ├── value_ladder.py      # Gera visualização HTML da escada + análise JSON
│   └── maturity_diagnostic.py # Gera radar chart SVG + análise JSON
└── datasets/
    ├── demo-b2b-saas.json   # CloudMetrics: 80 func, R$600K/mês
    ├── demo-ecommerce.json  # ModaViva: 150 func, R$2M/mês
    └── demo-servicos-educacao.json # Academia de Líderes: 25 func, R$350K/mês
```

## Conexão com Outras Skills

- **`/rfm-analysis`** — O módulo RFV delega para esta skill (atualizada com nomenclatura PT-BR do Nardon)
- **`/ecossistema-vendas`** — Complementar: canais + budget + comp plan
- **`/onde-usar-ia`** — Se o gargalo é TI, sugere este workflow

## Frameworks da Aula

### 5 Fases de Crescimento
Fundação → Expansão Inicial → Fortalecimento → Expansão Estratégica → Maturação

### Progressão de Maturidade
Pessoas → Processos → Tecnologia → Escala

### 11 Categorias RFV
Campeões · Clientes Fiéis · Fiéis em Potencial · Novos Clientes · Promessas · Precisando de Atenção · Não Pode Perder · Em Risco · Quase Dormentes · Hibernando · Perdidos

### 4 Alavancas de LTV
1. Vender mais do mesmo
2. Vender algo diferente
3. Encontrar casos de uso correlatos
4. Lembrar que você existe
