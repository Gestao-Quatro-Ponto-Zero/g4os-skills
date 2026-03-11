---
name: "Stock Pick Analysis"
description: "Analyze a stock with full investment thesis — fundamentals, valuation models (DCF/Gordon/multiples), peer comparison, sensitivity analysis, and BUY/HOLD/SELL recommendation for 12-month and 60-month horizons"
icon: "📈"
---

# /stock-pick - Stock Pick Analysis

## Purpose

Produce a comprehensive, institutional-quality stock analysis with a clear investment recommendation. Given a ticker or company name, research the company end-to-end and deliver a structured report covering fundamentals, valuation, peer comparison, and scenario analysis across two time horizons (12 months and 5 years).

**Perfect for:**
- Evaluating individual stock investments (long-term and medium-term)
- Building investment theses with quantitative backing
- Comparing a stock against sector peers on multiples
- Running DCF, Gordon Growth, or other valuation models with sensitivity tables
- Producing a self-contained report suitable for an investment committee or personal records

**Not ideal for:**
- Pre-revenue startups (no cash flows to model)
- Distressed/bankrupt companies (need special valuation methods)
- Fixed income, commodities, or derivatives analysis
- Day-trading or technical analysis (this is fundamentals-focused)

---

## Permission Mode Handling

This workflow requires **Execute mode** (writes files, runs web searches, produces the full report).

**Before starting any research:**

1. Check the `<session_state>` tag for `permissionMode`
2. If `permissionMode: execute` → proceed directly to Step 1
3. If `permissionMode: explore` or `permissionMode: ask_to_edit` → do the following:
   - Briefly tell the user: "This workflow needs Execute mode to run web searches and save the report. Submitting a plan for approval."
   - Write a short plan file to the session's `plansFolderPath` summarizing: "Run full stock pick analysis for [TICKER] — web research, financials, peer comparison, valuation models, sensitivity analysis, and final recommendation report."
   - Call `SubmitPlan` with the plan file path
   - **Stop and wait** — the user will click "Accept Plan" to transition to Execute mode
   - Once in Execute mode, proceed to Step 1

---

## Workflow

### Step 1: Identify the Stock

If a ticker or company name is provided as input, use it. Otherwise ask:
- "What stock would you like me to analyze?"

Once identified, confirm:
- **Full company name and ticker** (e.g., "Apple Inc. (AAPL)")
- **Exchange** (NASDAQ, NYSE, B3, etc.)
- **Currency** of the primary listing

### Step 2: Clarify Scope

Before starting, ask briefly:
1. **"Any specific angle?"** — e.g., post-earnings reassessment, sector rotation thesis, portfolio addition screening
2. **"Any constraints?"** — e.g., max position size, ESG filters, sector allocation limits

If the user says "just analyze it", proceed with the full standard workflow.

### Step 3: Current Market Snapshot

Use `WebSearch` to gather real-time data. **Price verification is critical — see rules below.**

- **Current stock price** (with date/time stamp)
- **Market cap**
- **52-week high/low**
- **Average daily volume**
- **YTD performance**
- **Key index benchmarks** (S&P 500, IBOV, sector ETF) for context

#### Price Verification Protocol (Mandatory)

**WebSearch returns cached/stale prices.** Google snippets, aggregator summaries, and AI-generated search answers often show prices that are hours or days old — especially after market close.

**You MUST cross-check the stock price from at least 2 independent sources, with Google Finance as the anchor.**

##### Source 1 (Anchor): Google Finance via WebFetch

Use `WebFetch` to scrape the Google Finance quote page directly. This returns the most recent price with an explicit date/time — far more reliable than search snippets.

**URL pattern by exchange:**

| Exchange | URL Pattern | Example |
|----------|-------------|---------|
| B3 (Brazil) | `https://www.google.com/finance/quote/TICKER:BVMF` | `.../JHSF3:BVMF` |
| NYSE | `https://www.google.com/finance/quote/TICKER:NYSE` | `.../JPM:NYSE` |
| NASDAQ | `https://www.google.com/finance/quote/TICKER:NASDAQ` | `.../AAPL:NASDAQ` |
| LSE (London) | `https://www.google.com/finance/quote/TICKER:LON` | `.../SHEL:LON` |
| Euronext (Paris) | `https://www.google.com/finance/quote/TICKER:EPA` | `.../MC:EPA` |
| Euronext (Amsterdam) | `https://www.google.com/finance/quote/TICKER:AMS` | `.../ASML:AMS` |
| Frankfurt (Xetra) | `https://www.google.com/finance/quote/TICKER:ETR` | `.../SAP:ETR` |
| TSX (Toronto) | `https://www.google.com/finance/quote/TICKER:TSE` | `.../SHOP:TSE` |
| ASX (Sydney) | `https://www.google.com/finance/quote/TICKER:ASX` | `.../BHP:ASX` |
| Hong Kong | `https://www.google.com/finance/quote/TICKER:HKG` | `.../0700:HKG` |
| Tokyo | `https://www.google.com/finance/quote/TICKER:TYO` | `.../7203:TYO` |

**WebFetch prompt:** `"Extract: (1) current/last stock price and currency, (2) date and time of that price, (3) previous close, (4) market cap, (5) 52-week high and low, (6) P/E ratio, (7) dividend yield, (8) day's range, (9) YTD return or 1Y return if available. Return all values as a structured list."`

##### Source 2: WebSearch cross-check

Run **1-2 additional web searches** to verify the Google Finance price:
- Search: `"[TICKER] stock price today [DATE]"` (date-specific)
- For B3 stocks, also try: `"[TICKER] cotação" site:statusinvest.com.br`
- For US stocks, also try: `"[TICKER] stock quote" site:finance.yahoo.com`

##### Verification rules

1. **Compare all prices.** If Google Finance and WebSearch differ by >0.5%, investigate which is correct.
2. **Google Finance takes priority** when it has an explicit date — its price is pulled directly from exchange data.
3. **Never use a price without knowing WHICH trading day it represents.** If a source doesn't show a date, discard it.
4. **Flag uncertainty:** If sources conflict, report BOTH with sources and note the discrepancy.
5. **After-hours warning:** If running outside market hours (B3: after 18:00 BRT / US: after 16:00 ET / EU: after 17:30 CET), note the price is from the prior close.

