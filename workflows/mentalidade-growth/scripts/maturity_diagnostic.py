#!/usr/bin/env python3
"""
Maturity Diagnostic Generator — G4 OS
Generates an interactive HTML radar chart and JSON analysis
for business maturity assessment across key areas.
"""

import argparse
import json
import math
import os
import sys
from datetime import datetime


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PHASES = [
    (10, "Fundacao"),
    (50, "Expansao Inicial"),
    (200, "Fortalecimento"),
    (500, "Expansao Estrategica"),
    (float("inf"), "Maturacao"),
]

PHASE_BENCHMARKS = {
    "Fundacao": {"marketing": 3, "comercial": 3, "ti": 2, "operacoes": 3},
    "Expansao Inicial": {"marketing": 5, "comercial": 5, "ti": 4, "operacoes": 5},
    "Fortalecimento": {"marketing": 7, "comercial": 6, "ti": 5, "operacoes": 7},
    "Expansao Estrategica": {"marketing": 8, "comercial": 8, "ti": 7, "operacoes": 8},
    "Maturacao": {"marketing": 9, "comercial": 9, "ti": 8, "operacoes": 9},
}

STAGE_NAMES = {
    (1, 3): "Pessoas",
    (4, 6): "Processos",
    (7, 8): "Tecnologia",
    (9, 10): "Escala",
}

AREA_LABELS = {
    "marketing": "Marketing",
    "comercial": "Comercial",
    "ti": "TI",
    "operacoes": "Operacoes",
}

