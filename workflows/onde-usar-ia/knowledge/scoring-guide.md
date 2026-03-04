# Guia de Scoring Multidimensional

## 3 Dimensoes de Avaliacao

Cada atividade e avaliada em 3 eixos independentes. A combinacao determina prioridade.

| Dimensao | Peso | O que mede | Quem define |
|----------|-----:|------------|-------------|
| **Capacidade IA** | 40% | Quao boa a IA e nessa tarefa hoje | METR Horizon (duracao vs horizonte do modelo) + AEI como validacao |
| **Impacto de negocio** | 40% | Quanto tempo/dinheiro economiza | Dados do discovery (volume x tempo x pessoas) |
| **Facilidade de implementacao** | 20% | Quao facil e colocar pra rodar | Ferramentas disponiveis + maturidade do time |

**Score Final** = (Capacidade IA x 0.4) + (Impacto x 0.4) + (Facilidade x 0.2)

---

## Dimensao 1: Capacidade IA (1-5)

### Metodologia: METR Horizon

A avaliacao de capacidade IA usa o **METR Horizon** como referencia empirica primaria. O METR Horizon mede a duracao maxima de tarefa (em horas de trabalho humano) que modelos de IA completam com determinada taxa de sucesso:

- **p80 Horizon**: Tarefas ate essa duracao → modelo acerta ≥80% — **alta confiabilidade**
- **p50 Horizon**: Tarefas ate essa duracao → modelo acerta ≥50% — **confiabilidade moderada**

**Principio**: Se a tarefa leva T horas para um humano e T esta dentro do p80 horizon do modelo, a IA provavelmente completa com >80% de sucesso. Quanto mais curta a tarefa relativo ao horizonte, mais confiavel.

Consulte `knowledge/metr-horizon-reference.md` para a tabela completa de modelos, horizontes, intervalos de confianca, e exemplos praticos.

### Pre-condicao: Tarefa Digital

O METR Horizon mede tarefas executadas em computador. **Pre-filtro obrigatorio:**

- ✅ Tarefa executada primariamente em computador (email, planilha, sistema, codigo, texto, dados)
- ❌ Tarefa que exige presenca fisica (visita a cliente, trabalho manual, producao)
- ❌ Tarefa que exige interacao humana em tempo real como componente CENTRAL (negociacao presencial, coaching 1:1)
- ⚠️ Tarefas hibridas: avaliar a parte digital separadamente

**Se a tarefa nao e digital → Score maximo = 2** (IA pode ajudar na preparacao, mas nao na execucao).

### Modelo de Referencia

O score depende de qual modelo/ferramenta o usuario usa. Capturado na Fase 2 (discovery).

| Ferramenta | Modelo de referencia (Mar 2026) | p80 (h) | p50 (h) |
|------------|-------------------------------|---------|---------|
| ChatGPT Plus/Pro/Enterprise | GPT-5.2 | 66 | 352 |
| Claude Pro / G4 OS | Claude Opus 4.6 | 70 | 719 |
| Gemini Advanced | Gemini 3 Pro | 54 | 224 |
| Microsoft Copilot | GPT-5.1 (est.) | 51 | 224 |
| "Qualquer" / "Nao sei" | Frontier (Claude Opus 4.6) | 70 | 719 |

### Escala de Capacidade IA

Dado **T** = tempo estimado por ocorrencia da tarefa (coletado na Fase 3), e p80/p50 do modelo de referencia do usuario:

| Score | Condicao | Interpretacao |
|------:|----------|---------------|
| **5** | T ≤ 2h, digital, estruturada/repetitiva | Dentro do horizonte de todos os modelos atuais. IA completa sozinha |
| **4** | T ≤ 2h digital (com julgamento), OU T entre 2-12h digital | Maioria dos modelos lida bem. IA faz com supervisao leve |
| **3** | T entre 12h e p80 do modelo, digital | Dentro do p80 do modelo. IA consegue com setup estruturado |
| **2** | T entre p80 e p50, OU forte componente contextual/relacional | No limite do horizonte. IA ajuda parcialmente, humano lidera |
| **1** | T > p50 OU tarefa nao-digital | Alem do horizonte. Ineficaz para automacao end-to-end |

### Modificadores Qualitativos

Apos o score base por duracao, aplicar modificadores:

