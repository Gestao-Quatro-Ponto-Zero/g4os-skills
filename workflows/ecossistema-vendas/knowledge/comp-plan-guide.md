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

## Ramp-up para Novos Vendedores

Nos primeiros meses, o acelerador agressivo (0-70% = 0x) pode desmotivar quem está aprendendo. Opções:

1. **Garantia de ramp** — pagar OTE cheio nos 2 primeiros meses independente de performance
2. **Floor mais baixo** — nos primeiros 3 meses, comissionar a partir de 50% (não 70%)
3. **Meta reduzida** — meta de 60% nos meses 1-2, 80% no mês 3, 100% a partir do mês 4

**Recomendação:** Garantia de ramp + meta reduzida. Proteção para o vendedor, clareza para a empresa.
