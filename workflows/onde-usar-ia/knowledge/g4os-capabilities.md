# O que o G4 OS consegue fazer

Este arquivo documenta as capacidades reais do G4 OS para que o workflow possa recomendar solucoes concretas que o usuario executa na hora.

## Principio

> **G4 OS e a ferramenta primaria.** Toda recomendacao deve primeiro considerar: "da pra fazer isso aqui dentro?" Se sim, e a primeira opcao. Alternativas externas (ChatGPT, N8N, etc.) sao fallback para o que o G4 OS nao cobre.

---

## Capacidades por Categoria

### 1. Analise e Processamento de Dados
O G4 OS roda **Python inline** — sem instalar nada, sem sair da conversa.

| Capacidade | Como usar | Exemplo |
|-----------|----------|---------|
| Processar CSVs/Excel | Python com pandas | "Analisa esse CSV de vendas e me mostra tendencias" |
| Criar graficos | Python com matplotlib/seaborn | "Plota um grafico de receita por mes" |
| Manipular planilhas | Skill XLSX | "Abre essa planilha e adiciona uma coluna calculada" |
| Analisar PDFs | Leitura nativa + Python | "Extrai os dados desse contrato" |
| Processar em batch | `llm_map` (processar N itens em paralelo) | "Classifica esses 200 leads por potencial" |

**Prompt pro aluno:**
> "Cole seus dados aqui (tabela, CSV, ou descreva onde estao) e me diga o que quer descobrir."

### 2. Comunicacao e Mensagens
Conectado via MCP a ferramentas do dia a dia.

| Capacidade | MCP/Ferramenta | Exemplo |
|-----------|---------------|---------|
| Ler/enviar Slack | Slack MCP | "Manda um resumo no canal #vendas" |
| Ler/enviar email | Google Workspace (Gmail) | "Redige um email de follow-up pro Joao" |
| Ler/enviar Google Chat | Google Workspace | "Manda update no space do time" |
| Monitorar respostas | Vigia watchers | "Me avisa quando o Fulano responder no Slack" |

**Prompt pro aluno:**
> "Quer que eu redija e envie direto, ou prefere revisar antes?"

### 3. Gestao de Documentos e Conteudo
Cria, edita e organiza documentos.

| Capacidade | Como | Exemplo |
|-----------|------|---------|
| Criar Google Docs | Google Workspace | "Cria um doc com o status report da semana" |
| Editar Google Docs | Google Workspace | "Atualiza a secao de riscos nesse doc" |
| Criar Google Sheets | Google Workspace | "Monta uma planilha de tracking de OKRs" |
| Criar apresentacoes | Skills PPTX / Slides | "Monta um deck com esses dados" |
| Criar/editar Notion | Notion MCP | "Atualiza a pagina do projeto no Notion" |
| Gerar PDFs | HTML → PDF | "Gera um relatorio em PDF" |
| Criar web apps | Workflow Web App | "Monta um dashboard interativo" |

**Prompt pro aluno:**
> "Descreve o documento que precisa e eu crio agora."

### 4. Calendario e Agenda
Acesso direto ao Google Calendar.

| Capacidade | Como | Exemplo |
|-----------|------|---------|
| Ver agenda | Google Workspace (Calendar) | "O que tenho hoje?" |
| Criar eventos | Google Workspace | "Marca uma reuniao com o time amanha 14h" |
| Verificar disponibilidade | Google Workspace (freebusy) | "Quando o Joao e a Maria estao livres?" |
| Preparar para reunioes | Built-in skills | "Me prepara pro 1:1 com o Lucas" |

### 5. Automacao e Recorrencia
Tarefas que se repetem podem ser automatizadas.

| Capacidade | Como | Exemplo |
|-----------|------|---------|
| Jobs recorrentes | Scheduled actions | "Todo dia 8h manda resumo de metricas no Slack" |
| Monitorar e alertar | Vigia watchers | "Me avisa se alguem mencionar 'bug' no canal #suporte" |
| Workflows completos | Skills customizadas | "Cria uma skill que processa relatorios semanais" |
| Pesquisa web | Web search nativo | "Pesquisa as ultimas tendencias de IA em vendas" |
| Browser automation | Agent Browser skill | "Entra no dashboard X e extrai os dados" |

