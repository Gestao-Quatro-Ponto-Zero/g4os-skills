---
name: "RFM Analysis"
description: "Analyze customer segments with RFM scoring, K-Means clustering, and actionable marketing insights from transactional data (CSV/XLSX)"
alwaysAllow: ["Bash", "Read", "Write", "Edit"]
---

# RFM Customer Analysis & Clustering

**Scripts location**: This skill's `scripts/` directory is relative to where it was installed. Resolve the absolute path dynamically:
```bash
SKILL_DIR="$HOME/.g4os/workspaces/$(ls $HOME/.g4os/workspaces/ | head -1)/skills/rfm-analysis"
```
Always use absolute paths when running commands.

**Python**: Always use `python3`.

## Overview

This skill takes transactional data (CSV or XLSX), computes RFM (Recency, Frequency, Monetary) scores, segments customers into actionable groups, runs K-Means clustering, and presents results using **native G4 OS rendering** (jsonrender dashboards, datatables) directly in chat. **Do NOT use mermaid pie charts — they are not supported.**

## Conversation Flow

Follow this exact sequence when the user invokes the skill:

### Phase 0: Data Source Resolution

**If the user provides a file** (path or attachment) → proceed to Phase 1.

**If the user does NOT provide a file** → offer the example dataset:

> "Voce nao anexou um arquivo de dados. Quer que eu rode uma analise de demonstracao com o dataset de exemplo (10K transacoes de e-commerce)?
>
> O dataset inclui ~1.800 clientes, 7 categorias de produto, e 1 ano de transacoes — perfeito para ver o RFM em acao."

If the user accepts, use the bundled example dataset:
```bash
SKILL_DIR="$(find $HOME/.g4os/workspaces -maxdepth 1 -mindepth 1 -type d | head -1)/skills/rfm-analysis"
INPUT_FILE="$SKILL_DIR/datasets/ecommerce_sales_data.csv"
```

Use this pre-built mapping for the example dataset:
```json
{
  "customer_id": "CustomerID",
  "transaction_date": "TransactionDate",
  "revenue": "Price",
  "quantity": "Quantity",
  "discount": "Discount"
}
```

And this context:
```json
{
  "company_name": "E-commerce Demo",
  "product_type": "Multi-category e-commerce (Clothing, Electronics, Beauty, Books, Sports, Toys, Home & Kitchen)",
  "campaign_goal": "Demo run — general health check"
}
```

Skip the column mapping confirmation and business context interview in demo mode — go straight to Phase 3 (Run Analysis). After presenting results, remind the user: "Essa foi uma run de demonstracao. Para analisar seus proprios dados, rode `/rfm-analysis` novamente anexando seu arquivo CSV ou XLSX."

### Phase 1: Data Intake

1. **Ask for the file** (if not already provided):
   - "Which file should I analyze? Drop a CSV or XLSX with your transactional data."

2. **Load and inspect the file** — read the first few rows to understand the columns.

3. **Auto-detect columns** — the script auto-maps common column names. Present the mapping to the user:
   - "I detected these columns: CustomerID → customer_id, TransactionDate → transaction_date, Price → revenue. Does this look right?"
   - If detection fails, ask the user to specify: customer ID column, transaction date column, and revenue/amount column.

4. **Confirm column mapping** before proceeding.

### Phase 2: Business Context Interview

Before running the analysis, ask these questions to generate better insights. Ask them naturally, not as a checklist dump. One or two per message.

**Required:**
- What product or service does this data represent? (e-commerce, SaaS, marketplace, etc.)
- What's the goal of this analysis? (retention campaign, reactivation, upsell, general health check)

**Optional (ask if relevant):**
- Are there any active promotions or campaigns running?
- Is there a specific customer segment you're most concerned about?
- What's the typical purchase cycle? (weekly, monthly, quarterly)
- Company name (for the report header)

Store the answers in a context JSON:
```json
{
  "company_name": "...",
  "product_type": "...",
  "campaign_goal": "...",
  "purchase_cycle": "...",
  "custom_insights": "..."
}
```

### Phase 3: Run Analysis

Resolve the script path dynamically:

```bash
SKILL_DIR="$(find $HOME/.g4os/workspaces -maxdepth 1 -mindepth 1 -type d | head -1)/skills/rfm-analysis"

python3 "$SKILL_DIR/scripts/rfm_analysis.py" \
  "<input_file>" \
  "<output_dir>" \
  --mapping-json '<mapping_json>' \
  --context-json '<context_json>'
```