AREA_ORDER = ["marketing", "comercial", "ti", "operacoes"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def determine_phase(num_employees: int) -> str:
    for threshold, name in PHASES:
        if num_employees <= threshold:
            return name
    return "Maturacao"


def determine_stage(score: int) -> str:
    for (lo, hi), name in STAGE_NAMES.items():
        if lo <= score <= hi:
            return name
    return "Desconhecido"


def compute_analysis(data: dict) -> dict:
    phase = determine_phase(data["num_employees"])
    benchmarks = PHASE_BENCHMARKS[phase]

    areas_analysis = {}
    min_score = 11
    bottleneck_key = None

    for key in AREA_ORDER:
        area = data["areas"][key]
        score = area["score"]
        expected = benchmarks[key]
        gap = score - expected
        stage = determine_stage(score)

        areas_analysis[key] = {
            "label": AREA_LABELS[key],
            "score": score,
            "expected": expected,
            "gap": gap,
            "stage": stage,
            "notes": area.get("notes", ""),
        }

        if score < min_score:
            min_score = score
            bottleneck_key = key

    overall_score = sum(data["areas"][k]["score"] for k in AREA_ORDER) / len(AREA_ORDER)
    overall_expected = sum(benchmarks[k] for k in AREA_ORDER) / len(AREA_ORDER)

    return {
        "company_name": data["company_name"],
        "num_employees": data["num_employees"],
        "monthly_revenue": data["monthly_revenue"],
        "sector": data["sector"],
        "main_challenge": data["main_challenge"],
        "phase": phase,
        "overall_score": round(overall_score, 1),
        "overall_expected": round(overall_expected, 1),
        "overall_gap": round(overall_score - overall_expected, 1),
        "bottleneck": bottleneck_key,
        "bottleneck_label": AREA_LABELS[bottleneck_key],
        "bottleneck_score": min_score,
        "areas": areas_analysis,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }


# ---------------------------------------------------------------------------
# SVG Radar Chart (pure string building)
# ---------------------------------------------------------------------------


def _polar_to_cart(cx: float, cy: float, radius: float, angle_deg: float):
    """Convert polar coordinates to cartesian. 0 deg = top (north)."""
    angle_rad = math.radians(angle_deg - 90)
    x = cx + radius * math.cos(angle_rad)
    y = cy + radius * math.sin(angle_rad)
    return x, y


def build_radar_svg(analysis: dict, size: int = 400) -> str:
    cx, cy = size / 2, size / 2
    max_val = 10
    max_radius = size * 0.38
    n = len(AREA_ORDER)
    angle_step = 360 / n

    lines = []
    lines.append(f'<svg viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">')

    # Grid rings
    for level in range(1, 6):
        r = max_radius * (level * 2) / max_val
        lines.append(
            f'  <circle cx="{cx}" cy="{cy}" r="{r:.1f}" '
            f'fill="none" stroke="#2a2d3a" stroke-width="1" />'
        )
        # Ring label
        lx, ly = cx + 4, cy - r + 12
        if level in (2, 4):
            lines.append(
                f'  <text x="{lx:.1f}" y="{ly:.1f}" '
                f'fill="#555" font-size="10" font-family="monospace">{level * 2}</text>'
            )

    # Axis lines and labels
    for i, key in enumerate(AREA_ORDER):
        angle = i * angle_step
        ex, ey = _polar_to_cart(cx, cy, max_radius + 4, angle)
        lines.append(
            f'  <line x1="{cx}" y1="{cy}" x2="{ex:.1f}" y2="{ey:.1f}" '
            f'stroke="#2a2d3a" stroke-width="1" />'
        )
        # Label
        lx, ly = _polar_to_cart(cx, cy, max_radius + 24, angle)
        anchor = "middle"
        if abs(lx - cx) > 5:
            anchor = "start" if lx > cx else "end"
        if angle == 0:
            ly -= 6
        elif angle == 180:
            ly += 14
        label = AREA_LABELS[key]
        lines.append(
            f'  <text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" '
            f'fill="#e4e4e7" font-size="13" font-family="system-ui, sans-serif" '
            f'font-weight="600">{label}</text>'
        )

    # Expected polygon (dashed)
    expected_points = []
    for i, key in enumerate(AREA_ORDER):
        angle = i * angle_step
        r = max_radius * analysis["areas"][key]["expected"] / max_val
        px, py = _polar_to_cart(cx, cy, r, angle)
        expected_points.append(f"{px:.1f},{py:.1f}")
    lines.append(
        f'  <polygon points="{" ".join(expected_points)}" '
        f'fill="none" stroke="#555" stroke-width="1.5" stroke-dasharray="6,4" />'
    )

    # Actual polygon (filled)
    actual_points = []
    for i, key in enumerate(AREA_ORDER):
        angle = i * angle_step
        r = max_radius * analysis["areas"][key]["score"] / max_val
        px, py = _polar_to_cart(cx, cy, r, angle)
        actual_points.append(f"{px:.1f},{py:.1f}")
    lines.append(
        f'  <polygon points="{" ".join(actual_points)}" '
        f'fill="rgba(59,130,246,0.18)" stroke="#3b82f6" stroke-width="2" />'
    )

    # Data point dots
    for i, key in enumerate(AREA_ORDER):
        angle = i * angle_step
        r = max_radius * analysis["areas"][key]["score"] / max_val
        px, py = _polar_to_cart(cx, cy, r, angle)
        is_bottleneck = key == analysis["bottleneck"]
        dot_color = "#ef4444" if is_bottleneck else "#3b82f6"
        dot_r = 6 if is_bottleneck else 4.5
        lines.append(
            f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="{dot_r}" '
            f'fill="{dot_color}" stroke="#0f1117" stroke-width="2" />'
        )
        # Score number near dot
        tx, ty = _polar_to_cart(cx, cy, r + 14, angle)
        lines.append(
            f'  <text x="{tx:.1f}" y="{ty:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="{dot_color}" '
            f'font-size="12" font-weight="700" font-family="monospace">'
            f'{analysis["areas"][key]["score"]}</text>'
        )

    lines.append("</svg>")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------


def _fmt_revenue(val: float) -> str:
    if val >= 1_000_000:
        return f"R$ {val / 1_000_000:.1f}M"
    if val >= 1_000:
        return f"R$ {val / 1_000:.0f}K"
    return f"R$ {val:.0f}"


def _stage_color(stage: str) -> str:
    return {
        "Pessoas": "#ef4444",
        "Processos": "#f59e0b",
        "Tecnologia": "#3b82f6",
        "Escala": "#10b981",
    }.get(stage, "#888")


def _gap_display(gap: int) -> str:
    if gap > 0:
        return f'<span style="color:#10b981">+{gap}</span>'
    if gap < 0:
        return f'<span style="color:#ef4444">{gap}</span>'
    return '<span style="color:#888">0</span>'


def build_html(analysis: dict) -> str:
    radar_svg = build_radar_svg(analysis)

    # Build area cards
    area_cards = []
    for key in AREA_ORDER:
        a = analysis["areas"][key]
        is_bottleneck = key == analysis["bottleneck"]
        border = "border-left: 3px solid #ef4444;" if is_bottleneck else "border-left: 3px solid #2a2d3a;"
        badge_bg = _stage_color(a["stage"])
        bottleneck_tag = (
            '<span style="background:#ef4444;color:#fff;padding:2px 8px;'
            'border-radius:4px;font-size:11px;font-weight:700;margin-left:8px;">'
            "GARGALO</span>"
            if is_bottleneck
            else ""
        )
        notes_html = (
            f'<p style="color:#888;font-size:13px;margin:8px 0 0;">'
            f'"{a["notes"]}"</p>'
            if a["notes"]
            else ""
        )

        card = f"""
        <div style="background:var(--surface);border-radius:8px;padding:20px;{border}">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
            <div style="display:flex;align-items:center;gap:8px;">
              <h3 style="margin:0;font-size:16px;color:var(--text);">{a["label"]}</h3>
              {bottleneck_tag}
            </div>
            <span style="background:{badge_bg};color:#fff;padding:3px 10px;
              border-radius:12px;font-size:11px;font-weight:600;">{a["stage"]}</span>
          </div>
          <div style="display:flex;gap:24px;align-items:baseline;">
            <div>
              <span style="font-size:32px;font-weight:700;color:{'#ef4444' if is_bottleneck else '#3b82f6'};">{a["score"]}</span>
              <span style="color:#888;font-size:14px;">/10</span>
            </div>
            <div style="font-size:13px;color:#888;">
              Esperado: <strong style="color:var(--text);">{a["expected"]}</strong>
              &nbsp;&middot;&nbsp; Gap: {_gap_display(a["gap"])}
            </div>
          </div>
          {notes_html}
        </div>"""
        area_cards.append(card)

    area_cards_html = "\n".join(area_cards)

    overall_color = "#10b981" if analysis["overall_gap"] >= 0 else "#ef4444"

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Diagnostico de Maturidade — {analysis["company_name"]}</title>
<style>
  :root {{
    --bg: #0f1117;
    --surface: #1a1d27;
    --border: #2a2d3a;
    --text: #e4e4e7;
    --accent: #3b82f6;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: var(--bg);
    color: var(--text);
    font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
    line-height: 1.6;
    padding: 32px 24px;
  }}
  .container {{ max-width: 900px; margin: 0 auto; }}
  .header {{
    text-align: center;
    margin-bottom: 32px;
    padding-bottom: 24px;
    border-bottom: 1px solid var(--border);
  }}
  .header h1 {{
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 4px;
  }}
  .header p {{ color: #888; font-size: 14px; }}
  .meta-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 12px;
    margin-bottom: 32px;
  }}
  .meta-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px;
  }}
  .meta-card .label {{ font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }}
  .meta-card .value {{ font-size: 18px; font-weight: 700; }}
  .section-title {{
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #888;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
  }}
  .radar-container {{
    display: flex;
    justify-content: center;
    margin-bottom: 32px;
    padding: 20px;
    background: var(--surface);
    border-radius: 12px;
    border: 1px solid var(--border);
  }}
  .radar-container svg {{ width: 100%; max-width: 420px; height: auto; }}
  .legend {{
    display: flex;
    justify-content: center;
    gap: 24px;
    margin-top: 12px;
    font-size: 13px;
    color: #888;
  }}
  .legend-item {{
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .areas-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
    gap: 12px;
    margin-bottom: 32px;
  }}
  .overall-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px;
    text-align: center;
    margin-bottom: 32px;
  }}
  .challenge-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid #f59e0b;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 32px;
  }}
  .footer {{
    text-align: center;
    font-size: 12px;
    color: #555;
    margin-top: 40px;
    padding-top: 16px;
    border-top: 1px solid var(--border);
  }}
  @media (max-width: 600px) {{
    .areas-grid {{ grid-template-columns: 1fr; }}
    .meta-grid {{ grid-template-columns: 1fr 1fr; }}
    body {{ padding: 16px 12px; }}
  }}
