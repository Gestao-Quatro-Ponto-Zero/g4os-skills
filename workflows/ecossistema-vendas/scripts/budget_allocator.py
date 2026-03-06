#!/usr/bin/env python3
"""
Budget 70/20/10 Allocator
Framework: Alfredo Soares (Ecossistema de Vendas, G4 GE 2026)

Analisa alocacao atual de budget vs regra 70/20/10 e gera plano de realocacao.
"""

import json
import argparse
import os
from datetime import datetime


def analyze(data):
    """Run full budget allocation analysis."""
    channels = data["channels"]
    total_budget = data.get("monthly_budget", 0)
    currency = data.get("currency", "BRL")

    # Compute current totals per category
    categories = {"escala": [], "aceleracao": [], "descoberta": []}
    for ch in channels:
        cat = ch.get("category", "descoberta").lower()
        if cat not in categories:
            cat = "descoberta"
        ch["category_normalized"] = cat
        ch["budget_pct"] = (ch["budget"] / total_budget * 100) if total_budget > 0 else 0
        categories[cat].append(ch)

    # Current split
    current_split = {}
    for cat, chs in categories.items():
        total = sum(ch["budget"] for ch in chs)
        current_split[cat] = {
            "total": total,
            "pct": round(total / total_budget * 100, 1) if total_budget > 0 else 0,
            "count": len(chs),
        }

    # Ideal split
    ideal_pcts = {"escala": 70, "aceleracao": 20, "descoberta": 10}
    ideal_split = {}
    for cat, pct in ideal_pcts.items():
        ideal_split[cat] = {
            "total": total_budget * pct / 100,
            "pct": pct,
        }

    # Gap analysis
    gaps = {}
    for cat in ideal_pcts:
        current = current_split.get(cat, {"total": 0, "pct": 0})
        ideal = ideal_split[cat]
        gaps[cat] = {
            "delta_abs": ideal["total"] - current["total"],
            "delta_pct": round(ideal["pct"] - current["pct"], 1),
        }

    # Calculate ideal budget per channel
    for ch in channels:
        cat = ch["category_normalized"]
        cat_channels = categories[cat]
        cat_ideal_total = ideal_split[cat]["total"]

        # Weight by LTV:CAC for escala, equal for others
        if cat == "escala" and any(c.get("ltv_cac") for c in cat_channels):
            total_weight = sum(c.get("ltv_cac", 1) or 1 for c in cat_channels)
            weight = (ch.get("ltv_cac", 1) or 1) / total_weight
        else:
            weight = 1 / len(cat_channels) if cat_channels else 0

        ch["ideal_budget"] = round(cat_ideal_total * weight)
        ch["ideal_pct"] = round(ch["ideal_budget"] / total_budget * 100, 1) if total_budget > 0 else 0
        ch["delta"] = ch["ideal_budget"] - ch["budget"]
        ch["delta_pct"] = round(ch["ideal_pct"] - ch["budget_pct"], 1)

    # Sub-allocation for ESCALA (60/30/10: midia/equipe/ferramentas)
    escala_total = ideal_split["escala"]["total"]
    sub_escala = {
        "midia": {"pct": 60, "value": round(escala_total * 0.60)},
        "equipe": {"pct": 30, "value": round(escala_total * 0.30)},
        "ferramentas": {"pct": 10, "value": round(escala_total * 0.10)},
    }

    # Sub-allocation for ACELERACAO (90/5/5)
    accel_total = ideal_split["aceleracao"]["total"]
    sub_accel = {
        "midia": {"pct": 90, "value": round(accel_total * 0.90)},
        "equipe": {"pct": 5, "value": round(accel_total * 0.05)},
        "ferramentas": {"pct": 5, "value": round(accel_total * 0.05)},
    }

    # Risk metrics
    unvalidated_budget = sum(ch["budget"] for ch in channels if not ch.get("roi_confirmed", False))
    unvalidated_pct = round(unvalidated_budget / total_budget * 100, 1) if total_budget > 0 else 0

    validated_channels = [ch for ch in channels if ch.get("ltv_cac")]
    if validated_channels:
        weighted_ltv_cac = sum(ch["ltv_cac"] * ch["budget"] for ch in validated_channels) / sum(ch["budget"] for ch in validated_channels)
    else:
        weighted_ltv_cac = None

    top2_budget = sorted(channels, key=lambda x: x["budget"], reverse=True)[:2]
    concentration = sum(ch["budget_pct"] for ch in top2_budget)

    # Channels to increase, decrease, maintain
    increase = sorted([ch for ch in channels if ch["delta"] > 5000], key=lambda x: x["delta"], reverse=True)
    decrease = sorted([ch for ch in channels if ch["delta"] < -5000], key=lambda x: x["delta"])
    maintain = [ch for ch in channels if abs(ch["delta"]) <= 5000]

    return {
        "company_name": data.get("company_name", ""),
        "industry": data.get("industry", ""),
        "monthly_budget": total_budget,
        "currency": currency,
        "total_channels": len(channels),
        "current_split": current_split,
        "ideal_split": ideal_split,
        "gaps": gaps,
        "sub_allocation_escala": sub_escala,
        "sub_allocation_aceleracao": sub_accel,
        "risk_metrics": {
            "unvalidated_budget_pct": unvalidated_pct,
            "weighted_ltv_cac": round(weighted_ltv_cac, 1) if weighted_ltv_cac else None,
            "top2_concentration_pct": round(concentration, 1),
        },
        "channels": channels,
        "reallocation": {
            "increase": [{"name": ch["name"], "delta": ch["delta"], "from": ch["budget"], "to": ch["ideal_budget"]} for ch in increase],
            "decrease": [{"name": ch["name"], "delta": ch["delta"], "from": ch["budget"], "to": ch["ideal_budget"]} for ch in decrease],
            "maintain": [{"name": ch["name"]} for ch in maintain],
        },
        "generated_at": datetime.now().isoformat(),
    }


