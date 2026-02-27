#!/bin/bash
# G4 OS Skills Installer
# Usage: curl -sL https://raw.githubusercontent.com/Gestao-Quatro-Ponto-Zero/g4os-skills/main/install.sh | bash -s -- <type>/<slug>
#
# Examples:
#   curl -sL .../install.sh | bash -s -- skills/humanize
#   curl -sL .../install.sh | bash -s -- workflows/onde-usar-ia

set -euo pipefail

REPO="Gestao-Quatro-Ponto-Zero/g4os-skills"
BRANCH="main"
TARGET_PATH="${1:-}"

if [ -z "$TARGET_PATH" ]; then
  echo "Usage: $0 <type>/<slug>"
  echo ""
  echo "Available:"
  echo "  skills/humanize          - Rewrite content to sound naturally human"
  echo "  skills/video-combiner    - Combine Hook+Body+CTA video segments"
  echo "  workflows/onde-usar-ia   - AI implementation diagnostic (PT-BR)"
  echo ""
  echo "Example:"
  echo "  curl -sL https://raw.githubusercontent.com/$REPO/$BRANCH/install.sh | bash -s -- skills/humanize"
  exit 1
fi

# Parse type and slug
TYPE=$(echo "$TARGET_PATH" | cut -d'/' -f1)
SLUG=$(echo "$TARGET_PATH" | cut -d'/' -f2)

if [ "$TYPE" != "skills" ] && [ "$TYPE" != "workflows" ]; then
  echo "Error: Type must be 'skills' or 'workflows', got '$TYPE'"
  exit 1
fi

# Find G4 OS workspace
G4OS_DIR="$HOME/.g4os/workspaces"
if [ ! -d "$G4OS_DIR" ]; then
  echo "Error: G4 OS workspace directory not found at $G4OS_DIR"
  echo "Make sure G4 OS is installed first."
  exit 1
fi

# Find the active workspace (first directory)
WORKSPACE=$(ls -1 "$G4OS_DIR" | head -n1)
if [ -z "$WORKSPACE" ]; then
  echo "Error: No G4 OS workspace found"
  exit 1
fi

DEST="$G4OS_DIR/$WORKSPACE/$TYPE/$SLUG"

# Check if already installed
if [ -d "$DEST" ]; then
  echo "Warning: $TYPE/$SLUG already exists at $DEST"
  read -p "Overwrite? [y/N] " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
  fi
  rm -rf "$DEST"
fi

echo "Installing $TYPE/$SLUG to $DEST..."

# Create temp directory
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

# Download using git sparse checkout (or fallback to tarball)
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
    echo "Error: $TARGET_PATH not found in repository"
    exit 1
  fi
else
  # Fallback: download tarball and extract
  curl -sL "https://github.com/$REPO/archive/$BRANCH.tar.gz" -o "$TMPDIR/repo.tar.gz"
  tar -xzf "$TMPDIR/repo.tar.gz" -C "$TMPDIR"

  EXTRACTED="$TMPDIR/g4os-skills-$BRANCH/$TARGET_PATH"
  if [ -d "$EXTRACTED" ]; then
    mkdir -p "$(dirname "$DEST")"
    cp -r "$EXTRACTED" "$DEST"
  else
    echo "Error: $TARGET_PATH not found in repository"
    exit 1
  fi
fi

# Verify installation
if [ "$TYPE" = "skills" ] && [ -f "$DEST/SKILL.md" ]; then
  NAME=$(grep '^name:' "$DEST/SKILL.md" | head -1 | sed 's/name: *"\(.*\)"/\1/')
  echo ""
  echo "Installed: $NAME"
  echo "Location: $DEST"
  echo ""
  echo "The skill is now available in G4 OS. Start a new conversation to use it."
elif [ "$TYPE" = "workflows" ] && [ -f "$DEST/WORKFLOW.md" ]; then
  NAME=$(grep '^name:' "$DEST/WORKFLOW.md" | head -1 | sed 's/name: *"\(.*\)"/\1/')
  echo ""
  echo "Installed: $NAME"
  echo "Location: $DEST"
  echo ""
  echo "The workflow is now available in G4 OS. Type /$SLUG to use it."
else
  echo ""
  echo "Warning: Installation completed but definition file not found."
  echo "Location: $DEST"
fi