</style>
</head>
<body>
<div class="container">

  <div class="header">
    <h1>Diagnostico de Maturidade</h1>
    <p>{analysis["company_name"]} &middot; {analysis["generated_at"][:10]}</p>
  </div>

  <!-- Meta info -->
  <div class="meta-grid">
    <div class="meta-card">
      <div class="label">Fase</div>
      <div class="value" style="color:var(--accent);">{analysis["phase"]}</div>
    </div>
    <div class="meta-card">
      <div class="label">Colaboradores</div>
      <div class="value">{analysis["num_employees"]}</div>
    </div>
    <div class="meta-card">
      <div class="label">Receita Mensal</div>
      <div class="value">{_fmt_revenue(analysis["monthly_revenue"])}</div>
    </div>
    <div class="meta-card">
      <div class="label">Setor</div>
      <div class="value">{analysis["sector"]}</div>
    </div>
  </div>

  <!-- Challenge -->
  <div class="challenge-card">
    <div style="font-size:11px;color:#f59e0b;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;">
      Principal Desafio
    </div>
    <p style="font-size:15px;">"{analysis["main_challenge"]}"</p>
  </div>

  <!-- Overall -->
  <div class="overall-card">
    <div style="font-size:11px;color:#888;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;">
      Score Geral
    </div>
    <div style="font-size:48px;font-weight:700;color:{overall_color};">{analysis["overall_score"]}</div>
    <div style="font-size:14px;color:#888;">
      Esperado para a fase: <strong style="color:var(--text);">{analysis["overall_expected"]}</strong>
      &nbsp;&middot;&nbsp;
      Gap: <span style="color:{overall_color};font-weight:700;">
        {"+" if analysis["overall_gap"] >= 0 else ""}{analysis["overall_gap"]}</span>
    </div>
    <div style="margin-top:12px;font-size:13px;color:#888;">
      Gargalo: <strong style="color:#ef4444;">{analysis["bottleneck_label"]}</strong>
      (score {analysis["bottleneck_score"]})
    </div>
  </div>

  <!-- Radar -->
  <div style="margin-bottom:32px;">
    <div class="section-title">Radar de Maturidade</div>
    <div class="radar-container">
      <div>
        {radar_svg}
        <div class="legend">
          <div class="legend-item">
            <div style="width:16px;height:3px;background:#3b82f6;border-radius:2px;"></div>
            Atual
          </div>
          <div class="legend-item">
            <div style="width:16px;height:3px;background:#555;border-radius:2px;
              border-top:1px dashed #555;"></div>
            Esperado
          </div>
          <div class="legend-item">
            <div style="width:10px;height:10px;background:#ef4444;border-radius:50%;"></div>
            Gargalo
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Area cards -->
  <div style="margin-bottom:32px;">
    <div class="section-title">Detalhamento por Area</div>
    <div class="areas-grid">
      {area_cards_html}
    </div>
  </div>

  <!-- Stage legend -->
  <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:20px;margin-bottom:32px;">
    <div style="font-size:12px;color:#888;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:12px;">
      Estagios de Maturidade
    </div>
    <div style="display:flex;flex-wrap:wrap;gap:16px;">
      <div style="display:flex;align-items:center;gap:6px;">
        <span style="width:10px;height:10px;border-radius:50%;background:#ef4444;display:inline-block;"></span>
        <span style="font-size:13px;"><strong>1-3</strong> Pessoas</span>
      </div>
      <div style="display:flex;align-items:center;gap:6px;">
        <span style="width:10px;height:10px;border-radius:50%;background:#f59e0b;display:inline-block;"></span>
        <span style="font-size:13px;"><strong>4-6</strong> Processos</span>
      </div>
      <div style="display:flex;align-items:center;gap:6px;">
        <span style="width:10px;height:10px;border-radius:50%;background:#3b82f6;display:inline-block;"></span>
        <span style="font-size:13px;"><strong>7-8</strong> Tecnologia</span>
      </div>
      <div style="display:flex;align-items:center;gap:6px;">
        <span style="width:10px;height:10px;border-radius:50%;background:#10b981;display:inline-block;"></span>
        <span style="font-size:13px;"><strong>9-10</strong> Escala</span>
      </div>
    </div>
  </div>

  <div class="footer">
    Gerado por G4 OS &middot; Mentalidade Growth Workflow
  </div>