def fmt_currency(value, currency="BRL"):
    """Format currency value."""
    if currency == "BRL":
        if abs(value) >= 1_000_000:
            return f"R${value/1_000_000:.1f}M"
        elif abs(value) >= 1_000:
            return f"R${value/1_000:.0f}K"
        return f"R${value:,.0f}"
    return f"${value:,.0f}"


def generate_html(result, output_path):
    """Generate interactive HTML budget report."""
    channels = result["channels"]
    company = result["company_name"] or "Sua Empresa"
    currency = result["currency"]
    budget = result["monthly_budget"]
    current = result["current_split"]
    ideal = result["ideal_split"]

    cat_colors = {"escala": "#22c55e", "aceleracao": "#3b82f6", "descoberta": "#eab308"}
    cat_labels = {"escala": "Escala", "aceleracao": "Aceleracao", "descoberta": "Descoberta"}

    channels_js = json.dumps([{
        "name": ch["name"],
        "category": ch["category_normalized"],
        "budget": ch["budget"],
        "budget_pct": round(ch["budget_pct"], 1),
        "ideal": ch["ideal_budget"],
        "ideal_pct": ch["ideal_pct"],
        "delta": ch["delta"],
        "roi": ch.get("roi_confirmed", False),
        "ltv_cac": ch.get("ltv_cac"),
    } for ch in channels], ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Budget 70/20/10 — {company}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; padding: 24px; }}