**Prompt pro aluno:**
> "Qual tarefa voce faz toda semana que segue sempre o mesmo padrao?"

### 6. Criacao de Skills e Workflows
O G4 OS pode criar novas ferramentas para si mesmo.

| Capacidade | Como | Exemplo |
|-----------|------|---------|
| Criar skills | Skill Creator | "Cria uma skill de analise semanal de vendas" |
| Criar workflows | Workflow Builder | "Monta um workflow de onboarding de cliente" |
| Construir web apps | Web App workflow | "Faz um app de calculadora de ROI" |

**Este e o superpoder**: o usuario nao precisa saber programar. Ele descreve o que precisa, e o G4 OS cria a ferramenta.

### 7. Pesquisa e Contexto
Busca informacoes de multiplas fontes.

| Capacidade | Como | Exemplo |
|-----------|------|---------|
| Web search | Nativo | "Quais as melhores praticas de cold email em 2026?" |
| Pesquisa academica | Web search + analise | "Resume o paper X sobre produtividade com IA" |
| Analise competitiva | Competitive Analysis workflow | "Analisa os concorrentes da empresa Y" |
| Busca em documentos | Google Drive search | "Encontra o ultimo relatorio de vendas no Drive" |

---

## Hierarquia de Recomendacao

Ao recomendar solucoes para cada atividade da matriz, siga esta ordem:

### Nivel 1: G4 OS direto (prioridade maxima)
"Voce pode fazer isso agora, aqui comigo."
- Cole dados → analise imediata
- Descreva o documento → criacao imediata
- Peca o email/mensagem → envio direto
- Defina a recorrencia → automacao configurada

### Nivel 2: G4 OS + skill/workflow novo
"Posso criar uma ferramenta personalizada pra isso."
- Skill customizada para tarefa recorrente
- Workflow para processo multi-etapa
- Web app para dashboard/calculadora

### Nivel 3: G4 OS como orquestrador + ferramenta externa
"Eu coordeno, a ferramenta externa executa a parte especifica."
- G4 OS prepara o prompt → aluno usa no ChatGPT/Gemini para tarefas que preferir fazer la
- G4 OS analisa dados → exporta pra Google Sheets/Notion para compartilhar
- G4 OS gera template → aluno customiza no Canva/Figma

### Nivel 4: Ferramenta externa autonoma (fallback)
"Para isso, a melhor opcao e usar [ferramenta X]. Aqui esta como:"
- N8N/Zapier para automacoes que rodam independente do G4 OS
- Ferramentas especializadas (Figma, Tableau, etc.)
- ChatGPT/Gemini/Copilot para contextos onde o usuario nao tem G4 OS

---

## Exemplos de Recomendacao por Quadrante

### AUTOMATIZAR — "G4 OS faz pra voce"
> **Atividade**: Gerar relatorio semanal de vendas
> **Recomendacao Nivel 1**: "Me pede toda segunda-feira: 'gera o relatorio de vendas da semana'. Eu puxo os dados, analiso, e mando no Slack do time."
> **Recomendacao Nivel 2**: "Posso criar uma acao recorrente que faz isso automaticamente toda segunda as 8h."

### AMPLIFICAR — "G4 OS te ajuda a fazer melhor"
> **Atividade**: Escrever propostas comerciais
> **Recomendacao Nivel 1**: "Me passa o contexto do cliente e eu gero um rascunho de proposta. Voce revisa e ajusta o tom."
> **Recomendacao Nivel 2**: "Posso criar uma skill proposta-comercial que sempre pede os inputs certos e gera no formato padrao da empresa."

### QUEBRAR/BACKLOG — "G4 OS resolve as partes que pode"
> **Atividade**: Negociar contratos
> **Recomendacao**: "Negociacao em si e humana, mas posso: (1) pesquisar benchmarks de mercado, (2) gerar a primeira versao do contrato, (3) revisar clausulas, (4) documentar os termos acordados."