</div>
</body>
</html>"""
    return html


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Generate a business maturity diagnostic with radar chart."
    )
    parser.add_argument(
        "--input-json",
        required=True,
        help="JSON string with maturity data",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Output directory for generated files",
    )
    args = parser.parse_args()

    # Parse input
    try:
        data = json.loads(args.input_json)
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON input — {exc}", file=sys.stderr)
        sys.exit(1)

    # Validate required fields
    required = ["company_name", "num_employees", "monthly_revenue", "sector", "main_challenge", "areas"]
    missing = [f for f in required if f not in data]
    if missing:
        print(f"Error: missing required fields: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    for key in AREA_ORDER:
        if key not in data["areas"]:
            print(f"Error: missing area '{key}' in areas object", file=sys.stderr)
            sys.exit(1)
        if "score" not in data["areas"][key]:
            print(f"Error: missing 'score' in area '{key}'", file=sys.stderr)
            sys.exit(1)

    # Compute analysis
    analysis = compute_analysis(data)

    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)

    # Write HTML
    html_path = os.path.join(args.output_dir, "maturity_diagnostic.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(build_html(analysis))

    # Write JSON analysis
    json_path = os.path.join(args.output_dir, "maturity_analysis.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)

    # Print summary to stdout
    summary = {
        "company": analysis["company_name"],
        "phase": analysis["phase"],
        "overall_score": analysis["overall_score"],
        "overall_expected": analysis["overall_expected"],
        "overall_gap": analysis["overall_gap"],
        "bottleneck": analysis["bottleneck_label"],
        "bottleneck_score": analysis["bottleneck_score"],
        "areas": {
            key: {
                "score": a["score"],
                "expected": a["expected"],
                "gap": a["gap"],
                "stage": a["stage"],
            }
            for key, a in analysis["areas"].items()
        },
        "output_html": html_path,
        "output_json": json_path,
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
