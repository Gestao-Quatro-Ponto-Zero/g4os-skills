# Onde Usar IA

Diagnostico interativo de IA generativa. Ajuda profissionais e times a descobrir **onde e como usar IA** no trabalho, com matriz 2x2, business case quantificado, e demonstracao ao vivo.

## O que faz

- Entrevista de discovery para entender o contexto real (area, ferramentas, volume, dores)
- Mapeia 8-12 atividades concretas do dia a dia
- Pontua cada atividade em 3 dimensoes: capacidade IA, impacto de negocio, facilidade
- Classifica em matriz 2x2 (Automatizar / Amplificar / Quebrar / Baixa prioridade)
- Quantifica economia em horas/mes e FTEs
- Detalha top 3 acoes com prompts prontos (framework RCDEF)
- Demonstra a acao #1 ao vivo na sessao

Baseado em dados do Anthropic Economic Index (milhoes de conversas) e GDPVal (220 tarefas profissionais).

## Instalar

```bash
curl -sL https://raw.githubusercontent.com/Gestao-Quatro-Ponto-Zero/g4os-skills/main/install.sh | bash -s -- workflows/onde-usar-ia
```

## Usar

No G4 OS, digite:

> `/onde-usar-ia`

Ou simplesmente:

> "Quero descobrir onde usar IA no meu time de vendas"

## Arquivos

| Arquivo | Conteudo |
|---------|----------|
| `WORKFLOW.md` | Workflow completo em 8 fases |
| `knowledge/discovery-framework.md` | Perguntas de contexto por area (vendas, marketing, suporte, financeiro, RH, tech, gestao) |
| `knowledge/scoring-guide.md` | Metodologia de scoring 3D com calibracao e exemplos |
| `knowledge/action-playbook.md` | Templates de recomendacao por quadrante |
| `knowledge/anti-patterns.md` | 13 erros comuns ao implementar IA |
| `knowledge/g4os-capabilities.md` | Capacidades do G4 OS por categoria |
| `knowledge/occupation-mappings.md` | Mapeamento cargos brasileiros → O*NET |
| `knowledge/prompt-building-guide.md` | Framework RCDEF com exemplos por area |
