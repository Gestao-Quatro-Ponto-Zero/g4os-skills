# Valuation Models Reference

## Model Selection Guide

| Company Profile | Primary Model | Secondary Model | Notes |
|----------------|---------------|-----------------|-------|
| Stable FCF, mature | DCF (FCFF) | Multiples (EV/EBITDA) | Most reliable — visible cash flows |
| Dividend payer, stable | DDM / Gordon Growth | DCF (FCFF) | Use multi-stage DDM if growth phases differ |
| High-growth, profitable | DCF (FCFF) | EV/Revenue multiples | Weight terminal value carefully |
| High-growth, pre-profit | EV/Revenue multiples | DCF with long projection period | DCF highly sensitive to assumptions |
| Cyclical | Normalized multiples | DCF with mid-cycle margins | Avoid peak/trough as base case |
| Financial services | Excess Return / DDM | P/Book regression vs. ROE | EV-based models don't work for banks |
| REITs / Infrastructure | DDM / P/FFO | NAV-based | Use FFO not earnings |
| Holding / Conglomerate | Sum-of-the-Parts (SOTP) | NAV discount analysis | Value each segment separately |

---

## 1. DCF — Discounted Cash Flow (FCFF)

### Formula

```
Enterprise Value = Σ [FCFFt / (1 + WACC)^t] + [Terminal Value / (1 + WACC)^n]

Equity Value = Enterprise Value - Net Debt - Minority Interest + Associates

Price per Share = Equity Value / Diluted Shares Outstanding
```

### Free Cash Flow to Firm (FCFF)

```
FCFF = EBIT × (1 - Tax Rate)
     + Depreciation & Amortization
     - Capital Expenditures
     - Change in Net Working Capital
```

Alternative from EBITDA:
```
FCFF = EBITDA × (1 - Tax Rate)
     + D&A × Tax Rate        (tax shield on D&A)
     - Capital Expenditures
     - Change in Net Working Capital
```

### Terminal Value Methods

**Method 1: Gordon Growth (Perpetuity Growth)**
```
Terminal Value = FCFFn × (1 + g) / (WACC - g)
```
- g = terminal growth rate (typically 2-3% for developed markets, 3-5% for emerging)
- g should NEVER exceed long-term nominal GDP growth
- Sanity check: TV should be 50-75% of total EV. If >80%, the model is too dependent on terminal assumptions

**Method 2: Exit Multiple**
```
Terminal Value = EBITDAn × Exit Multiple
```
- Exit multiple = peer median EV/EBITDA or historical average
- More market-grounded but introduces circular logic with multiples

**Best practice:** Run both methods and compare. If they diverge >20%, investigate why.

### WACC Calculation

```
WACC = (E/V) × Ke + (D/V) × Kd × (1 - Tax Rate)
```

**Cost of Equity (CAPM):**
```
Ke = Rf + β × ERP + CRP (if applicable)
```

| Component | Source | Typical Range |
|-----------|--------|--------------|
| Risk-free rate (Rf) | 10Y Treasury (US) or NTN-B (Brazil) | 4-5% (US), 6-7% (BR real) |
| Equity risk premium (ERP) | Damodaran annual update | 4.5-6.0% (US), 7-9% (BR) |
| Beta (β) | Regression vs. market index, or unlevered peer average re-levered | 0.8-1.5 typical |
| Country risk premium (CRP) | CDS spread or EMBI+ | 2-4% for Brazil |

**Beta guidance:**
- Use 2-year weekly returns vs. broad market index as default
- If company-specific beta is unreliable (low R², recent IPO), use unlevered peer median:
  ```
  β_unlevered = β_levered / [1 + (1 - Tax) × (D/E)]
  β_relevered = β_unlevered × [1 + (1 - Tax) × (Target D/E)]
  ```

**Cost of Debt:**
```
Kd = Risk-free rate + Credit spread (based on rating or synthetic rating)
Kd after-tax = Kd × (1 - Tax Rate)
```

### Projection Best Practices

- **Revenue:** Project from drivers (volume × price, segment growth, TAM penetration) — not just % growth
- **Margins:** Model convergence to peer median or management targets over projection period
- **CapEx:** Distinguish maintenance CapEx (sustain operations) from growth CapEx (expand capacity)
- **Working capital:** Use historical days metrics (DSO, DIO, DPO) applied to projected revenue/COGS
- **Fade to maturity:** Growth rates and margins should converge to sustainable levels by terminal year

---

## 2. DDM — Dividend Discount Model

### Single-Stage (Gordon Growth)

```
P = D1 / (Ke - g)

Where:
D1 = Expected dividend next year = D0 × (1 + g)
Ke = Cost of equity
g  = Sustainable dividend growth rate
```

**Sustainable growth rate:**
```
g = ROE × (1 - Payout Ratio)
```

### Multi-Stage DDM

**Two-stage:**
```
P = Σ [Dt / (1 + Ke)^t]  for t = 1 to n    (high-growth phase)
  + [Dn+1 / (Ke - g_stable)] / (1 + Ke)^n   (stable phase)
```

