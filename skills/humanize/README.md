# Humanize Writing

Reescreve ou cria conteudo que soa naturalmente humano. Remove todos os 18 padroes de escrita AI identificados pelo guia "Signs of AI writing" da Wikipedia.

> **Nota**: Este skill e voltado para textos em **ingles**. Os anti-padroes sao especificos da escrita AI em ingles (puffery, participial padding, AI vocabulary, etc.).

## O que faz

- Pega texto gerado por AI ou texto rigido e reescreve para soar natural
- Cria conteudo novo do zero sem padroes de AI
- Aplica 18 regras especificas de anti-padroes

## Instalar

**Colar no G4 OS:**
```
Instale o skill "humanize" de https://github.com/Gestao-Quatro-Ponto-Zero/g4os-skills — clone o repo, copie skills/humanize/ para o diretorio de skills do meu G4 OS, e confirme que esta funcionando.
```

**Ou via terminal:**
```bash
curl -sL https://raw.githubusercontent.com/Gestao-Quatro-Ponto-Zero/g4os-skills/main/install.sh | bash -s -- skills/humanize
```

## Uso

No G4 OS, basta pedir:

> "Humanize this text: [cole o texto]"

Ou:

> "Write a blog post about X" (o skill ativa automaticamente quando envolve escrita)

## Arquivos

| Arquivo | Funcao |
|---------|--------|
| `SKILL.md` | Definicao do skill com todas as 18 regras de anti-padroes (em ingles) |
| `icon.svg` | Icone de caneta/edicao |
