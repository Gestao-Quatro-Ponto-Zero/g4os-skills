# Guia de Comp Plan — Aceleradores e OTE

Referência detalhada para desenho de planos de comissionamento.

## Conceitos-Chave

### OTE (On-Target Earnings)
Quanto a pessoa ganha se bater **100% da meta**. É a soma do salário base + variável máximo regular.

```
OTE = Base + Variável (a 100%)
Split = Base / OTE (ex: 50/50, 33/67)
```

### Split Recomendado por Cargo

| Cargo | Split Fixo/Variável | Racional |
|-------|---------------------|----------|
| SDR/BDR | 50/50 a 60/40 | Previsibilidade + incentivo a volume |
| Closer/AE | 30/70 a 40/60 | Alta variável = alta motivação por deal |
| Account Manager | 50/50 a 60/40 | Equilíbrio entre retenção e expansão |
| CS/Sucesso | 70/30 a 80/20 | Mais fixo, variável por NPS/churn |
| Head/Diretor | 60/40 a 70/30 | Variável ligada a meta do time, não individual |

### Mecanismos de Comissão

**Por unidade** (melhor para SDR):
```
Comissão = unidades_entregues × valor_por_unidade × multiplicador
Ex: 18 reuniões × R$150 × 0.7 = R$1.890
```

**Por % de receita** (melhor para Closer/AM):
```
Comissão = receita_gerada × % × multiplicador
Ex: R$90.000 × 10% × 0.7 = R$6.300
```

## Método de Aplicação dos Aceleradores

### Flat (padrão — como na aula do Alfredo)

O multiplicador se aplica sobre TODA a comissão base do período.

```
Atingiu 90% → 0.7x sobre TODA a comissão
Comissão base = R$9.000
Comissão final = R$9.000 × 0.7 = R$6.300
```

**Vantagem:** Simples de explicar. O vendedor sabe exatamente: "se eu bater X, ganho Y."
**Desvantagem:** Salto abrupto entre faixas (passar de 85% para 86% muda de 0.5x para 0.7x).

### Progressivo (alternativa sofisticada)

Cada faixa se aplica apenas sobre a parcela correspondente.

```
Atingiu 90%:
- 0-70% → R$0 (0x)
- 71-85% (15pp) → R$2.250 × 0.5 = R$1.125
- 86-90% (5pp) → R$750 × 0.7 = R$525
Total = R$1.650
```

**Vantagem:** Mais justo, sem saltos abruptos.
**Desvantagem:** Mais difícil de comunicar e calcular.

**Recomendação:** Usar flat para times < 20 pessoas. Progressivo para operações maiores com ops de vendas.

## Contests (Incentivos de Curto Prazo)

### Boas Práticas

- **Duração curta** (1-2 semanas) — manter urgência
- **Meta clara e mensurável** — "quem agendar mais reuniões essa semana"
- **Prêmio tangível e imediato** — R$ cash, jantar, folga, experiência
- **Não substituir comissão** — contest é extra, não base

### Templates por Cargo

**SDR:**
- Sprint de Volume: maior número de reuniões agendadas na semana → R$500
- Qualidade: maior % de reuniões que viram oportunidade → R$300
- Rampa: bater meta 3 meses seguidos → promoção ou bonus de R$2.000

**Closer:**
- Deal do Mês: maior deal fechado → R$2.000
- Velocidade: menor ciclo médio de venda no mês → R$1.000
- Cross-sell: maior receita de produto secundário → R$1.500

**Account Manager:**
- Churn Zero: manter churn 0% no mês → R$1.500
- Expansão Record: maior upsell/cross-sell → R$2.000
- NPS Alto: manter NPS > 80 por 3 meses → bônus trimestral

## Custo de Comissão — Benchmarks

| Tipo de Negócio | % Comissão / Receita | Notas |
|-----------------|---------------------|-------|
| SaaS B2B | 8-15% | Inclui base + variável do time comercial |
| E-commerce | 3-8% | Mais mídia que equipe |
| Serviços | 10-20% | Time-intensive |
| Educação | 8-15% | Similar a SaaS |

**Red flags:**
- Comissão > 20% da receita → insustentável
- Comissão < 5% → incentivo fraco, perda de talentos
- Top performer ganhando < 2x do piso → spread insuficiente

## Modificadores por Condição de Venda

