---
name: "Mentalidade de Growth"
description: "Diagnóstico de maturidade, escada de valor e análise RFV — 3 ferramentas práticas para destravar crescimento. Framework Bruno Nardon (G4 GE 2026)."
icon: "🚀"
---

# Mentalidade de Growth

Workflow interativo com 3 ferramentas práticas para destravar crescimento. Baseado na aula do Bruno Nardon (Mentalidade de Growth, G4 GE Fev 2026).

**Scripts**: `workflows/mentalidade-growth/scripts/`
**Knowledge**: `workflows/mentalidade-growth/knowledge/`
**Datasets demo**: `workflows/mentalidade-growth/datasets/`

Todas as referências a `scripts/`, `knowledge/` e `datasets/` neste arquivo são relativas ao diretório deste workflow. Use caminhos absolutos ao executar comandos.

## Ferramentas Disponíveis

| Ferramenta | Slug | O que faz |
|------------|------|-----------|
| **Escada de Valor** | `escada` | Mapeia produtos/serviços do mais barato ao mais caro, identifica gaps e sugere novos degraus para aumentar LTV |
| **Diagnóstico de Maturidade** | `maturidade` | Avalia maturidade do negócio em 4 áreas (Marketing, Comercial, TI, Operações), identifica gargalo e recomenda foco |
| **Análise RFV** | `rfv` | Segmenta base de clientes com Recência, Frequência e Valor usando as 11 categorias do Nardon |

## Resultado Final (por ferramenta)

**Escada**: Visualização da escada atual + escada proposta + gap analysis + plano de LTV expansion
**Maturidade**: Radar chart + identificação de gargalo + playbook por fase de crescimento
**RFV**: Dashboard inline com 11 segmentos, clusters K-Means, ações recomendadas por segmento (roda a skill `/rfm-analysis` com nomenclatura PT-BR)

---

## ONBOARDING & CONFIGURAÇÃO

Antes de rodar qualquer módulo pela primeira vez, entender a realidade do usuário. Isso NÃO é um questionário longo — são 2-3 perguntas que mudam tudo.

### Passo 1: Descobrir fontes de dados

> Antes de começar: você tem algum desses dados acessíveis?
> - CRM (Salesforce, HubSpot, Pipedrive, etc.)
> - Planilha de produtos/serviços, clientes ou receita (Excel, Google Sheets)
> - Plataforma de pagamento (Stripe, PagSeguro, etc.)
> - ERP ou sistema financeiro
> - Nenhum — vamos construir do zero

**Se tem dados em ferramentas conectadas ao G4 OS (MCPs ativos):**
- Verificar quais sources estão disponíveis na sessão
- Se Databricks/HubSpot/Salesforce/Notion estão ativos → oferecer puxar dados automaticamente
- Se Google Sheets está ativo → oferecer importar direto da planilha
- Exemplo: "Vi que você tem o Databricks conectado. Quer que eu puxe os dados de receita por produto de lá?"

**Se tem dados em planilha/arquivo:**
- Pedir para anexar ou colar
- Auto-mapear colunas com fuzzy match
- Validar antes de prosseguir

**Se não tem dados:**
- Modo entrevista (coletar conversando) ou modo demo (dados fictícios para entender o framework)

### Passo 2: Contextualizar os exemplos

Os datasets demo e frameworks são **pontos de partida, não verdade absoluta**. Sempre:

1. **Apresentar o framework** — "O Nardon ensina que X"
2. **Perguntar se faz sentido** — "Na sua realidade, isso se aplica? O que mudaria?"
3. **Ajustar antes de rodar** — Customizar os parâmetros para a realidade do usuário
4. **Nunca rodar com defaults sem confirmar** — Mesmo no demo, explicar que os números são ilustrativos

### Passo 3: Validar antes de executar

Antes de rodar qualquer análise:
1. **Resumir os dados coletados** — mostrar em tabela ou lista
2. **Confirmar com o usuário** — "Esses dados estão corretos? Algo a ajustar?"
3. **Sinalizar inconsistências** — "Você disse que tem 500 funcionários mas só 2 produtos. Isso é intencional?"
4. **Só processar depois do OK**

### Integração com MCPs e APIs

