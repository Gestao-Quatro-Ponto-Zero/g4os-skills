#!/usr/bin/env python3
"""
value_ladder.py — Value Ladder Visualization & Analysis

Generates an interactive HTML visualization and JSON analysis of a company's
product value ladder. Flags pricing cliffs (>3x gaps), computes health metrics,
and renders a dark-themed SVG-based ladder diagram.

Usage:
    python value_ladder.py \
        --input-json '{"company_name": "...", "products": [...]}' \
        --output-dir /path/to/output
"""

import argparse
import json
import os
import sys
from html import escape
from datetime import datetime


# ---------------------------------------------------------------------------
# Analysis Engine
# ---------------------------------------------------------------------------

def analyze_value_ladder(data: dict) -> dict:
    """Compute all value-ladder metrics from the input data."""
    company = data["company_name"]
    products = sorted(data["products"], key=lambda p: p["price"])

    steps = []
    total_revenue = 0
    max_revenue = 0
    ascension_rates = []
    cliff_count = 0
    total_gaps = 0

    for i, prod in enumerate(products):
        revenue = prod["price"] * prod["active_clients"]
        margin_revenue = revenue * (prod["margin_pct"] / 100)
        total_revenue += revenue
        if revenue > max_revenue:
            max_revenue = revenue

        step = {
            "index": i,
            "name": prod["name"],
            "price": prod["price"],
            "type": prod["type"],
            "margin_pct": prod["margin_pct"],
            "active_clients": prod["active_clients"],
            "recurring": prod.get("recurring", False),
            "revenue": revenue,
            "margin_revenue": margin_revenue,
            "conversion_from_previous": prod.get("conversion_from_previous"),
            "gap_to_next_ratio": None,
            "gap_to_next_abs": None,
            "is_cliff": False,
        }

        # Gap to next step
        if i < len(products) - 1:
            next_price = products[i + 1]["price"]
            ratio = next_price / prod["price"] if prod["price"] > 0 else float("inf")
            step["gap_to_next_ratio"] = round(ratio, 2)
            step["gap_to_next_abs"] = next_price - prod["price"]
            step["is_cliff"] = ratio > 3.0
            if ratio > 3.0:
                cliff_count += 1
            total_gaps += 1

        # Ascension rate
        if prod.get("conversion_from_previous") is not None:
            ascension_rates.append(prod["conversion_from_previous"])

        steps.append(step)

    # Health metrics
    non_cliff_gaps = total_gaps - cliff_count
    coverage_score = round((non_cliff_gaps / total_gaps * 100) if total_gaps > 0 else 100, 1)
    revenue_concentration = round((max_revenue / total_revenue * 100) if total_revenue > 0 else 0, 1)
    avg_ascension = round(sum(ascension_rates) / len(ascension_rates), 1) if ascension_rates else 0
    theoretical_ltv = sum(p["price"] for p in products)

    health = {
        "coverage_score": coverage_score,
        "revenue_concentration": revenue_concentration,
        "avg_ascension_rate": avg_ascension,
        "theoretical_ltv": theoretical_ltv,
        "total_revenue": total_revenue,
        "total_margin_revenue": sum(s["margin_revenue"] for s in steps),
        "cliff_count": cliff_count,
        "total_steps": len(steps),
        "total_gaps": total_gaps,
    }

    # Health rating
    if coverage_score >= 80 and revenue_concentration <= 50 and avg_ascension >= 20:
        health["rating"] = "Saudavel"
        health["rating_emoji"] = "green"
    elif coverage_score >= 50 and avg_ascension >= 10:
        health["rating"] = "Atencao"
        health["rating_emoji"] = "yellow"
    else:
        health["rating"] = "Critico"
        health["rating_emoji"] = "red"

    # Recommendations
    recommendations = []
    if cliff_count > 0:
        cliffs = [s for s in steps if s["is_cliff"]]
        for c in cliffs:
            next_step = steps[c["index"] + 1] if c["index"] + 1 < len(steps) else None
            if next_step:
                midpoint = int((c["price"] + next_step["price"]) / 2)
                recommendations.append({
                    "type": "precipicio",
                    "severity": "alta",
                    "message": f"Gap de {c['gap_to_next_ratio']}x entre '{c['name']}' (R${c['price']:,.0f}) e '{next_step['name']}' (R${next_step['price']:,.0f}). Considere produto intermediario ~R${midpoint:,.0f}.",
                })

    if revenue_concentration > 60:
        top_product = max(steps, key=lambda s: s["revenue"])
        recommendations.append({
            "type": "concentracao",
            "severity": "media",
            "message": f"'{top_product['name']}' concentra {revenue_concentration}% da receita. Diversificar para reduzir risco.",
        })

    if avg_ascension < 15 and avg_ascension > 0:
        recommendations.append({
            "type": "ascensao_baixa",
            "severity": "media",
            "message": f"Taxa media de ascensao ({avg_ascension}%) abaixo do benchmark (15-25%). Revisar ofertas de transicao.",
        })

    has_recurring = any(s["recurring"] for s in steps)
    if not has_recurring:
        recommendations.append({
            "type": "sem_recorrencia",
            "severity": "media",
            "message": "Nenhum produto recorrente na escada. Considere adicionar revenue recorrente.",
        })

    return {
        "company_name": company,
        "generated_at": datetime.now().isoformat(),
        "steps": steps,
        "health": health,
        "recommendations": recommendations,
    }