Além dos aceleradores por atingimento de meta, a comissão pode ter **modificadores (bônus ou deflators)** baseados nas condições da venda. Isso incentiva não só vender mais, mas vender melhor.

### Modal de Pagamento

O modal de pagamento impacta diretamente o cash flow da empresa. Vendas à vista têm custo financeiro zero; parcelamentos longos aumentam inadimplência e custo de capital.

| Condição | Modificador | Racional |
|----------|-------------|----------|
| PIX / À vista | **+10% a +20%** na comissão do deal | Cash flow imediato, risco zero |
| Cartão 1-3x | **Neutro** (1.0x) | Padrão de mercado |
| Cartão 4-6x | **-5% a -10%** | Custo da antecipação de recebíveis |
| Boleto parcelado 7-12x | **-10% a -15%** | Alto risco de inadimplência |
| Recorrência mensal (SaaS) | **Neutro** ou **+5%** se anual upfront | Modelo padrão SaaS; upfront é melhor |
| Pagamento anual antecipado | **+15% a +25%** | 12 meses de cash flow antecipado |

**Exemplo prático:**
```
Deal de R$120.000 (contrato anual)
Comissão base: 10% = R$12.000

→ Se pagou à vista (PIX): R$12.000 × 1.15 = R$13.800
→ Se parcelou em 12x boleto: R$12.000 × 0.85 = R$10.200
→ Diferença: R$3.600 por deal — incentivo claro para negociar pagamento melhor
```

### Carência (Grace Period)

Carência é quando o cliente começa a usar mas não paga imediatamente. Comum em SaaS (trial estendido), serviços (setup gratuito), e educação (primeira parcela futura).

| Condição | Modificador | Racional |
|----------|-------------|----------|
| Sem carência | **Neutro** (1.0x) | Padrão |
| Carência 30 dias | **-5%** | 1 mês de custo sem receita |
| Carência 60+ dias | **-10% a -15%** | Risco de churn antes do primeiro pagamento |
| Setup gratuito (< R$5K) | **Neutro** | Custo baixo, não penalizar |
| Implementação grátis (> R$5K) | **-10%** | Custo relevante absorvido pela empresa |

**Regra prática:** cada mês de carência = -5% na comissão do deal. Simples de comunicar.

### Desconto Concedido

Desconto reduz margem. O vendedor precisa sentir isso na comissão, senão o incentivo é sempre dar desconto para fechar.

| Desconto sobre tabela | Modificador | Racional |
|----------------------|-------------|----------|
| 0% (preço cheio) | **+10% a +15%** na comissão | Premiar quem vende o valor |
| 1-10% | **Neutro** (1.0x) | Faixa aceitável de negociação |
| 11-20% | **-15% a -20%** | Margem começa a comprometer |
| 21-30% | **-30% a -50%** | Desconto precisa aprovação do head |
| 31%+ | **-50% ou sem comissão** | Provavelmente deal ruim, exigir aprovação C-level |

**Modelo alternativo — Comissão sobre margem (não sobre receita):**
```
Receita do deal: R$100.000
Desconto: 20% → Receita líquida: R$80.000
Custo de servir: R$30.000
Margem: R$50.000

Comissão = 10% × margem = R$5.000 (em vez de R$10.000 sobre receita cheia)
```

Comissionar sobre margem elimina o problema de desconto sem precisar de tabelas de deflators — o vendedor sente o desconto naturalmente. Porém, exige visibilidade do custo de servir por deal.

### Combinando Modificadores

Modificadores são multiplicativos. Exemplo:

```
Closer: meta 100%, deal de R$100K
- Acelerador de meta: 1.0x (bateu 100%)
- Modal PIX: 1.15x
- Sem desconto: 1.10x
- Sem carência: 1.0x

Comissão = R$100K × 10% × 1.0 × 1.15 × 1.10 × 1.0 = R$12.650
(vs R$10.000 sem modificadores)

Mesmo deal com 25% de desconto e 60 dias carência:
Comissão = R$75K × 10% × 1.0 × 1.0 × 0.70 × 0.90 = R$4.725
```

**O spread é intencional** — incentiva o vendedor a negociar condições melhores.

### Simplificação para Times Menores

Para times < 10 vendedores, a tabela completa pode ser complexa demais. Versão simplificada:

| Condição | Modificador |
|----------|-------------|
| À vista ou anual upfront | **+15%** |
| Preço cheio (sem desconto) | **+10%** |
| Desconto > 15% | **-20%** |
| Carência > 30 dias | **-10%** |