| Fator | Modificador | Exemplo |
|-------|------------|---------|
| Repetitiva / padronizada | +1 (max 5) | Classificar tickets, preencher formularios |
| Dados estruturados disponiveis | +0.5 (max 5) | Planilha ou banco de dados como input |
| Contexto organizacional profundo | -1 | Decisoes politicas, historico de cliente longo |
| Criatividade original | -0.5 | Design grafico original, estrategia inedita |
| Regulamentado / compliance | -0.5 | Laudos medicos, contratos regulados |
| Multi-step com dependencias externas | -1 | Aprovacao de terceiros no meio |

**Score final IA = clamp(score_base + modificadores, 1, 5)**

### Dados complementares (AEI)

O dataset AEI (~3.500 tarefas) pode ser usado como **validacao secundaria** quando disponivel:

The workflow includes a `data/` directory with download instructions (see `data/README.md`). Run `data/download.sh` to fetch the datasets from HuggingFace.

After download + first workflow run, the data directory will contain:

```
data/
  onet_task_statements.csv       → Lista de tarefas por ocupacao O*NET (download)
  onet_task_mappings.csv         → % de conversas Claude por tarefa (download)
  v4_task_ai_scores_lookup.json  → Scores por tarefa, chaves LOWERCASE (gerado)
  occupation_ai_summary.json     → Resumo por ocupacao, avg/max AI usage (gerado)
  metr_horizon_v1_1.yaml         → Dados brutos METR Horizon v1.1
```

**Como usar AEI para validacao:**

```python
import json

# Carregar lookup (chaves lowercase)
with open('data/v4_task_ai_scores_lookup.json') as f:
    v4 = json.load(f)

# Buscar por keywords
keyword = "classify"
matches = {k: v for k, v in v4.items() if keyword in k}

# Se match direto/proximo → confirma ou ajusta o score METR
# Se conflito → prevalece o METR (mais recente e empirico)
# Se sem match → confiar no score baseado no METR Horizon
```

**NUNCA force um fuzzy match ruim no AEI.** Se nao houver match claro, confie no score baseado no METR Horizon.

### Vieses conhecidos (calibrar manualmente)

- **Vies de task type**: METR testa tarefas de software/research — atividades de escrita, analise e criacao podem ter performance ligeiramente diferente
- **Vies anglofono**: Tarefas em contexto BR podem ter performance diferente
- **Scaffold matters**: Performance depende de como a IA e orquestrada (prompt, ferramentas, contexto). Scores METR usam scaffolds otimizados
- **Temporal**: Horizonte dobra a cada ~4 meses. Tarefas com score 2-3 podem subir em 6 meses. Data de referencia dos dados: Marco 2026

---

## Dimensao 2: Impacto de Negocio (1-5)

### Calculo baseado no Discovery

```
Horas_semanais_time = Frequencia_semanal x Tempo_por_vez x No_pessoas

Score 5: > 20h/semana de time (> 80h/mes)
Score 4: 10-20h/semana (40-80h/mes)
Score 3: 5-10h/semana (20-40h/mes)
Score 2: 2-5h/semana (8-20h/mes)
Score 1: < 2h/semana (< 8h/mes)
```

### Exemplos concretos

| Atividade | Frequencia | Tempo | Pessoas | Total/semana | Score |
|-----------|-----------|-------|---------|-------------|------:|
| Classificar 80 chamados/dia | 5x/sem | 5min cada = 400min/dia | 3 | 100h | **5** |
| Gerar relatorio semanal | 1x/sem | 3h | 1 | 3h | **2** |
| Redigir propostas comerciais | 5x/sem | 2h | 4 | 40h | **5** |
| Preparar 1:1 semanal | 1x/sem | 30min | 1 | 0.5h | **1** |
| Responder emails de clientes | 5x/sem | 1h/dia | 3 | 15h | **4** |

**IMPORTANTE**: Usar os dados reais do discovery, nao estimativas genericas. Se o aluno disse "a gente recebe uns 80 chamados por dia", use 80.

### Quando o aluno nao deu volume

Se o discovery nao deu dados suficientes:
1. Estimar baseado em benchmarks do setor
2. Marcar como "estimado" na tabela
3. Perguntar: "Estou estimando que voces lidam com ~[X] por [periodo]. Ta na faixa?"

---

## Dimensao 3: Facilidade de Implementacao (1-5)

