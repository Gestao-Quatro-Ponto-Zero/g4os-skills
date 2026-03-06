---
name: "Ecossistema de Vendas"
description: "Construa seu ecossistema de vendas com 3 ferramentas práticas — priorização de canais, alocação de budget 70/20/10, e plano de comissionamento com aceleradores. Framework Alfredo Soares (G4 GE 2026)."
icon: "🎯"
---

# Ecossistema de Vendas

Workflow interativo com 3 ferramentas práticas para construir um ecossistema de vendas. Baseado na aula do Alfredo Soares (Ecossistema de Vendas, G4 GE Fev 2026).

**Scripts**: `workflows/ecossistema-vendas/scripts/`
**Knowledge**: `workflows/ecossistema-vendas/knowledge/`
**Datasets demo**: `workflows/ecossistema-vendas/datasets/`

Todas as referências a `scripts/`, `knowledge/` e `datasets/` neste arquivo são relativas ao diretório deste workflow. Use caminhos absolutos ao executar comandos.

## Ferramentas Disponíveis

| Ferramenta | Slug | O que faz |
|------------|------|-----------|
| **Matriz de Canais** | `canais` | Classifica canais em 4 quadrantes (Escalar/Apostar/Manter/Explorar) baseado em validação e potencial |
| **Budget 70/20/10** | `budget` | Analisa alocação de budget vs regra 70% Escala / 20% Aceleração / 10% Descoberta |
| **Comp Plan** | `comp` | Desenha planos de comissionamento com aceleradores por faixa de atingimento |

## Resultado Final (por ferramenta)

**Canais**: Matriz 2x2 interativa (HTML) + tabela de gap + recomendações por quadrante
**Budget**: Comparação atual vs ideal + plano de realocação + subdivisão interna
**Comp Plan**: Calculadora interativa (HTML) + simulação de cenários + documento compartilhável (.md)

---

## ONBOARDING & CONFIGURAÇÃO

Antes de rodar qualquer módulo pela primeira vez, entender a realidade do usuário. Isso NÃO é um questionário longo — são 2-3 perguntas que mudam tudo.

### Passo 1: Descobrir fontes de dados

> Antes de começar: você tem algum desses dados acessíveis?
> - CRM (Salesforce, HubSpot, Pipedrive, etc.)
> - Planilha de canais/budget (Excel, Google Sheets)
> - Plataforma de ads (Meta, Google Ads)
> - ERP ou sistema financeiro
> - Nenhum — vamos construir do zero

**Se tem dados em ferramentas conectadas ao G4 OS (MCPs ativos):**
- Verificar quais sources estão disponíveis na sessão
- Se Databricks/HubSpot/Salesforce/Meta Ads/Notion estão ativos → oferecer puxar dados automaticamente
- Se Google Sheets está ativo → oferecer importar direto da planilha
- Exemplo: "Vi que você tem o Databricks conectado. Quer que eu puxe os dados de canais/receita de lá?"

**Se tem dados em planilha/arquivo:**
- Pedir para anexar ou colar
- Auto-mapear colunas com fuzzy match
- Validar antes de prosseguir

**Se não tem dados:**
- Modo entrevista (coletar conversando) ou modo demo (dados fictícios para entender o framework)

### Passo 2: Contextualizar os exemplos

Os datasets demo e valores default (aceleradores, faixas salariais, benchmarks de budget) são **pontos de partida, não verdade absoluta**. Sempre:

1. **Apresentar o default** — "O framework do Alfredo sugere X"
2. **Perguntar se faz sentido** — "Na sua realidade, isso se aplica? O que mudaria?"
3. **Ajustar antes de rodar** — Customizar os parâmetros para a realidade do usuário
4. **Nunca rodar com defaults sem confirmar** — Mesmo no demo, explicar que os números são ilustrativos

Exemplos de ajustes comuns:
- Acelerador 0-70% = 0x é agressivo demais para time em ramp-up → sugerir floor de 50%
- Regra 70/20/10 pode ser 60/25/15 para empresas em fase de crescimento
- Benchmarks salariais mudam por cidade, segmento e tamanho de empresa

### Passo 3: Validar antes de executar

Antes de rodar qualquer análise:
1. **Resumir os dados coletados** — mostrar em tabela ou lista
2. **Confirmar com o usuário** — "Esses dados estão corretos? Algo a ajustar?"
3. **Sinalizar inconsistências** — "Você disse LTV:CAC de 12x mas o budget é só 2% — está certo?"
4. **Só processar depois do OK**