Se MCPs relevantes estão ativos na sessão, usar proativamente:

| Source | Como usar | Módulo |
|--------|-----------|--------|
| **Databricks** | Puxar dados de receita por produto, base de clientes | Escada, RFV |
| **Salesforce / HubSpot** | Pipeline, produtos, ticket médio, dados de clientes | Todos |
| **Google Sheets** | Importar/exportar planilhas | Todos |
| **Notion** | Buscar docs de planejamento, catálogo de produtos | Escada, Maturidade |
| **Slack** | Enviar resultado para canal ou pessoa | Todos |

**Regra**: Se o MCP está ativo e o dado existe lá, oferecer puxar automaticamente em vez de pedir pro usuário digitar.

---

## ROTEAMENTO — Como decidir o que rodar

### Regra #1: Se o usuário pedir algo específico, vá direto

| Usuário diz | Ferramenta |
|-------------|-----------|
| "escada de valor", "value ladder", "aumentar LTV", "precificação", "portfólio de produtos" | **Escada** |
| "maturidade", "diagnóstico", "gargalo", "onde investir", "qual área focar", "fase do negócio" | **Maturidade** |
| "rfv", "rfm", "segmentar clientes", "base de clientes", "recência", "churn" | **RFV** |
| "growth", "crescimento", "por onde começar", sem especificar | **Diagnóstico** (abaixo) |

### Regra #2: Se não ficou claro, faça UM diagnóstico rápido

> Tenho 3 ferramentas práticas baseadas na aula do Bruno Nardon. Me conta: qual desses desafios é mais urgente pra você?
>
> 1. **Meu portfólio de produtos tem gaps** — vou mapear sua escada de valor e identificar onde criar novos degraus pra aumentar LTV
> 2. **Não sei qual área priorizar** — vou diagnosticar a maturidade do negócio em 4 áreas e achar o gargalo
> 3. **Preciso entender minha base de clientes** — vou segmentar com RFV e mostrar quem proteger, crescer e reativar
>
> Ou se quiser, rodo o diagnóstico de maturidade primeiro (ele indica os outros).

### Regra #3: Nunca carregue contexto que não vai usar

- Se o usuário quer só Escada de Valor, NÃO explique o diagnóstico de maturidade
- Execute apenas o módulo relevante
- Ao final de cada módulo, ofereça o próximo lógico (ver Conexões)

### Conexões entre ferramentas

```
Maturidade → Escada (maturidade mostra onde focar, escada aprofunda no portfólio)
Maturidade → RFV (se gargalo é comercial/marketing, RFV ajuda a entender a base)
Escada → RFV (escada identifica gaps, RFV mostra quais clientes upsell)
RFV → Escada (segmentos mostram oportunidade de LTV, escada estrutura a oferta)
```

Ao terminar um módulo:
> Quer rodar a próxima ferramenta? O output daqui alimenta [próximo módulo] diretamente.

---

## DADOS — 3 Modos de Input

Cada ferramenta aceita 3 modos. Detecte automaticamente:

### Modo 1: Demo (sem dados)

Usar quando: usuário não tem dados, quer entender o framework, ou pediu "exemplo".

> Quer ver como funciona com um exemplo prático? Tenho demos para 3 tipos de negócio:
> - **B2B SaaS** — 4 degraus de produto, 5.000 clientes, time de 30
> - **E-commerce** — 6 categorias, 20.000 clientes, 3 canais de venda
> - **Serviços/Educação** — 5 degraus (curso online → mentoria → consultoria), 8.000 alunos
>
> Qual se parece mais com seu negócio?

Carregar o dataset correspondente de `datasets/` e rodar direto.

**IMPORTANTE sobre demos:**
- Demo é ferramenta de aprendizado, não deliverable final
- Durante o demo, ir explicando o racional: "Esse produto está nessa posição porque..."
- **Ao final do demo, SEMPRE transicionar para dados reais:**

> Essa foi uma análise com dados fictícios para você entender o framework. Agora que você viu como funciona, quer rodar com seus dados reais?

### Modo 2: Entrevista (tem conhecimento, não tem planilha)

Usar quando: usuário sabe do negócio mas não trouxe arquivo.