**Three-stage** (high growth → transition → stable):
- Phase 1 (years 1-5): High growth rate g1
- Phase 2 (years 6-10): Linear decline from g1 to g_stable
- Phase 3 (year 11+): Stable growth g_stable in perpetuity

### When to Use DDM

| Condition | Use DDM? |
|-----------|----------|
| Regular, predictable dividends | Yes — primary model |
| High payout ratio (>50%) | Yes — DDM captures value return |
| Low/no dividends, high growth | No — use DCF (FCFF/FCFE) |
| Erratic dividend history | No — use DCF |
| Financial services (banks, insurance) | Yes — DDM or excess return preferred over DCF |

### DDM Sanity Checks

- Implied payout ratio in terminal year should be 40-70% for most mature companies
- g_stable should not exceed nominal GDP growth (2-3% developed, 4-6% emerging)
- If DDM value >> DCF value, the dividend growth rate assumption is likely too aggressive

---

## 3. Multiples-Based Valuation

### Enterprise Value Multiples

| Multiple | Formula | Best For |
|----------|---------|----------|
| EV/Revenue | EV / LTM Revenue | High-growth, unprofitable companies |
| EV/EBITDA | EV / LTM EBITDA | Most universal — operating profitability |
| EV/EBIT | EV / LTM EBIT | Capital-intensive companies (captures D&A impact) |
| EV/FCF | EV / LTM Free Cash Flow | Cash generative businesses |

### Equity Multiples

| Multiple | Formula | Best For |
|----------|---------|----------|
| P/E | Price / EPS | Profitable companies, quick screen |
| P/FCF | Price / FCF per share | Cash-focused investors |
| P/Book | Price / Book Value per share | Banks, insurance, REITs |
| PEG | P/E / EPS Growth Rate | Growth-adjusted comparison |

### Application Method

1. **Select peer group** (4-6 companies, truly comparable)
2. **Calculate multiples** for each peer using consistent metrics (LTM or NTM)
3. **Compute statistics** (median preferred over mean — less sensitive to outliers)
4. **Apply peer median multiple** to target's metric:
   ```
   Implied EV = Peer Median EV/EBITDA × Target EBITDA
   Implied Equity = Implied EV - Net Debt
   Implied Price = Implied Equity / Shares Outstanding
   ```
5. **Cross-reference** with other multiples for consistency

### Premium/Discount Justification

A company should trade at a premium to peers if:
- Higher growth rate
- Better margins / profitability
- Stronger competitive moat
- Better balance sheet
- Superior management track record
- Higher dividend yield / buyback yield

A company may trade at a discount due to:
- Governance concerns
- Concentration risk (customer, geography, product)
- Cyclical exposure
- Regulatory overhang
- Execution risk

### NTM vs. LTM

| Metric | When to Use |
|--------|-------------|
| LTM (Last Twelve Months) | Default — actual results, no estimate risk |
| NTM (Next Twelve Months) | Growth companies where forward estimates differ materially from trailing |
| Consensus NTM | When available — use with `[E]` flag and cite source |

---

## 4. Sum-of-the-Parts (SOTP)

For diversified companies with distinct business segments:

```
Total EV = Σ (Segment EV)
         = Σ (Segment Metric × Appropriate Multiple)

Equity Value = Total EV - Net Debt (consolidated) - Minority Interest + Associates
```

| Segment | Metric | Multiple | Implied EV |
|---------|--------|----------|-----------|
| Segment A | EBITDA $X.XB | XX.Xx (peer set A) | $X.XB |
| Segment B | Revenue $X.XB | XX.Xx (peer set B) | $X.XB |
| Segment C | EBITDA $X.XB | XX.Xx (peer set C) | $X.XB |
| **Total EV** | | | **$X.XB** |
| (-) Net Debt | | | ($X.XB) |
| **Equity Value** | | | **$X.XB** |

### Conglomerate Discount

Diversified companies typically trade at a 10-25% discount to SOTP value due to:
- Lack of pure-play transparency
- Capital allocation inefficiency
- Complexity premium demanded by investors

---

## 5. Valuation Cross-Check Framework

Always triangulate with multiple methods:

| Check | What to Compare | Red Flag |
|-------|----------------|----------|
| DCF vs. Multiples | Implied EV from DCF vs. multiples | Divergence >30% |
| Terminal value % | TV as % of total DCF value | >80% (too speculative) |
| Implied growth | Growth rate implied by current price | Higher than TAM growth |
| Implied margins | Margins implied by current valuation | Higher than best-in-class peer |
| Football field | Range of values across all methods | No overlap between methods |

### Football Field Chart

Present all valuation ranges on a single scale:

```
Method              Low        Base       High
                    |----------|==========|----------|
DCF                 $XXX ------[$XXX]---- $XXX
DDM                 $XXX ------[$XXX]---- $XXX
EV/EBITDA          $XXX ------[$XXX]---- $XXX
P/E                $XXX ------[$XXX]---- $XXX
52-week range      $XXX ------[$XXX]---- $XXX
                    |----------|==========|----------|
Current price: $XXX  ↑
```

This visual helps show where current price sits relative to the range of fair values.
