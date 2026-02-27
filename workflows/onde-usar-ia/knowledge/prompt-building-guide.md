# Guia: Como Construir Bons Prompts para IA

Baseado na analise de 220 prompts profissionais reais do dataset GDPVal (OpenAI) + padroes do Anthropic Economic Index.

## O Framework RCDEF

89% dos melhores prompts profissionais seguem este padrao:

| Componente | O que e | % dos bons prompts que usam |
|-----------|---------|---------------------------|
| **R**ole (Papel) | "Voce e um [cargo] que trabalha em [contexto]" | 89% |
| **C**ontext (Contexto) | Situacao especifica, background, dados disponiveis | 82% |
| **D**eliverable (Entregavel) | O que exatamente precisa ser produzido | 82% |
| **E**xpectations (Expectativas) | Restricoes, criterios de qualidade, o que evitar | 81% |
| **F**ormat (Formato) | Como estruturar a saida (tabela, bullet points, PDF, etc.) | 71% |

## Exemplos por Area

### Vendas / Comercial

**Prompt ruim:**
> Escreve um email de follow-up pro cliente

**Prompt bom (RCDEF):**
> **[R]** Voce e um executivo de vendas B2B de uma empresa de tecnologia SaaS.
> **[C]** Tive uma reuniao com o Joao Silva, CFO da empresa XYZ (300 funcionarios), ha 3 dias. Ele demonstrou interesse na solucao mas disse que precisa validar internamente. Nosso produto custa R$15K/mes.
> **[D]** Escreva um email de follow-up que reative o contato sem ser invasivo.
> **[E]** Tom: profissional mas pessoal. Maximo 150 palavras. Inclua uma pergunta aberta. Nao mencione preco. Referencia algo especifico da reuniao.
> **[F]** Formato: Assunto + corpo do email. Marque entre colchetes [X] os pontos que eu devo personalizar.

### Gestao de Projetos

**Prompt ruim:**
> Faz um status report do projeto

**Prompt bom (RCDEF):**
> **[R]** Voce e um PMO responsavel por reportar status de projetos para a diretoria.
> **[C]** Projeto: Migracao Salesforce. Status atual: fase 3 de 5 (integracao com ERP). Blocker: time de Finance nao priorizou input dos campos contabeis. Timeline original: go-live em abril. Risco de atraso: 2-3 semanas.
> **[D]** Crie um status report executivo de 1 pagina.
> **[E]** Inclua: semaforo geral (verde/amarelo/vermelho), progresso vs plano, top 3 riscos com owner e acao, proximos milestones. Seja direto — diretores leem em 2 minutos.
> **[F]** Formato: tabela resumo no topo + bullets por secao. Sem jargao tecnico.

### Financeiro

**Prompt ruim:**
> Analisa esse P&L

**Prompt bom (RCDEF):**
> **[R]** Voce e um analista financeiro de uma empresa de educacao com receita de ~R$500M/ano.
> **[C]** Segue o P&L do Q4 2025 [cole dados]. O board meeting e quinta-feira e o CFO precisa de uma analise clara.
> **[D]** Faca uma analise do P&L identificando: (1) variacoes vs Q3, (2) anomalias ou outliers, (3) 3 riscos e 3 oportunidades.
> **[E]** Foque em variacoes >5% ou >R$500K. Compare com o budget quando possivel. Nao faca suposicoes — se falta dado, sinalize.
> **[F]** Formato: tabela de variacoes (valor, %, vs budget) + commentary em bullets. Maximo 1 pagina executiva + 1 pagina de detalhe.

### Marketing / Conteudo

**Prompt ruim:**
> Cria um post pro Instagram

**Prompt bom (RCDEF):**
> **[R]** Voce e o social media manager de uma escola de negocios premium (publico: empreendedores e C-levels, 25-50 anos).
> **[C]** Temos um evento ao vivo sobre "Como usar IA na gestao" acontecendo dia 15/03. Ingressos a partir de R$2.500. Ja vendemos 60% — faltam 40 vagas.
> **[D]** Crie 3 variacoes de post para Instagram (carrossel de 5 slides cada).
> **[E]** Tom: autoridade + urgencia sutil. Nao use "imperdivel", "exclusivo", ou emojis de foguete. Angulos: (1) dados/estatisticas, (2) dor do lider, (3) prova social.
> **[F]** Formato para cada variacao: Hook (slide 1) | Desenvolvimento (slides 2-4) | CTA (slide 5). Texto maximo 30 palavras por slide.

### Customer Success / Suporte

**Prompt ruim:**
> Me ajuda a responder esse cliente bravo

