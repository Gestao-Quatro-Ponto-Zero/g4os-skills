#!/usr/bin/env python3
"""
Channel Matrix — Priorizacao de Canais 2x2
Framework: Alfredo Soares (Ecossistema de Vendas, G4 GE 2026)

Gera matriz interativa de canais plotados em Validacao x Potencial de Receita.
"""

import json
import argparse
import os
from datetime import datetime


def classify_quadrant(validation, potential):
    """Classifica canal no quadrante baseado nos scores."""
    if validation >= 6 and potential >= 6:
        return "ESCALAR"
    elif validation < 6 and potential >= 6:
        return "APOSTAR"
    elif validation >= 6 and potential < 6:
        return "MANTER"
    else:
        return "EXPLORAR"


def calculate_ideal_budget(channels, total_budget):
    """Calcula budget ideal por canal baseado no quadrante."""
    quadrant_targets = {
        "ESCALAR": 0.70,
        "APOSTAR": 0.20,
        "MANTER": 0.0,  # Residual do que sobrar
        "EXPLORAR": 0.10,
    }

    # Group channels by quadrant
    quadrants = {}
    for ch in channels:
        q = ch["quadrant"]
        if q not in quadrants:
            quadrants[q] = []
        quadrants[q].append(ch)

    # Calculate ideal budget per quadrant
    quadrant_budgets = {}
    for q, target_pct in quadrant_targets.items():
        quadrant_budgets[q] = total_budget * target_pct

    # MANTER gets whatever is left (should be ~0 but handles edge cases)
    used = sum(v for k, v in quadrant_budgets.items() if k != "MANTER")
    quadrant_budgets["MANTER"] = max(0, total_budget - used)

    # Distribute within each quadrant
    for ch in channels:
        q = ch["quadrant"]
        q_channels = quadrants.get(q, [])
        if len(q_channels) == 0:
            ch["ideal_budget_pct"] = 0
            ch["ideal_budget"] = 0
            continue

        # Weight by LTV:CAC if available, otherwise equal
        if q == "ESCALAR" and any(c.get("ltv_cac") for c in q_channels):
            total_ltv = sum(c.get("ltv_cac", 1) or 1 for c in q_channels)
            weight = (ch.get("ltv_cac", 1) or 1) / total_ltv
        else:
            weight = 1 / len(q_channels)

        ch["ideal_budget"] = quadrant_budgets[q] * weight
        ch["ideal_budget_pct"] = (ch["ideal_budget"] / total_budget * 100) if total_budget > 0 else 0

    return channels


def analyze(data):
    """Run full channel matrix analysis."""
    channels = data["channels"]
    total_budget = data.get("monthly_budget", 0)

    # Calculate current budget percentages
    total_current = sum(ch.get("current_budget_pct", 0) for ch in channels)

    # Classify quadrants
    for ch in channels:
        ch["quadrant"] = classify_quadrant(ch["validation"], ch["potential"])
        ch["current_budget"] = total_budget * ch.get("current_budget_pct", 0) / 100

    # Calculate ideal budgets
    channels = calculate_ideal_budget(channels, total_budget)

    # Calculate deltas
    for ch in channels:
        ch["delta_pct"] = ch["ideal_budget_pct"] - ch.get("current_budget_pct", 0)
        ch["delta_abs"] = ch["ideal_budget"] - ch["current_budget"]

    # Summary stats
    quadrant_summary = {}
    for q in ["ESCALAR", "APOSTAR", "MANTER", "EXPLORAR"]:
        q_channels = [ch for ch in channels if ch["quadrant"] == q]
        quadrant_summary[q] = {
            "count": len(q_channels),
            "current_budget_pct": sum(ch.get("current_budget_pct", 0) for ch in q_channels),
            "ideal_budget_pct": sum(ch.get("ideal_budget_pct", 0) for ch in q_channels),
            "channels": [ch["name"] for ch in q_channels],
        }

    validated_channels = [ch for ch in channels if ch.get("ltv_cac")]
    avg_ltv_cac = (
        sum(ch["ltv_cac"] for ch in validated_channels) / len(validated_channels)
        if validated_channels else None
    )

    unvalidated_budget = sum(
        ch.get("current_budget_pct", 0) for ch in channels if ch["validation"] < 6
    )

    return {
        "company_name": data.get("company_name", ""),
        "industry": data.get("industry", ""),
        "monthly_budget": total_budget,
        "total_channels": len(channels),
        "avg_ltv_cac_validated": round(avg_ltv_cac, 1) if avg_ltv_cac else None,
        "unvalidated_budget_pct": round(unvalidated_budget, 1),
        "quadrant_summary": quadrant_summary,
        "channels": channels,
        "generated_at": datetime.now().isoformat(),
    }


