---
name: "Conciliação Financeira"
description: "Conciliação automática de extratos bancários com gateways de pagamento, ERPs ou outras fontes financeiras. Use quando o usuário pedir 'conciliar extratos', 'reconciliação bancária', 'cruzar extrato com gateway', 'conferir recebimentos', 'conciliação financeira', ou '/conciliacao'. Aceita PDF, CSV, XLSX, XML e TXT como inputs."
alwaysAllow: ["Bash", "Read", "Write", "Edit"]
globs: ["*.ofx", "*.qfx"]
---

# Conciliação Financeira

Reconcilia transações entre duas ou mais fontes financeiras (gateway vs banco, ERP vs banco, etc.) usando processamento em Python para volume e precisão.

## Architecture Rule

**Python for data, LLM for judgment.** All normalization, matching, and computation runs in `scripts/reconcile.py`. The LLM orchestrates, extracts data from PDFs, and interprets results — never loops over transactions in-context.

## Known Parsers

Read [references/parsers.md](references/parsers.md) for known format signatures, field mappings, and the canonical schema. Always check it before parsing — a known format saves a round-trip with the user.

## Execution Flow

### Step 1 — Receive & Classify Files

For each file the user provides:

1. **Detect format**: CSV, XLSX, XML, PDF, TXT, OFX
2. **Check known parsers** in `references/parsers.md` — match by header signature or content patterns
3. **If unknown format**: show a 5-row sample to the user and ask:
   - "Qual coluna é a data? Valor? Descrição? ID (se tiver)?"
   - Store the answer for this session

4. **Ask which side each file belongs to** (or infer if obvious):
   - **Lado A (referência)**: gateway, ERP, sistema de cobrança — what *should* have arrived
   - **Lado B (banco)**: bank statement — what *actually* arrived
   - If both sides are obvious (e.g., Stripe CSV + Itaú PDF), skip asking

### Step 2 — Extract & Normalize

For each file, produce a canonical CSV at `/tmp/conciliacao_{side}_{filename}.csv` with columns: `date,amount,description,reference_id,source_file,raw_line`

**By format:**

| Format | Method |
|--------|--------|
| CSV/TSV | `pandas.read_csv()` → map columns per parser spec |
| XLSX | `pandas.read_excel()` → detect header row → map columns |
| XML (NFe/OFX) | Python `xml.etree` or `ofxparse` → extract transactions |
| PDF | Preferred: `call_llm(prompt, attachments=[path])` → get JSON → write CSV. Fallback: if `call_llm` unavailable (no API key), use a `Task` subagent with `subagent_type="general-purpose"` to read the PDF and extract transactions, or extract inline if PDF content is already in conversation context |
| TXT (positional) | Detect layout → Python fixed-width parse or `call_llm`/`Task` subagent |

**PDF extraction prompt** (adapt per bank — see parsers.md for bank-specific prompts):

```
Extract ALL transaction rows from this bank statement PDF as a JSON array.
Each row: {"date": "YYYY-MM-DD", "description": "exact text", "amount": number}
Rules:
- Skip balance/summary rows (SALDO ANTERIOR, SALDO TOTAL DISPONÍVEL)
- Amount should be positive for credits (money in)
- Date format in source is DD/MM/YYYY — convert to YYYY-MM-DD
- Include ALL rows even small ones
Return ONLY the JSON array, no markdown fences.
```

**If multiple files for the same side**: concatenate into one canonical CSV.

### Step 3 — Configure & Run Match Engine

Create a config JSON at `/tmp/conciliacao_config.json`:

```json
{
  "side_a_file": "/tmp/conciliacao_A_xxx.csv",
  "side_b_file": "/tmp/conciliacao_B_xxx.csv",
  "days_tolerance": 3,
  "amount_tolerance_pct": 0.01,
  "amount_tolerance_abs": 0.50
}
```

Run the reconciliation engine:

```bash
python ~/.g4os/workspaces/my-workspace/skills/conciliacao/scripts/reconcile.py /tmp/conciliacao_config.json -o /tmp/conciliacao_result.json
```

### Step 4 — Present Results

Read the result JSON and present three distinct sections:

#### 4a. Summary (jsonrender or markdown)

Show key metrics: total transactions each side, matched count, divergence count, unmatched count, total amounts, difference.

#### 4b. Conciliados (datatable)

