# Sensitivity Analysis Framework

## Purpose

Sensitivity analysis answers: "How wrong can my assumptions be before the investment thesis breaks?" It converts a single-point estimate into a range of outcomes, highlighting which assumptions matter most and where the margin of safety exists.

---

## Standard Sensitivity Tables

### Table 1: WACC vs. Terminal Growth Rate

This is the **mandatory** sensitivity table for any DCF. It captures the two assumptions with the largest impact on terminal value.

**Construction:**
- Rows: WACC — base case ± 2 percentage points, in 0.5-1.0pp increments (5 rows)
- Columns: Terminal growth rate (g) — base case ± 1-1.5pp, in 0.5pp increments (5 columns)
- Each cell = implied price per share from the DCF model with those inputs
- Highlight base case cell (bold or color)

**Example structure:**

| WACC \ g | 1.5% | 2.0% | 2.5% | 3.0% | 3.5% |
|----------|------|------|------|------|------|
| 8.0% | $XXX | $XXX | $XXX | $XXX | $XXX |
| 9.0% | $XXX | $XXX | $XXX | $XXX | $XXX |
| **10.0%** | $XXX | **$XXX** | $XXX | $XXX | $XXX |
| 11.0% | $XXX | $XXX | $XXX | $XXX | $XXX |
| 12.0% | $XXX | $XXX | $XXX | $XXX | $XXX |