### Integração com MCPs e APIs

Se MCPs relevantes estão ativos na sessão, usar proativamente:

| Source | Como usar | Módulo |
|--------|-----------|--------|
| **Databricks** | Puxar dados de receita, canais, pipeline | Canais, Budget |
| **Meta Ads / Google Ads** | Dados de spend, CPL, ROAS por canal | Canais, Budget |
| **Salesforce / HubSpot** | Pipeline, win rate, cycle time, comp data | Todos |
| **Google Sheets** | Importar/exportar planilhas de dados | Todos |
| **Notion** | Buscar docs de planejamento, OKRs | Contexto |
| **Slack** | Enviar resultado para canal ou pessoa | Todos |

**Regra**: Se o MCP está ativo e o dado existe lá, oferecer puxar automaticamente em vez de pedir pro usuário digitar.

---

## ROTEAMENTO — Como decidir o que rodar

### Regra #1: Se o usuário pedir algo específico, vá direto

Mapeie a intenção do usuário para a ferramenta:

| Usuário diz | Ferramenta |
|-------------|-----------|
| "priorizar canais", "quais canais investir", "matriz de canais", "onde anunciar" | **Canais** |
| "budget", "alocação", "quanto gastar", "70/20/10", "distribuir verba" | **Budget** |
| "comissão", "comp plan", "remuneração variável", "acelerador", "OTE", "quanto pagar vendedor" | **Comp Plan** |
| "ecossistema", "diagnóstico", "por onde começar", sem especificar | **Diagnóstico** (abaixo) |

### Regra #2: Se não ficou claro, faça UM diagnóstico rápido

> Tenho 3 ferramentas práticas baseadas na aula do Alfredo Soares. Me conta: qual desses desafios é mais urgente pra você?
>
> 1. **Não sei quais canais priorizar** — vou te ajudar a classificar cada canal por validação e potencial de receita
> 2. **Meu budget não tem regra clara** — vou analisar sua alocação atual vs a regra 70/20/10
> 3. **Preciso redesenhar o comp plan do time** — vou desenhar um plano com aceleradores e simular cenários
>
> Ou se quiser, rodo as 3 em sequência (canais → budget → comp plan).

### Regra #3: Nunca carregue contexto que não vai usar

- Se o usuário quer só Comp Plan, NÃO explique a matriz de canais
- Execute apenas o módulo relevante
- Ao final de cada módulo, ofereça o próximo lógico (ver Conexões)

### Conexões entre ferramentas

```
Canais → Budget (canais classificados viram input de alocação)
Budget → Comp Plan (budget de equipe informa OTE)
Comp Plan → standalone (não depende dos outros)
```

Ao terminar um módulo:
> Quer rodar a próxima ferramenta? O output daqui alimenta [próximo módulo] diretamente.

---

## DADOS — 3 Modos de Input

Cada ferramenta aceita 3 modos. Detecte automaticamente:

### Modo 1: Demo (sem dados)

Usar quando: usuário não tem dados, quer entender o framework, ou pediu "exemplo".

> Quer ver como funciona com um exemplo prático? Tenho demos para 3 tipos de negócio:
> - **B2B SaaS** — 12 canais, R$500K/mês de budget, time de 12 vendedores
> - **E-commerce** — 10 canais, R$200K/mês, time de 8
> - **Serviços/Educação** — 8 canais, R$300K/mês, time de 10
>
> Qual se parece mais com seu negócio?

Carregar o dataset correspondente de `datasets/` e rodar direto.

**IMPORTANTE sobre demos:**
- Demo é ferramenta de aprendizado, não deliverable final
- Durante o demo, ir explicando o racional: "Esse canal está no quadrante APOSTAR porque..."
- **Ao final do demo, SEMPRE transicionar para dados reais:**

> Essa foi uma análise com dados fictícios para você entender o framework. Agora que você viu como funciona, quer rodar com seus dados reais? Posso te guiar — começa me dizendo quais canais você usa e um budget aproximado.

- Se o usuário quiser ficar no demo, tudo bem — mas oferecer a transição

### Modo 2: Entrevista (tem conhecimento, não tem planilha)

Usar quando: usuário sabe do negócio mas não trouxe arquivo.