**Red flags to catch:**
- Price very close to 52w high/low (could be stale cached extremes)
- Price from a search snippet with no explicit date
- Single-source pricing (violates the 2-source rule)
- Google Finance page returning "No results" — try alternative exchange codes

Present as a quick summary table:

| Metric | Value |
|--------|-------|
| Price | $XXX.XX (close [DATE], source: [SOURCE]) |
| Market Cap | $XX.XB |
| 52w Range | $XXX - $XXX |
| YTD Return | +XX.X% |
| Avg Volume | X.XM |
| Benchmark YTD | +XX.X% (S&P 500) |

### Step 4: Company Profile & Business Model

**FIRST:** Search for the most recent earnings release / quarterly results before gathering any financials. See "Data Recency Protocol" below. Determine:
- Latest reported quarter (e.g., "Q3 2025 reported on Nov 12, 2025")
- Whether LTM can be constructed from available quarterly data
- Next earnings date (for the monitoring checklist)

Research and present:

**Business overview** (2-3 sentences — what they do, how they make money)

**Revenue breakdown** by segment/product/geography (using most recent available data):

| Segment | Revenue | % of Total | YoY Growth |
|---------|---------|-----------|------------|
| Segment A | $X.XB | XX% | +XX% |
| Segment B | $X.XB | XX% | +XX% |
| Total | $X.XB | 100% | +XX% |

**Key financial metrics** (most recent fiscal year + LTM):

| Metric | FY-2 | FY-1 | LTM |
|--------|------|------|-----|
| Revenue | $X.XB | $X.XB | $X.XB |
| Revenue Growth | +XX% | +XX% | +XX% |
| Gross Margin | XX% | XX% | XX% |
| EBITDA | $X.XB | $X.XB | $X.XB |
| EBITDA Margin | XX% | XX% | XX% |
| Net Income | $X.XB | $X.XB | $X.XB |
| Net Margin | XX% | XX% | XX% |
| Free Cash Flow | $X.XB | $X.XB | $X.XB |
| FCF Margin | XX% | XX% | XX% |
| EPS | $X.XX | $X.XX | $X.XX |
| Dividends/Share | $X.XX | $X.XX | $X.XX |
| Payout Ratio | XX% | XX% | XX% |

**Balance sheet health:**

| Metric | Value |
|--------|-------|
| Total Debt | $X.XB |
| Cash & Equivalents | $X.XB |
| Net Debt | $X.XB |
| Net Debt / EBITDA | X.Xx |
| Interest Coverage | X.Xx |
| Current Ratio | X.Xx |

### Step 5: Key Vectors & Catalysts

Identify the 3-5 most important factors that will drive the stock over the next 12-60 months. For each vector:

**Format:**
> **[Vector Name]** — [Bull / Bear / Neutral]
>
> [2-3 sentence explanation with specific data points]
>
> *12-month impact:* [High / Medium / Low] — [specific near-term expectation]
> *60-month impact:* [High / Medium / Low] — [structural thesis]

Common vector categories:
- **Revenue growth drivers** (new markets, products, pricing power)
- **Margin trajectory** (operating leverage, cost structure changes)
- **Competitive dynamics** (market share gains/losses, new entrants)
- **Regulatory/policy** (government actions, tariffs, regulation)
- **Capital allocation** (buybacks, dividends, M&A, CapEx cycle)
- **Macro sensitivity** (interest rates, currency, commodity prices)
- **Management quality** (track record, alignment, succession)
- **ESG / sustainability** (material risks or opportunities)

### Step 6: Market & Industry Context

Research using `WebSearch`:

- **TAM/SAM/SOM** — total addressable market with growth rate
- **Industry lifecycle** — early growth, growth, mature, declining
- **Secular trends** — tailwinds and headwinds
- **Competitive landscape** — market structure (oligopoly, fragmented, etc.)
- **Recent industry events** — M&A, regulation, disruption

### Step 7: Peer Comparison & Multiples

Select **4-6 comparable companies** based on business model, scale, and sector. Present for confirmation.

**Trading Multiples Comparison:**

| Company | Mkt Cap | EV | EV/Rev | EV/EBITDA | P/E | P/FCF | Div Yield |
|---------|---------|----|---------|-----------|----|-------|-----------|
| **Target** | $XXB | $XXB | XX.Xx | XX.Xx | XX.Xx | XX.Xx | X.X% |
| Peer 1 | $XXB | $XXB | XX.Xx | XX.Xx | XX.Xx | XX.Xx | X.X% |
| Peer 2 | $XXB | $XXB | XX.Xx | XX.Xx | XX.Xx | XX.Xx | X.X% |
| Peer 3 | $XXB | $XXB | XX.Xx | XX.Xx | XX.Xx | XX.Xx | X.X% |
| Peer 4 | $XXB | $XXB | XX.Xx | XX.Xx | XX.Xx | XX.Xx | X.X% |

**Statistics:**

| Stat | EV/Rev | EV/EBITDA | P/E | P/FCF |
|------|--------|-----------|-----|-------|
| Maximum | | | | |
| 75th Pctl | | | | |
| Median | | | | |
| 25th Pctl | | | | |
| Minimum | | | | |
| **Target** | | | | |

**Operating Metrics Comparison:**

| Company | Rev Growth | Gross Margin | EBITDA Margin | Net Margin | FCF Margin | ROE |
|---------|-----------|-------------|--------------|-----------|-----------|-----|
| **Target** | | | | | | |
| Peer 1 | | | | | | |
| ... | | | | | | |

Add industry-specific metrics per `knowledge/industry-metrics.md`.

**Premium/Discount Analysis:**
- Where the target trades vs. peer median on each multiple
- Justify premium (if any) with growth, margins, moat
- Flag discount as potential opportunity or value trap

### Step 8: Valuation Models (Python-Computed)

**CRITICAL: All numerical calculations MUST be done in Python via Bash.** Do NOT perform arithmetic as an LLM — LLMs make calculation errors, especially with compound growth, discounting, and sensitivity grids.

**Workflow:**
1. Gather all assumptions from research (Steps 3-7)
2. Write a Python script that computes all valuation models
3. Execute via `Bash(python3 /tmp/valuation_[TICKER].py)`
4. Parse the JSON output and present the results
5. Keep the script in `/tmp/` for reproducibility — if the user questions a number, re-run with adjusted inputs

Run **at least two** valuation approaches. Choose based on the company profile:

| Company Type | Primary Model | Secondary Model |
|-------------|---------------|-----------------|
| Stable cash flows, dividends | DCF (FCFF) | Gordon Growth / DDM |
| High-growth, no dividends | DCF (FCFF or FCFE) | EV/Revenue multiples |
| Mature, dividend payer | DDM / Gordon Growth | DCF (FCFF) |
| Cyclical | Normalized earnings multiples | DCF with mid-cycle assumptions |
| Financial services | Excess return / DDM | P/Book regression |
| Pre-profit growth | EV/Revenue multiples | DCF with terminal value focus |

See `knowledge/valuation-models.md` for full model specifications.

#### Python Valuation Script Structure

Write a single Python script that:
1. Takes all assumptions as variables at the top (easy to modify)
2. Computes DCF/DDM/Excess Return projections year by year
3. Computes terminal value (both perpetuity growth and exit multiple methods)
4. Computes WACC from components
5. Generates both sensitivity tables (5x5 grids)
6. Computes multiples-based valuations
7. Computes scenario analysis (bull/base/bear)
8. Outputs everything as JSON to stdout

**Template structure:**
```python
import json

# ============================================================
# ASSUMPTIONS (modify these for each stock)
# ============================================================
ticker = "XXXX"
current_price = 0.0
shares_outstanding = 0  # in millions

# Revenue & margins
base_revenue = 0.0  # LTM revenue in millions
revenue_cagr_phase1 = 0.0  # Years 1-3
revenue_cagr_phase2 = 0.0  # Years 4-5
terminal_growth = 0.0
base_ebitda_margin = 0.0
terminal_ebitda_margin = 0.0
capex_pct_revenue = 0.0
nwc_change_pct_revenue = 0.0
tax_rate = 0.0

# WACC components
risk_free_rate = 0.0
equity_risk_premium = 0.0
beta = 0.0
cost_of_debt_pretax = 0.0
debt_equity_ratio = 0.0

# DDM (if applicable)
current_dps = 0.0
dps_growth_phase1 = 0.0
dps_growth_stable = 0.0

# Peer multiples
peer_ev_ebitda = 0.0  # median
peer_pe = 0.0  # median
peer_ev_revenue = 0.0  # median

# Balance sheet
net_debt = 0.0  # positive = net debt, negative = net cash

# ============================================================
# CALCULATIONS
# ============================================================

# Cost of equity
ke = risk_free_rate + beta * equity_risk_premium

# WACC
weight_equity = 1 / (1 + debt_equity_ratio)
weight_debt = debt_equity_ratio / (1 + debt_equity_ratio)
kd_after_tax = cost_of_debt_pretax * (1 - tax_rate)
wacc = weight_equity * ke + weight_debt * kd_after_tax

# DCF Projections
projections = []
revenue = base_revenue
for year in range(1, 6):
    cagr = revenue_cagr_phase1 if year <= 3 else revenue_cagr_phase2
    revenue *= (1 + cagr)
    # Linear margin convergence to terminal
    margin = base_ebitda_margin + (terminal_ebitda_margin - base_ebitda_margin) * (year / 5)
    ebitda = revenue * margin
    capex = revenue * capex_pct_revenue
    nwc = revenue * nwc_change_pct_revenue
    fcff = ebitda * (1 - tax_rate) + (ebitda - ebitda * (1 - tax_rate)) * 0 - capex - nwc
    # Simplified: FCFF = EBIT(1-t) + D&A - CapEx - dNWC
    # Using EBITDA proxy: FCFF ≈ EBITDA(1-t) + t*D&A - CapEx - dNWC
    # Simplified further for model: FCFF = EBITDA - Tax on EBIT - CapEx - dNWC
    nopat = ebitda * (1 - tax_rate)  # approximation
    fcff = nopat - capex - nwc
    pv_factor = 1 / (1 + wacc) ** year
    projections.append({
        "year": year, "revenue": revenue, "ebitda": ebitda,
        "capex": capex, "nwc_change": nwc, "fcff": fcff,
        "pv_factor": pv_factor, "pv_fcff": fcff * pv_factor
    })

# Terminal value
terminal_fcff = projections[-1]["fcff"] * (1 + terminal_growth)
terminal_value = terminal_fcff / (wacc - terminal_growth)
pv_terminal = terminal_value / (1 + wacc) ** 5

# Enterprise value
pv_fcffs = sum(p["pv_fcff"] for p in projections)
enterprise_value = pv_fcffs + pv_terminal
equity_value = enterprise_value - net_debt
implied_price = equity_value / shares_outstanding

# Sensitivity: WACC vs terminal growth (5x5)
wacc_range = [wacc - 0.02, wacc - 0.01, wacc, wacc + 0.01, wacc + 0.02]
g_range = [terminal_growth - 0.01, terminal_growth - 0.005, terminal_growth,
           terminal_growth + 0.005, terminal_growth + 0.01]

sensitivity_wacc_g = []
for w in wacc_range:
    row = []
    for g in g_range:
        if w <= g:
            row.append(None)  # Invalid
            continue
        tv = projections[-1]["fcff"] * (1 + g) / (w - g)
        pv_tv = tv / (1 + w) ** 5
        # Recalculate PV of FCFs with new WACC
        pv_sum = sum(p["fcff"] / (1 + w) ** p["year"] for p in projections)
        ev = pv_sum + pv_tv
        eq = ev - net_debt
        price = eq / shares_outstanding
        row.append(round(price, 2))
    sensitivity_wacc_g.append(row)

# ... (similar for revenue CAGR vs margin sensitivity)
# ... (DDM calculation if applicable)
# ... (multiples-based valuation)
# ... (scenario analysis)

# Output as JSON
results = {
    "ticker": ticker,
    "wacc": {"ke": ke, "kd_after_tax": kd_after_tax, "wacc": wacc},
    "dcf": {
        "projections": projections,
        "terminal_value": terminal_value,
        "pv_terminal": pv_terminal,
        "pv_fcffs": pv_fcffs,
        "enterprise_value": enterprise_value,
        "equity_value": equity_value,
        "implied_price": implied_price,
        "upside": (implied_price / current_price - 1)
    },
    "sensitivity_wacc_g": {
        "wacc_values": [round(w*100, 1) for w in wacc_range],
        "g_values": [round(g*100, 1) for g in g_range],
        "prices": sensitivity_wacc_g
    },
    # ... other models
}
print(json.dumps(results, indent=2, default=str))
```