# ---------------------------------------------------------------------------
# HTML Generator
# ---------------------------------------------------------------------------

TYPE_COLORS = {
    "entrada": {"fill": "#22c55e", "bg": "rgba(34,197,94,0.15)", "border": "#22c55e", "label": "Entrada"},
    "core": {"fill": "#3b82f6", "bg": "rgba(59,130,246,0.15)", "border": "#3b82f6", "label": "Core"},
    "premium": {"fill": "#a855f7", "bg": "rgba(168,85,247,0.15)", "border": "#a855f7", "label": "Premium"},
    "super-premium": {"fill": "#f59e0b", "bg": "rgba(245,158,11,0.15)", "border": "#f59e0b", "label": "Super-Premium"},
}

RATING_COLORS = {
    "green": "#22c55e",
    "yellow": "#eab308",
    "red": "#ef4444",
}


def _fmt_brl(value: int | float) -> str:
    """Format a number as R$ Brazilian currency string."""
    if value >= 1_000_000:
        return f"R${value / 1_000_000:,.1f}M"
    if value >= 1_000:
        return f"R${value / 1_000:,.1f}K"
    return f"R${value:,.0f}"


def _fmt_full_brl(value: int | float) -> str:
    """Format with full digits."""
    return f"R${value:,.0f}".replace(",", ".")