Coletar dados via conversa guiada:
- Aceitar respostas aproximadas ("temos uns 5 produtos, o mais barato R$500 e o mais caro R$50K")
- NÃO forçar precisão — melhor rodar com dados aproximados do que não rodar
- Validar antes de processar
- **Sugerir ajustes se algo não faz sentido**
- **Checar se tem MCP ativo que pode preencher gaps**

### Modo 3: Import (tem dados prontos)

Usar quando: usuário menciona "tenho uma planilha", "CSV", "arquivo", ou anexa algo.

Aceitar: CSV/XLSX, JSON, texto colado, Google Sheets (se MCP ativo).
Se o mapeamento automático falhar, mostrar as colunas encontradas e perguntar qual é qual.

---

## MÓDULO 1: ESCADA DE VALOR

**Conceito (Slides 43-45 da aula):** Mapear produtos/serviços do mais barato ao mais caro para identificar gaps e oportunidades de LTV. Se tem um pulo de R$500 pra R$50.000 na escada, tem degrau faltando.

### As 4 Alavancas de LTV (Nardon)

| Alavanca | Descrição | Exemplo |
|----------|-----------|---------|
| **Vender mais do mesmo** | Aumentar frequência de compra | Assinatura mensal, recompra automática |
| **Vender algo diferente** | Cross-sell complementar | Curso + mentoria, software + consultoria |
| **Encontrar casos de uso correlatos** | Expandir a job-to-be-done | Dentista: limpeza → estética → harmonização |
| **Lembrar que você existe** | Reativação e remarketing | Email nurturing, conteúdo, comunidade |

### Exemplo de Referência: Dentista (Slide 43)

```
Limpeza (R$200) → Clareamento (R$800) → Aparelho (R$3.000) → Estética (R$8.000)
```

### Exemplo de Referência: G4 (Slides 44-45)

```
Conteúdo grátis → Online (R$3K) → Presencial (R$12K) → Comunidade (R$25K) → Mentoring (R$50K) → Consultoria (R$400-600K)
```

### Coleta de dados

Para cada produto/serviço, coletar:

| Campo | Obrigatório | Como perguntar |
|-------|-------------|----------------|
| nome | Sim | "Liste seus produtos/serviços, do mais barato ao mais caro" |
| preco | Sim | "Qual o preço médio?" |
| tipo | Não | "É entrada, core, premium ou super-premium?" |
| margem_pct | Não | "Se souber, qual a margem?" |
| clientes_ativos | Não | "Quantos clientes têm nesse produto?" |
| taxa_conversao | Não | "Que % dos clientes do degrau anterior sobe pra esse?" |
| recorrente | Não | "É compra única ou recorrente?" |

**Aceitar input em bloco:**
> "Tenho 3 produtos: curso online R$997, imersão R$5.000, mentoria R$25.000"

Parsear naturalmente, confirmar, e prosseguir.

### Processamento

```bash
python3 {workflow_dir}/scripts/value_ladder.py \
  --input-json '<json>' \
  --output-dir '/tmp/value-ladder-{timestamp}'
```

### Apresentação dos resultados

**Ordem exata — seguir sem pular:**

1. **KPI Dashboard** (jsonrender) — Total de degraus, receita total estimada, ticket médio, maior gap de preço, LTV estimado (se dados disponíveis)

2. **Escada Visual** (web-app-preview) — HTML interativo com escada de valor. Cada degrau como bloco com nome, preço, clientes. Linhas conectando degraus com taxa de conversão entre eles. Cores: verde (entrada) → azul (core) → roxo (premium) → dourado (super-premium).

3. **Tabela de Produtos** (datatable) — Colunas: Produto, Preço (currency), Tipo (badge), Margem (percent), Clientes Ativos (number), Conversão do Anterior (percent), Receita Estimada (currency). Ordenar por preço crescente.

4. **Gap Analysis** (jsonrender) — Card com Progress bars mostrando gaps entre degraus. Gaps > 3x o degrau anterior ficam em vermelho com alert. Cada gap tem sugestão de produto intermediário.

5. **Alavancas de LTV** (jsonrender Tabs) — 4 abas, uma por alavanca (Mais do Mesmo, Algo Diferente, Casos Correlatos, Lembrar que Existe). Cada aba com Checklist de ações específicas usando os nomes dos produtos do usuário.

