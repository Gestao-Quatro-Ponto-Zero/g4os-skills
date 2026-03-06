#!/usr/bin/env python3
"""
Comp Plan Designer — Plano de Comissionamento com Aceleradores
Framework: Alfredo Soares (Ecossistema de Vendas, G4 GE 2026)

Desenha comp plans, simula cenarios e gera calculadora interativa.
"""

import json
import argparse
import os
from datetime import datetime


def get_multiplier(attainment_pct, accelerators):
    """Get the commission multiplier for a given attainment percentage."""
    for tier in accelerators:
        if tier["min_pct"] <= attainment_pct <= tier["max_pct"]:
            return tier["multiplier"]
    return 0


def compute_deal_modifier(modifiers, scenario="neutral"):
    """Compute combined deal modifier for a given scenario.

    Scenarios: 'best' (all bonuses), 'neutral' (no modifiers), 'worst' (all deflators).
    Returns the combined multiplier and a breakdown dict.
    """
    if not modifiers:
        return 1.0, {}

    breakdown = {}
    combined = 1.0

    for mod_type, rules in modifiers.items():
        if scenario == "best":
            # Pick the highest modifier
            val = max(rules.values())
            key = [k for k, v in rules.items() if v == val][0]
        elif scenario == "worst":
            # Pick the lowest modifier
            val = min(rules.values())
            key = [k for k, v in rules.items() if v == val][0]
        else:
            # Neutral — pick the one closest to 1.0
            val = min(rules.values(), key=lambda v: abs(v - 1.0))
            key = [k for k, v in rules.items() if v == val][0]
        breakdown[mod_type] = {"condition": key, "multiplier": val}
        combined *= val

    return round(combined, 4), breakdown


def simulate_plan(plan, attainment_pct, deal_modifier=1.0):
    """Simulate compensation for a given attainment level."""
    base = plan["base_salary"]
    target_value = plan["target_value"]
    accelerators = plan.get("accelerators", [
        {"min_pct": 0, "max_pct": 70, "multiplier": 0},
        {"min_pct": 71, "max_pct": 85, "multiplier": 0.5},
        {"min_pct": 86, "max_pct": 99, "multiplier": 0.7},
        {"min_pct": 100, "max_pct": 119, "multiplier": 1.0},
        {"min_pct": 120, "max_pct": 999, "multiplier": 1.5},
    ])

    multiplier = get_multiplier(attainment_pct, accelerators)
    units_delivered = target_value * attainment_pct / 100

    # Calculate base commission (before multiplier)
    if plan.get("commission_per_unit"):
        base_commission = units_delivered * plan["commission_per_unit"]
    elif plan.get("commission_pct"):
        base_commission = units_delivered * plan["commission_pct"] / 100
    else:
        # Fallback: derive from OTE
        ote_variable = plan["ote"] - base
        base_commission = ote_variable * attainment_pct / 100

    variable = base_commission * multiplier * deal_modifier
    total = base + variable

    return {
        "attainment_pct": attainment_pct,
        "units_delivered": round(units_delivered, 1),
        "multiplier": multiplier,
        "deal_modifier": deal_modifier,
        "base_salary": base,
        "variable": round(variable),
        "total_comp": round(base + variable),
        "cost_per_head": round(base + variable),
    }