Coletar dados via conversa guiada. Regras:
- Aceitar respostas aproximadas ("gasto uns R$50K em Meta Ads")
- Aceitar lotes ("Meta 50K, Google 30K, SEO 15K, o resto é pouco")
- NÃO forçar precisão — melhor rodar com dados aproximados do que não rodar
- Validar antes de processar ("Entendi X canais, budget total Y. Confere?")
- **Sugerir ajustes se algo não faz sentido**: "Você disse que gasta R$100K em LinkedIn com LTV:CAC de 1.5x — isso é preocupante, vale revisitar?"
- **Checar se tem MCP ativo que pode preencher gaps**: "Vi que você tem o Meta Ads conectado. Quer que eu puxe os dados de spend de lá?"

### Modo 3: Import (tem dados prontos)

Usar quando: usuário menciona "tenho uma planilha", "CSV", "arquivo", ou anexa algo.

Aceitar:
- **CSV/XLSX**: Auto-mapear colunas (fuzzy match nos nomes)
- **JSON**: Validar schema contra o modelo esperado
- **Texto colado**: Parsear tabela markdown ou lista
- **Google Sheets** (se MCP ativo): Puxar direto da planilha compartilhada
- **Templates XLSX do workflow**: Reconhecer automaticamente os templates que geramos (`templates/`)

Se o mapeamento automático falhar, mostrar as colunas encontradas e perguntar qual é qual.

**Após importar, SEMPRE:**
1. Mostrar os dados importados em tabela
2. Sinalizar campos vazios ou suspeitos
3. Perguntar se quer ajustar algo antes de rodar
4. Oferecer os templates XLSX se o formato do usuário estava bagunçado

---

## MÓDULO 1: MATRIZ DE CANAIS

**Conceito (Slide 47-48 da aula):** Plotar canais em 2 eixos — Validação (0-10) e Potencial de Receita (0-10) — para classificar em 4 quadrantes e decidir onde investir.

### Quadrantes

| Quadrante | Validação | Potencial | Ação | Budget |
|-----------|-----------|-----------|------|--------|
| **ESCALAR** | >= 6 | >= 6 | Colocar dinheiro, escalar | 70% |
| **APOSTAR** | < 6 | >= 6 | Investir para validar rápido | 20% |
| **MANTER** | >= 6 | < 6 | Manter com eficiência | Residual |
| **EXPLORAR** | < 6 | < 6 | Teste rápido, cortar se falhar | 10% |

### Coleta de dados

Para cada canal, coletar:

| Campo | Obrigatório | Como perguntar |
|-------|-------------|----------------|
| nome | Sim | "Liste seus canais de aquisição" |
| validação (0-10) | Sim | "De 0 a 10, quanto esse canal já foi testado com dados reais?" |
| potencial (0-10) | Sim | "De 0 a 10, qual o potencial máximo de receita?" |
| budget_mensal ou % | Sim | "Quanto % do budget vai pra cada canal?" |
| ltv_cac | Não | "Se souber, qual o LTV:CAC?" |
| ciclo_venda_dias | Não | "Quantos dias em média até fechar?" |

**Dicas de scoring para o usuário:**
- 0-3: Não testou ou testou pouco, sem dados confiáveis
- 4-6: Tem alguns dados mas inconsistentes ou pouco volume
- 7-10: Dados sólidos, resultado previsível, pode projetar com confiança

Se o usuário não souber classificar, oferecer lista padrão por segmento (consultar `knowledge/channel-scoring-guide.md`).

### Processamento

```bash
python3 {workflow_dir}/scripts/channel_matrix.py \
  --input-json '<json>' \
  --output-dir '/tmp/channel-matrix-{timestamp}'
```

### Apresentação dos resultados

**Ordem exata — seguir sem pular:**

1. **KPI Dashboard** (jsonrender) — Total canais, budget total, canais no ESCALAR, LTV:CAC médio, alert se >40% em canais não validados

2. **Matriz Visual** (web-app-preview) — HTML interativo gerado pelo script. Scatter com bolhas coloridas por quadrante, tamanho = % budget. Hover com detalhes.

3. **Tabela de Canais** (datatable) — Colunas: Canal, Quadrante (badge), Validação, Potencial, Budget Atual (%), Budget Ideal (%), Gap, LTV:CAC. Ordenar por quadrante → potencial desc.

4. **Recomendações por Quadrante** (jsonrender Tabs) — Uma aba por quadrante com Checklist de ações específicas para cada canal. NÃO recomendações genéricas — usar o nome do canal e dados coletados.