6. **Escada Proposta** (web-app-preview) — Mesma visualização do item 2, mas com degraus sugeridos incluídos (em tracejado/pontilhado). Comparação visual antes/depois.

7. **Plano de Ação** (markdown) — 3-5 bullets: próximo degrau a criar, estimativa de impacto em LTV, quick wins vs investimentos maiores.

8. **File Cards** — `value_ladder.html` + `value_ladder_analysis.json`

### Métricas de Saúde da Escada

Calcular e apresentar:
- **Cobertura de faixas**: % de faixas de preço cobertas (sem gaps > 3x)
- **Concentração de receita**: % da receita no degrau principal (se > 70%, risco alto)
- **Taxa de ascensão**: % médio de clientes que sobem na escada
- **LTV teórico**: se todos os clientes subissem todos os degraus

---

## MÓDULO 2: DIAGNÓSTICO DE MATURIDADE

**Conceito (Slides 11-23 da aula):** Avaliar maturidade do negócio em 4 áreas usando a progressão Pessoas → Processos → Tecnologia → Escala. O gargalo é a área mais atrasada — e é ela que limita o crescimento.

### As 4 Áreas

| Área | O que avalia | Exemplos de maturidade |
|------|-------------|----------------------|
| **Marketing** | Geração de demanda, marca, canais | Depende de indicação (1) → multi-canal previsível (10) |
| **Comercial** | Vendas, pipeline, conversão | Fundador vende sozinho (1) → time com processo e previsibilidade (10) |
| **TI/Tecnologia** | Sistemas, automação, dados | Planilha Excel (1) → stack integrado com dados em real-time (10) |
| **Operações** | Entrega, suporte, processos internos | Improviso (1) → processos documentados e escaláveis (10) |

### Escala de Maturidade (Nardon)

Para cada área, avaliar em qual estágio está:

| Estágio | Score | Descrição |
|---------|-------|-----------|
| **Pessoas** | 1-3 | Depende de indivíduos. Sem processo. "Se fulano sair, para tudo." |
| **Processos** | 4-6 | Tem processo documentado. Funciona mesmo se trocar pessoa. |
| **Tecnologia** | 7-8 | Processo automatizado por ferramentas. Escala sem esforço linear. |
| **Escala** | 9-10 | Máquina rodando. Previsível, mensurável, auto-ajustável. |

### 5 Fases de Crescimento (Slides 25-26)

| Fase | Porte | Colaboradores | Papel do Fundador | Objetivo Principal |
|------|-------|---------------|-------------------|-------------------|
| **Fundação (Bebê)** | Micro | Até 10 | Generalista | Vender |
| **Expansão Inicial (Criança)** | Pequena | 10-50 | Vendedor + Gestor | Vender de forma organizada |
| **Fortalecimento (Adolescente)** | Média | 50-200 | Líder de líderes | Automatizar e criar novos produtos |
| **Expansão Estratégica (Adulto)** | Grande | 200-500 | Estrategista | Não deixar burocracia frear crescimento |
| **Maturação (Melhor idade)** | Enterprise | 500+ | Conselheiro/Visionário | Manter liderança de mercado |

### Coleta de dados

**Entrevista guiada — perguntar por área, uma de cada vez:**

Para cada área (Marketing, Comercial, TI, Operações):

| Pergunta | Para entender |
|----------|--------------|
| "De 1 a 10, como você avalia a maturidade de [área]?" | Score geral |
| "Se a pessoa-chave dessa área sair, o que acontece?" | Dependência de pessoas (1-3) |
| "Os processos estão documentados e funcionam sem supervisão?" | Processos (4-6) |
| "Quais ferramentas/sistemas essa área usa?" | Tecnologia (7-8) |
| "Vocês conseguem prever resultados com X% de confiança?" | Escala (9-10) |

**Contexto adicional:**

| Campo | Obrigatório |
|-------|-------------|
| num_colaboradores | Sim (para mapear fase) |
| receita_mensal | Não (para calibrar expectativa) |
| principal_desafio | Sim ("o que mais te incomoda?") |
| setor | Não (para benchmarks) |