**Output directory**: Create inside the same folder as the input file, named `rfm-output/`. For demo mode, use `/tmp/rfm-demo-output/`.

The script outputs to stdout a JSON summary with segment and cluster data. Read this to present insights.

### Phase 4: Present Results (Native Rendering)

After the script runs, present ALL results directly in chat using G4 OS native components. **Do NOT use html-preview.** Read the script's stdout JSON and the output files to build the rendering.

#### Step 1: KPI Dashboard (jsonrender)

Build a `jsonrender` Card with a Grid of Metrics showing the headline numbers:
- Total Customers
- Total Revenue (formatted as currency)
- Avg Frequency
- Avg Recency (days)
- Avg Customer Value (currency)

Add an Alert if any concerning pattern exists (e.g., >20% At Risk + Can't Lose Them).

Example structure:
```
Card "RFM Analysis — {company_name}"
  └─ Grid (columns: 3-5)
       ├─ Metric "Customers" value="9,000"
       ├─ Metric "Revenue" value="R$ 106.7M"
       ├─ Metric "Avg Frequency" value="11.1"
       ├─ Metric "Avg Recency" value="33 days"
       └─ Metric "Avg CLV" value="R$ 11,851"
  └─ Alert (warning) if At Risk + Can't Lose > 20%
```

#### Step 2: Segment Distribution (datatable)

Use `datatable` with typed columns to show all segments:

Columns:
- `segment` (text) — Segment name
- `customers` (number) — Count
- `pct_customers` (percent) — % of total
- `total_revenue` (currency) — Revenue
- `pct_revenue` (percent) — % of revenue
- `avg_recency` (number) — Avg recency days
- `avg_frequency` (number) — Avg frequency
- `avg_monetary` (currency) — Avg monetary value

Sort by revenue descending. Title: "RFM Segments"

#### Step 3: Segment Health (jsonrender)

Build a second `jsonrender` block showing segment health as Progress bars inside a Card:

```
Card "Segment Health"
  └─ Stack (vertical)
       ├─ Progress "Champions" value=14.7 color="green"
       ├─ Progress "Potential Loyalists" value=22.3 color="blue"
       ├─ Progress "Loyal Customers" value=12.1 color="green"
       ├─ Progress "At Risk" value=12.8 color="red"
       ├─ Progress "Can't Lose Them" value=8.9 color="red"
       └─ ...etc for all segments with >3%
```

Use color mapping: Champions/Loyal = green, Potential/Promising/Recent = blue, At Risk/Can't Lose = red, Hibernating/Lost = yellow.

#### Step 4: Cluster Profiles (datatable)

Use `datatable` for K-Means cluster profiles:

Columns: cluster (text), customers (number), avg_recency (number), avg_frequency (number), avg_monetary (currency), total_revenue (currency), top_segment (text)

Title: "K-Means Cluster Profiles"

#### Step 5: Revenue Concentration (jsonrender)

Build a `jsonrender` Card with stacked Progress bars showing each segment's revenue share (% of total). This replaces a pie chart with a more readable breakdown:

```
Card "Revenue Concentration"
  └─ Stack (vertical)
       ├─ Progress "Potential Loyalists — 21.1%" value=21 color="blue"
       ├─ Progress "Champions — 20.5%" value=21 color="green"
       ├─ Progress "Loyal Customers — 15.1%" value=15 color="green"
       ├─ Progress "At Risk — 12.1%" value=12 color="red"
       ├─ Progress "Can't Lose Them — 11.9%" value=12 color="red"
       └─ Progress "Others — 19.3%" value=19 color="yellow"
```

Sort segments by revenue share descending. Use same color mapping as Step 3.

#### Step 6: Recommended Actions (jsonrender)

Build a Tabs component with one tab per priority tier:

```
Tabs
  ├─ TabPanel "Protect" → Checklist with actions for Champions + Loyal + Can't Lose
  ├─ TabPanel "Grow" → Checklist with actions for Potential Loyalists + Promising + Recent
  └─ TabPanel "Reactivate" → Checklist with actions for At Risk + Hibernating + Lost
```

Customize checklist items using the business context (product type, campaign goal).

#### Step 7: Actionable Insights (markdown)

Write 3-5 bullet points of **specific, data-backed insights** using the business context:
- Revenue concentration risk/opportunity
- Biggest reactivation opportunity with estimated value
- Segment migration recommendations
- Campaign targeting suggestions

#### Step 8: File Cards

Show file cards for exported data:
- `rfm_segments.csv` — Full customer-level data
- `cluster_profiles.json` — Cluster centroids

### Phase 5: Deep Dive (Optional)

If the user wants to explore further, offer:

- **Segment drill-down**: Filter `rfm_segments.csv` for a specific segment and show customer details
- **Campaign list export**: Generate a targeted list (e.g., "all At Risk customers with >$500 lifetime value")
- **Cohort analysis**: If date range is sufficient, show monthly cohort retention
- **Custom clustering**: Re-run with different K or add demographic features
- **Cross-segment category analysis**: Which products do Champions buy vs At Risk?

## Script Reference

### `rfm_analysis.py`

**Arguments:**
| Arg | Required | Description |
|-----|----------|-------------|
| `input_file` | Yes | Path to CSV or XLSX |
| `output_dir` | Yes | Directory for output files |
| `--config` | No | JSON config file with mapping + context |
| `--n-clusters` | No | Number of K-Means clusters (0 = auto-detect) |
| `--mapping-json` | No | Column mapping as JSON string |
| `--context-json` | No | Business context as JSON string |

**Column mapping JSON format:**
```json
{
  "customer_id": "CustomerID",
  "transaction_date": "TransactionDate",
  "revenue": "Price",
  "quantity": "Quantity",
  "discount": "Discount"
}
```

Only `customer_id` and `transaction_date` are required. If `revenue` maps to a unit price column, the script auto-multiplies by quantity and applies discount.

**Output files:**
| File | Description |
|------|-------------|
| `rfm_segments.csv` | Customer-level: ID, recency, frequency, monetary, R/F/M scores, segment, cluster |
| `cluster_profiles.json` | Cluster centroids and dominant segments |
| `segment_summary.json` | Segment-level aggregates — **primary data source for in-chat rendering** |

Note: The script also generates `rfm_report.html` as a standalone backup, but primary presentation is via native G4 OS rendering in chat (jsonrender, datatable).

## Example Datasets

| Dataset | Rows | Customers | Description | Path |
|---------|------|-----------|-------------|------|
| E-commerce Sales (sample) | 10,000 | ~1,800 | Multi-category e-commerce (Clothing, Electronics, Beauty, Books, Sports, Toys, Home & Kitchen). 1 year of transactions (Sep 2023 – Sep 2024). Source: [Kaggle](https://www.kaggle.com/datasets/thedevastator/unlock-profits-with-e-commerce-sales-data). Run `datasets/download_full.sh` for the full 100K dataset. | `datasets/ecommerce_sales_data.csv` |

## RFM Segments Reference

| Segment | R Score | FM Score | Description |
|---------|---------|----------|-------------|
| Champions | 4-5 | 4-5 | Best customers. Recent, frequent, high spend |
| Loyal Customers | 3-5 | 3-5 | Consistent buyers with good monetary value |
| Potential Loyalists | 3-5 | 2-4 | Recent customers with growth potential |
| Recent Customers | 5 | 1 | Just bought, first or second purchase |
| Promising | 3-4 | 1-2 | Recent but low engagement — nurture |
| Needing Attention | 3 | 1 | Above average but slipping away |
| Can't Lose Them | 1-2 | 4-5 | Were great customers, now going away — urgent |
| At Risk | 1-2 | 2-4 | Spent well before, haven't returned |
| About to Sleep | 1-2 | 1-3 | Below average, fading out |
| Hibernating | 1 | 2 | Long gone, minimal engagement |
| Lost | 1 | 1 | Lowest on all dimensions |

## Dependencies

Python packages (all standard in miniconda):
- `pandas` — Data manipulation
- `numpy` — Numerical operations
- `scikit-learn` — K-Means clustering
- `plotly` — Interactive charts (for HTML backup report)
- `openpyxl` — XLSX reading

## Quality Checklist

Before presenting results:
- [ ] Column mapping confirmed by user (skip for demo mode)
- [ ] No ERROR messages in script output
- [ ] segment_summary.json and cluster_profiles.json exist and are valid
- [ ] Segment distribution looks reasonable (no single segment > 60%)
- [ ] Business context incorporated into recommendations
- [ ] All 8 rendering steps completed (KPIs → datatable → health → clusters → revenue bars → actions → insights → files)
