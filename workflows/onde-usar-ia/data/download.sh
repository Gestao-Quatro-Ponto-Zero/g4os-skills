#!/bin/bash
# Download data files for the Onde Usar IA workflow
# Source: Anthropic Economic Index (CC-BY) + GDPVal (MIT)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Downloading data for Onde Usar IA ==="
echo ""

# AEI data from HuggingFace
echo "[1/2] Downloading O*NET task statements..."
curl -L --progress-bar -o onet_task_statements.csv \
  "https://huggingface.co/datasets/Anthropic/EconomicIndex/raw/main/release_2025_02_10/onet_task_statements.csv"

echo "[2/2] Downloading O*NET task mappings..."
curl -L --progress-bar -o onet_task_mappings.csv \
  "https://huggingface.co/datasets/Anthropic/EconomicIndex/raw/main/release_2025_02_10/onet_task_mappings.csv"

echo ""
echo "=== Download complete ==="
echo ""
echo "Files downloaded:"
ls -lh onet_task_statements.csv onet_task_mappings.csv 2>/dev/null
echo ""
echo "Note: v4_task_ai_scores_lookup.json and occupation_ai_summary.json"
echo "will be generated automatically on first workflow run."
echo ""
echo "Optional: GDPVal prompts (220 professional prompts, ~1.7MB)"
echo "  Download manually from the OpenAI evals repo if needed."