**Adapt the script for each stock:** The template above is a starting point. For financial services, replace DCF with Excess Return Model. For REITs, use DDM/NAV. Always customize the calculation logic to match the chosen valuation approach.

#### 8a: DCF Model (Discounted Cash Flow)

Present the Python-computed results in these tables:

**Assumptions table:**

| Assumption | Value | Rationale |
|-----------|-------|-----------|
| Projection period | 5-10 years | |
| Revenue CAGR (Years 1-3) | XX% | Based on [guidance/trend] |
| Revenue CAGR (Years 4-5) | XX% | Moderated growth |
| Terminal growth rate | X.X% | Long-term GDP + inflation proxy |
| EBITDA margin (Year 5) | XX% | Peer median / management target |
| CapEx as % of Revenue | XX% | Historical average |
| WACC | XX.X% | See calculation below |
| Tax rate | XX% | Effective rate |

**WACC calculation:**

| Component | Value |
|-----------|-------|
| Risk-free rate | X.X% (10Y Treasury / NTN-B) |
| Equity risk premium | X.X% |
| Beta (levered) | X.Xx |
| Cost of equity (Ke) | XX.X% |
| Cost of debt (Kd) pre-tax | X.X% |
| Cost of debt (Kd) after-tax | X.X% |
| Debt/Equity | X.X% |
| **WACC** | **XX.X%** |

**Projected Free Cash Flows (Python-computed):**

| Year | Revenue | EBITDA | CapEx | Change in WC | FCFF | PV(FCFF) |
|------|---------|--------|-------|-------------|------|----------|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |
| 4 | | | | | | |
| 5 | | | | | | |
| Terminal | | | | | | |

**Valuation summary:**

| Component | Value |
|-----------|-------|
| PV of projected FCFs | $X.XB |
| PV of terminal value | $X.XB |
| Enterprise Value | $X.XB |
| (-) Net Debt | $X.XB |
| Equity Value | $X.XB |
| Shares Outstanding | X.XB |
| **Implied Price/Share** | **$XXX.XX** |
| Current Price | $XXX.XX |
| **Upside / Downside** | **+XX% / -XX%** |

#### 8b: Gordon Growth Model / DDM (if applicable)

| Assumption | Value |
|-----------|-------|
| Current DPS | $X.XX |
| Dividend Growth Rate (g) | X.X% |
| Cost of Equity (Ke) | XX.X% |
| **Implied Value** | **$XXX.XX** |

For multi-stage DDM (high-growth → stable):

| Phase | Years | DPS Growth | Terminal Ke |
|-------|-------|-----------|-------------|
| High growth | 1-5 | XX% | |
| Transition | 6-8 | Declining to X% | |
| Stable | 9+ | X.X% | XX.X% |

#### 8c: Multiples-Based Valuation

| Multiple | Peer Median | Target Metric | Implied EV | Implied Equity | Implied Price |
|----------|-----------|--------------|-----------|---------------|--------------|
| EV/Revenue | XX.Xx | $X.XB | $X.XB | $X.XB | $XXX |
| EV/EBITDA | XX.Xx | $X.XB | $X.XB | $X.XB | $XXX |
| P/E | XX.Xx | $X.XX EPS | - | $X.XB | $XXX |
| P/FCF | XX.Xx | $X.XX FCFPS | - | $X.XB | $XXX |

**Valuation Summary (all methods):**

| Method | Implied Price | vs. Current | Weight |
|--------|--------------|-------------|--------|
| DCF | $XXX | +XX% | 40% |
| DDM/Gordon | $XXX | +XX% | 20% |
| EV/EBITDA (peer median) | $XXX | +XX% | 20% |
| P/E (peer median) | $XXX | +XX% | 20% |
| **Weighted Average** | **$XXX** | **+XX%** | 100% |

### Step 9: Sensitivity Analysis (Python-Computed)

The sensitivity tables MUST come from the Python script (Step 8). Do NOT compute 25 cells manually.

See `knowledge/sensitivity-framework.md` for methodology.

**Table 1: WACC vs. Terminal Growth Rate**

| | g = 1.5% | g = 2.0% | g = 2.5% | g = 3.0% | g = 3.5% |
|---|---------|---------|---------|---------|---------|
| WACC 8.0% | $XXX | $XXX | $XXX | $XXX | $XXX |
| WACC 9.0% | $XXX | $XXX | $XXX | $XXX | $XXX |
| **WACC 10.0%** | $XXX | **$XXX** | $XXX | $XXX | $XXX |
| WACC 11.0% | $XXX | $XXX | $XXX | $XXX | $XXX |
| WACC 12.0% | $XXX | $XXX | $XXX | $XXX | $XXX |

*Bold = base case*

**Table 2: Revenue CAGR vs. Terminal EBITDA Margin**

| | Margin 18% | Margin 20% | Margin 22% | Margin 24% | Margin 26% |
|---|-----------|-----------|-----------|-----------|-----------|
| CAGR 5% | $XXX | $XXX | $XXX | $XXX | $XXX |
| CAGR 8% | $XXX | $XXX | $XXX | $XXX | $XXX |
| **CAGR 10%** | $XXX | **$XXX** | $XXX | $XXX | $XXX |
| CAGR 12% | $XXX | $XXX | $XXX | $XXX | $XXX |
| CAGR 15% | $XXX | $XXX | $XXX | $XXX | $XXX |

*Bold = base case*

**Breakeven Analysis:**
- "For the stock to be fairly valued at today's price, you need [WACC of X% + terminal growth of Y%], which implies [assessment of whether that's reasonable]"

### Step 10: Scenario Analysis

| Scenario | Probability | Key Assumptions | Implied Price | Upside/Downside |
|----------|-----------|-----------------|--------------|----------------|
| **Bull** | 25% | [Specific drivers] | $XXX | +XX% |
| **Base** | 50% | [Specific drivers] | $XXX | +XX% |
| **Bear** | 25% | [Specific drivers] | $XXX | -XX% |
| **Probability-Weighted** | 100% | | **$XXX** | **+XX%** |

For each scenario, specify:
- Revenue growth trajectory
- Margin assumptions
- Multiple expansion/contraction
- Key catalyst or risk that triggers this scenario

### Step 11: Devil's Advocate — Contrarian Stress-Test

**Before writing the final recommendation, force yourself to argue AGAINST your own thesis.** This step exists to combat confirmation bias — the #1 analytical trap.