def analyze(data):
    """Run full comp plan analysis."""
    plans = data["plans"]
    company_targets = data.get("company_targets", {})
    revenue_target = company_targets.get("monthly_revenue_target", 0)
    max_commission_pct = company_targets.get("max_commission_budget_pct", 15)

    scenarios = [50, 75, 90, 100, 110, 130, 150]

    results = []
    for plan in plans:
        simulations = []
        for pct in scenarios:
            sim = simulate_plan(plan, pct)
            simulations.append(sim)

        # OTE check
        ote_sim = simulate_plan(plan, 100)
        ote_match = abs(ote_sim["total_comp"] - plan["ote"]) < plan["ote"] * 0.05

        # Deal modifier scenarios (if modifiers defined)
        modifiers = plan.get("modifiers", {})
        modifier_scenarios = {}
        if modifiers:
            for scenario_name in ["best", "neutral", "worst"]:
                mod_val, mod_breakdown = compute_deal_modifier(modifiers, scenario_name)
                sim_100 = simulate_plan(plan, 100, deal_modifier=mod_val)
                modifier_scenarios[scenario_name] = {
                    "deal_modifier": mod_val,
                    "breakdown": mod_breakdown,
                    "variable_at_100": sim_100["variable"],
                    "total_at_100": sim_100["total_comp"],
                }

        results.append({
            "role": plan["role"],
            "headcount": plan["headcount"],
            "base_salary": plan["base_salary"],
            "ote": plan["ote"],
            "variable_pct": plan.get("variable_pct", round((plan["ote"] - plan["base_salary"]) / plan["ote"] * 100)),
            "target_metric": plan.get("target_metric", ""),
            "target_value": plan["target_value"],
            "target_unit": plan.get("target_unit", ""),
            "commission_mechanism": f"R${plan['commission_per_unit']}/unidade" if plan.get("commission_per_unit") else f"{plan.get('commission_pct', 0)}% da receita",
            "accelerators": plan.get("accelerators", []),
            "modifiers": modifiers,
            "modifier_scenarios": modifier_scenarios,
            "contests": plan.get("contests", []),
            "split_metrics": plan.get("split_metrics", []),
            "simulations": simulations,
            "ote_check": ote_match,
        })

    # Company cost projections
    cost_scenarios = {}
    for pct in [80, 100, 120]:
        total_cost = 0
        for plan, result in zip(plans, results):
            sim = simulate_plan(plan, pct)
            total_cost += sim["cost_per_head"] * plan["headcount"]
        cost_scenarios[str(pct)] = {
            "total_cost": total_cost,
            "pct_of_revenue": round(total_cost / revenue_target * 100, 1) if revenue_target > 0 else None,
        }

    total_headcount = sum(p["headcount"] for p in plans)
    total_base = sum(p["base_salary"] * p["headcount"] for p in plans)
    total_ote = sum(p["ote"] * p["headcount"] for p in plans)
    total_variable_100 = total_ote - total_base

    return {
        "company_name": data.get("company_name", ""),
        "currency": data.get("currency", "BRL"),
        "total_headcount": total_headcount,
        "total_base_payroll": total_base,
        "total_ote": total_ote,
        "total_variable_at_100": total_variable_100,
        "commission_pct_of_revenue_at_100": round(total_variable_100 / revenue_target * 100, 1) if revenue_target > 0 else None,
        "max_commission_pct": max_commission_pct,
        "revenue_target": revenue_target,
        "plans": results,
        "cost_scenarios": cost_scenarios,
        "generated_at": datetime.now().isoformat(),
    }


def generate_html(result, output_path):
    """Generate interactive HTML comp plan calculator."""
    plans = result["plans"]
    company = result["company_name"] or "Sua Empresa"

    plans_js = json.dumps(plans, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Comp Plan — {company}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; padding: 24px; }}