def generate_html(result, output_path):
    """Generate interactive HTML matrix visualization."""
    channels = result["channels"]
    company = result["company_name"] or "Sua Empresa"

    # Build channel data for JS
    channel_js = json.dumps([{
        "name": ch["name"],
        "x": ch["validation"],
        "y": ch["potential"],
        "budget_pct": ch.get("current_budget_pct", 0),
        "ideal_pct": round(ch.get("ideal_budget_pct", 0), 1),
        "quadrant": ch["quadrant"],
        "ltv_cac": ch.get("ltv_cac"),
        "cycle_days": ch.get("cycle_days"),
        "notes": ch.get("notes", ""),
        "delta_pct": round(ch.get("delta_pct", 0), 1),
    } for ch in channels], ensure_ascii=False)

    quadrant_colors = {
        "ESCALAR": "#22c55e",
        "APOSTAR": "#3b82f6",
        "MANTER": "#eab308",
        "EXPLORAR": "#6b7280",
    }

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Matriz de Canais — {company}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; padding: 24px; }}
.header {{ text-align: center; margin-bottom: 32px; }}
.header h1 {{ font-size: 24px; font-weight: 700; color: #f8fafc; }}
.header p {{ color: #94a3b8; margin-top: 4px; font-size: 14px; }}
.matrix-container {{ position: relative; width: 100%; max-width: 700px; height: 700px; margin: 0 auto; background: #1e293b; border-radius: 12px; overflow: hidden; }}
.quadrant {{ position: absolute; width: 50%; height: 50%; display: flex; align-items: flex-start; justify-content: flex-start; padding: 12px; }}
.quadrant-label {{ font-size: 13px; font-weight: 600; opacity: 0.6; text-transform: uppercase; letter-spacing: 0.5px; }}
.q-escalar {{ top: 0; right: 0; background: rgba(34,197,94,0.08); border-left: 1px solid rgba(255,255,255,0.05); border-bottom: 1px solid rgba(255,255,255,0.05); }}
.q-escalar .quadrant-label {{ color: #22c55e; }}
.q-apostar {{ top: 0; left: 0; background: rgba(59,130,246,0.08); border-right: 1px solid rgba(255,255,255,0.05); border-bottom: 1px solid rgba(255,255,255,0.05); }}
.q-apostar .quadrant-label {{ color: #3b82f6; }}
.q-manter {{ bottom: 0; right: 0; background: rgba(234,179,8,0.08); border-left: 1px solid rgba(255,255,255,0.05); border-top: 1px solid rgba(255,255,255,0.05); }}
.q-manter .quadrant-label {{ color: #eab308; }}
.q-explorar {{ bottom: 0; left: 0; background: rgba(107,114,128,0.08); border-right: 1px solid rgba(255,255,255,0.05); border-top: 1px solid rgba(255,255,255,0.05); }}
.q-explorar .quadrant-label {{ color: #6b7280; }}
.axis-label {{ position: absolute; font-size: 12px; color: #64748b; font-weight: 500; }}
.axis-x {{ bottom: -24px; left: 50%; transform: translateX(-50%); }}
.axis-y {{ top: 50%; left: -60px; transform: rotate(-90deg); white-space: nowrap; }}
.bubble {{ position: absolute; border-radius: 50%; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: 600; color: #fff; text-align: center; line-height: 1.1; }}
.bubble:hover {{ transform: scale(1.15); box-shadow: 0 0 20px rgba(255,255,255,0.2); z-index: 100; }}
.tooltip {{ display: none; position: fixed; background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 12px 16px; font-size: 13px; z-index: 1000; min-width: 220px; box-shadow: 0 8px 32px rgba(0,0,0,0.4); pointer-events: none; }}
.tooltip.show {{ display: block; }}
.tooltip h3 {{ font-size: 15px; font-weight: 600; margin-bottom: 8px; }}
.tooltip .row {{ display: flex; justify-content: space-between; margin: 3px 0; }}
.tooltip .label {{ color: #94a3b8; }}
.tooltip .value {{ font-weight: 600; }}
.tooltip .notes {{ color: #94a3b8; font-style: italic; margin-top: 6px; font-size: 12px; border-top: 1px solid #334155; padding-top: 6px; }}
.legend {{ display: flex; gap: 24px; justify-content: center; margin-top: 40px; flex-wrap: wrap; }}
.legend-item {{ display: flex; align-items: center; gap: 6px; font-size: 13px; color: #94a3b8; }}
.legend-dot {{ width: 12px; height: 12px; border-radius: 50%; }}
.summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-top: 32px; max-width: 700px; margin-left: auto; margin-right: auto; }}
.summary-card {{ background: #1e293b; border-radius: 8px; padding: 16px; }}
.summary-card .sq-label {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }}
.summary-card .sq-value {{ font-size: 28px; font-weight: 700; margin-top: 4px; }}
.summary-card .sq-detail {{ font-size: 12px; color: #64748b; margin-top: 4px; }}
.footer {{ text-align: center; margin-top: 40px; font-size: 12px; color: #475569; }}
</style>
</head>
<body>
<div class="header">
  <h1>Matriz de Canais — {company}</h1>
  <p>Framework Alfredo Soares | Validacao x Potencial de Receita</p>
</div>

<div style="position: relative; max-width: 700px; margin: 0 auto;">
  <div class="axis-label axis-x">Validacao →</div>
  <div class="matrix-container" id="matrix">
    <div class="quadrant q-apostar"><span class="quadrant-label">Apostar (20%)</span></div>
    <div class="quadrant q-escalar"><span class="quadrant-label">Escalar (70%)</span></div>
    <div class="quadrant q-explorar"><span class="quadrant-label">Explorar (10%)</span></div>
    <div class="quadrant q-manter"><span class="quadrant-label">Manter</span></div>
  </div>
</div>

<div class="legend">
  <div class="legend-item"><div class="legend-dot" style="background:#22c55e"></div> Escalar</div>
  <div class="legend-item"><div class="legend-dot" style="background:#3b82f6"></div> Apostar</div>
  <div class="legend-item"><div class="legend-dot" style="background:#eab308"></div> Manter</div>
  <div class="legend-item"><div class="legend-dot" style="background:#6b7280"></div> Explorar</div>
  <div class="legend-item" style="color:#64748b">Tamanho = % do budget</div>
</div>

<div class="summary" id="summary"></div>

<div class="footer">
  Gerado por G4 OS | {datetime.now().strftime('%d/%m/%Y %H:%M')}
</div>

<div class="tooltip" id="tooltip"></div>

<script>
const channels = {channel_js};
const colors = {json.dumps(quadrant_colors)};
const matrix = document.getElementById('matrix');
const tooltip = document.getElementById('tooltip');

channels.forEach(ch => {{
  const bubble = document.createElement('div');
  bubble.className = 'bubble';

  const size = Math.max(28, Math.min(70, 20 + ch.budget_pct * 1.5));
  const x = (ch.x / 10) * 90 + 5;
  const y = (1 - ch.y / 10) * 90 + 5;

  bubble.style.width = size + 'px';
  bubble.style.height = size + 'px';
  bubble.style.left = `calc(${{x}}% - ${{size/2}}px)`;
  bubble.style.top = `calc(${{y}}% - ${{size/2}}px)`;
  bubble.style.background = colors[ch.quadrant];
  bubble.style.opacity = '0.85';

  const shortName = ch.name.length > 8 ? ch.name.substring(0, 7) + '...' : ch.name;
  if (size >= 40) bubble.textContent = shortName;

  bubble.addEventListener('mouseenter', (e) => {{
    const rect = e.target.getBoundingClientRect();
    let html = `<h3 style="color:${{colors[ch.quadrant]}}">${{ch.name}}</h3>`;
    html += `<div class="row"><span class="label">Quadrante</span><span class="value">${{ch.quadrant}}</span></div>`;
    html += `<div class="row"><span class="label">Validacao</span><span class="value">${{ch.x}}/10</span></div>`;
    html += `<div class="row"><span class="label">Potencial</span><span class="value">${{ch.y}}/10</span></div>`;
    html += `<div class="row"><span class="label">Budget Atual</span><span class="value">${{ch.budget_pct}}%</span></div>`;
    html += `<div class="row"><span class="label">Budget Ideal</span><span class="value">${{ch.ideal_pct}}%</span></div>`;
    const delta = ch.delta_pct > 0 ? `+${{ch.delta_pct}}pp` : `${{ch.delta_pct}}pp`;
    const dc = ch.delta_pct > 0 ? '#22c55e' : ch.delta_pct < 0 ? '#ef4444' : '#94a3b8';
    html += `<div class="row"><span class="label">Delta</span><span class="value" style="color:${{dc}}">${{delta}}</span></div>`;
    if (ch.ltv_cac) html += `<div class="row"><span class="label">LTV:CAC</span><span class="value">${{ch.ltv_cac}}x</span></div>`;
    if (ch.cycle_days) html += `<div class="row"><span class="label">Ciclo</span><span class="value">${{ch.cycle_days}} dias</span></div>`;
    if (ch.notes) html += `<div class="notes">${{ch.notes}}</div>`;

    tooltip.innerHTML = html;
    tooltip.classList.add('show');
    tooltip.style.left = (rect.right + 12) + 'px';
    tooltip.style.top = rect.top + 'px';

    if (rect.right + 240 > window.innerWidth) {{
      tooltip.style.left = (rect.left - 240) + 'px';
    }}
  }});

  bubble.addEventListener('mouseleave', () => {{
    tooltip.classList.remove('show');
  }});

  matrix.appendChild(bubble);
}});

// Summary cards
const quadrants = {{}};
channels.forEach(ch => {{
  if (!quadrants[ch.quadrant]) quadrants[ch.quadrant] = {{ channels: [], budget: 0 }};
  quadrants[ch.quadrant].channels.push(ch.name);
  quadrants[ch.quadrant].budget += ch.budget_pct;
}});

const summaryEl = document.getElementById('summary');
['ESCALAR', 'APOSTAR', 'MANTER', 'EXPLORAR'].forEach(q => {{
  const d = quadrants[q] || {{ channels: [], budget: 0 }};
  const card = document.createElement('div');
  card.className = 'summary-card';
  card.innerHTML = `
    <div class="sq-label" style="color:${{colors[q]}}">${{q}}</div>
    <div class="sq-value" style="color:${{colors[q]}}">${{d.channels.length}} canais</div>
    <div class="sq-detail">${{Math.round(d.budget)}}% do budget atual</div>
    <div class="sq-detail">${{d.channels.join(', ')}}</div>
  `;
  summaryEl.appendChild(card);
}});
</script>
</body>
</html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)


def main():
    parser = argparse.ArgumentParser(description='Channel Matrix Analysis')
    parser.add_argument('--input-json', required=True, help='JSON string with channel data')
    parser.add_argument('--output-dir', required=True, help='Output directory')
    args = parser.parse_args()

    data = json.loads(args.input_json)
    os.makedirs(args.output_dir, exist_ok=True)

    result = analyze(data)

    # Save analysis JSON
    json_path = os.path.join(args.output_dir, 'channel_analysis.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Generate HTML
    html_path = os.path.join(args.output_dir, 'channel_matrix.html')
    generate_html(result, html_path)

    # Print summary to stdout
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