Answer ALL of the following questions honestly. If the answers weaken the thesis, adjust the recommendation accordingly.

#### Mandatory Contrarian Questions

**1. Existential test:**
> "Can we imagine the world without this company in 5 years? Why or why not?"
> - If yes → What replaces it? How fast could that happen?
> - If no → That's a moat signal. But is the moat PRICED IN already?

**2. Capital loss scenario:**
> "Our thesis is wrong and we lose 30-50% of our capital in the [12/60]-month horizon. What went wrong?"
> - Write 2-3 specific, plausible narratives for how this plays out
> - For each: What was the early warning sign we missed?

**3. The bear is right:**
> "The most vocal bear on this stock is right. What is their argument, and what evidence supports it?"
> - Search: `"[TICKER] bear case"` or `"[TICKER] overvalued"` or `"por que não investir em [TICKER]"`
> - Steelman the bear case — present it as convincingly as possible

**4. Consensus trap:**
> "What does everyone agree on about this stock — and what happens if that consensus is wrong?"
> - If consensus = "great management" → What if key person leaves?
> - If consensus = "growing market" → What if TAM is smaller than estimated?
> - If consensus = "cheap on multiples" → Is it cheap for a reason (value trap)?

**5. Alternatives test:**
> "For the same risk, is there a better opportunity?"
> - Compare risk-adjusted return vs. benchmark index (just buying the index)
> - Compare vs. the best peer in the comparison table
> - If a peer offers similar upside with lower risk → flag it

#### Presentation

Present this section as a clear-eyed counterargument, then explain whether each contrarian point:
- **(a) Changes the thesis** — lower conviction, adjust target, change rating
- **(b) Is acknowledged but priced in** — the market already discounts this risk
- **(c) Is a real risk but low probability** — monitor it, include in the checklist

**This section must appear in both the chat output AND the saved file.** It is as important as the valuation itself.

### Step 12: Final Recommendation

**Rating:** **BUY / HOLD / SELL**

**Rating Framework:**

| Rating | Criteria |
|--------|----------|
| **BUY** | Probability-weighted upside > 15% AND base case upside > 10% AND no critical unresolvable risks |
| **HOLD** | Probability-weighted upside between -10% and +15% OR significant uncertainty that could resolve either way |
| **SELL** | Probability-weighted downside > 10% OR deteriorating fundamentals OR better risk/reward elsewhere |

**Summary Table:**

| Horizon | Target Price | Upside/Downside | Rating | Confidence |
|---------|-------------|----------------|--------|------------|
| 12 months | $XXX | +XX% | BUY/HOLD/SELL | High/Medium/Low |
| 60 months | $XXX | +XX% | BUY/HOLD/SELL | High/Medium/Low |

**Investment Thesis (3-5 sentences):**
- Why own this stock (or why not)
- What's the key bet you're making
- What would change the thesis (bull and bear triggers)
- Position sizing guidance (conviction level → % of portfolio)

**Key Risks:**
1. [Risk 1 — probability and impact]
2. [Risk 2 — probability and impact]
3. [Risk 3 — probability and impact]

**Monitoring Checklist:**
- [ ] [Metric/event to watch quarterly]
- [ ] [Metric/event to watch quarterly]
- [ ] [Earnings date or catalyst date]

---

## Output Format

### 1. Save the Full Report to File

Generate a structured markdown report saved to a file with all sections:

1. **Executive Summary** — 1-paragraph thesis + rating table
2. **Market Snapshot** — current price and trading data (with source + date)
3. **Company Profile** — business model, financials, balance sheet (latest quarter)
4. **Key Vectors** — catalysts and risks with time-horizon impact
5. **Industry Context** — TAM, trends, competitive landscape
6. **Peer Comparison** — multiples tables with statistics
7. **Valuation** — DCF + secondary model + multiples-based, with assumptions
8. **Sensitivity Analysis** — 2 sensitivity tables + breakeven
9. **Scenario Analysis** — bull/base/bear with probabilities
10. **Devil's Advocate** — contrarian stress-test (existential, capital loss, bear case, consensus trap, alternatives)
11. **Recommendation** — rating, target prices, thesis, risks, monitoring

**File naming:** `[TICKER]_stock-pick_[YYYY-MM-DD].md`
**Save to:** The current working directory or a subfolder if the user has a preferred location.

### 2. Present the FULL Report in Chat (Critical!)

**DO NOT just show a summary dashboard.** The user expects to read the complete analysis in the chat window, not have to open a file. After saving the file, present the ENTIRE report in chat with rich formatting.

**The chat output should be SELF-CONTAINED — a reader who never opens the file should get the full picture. The file is a backup/archive, not the primary delivery. Show every table, every number, every piece of analysis. Do not truncate, summarize, or skip sections.**

#### Chat Output Template (follow this exact structure)

**Section 1 — Executive Summary Card** (`jsonrender`)
- Card with title = "[TICKER] — [Company Name]" and subtitle = "Stock Pick — [Date]"
- Grid (3-4 columns) with Metric components: Price (+YTD change), Weighted Fair Value (+upside%), key ratio (Div Yield or P/E), Rating (BUY/HOLD/SELL)
- Divider + Alert (type: info/warning depending on thesis tone) with 2-sentence thesis

**Section 2 — Market Snapshot** (`datatable`)
- All market data (price, market cap, 52w range, YTD return, shares outstanding, beta, listing, key people)
- Below the table: brief note on price verification sources

**Section 3 — Company Profile** (markdown narrative + `datatable` + optional `mermaid`)
- 2-3 sentence business overview
- If the company has 4+ distinct business segments → `mermaid` flowchart showing the ecosystem (like JHSF example)
- Revenue breakdown → `datatable` with columns: Segment, Revenue, % of Total, YoY Growth
- Key financials → `datatable` with columns: Metric, Value, YoY Change (use latest quarter/LTM data)
- Balance sheet → `datatable` with key metrics

**Section 4 — Key Vectors & Catalysts** (`jsonrender` tabs OR markdown blockquotes)
- Option A (preferred for visual impact): `jsonrender` Tabs component with "Bullish" and "Bearish" tabs, each containing a Checklist with catalyst items (checked = already materializing, unchecked = yet to play out)
- Option B (simpler, also good): Markdown blockquotes per vector with Bull/Bear/Neutral tag, explanation, and 12m/60m impact ratings
- Either format works — pick based on the stock's catalyst count