### Processamento

```bash
python3 {workflow_dir}/scripts/maturity_diagnostic.py \
  --input-json '<json>' \
  --output-dir '/tmp/maturity-{timestamp}'
```

### Apresentação dos resultados

1. **Fase Identificada** (jsonrender) — Card com a fase atual (das 5), papel do fundador, objetivo principal. Alert se scores indicam fase diferente da esperada pelo porte.

2. **Radar de Maturidade** (web-app-preview) — HTML com radar chart (4 eixos: Marketing, Comercial, TI, Operações). Área preenchida mostrando o perfil. Linha de referência da fase esperada.

3. **Scores por Área** (jsonrender) — Grid com 4 cards, cada um com: nome da área, score, estágio (Pessoas/Processos/Tecnologia/Escala como badge), Progress bar colorida. A área com menor score fica com borda vermelha = **gargalo identificado**.

4. **Gargalo Analysis** (jsonrender) — Card destacado: "Seu gargalo é [ÁREA] (score X/10)". Explicação de por que isso limita crescimento. Referência ao framework do Nardon: "Se não existisse gargalo, não teria restrição."

5. **Diagnóstico Detalhado por Área** (jsonrender Tabs) — 4 abas, uma por área. Cada aba: estágio atual, o que está funcionando, o que está faltando, próximo nível a alcançar, ações recomendadas.

6. **Playbook por Fase** (markdown) — Baseado na fase identificada:
   - Onde alocar tempo de liderança
   - Quais ferramentas/estruturas priorizar
   - O que **parar de fazer** ("o que te trouxe até aqui não te levará até lá")
   - Checklist de transição para próxima fase

7. **Lembretes do Nardon** (jsonrender Alert) — 4 alertas com os princípios:
   - "Não existe bala de prata"
   - "Mantenha tudo o mais simples possível"
   - "Disciplina é o nome do jogo"
   - "O que te trouxe até aqui, não te levará até lá"

8. **File Cards** — `maturity_diagnostic.html` + `maturity_analysis.json`

### Conexão com Próximos Passos

Após o diagnóstico, sugerir baseado no gargalo:
- Se gargalo = **Marketing/Comercial** → "Quer rodar a Análise RFV pra entender melhor sua base de clientes?"
- Se gargalo = **Comercial/Operações** → "Quer mapear sua Escada de Valor pra estruturar o portfólio?"
- Se gargalo = **TI** → "Quer ver quais automações priorizar?" (link com workflow `/onde-usar-ia` se disponível)

---

## MÓDULO 3: ANÁLISE RFV

**Conceito (Slides 36-41 da aula):** Segmentar base de clientes usando Recência, Frequência e Valor Monetário. O Nardon usa 11 categorias com nomes em português.

### Este módulo delega para a skill `/rfm-analysis`

A skill `/rfm-analysis` já tem todo o pipeline (Python, clustering, visualização). Este módulo adiciona:

1. **Nomenclatura PT-BR do Nardon** — nomes dos 11 segmentos em português
2. **Contexto da aula** — explicações e ações baseadas no framework do Nardon
3. **Conexão com os outros módulos** — segmentos alimentam a Escada de Valor

### As 11 Categorias RFV (Nardon)

| Código | Segmento | R | FM | Ação Principal |
|--------|----------|---|-----|---------------|
| A | **Campeões** | 4-5 | 4-5 | Recompensar, pedir indicações, upsell premium |
| B | **Clientes Fiéis** | 3-5 | 3-5 | Programa de fidelidade, upsell de valor |
| C | **Fiéis em Potencial** | 3-5 | 2-4 | Oferecer programa de fidelidade, recomendar produtos |
| D | **Novos Clientes** | 5 | 1 | Onboarding, construir relacionamento |
| E | **Promessas** | 3-4 | 1-2 | Awareness, trial, incentivo de segunda compra |
| F | **Precisando de Atenção** | 3 | 1 | Ofertas personalizadas, promoções limitadas |
| G | **Quase Dormentes** | 1-2 | 1-3 | Re-engajar com conteúdo, ofertas de urgência |
| H | **Não Pode Perder** | 1-2 | 4-5 | Win-back urgente, outreach pessoal, entender o que mudou |
| I | **Em Risco** | 1-2 | 2-4 | Campanha de reativação personalizada |
| J | **Hibernando** | 1 | 2 | Descontos agressivos, testar novos canais |
| K | **Perdidos** | 1 | 1 | Ignorar ou reativação de baixo custo |