**Prompt bom (RCDEF):**
> **[R]** Voce e um CS Manager de uma empresa de software B2B. O cliente e uma conta enterprise (R$50K/mes).
> **[C]** O cliente reportou que a integracao com o ERP dele falhou 3x na ultima semana. Ele mandou este email [cole email]. Nosso time de engenharia ja identificou o bug e vai corrigir em 48h.
> **[D]** Redija uma resposta que reconheca o problema, comunique a solucao e mantenha a confianca.
> **[E]** Tom: empatico mas tecnico. Nao minimize o problema. Inclua: (1) reconhecimento, (2) causa raiz simplificada, (3) plano de acao com datas, (4) compensacao sugerida. Maximo 200 palavras.
> **[F]** Formato: email profissional com assunto. Use bullet points para o plano de acao.

### RH / People

**Prompt ruim:**
> Faz uma descricao de vaga

**Prompt bom (RCDEF):**
> **[R]** Voce e head de People de uma empresa de tecnologia com ~200 funcionarios, cultura high-performance.
> **[C]** Preciso contratar um Product Manager Senior para a squad de Growth. O time atual tem 1 PM Jr, 4 devs, 1 designer. A squad e responsavel por aumentar conversao de trial→pago (hoje 8%, meta 15%).
> **[D]** Crie uma job description completa para LinkedIn.
> **[E]** Nao use: "proativo", "dinamico", "hands-on". Foque em resultados esperados, nao em lista generica de requisitos. Inclua faixa salarial indicativa (R$18-25K). Diferencie "essencial" de "diferencial".
> **[F]** Formato: Sobre a empresa (2 linhas) | O desafio (3 linhas) | O que esperamos (bullets) | Requisitos essenciais | Diferenciais | O que oferecemos | Como aplicar.

## Principios de um Bom Prompt

### 1. Especificidade > Generalidade
- Ruim: "me ajuda com vendas"
- Bom: "me ajuda a redigir uma proposta comercial para empresa de logistica, ticket R$50K/ano, 3 concorrentes no processo"

### 2. Restricoes sao libertadoras
- Sem restricao: IA gera texto generico
- Com restricao ("maximo 200 palavras, sem jargao, em formato de email"): IA gera algo usavel

### 3. Exemplos valem mais que instrucoes
- Ao inves de "escreva de forma profissional", de um exemplo de tom desejado
- Ao inves de "formate bem", mostre o formato que quer

### 4. Iteracao > Prompt perfeito
- Primeiro prompt gera ~70% do que precisa
- Refinar com "ajuste X", "mude o tom de Y", "adicione Z"
- 3 iteracoes tipicamente chegam a 95%+

### 5. Dados de entrada fazem diferenca
- Quanto mais contexto especifico, melhor o output
- Cole dados reais (tabelas, emails, notas) — IA trabalha melhor com material concreto
- Diga o que NAO quer (tao importante quanto o que quer)

## Anatomia de Prompt por Tipo de Tarefa

### Tarefas de CRIACAO (escrever, criar, gerar)
```
Papel → Audiencia → Objetivo → Restricoes → Formato → Exemplos
```

### Tarefas de ANALISE (analisar, avaliar, diagnosticar)
```
Papel → Dados (cole aqui) → Perguntas especificas → Framework de analise → Formato do output
```

### Tarefas de PROCESSO (organizar, planejar, estruturar)
```
Papel → Contexto atual → Estado desejado → Restricoes → Cronograma → Formato
```

### Tarefas de REVISAO (revisar, corrigir, melhorar)
```
Papel → Material original (cole aqui) → Criterios de qualidade → Tipo de feedback → Formato
```

## Adaptacao por Ferramenta

| Ferramenta | Dica especifica |
|-----------|----------------|
| **ChatGPT** | Use "Custom Instructions" para definir R(ole) uma vez. Prompt fica menor no dia a dia |
| **Claude** | Use Projects para upload de documentos de referencia. Artifacts para outputs longos |
| **Gemini** | Funciona bem com Google Workspace. Use "@ mencao" para incluir docs do Drive |
| **Copilot (Microsoft)** | Referencia documentos do SharePoint/Teams direto no prompt |
| **N8N/Zapier** | Prompts mais curtos e estruturados (JSON-like). Menos narrativa, mais instrucao direta |

## Exemplos Trabalhados (contextualizados ao discovery)

A diferenca entre um prompt generico e um prompt que gera valor e o CONTEXTO do aluno. Sempre adaptar usando as informacoes coletadas na Fase 2 (discovery).

### Exemplo: Suporte N0/N1 (contexto real)

**Discovery coletou**: Zendesk, 80 chamados/dia, 3 atendentes, SaaS B2B, SLA 4h

**Prompt generico (ruim)**:
> Classifica esse chamado e sugere uma resposta.