def generate_html(analysis: dict) -> str:
    """Generate the interactive HTML visualization."""
    steps = analysis["steps"]
    health = analysis["health"]
    company = escape(analysis["company_name"])
    recommendations = analysis["recommendations"]
    n = len(steps)

    # SVG dimensions
    svg_width = 900
    block_height = 80
    block_gap = 60
    margin_top = 40
    margin_bottom = 40
    margin_left = 60
    margin_right = 60
    svg_height = margin_top + n * block_height + (n - 1) * block_gap + margin_bottom

    # Build SVG blocks (bottom = cheapest, top = most expensive)
    svg_elements = []
    block_positions = []  # (cx, cy) center of each block

    max_price = max(s["price"] for s in steps) if steps else 1

    for i, step in enumerate(steps):
        # i=0 is cheapest → bottom of SVG
        visual_index = n - 1 - i
        y = margin_top + visual_index * (block_height + block_gap)

        # Width proportional to price (min 200, max area width)
        area_width = svg_width - margin_left - margin_right
        min_block_w = 220
        w = max(min_block_w, int(area_width * (step["price"] / max_price) * 0.85 + area_width * 0.15))
        x = margin_left + (area_width - w) // 2

        colors = TYPE_COLORS.get(step["type"], TYPE_COLORS["core"])
        cx = x + w // 2
        cy = y + block_height // 2
        block_positions.append((cx, cy, x, y, w))

        # Recurring badge
        recurring_badge = ""
        if step["recurring"]:
            recurring_badge = f'<text x="{x + w - 12}" y="{y + 18}" font-size="11" fill="#22c55e" text-anchor="end" font-weight="600">RECORRENTE</text>'

        # Tooltip data
        tooltip_lines = [
            f"Produto: {escape(step['name'])}",
            f"Preco: {_fmt_full_brl(step['price'])}",
            f"Tipo: {colors['label']}",
            f"Clientes ativos: {step['active_clients']}",
            f"Receita: {_fmt_full_brl(step['revenue'])}",
            f"Margem: {step['margin_pct']}% ({_fmt_full_brl(step['margin_revenue'])})",
        ]
        if step["conversion_from_previous"] is not None:
            tooltip_lines.append(f"Conversao do step anterior: {step['conversion_from_previous']}%")
        if step["gap_to_next_ratio"] is not None:
            tooltip_lines.append(f"Gap para proximo: {step['gap_to_next_ratio']}x ({_fmt_full_brl(step['gap_to_next_abs'])})")
            if step["is_cliff"]:
                tooltip_lines.append("PRECIPICIO: gap > 3x!")
        tooltip_text = "&#10;".join(tooltip_lines)

        svg_elements.append(f'''
    <g class="ladder-block" data-index="{i}">
      <title>{tooltip_text}</title>
      <rect x="{x}" y="{y}" width="{w}" height="{block_height}" rx="10" ry="10"
            fill="{colors['bg']}" stroke="{colors['border']}" stroke-width="2" />
      <text x="{cx}" y="{y + 28}" text-anchor="middle" fill="#f1f5f9" font-size="16" font-weight="700">
        {escape(step['name'])}
      </text>
      <text x="{cx}" y="{y + 50}" text-anchor="middle" fill="{colors['fill']}" font-size="20" font-weight="800">
        {_fmt_full_brl(step['price'])}
      </text>
      <text x="{x + 12}" y="{y + 70}" fill="#94a3b8" font-size="11">
        {step['active_clients']} clientes | Rev: {_fmt_brl(step['revenue'])}
      </text>
      {recurring_badge}
    </g>''')

    # Connector lines between steps
    for i in range(n - 1):
        # From step i (cheaper) to step i+1 (more expensive)
        _, _, _, y_low, _ = block_positions[i]
        cx_low = block_positions[i][0]
        _, _, _, y_high, _ = block_positions[i + 1]
        cx_high = block_positions[i + 1][0]

        # visual: low block is rendered at bottom, high block above
        # In SVG coords: low block has HIGHER y, high block has LOWER y
        start_y = margin_top + (n - 1 - i) * (block_height + block_gap)
        end_y = margin_top + (n - 1 - (i + 1)) * (block_height + block_gap) + block_height

        step_data = steps[i]
        next_step = steps[i + 1]

        if step_data["is_cliff"]:
            # Red dashed line for cliff
            mid_y = (start_y + end_y) // 2
            svg_elements.append(f'''
    <line x1="{cx_low}" y1="{start_y}" x2="{cx_high}" y2="{end_y}"
          stroke="#ef4444" stroke-width="2" stroke-dasharray="8,4" opacity="0.8" />
    <rect x="{cx_low - 80}" y="{mid_y - 16}" width="160" height="32" rx="6"
          fill="rgba(239,68,68,0.15)" stroke="#ef4444" stroke-width="1" stroke-dasharray="4,3" />
    <text x="{cx_low}" y="{mid_y + 4}" text-anchor="middle" fill="#ef4444" font-size="12" font-weight="700">
      PRECIPICIO {step_data['gap_to_next_ratio']}x
    </text>''')
        else:
            # Normal connector
            svg_elements.append(f'''
    <line x1="{cx_low}" y1="{start_y}" x2="{cx_high}" y2="{end_y}"
          stroke="#475569" stroke-width="2" opacity="0.6" />''')

        # Conversion label
        if next_step["conversion_from_previous"] is not None:
            mid_y = (start_y + end_y) // 2
            label_x = min(block_positions[i][0], block_positions[i + 1][0]) - 60
            svg_elements.append(f'''
    <text x="{label_x}" y="{mid_y + 4}" text-anchor="end" fill="#94a3b8" font-size="12" font-weight="600">
      {next_step['conversion_from_previous']}%
    </text>
    <text x="{label_x}" y="{mid_y + 18}" text-anchor="end" fill="#64748b" font-size="10">
      conversao
    </text>''')

    svg_content = "\n".join(svg_elements)

    # Health card color
    rating_color = RATING_COLORS.get(health["rating_emoji"], "#94a3b8")

    # Recommendations HTML
    rec_html = ""
    if recommendations:
        rec_items = []
        for rec in recommendations:
            severity_color = {"alta": "#ef4444", "media": "#eab308", "baixa": "#22c55e"}.get(rec["severity"], "#94a3b8")
            rec_items.append(f'''
          <div class="rec-item">
            <span class="rec-severity" style="background:{severity_color}20;color:{severity_color};border:1px solid {severity_color}40">
              {escape(rec['severity'].upper())}
            </span>
            <span class="rec-msg">{escape(rec['message'])}</span>
          </div>''')
        rec_html = f'''
      <div class="card">
        <h2>Recomendacoes</h2>
        {"".join(rec_items)}
      </div>'''

    html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Value Ladder — {company}</title>