4 regras simples, fáceis de comunicar e calcular.

## Pesquisa de Base Salarial

Antes de definir o OTE, é fundamental calibrar o salário base com o mercado. Pagar acima do mercado atrai talento mas reduz margem de variável; pagar abaixo dificulta contratação.

### Fontes de Pesquisa

| Fonte | O que oferece | Acesso | Atualização |
|-------|---------------|--------|-------------|
| **Glassdoor** | Salários reportados por cargo + empresa + cidade | Gratuito (com login) | Contínua |
| **Robert Half Salary Guide** | Faixas salariais por cargo + senioridade + região (BR) | PDF anual gratuito | Anual |
| **Catho Pesquisa Salarial** | Dados de cadastros de vagas + candidatos (BR) | Gratuito (parcial) | Contínua |
| **Vagas.com** | Distribuição salarial por cargo + região (BR) | Gratuito | Contínua |
| **Levels.fyi** | Salários em tech (incluindo sales em empresas tech) | Gratuito | Contínua |
| **LinkedIn Salary Insights** | Faixas por cargo + localidade + experiência | LinkedIn Premium | Contínua |
| **Gupy / Revelo / Guia Salarial** | Market data de plataformas de recrutamento | Varia | Anual/Contínua |

### Como Usar no Workflow

Quando o usuário não souber o salário base adequado, o workflow pode:

1. **Perguntar cargo + cidade + senioridade** — "Qual o cargo, cidade e nível de experiência?"
2. **Buscar via web search** — pesquisar "salário [cargo] [cidade] 2026 glassdoor" ou "guia salarial robert half 2026"
3. **Apresentar faixa** — "O mercado paga entre R$X e R$Y para [cargo] em [cidade]. Recomendo usar R$Z como base."
4. **Ajustar por contexto** — startup early-stage paga menos base + mais equity; empresa consolidada paga mais base

### Benchmarks Rápidos (Brasil, 2025-2026)

| Cargo | Cidade Tier 1 (SP/RJ) | Cidade Tier 2 | Remoto |
|-------|----------------------|---------------|--------|
| SDR/BDR Jr | R$2.500-3.500 | R$2.000-3.000 | R$2.200-3.200 |
| SDR/BDR Pleno | R$3.500-5.000 | R$2.800-4.000 | R$3.000-4.500 |
| Closer/AE Jr | R$4.000-6.000 | R$3.000-5.000 | R$3.500-5.500 |
| Closer/AE Pleno | R$6.000-9.000 | R$4.500-7.000 | R$5.000-8.000 |
| Closer/AE Sr | R$8.000-14.000 | R$6.000-10.000 | R$7.000-12.000 |
| Account Manager | R$5.000-9.000 | R$4.000-7.000 | R$4.500-8.000 |
| CS/Sucesso | R$4.000-7.000 | R$3.000-5.500 | R$3.500-6.000 |
| Head Comercial | R$12.000-25.000 | R$8.000-18.000 | R$10.000-20.000 |

**Caveat:** Esses são benchmarks aproximados. Sempre validar com pesquisa atualizada via web search no momento do uso. Mercado muda rápido, especialmente em tech/vendas.

### Fatores de Ajuste

| Fator | Impacto no Base |
|-------|----------------|
| Startup early-stage (< 50 funcionários) | -10% a -20% (compensa com equity/upside) |
| Empresa consolidada (> 500 func.) | +10% a +15% (estabilidade) |
| Segmento premium (fintech, SaaS enterprise) | +15% a +25% |
| Mercado aquecido (SDRs em 2024-2026) | +10% a +20% (escassez de talento) |
| Cidade com custo de vida alto | +10% a +15% |
| Full remote (empresa permite remoto de qualquer lugar) | Ajustar para custo médio, não de SP/RJ |

## Ramp-up para Novos Vendedores

Nos primeiros meses, o acelerador agressivo (0-70% = 0x) pode desmotivar quem está aprendendo. Opções:

1. **Garantia de ramp** — pagar OTE cheio nos 2 primeiros meses independente de performance
2. **Floor mais baixo** — nos primeiros 3 meses, comissionar a partir de 50% (não 70%)
3. **Meta reduzida** — meta de 60% nos meses 1-2, 80% no mês 3, 100% a partir do mês 4

**Recomendação:** Garantia de ramp + meta reduzida. Proteção para o vendedor, clareza para a empresa.