**Section 5 — Peer Comparison** (`spreadsheet` or `datatable`)
- Use `spreadsheet` if the user may want to export (peer multiples are often useful to copy)
- Columns: Metric as row labels, each peer as a column, plus Peer Median column
- Include both trading multiples (P/E, P/B, EV/EBITDA, Div Yield) AND operating metrics (Gross Margin, EBITDA Margin, ROE, Net Debt/EBITDA, Revenue Growth)
- Below: 1-2 sentence premium/discount analysis text

**Section 6 — Valuation Models** (`datatable` + `jsonrender`)
- WACC or Ke components → `datatable` or brief markdown summary
- Projected cash flows / DDM projections → `datatable` with year-by-year data (columns: Year, Revenue/EPS, EBITDA/Payout, FCFF/DPS, PV)
- Each model result → `datatable` (e.g., DDM implied prices by Ke scenario, or forward P/E at different multiples)
- **All-methods summary** → `jsonrender` Card with Grid of Stat components (one per model: name, implied price, weight) + Divider + Metric for Weighted Fair Value
- Below: interpretive text explaining the gap between intrinsic and market-implied values

**Section 7 — Sensitivity Analysis** (`spreadsheet` × 2 + markdown)
- Table 1 (WACC/Ke vs Terminal Growth) → `spreadsheet` with bold base case label in row/column headers
- Table 2 (Revenue CAGR vs Margin, or Growth vs ROE for banks) → `spreadsheet`
- Below each table: 1-2 sentence interpretation (e.g., "X of 25 scenarios show upside", "current price requires WACC of X%")
- Breakeven analysis → markdown text or small markdown table

**Section 8 — Scenario Analysis** (`datatable`)
- Columns: Scenario, Probability, Price, vs Current, Key Assumptions
- Rows: Bull, Base, Bear, Probability-Weighted
- Below: 1 sentence on risk/reward asymmetry

**Section 9 — Devil's Advocate** (markdown)
- Numbered Q&A format with the 5 mandatory contrarian questions
- Each answer: 2-4 sentences, direct and honest
- For each: tag as (a) changes thesis, (b) priced in, or (c) low probability/monitor

**Section 10 — Final Recommendation** (`jsonrender` + markdown)
- `jsonrender` Card with: title = "Recommendation: [RATING]", subtitle = "[TICKER] · [PRICE]"
  - Grid (2 columns) with Stat for 12-month target and 60-month or prob-weighted target
  - Divider + Checklist with 5-7 monitoring items (unchecked)
- Below: **Investment Thesis** as 2-3 sentence markdown paragraph
- **Position Sizing** as markdown table (Entry Point → Allocation %)

**Section 11 — Closing** (`filecard` + sources + disclaimer)
- `filecard` for the saved .md report file
- **Sources:** Bulleted list of all web sources cited, as markdown links
- **Disclaimer:** Standard AI-generated analysis disclaimer (1 sentence italic)
- **Optional xlsx prompt:** "Quer que eu gere uma planilha Excel com o modelo de valuation editável?"

### 3. Optional: Valuation Spreadsheet (.xlsx)

After presenting the full report, **ask the user:** "Quer que eu gere uma planilha Excel com o modelo de valuation editável?"

If yes, use the `/xlsx` skill to create a spreadsheet with:

**Tab 1 — Premissas (Assumptions):**
- All editable assumptions in a clear table (highlighted cells = user-editable)
- WACC components, growth rates, margins, terminal assumptions
- Named ranges for easy formula references

**Tab 2 — DCF Model:**
- Year-by-year projections with formulas (not hardcoded values)
- Revenue = Prior Year × (1 + Growth Rate)
- EBITDA = Revenue × Margin
- FCFF = NOPAT - CapEx - dNWC
- PV = FCFF / (1 + WACC)^Year
- Terminal value calculation
- Enterprise Value → Equity Value → Price/Share

**Tab 3 — Sensitivity:**
- WACC vs. g table (5x5) — **MUST use Excel formulas** that recalculate when assumptions change (see rules below)
- Revenue CAGR vs. Margin table (5x5) — **MUST use Excel formulas**
- Conditional formatting (green = upside, red = downside)

**Tab 4 — Peer Comparison:**
- All peer multiples data
- Statistics (mean, median, quartiles)
- Target's position vs. peers

**Tab 5 — Summary:**
- Football field (all methods side by side)
- Rating and target prices
- Key metrics dashboard

**File naming:** `[TICKER]_valuation_[YYYY-MM-DD].xlsx`

#### Spreadsheet Formula Rules (Critical — Prevents Known Bugs)

**The following bugs have occurred in past spreadsheet generations. These rules are mandatory:**

**Rule 1: Track cell addresses explicitly.**
When writing formulas with f-strings in openpyxl, row offsets are the #1 source of bugs. Before writing any formula, add a comment block mapping every variable name to its cell address:

```python
# === CELL ADDRESS MAP ===
# B4 = Base Revenue        B5 = CAGR Phase 1     B6 = CAGR Phase 2
# B7 = Base EBITDA Margin  B8 = Term Margin       B9 = Terminal Growth
# B10 = CapEx %            B11 = NWC %            B12 = D&A %
# B13 = Tax Rate           B14 = WACC             B15 = Exit Multiple
# B16 = Shares Outstanding B17 = Net Debt
# ...
# TV_PERP_ROW = 29  TV_EXIT_ROW = 30  PV_PERP_ROW = 31  PV_EXIT_ROW = 32
```

**Rule 2: Never reference column A in a calculation formula.**
Column A is always labels. If you find yourself writing `=A{row}`, you almost certainly mean `=B{row}`. This bug caused the JHSF3 PV Terminal Value to reference a text label instead of a number.

**Rule 3: After writing each formula, verify it references the correct row.**
When items are laid out vertically in column B (e.g., TV Perpetuity in B29, TV Exit Multiple in B30), the PV of each must reference its OWN row:
- `PV TV Perpetuity = B29 / (1+WACC)^5` → references B29 ✓
- `PV TV Exit Multiple = B30 / (1+WACC)^5` → references B30 ✓ (NOT B29)

**Rule 4: Sensitivity tables MUST use formulas, not hardcoded values.**
The whole point of a spreadsheet is that changing an input updates the outputs. Sensitivity tables with pasted numbers are useless.

