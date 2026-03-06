# G4 OS Skills & Workflows

Skills e workflows da comunidade para o [G4 OS](https://g4os.dev) — a plataforma de AI Chief of Staff.

Skills sao ferramentas de proposito unico. Workflows sao processos multi-fase com bases de conhecimento. Ambos se instalam com um comando.

---

## Catalogo

### Skills

| Skill | Descricao | Instalar |
|-------|-----------|----------|
| **[Humanize Writing](skills/humanize/)** | Reescreve conteudo para soar naturalmente humano. Remove 18 padroes de escrita AI segundo a Wikipedia. *Para textos em ingles.* | `skills/humanize` |
| **[Video Combiner](skills/video-combiner/)** | Combina segmentos de video Hook + Body + CTA em variacoes de ads com legendas automaticas em multiplos aspect ratios | `skills/video-combiner` |
| **[Conciliacao Financeira](skills/conciliacao/)** | Conciliacao automatica de extratos bancarios com gateways, ERPs ou outras fontes — motor multi-pass em Python, parsers para Stripe/Itau/Nubank/OFX/NFe | `skills/conciliacao` |
| **[RFM Analysis](skills/rfm-analysis/)** | Segmentacao de clientes com scoring RFM, clustering K-Means, e insights de marketing — inclui dataset de exemplo para demo imediata | `skills/rfm-analysis` |

### Workflows

| Workflow | Descricao | Instalar |
|----------|-----------|----------|
| **[Onde Usar IA](workflows/onde-usar-ia/)** | Diagnostico interativo de IA generativa — matriz 2x2, business case quantificado, demo ao vivo | `workflows/onde-usar-ia` |
| **[Cortes Virais](workflows/cortes-virais/)** | Transforma entrevistas/podcasts do YouTube em 5-7 cortes verticais (9:16) de 60-90s com hook teaser e legendas dinamicas | `workflows/cortes-virais` |
| **[Ecossistema de Vendas](workflows/ecossistema-vendas/)** | 3 ferramentas praticas para construir seu ecossistema de vendas — priorizacao de canais (matriz 2x2), alocacao de budget (70/20/10), e comp plan com aceleradores. Framework Alfredo Soares. | `workflows/ecossistema-vendas` |
| **[Mentalidade de Growth](workflows/mentalidade-growth/)** | 3 ferramentas para destravar crescimento — escada de valor (LTV), diagnostico de maturidade (radar 4 areas), e analise RFV (11 segmentos). Framework Bruno Nardon. | `workflows/mentalidade-growth` |

---

## Instalacao

### Opcao A: Colar no G4 OS (recomendado)

Copie e cole um desses prompts em uma conversa do G4 OS:

**Humanize Writing:**
```
Instale o skill "humanize" de https://github.com/Gestao-Quatro-Ponto-Zero/g4os-skills — clone o repo, copie skills/humanize/ para o diretorio de skills do meu G4 OS, e confirme que esta funcionando.
```

**Video Combiner:**
```
Instale o skill "video-combiner" de https://github.com/Gestao-Quatro-Ponto-Zero/g4os-skills — clone o repo, copie skills/video-combiner/ para o diretorio de skills do meu G4 OS, instale as dependencias (brew install ffmpeg whisper-cpp), e confirme que esta funcionando.
```

**Onde Usar IA:**
```
Instale o workflow "onde-usar-ia" de https://github.com/Gestao-Quatro-Ponto-Zero/g4os-skills — clone o repo, copie workflows/onde-usar-ia/ para o diretorio de workflows do meu G4 OS, depois execute data/download.sh para baixar os datasets de scoring. Confirme que esta funcionando.
```

**Conciliacao Financeira:**
```
Instale o skill "conciliacao" de https://github.com/Gestao-Quatro-Ponto-Zero/g4os-skills — clone o repo, copie skills/conciliacao/ para o diretorio de skills do meu G4 OS, confirme que pandas esta instalado (pip install pandas), e teste que esta funcionando.
```

**RFM Analysis:**
```
Instale o skill "rfm-analysis" de https://github.com/Gestao-Quatro-Ponto-Zero/g4os-skills — clone o repo, copie skills/rfm-analysis/ para o diretorio de skills do meu G4 OS, confirme que pandas e scikit-learn estao instalados, e teste que esta funcionando.
```

**Cortes Virais:**
```
Instale o workflow "cortes-virais" de https://github.com/Gestao-Quatro-Ponto-Zero/g4os-skills — clone o repo, copie workflows/cortes-virais/ para o diretorio de workflows do meu G4 OS, instale as dependencias (brew install yt-dlp ffmpeg whisper-cpp + download do modelo ggml-medium.bin), e confirme que esta funcionando.
```

**Ecossistema de Vendas:**
```
Instale o workflow "ecossistema-vendas" de https://github.com/Gestao-Quatro-Ponto-Zero/g4os-skills — clone o repo, copie workflows/ecossistema-vendas/ para o diretorio de workflows do meu G4 OS, e confirme que esta funcionando. Depois me apresente o que o workflow faz e como usar.
```

**Mentalidade de Growth:**
```
Instale o workflow "Mentalidade de Growth" do repositório g4os-skills: https://github.com/Gestao-Quatro-Ponto-Zero/g4os-skills/tree/main/workflows/mentalidade-growth
```

O G4 OS cuida do git clone, copia para o caminho correto do workspace, e verifica a instalacao.

### Opcao B: Comando no terminal

```bash
curl -sL https://raw.githubusercontent.com/Gestao-Quatro-Ponto-Zero/g4os-skills/main/install.sh | bash -s -- <caminho>
```

**Exemplos:**

```bash
# Instalar o skill humanize
curl -sL https://raw.githubusercontent.com/Gestao-Quatro-Ponto-Zero/g4os-skills/main/install.sh | bash -s -- skills/humanize

# Instalar o workflow onde-usar-ia
curl -sL https://raw.githubusercontent.com/Gestao-Quatro-Ponto-Zero/g4os-skills/main/install.sh | bash -s -- workflows/onde-usar-ia
```

### Opcao C: Manual

Clone o repo e copie a pasta desejada:

```bash
git clone https://github.com/Gestao-Quatro-Ponto-Zero/g4os-skills.git
cp -r g4os-skills/skills/humanize ~/.g4os/workspaces/<seu-workspace>/skills/
```

---

## Example Datasets

Alguns skills incluem datasets de exemplo para demonstracao e testes. Rode o skill sem anexar arquivo para usar o dataset automaticamente.

| Dataset | Skill | Linhas | Descricao | Fonte |
|---------|-------|--------|-----------|-------|
| [ecommerce_sales_data.csv](skills/rfm-analysis/datasets/ecommerce_sales_data.csv) | RFM Analysis | 10,000 (sample) | E-commerce multi-categoria — ~1.8K clientes, 7 categorias, 1 ano de transacoes. Full 100K via `download_full.sh` | [Kaggle](https://www.kaggle.com/datasets/thedevastator/unlock-profits-with-e-commerce-sales-data) |

---

## Como funciona

Um skill e uma pasta com um arquivo `SKILL.md`:

```
meu-skill/
├── SKILL.md          # Obrigatorio: YAML frontmatter + instrucoes
├── icon.svg          # Opcional: icone para a UI
├── references/       # Opcional: documentos de referencia carregados sob demanda
└── scripts/          # Opcional: scripts executaveis
```

Um workflow e uma pasta com um arquivo `WORKFLOW.md`:

```
meu-workflow/
├── WORKFLOW.md       # Obrigatorio: YAML frontmatter + instrucoes multi-fase
└── knowledge/        # Opcional: arquivos de conhecimento do dominio
```

### Formato do SKILL.md / WORKFLOW.md

```yaml
---
name: "Nome de Exibicao"
description: "O que faz e quando acionar"
icon: "🔧"                              # emoji opcional
---

# Instrucoes

O corpo em markdown contem as instrucoes que o G4 OS segue
quando este skill/workflow esta ativo.
```

O G4 OS descobre skills e workflows automaticamente pelo filesystem. Nenhum passo de registro necessario.

---

## Contribuindo

1. Fork este repo
2. Crie uma nova pasta em `skills/` ou `workflows/`
3. Adicione um `SKILL.md` ou `WORKFLOW.md` com frontmatter valido
4. Adicione um `README.md` com descricao e comando de instalacao
5. Envie um PR

### Diretrizes

- Mantenha o arquivo principal de definicao abaixo de 500 linhas. Mova material de referencia detalhado para `references/` ou `knowledge/`
- Sem caminhos hardcoded — use caminhos relativos ou `$HOME`
- Inclua um `README.md` com o comando de instalacao
- Teste o script de instalacao antes de submeter

---

## Licenca

MIT