### Fatores que determinam facilidade

| Fator | Facilita (→5) | Dificulta (→1) |
|-------|--------------|----------------|
| **Ferramenta** | G4 OS faz direto ou tem skill | Precisa de desenvolvimento custom |
| **Dados** | Dados ja existem e sao acessiveis | Dados nao existem ou sao desestruturados |
| **Maturidade** | Time ja usa alguma IA | Time nunca usou IA |
| **Integracao** | Ferramenta do aluno tem API/integracao | Sistema legado sem API |
| **Aprovacoes** | Pode comecar sozinho | Precisa de aprovacao de IT/compliance |

### Escala

| Score | Setup | Exemplos |
|------:|-------|----------|
| **5** | Agora, 0 setup | Prompt pronto no G4 OS, conversa direta |
| **4** | 1-2h | Criar skill customizada, configurar acao recorrente |
| **3** | 1 dia | Integrar com ferramenta existente, treinar time |
| **2** | 1 semana+ | Desenvolvimento de workflow, setup de N8N |
| **1** | Meses | Projeto complexo, multiplos stakeholders, compliance |

### Boost por contexto do aluno

Se o aluno mencionou no discovery:
- "Ja uso ChatGPT/Claude" → +1 na facilidade (time sabe usar IA)
- "Temos [ferramenta] com API" → +1 se a solucao usa essa API
- "Nunca usamos IA" → -1 (curva de aprendizado)
- "Preciso de aprovacao do TI" → -1 (burocracia)

---

## Score Final e Priorizacao

### Calculo

```python
score_final = (capacidade_ia * 0.4) + (impacto * 0.4) + (facilidade * 0.2)
```

### Faixas de prioridade

| Score Final | Prioridade | Acao |
|------------|-----------|------|
| **4.0+** | 🔴 Urgente | Implementar esta semana |
| **3.0-3.9** | 🟡 Importante | Implementar este mes |
| **2.0-2.9** | 🔵 Backlog | Planejar para proximo trimestre |
| **< 2.0** | ⚪ Nao priorizar | Revisitar quando tecnologia evoluir |

### Desempate

Quando dois scores finais sao iguais:
1. Maior impacto de negocio ganha (tempo do time > capacidade IA)
2. Maior facilidade ganha (quick wins > projetos complexos)
3. Atividade que e a "dor principal" do discovery ganha

---

## Economia Estimada por Atividade

### Formula de economia

```
Horas_economizadas_mes = Freq_mensal x Tempo x %_automacao x No_pessoas

Onde %_automacao:
- AUTOMATIZAR + IA score 5: 80%
- AUTOMATIZAR + IA score 4: 60%
- AUTOMATIZAR + IA score 3: 40%
- AMPLIFICAR + IA score 5: 50%
- AMPLIFICAR + IA score 4: 30%
- AMPLIFICAR + IA score 3: 20%
```

### Exemplo trabalhado

```
Atividade: Classificar e responder chamados N0
Frequencia: 80/dia x 22 dias = 1.760/mes
Tempo: 5min = 0.083h por chamado
Pessoas: 3
Quadrante: AUTOMATIZAR (IA score 4.5, satisfacao 2)
%_automacao: 70% (entre 60% e 80%)

Economia = 1.760 x 0.083h x 0.70 x 3 = 307h/mes
Equivalente: 1.9 FTEs (307 / 160)

Em reais (se salario medio R$4.000):
R$ 4.000 x 1.9 = R$ 7.600/mes de capacidade liberada
```

**NOTA**: Economia nao significa demissao. Significa que o time pode dedicar essas horas a atividades de maior valor (N1, N2, retencao proativa, etc.).

---

## Nivel de Confianca

Sempre classificar cada score:

| Nivel | Criterios | Linguagem |
|-------|-----------|-----------|
| **Alta** | Duracao clara + dentro do p80 METR + validacao AEI + volume claro do aluno | "Baseado no METR Horizon, tarefas de ate Xh tem >80% de taxa de sucesso em modelos como..." |
| **Media** | Duracao estimada + dentro do horizonte mas sem validacao AEI | "Com base no horizonte empirico do modelo, tarefas dessa duracao tendem a..." |
| **Baixa** | Duracao incerta, ou tarefa no limite entre faixas, ou contexto vago | "Esta e uma estimativa inicial — recomendo validar com um teste pratico" |