5. **Gap Analysis** (markdown) — 3-5 bullets: onde sobre-investindo, onde sub-investindo, top 3 ações imediatas.

6. **File Cards** — `channel_matrix.html` + `channel_analysis.json`

### 4 Eixos do Alfredo (Slide 48)

Se o usuário forneceu LTV:CAC e ciclo de venda, adicionar ranking:
- Qual canal gera **maior LTV**?
- Qual tem **menor CAC**?
- Qual tem **mais escalabilidade**?
- Qual tem **menor ciclo de venda**?

---

## MÓDULO 2: BUDGET 70/20/10

**Conceito (Slide 49 da aula):** Todo budget de marketing/vendas deve seguir 70% Escala (ROI imediato) / 20% Aceleração (payback longo, alto potencial) / 10% Descoberta (testes novos).

### Categorias

| Categoria | % Budget | Perfil | Subdivisão interna |
|-----------|----------|--------|-------------------|
| **ESCALA** | 70% | Canais validados, ROI comprovado, previsível | 60% mídia / 30% equipe / 10% ferramentas |
| **ACELERAÇÃO** | 20% | Em validação, payback longo, alto potencial | 90% mídia / 5% equipe / 5% ferramentas |
| **DESCOBERTA** | 10% | Novos, experimentais, testes rápidos | Flexível |

### Conexão com Módulo 1

Se o usuário já rodou a Matriz de Canais:
- ESCALAR → categoria ESCALA
- APOSTAR → categoria ACELERAÇÃO
- MANTER → mantém budget atual (não entra na regra)
- EXPLORAR → categoria DESCOBERTA

Oferecer: "Quer que eu use a classificação dos canais que fizemos? Assim o budget já fica conectado."

### Coleta de dados

| Campo | Obrigatório | Como perguntar |
|-------|-------------|----------------|
| budget_mensal_total | Sim | "Qual o budget mensal total de marketing + vendas?" |
| por canal: nome + valor | Sim | "Quanto vai pra cada canal?" |
| por canal: categoria | Sim | "Esse canal é Escala (ROI provado), Aceleração (validando), ou Descoberta (teste)?" |
| por canal: roi_confirmado | Não | "Tem ROI comprovado?" |
| por canal: ltv_cac | Não | "LTV:CAC se souber" |

### Processamento

```bash
python3 {workflow_dir}/scripts/budget_allocator.py \
  --input-json '<json>' \
  --output-dir '/tmp/budget-{timestamp}'
```

### Apresentação dos resultados

1. **KPIs** (jsonrender) — Budget total, split atual (X/Y/Z%), split ideal (70/20/10), desvio total (pp), alert se escala < 50%

2. **Comparação Visual** (jsonrender) — 2 grupos de Progress bars: Atual e Ideal, lado a lado com cores (verde escala, azul aceleração, amarelo descoberta)

3. **Tabela de Canais** (datatable) — Colunas: Canal, Categoria (badge), Budget Atual, % Atual, Budget Ideal, % Ideal, Delta, ROI Confirmado, LTV:CAC. Subtotais por categoria + total geral.

4. **Subdivisão Interna** (jsonrender) — Para ESCALA: 60/30/10 mídia/equipe/ferramentas. Para ACELERAÇÃO: 90/5/5.

5. **Plano de Realocação** (jsonrender Tabs) — 3 abas: Aumentar (canais que precisam mais), Reduzir (canais com excesso), Manter. Cada item com valor exato e justificativa.

6. **Web App** (web-app-preview) — HTML com barras comparativas + drill-down

7. **Insights** (markdown) — 3-5 bullets: risco principal, oportunidade, quick win, métricas do Alfredo

8. **File Cards** — `budget_report.html` + `budget_analysis.json`

---

## MÓDULO 3: COMP PLAN DESIGNER

**Conceito (Slides 66-72 da aula):** Compensation Plan = colocar o incentivo no lugar certo. Aceleradores por faixa de atingimento + incentivos curto/médio/longo prazo.

### Framework de Aceleradores (Slide 71)

| Faixa | Multiplicador | Significado |
|-------|---------------|-------------|
| 0-70% | 0x | Não comissiona — abaixo do mínimo |
| 71-85% | 0.5x | Meia comissão — aquém da meta |
| 86-99% | 0.7x | Quase lá — incentivo a fechar o gap |
| 100-119% | 1.0x | Na meta — comissão cheia |
| 120%+ | 1.5x | Super performance — acelerador |