.header {{ text-align: center; margin-bottom: 32px; }}
.header h1 {{ font-size: 24px; font-weight: 700; }}
.header p {{ color: #94a3b8; margin-top: 4px; font-size: 14px; }}
.tabs {{ display: flex; gap: 8px; justify-content: center; margin-bottom: 24px; flex-wrap: wrap; }}
.tab {{ padding: 8px 20px; border-radius: 8px; background: #1e293b; border: 1px solid #334155; cursor: pointer; font-size: 14px; font-weight: 500; transition: all 0.2s; }}
.tab.active {{ background: #3b82f6; border-color: #3b82f6; color: #fff; }}
.tab:hover {{ border-color: #3b82f6; }}
.plan-view {{ max-width: 800px; margin: 0 auto; }}
.card {{ background: #1e293b; border-radius: 10px; padding: 20px; margin-bottom: 20px; }}
.card h2 {{ font-size: 18px; font-weight: 600; margin-bottom: 16px; }}
.card h3 {{ font-size: 15px; font-weight: 600; margin-bottom: 12px; color: #94a3b8; }}
.metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-bottom: 20px; }}
.metric {{ text-align: center; padding: 12px; background: #0f172a; border-radius: 8px; }}
.metric .label {{ font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }}
.metric .value {{ font-size: 22px; font-weight: 700; margin-top: 2px; }}
.metric .sub {{ font-size: 11px; color: #94a3b8; }}
.slider-container {{ margin: 20px 0; }}
.slider-label {{ display: flex; justify-content: space-between; margin-bottom: 8px; }}
.slider-label span {{ font-size: 14px; color: #94a3b8; }}
.slider-value {{ font-size: 32px; font-weight: 700; text-align: center; margin-bottom: 8px; }}
input[type="range"] {{ width: 100%; height: 6px; -webkit-appearance: none; background: #334155; border-radius: 3px; outline: none; }}
input[type="range"]::-webkit-slider-thumb {{ -webkit-appearance: none; width: 20px; height: 20px; background: #3b82f6; border-radius: 50%; cursor: pointer; }}
.result-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-top: 16px; }}
.result-box {{ background: #0f172a; border-radius: 8px; padding: 16px; text-align: center; }}
.result-box .rlabel {{ font-size: 12px; color: #64748b; }}
.result-box .rvalue {{ font-size: 24px; font-weight: 700; margin-top: 4px; }}
.accel-chart {{ display: flex; align-items: flex-end; gap: 4px; height: 120px; margin: 16px 0; }}
.accel-bar {{ flex: 1; border-radius: 4px 4px 0 0; position: relative; transition: height 0.3s; display: flex; flex-direction: column; justify-content: flex-end; align-items: center; padding-bottom: 4px; }}
.accel-bar .bar-label {{ font-size: 10px; color: #e2e8f0; font-weight: 600; }}
.accel-bar .bar-range {{ font-size: 9px; color: #94a3b8; position: absolute; bottom: -18px; white-space: nowrap; }}
.table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
.table th {{ font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; padding: 8px; text-align: left; border-bottom: 1px solid #334155; }}
.table td {{ padding: 8px; font-size: 14px; border-bottom: 1px solid rgba(51,65,85,0.5); }}
.table tr.highlight {{ background: rgba(59,130,246,0.1); }}
.footer {{ text-align: center; margin-top: 40px; font-size: 12px; color: #475569; }}
.mod-section {{ margin-top: 16px; padding: 16px; background: #0f172a; border-radius: 8px; }}
.mod-row {{ display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }}
.mod-row label {{ font-size: 13px; color: #94a3b8; min-width: 120px; }}
.mod-row select {{ background: #1e293b; color: #e2e8f0; border: 1px solid #334155; border-radius: 6px; padding: 6px 10px; font-size: 13px; }}
.mod-badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; margin-left: 8px; }}
.mod-badge.bonus {{ background: rgba(34,197,94,0.15); color: #22c55e; }}
.mod-badge.neutral {{ background: rgba(148,163,184,0.15); color: #94a3b8; }}
.mod-badge.deflator {{ background: rgba(239,68,68,0.15); color: #ef4444; }}
</style>
</head>
<body>
<div class="header">
  <h1>Comp Plan Calculator — {company}</h1>
  <p>Framework Alfredo Soares | Aceleradores de Comissao</p>
</div>

<div class="tabs" id="tabs"></div>
<div class="plan-view" id="planView"></div>

<div class="footer">
  Gerado por G4 OS | {datetime.now().strftime('%d/%m/%Y %H:%M')}
</div>

<script>
const plans = {plans_js};
let activePlan = 0;

function fmtBRL(v) {{
  return 'R$' + v.toLocaleString('pt-BR', {{ minimumFractionDigits: 0, maximumFractionDigits: 0 }});
}}

function getMultiplier(pct, accels) {{
  for (const a of accels) {{
    if (pct >= a.min_pct && pct <= a.max_pct) return a.multiplier;
  }}
  return 0;
}}

function simulate(plan, pct, dealMod) {{
  dealMod = dealMod || 1.0;
  const base = plan.base_salary;
  const target = plan.target_value;
  const units = target * pct / 100;
  const mult = getMultiplier(pct, plan.accelerators);

  let baseComm;
  if (plan.commission_mechanism.includes('/unidade')) {{
    const perUnit = parseFloat(plan.commission_mechanism.replace('R$', '').replace('/unidade', ''));
    baseComm = units * perUnit;
  }} else {{
    const commPct = parseFloat(plan.commission_mechanism.replace('% da receita', ''));
    baseComm = units * commPct / 100;
  }}

  const variable = baseComm * mult * dealMod;
  return {{ base, variable: Math.round(variable), total: Math.round(base + variable), mult, dealMod, units: Math.round(units * 10) / 10 }};
}}

function getDealModifier(plan) {{
  if (!plan.modifiers || Object.keys(plan.modifiers).length === 0) return 1.0;
  let combined = 1.0;
  for (const [modType, rules] of Object.entries(plan.modifiers)) {{
    const sel = document.getElementById('mod_' + activePlan + '_' + modType);
    if (sel) combined *= parseFloat(sel.value);
  }}
  return combined;
}}

function renderPlan(idx) {{
  activePlan = idx;
  const plan = plans[idx];
  const view = document.getElementById('planView');

  // Update tabs
  document.querySelectorAll('.tab').forEach((t, i) => {{
    t.classList.toggle('active', i === idx);
  }});

  let html = `
  <div class="card">
    <h2>${{plan.role}}</h2>
    <div class="metrics-grid">
      <div class="metric"><div class="label">Base</div><div class="value">${{fmtBRL(plan.base_salary)}}</div></div>
      <div class="metric"><div class="label">OTE</div><div class="value" style="color:#22c55e">${{fmtBRL(plan.ote)}}</div></div>
      <div class="metric"><div class="label">Variavel</div><div class="value">${{plan.variable_pct}}%</div></div>
      <div class="metric"><div class="label">Headcount</div><div class="value">${{plan.headcount}}</div></div>
      <div class="metric"><div class="label">Meta</div><div class="value">${{plan.target_value}}</div><div class="sub">${{plan.target_unit}}</div></div>
      <div class="metric"><div class="label">Mecanismo</div><div class="value" style="font-size:14px">${{plan.commission_mechanism}}</div></div>
    </div>
  </div>

  <div class="card">
    <h3>Aceleradores</h3>
    <div class="accel-chart">`;

  const maxMult = Math.max(...plan.accelerators.map(a => a.multiplier));
  plan.accelerators.forEach(a => {{
    const h = maxMult > 0 ? (a.multiplier / maxMult * 100) : 0;
    const color = a.multiplier === 0 ? '#ef4444' : a.multiplier < 1 ? '#eab308' : a.multiplier === 1 ? '#22c55e' : '#3b82f6';
    html += `<div class="accel-bar" style="height:${{Math.max(h, 5)}}%;background:${{color}}">
      <span class="bar-label">${{a.multiplier}}x</span>
      <span class="bar-range">${{a.min_pct}}-${{a.max_pct}}%</span>
    </div>`;
  }});

  html += `</div></div>

  <div class="card">
    <h3>Simulador Interativo</h3>
    <div class="slider-container">
      <div class="slider-value" id="sliderVal">100%</div>
      <input type="range" id="attSlider" min="0" max="200" value="100" step="5">
      <div class="slider-label"><span>0%</span><span>100%</span><span>200%</span></div>
    </div>`;

  // Modifier dropdowns if plan has modifiers
  const modLabels = {{ payment: 'Modal Pagamento', discount: 'Desconto', grace_period: 'Carencia' }};
  const condLabels = {{
    pix: 'PIX / À vista', cartao_1_3: 'Cartão 1-3x', cartao_4_6: 'Cartão 4-6x',
    boleto_7_12: 'Boleto 7-12x', anual_upfront: 'Anual upfront', recorrencia: 'Recorrência',
    full_price: 'Preço cheio (0%)', '1_10pct': 'Desconto 1-10%', '11_20pct': 'Desconto 11-20%',
    '21_plus': 'Desconto 21%+', none: 'Sem carência', '30_days': '30 dias', '60_plus': '60+ dias'
  }};
  if (plan.modifiers && Object.keys(plan.modifiers).length > 0) {{
    html += `<div class="mod-section"><h3 style="margin-bottom:12px;font-size:14px;color:#94a3b8">Modificadores de Deal</h3>`;
    for (const [modType, rules] of Object.entries(plan.modifiers)) {{
      html += `<div class="mod-row"><label>${{modLabels[modType] || modType}}</label><select id="mod_${{idx}}_${{modType}}" onchange="updateSlider()">`;
      for (const [cond, val] of Object.entries(rules)) {{
        const label = condLabels[cond] || cond;
        const selected = Math.abs(val - 1.0) < 0.001 ? ' selected' : '';
        html += `<option value="${{val}}"${{selected}}>${{label}} (${{val > 1 ? '+' : ''}}${{Math.round((val-1)*100)}}%)</option>`;
      }}
      html += `</select></div>`;
    }}
    html += `<div style="margin-top:8px;font-size:12px;color:#64748b">Modificador combinado: <span id="modCombined" style="color:#e2e8f0;font-weight:600">1.0x</span></div></div>`;
  }}

  html += `
    <div class="result-grid">
      <div class="result-box"><div class="rlabel">Base</div><div class="rvalue" id="rBase">${{fmtBRL(plan.base_salary)}}</div></div>
      <div class="result-box"><div class="rlabel">Variavel</div><div class="rvalue" id="rVar" style="color:#22c55e">—</div></div>
      <div class="result-box"><div class="rlabel">Total</div><div class="rvalue" id="rTotal" style="color:#3b82f6">—</div></div>
    </div>
  </div>`;

  <div class="card">
    <h3>Tabela de Cenarios</h3>
    <table class="table">
      <tr><th>Atingimento</th><th>Entregas</th><th>Mult.</th><th>Base</th><th>Variavel</th><th>Total</th></tr>`;

  plan.simulations.forEach(s => {{
    const cls = s.attainment_pct === 100 ? ' class="highlight"' : '';
    html += `<tr${{cls}}>
      <td>${{s.attainment_pct}}%</td>
      <td>${{s.units_delivered}}</td>
      <td>${{s.multiplier}}x</td>
      <td>${{fmtBRL(s.base_salary)}}</td>
      <td>${{fmtBRL(s.variable)}}</td>
      <td style="font-weight:600">${{fmtBRL(s.total_comp)}}</td>
    </tr>`;
  }});

  html += `</table></div>`;

  if (plan.contests && plan.contests.length > 0) {{
    html += `<div class="card"><h3>Contests & Incentivos</h3>`;
    plan.contests.forEach(c => {{
      html += `<div style="padding:8px 0;border-bottom:1px solid #334155">
        <div style="font-weight:600">${{c.name}}</div>
        <div style="font-size:13px;color:#94a3b8">${{c.metric}} — ${{c.prize}} (${{c.duration}})</div>
      </div>`;
    }});
    html += `</div>`;
  }}

  view.innerHTML = html;

  // Attach slider listener
  const slider = document.getElementById('attSlider');
  window.updateSlider = () => {{
    const pct = parseInt(slider.value);
    const dealMod = getDealModifier(plan);
    document.getElementById('sliderVal').textContent = pct + '%';
    document.getElementById('sliderVal').style.color = pct < 71 ? '#ef4444' : pct < 100 ? '#eab308' : '#22c55e';
    const sim = simulate(plan, pct, dealMod);
    document.getElementById('rBase').textContent = fmtBRL(sim.base);
    document.getElementById('rVar').textContent = fmtBRL(sim.variable);
    document.getElementById('rTotal').textContent = fmtBRL(sim.total);
    const modEl = document.getElementById('modCombined');
    if (modEl) {{
      modEl.textContent = dealMod.toFixed(2) + 'x';
      modEl.style.color = dealMod > 1 ? '#22c55e' : dealMod < 1 ? '#ef4444' : '#e2e8f0';
    }}
  }};
  slider.addEventListener('input', updateSlider);
  updateSlider();
}}

// Build tabs
const tabsEl = document.getElementById('tabs');
plans.forEach((p, i) => {{
  const tab = document.createElement('div');
  tab.className = 'tab' + (i === 0 ? ' active' : '');
  tab.textContent = p.role + ' (' + p.headcount + ')';
  tab.onclick = () => renderPlan(i);
  tabsEl.appendChild(tab);
}});

renderPlan(0);
</script>
</body>
</html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)


def generate_doc(result, output_path):
    """Generate shareable comp plan document."""
    company = result["company_name"] or "Sua Empresa"
    currency = result["currency"]

    def fmt(v):
        if v >= 1_000_000:
            return f"R${v/1_000_000:.1f}M"
        if v >= 1_000:
            return f"R${v/1_000:.0f}K"
        return f"R${v:,.0f}"

    doc = f"""# Plano de Comissionamento — {company}

**Data**: {datetime.now().strftime('%d/%m/%Y')}
**Headcount total**: {result['total_headcount']} pessoas
**Folha base**: {fmt(result['total_base_payroll'])}/mes
**OTE total**: {fmt(result['total_ote'])}/mes

---

"""

    for plan in result["plans"]:
        doc += f"""## {plan['role']} ({plan['headcount']} pessoas)

| Item | Valor |
|------|-------|
| Salario Base | {fmt(plan['base_salary'])} |
| OTE (100%) | {fmt(plan['ote'])} |
| Split | {100 - plan['variable_pct']}% fixo / {plan['variable_pct']}% variavel |
| Meta | {plan['target_value']} {plan['target_unit']} |
| Mecanismo | {plan['commission_mechanism']} |

### Aceleradores

| Faixa | Multiplicador |
|-------|---------------|
"""
        for acc in plan["accelerators"]:
            doc += f"| {acc['min_pct']}-{acc['max_pct']}% | {acc['multiplier']}x |\n"

        doc += "\n### Simulacao de Cenarios\n\n"
        doc += "| Atingimento | Entregas | Mult. | Base | Variavel | Total |\n"
        doc += "|-------------|----------|-------|------|----------|-------|\n"
        for sim in plan["simulations"]:
            doc += f"| {sim['attainment_pct']}% | {sim['units_delivered']} | {sim['multiplier']}x | {fmt(sim['base_salary'])} | {fmt(sim['variable'])} | {fmt(sim['total_comp'])} |\n"

        if plan.get("modifier_scenarios") and plan["modifier_scenarios"]:
            doc += "\n### Modificadores de Deal (impacto a 100% de meta)\n\n"
            doc += "| Cenario | Modificador | Variavel | Total |\n"
            doc += "|---------|-------------|----------|-------|\n"
            labels = {"best": "Melhor caso", "neutral": "Neutro", "worst": "Pior caso"}
            for sc_name, sc_data in plan["modifier_scenarios"].items():
                sign = "+" if sc_data["deal_modifier"] > 1 else ""
                doc += f"| {labels.get(sc_name, sc_name)} | {sc_data['deal_modifier']}x ({sign}{round((sc_data['deal_modifier']-1)*100)}%) | {fmt(sc_data['variable_at_100'])} | {fmt(sc_data['total_at_100'])} |\n"

        if plan.get("contests"):
            doc += "\n### Contests & Incentivos\n\n"
            for c in plan["contests"]:
                doc += f"- **{c['name']}**: {c['metric']} — {c['prize']} ({c['duration']})\n"

        doc += "\n---\n\n"

    # Cost summary
    doc += """## Custo Total para Empresa

| Cenario | Custo Mensal | % da Receita Target |
|---------|-------------|--------------------|\n"""

    for pct, scenario in result["cost_scenarios"].items():
        pct_rev = f"{scenario['pct_of_revenue']}%" if scenario['pct_of_revenue'] else "—"
        doc += f"| Time a {pct}% | {fmt(scenario['total_cost'])} | {pct_rev} |\n"

    doc += f"""
---

## Regras Gerais

1. **Elegibilidade**: Comissao valida a partir do 1o mes completo apos onboarding
2. **Pagamento**: Comissao paga no mes seguinte ao fechamento
3. **Teto**: Budget de comissao nao deve ultrapassar {result['max_commission_pct']}% da receita target
4. **Revisao**: Plano revisado trimestralmente com base em performance

---

*Documento gerado por G4 OS | Framework Alfredo Soares*
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(doc)


def main():
    parser = argparse.ArgumentParser(description='Comp Plan Designer')
    parser.add_argument('--input-json', required=True, help='JSON string with comp plan data')
    parser.add_argument('--output-dir', required=True, help='Output directory')
    args = parser.parse_args()

    data = json.loads(args.input_json)
    os.makedirs(args.output_dir, exist_ok=True)

    result = analyze(data)

    json_path = os.path.join(args.output_dir, 'comp_plan_analysis.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    html_path = os.path.join(args.output_dir, 'comp_plan_report.html')
    generate_html(result, html_path)

    doc_path = os.path.join(args.output_dir, 'comp_plan_doc.md')
    generate_doc(result, doc_path)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
