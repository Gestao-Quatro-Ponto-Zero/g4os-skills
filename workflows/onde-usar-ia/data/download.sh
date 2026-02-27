#!/bin/bash
# Baixar arquivos de dados para o workflow Onde Usar IA
# Fonte: Anthropic Economic Index (CC-BY) + GDPVal (MIT)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Baixando dados para Onde Usar IA ==="
echo ""

# Dados AEI do HuggingFace
echo "[1/2] Baixando O*NET task statements..."
curl -L --progress-bar -o onet_task_statements.csv \
  "https://huggingface.co/datasets/Anthropic/EconomicIndex/raw/main/release_2025_02_10/onet_task_statements.csv"

echo "[2/2] Baixando O*NET task mappings..."
curl -L --progress-bar -o onet_task_mappings.csv \
  "https://huggingface.co/datasets/Anthropic/EconomicIndex/raw/main/release_2025_02_10/onet_task_mappings.csv"

echo ""
echo "=== Download concluido ==="
echo ""
echo "Arquivos baixados:"
ls -lh onet_task_statements.csv onet_task_mappings.csv 2>/dev/null
echo ""
echo "Nota: v4_task_ai_scores_lookup.json e occupation_ai_summary.json"
echo "serao gerados automaticamente na primeira execucao do workflow."
echo ""
echo "Opcional: GDPVal prompts (220 prompts profissionais, ~1.7MB)"
echo "  Baixe manualmente do repo OpenAI evals se necessario."
