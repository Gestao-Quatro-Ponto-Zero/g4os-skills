# Known Parsers & Canonical Schema

## Canonical Schema

Every transaction, regardless of source, must be normalized to:

```python
{
    "date": "YYYY-MM-DD",        # Transaction effective date (arrival date for payouts)
    "amount": 123.45,            # Positive = credit, negative = debit
    "description": "string",     # Raw description from source
    "reference_id": "string",    # Unique ID if available (payout ID, txn ID), else None
    "source_file": "filename",   # Which file this came from
    "raw_line": 0,               # Original line/row number for audit trail
    "side": "A" | "B",           # A = reference (gateway/ERP), B = bank
    "category": "string"         # Optional: auto-classified category
}
```

## Known Formats

### Stripe Payouts CSV

**Detection**: CSV with header containing `id,Amount,Created (UTC),Currency,Arrival Date (UTC)`

**Field mapping**:
| Source field | Canonical field |
|-------------|----------------|
| `Arrival Date (UTC)` | `date` (use arrival, not created — this is when money hits bank) |
| `Amount` | `amount` |
| `Type` + `Destination Name` | `description` |
| `id` | `reference_id` |

**Notes**:
- Amount is already net (after Stripe fees)
- Arrival date is the bank-matching date, not Created date
- Currency field confirms BRL
- Status should be `paid` — skip `in_transit` or `failed`

### Itaú Extrato PDF

**Detection**: PDF containing "JOAO VITOR CHAVES SILVA" or "extrato conta corrente" or "ITAÚ" + "lançamentos"

**Extraction**: Requires LLM (call_llm) to extract table from PDF. Prompt template:

```
Extract ALL transaction rows from this bank statement PDF as a JSON array.
Each row: {"date": "YYYY-MM-DD", "description": "exact text", "amount": number}
Rules:
- Skip rows that say "SALDO ANTERIOR", "SALDO TOTAL DISPONÍVEL DIA"
- Amount is always positive in the source — determine credit/debit from context
- For "STRIPE" entries: these are credits (incoming)
- Date format in source is DD/MM/YYYY — convert to YYYY-MM-DD
- Include ALL rows, even small ones (rendimentos, taxas)
Return ONLY the JSON array, no markdown.
```

**Post-extraction field mapping**:
| Extracted field | Canonical field |
|----------------|----------------|
| `date` | `date` |
| `amount` | `amount` |
| `description` | `description` |
| (none) | `reference_id` = None |

**Notes**:
- Itaú PDFs mix credits and debits in same column — need sign inference
- "STRIPE VISA/MAST CDCD0rR7iy5q" = Stripe payouts
- "SISPAG" = salary/transfers from companies
- "PIX TRANSF" = PIX transfers
- "REND PAGO APLIC AUT MAIS" = automatic investment returns (tiny amounts)
- "COR DIVIDENDOS/RENDIMENTO" = stock dividends
- "TED" = wire transfers

### Nubank Extrato CSV

**Detection**: CSV with headers like `Data,Valor,Identificador,Descrição` or `date,amount,id,description`

**Field mapping**:
| Source field | Canonical field |
|-------------|----------------|
| `Data` / `date` | `date` |
| `Valor` / `amount` | `amount` |
| `Descrição` / `description` | `description` |
| `Identificador` / `id` | `reference_id` |

### OFX/QFX (Open Financial Exchange)

**Detection**: File starts with `OFXHEADER` or `<?OFX` or contains `<OFX>`

**Parsing**: Use `ofxparse` library or regex extraction of `<STMTTRN>` blocks.

**Field mapping**:
| OFX tag | Canonical field |
|---------|----------------|
| `<DTPOSTED>` | `date` (format: YYYYMMDD) |
| `<TRNAMT>` | `amount` |
| `<MEMO>` or `<NAME>` | `description` |
| `<FITID>` | `reference_id` |

### XML NFe (Nota Fiscal Eletrônica)

**Detection**: XML containing `<nfeProc>` or `<NFe>` namespace

**Field mapping**:
| XPath | Canonical field |
|-------|----------------|
| `//ide/dhEmi` | `date` |
| `//ICMSTot/vNF` | `amount` |
| `//emit/xNome` | `description` |
| `//ide/nNF` | `reference_id` (nota number) |

### Generic CSV (unknown)

When no known format is detected:
1. Read first 5 rows
2. Show to user with column indices
3. Ask: "Which column is date? amount? description? ID (if any)?"
4. Store mapping for reuse

### Generic XLSX (unknown)

Same as generic CSV but:
1. List sheet names
2. Ask which sheet to use (or process all)
3. Detect header row (may not be row 1)
4. Same column mapping flow

## Adding New Parsers

When a new format is encountered and successfully mapped, the user may want to save it as a reusable sub-routine. See SKILL.md section on sub-routine creation.
