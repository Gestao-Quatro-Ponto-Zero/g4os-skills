# Conciliacao Financeira

Conciliacao automatica de extratos bancarios com gateways de pagamento, ERPs ou outras fontes financeiras. Aceita PDF, CSV, XLSX, XML, OFX e TXT.

## O que faz

- Recebe dois lados (gateway/ERP vs banco) e cruza transacoes automaticamente
- Motor de matching multi-pass em Python: exato, data flexivel, valor flexivel, fuzzy, e batch (N:1)
- Parsers conhecidos para Stripe, Itau PDF, Nubank CSV, OFX/QFX, e NFe XML
- Detecta formatos desconhecidos e pede mapeamento ao usuario
- Apresenta resultados em tabelas interativas: conciliados, divergencias, e itens sem match
- Sugere sub-rotinas reutilizaveis para conciliacoes recorrentes

## Pre-requisitos

- Python 3.9+ com `pandas` instalado (`pip install pandas`)
- Para PDFs: requer LLM com capacidade de leitura de documentos (o G4 OS usa `call_llm`)

## Instalar

**Colar no G4 OS:**
```
Instale o skill "conciliacao" de https://github.com/Gestao-Quatro-Ponto-Zero/g4os-skills — clone o repo, copie skills/conciliacao/ para o diretorio de skills do meu G4 OS, confirme que pandas esta instalado, e teste que esta funcionando.
```

**Ou via terminal:**
```bash
curl -sL https://raw.githubusercontent.com/Gestao-Quatro-Ponto-Zero/g4os-skills/main/install.sh | bash -s -- skills/conciliacao
pip install pandas  # se nao tiver
```

## Uso

No G4 OS, basta pedir:

> "Concilia esse extrato do Itau com os payouts do Stripe"

Ou use o comando:

> `/conciliacao`

Depois arraste ou indique os arquivos dos dois lados.

## Arquivos

| Arquivo | Funcao |
|---------|--------|
| `SKILL.md` | Definicao do skill com fluxo completo de execucao |
| `scripts/reconcile.py` | Motor de reconciliacao multi-pass em Python |
| `references/parsers.md` | Parsers conhecidos e schema canonico de transacoes |
| `icon.svg` | Icone de grafico/barras |