**Prompt contextualizado (bom)**:
> **[R]** Voce e um especialista em suporte N0 de uma empresa SaaS B2B.
> **[C]** Temos 80 chamados/dia no Zendesk, SLA de 4h para primeira resposta, 3 atendentes. Os tipos mais comuns sao: duvida de uso (40%), bug report (25%), solicitacao de feature (15%), reclamacao (10%), outros (10%).
> **[D]** Para o chamado abaixo, faca: (1) classifique por tipo e urgencia (P1-P4), (2) identifique se existe resposta na FAQ, (3) gere um rascunho de resposta.
> **[E]** Tom: empatico mas objetivo. Se for bug, peca logs/screenshot. Se for feature request, agradeca e explique o processo. Maximo 150 palavras na resposta. Se P1/P2, sinalize para escalar.
> **[F]** Formato: Classificacao (tipo + urgencia) | FAQ match (sim/nao + link) | Resposta rascunho
>
> Chamado: [colar chamado]

**No G4 OS**: Depois de classificar, "manda essa resposta no Zendesk" (quando integrado) ou "manda por email pro cliente".

### Exemplo: Vendas B2B (contexto real)

**Discovery coletou**: HubSpot, 15 deals/mes, ticket R$30K, ciclo 45 dias, 4 AEs

**Prompt generico (ruim)**:
> Me ajuda a fazer uma proposta comercial.

**Prompt contextualizado (bom)**:
> **[R]** Voce e um executivo de vendas de uma empresa de tecnologia SaaS B2B (ticket medio R$30K/ano, ciclo 45 dias).
> **[C]** Empresa: [nome], Setor: [setor], Porte: [porte], Contato: [nome, cargo]. Na reuniao de discovery, os principais pain points foram: [lista]. Eles usam [sistema atual] e querem migrar porque [motivo]. Concorrentes no processo: [lista]. Budget aprovado: [sim/nao/em aprovacao].
> **[D]** Gere uma proposta comercial personalizada com 3 secoes: (1) Diagnostico (mostrando que entendi o problema), (2) Solucao proposta (como nosso produto resolve cada pain point), (3) Investimento e ROI projetado.
> **[E]** Tom: consultivo, nao vendedor. Conecte cada feature a um pain point especifico. Inclua 2-3 metricas de ROI realistas. Nao exagere — CFOs detectam bullshit.
> **[F]** Formato: PDF-ready com headers, bullets, e uma tabela de ROI no final.

**No G4 OS**: "Agora salva isso num Google Doc formatado e manda por email pro [contato]" → executa via MCP.

### Exemplo: Marketing de Conteudo (contexto real)

**Discovery coletou**: Instagram + LinkedIn, 5 posts/semana, escola de negocios, publico C-level 30-50 anos

**Prompt generico (ruim)**:
> Cria posts pro Instagram.

**Prompt contextualizado (bom)**:
> **[R]** Voce e o head de conteudo de uma escola de negocios premium (publico: CEOs e diretores, 30-50 anos, Brasil).
> **[C]** Calendario da semana: segunda = insight de gestao, terca = case de aluno, quarta = dado/pesquisa, quinta = bastidor/cultura, sexta = CTA para evento/programa. Proximo evento: [nome] dia [data], R$[valor], [X]% vendido. Tom da marca: autoridade sem arrogancia, pratico, direto.
> **[D]** Gere o pacote completo de 5 posts da semana, cada um com: (1) hook, (2) desenvolvimento, (3) CTA.
> **[E]** Maximo 2.200 caracteres por post (limite IG). Sem emojis excessivos (maximo 2 por post). Sem "imperdivel", "exclusivo", "nao perca". Cada post deve funcionar sozinho (nao depender dos outros). Inclua sugestao de visual.
> **[F]** Formato: tabela com colunas [Dia | Tema | Hook | Texto | CTA | Visual sugerido]

**No G4 OS**: "Salva num Google Doc e manda pro canal #marketing no Slack pra revisao" → executa via MCP.

## Regra de Ouro para Prompts no Diagnostico

Quando gerar prompts para o aluno no diagnostico, SEMPRE:

1. **Usar as ferramentas que ele mencionou** — se disse "Zendesk", o prompt menciona Zendesk
2. **Usar os volumes reais** — se disse "80/dia", o prompt assume 80/dia
3. **Usar o tom do setor** — SaaS B2B ≠ varejo ≠ educacao
4. **Mostrar o diferencial G4 OS** — "depois de gerar, manda no Slack/email/Doc"
5. **Ensinar por que funciona** — explicar cada componente RCDEF em 1 linha

## Fonte
Padroes extraidos de 220 prompts profissionais do dataset GDPVal (OpenAI, 2025) — benchmark de tarefas economicas reais em 44 ocupacoes.