### Modificadores por Condição de Venda

Além dos aceleradores por meta, cada deal pode ter **modificadores** que bonificam ou penalizam a comissão baseado na qualidade da venda. São multiplicadores sobre a comissão do deal individual.

| Tipo | Condição | Modificador |
|------|----------|-------------|
| **Modal de Pagamento** | PIX / à vista | +15% |
| | Cartão 1-3x | Neutro |
| | Boleto 7-12x | -10% |
| | Anual upfront | +20% |
| **Carência** | Sem carência | Neutro |
| | 30 dias | -5% |
| | 60+ dias | -10% a -15% |
| **Desconto** | Preço cheio (0%) | +10% |
| | 1-10% | Neutro |
| | 11-20% | -15% |
| | 21%+ | -30% ou sem comissão |

Modificadores são **multiplicativos** entre si. Exemplo: deal à vista (+15%) + sem desconto (+10%) = comissão × 1.15 × 1.10 = +26.5%.

Para times < 10, usar versão simplificada com 4 regras (ver `knowledge/comp-plan-guide.md`).

Ao coletar dados, perguntar: **"Vocês já diferenciam comissão por modal de pagamento, desconto, ou carência? Querem incluir isso?"**
- Se sim: coletar as regras atuais e modelar
- Se não mas tem interesse: sugerir a versão simplificada
- Se não quer: pular — modificadores são opcionais

### Pesquisa de Base Salarial

**Quando usar:** Se o usuário não sabe qual salário base definir, ou quer validar se está competitivo.

**Fluxo:**
1. Perguntar: cargo, cidade, senioridade (Jr/Pl/Sr), tipo de empresa (startup/consolidada)
2. Fazer **web search** por: `"salário [cargo] [cidade] 2026"` em fontes como Glassdoor, Robert Half, Catho
3. Apresentar faixa de mercado em datatable
4. Recomendar um valor considerando ajustes (startup, segmento premium, remoto, etc.)
5. Usar o valor acordado como base para calcular o OTE

**Benchmarks de referência** estão em `knowledge/comp-plan-guide.md` — usar como fallback se web search não retornar dados.

### Tipos de incentivo por prazo (Slide 70)

| Prazo | Exemplos | Para quê |
|-------|----------|----------|
| **Curto** (semanal) | Sprint de reuniões, contest de volume | Tração imediata |
| **Médio** (mensal/tri) | Comissão padrão, metas mensais | Consistência |
| **Longo** (semestral+) | PPR, PLR, equity, promoção | Retenção e cultura |

### Coleta de dados

**Contexto da empresa:**

| Campo | Obrigatório |
|-------|-------------|
| meta_receita_mensal | Sim |
| teto_comissao_pct | Não (default 12%) |

**Por cargo (pelo menos 1, idealmente 2-3):**

| Campo | Obrigatório | Exemplo |
|-------|-------------|---------|
| cargo | Sim | "SDR", "Closer", "Account Manager" |
| headcount | Sim | 5 |
| salario_base | Sim (ou pedir pesquisa salarial) | R$3.000 |
| ote | Sim | R$6.000 |
| meta (valor + unidade) | Sim | 20 reuniões/mês |
| mecanismo | Sim | R$150/reunião OU 10% da receita |
| aceleradores | Não | Default do Alfredo se não customizar |

**Modificadores de deal (opcional):**

| Campo | Obrigatório | Exemplo |
|-------|-------------|---------|
| modifiers.payment | Não | {"pix": 1.15, "cartao_1_3": 1.0, "boleto_7_12": 0.90} |
| modifiers.discount | Não | {"full_price": 1.10, "1_10pct": 1.0, "11_20pct": 0.85, "21_plus": 0.70} |
| modifiers.grace_period | Não | {"none": 1.0, "30_days": 0.95, "60_plus": 0.85} |

**Aceitar input em bloco:**
> "Tenho 5 SDRs ganhando R$3K base, OTE R$6K, meta de 20 reuniões, R$150 por reunião qualificada"

Parsear naturalmente, confirmar, e prosseguir.

### Processamento

```bash
python3 {workflow_dir}/scripts/comp_plan.py \
  --input-json '<json>' \
  --output-dir '/tmp/comp-plan-{timestamp}'
```

### Apresentação dos resultados