**Interpretation guide:**
- If the current price falls within the table range, note which WACC/g combinations justify the price
- If the current price is below ALL cells, strong buy signal (even worst-case assumptions support upside)
- If the current price is above ALL cells, strong sell signal (even best-case doesn't justify the price)
- Count how many cells show upside vs. downside → "X of 25 scenarios show upside"

### Table 2: Revenue Growth vs. Margin

This captures operating performance uncertainty.

**Construction:**
- Rows: Revenue CAGR over projection period — base case ± 3-5pp
- Columns: Terminal EBITDA Margin (or operating margin) — base case ± 3-5pp
- Each cell = implied price per share

**Example structure:**

| Rev CAGR \ EBITDA Margin | 18% | 20% | 22% | 24% | 26% |
|--------------------------|-----|-----|-----|-----|-----|
| 5% | $XXX | $XXX | $XXX | $XXX | $XXX |
| 8% | $XXX | $XXX | $XXX | $XXX | $XXX |
| **10%** | $XXX | **$XXX** | $XXX | $XXX | $XXX |
| 12% | $XXX | $XXX | $XXX | $XXX | $XXX |
| 15% | $XXX | $XXX | $XXX | $XXX | $XXX |

### Table 3 (Optional): Industry-Specific Sensitivities

| Industry | Row Variable | Column Variable |
|----------|-------------|----------------|
| Oil & Gas | Oil price ($/bbl) | Production growth (%) |
| Banks | NIM (%) | NPL ratio (%) |
| SaaS | NRR (%) | Rev Growth (%) |
| Retail | SSS growth (%) | Gross Margin (%) |
| Utilities | Regulatory ROE (%) | RAB growth (%) |
| Pharma | Pipeline success probability (%) | Peak sales ($) |

---

## Scenario Analysis Framework

### Three-Scenario Model

Every stock pick should include three scenarios with assigned probabilities:

| Scenario | Typical Probability | Description |
|----------|-------------------|-------------|
| **Bull** | 20-30% | Everything goes right — growth accelerates, margins expand, multiple re-rates |
| **Base** | 40-60% | Consensus expectations met — current trajectory continues |
| **Bear** | 20-30% | Key risks materialize — growth slows, margins compress, multiple de-rates |

**Rules:**
- Probabilities must sum to 100%
- Bull and Bear should not be symmetric if the risk profile is skewed
- Each scenario must have specific, measurable assumptions (not vague descriptions)
- Implied price for each scenario

### Scenario Definition Template

For each scenario, specify:

```
**[Bull/Base/Bear] Scenario** — Probability: XX%

Key assumptions:
- Revenue CAGR: XX% (vs. base XX%)
- Terminal EBITDA margin: XX% (vs. base XX%)
- Exit multiple: XX.Xx (vs. base XX.Xx)
- Specific catalyst: [What triggers this scenario]

Implied valuation:
- DCF value: $XXX per share
- Multiples value: $XXX per share
- Blended: $XXX per share
- vs. Current price: +/-XX%
```

### Probability-Weighted Valuation

```
Expected Value = (P_bull × V_bull) + (P_base × V_base) + (P_bear × V_bear)

Example:
= (25% × $180) + (50% × $140) + (25% × $90)
= $45 + $70 + $22.50
= $137.50 per share
```

---

## Breakeven Analysis

Answer the critical question: "What does the market need to believe for the current price to be fair?"

### Method

1. Set the DCF output equal to the current market price
2. Solve for the implied assumptions:
   - What revenue CAGR is implied?
   - What terminal margin is implied?
   - What WACC is implied?
3. Assess reasonableness:
   - "The market is pricing in XX% revenue CAGR for the next 5 years, which compares to the industry average of YY% and the company's historical ZZ%"
   - "To justify the current price, the company needs to achieve XX% EBITDA margin by year 5, which would place it in the top quartile of peers"

### Implied Growth Rate from Multiples

Quick reverse-engineer for P/E:
```
Implied growth = (P/E - 1/Ke) × Ke
```

For EV/EBITDA:
```
Higher EV/EBITDA → market expects higher growth or lower risk
Compare implied growth to achievable growth based on TAM and competitive position
```

---

## Tornado Chart (Sensitivity Ranking)

Rank assumptions by impact on valuation. For each key assumption, calculate the implied price at -1 standard deviation and +1 standard deviation (or ±reasonable range), holding all else at base case.

| Assumption | Low Case | Base | High Case | Range ($) |
|-----------|----------|------|-----------|-----------|
| Revenue CAGR | $XXX (at 5%) | $XXX (at 10%) | $XXX (at 15%) | $XX |
| Terminal margin | $XXX (at 18%) | $XXX (at 22%) | $XXX (at 26%) | $XX |
| WACC | $XXX (at 12%) | $XXX (at 10%) | $XXX (at 8%) | $XX |
| Terminal g | $XXX (at 1.5%) | $XXX (at 2.5%) | $XXX (at 3.5%) | $XX |
| CapEx/Rev | $XXX (at 8%) | $XXX (at 5%) | $XXX (at 3%) | $XX |

Sort by Range ($) descending — the top 2-3 assumptions are what you should focus the sensitivity tables on.

---

## Margin of Safety Assessment

| Category | Criteria | Assessment |
|----------|----------|------------|
| **Strong margin of safety** | Current price < bear case value | Very attractive entry |
| **Adequate margin** | Current price < base case by >15% | Standard buy threshold |
| **Fair value** | Current price within ±10% of base case | Hold / neutral |
| **Overvalued** | Current price > base case by >15% | Avoid / sell |
| **Extremely overvalued** | Current price > bull case value | Strong sell |

### Practical Rule

"If 80%+ of your sensitivity table cells show upside, it's likely a buy. If 80%+ show downside, it's likely a sell. In between, you need conviction on specific assumptions to justify a position."

---

## Common Pitfalls

1. **Anchoring to current price** — build the model from fundamentals, THEN compare to price
2. **Symmetric sensitivities** — downside scenarios often have fatter tails than upside
3. **Ignoring correlation** — revenue growth and margin expansion don't always move independently
4. **Too-narrow ranges** — ±1pp on WACC is too tight; ±2-3pp captures real uncertainty
5. **Forgetting second-order effects** — higher growth requires higher CapEx and working capital
6. **Terminal value dominance** — if >80% of value comes from terminal, the model is really just a multiple in disguise
