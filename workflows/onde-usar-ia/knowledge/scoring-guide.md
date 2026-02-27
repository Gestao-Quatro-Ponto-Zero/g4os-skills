# Guia de Scoring Multidimensional

## 3 Dimensoes de Avaliacao

Cada atividade e avaliada em 3 eixos independentes. A combinacao determina prioridade.

| Dimensao | Peso | O que mede | Quem define |
|----------|-----:|------------|-------------|
| **Capacidade IA** | 40% | Quao boa a IA e nessa tarefa hoje | Dados AEI + knowledge do modelo |
| **Impacto de negocio** | 40% | Quanto tempo/dinheiro economiza | Dados do discovery (volume x tempo x pessoas) |
| **Facilidade de implementacao** | 20% | Quao facil e colocar pra rodar | Ferramentas disponiveis + maturidade do time |

**Score Final** = (Capacidade IA x 0.4) + (Impacto x 0.4) + (Facilidade x 0.2)

---

## Dimensao 1: Capacidade IA (1-5)

### Abordagem Honesta

O dataset AEI tem ~3.500 tarefas em ingles. Atividades descritas em portugues raramente tem match exato. **A abordagem e:**

1. **Match direto/proximo nos dados** → Use os scores → Confianca: **Alta**
2. **Sem match, mas tarefa bem conhecida em IA** → Estime baseado no estado da arte → Confianca: **Media**
3. **Tarefa ambigua ou niche** → Estime com cautela → Confianca: **Baixa**

**NUNCA force um fuzzy match ruim.** Se "Registrar chamados no Zendesk" matcha com uma tarefa de psicologia no AEI, e mais honesto estimar do que usar um dado falso.

### Fontes de Dados

The workflow includes a `data/` directory with download instructions (see `data/README.md`). Run `data/download.sh` to fetch the datasets from HuggingFace.

After download + first workflow run, the data directory will contain:

```
data/
  onet_task_statements.csv       → Lista de tarefas por ocupacao O*NET (download)
  onet_task_mappings.csv         → % de conversas Claude por tarefa (download)
  v4_task_ai_scores_lookup.json  → Scores por tarefa, chaves LOWERCASE (gerado)
  occupation_ai_summary.json     → Resumo por ocupacao, avg/max AI usage (gerado)
```

**Sem os dados**: o workflow funciona normalmente — usa estimativa do modelo (confianca "Media" ou "Baixa" ao inves de "Alta").

### Como buscar dados

```python
import json, csv

# 1. Carregar lookup (chaves lowercase)
with open('data/v4_task_ai_scores_lookup.json') as f:
    v4 = json.load(f)

# 2. Buscar por keywords (melhor que fuzzy match por nome completo)
keyword = "classify"  # ou "email", "report", "analyze"
matches = {k: v for k, v in v4.items() if keyword in k}

# 3. Para cada match, extrair o score de autonomia
for task_name, scores in matches.items():
    autonomy = scores.get('GLOBAL_autonomy_mean', 'N/A')
    print(f"  {task_name[:60]}... → autonomy: {autonomy}")
```

### Escala de Capacidade IA

| Score | Significado | Indicadores | Exemplos |
|------:|-------------|-------------|----------|
| **5** | IA faz sozinha com qualidade | Autonomia 4.5+, sucesso >85%, padrao "directive" | Classificar texto, traduzir, gerar codigo boilerplate |
| **4** | IA faz bem com supervisao leve | Autonomia 3.5-4.4, sucesso 70-85% | Redigir emails, analisar dados estruturados, criar apresentacoes |
| **3** | IA ajuda parcialmente | Autonomia 2.5-3.4, ou tarefa com componentes mistas | Preparar propostas (IA faz rascunho, humano personaliza) |
| **2** | IA ajuda pouco | Autonomia <2.5, ou tarefa muito contextual | Negociacao, gestao de conflito, decisoes politicas |
| **1** | IA ineficaz | Sem dados, tarefa fisica ou profundamente relacional | Trabalho manual, empatia profunda, lideranca presencial |

### Vieses conhecidos (calibrar manualmente)

- **Vies tech**: Programacao tem scores inflados (devs sao heavy users)
- **Vies anglofono**: Tarefas em contexto BR podem ter performance diferente
- **Ausencia ≠ incapacidade**: Se uma tarefa nao aparece no dataset, pode ser porque o publico-alvo nao usa IA (ainda), nao porque a IA nao consegue
- **Temporal**: Dados de Nov 2025 — modelos evoluem rapido. Tarefas com score 2-3 podem subir em 6 meses

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
| **Alta** | Match direto nos dados AEI + volume claro do aluno + ferramenta identificada | "Baseado em dados reais de 458K conversas com IA..." |
| **Media** | Estimativa informada + volume aproximado + ferramenta generica | "Com base no estado atual da tecnologia, tarefas como essa..." |
| **Baixa** | Sem dados, sem volume claro, contexto vago | "Esta e uma estimativa inicial — recomendo validar com um teste pratico" |
