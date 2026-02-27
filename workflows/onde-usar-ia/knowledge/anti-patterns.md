# Anti-Patterns: Erros Comuns ao Implementar IA

Incluir os anti-patterns relevantes no diagnostico final. Ajuda o aluno a evitar armadilhas comuns.

## Anti-Patterns de Diagnostico

### 1. "IA pra tudo"
**Erro**: Querer aplicar IA em todas as atividades ao mesmo tempo.
**Realidade**: Time tem capacidade limitada de absorver mudancas. Maximo 2-3 implementacoes simultaneas.
**Corrigir**: Priorizar pelo score final. Quick wins primeiro, projetos complexos depois.

### 2. "Solucao procurando problema"
**Erro**: "Ouvi falar de IA, quero usar em alguma coisa."
**Realidade**: Comecar pela dor, nao pela tecnologia. "O que ta doendo?" primeiro, "IA resolve?" segundo.
**Corrigir**: O diagnostico comeca com discovery (dor + contexto), nao com IA.

### 3. "ChatGPT resolve"
**Erro**: Achar que colar texto no ChatGPT = implementar IA.
**Realidade**: Valor real vem de IA integrada ao fluxo de trabalho (nao de copy-paste entre abas).
**Corrigir**: Recomendar solucoes que se integram as ferramentas existentes. G4 OS conecta, N8N automatiza.

### 4. "Prompt magico"
**Erro**: Buscar o "prompt perfeito" que resolve tudo.
**Realidade**: Bons resultados vem de bons inputs (contexto, dados, restricoes), nao de formulas magicas. 3 iteracoes > 1 prompt perfeito.
**Corrigir**: Ensinar RCDEF como framework de pensamento, nao como receita.

### 5. "IA substitui pessoa"
**Erro**: Apresentar IA como substituto de funcionarios.
**Realidade**: IA libera capacidade. Time pode dedicar horas economizadas a tarefas de maior valor.
**Corrigir**: Sempre enquadrar como "liberar X horas para [atividade de maior valor]", nunca como "eliminar X pessoas".

## Anti-Patterns de Implementacao

### 6. "Automatizar sem entender o processo"
**Erro**: Automatizar uma atividade sem mapear o fluxo completo.
**Realidade**: Automatizar um processo ruim resulta em processo ruim mais rapido.
**Corrigir**: Na fase de discovery, perguntar "como funciona hoje, passo a passo?" antes de recomendar automacao.

### 7. "Piloto eterno"
**Erro**: Testar IA com 1 pessoa por meses sem escalar.
**Realidade**: Valor so se materializa quando o time todo adota. Piloto deve ter prazo definido (2-4 semanas) e criterios de sucesso.
**Corrigir**: Incluir "criterios de sucesso" e "prazo do piloto" em cada recomendacao.

### 8. "IA sem feedback loop"
**Erro**: Implementar IA e nunca medir se esta funcionando.
**Realidade**: Qualidade do output degrada se ninguem monitora. Prompts precisam de refinamento.
**Corrigir**: Para cada acao, definir 1 metrica simples de sucesso (tempo economizado, taxa de acerto, satisfacao).

### 9. "Over-engineer na primeira semana"
**Erro**: Construir pipeline complexo (API + banco + frontend) antes de validar que a IA resolve.
**Realidade**: Comece com prompt no chat → se funciona, crie skill → se escala, automatize.
**Corrigir**: Recomendar a hierarquia G4 OS (direto → skill → orquestrador → externo).

### 10. "Dados sensiveis no prompt"
**Erro**: Colar dados confidenciais (salarios, CPFs, estrategia) em IA sem pensar.
**Realidade**: Dados compartilhados com IA devem respeitar politica da empresa.
**Corrigir**: Sempre perguntar: "Esses dados podem ser compartilhados com IA? Precisa anonimizar algo?"

## Anti-Patterns de Expectativa

### 11. "Resultado perfeito de primeira"
**Erro**: Esperar que IA gere output final na primeira tentativa.
**Realidade**: Resultado bom = prompt + 2-3 iteracoes. 70% na primeira, 95% na terceira.
**Corrigir**: Ensinar o ciclo gerar → revisar → refinar. Iteracao e feature, nao bug.

### 12. "IA precisa de zero contexto"
**Erro**: Achar que IA sabe o contexto da empresa/time/projeto sem ser informada.
**Realidade**: IA e poderosa mas amnesica. Contexto precisa ser dado a cada conversa (ou configurado em skills/projects).
**Corrigir**: Ensinar a incluir contexto no prompt (o C do RCDEF).

### 13. "Funciona no demo, funciona em producao"
**Erro**: Assumir que uma demo bem-sucedida = implementacao garantida.
**Realidade**: Casos de borda, variacoes de input, e resistencia do time sao reais.
**Corrigir**: Incluir "limitacoes conhecidas" em cada recomendacao.

## Como Incluir no Diagnostico

No resultado final, selecione os 2-3 anti-patterns mais relevantes para o contexto do aluno e apresente como:

> **Armadilhas a evitar:**
> - [Anti-pattern relevante] — [explicacao de 1 linha contextualizada]
> - [Anti-pattern relevante] — [explicacao de 1 linha contextualizada]
> - [Anti-pattern relevante] — [explicacao de 1 linha contextualizada]

Escolha baseado em:
- Se o aluno disse "nunca usamos IA" → incluir #4, #11, #12
- Se quer "automatizar tudo" → incluir #1, #6, #9
- Se mencionou dados sensiveis → incluir #10
- Se e lider/gestor → incluir #5, #7, #8