<style>
  :root {{
    --bg: #0f1117;
    --surface: #1a1d27;
    --surface2: #232736;
    --border: #2d3148;
    --text: #f1f5f9;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --green: #22c55e;
    --blue: #3b82f6;
    --purple: #a855f7;
    --gold: #f59e0b;
    --red: #ef4444;
    --yellow: #eab308;
  }}

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    line-height: 1.6;
    padding: 24px;
  }}

  .container {{
    max-width: 1000px;
    margin: 0 auto;
  }}

  header {{
    text-align: center;
    margin-bottom: 32px;
    padding-bottom: 24px;
    border-bottom: 1px solid var(--border);
  }}

  header h1 {{
    font-size: 28px;
    font-weight: 800;
    margin-bottom: 4px;
  }}

  header .subtitle {{
    color: var(--text-secondary);
    font-size: 14px;
  }}

  .metrics-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
    margin-bottom: 32px;
  }}

  .metric-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
  }}

  .metric-card .metric-value {{
    font-size: 28px;
    font-weight: 800;
    margin-bottom: 4px;
  }}

  .metric-card .metric-label {{
    font-size: 12px;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}

  .card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 24px;
  }}

  .card h2 {{
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 16px;
    color: var(--text);
  }}

  .ladder-svg {{
    display: block;
    margin: 0 auto;
    width: 100%;
    max-width: {svg_width}px;
  }}

  .ladder-block {{
    cursor: pointer;
    transition: opacity 0.2s;
  }}

  .ladder-block:hover {{
    opacity: 0.85;
  }}

  .ladder-block:hover rect {{
    stroke-width: 3;
    filter: drop-shadow(0 0 8px rgba(255,255,255,0.1));
  }}

  .rec-item {{
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 12px 0;
    border-bottom: 1px solid var(--border);
  }}

  .rec-item:last-child {{
    border-bottom: none;
    padding-bottom: 0;
  }}

  .rec-severity {{
    font-size: 10px;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 4px;
    white-space: nowrap;
    flex-shrink: 0;
    margin-top: 2px;
  }}

  .rec-msg {{
    font-size: 14px;
    color: var(--text-secondary);
    line-height: 1.5;
  }}

  .table-wrapper {{
    overflow-x: auto;
  }}

  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
  }}

  th {{
    text-align: left;
    padding: 10px 12px;
    border-bottom: 2px solid var(--border);
    color: var(--text-secondary);
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
  }}

  td {{
    padding: 10px 12px;
    border-bottom: 1px solid var(--border);
    color: var(--text);
  }}

  tr:hover td {{
    background: var(--surface2);
  }}

  .type-badge {{
    display: inline-block;
    font-size: 10px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 4px;
    text-transform: uppercase;
  }}

  .cliff-badge {{
    color: var(--red);
    font-weight: 700;
  }}

  .rating-badge {{
    display: inline-block;
    padding: 4px 14px;
    border-radius: 6px;
    font-weight: 700;
    font-size: 14px;
  }}

  footer {{
    text-align: center;
    padding-top: 24px;
    margin-top: 16px;
    border-top: 1px solid var(--border);
    color: var(--text-muted);
    font-size: 12px;
  }}