Instead of:
```python
prices = [[8.31, 8.72, ...]]  # WRONG — static numbers
ws.cell(row=row, column=col, value=p)
```

Do this — each sensitivity cell should contain a formula that computes the implied price from the row/column assumption:
```python
# Sensitivity inputs: WACC values in column A (rows 5-9), g values in row 4 (cols B-F)
# Each cell formula: rebuild the DCF with that cell's WACC and g
# Approach: reference the DCF sheet's FCFF row, compute TV and PV inline
for i, w_row in enumerate(wacc_rows):
    for j, g_col in enumerate(g_cols):
        # PV of FCFs with this WACC + TV with this g / (this WACC - this g), discounted
        cell = ws.cell(row=w_row, column=g_col)
        cell.value = f"=<formula using $A{w_row} as WACC and {g_col_letter}$4 as g>"
```

If inline DCF formulas are too complex, an acceptable alternative is to use the Python valuation script's output BUT ALSO include an "Assumptions" input area on the sensitivity sheet that feeds into simpler formulas (e.g., Gordon Growth shortcut: `=FCFF_Y5*(1+g)/(WACC-g)` per cell).

**Rule 5: Run the formula validation script BEFORE delivering the file.**
After generating the xlsx, run this validation:

```python
# /tmp/validate_xlsx.py — run after generating the spreadsheet
import openpyxl, json, sys

path = sys.argv[1]
wb = openpyxl.load_workbook(path)
errors = []

for ws in wb.worksheets:
    for row in ws.iter_rows():
        for cell in row:
            if isinstance(cell.value, str) and cell.value.startswith('='):
                formula = cell.value
                coord = f"'{ws.title}'!{cell.coordinate}"

                # Check 1: References to column A in calculation formulas
                # (A is usually labels — flag unless it's a year number like A21)
                import re
                a_refs = re.findall(r'(?<![A-Z])A(\d+)', formula)
                for ref_row in a_refs:
                    errors.append(f"WARNING: {coord} references A{ref_row} (usually labels): {formula}")

                # Check 2: Cross-sheet references to non-existent sheets
                sheet_refs = re.findall(r"'([^']+)'!", formula)
                for sref in sheet_refs:
                    if sref not in wb.sheetnames:
                        errors.append(f"ERROR: {coord} references non-existent sheet '{sref}': {formula}")

                # Check 3: Division where denominator could be zero
                if '/0' in formula or '-0)' in formula:
                    errors.append(f"WARNING: {coord} possible div/0: {formula}")

# Check 4: Sheets with zero formulas (likely hardcoded)
for ws in wb.worksheets:
    formula_count = sum(1 for row in ws.iter_rows() for cell in row
                       if isinstance(cell.value, str) and cell.value.startswith('='))
    if 'sens' in ws.title.lower() or 'sensitivity' in ws.title.lower():
        if formula_count == 0:
            errors.append(f"ERROR: Sheet '{ws.title}' has 0 formulas — sensitivity tables must use formulas, not hardcoded values")

result = {"total_errors": len(errors), "errors": errors}
print(json.dumps(result, indent=2))
if errors:
    sys.exit(1)
```

Execute: `python3 /tmp/validate_xlsx.py [TICKER]_valuation_[DATE].xlsx`

**If ANY errors are found, fix them before delivering the file.** Re-generate the xlsx and re-validate until clean.

**Rule 6: Run the `/xlsx` recalc script if LibreOffice is available.**
After validation, try: `python3 scripts/recalc.py output.xlsx`
If it fails (LibreOffice not installed), note to the user: "Formulas will calculate when you open the file in Excel or Google Sheets. Pre-calculation wasn't possible without LibreOffice."

---

## Data Sourcing Rules

1. **Use `WebSearch` aggressively** — current prices, recent filings, consensus estimates, news
2. **Cite every number** — "[Company 10-K FY2025]", "[Yahoo Finance, Feb 2026]", "[Consensus estimate, Bloomberg]"
3. **Flag estimates** — use `[E]` suffix for any estimated or consensus number
4. **Flag stale data** — if a data point is >6 months old, note it
5. **Never fabricate financials** — if you cannot find a specific number, say so and use reasonable proxies with clear disclosure
6. **Cross-check critical numbers** — revenue, EBITDA, net income should be verified across at least 2 sources
7. **For Brazilian stocks (B3):** use BRL, reference IBOV as benchmark, use SELIC + risk premium for WACC, NTN-B for risk-free rate

### Data Recency Protocol (Mandatory)

**ALWAYS use the most recent financial data available.** This means the latest quarterly or half-year report, NOT just the latest annual report.

**Before using any financial data, determine the freshness chain:**

1. **Search for the most recent earnings release first:**
   - `"[COMPANY] earnings Q[X] [YEAR]"` or `"[COMPANY] resultados [trimestre] [ANO]"` (for B3)
   - Check the company's IR (Investor Relations) website for the latest press release
   - For B3 stocks: search `"[TICKER] resultados" site:ri.[company].com.br`

2. **Identify the latest available period:**
   | Data Type | Check Order (most recent first) |
   |-----------|-------------------------------|
   | Income Statement | LTM → Latest quarter → Latest half-year → Latest annual |
   | Balance Sheet | Latest quarter-end → Latest annual |
   | Cash Flow | LTM → Latest annual |
   | Guidance | Most recent earnings call or investor day |

3. **Construct LTM (Last Twelve Months) when possible:**
   ```
   LTM = Annual (latest FY) + YTD (current year quarters) - YTD (prior year same quarters)
   ```
   Or: sum of last 4 reported quarters.

4. **Always disclose the reporting period:**
   - "Revenue: R$2.1B [LTM Q3 2025]" — not just "Revenue: R$2.1B"
   - "Net Income: R$450M [FY 2024]" — if only annual is available, say so

5. **Red flags for stale data:**
   - Using annual data when 2+ quarters of newer data exist → **unacceptable**
   - Financial data more than 2 quarters old without disclosure → **flag it**
   - Peer comparison mixing different periods (one peer LTM, another FY) → **normalize**

6. **When quarterly data is unavailable** (some non-US companies report only semi-annually):
   - Use the latest semi-annual + prior annual to construct approximations
   - Clearly label: "[H1 2025 annualized, E]"

**The goal:** Every financial metric in the report should reflect the company's CURRENT state, not a snapshot from 6-12 months ago.

---

## Brazilian Market Specifics

When analyzing stocks on B3 (Brasil Bolsa Balcao):

