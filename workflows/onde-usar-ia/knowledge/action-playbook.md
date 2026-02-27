# Playbook de Acoes por Quadrante

> **Regra #1**: G4 OS e a ferramenta primaria. Toda recomendacao comeca com "faca isso aqui, comigo".
> **Regra #2**: Toda recomendacao tem economia quantificada. Sem numero = sem valor.
> **Regra #3**: A acao #1 e demonstrada ao vivo. Nao apenas recomendada — executada.

## Hierarquia de Recomendacao

1. **G4 OS direto** → "Faca agora, aqui comigo"
2. **G4 OS + skill nova** → "Posso criar uma ferramenta permanente pra isso"
3. **G4 OS como orquestrador** → "Eu preparo, voce executa em [ferramenta]"
4. **Ferramenta externa** → "Para isso, use [X]. Aqui esta como"

---

## 🔴 AUTOMATIZAR (IA boa + Time nao gosta)

**Principio**: Tirar do prato. Quanto menos o humano tocar, melhor.
**Padrao de solucao depende do "por que":**

| Motivo da insatisfacao | Tipo de solucao | Exemplo |
|----------------------|-----------------|---------|
| Repetitivo demais | Automacao full (IA faz sozinha) | Classificar chamados, gerar reports |
| Ferramenta ruim | Substituir interface (IA como nova interface) | G4 OS como front-end do Zendesk/CRM |
| Demora muito | Aceleracao (IA faz 80%, humano revisa 20%) | Rascunho de propostas, pesquisa de mercado |

### G4 OS faz direto

| Padrao | Ferramenta G4 OS | Exemplo concreto |
|--------|-----------------|------------------|
| Tarefa recorrente | Scheduled actions | "Toda segunda 8h, gera relatorio de vendas e manda no Slack" |
| Processar N itens iguais | `llm_map` | "Classifica esses 200 leads por potencial e prioridade" |
| Monitorar e alertar | Vigia watchers | "Me avisa se ninguem responder o cliente enterprise em 4h" |
| Gerar documentos | Conversa + MCP | "Gera a ata dessa reuniao e salva no Google Doc" |
| Triagem/classificacao | Conversa + Python | "Classifica esses tickets por urgencia e tema" |

### G4 OS + skill nova

Se o padrao se repete semanalmente, vale criar uma skill permanente:

| Skill | O que faz | Quando criar |
|-------|----------|-------------|
| Triagem | Classifica itens com criterios fixos | > 20 itens/dia do mesmo tipo |
| Relatorio | Consolida fontes e gera report | Relatorio semanal/mensal recorrente |
| Resposta padrao | Gera resposta contextualizada para cenarios comuns | > 30% dos atendimentos sao FAQ |

### Ferramentas externas (quando G4 OS nao basta)

| Necessidade | Ferramenta | Quando usar |
|-------------|-----------|-------------|
| Automacao 24/7 com triggers | N8N, Zapier, Make | Precisa reagir em tempo real sem humano |
| Chatbot voltado ao cliente | Intercom, Zendesk AI | Atendimento self-service do cliente final |
| Pipeline de dados | Python scripts, Airflow | Volume > 10K itens/dia |

---

## 🟢 AMPLIFICAR (IA boa + Time gosta)

**Principio**: Fazer melhor e mais rapido o que ja gosta. Humano lidera, IA potencializa.

### Padroes de amplificacao

| Padrao | Como funciona | Economia tipica |
|--------|--------------|-----------------|
| **Copiloto** | Humano pede ajuda pontual, IA responde | 20-30% do tempo |
| **Rascunho + revisao** | IA gera primeiro draft, humano refina | 40-60% do tempo |
| **Pesquisa + briefing** | IA coleta e sintetiza, humano decide | 50-70% do tempo de prep |
| **Review + feedback** | Humano cria, IA revisa e sugere melhorias | 30-50% do tempo de revisao |

### G4 OS como copiloto

| Tarefa | Como usar | Exemplo |
|--------|----------|---------|
| Brainstorm | Conversa direta | "Me ajuda com 10 abordagens para resolver [problema]" |
| Redigir | Conversa + MCP | "Escreve um email pro [nome] sobre [assunto] e manda pelo Gmail" |
| Analisar | Python inline | "Analisa esses dados e me mostra as 3 tendencias mais relevantes" |
| Preparar reuniao | Built-in skills | "Me prepara pro 1:1 com [nome] amanha" |
| Criar docs | Built-in skills | "Monta um deck com esses dados pra apresentacao de quinta" |
| Pesquisar | Web search + sintese | "Quais as melhores praticas de [tema] em 2026?" |

### Prompts de amplificacao (padrao RCDEF)

Ao gerar prompts para atividades AMPLIFICAR, o prompt deve:
- Definir o PAPEL do humano (nao da IA) — a IA e o assistente
- Incluir contexto REAL do aluno (ferramentas, produto, publico)
- Pedir OUTPUT parcial (rascunho, analise, opcoes) — nao final
- Especificar o que o humano vai FAZER com o output (revisar, apresentar, decidir)

---

## 🟡 QUEBRAR / BACKLOG (IA limitada + Time nao gosta)

**Principio**: Nao forcar. Mas decompor pode revelar sub-tarefas automatizaveis.

### Padrao de decomposicao

Para cada atividade neste quadrante, quebre em 4-6 sub-tarefas e reclassifique cada uma:

**Exemplo: "Negociar contratos" (IA 2, Satisfacao 2)**

| Sub-tarefa | IA Score | G4 OS faz? | Economia |
|-----------|---------|-----------|----------|
| Pesquisar benchmarks de mercado | **4** | Sim — web search + analise | 2h → 20min |
| Redigir primeira versao | **4** | Sim — gera rascunho | 3h → 30min |
| Revisar clausulas de risco | **4** | Sim — contract review | 1h → 15min |
| Conduzir a negociacao | **1** | Nao — humano faz | 0 |
| Documentar termos acordados | **4** | Sim — gera doc formatado | 1h → 10min |

**Resultado**: 4/5 sub-tarefas automatizaveis → 7h → 1h15 + negociacao

### Backlog inteligente

Para tarefas que realmente nao tem solucao IA hoje:
- **Registrar** com motivo especifico: "Requer julgamento politico", "Dados nao digitalizados"
- **Data de revisao**: 3-6 meses (modelos evoluem rapido)
- **Trigger**: "Revisar quando [evento] — ex: quando Zendesk lancar IA nativa para [feature]"

### Workaround — G4 OS no antes e depois

Mesmo quando a tarefa principal e humana:
- **Antes**: G4 OS prepara briefing, dados, contexto, checklist
- **Depois**: G4 OS documenta, organiza, distribui resultado
- **Durante**: Impossivel automatizar, mas as bordas sim

---

## ⚪ BAIXA PRIORIDADE (IA limitada + Time gosta)

**Principio**: Se funciona e o time gosta, nao mexa.

- Sem acao imediata
- Revisao trimestral — reavaliar capacidade IA
- Mencionar brevemente no diagnostico, nao gastar tempo aqui

---

## Template do Mini-Plano (top 3)

```markdown
## Acao #[N]: [Nome da atividade]

**Quadrante**: 🔴 AUTOMATIZAR / 🟢 AMPLIFICAR
**Scores**: IA [X] | Impacto [X] | Facilidade [X] | Final [X.X]
**Confianca**: Alta / Media / Baixa
**Por que incomoda**: [motivo especifico do discovery — repetitivo/ferramenta/emocional/etc.]

### Economia estimada
- **Hoje**: [X] vezes por [periodo] x [Y]min = [Z]h/mes para [N] pessoas
- **Com IA**: reducao de ~[%] → economia de **[W]h/mes**
- **Equivalente**: [W/160] FTEs de capacidade liberada

### Solucao recomendada
[3-5 linhas usando o contexto especifico do aluno — ferramentas que mencionou, volume real, canais]

### Com G4 OS (faca agora)
**Nivel [1/2/3]**: [Instrucao especifica]
Exemplo: "Me manda 3 chamados reais do seu Zendesk e eu mostro a classificacao + resposta automatica"

### Alternativa (sem G4 OS)
[Ferramenta + como configurar em 2-3 linhas]

### Prompt pronto
[Prompt RCDEF completo — especifico ao contexto do aluno, nao generico]

**Por que funciona (RCDEF):**
- **R**: [1 linha]
- **C**: [1 linha]
- **D**: [1 linha]
- **E**: [1 linha]
- **F**: [1 linha]

### Setup
**Dificuldade**: [Facil/Medio/Avancado] | **Tempo**: [estimativa] | **Pre-req**: [o que precisa]
```

---

## Demonstracao ao Vivo (acao #1)

A acao #1 SEMPRE e demonstrada ao vivo. Isso e o que transforma o diagnostico de relatorio em experiencia.

### O que pedir ao aluno

| Tipo de atividade | Pedir | Fallback se nao tiver |
|------------------|-------|----------------------|
| Classificar/triar | "Cola 3-5 itens reais (pode anonimizar)" | Gerar exemplos realistas do contexto |
| Redigir/responder | "Me passa o contexto de algo que precisa responder hoje" | Simular cenario baseado no produto/servico |
| Analisar dados | "Me manda a planilha ou cola os numeros" | Usar dados de exemplo do setor |
| Gerar relatorio | "Me diz o periodo e as fontes de dados" | Criar relatorio com dados simulados |
| Preparar reuniao | "Com quem e e quando? Qual a pauta?" | Simular prep baseado no contexto |

### Depois da demo

> Isso levou [X]. Normalmente, quanto tempo voce gasta?
> Se fossem [volume] por [periodo], seriam ~[calculo]h/mes economizadas.
>
> Quer que eu:
> 1. **Transforme isso numa skill** que voce roda sempre?
> 2. **Configure como automacao recorrente**?
> 3. **Faca mais um exemplo** pra voce ver a consistencia?

---

## Priorizacao de Implementacao

### Ordem (score final como base, mas com ajustes):

1. **Score final 4.0+ com facilidade 5** → Quick win imediato (fazer NA sessao)
2. **Score final 4.0+ com facilidade 3-4** → Implementar esta semana
3. **Score final 3.0-3.9** → Planejar para o mes
4. **QUEBRAR com decomposicao rica** → Implementar sub-tarefas viaveis agora

### Maximo de acoes por sessao

- **Top 3 detalhadas** — com economia, prompt, e setup
- **Demo ao vivo da #1** — obrigatorio
- **Restante em tabela resumo** — so quadrante + score + recomendacao de 1 linha
- Se o aluno quiser mais, oferecer nova sessao ou desdobrar
