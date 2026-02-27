#!/bin/bash
# G4 OS Skills Installer
# Uso: curl -sL https://raw.githubusercontent.com/Gestao-Quatro-Ponto-Zero/g4os-skills/main/install.sh | bash -s -- <tipo>/<slug>
#
# Exemplos:
#   curl -sL .../install.sh | bash -s -- skills/humanize
#   curl -sL .../install.sh | bash -s -- workflows/onde-usar-ia

set -euo pipefail

REPO="Gestao-Quatro-Ponto-Zero/g4os-skills"
BRANCH="main"
TARGET_PATH="${1:-}"

if [ -z "$TARGET_PATH" ]; then
  echo "Uso: $0 <tipo>/<slug>"
  echo ""
  echo "Disponiveis:"
  echo "  skills/humanize          - Reescreve conteudo para soar naturalmente humano"
  echo "  skills/video-combiner    - Combina segmentos de video Hook+Body+CTA"
  echo "  workflows/onde-usar-ia   - Diagnostico de implementacao de IA"
  echo ""
  echo "Exemplo:"
  echo "  curl -sL https://raw.githubusercontent.com/$REPO/$BRANCH/install.sh | bash -s -- skills/humanize"
  exit 1
fi

# Extrair tipo e slug
TYPE=$(echo "$TARGET_PATH" | cut -d'/' -f1)
SLUG=$(echo "$TARGET_PATH" | cut -d'/' -f2)

if [ "$TYPE" != "skills" ] && [ "$TYPE" != "workflows" ]; then
  echo "Erro: Tipo deve ser 'skills' ou 'workflows', recebido '$TYPE'"
  exit 1
fi

# Encontrar workspace do G4 OS
G4OS_DIR="$HOME/.g4os/workspaces"
if [ ! -d "$G4OS_DIR" ]; then
  echo "Erro: Diretorio de workspace do G4 OS nao encontrado em $G4OS_DIR"
  echo "Certifique-se de que o G4 OS esta instalado."
  exit 1
fi

# Encontrar o workspace ativo (primeiro diretorio)
WORKSPACE=$(ls -1 "$G4OS_DIR" | head -n1)
if [ -z "$WORKSPACE" ]; then
  echo "Erro: Nenhum workspace do G4 OS encontrado"
  exit 1
fi

DEST="$G4OS_DIR/$WORKSPACE/$TYPE/$SLUG"

# Verificar se ja esta instalado
if [ -d "$DEST" ]; then
  echo "Aviso: $TYPE/$SLUG ja existe em $DEST"
  read -p "Sobrescrever? [s/N] " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
    echo "Cancelado."
    exit 0
  fi
  rm -rf "$DEST"
fi

echo "Instalando $TYPE/$SLUG em $DEST..."

# Criar diretorio temporario
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

# Download via git sparse checkout (ou fallback para tarball)
if command -v git &> /dev/null; then
  cd "$TMPDIR"
  git init -q
  git remote add origin "https://github.com/$REPO.git"
  git config core.sparseCheckout true
  echo "$TARGET_PATH/" >> .git/info/sparse-checkout
  git pull -q origin "$BRANCH" 2>/dev/null

  if [ -d "$TARGET_PATH" ]; then
    mkdir -p "$(dirname "$DEST")"
    cp -r "$TARGET_PATH" "$DEST"
  else
    echo "Erro: $TARGET_PATH nao encontrado no repositorio"
    exit 1
  fi
else
  # Fallback: baixar tarball e extrair
  curl -sL "https://github.com/$REPO/archive/$BRANCH.tar.gz" -o "$TMPDIR/repo.tar.gz"
  tar -xzf "$TMPDIR/repo.tar.gz" -C "$TMPDIR"

  EXTRACTED="$TMPDIR/g4os-skills-$BRANCH/$TARGET_PATH"
  if [ -d "$EXTRACTED" ]; then
    mkdir -p "$(dirname "$DEST")"
    cp -r "$EXTRACTED" "$DEST"
  else
    echo "Erro: $TARGET_PATH nao encontrado no repositorio"
    exit 1
  fi
fi

# Verificar instalacao
if [ "$TYPE" = "skills" ] && [ -f "$DEST/SKILL.md" ]; then
  NAME=$(grep '^name:' "$DEST/SKILL.md" | head -1 | sed 's/name: *"\(.*\)"/\1/')
  echo ""
  echo "Instalado: $NAME"
  echo "Local: $DEST"
  echo ""
  echo "O skill ja esta disponivel no G4 OS. Inicie uma nova conversa para usa-lo."
elif [ "$TYPE" = "workflows" ] && [ -f "$DEST/WORKFLOW.md" ]; then
  NAME=$(grep '^name:' "$DEST/WORKFLOW.md" | head -1 | sed 's/name: *"\(.*\)"/\1/')
  echo ""
  echo "Instalado: $NAME"
  echo "Local: $DEST"
  echo ""
  echo "O workflow ja esta disponivel no G4 OS. Digite /$SLUG para usa-lo."
else
  echo ""
  echo "Aviso: Instalacao concluida mas arquivo de definicao nao encontrado."
  echo "Local: $DEST"
fi