- **Currency:** All figures in BRL (R$) unless the user requests USD
- **Benchmark:** IBOV (Ibovespa) instead of S&P 500
- **Risk-free rate:** NTN-B (IPCA+ long-term) or SELIC for short-term
- **Country risk premium:** Add Brazil CDS spread or EMBI+ spread
- **WACC adjustments:** Use local CAPM with Brazil equity risk premium
- **Tax rate:** Standard corporate rate (34% — IR 25% + CSLL 9%)
- **Dividend rules:** Brazilian companies have mandatory minimum dividend (usually 25% of adjusted net income)
- **Sources:** CVM filings, RI websites, Status Invest, Fundamentus, B3 website
- **Multiples conventions:** P/L (not P/E), EV/EBITDA, P/VPA (P/Book), Dividend Yield

---

## International Market Adaptation

This workflow supports stocks from any major exchange. Detect the exchange in Step 1 and adapt the following automatically:

| Parameter | US (NYSE/NASDAQ) | Brazil (B3/BVMF) | Europe (LSE/Euronext/Xetra) | Asia-Pacific (HKG/TYO/ASX) |
|-----------|------------------|-------------------|-----------------------------|-----------------------------|
| **Currency** | USD ($) | BRL (R$) | GBP (£) / EUR (€) | HKD / JPY (¥) / AUD (A$) |
| **Benchmark** | S&P 500 | IBOV (Ibovespa) | FTSE 100 / STOXX 600 / DAX | Hang Seng / Nikkei 225 / ASX 200 |
| **Risk-free rate** | 10Y US Treasury | NTN-B (IPCA+ real) | 10Y Gilt / 10Y Bund | 10Y local sovereign |
| **ERP** | 4.5-5.5% | 5-7% + CRP 2-4% | 5-6% | 5-7% + CRP if applicable |
| **Tax rate** | 21% federal | 34% (IR+CSLL) | UK 25% / FR 25% / DE 30% | HK 16.5% / JP 30% / AU 30% |
| **Mandatory dividends** | None | Min. 25% adjusted NI | Varies | Varies |
| **Filings** | SEC (10-K, 10-Q) | CVM (DFP, ITR) | Annual Report, Half-year | Annual + interim |
| **Google Finance suffix** | `:NYSE` or `:NASDAQ` | `:BVMF` | `:LON` / `:EPA` / `:ETR` | `:HKG` / `:TYO` / `:ASX` |
| **Financial data sources** | Yahoo Finance, SEC EDGAR, Macrotrends | Status Invest, Fundamentus, CVM | FT, Morningstar, company RI | Yahoo Finance HK/JP, company RI |
| **Multiples conventions** | P/E, EV/EBITDA | P/L, EV/EBITDA, P/VPA | P/E, EV/EBITDA | P/E, P/B (common in Asia) |
| **Reporting currency** | Usually USD | Usually BRL | May be USD/EUR/GBP — check | May differ from listing currency |

**Auto-detection:** In Step 1, once the exchange is confirmed, apply the corresponding column above for ALL subsequent steps. If the user wants the analysis in a different currency (e.g., USD for a B3 stock), convert at the current exchange rate and note it.

**Cross-listed stocks:** If a company trades on multiple exchanges (e.g., ADR in NYSE + primary in B3), use the PRIMARY listing for price/volume data and note the ADR ticker for reference.

---

## Quality Checklist

Before delivery, verify:
- [ ] Stock price verified via Google Finance WebFetch + at least 1 additional source
- [ ] Price includes explicit date and source attribution
- [ ] Financial data uses the MOST RECENT available period (LTM or latest quarter, not outdated annual)
- [ ] Every financial metric cites its reporting period (e.g., "[LTM Q3 2025]", "[FY 2024]")
- [ ] At least 2 valuation methods applied, computed via Python
- [ ] Sensitivity tables have 5x5 grid with base case highlighted
- [ ] Peer group has 4-6 truly comparable companies with consistent reporting periods
- [ ] Both 12-month and 60-month horizons addressed
- [ ] Devil's Advocate section completed — all 5 contrarian questions answered
- [ ] Rating is clearly justified and consistent with the numbers
- [ ] Key risks are specific (not generic "market risk")
- [ ] Thesis can be summarized in 2 sentences
- [ ] No formula errors or contradictory numbers across sections
- [ ] International stocks use correct currency, benchmark, and WACC parameters for their market

---

## Common Mistakes to Avoid

**Price & Data:**
- **Trusting a single WebSearch price** — Google snippets return cached/stale prices (known bug: JHSF3 showed R$10.10 when actual close was R$9.92). ALWAYS use Google Finance WebFetch as anchor + cross-check
- **Using outdated financials** — If Q3 2025 results are published and you use only FY 2024 data, the analysis is 9 months stale. Always search for the latest quarterly report first
- **Mixing reporting periods in peer comparison** — One peer on LTM, another on FY → apples to oranges. Normalize all peers to the same period
- Using stale prices or outdated financials without disclosure

**Valuation errors:**
- Mixing currencies in peer comparison (always normalize)
- Applying EV multiples to equity metrics or vice versa
- Terminal growth rate > long-term GDP growth (unsustainable)
- WACC that doesn't reflect the company's actual capital structure
- Ignoring dilution from stock options / convertibles
- Treating consensus estimates as facts (always flag as `[E]`)

**Analytical bias:**
- **Confirmation bias** — present the bear case as seriously as the bull case. The Devil's Advocate step (Step 11) exists specifically to counter this
- **Skipping the "what if I'm wrong" question** — Every buy recommendation should have a clear "I'd sell if X happens" trigger
- Generic risk factors instead of company-specific ones
- Anchoring to current price when building projections (project from fundamentals, not price)

**International stocks:**
- Forgetting to adjust WACC for country risk premium in emerging markets
- Using US tax rates for non-US companies
- Not checking if the reporting currency differs from the trading currency (e.g., a London-listed company reporting in USD)

---

## Disclaimer

This analysis is generated by an AI assistant and is intended for informational and educational purposes only. It does **not** constitute financial advice, a recommendation to buy or sell securities, or an offer of any kind. Market data, financial projections, and valuations are based on publicly available sources and AI-generated estimates, which may be incomplete, outdated, or inaccurate. All findings should be independently verified before making investment decisions. Past performance is not indicative of future results. The user assumes all risk associated with investment decisions.