### Fluxo de Execução

1. **Perguntar se tem dados de transações** — CSV/XLSX com ID do cliente, data, valor
2. **Se não tem**: oferecer demo com dataset de exemplo da skill
3. **Se tem**: rodar a skill `/rfm-analysis` normalmente
4. **Ao apresentar resultados**: usar os nomes PT-BR e as ações da tabela acima
5. **Conectar com Escada de Valor**: "Seus Campeões compram X. Tem produto premium pra oferecer pra eles?"

### Apresentação (delegada à skill)

Seguir exatamente o fluxo da skill `/rfm-analysis` (8 passos: KPIs → datatable → health → clusters → revenue → actions → insights → files), mas:
- Traduzir nomes de segmentos para PT-BR
- Usar as ações da tabela acima nas recomendações
- Adicionar conexão com Escada de Valor no final

### Contexto da Segmentação (Nardon, Slides 31-35)

Antes de rodar o RFV, lembrar o framework de segmentação:
1. Segmentar a base em subgrupos
2. Entender dores/dúvidas/desejos de cada subgrupo
3. Avaliar para qual subgrupo seu negócio é **essencial** (não apenas útil)
4. Entender o que é **indispensável** para esse subgrupo

O RFV é uma ferramenta quantitativa para o passo 1. Os outros passos são qualitativos e devem ser feitos em conversa.

---

## Regras Gerais

### Qualidade

- **Recomendações específicas** — usar nomes de produtos, valores em R$, áreas reais. "Criar produto intermediário entre Curso Online (R$997) e Imersão (R$5.000)" > "Crie mais degraus"
- **Quantificar sempre** — todo gap tem valor absoluto e percentual
- **Não inventar dados** — se o usuário não deu margem, não estimar. Mostrar "—"
- **Validar antes de rodar** — confirmar dados coletados antes de processar
- **Sugerir ajustes proativamente** — se algo não faz sentido, falar. "Você tem gap de R$500 pra R$50.000 — isso é intencional ou falta produto no meio?"
- **Defaults são sugestões, não imposições** — sempre apresentar o framework do Nardon E perguntar se faz sentido para a realidade do usuário
- **Citar a fonte** — quando usar conceito específico, referenciar o slide/conceito do Nardon

### Dados e Integrações

- **Perguntar sobre fontes de dados antes de coletar manualmente** — o usuário pode ter CRM, planilha, ou API conectada
- **Usar MCPs ativos quando disponíveis** — se Databricks, Salesforce, Google Sheets, etc. estão na sessão, oferecer puxar dados de lá
- **Não duplicar trabalho** — se os dados estão num sistema, puxar de lá
- **Pesquisar benchmarks via web search** quando o usuário não sabe valores de mercado

### Tom

- **Consultor, não tutorial** — fale como quem já fez isso 50 vezes
- **Direto** — "Você tem gap de 10x entre o segundo e terceiro degrau. Isso não é escada, é precipício."
- **Questionar quando necessário** — "Seu score de TI é 2 mas você diz que tem automação. Me conta mais — o que exatamente está automatizado?"
- **Português brasileiro natural**

### Formato

- `datatable` para tabelas de dados com sorting
- `jsonrender` para dashboards e métricas visuais
- `web-app-preview` para HTMLs interativos (escada visual, radar chart)
- `filecard` para arquivos gerados
- `mermaid` apenas se complementar (não substituir datatable/jsonrender)

### Interação

- **Uma pergunta por vez** (exceto coleta de produtos/áreas, que pode ser em bloco)
- **Aceitar respostas rápidas** — "curso R$1K, imersão R$5K, mentoria R$25K"
- **Nunca terminar sem próximo passo** — ofereça o próximo módulo ou ação
- **Após demo, sempre oferecer transição** — "Agora com seus dados reais?"
- **Após resultado, oferecer compartilhamento** — "Quer que eu envie por Slack?" (se MCP ativo)