</style>
</head>
<body>
<div class="container">

  <header>
    <h1>Value Ladder</h1>
    <div class="subtitle">{company} &mdash; Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
  </header>

  <!-- Health Metrics -->
  <div class="metrics-grid">
    <div class="metric-card">
      <div class="metric-value" style="color:{rating_color}">{health['coverage_score']}%</div>
      <div class="metric-label">Coverage Score</div>
    </div>
    <div class="metric-card">
      <div class="metric-value" style="color:{'var(--green)' if health['revenue_concentration'] <= 50 else 'var(--yellow)' if health['revenue_concentration'] <= 70 else 'var(--red)'}">{health['revenue_concentration']}%</div>
      <div class="metric-label">Concentracao Receita</div>
    </div>
    <div class="metric-card">
      <div class="metric-value" style="color:var(--blue)">{health['avg_ascension_rate']}%</div>
      <div class="metric-label">Ascensao Media</div>
    </div>
    <div class="metric-card">
      <div class="metric-value" style="color:var(--gold)">{_fmt_full_brl(health['theoretical_ltv'])}</div>
      <div class="metric-label">LTV Teorico</div>
    </div>
    <div class="metric-card">
      <div class="metric-value" style="color:var(--text)">{_fmt_brl(health['total_revenue'])}</div>
      <div class="metric-label">Receita Total</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">
        <span class="rating-badge" style="background:{rating_color}20;color:{rating_color};border:1px solid {rating_color}40">{health['rating']}</span>
      </div>
      <div class="metric-label">Rating</div>
    </div>
  </div>

  <!-- Ladder Visualization -->
  <div class="card">
    <h2>Escada de Valor</h2>
    <svg class="ladder-svg" viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <filter id="glow">
          <feGaussianBlur stdDeviation="2" result="blur" />
          <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
      </defs>
      {svg_content}
    </svg>
  </div>

  <!-- Detail Table -->
  <div class="card">
    <h2>Detalhamento por Step</h2>
    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Step</th>
            <th>Produto</th>
            <th>Tipo</th>
            <th>Preco</th>
            <th>Clientes</th>
            <th>Receita</th>
            <th>Margem</th>
            <th>Conversao</th>
            <th>Gap</th>
          </tr>
        </thead>
        <tbody>'''

    for i, step in enumerate(steps):
        colors = TYPE_COLORS.get(step["type"], TYPE_COLORS["core"])
        conv_str = f"{step['conversion_from_previous']}%" if step["conversion_from_previous"] is not None else "&mdash;"
        gap_str = ""
        if step["gap_to_next_ratio"] is not None:
            if step["is_cliff"]:
                gap_str = f'<span class="cliff-badge">{step["gap_to_next_ratio"]}x PRECIPICIO</span>'
            else:
                gap_str = f'{step["gap_to_next_ratio"]}x'
        else:
            gap_str = "&mdash;"

        recurring_marker = ' <span style="color:var(--green);font-size:10px;font-weight:700">REC</span>' if step["recurring"] else ""

        html += f'''
          <tr>
            <td>{i + 1}</td>
            <td>{escape(step['name'])}{recurring_marker}</td>
            <td><span class="type-badge" style="background:{colors['bg']};color:{colors['fill']};border:1px solid {colors['border']}40">{colors['label']}</span></td>
            <td>{_fmt_full_brl(step['price'])}</td>
            <td>{step['active_clients']}</td>
            <td>{_fmt_full_brl(step['revenue'])}</td>
            <td>{step['margin_pct']}%</td>
            <td>{conv_str}</td>
            <td>{gap_str}</td>
          </tr>'''

    html += f'''
        </tbody>
      </table>
    </div>
  </div>

  {rec_html}

  <footer>
    Value Ladder Analysis &mdash; G4 OS &mdash; {datetime.now().strftime('%Y')}
  </footer>

</div>
</body>
</html>'''

    return html


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Value Ladder Visualization & Analysis"
    )
    parser.add_argument(
        "--input-json",
        required=True,
        help="JSON string with company_name and products array",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory to write output files",
    )
    args = parser.parse_args()

    # Parse input
    try:
        data = json.loads(args.input_json)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON input: {e}"}))
        sys.exit(1)

    # Validate
    if "products" not in data or not data["products"]:
        print(json.dumps({"error": "Input must contain a non-empty 'products' array"}))
        sys.exit(1)

    if "company_name" not in data:
        data["company_name"] = "Empresa"

    # Analyze
    analysis = analyze_value_ladder(data)

    # Ensure output dir exists
    os.makedirs(args.output_dir, exist_ok=True)

    # Write analysis JSON
    analysis_path = os.path.join(args.output_dir, "value_ladder_analysis.json")
    with open(analysis_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    # Generate and write HTML
    html = generate_html(analysis)
    html_path = os.path.join(args.output_dir, "value_ladder.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    # Print summary to stdout for LLM consumption
    summary = {
        "status": "success",
        "company": analysis["company_name"],
        "steps_count": len(analysis["steps"]),
        "health": analysis["health"],
        "recommendations_count": len(analysis["recommendations"]),
        "recommendations": [r["message"] for r in analysis["recommendations"]],
        "steps_summary": [
            {
                "name": s["name"],
                "price": s["price"],
                "type": s["type"],
                "revenue": s["revenue"],
                "active_clients": s["active_clients"],
                "gap_to_next": f"{s['gap_to_next_ratio']}x" if s["gap_to_next_ratio"] else None,
                "is_cliff": s["is_cliff"],
                "conversion_from_previous": s["conversion_from_previous"],
            }
            for s in analysis["steps"]
        ],
        "output_files": {
            "html": html_path,
            "analysis_json": analysis_path,
        },
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