.header {{ text-align: center; margin-bottom: 32px; }}
.header h1 {{ font-size: 24px; font-weight: 700; }}
.header p {{ color: #94a3b8; margin-top: 4px; font-size: 14px; }}
.section {{ max-width: 800px; margin: 0 auto 32px; }}
.section h2 {{ font-size: 18px; font-weight: 600; margin-bottom: 16px; color: #f8fafc; }}
.bars-container {{ display: flex; flex-direction: column; gap: 16px; }}
.bar-group {{ }}
.bar-label {{ font-size: 13px; color: #94a3b8; margin-bottom: 6px; display: flex; justify-content: space-between; }}
.bar-track {{ height: 32px; background: #1e293b; border-radius: 6px; overflow: hidden; position: relative; }}
.bar-fill {{ height: 100%; border-radius: 6px; display: flex; align-items: center; padding-left: 10px; font-size: 13px; font-weight: 600; transition: width 0.8s ease; }}
.comparison {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 24px; }}
.comp-col {{ background: #1e293b; border-radius: 10px; padding: 20px; }}
.comp-col h3 {{ font-size: 14px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 16px; }}
.channel-row {{ display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #334155; }}
.channel-row:last-child {{ border-bottom: none; }}
.ch-name {{ font-size: 14px; }}
.ch-value {{ font-size: 14px; font-weight: 600; }}
.ch-delta {{ font-size: 12px; padding: 2px 8px; border-radius: 4px; }}
.ch-delta.positive {{ background: rgba(34,197,94,0.15); color: #22c55e; }}
.ch-delta.negative {{ background: rgba(239,68,68,0.15); color: #ef4444; }}
.ch-delta.neutral {{ background: rgba(148,163,184,0.1); color: #94a3b8; }}
.metrics {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 32px; }}
.metric-card {{ background: #1e293b; border-radius: 8px; padding: 16px; text-align: center; }}
.metric-label {{ font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }}
.metric-value {{ font-size: 28px; font-weight: 700; margin-top: 4px; }}
.metric-sub {{ font-size: 12px; color: #64748b; margin-top: 2px; }}
.footer {{ text-align: center; margin-top: 40px; font-size: 12px; color: #475569; }}
</style>
</head>
<body>
<div class="header">
  <h1>Budget 70/20/10 — {company}</h1>
  <p>Framework Alfredo Soares | Alocacao: Escala / Aceleracao / Descoberta</p>
</div>

<div class="section">
  <div class="metrics" id="metrics"></div>
</div>

<div class="section">
  <h2>Alocacao Atual vs Ideal</h2>
  <div class="bars-container" id="bars"></div>
</div>

<div class="section">
  <h2>Plano de Realocacao por Canal</h2>
  <div class="comparison" id="reallocation"></div>
</div>

<div class="footer">
  Gerado por G4 OS | {datetime.now().strftime('%d/%m/%Y %H:%M')}
</div>

<script>
const channels = {channels_js};
const budget = {budget};
const colors = {json.dumps(cat_colors)};
const labels = {json.dumps(cat_labels)};
const current = {json.dumps({k: v["pct"] for k, v in current.items()})};
const ideal = {json.dumps({k: v["pct"] for k, v in ideal.items()})};

function fmtK(v) {{
  if (Math.abs(v) >= 1000000) return 'R$' + (v/1000000).toFixed(1) + 'M';
  if (Math.abs(v) >= 1000) return 'R$' + Math.round(v/1000) + 'K';
  return 'R$' + v.toLocaleString('pt-BR');
}}

// Metrics
const metricsEl = document.getElementById('metrics');
const totalBudgetFormatted = fmtK(budget);
const currentSplit = `${{current.escala || 0}}% / ${{current.aceleracao || 0}}% / ${{current.descoberta || 0}}%`;
const gapTotal = Math.abs((current.escala||0) - 70) + Math.abs((current.aceleracao||0) - 20) + Math.abs((current.descoberta||0) - 10);

[
  {{ label: 'Budget Total', value: totalBudgetFormatted, sub: '/mes', color: '#f8fafc' }},
  {{ label: 'Split Atual', value: currentSplit, sub: 'E / A / D', color: '#94a3b8' }},
  {{ label: 'Desvio Total', value: gapTotal.toFixed(0) + 'pp', sub: 'soma dos gaps', color: gapTotal > 15 ? '#ef4444' : '#eab308' }},
].forEach(m => {{
  const card = document.createElement('div');
  card.className = 'metric-card';
  card.innerHTML = `<div class="metric-label">${{m.label}}</div><div class="metric-value" style="color:${{m.color}}">${{m.value}}</div><div class="metric-sub">${{m.sub}}</div>`;
  metricsEl.appendChild(card);
}});

// Bars
const barsEl = document.getElementById('bars');
['escala', 'aceleracao', 'descoberta'].forEach(cat => {{
  const c = current[cat] || 0;
  const i = ideal[cat] || 0;
  const group = document.createElement('div');
  group.className = 'bar-group';
  group.innerHTML = `
    <div class="bar-label"><span style="color:${{colors[cat]}}">${{labels[cat]}}</span><span>Atual ${{c}}% → Ideal ${{i}}%</span></div>
    <div class="bar-track">
      <div class="bar-fill" style="width:${{c}}%;background:${{colors[cat]}};opacity:0.7">${{c}}% atual</div>
    </div>
    <div class="bar-track" style="margin-top:4px">
      <div class="bar-fill" style="width:${{i}}%;background:${{colors[cat]}}">${{i}}% ideal</div>
    </div>
  `;
  barsEl.appendChild(group);
}});

// Reallocation
const reallocEl = document.getElementById('reallocation');
const increase = channels.filter(c => c.delta > 5000).sort((a,b) => b.delta - a.delta);
const decrease = channels.filter(c => c.delta < -5000).sort((a,b) => a.delta - b.delta);

function makeCol(title, items, isPositive) {{
  const col = document.createElement('div');
  col.className = 'comp-col';
  let html = `<h3>${{title}}</h3>`;
  items.forEach(ch => {{
    const cls = isPositive ? 'positive' : 'negative';
    const sign = ch.delta > 0 ? '+' : '';
    html += `<div class="channel-row">
      <span class="ch-name">${{ch.name}}</span>
      <span class="ch-delta ${{cls}}">${{sign}}${{fmtK(ch.delta)}}</span>
    </div>`;
  }});
  if (items.length === 0) html += '<div style="color:#64748b;font-size:13px">Nenhum canal</div>';
  col.innerHTML = html;
  return col;
}}

reallocEl.appendChild(makeCol('Aumentar Budget', increase, true));
reallocEl.appendChild(makeCol('Reduzir Budget', decrease, false));
</script>
</body>
</html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)


def main():
    parser = argparse.ArgumentParser(description='Budget 70/20/10 Allocator')
    parser.add_argument('--input-json', required=True, help='JSON string with budget data')
    parser.add_argument('--output-dir', required=True, help='Output directory')
    args = parser.parse_args()

    data = json.loads(args.input_json)
    os.makedirs(args.output_dir, exist_ok=True)

    result = analyze(data)

    json_path = os.path.join(args.output_dir, 'budget_analysis.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    html_path = os.path.join(args.output_dir, 'budget_report.html')
    generate_html(result, html_path)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