1. **Visão Geral** (jsonrender) — Headcount total, folha base, OTE total, variável total a 100%, % comissão vs receita target, alert se > teto

2. **Plano por Cargo** (jsonrender Tabs) — Uma aba por cargo: métricas (base, OTE, variável, meta, mecanismo) + aceleradores como Progress bars visuais

3. **Modificadores de Deal** (datatable) — Se o usuário configurou modificadores: tabela mostrando cada condição, modificador, e impacto em R$ num deal exemplo. Se não configurou: pular.

4. **Simulação de Cenários** (datatable) — Por cargo: atingimento de 50% a 150% com multiplicador, base, variável, total. Highlight na linha de 100%.

5. **Simulação com Modificadores** (datatable) — Se configurou: mostrar 3 cenários de deal (melhor caso, caso neutro, pior caso) com modificadores aplicados. Ex: "Deal R$100K: à vista + preço cheio = R$12.650 vs boleto 12x + 20% desconto = R$6.120"

6. **Custo Total Empresa** (datatable) — Tabela consolidada: cargo, HC, folha base, custo se time a 80%, 100%, 120%. Linha de % da receita target.

7. **Contests & Incentivos** (jsonrender) — Checklist por prazo (curto/médio/longo)

8. **Alertas** (jsonrender) — Warnings se custo > teto, se floor muito agressivo para ramp-up, se spread de modificadores > 2x, tips do Alfredo

9. **Calculadora Interativa** (web-app-preview) — HTML com slider de atingimento + toggles de modificadores → remuneração em tempo real

10. **Documento Final** (filecard) — `comp_plan_doc.md` pronto para compartilhar com o time

11. **File Cards** — `comp_plan_report.html` + `comp_plan_analysis.json`

---

## Regras Gerais

### Qualidade

- **Recomendações específicas** — usar nomes de canais, valores em R$, cargos reais. "Mover R$15K de Eventos para Meta Ads" > "Realoque budget"
- **Quantificar sempre** — todo gap tem valor absoluto e percentual
- **Não inventar dados** — se o usuário não deu LTV:CAC, não estimar. Mostrar "—"
- **Validar antes de rodar** — confirmar dados coletados antes de processar
- **Sugerir ajustes proativamente** — se algo não faz sentido, falar. "Acelerador 0x até 70% pode ser agressivo para um time que acabou de ser contratado."
- **Defaults são sugestões, não imposições** — sempre apresentar o default do framework E perguntar se faz sentido para a realidade do usuário

### Dados e Integrações

- **Perguntar sobre fontes de dados antes de coletar manualmente** — o usuário pode ter CRM, planilha, ou API conectada
- **Usar MCPs ativos quando disponíveis** — se Databricks, Salesforce, Meta Ads, Google Sheets, etc. estão na sessão, oferecer puxar dados de lá
- **Não duplicar trabalho** — se os dados estão num sistema, puxar de lá em vez de pedir pro usuário re-digitar
- **Oferecer templates XLSX** se o usuário quer preencher offline: "Tenho planilhas prontas com exemplos e guia. Quer que eu gere?"
- **Pesquisar benchmarks via web search** quando o usuário não sabe valores de mercado (salários, LTV:CAC por segmento, budget médio)

### Tom

- **Consultor, não tutorial** — fale como quem já fez isso 50 vezes
- **Direto** — "Você está investindo 35% em Meta Ads com LTV:CAC de 4.2x mas só 2% em Indicações com 12.5x. Isso não faz sentido."
- **Questionar quando necessário** — "Esse desconto de 25% é recorrente? Se sim, o problema não é o comp plan, é a política de pricing."
- **Português brasileiro natural**

### Formato

- `datatable` para tabelas de dados com sorting
- `jsonrender` para dashboards e métricas visuais
- `web-app-preview` para HTMLs interativos
- `filecard` para arquivos gerados
- `mermaid` apenas se complementar (não substituir datatable/jsonrender)

### Interação

- **Uma pergunta por vez** (exceto coleta de canais/cargos, que pode ser em bloco)
- **Aceitar respostas rápidas** — "Meta 50K, Google 30K, SEO 15K"
- **Nunca terminar sem próximo passo** — ofereça o próximo módulo ou ação
- **Após demo, sempre oferecer transição** — "Agora com seus dados reais?"
- **Após resultado, oferecer compartilhamento** — "Quer que eu envie por Slack?" (se MCP ativo)
