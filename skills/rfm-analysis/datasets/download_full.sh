#!/bin/bash
# Download the full 100K-row e-commerce dataset from Kaggle
# The repo includes a 10K-row sample. This script downloads the complete version.
#
# Requires: kaggle CLI (pip install kaggle) + API credentials
# Or: download manually from https://www.kaggle.com/datasets/thedevastator/unlock-profits-with-e-commerce-sales-data

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT="$SCRIPT_DIR/ecommerce_sales_data_full.csv"

echo "Downloading full e-commerce dataset (100K rows)..."

if command -v kaggle &> /dev/null; then
  TMPDIR=$(mktemp -d)
  trap "rm -rf $TMPDIR" EXIT
  kaggle datasets download -d thedevastator/unlock-profits-with-e-commerce-sales-data -p "$TMPDIR" --unzip
  mv "$TMPDIR"/*.csv "$OUTPUT"
  echo "Downloaded: $OUTPUT ($(wc -l < "$OUTPUT") rows)"
else
  echo "Kaggle CLI not found. Install with: pip install kaggle"
  echo "Or download manually from:"
  echo "  https://www.kaggle.com/datasets/thedevastator/unlock-profits-with-e-commerce-sales-data"
  echo ""
  echo "Save the CSV as: $OUTPUT"
  exit 1
fi