All exact matches. Columns: Data, Valor, Descrição Lado A, Descrição Lado B, Ref ID.

Only show if user wants detail — for large volumes (>50), say "X transações conciliadas com match exato" and offer to show.

#### 4c. Divergências (datatable)

Matches found but with differences. Columns: Data A, Data B, Valor A, Valor B, Delta R$, Delta Dias, Pass (date_flex/amount_flex/fuzzy), Descrição A, Descrição B.

**Always show these** — they're the actionable items.

#### 4d. Dúvidas — Itens sem Match (datatable)

Two separate tables: orphans lado A (expected but not received?) and orphans lado B (received but not expected?).

**Always show these.** Flag clearly: "Estes itens precisam de verificação manual."

#### 4e. Batch Matches (if any)

Show groupings: "N transações do lado A (total R$X) correspondem a 1 lançamento do lado B (R$X)."

### Step 5 — Offer Next Actions

After presenting results, ask:

1. **Salvar relatório?** — Save as `.md` or `.xlsx` at a user-specified path
2. **Ajustar tolerâncias?** — Re-run with different day/amount thresholds if too many divergences or dúvidas
3. **Investigar dúvidas?** — Deep-dive into specific unmatched items

## Script Adaptation

The `scripts/reconcile.py` engine covers the standard multi-pass matching flow. However, specific use cases may require adaptations:

**When to adapt the script:**
- New match criteria (e.g., match by reference_id substring instead of date+amount)
- Custom filtering (e.g., exclude transactions below R$1, only match category X)
- Different tolerance logic (e.g., business-days-only calculation instead of calendar days)
- Output format changes (e.g., add columns, different grouping)

**How to adapt:**
1. Read the current `scripts/reconcile.py` to understand the structure
2. Create a **modified copy** at `/tmp/reconcile_custom.py` (never edit the original in-place)
3. Apply the needed changes
4. Run the modified script instead
5. If the adaptation is valuable for reuse, ask the user if they want to save it (see Sub-routines below)

**Never silently modify the base script.** Always explain what you're changing and why.

## Sub-routines

After completing a reconciliation, evaluate if a reusable sub-routine makes sense. This is relevant when:

- The user reconciles the **same pair of sources** repeatedly (e.g., "Stripe vs Itaú todo mês")
- A **custom parser** was created for a new format during the session
- **Custom tolerances or filters** were applied that are specific to a context

**When to suggest:**

Ask the user: *"Essa conciliação [Stripe vs Itaú / formato X] parece recorrente. Quer que eu crie uma sub-rotina `/conciliacao-stripe-itau` pra simplificar nas próximas vezes?"*

**What a sub-routine contains:**

A sub-routine is a **thin wrapper skill** that pre-configures the conciliação for a specific use case:

```yaml
---
name: "Conciliação Stripe → Itaú"
description: "Conciliação mensal dos payouts Stripe com extrato Itaú. Use com '/conciliacao-stripe-itau'."
---
```

The sub-routine SKILL.md:
1. Pre-sets which side is A (Stripe) and B (Itaú)
2. Includes the specific parser mappings (no need to detect)
3. Sets default tolerances tuned for this pair
4. References the base `conciliacao` skill's engine and scripts
5. May include a custom script variant if needed

**How to create:**
1. Confirm with the user (name, slug, what it pre-configures)
2. Create as a new skill at `skills/{slug}/SKILL.md`
3. Keep it thin — reference the base conciliação engine, don't duplicate

**Do NOT create sub-routines proactively.** Only suggest when the pattern is clear and the user confirms.

## Edge Cases

- **Duplicate amounts on same date**: If two transactions have identical date+amount, the engine matches them first-come-first-served. If this causes wrong pairings, suggest the user add a filter (e.g., by description keyword) to disambiguate.
- **Multi-currency**: Not supported yet. All amounts must be in the same currency. Flag if mixed currencies detected.
- **Partial months**: Bank statement may not cover the full period of the gateway file (or vice versa). Flag date range mismatch at the start.
- **Very large files (>1000 txns)**: The batch matching (subset-sum) pass becomes expensive. Skip it and log a warning if side A has >200 unmatched items after pass 4.
- **PDF extraction errors**: If `call_llm` returns malformed JSON, retry once with a stricter prompt. If still failing, ask the user to provide the data in CSV/XLSX instead.
