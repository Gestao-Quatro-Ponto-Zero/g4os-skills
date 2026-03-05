#!/usr/bin/env python3
"""
RFM Analysis & Customer Clustering Engine
==========================================
Reads transactional data, computes RFM scores, segments customers,
runs K-Means clustering, and generates an interactive HTML report.

Usage:
    python3 rfm_analysis.py <input_file> <output_dir> [--config config.json]

Input:
    - CSV or XLSX with transactional data
    - Optional JSON config for column mapping and business context

Output:
    - rfm_segments.csv        — Customer-level RFM scores and segments
    - rfm_report.html         — Interactive HTML report with charts
    - cluster_profiles.json   — Cluster centroids and characteristics
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings

warnings.filterwarnings("ignore")

# ─── RFM Segment Mapping ───────────────────────────────────────────────
# Based on R and FM combined scores (1-5 scale)
SEGMENT_MAP = {
    (5, 5): "Champions",
    (5, 4): "Champions",
    (4, 5): "Champions",
    (5, 3): "Loyal Customers",
    (4, 4): "Loyal Customers",
    (3, 5): "Loyal Customers",
    (5, 2): "Potential Loyalists",
    (4, 3): "Potential Loyalists",
    (4, 2): "Potential Loyalists",
    (3, 4): "Potential Loyalists",
    (3, 3): "Potential Loyalists",
    (5, 1): "Recent Customers",
    (4, 1): "Promising",
    (3, 2): "Promising",
    (3, 1): "Needing Attention",
    (2, 5): "Can't Lose Them",
    (2, 4): "Can't Lose Them",
    (2, 3): "At Risk",
    (2, 2): "At Risk",
    (1, 5): "Can't Lose Them",
    (1, 4): "At Risk",
    (1, 3): "About to Sleep",
    (2, 1): "About to Sleep",
    (1, 2): "Hibernating",
    (1, 1): "Lost",
}

SEGMENT_COLORS = {
    "Champions": "#2ecc71",
    "Loyal Customers": "#27ae60",
    "Potential Loyalists": "#3498db",
    "Recent Customers": "#1abc9c",
    "Promising": "#9b59b6",
    "Needing Attention": "#f39c12",
    "Can't Lose Them": "#e74c3c",
    "At Risk": "#e67e22",
    "About to Sleep": "#95a5a6",
    "Hibernating": "#7f8c8d",
    "Lost": "#34495e",
}

SEGMENT_ORDER = [
    "Champions", "Loyal Customers", "Potential Loyalists",
    "Recent Customers", "Promising", "Needing Attention",
    "Can't Lose Them", "At Risk", "About to Sleep",
    "Hibernating", "Lost",
]


# ─── Column Auto-Detection ─────────────────────────────────────────────

COLUMN_HINTS = {
    "customer_id": [
        "customerid", "customer_id", "client_id", "clientid", "user_id",
        "userid", "buyer_id", "buyerid", "account_id", "accountid",
        "cust_id", "custid", "customer", "cliente", "id_cliente",
    ],
    "transaction_date": [
        "transactiondate", "transaction_date", "date", "order_date",
        "orderdate", "purchase_date", "purchasedate", "invoicedate",
        "invoice_date", "created_at", "createdat", "data", "dt_compra",
        "data_transacao", "data_pedido",
    ],
    "revenue": [
        "revenue", "amount", "total", "value", "price", "sales",
        "total_amount", "totalamount", "order_value", "ordervalue",
        "transaction_amount", "transactionamount", "receita", "valor",
        "valor_total", "gmv", "net_revenue",
    ],
    "quantity": [
        "quantity", "qty", "units", "items", "quantidade",
        "num_items", "order_qty",
    ],
    "discount": [
        "discount", "desconto", "discount_pct", "discount_rate",
        "disc", "discount_amount",
    ],
}


def auto_detect_columns(df: pd.DataFrame) -> dict:
    """Auto-detect column mapping from dataframe columns."""
    mapping = {}
    df_cols_lower = {c.lower().replace(" ", "_").replace("-", "_"): c for c in df.columns}

    for role, hints in COLUMN_HINTS.items():
        for hint in hints:
            if hint in df_cols_lower:
                mapping[role] = df_cols_lower[hint]
                break

    return mapping


def compute_revenue(df: pd.DataFrame, mapping: dict) -> pd.Series:
    """Compute revenue per row from available columns."""
    if "revenue" in mapping and mapping["revenue"] in df.columns:
        rev = pd.to_numeric(df[mapping["revenue"]], errors="coerce").fillna(0)
        # If quantity and discount also exist, check if revenue is unit price
        if "quantity" in mapping and mapping["quantity"] in df.columns:
            qty = pd.to_numeric(df[mapping["quantity"]], errors="coerce").fillna(1)
            # Heuristic: if revenue column seems like unit price (name contains 'price'),
            # multiply by quantity
            rev_col_lower = mapping["revenue"].lower()
            if "price" in rev_col_lower and "total" not in rev_col_lower:
                rev = rev * qty
        if "discount" in mapping and mapping["discount"] in df.columns:
            disc = pd.to_numeric(df[mapping["discount"]], errors="coerce").fillna(0)
            # If discount values are between 0 and 1, treat as percentage
            if disc.max() <= 1.0:
                rev = rev * (1 - disc)
            else:
                rev = rev - disc
        return rev
    elif "quantity" in mapping and mapping["quantity"] in df.columns:
        # Fallback: just use quantity as a proxy
        return pd.to_numeric(df[mapping["quantity"]], errors="coerce").fillna(0)
    else:
        return pd.Series(1, index=df.index)


# ─── RFM Computation ───────────────────────────────────────────────────

def compute_rfm(df: pd.DataFrame, mapping: dict, reference_date=None) -> pd.DataFrame:
    """Compute RFM table from transactional data."""
    # Prepare columns
    cust_col = mapping["customer_id"]
    date_col = mapping["transaction_date"]

    df = df.copy()
    df["_revenue"] = compute_revenue(df, mapping)
    df["_date"] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=["_date"])

    if reference_date is None:
        reference_date = df["_date"].max() + timedelta(days=1)

    # Aggregate per customer
    rfm = df.groupby(cust_col).agg(
        recency=("_date", lambda x: (reference_date - x.max()).days),
        frequency=("_date", "count"),
        monetary=("_revenue", "sum"),
    ).reset_index()

    rfm.rename(columns={cust_col: "customer_id"}, inplace=True)

    # Score using quintiles (5 = best)
    rfm["R"] = pd.qcut(rfm["recency"], 5, labels=[5, 4, 3, 2, 1], duplicates="drop").astype(int)
    rfm["F"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5], duplicates="drop").astype(int)
    rfm["M"] = pd.qcut(rfm["monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5], duplicates="drop").astype(int)

    rfm["FM"] = ((rfm["F"] + rfm["M"]) / 2).round().astype(int)
    rfm["RFM_Score"] = rfm["R"] * 100 + rfm["F"] * 10 + rfm["M"]

    # Map to segments
    rfm["segment"] = rfm.apply(
        lambda row: SEGMENT_MAP.get((row["R"], row["FM"]), "Other"), axis=1
    )

    return rfm


# ─── K-Means Clustering ────────────────────────────────────────────────

def run_clustering(rfm: pd.DataFrame, n_clusters: int = 5) -> pd.DataFrame:
    """Run K-Means clustering on RFM values."""
    features = rfm[["recency", "frequency", "monetary"]].copy()
    # Log-transform monetary and frequency to reduce skew
    features["frequency"] = np.log1p(features["frequency"])
    features["monetary"] = np.log1p(features["monetary"])

    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    rfm = rfm.copy()
    rfm["cluster"] = kmeans.fit_predict(scaled)

    # Order clusters by monetary value (descending)
    cluster_order = (
        rfm.groupby("cluster")["monetary"]
        .mean()
        .sort_values(ascending=False)
        .index.tolist()
    )
    cluster_map = {old: new for new, old in enumerate(cluster_order)}
    rfm["cluster"] = rfm["cluster"].map(cluster_map)

    return rfm


# ─── Optimal K Detection ───────────────────────────────────────────────

def find_optimal_k(rfm: pd.DataFrame, max_k: int = 10) -> int:
    """Find optimal number of clusters using elbow method."""
    features = rfm[["recency", "frequency", "monetary"]].copy()
    features["frequency"] = np.log1p(features["frequency"])
    features["monetary"] = np.log1p(features["monetary"])

    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)

    inertias = []
    K = range(2, max_k + 1)
    for k in K:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(scaled)
        inertias.append(km.inertia_)

    # Simple elbow detection: find point of maximum curvature
    diffs = np.diff(inertias)
    diffs2 = np.diff(diffs)
    optimal_k = int(np.argmax(np.abs(diffs2)) + 3)  # +3 because of double diff offset from K=2
    optimal_k = min(max(optimal_k, 3), 8)  # clamp between 3 and 8
    return optimal_k


# ─── Report Generation ─────────────────────────────────────────────────

def generate_report(
    rfm: pd.DataFrame,
    output_path: str,
    business_context: dict = None,
    original_df: pd.DataFrame = None,
    mapping: dict = None,
) -> str:
    """Generate interactive HTML report with Plotly charts."""

    ctx = business_context or {}
    company = ctx.get("company_name", "")
    product = ctx.get("product_type", "")
    campaign_goal = ctx.get("campaign_goal", "")

    # ─── Summary Stats ──────────────────────────────────────
    total_customers = len(rfm)
    total_revenue = rfm["monetary"].sum()
    avg_frequency = rfm["frequency"].mean()
    avg_recency = rfm["recency"].mean()
    avg_monetary = rfm["monetary"].mean()

    # Segment distribution
    seg_dist = rfm["segment"].value_counts()
    seg_pct = (seg_dist / total_customers * 100).round(1)
    seg_revenue = rfm.groupby("segment")["monetary"].sum()
    seg_rev_pct = (seg_revenue / total_revenue * 100).round(1)

    # ─── Chart 1: Segment Distribution (Treemap) ────────────
    seg_data = pd.DataFrame({
        "segment": seg_dist.index,
        "count": seg_dist.values,
        "pct": seg_pct.values,
        "revenue": [seg_revenue.get(s, 0) for s in seg_dist.index],
        "rev_pct": [seg_rev_pct.get(s, 0) for s in seg_dist.index],
    })
    seg_data["color"] = seg_data["segment"].map(SEGMENT_COLORS)
    seg_data["label"] = seg_data.apply(
        lambda r: f"{r['segment']}<br>{r['count']:,} ({r['pct']}%)<br>R$ {r['revenue']:,.0f} ({r['rev_pct']}%)", axis=1
    )

    fig_treemap = px.treemap(
        seg_data, path=["segment"], values="count",
        color="segment", color_discrete_map=SEGMENT_COLORS,
        custom_data=["count", "pct", "revenue", "rev_pct"],
    )
    fig_treemap.update_traces(
        texttemplate="%{label}<br>%{customdata[0]:,} clientes (%{customdata[1]:.1f}%)<br>R$ %{customdata[2]:,.0f} (%{customdata[3]:.1f}%)",
        textfont_size=13,
    )
    fig_treemap.update_layout(
        title="Customer Segments — RFM Treemap",
        margin=dict(t=50, l=10, r=10, b=10), height=500,
    )

    # ─── Chart 2: RFM Scatter (R vs F, size=M) ─────────────
    fig_scatter = px.scatter(
        rfm, x="recency", y="frequency", size="monetary",
        color="segment", color_discrete_map=SEGMENT_COLORS,
        hover_data=["customer_id", "R", "F", "M", "monetary"],
        opacity=0.6, size_max=20,
    )
    fig_scatter.update_layout(
        title="Recency vs Frequency (bubble size = Monetary)",
        xaxis_title="Recency (days since last purchase)",
        yaxis_title="Frequency (# transactions)",
        height=500, margin=dict(t=50, b=40),
    )

    # ─── Chart 3: Segment Revenue Bar ───────────────────────
    seg_bar_data = seg_data.sort_values("revenue", ascending=True)
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        y=seg_bar_data["segment"], x=seg_bar_data["revenue"],
        orientation="h",
        marker_color=[SEGMENT_COLORS.get(s, "#888") for s in seg_bar_data["segment"]],
        text=[f"R$ {v:,.0f}" for v in seg_bar_data["revenue"]],
        textposition="auto",
    ))
    fig_bar.update_layout(
        title="Revenue by Segment",
        xaxis_title="Total Revenue (R$)", yaxis_title="",
        height=450, margin=dict(t=50, l=150, b=40),
    )

    # ─── Chart 4: Cluster 3D Scatter ───────────────────────
    fig_3d = px.scatter_3d(
        rfm, x="recency", y=np.log1p(rfm["frequency"]),
        z=np.log1p(rfm["monetary"]),
        color="cluster", symbol="cluster",
        hover_data=["customer_id", "segment", "monetary"],
        opacity=0.6,
        labels={"x": "Recency", "y": "log(Frequency)", "z": "log(Monetary)", "color": "Cluster"},
    )
    fig_3d.update_layout(
        title="K-Means Clusters (3D — Recency, Frequency, Monetary)",
        height=550, margin=dict(t=50, b=10),
    )

    # ─── Chart 5: RFM Score Distribution ────────────────────
    fig_rfm_hist = make_subplots(rows=1, cols=3, subplot_titles=("Recency Score", "Frequency Score", "Monetary Score"))
    for i, col in enumerate(["R", "F", "M"], 1):
        counts = rfm[col].value_counts().sort_index()
        fig_rfm_hist.add_trace(
            go.Bar(x=counts.index, y=counts.values, name=col,
                   marker_color=["#e74c3c", "#e67e22", "#f1c40f", "#2ecc71", "#27ae60"][: len(counts)]),
            row=1, col=i,
        )
    fig_rfm_hist.update_layout(
        title="RFM Score Distribution", height=350,
        showlegend=False, margin=dict(t=60, b=30),
    )

    # ─── Chart 6: Category analysis (if available) ──────────
    category_chart_html = ""
    if original_df is not None and mapping:
        cat_cols = [c for c in original_df.columns if "category" in c.lower() or "categoria" in c.lower()]
        if cat_cols:
            cat_col = cat_cols[0]
            cust_col = mapping["customer_id"]
            cat_seg = original_df.merge(
                rfm[["customer_id", "segment"]],
                left_on=cust_col, right_on="customer_id", how="inner"
            )
            cat_seg["_revenue"] = compute_revenue(original_df, mapping).values[:len(cat_seg)]
            cat_matrix = cat_seg.groupby(["segment", cat_col])["_revenue"].sum().reset_index()
            fig_cat = px.bar(
                cat_matrix, x="segment", y="_revenue", color=cat_col,
                barmode="group",
                category_orders={"segment": [s for s in SEGMENT_ORDER if s in cat_matrix["segment"].unique()]},
            )
            fig_cat.update_layout(
                title=f"Revenue by Segment & {cat_col}",
                xaxis_title="Segment", yaxis_title="Revenue (R$)",
                height=450, margin=dict(t=50, b=40),
            )
            category_chart_html = f"""
            <div class="chart-container">
                {fig_cat.to_html(full_html=False, include_plotlyjs=False)}
            </div>"""

    # ─── Cluster Profiles Table ─────────────────────────────
    cluster_profiles = rfm.groupby("cluster").agg(
        customers=("customer_id", "count"),
        avg_recency=("recency", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_monetary=("monetary", "mean"),
        total_revenue=("monetary", "sum"),
        top_segment=("segment", lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else "Mixed"),
    ).reset_index()
    cluster_profiles = cluster_profiles.round(1)

    cluster_table_rows = ""
    for _, row in cluster_profiles.iterrows():
        cluster_table_rows += f"""
        <tr>
            <td><strong>Cluster {int(row['cluster'])}</strong></td>
            <td>{int(row['customers']):,}</td>
            <td>{row['avg_recency']:.0f} days</td>
            <td>{row['avg_frequency']:.1f}</td>
            <td>R$ {row['avg_monetary']:,.0f}</td>
            <td>R$ {row['total_revenue']:,.0f}</td>
            <td>{row['top_segment']}</td>
        </tr>"""

    # ─── Segment Action Table ───────────────────────────────
    segment_actions = {
        "Champions": "Reward them. Upsell premium. Ask for referrals and reviews.",
        "Loyal Customers": "Upsell higher-value products. Engage with loyalty programs.",
        "Potential Loyalists": "Offer membership/loyalty programs. Recommend related products.",
        "Recent Customers": "Provide onboarding support. Start building the relationship.",
        "Promising": "Create brand awareness. Offer free trials or introductory discounts.",
        "Needing Attention": "Reactivate with personalized offers. Limited-time promotions.",
        "Can't Lose Them": "Win them back urgently. Personal outreach. Understand pain points.",
        "At Risk": "Send personalized reactivation campaigns. Survey for feedback.",
        "About to Sleep": "Re-engage with relevant content. Countdown urgency offers.",
        "Hibernating": "Offer deep discounts to reignite interest. Test different channels.",
        "Lost": "Ignore or very low-cost reactivation attempt. Focus budget elsewhere.",
    }

    action_rows = ""
    for seg in SEGMENT_ORDER:
        if seg in seg_dist.index:
            count = seg_dist[seg]
            pct = seg_pct[seg]
            rev = seg_revenue.get(seg, 0)
            color = SEGMENT_COLORS.get(seg, "#888")
            action = segment_actions.get(seg, "")
            action_rows += f"""
            <tr>
                <td><span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:{color};margin-right:6px;"></span>{seg}</td>
                <td>{count:,} ({pct}%)</td>
                <td>R$ {rev:,.0f}</td>
                <td>{action}</td>
            </tr>"""

    # ─── Business Context Section ───────────────────────────
    ctx_section = ""
    if any([company, product, campaign_goal]):
        ctx_items = []
        if company:
            ctx_items.append(f"<li><strong>Company:</strong> {company}</li>")
        if product:
            ctx_items.append(f"<li><strong>Product/Industry:</strong> {product}</li>")
        if campaign_goal:
            ctx_items.append(f"<li><strong>Campaign Goal:</strong> {campaign_goal}</li>")
        custom_insights = ctx.get("custom_insights", "")
        ctx_section = f"""
        <div class="context-box">
            <h3>Business Context</h3>
            <ul>{''.join(ctx_items)}</ul>
            {f'<div class="insight-box">{custom_insights}</div>' if custom_insights else ''}
        </div>"""

    # ─── Assemble HTML ──────────────────────────────────────
    title = f"RFM Analysis Report{' — ' + company if company else ''}"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<script src="https://cdn.plot.ly/plotly-2.35.0.min.js"></script>
<style>
    :root {{
        --bg: #0f1117; --surface: #1a1d27; --border: #2a2d3a;
        --text: #e4e4e7; --text-muted: #a1a1aa; --accent: #3b82f6;
    }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
        background: var(--bg); color: var(--text);
        line-height: 1.6; padding: 2rem;
    }}
    .container {{ max-width: 1200px; margin: 0 auto; }}
    h1 {{ font-size: 1.8rem; margin-bottom: 0.5rem; }}
    h2 {{ font-size: 1.3rem; margin: 2rem 0 1rem; color: var(--accent); }}
    h3 {{ font-size: 1.1rem; margin-bottom: 0.5rem; }}
    .subtitle {{ color: var(--text-muted); margin-bottom: 2rem; }}
    .kpi-grid {{
        display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem; margin-bottom: 2rem;
    }}
    .kpi-card {{
        background: var(--surface); border: 1px solid var(--border);
        border-radius: 12px; padding: 1.2rem;
    }}
    .kpi-value {{ font-size: 1.6rem; font-weight: 700; color: var(--accent); }}
    .kpi-label {{ font-size: 0.85rem; color: var(--text-muted); margin-top: 0.3rem; }}
    .chart-container {{
        background: var(--surface); border: 1px solid var(--border);
        border-radius: 12px; padding: 1rem; margin-bottom: 1.5rem;
    }}
    table {{
        width: 100%; border-collapse: collapse;
        background: var(--surface); border-radius: 12px; overflow: hidden;
    }}
    th, td {{ padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid var(--border); }}
    th {{ background: #1e2130; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }}
    td {{ font-size: 0.9rem; }}
    tr:last-child td {{ border-bottom: none; }}
    .context-box {{
        background: var(--surface); border: 1px solid var(--accent);
        border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem;
    }}
    .insight-box {{
        background: #1e2130; border-radius: 8px; padding: 1rem;
        margin-top: 1rem; white-space: pre-wrap;
    }}
    .footer {{
        text-align: center; color: var(--text-muted); font-size: 0.8rem;
        margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid var(--border);
    }}
    .js-plotly-plot .plotly .modebar {{ top: 5px !important; }}
</style>
</head>
<body>
<div class="container">
    <h1>{title}</h1>
    <p class="subtitle">Generated {datetime.now().strftime('%B %d, %Y at %H:%M')} &mdash; {total_customers:,} customers analyzed</p>

    {ctx_section}

    <!-- KPI Cards -->
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-value">{total_customers:,}</div>
            <div class="kpi-label">Total Customers</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">R$ {total_revenue:,.0f}</div>
            <div class="kpi-label">Total Revenue</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{avg_frequency:.1f}</div>
            <div class="kpi-label">Avg Frequency</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{avg_recency:.0f} days</div>
            <div class="kpi-label">Avg Recency</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">R$ {avg_monetary:,.0f}</div>
            <div class="kpi-label">Avg Customer Value</div>
        </div>
    </div>

    <!-- Segment Treemap -->
    <h2>Segment Overview</h2>
    <div class="chart-container">
        {fig_treemap.to_html(full_html=False, include_plotlyjs=False)}
    </div>

    <!-- RFM Scatter -->
    <h2>Customer Distribution</h2>
    <div class="chart-container">
        {fig_scatter.to_html(full_html=False, include_plotlyjs=False)}
    </div>

    <!-- Revenue by Segment -->
    <div class="chart-container">
        {fig_bar.to_html(full_html=False, include_plotlyjs=False)}
    </div>

    <!-- Category Breakdown -->
    {category_chart_html}

    <!-- RFM Score Distribution -->
    <h2>Score Distribution</h2>
    <div class="chart-container">
        {fig_rfm_hist.to_html(full_html=False, include_plotlyjs=False)}
    </div>

    <!-- Cluster Analysis -->
    <h2>K-Means Cluster Profiles</h2>
    <table>
        <thead>
            <tr>
                <th>Cluster</th><th>Customers</th><th>Avg Recency</th>
                <th>Avg Frequency</th><th>Avg Monetary</th><th>Total Revenue</th>
                <th>Dominant Segment</th>
            </tr>
        </thead>
        <tbody>{cluster_table_rows}</tbody>
    </table>

    <div class="chart-container" style="margin-top: 1.5rem;">
        {fig_3d.to_html(full_html=False, include_plotlyjs=False)}
    </div>

    <!-- Segment Actions -->
    <h2>Recommended Actions by Segment</h2>
    <table>
        <thead>
            <tr><th>Segment</th><th>Customers</th><th>Revenue</th><th>Recommended Action</th></tr>
        </thead>
        <tbody>{action_rows}</tbody>
    </table>

    <div class="footer">
        RFM Analysis &mdash; Generated by G4 OS &bull; Skill: rfm-analysis
    </div>
</div>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path


# ─── Main Pipeline ──────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="RFM Analysis & Customer Clustering")
    parser.add_argument("input_file", help="Path to CSV or XLSX file")
    parser.add_argument("output_dir", help="Directory for output files")
    parser.add_argument("--config", help="JSON config file with column mapping and context", default=None)
    parser.add_argument("--n-clusters", type=int, default=0, help="Number of clusters (0=auto)")
    parser.add_argument("--mapping-json", help="Column mapping as JSON string", default=None)
    parser.add_argument("--context-json", help="Business context as JSON string", default=None)
    args = parser.parse_args()

    # ─── Load Data ──────────────────────────────────────────
    ext = os.path.splitext(args.input_file)[1].lower()
    if ext in (".xlsx", ".xls"):
        df = pd.read_excel(args.input_file)
    elif ext == ".csv":
        df = pd.read_csv(args.input_file)
    elif ext == ".tsv":
        df = pd.read_csv(args.input_file, sep="\t")
    else:
        print(f"ERROR: Unsupported file format: {ext}", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(df):,} rows, {len(df.columns)} columns", file=sys.stderr)
    print(f"Columns: {list(df.columns)}", file=sys.stderr)

    # ─── Column Mapping ─────────────────────────────────────
    config = {}
    if args.config:
        with open(args.config) as f:
            config = json.load(f)

    if args.mapping_json:
        mapping = json.loads(args.mapping_json)
    elif "mapping" in config:
        mapping = config["mapping"]
    else:
        mapping = auto_detect_columns(df)

    print(f"Column mapping: {json.dumps(mapping)}", file=sys.stderr)

    if "customer_id" not in mapping or "transaction_date" not in mapping:
        print("ERROR: Could not auto-detect required columns (customer_id, transaction_date).", file=sys.stderr)
        print(f"Available columns: {list(df.columns)}", file=sys.stderr)
        print("Please provide mapping via --mapping-json or --config.", file=sys.stderr)
        sys.exit(1)

    # ─── Business Context ───────────────────────────────────
    if args.context_json:
        business_context = json.loads(args.context_json)
    elif "context" in config:
        business_context = config["context"]
    else:
        business_context = {}

    # ─── Compute RFM ────────────────────────────────────────
    print("Computing RFM scores...", file=sys.stderr)
    rfm = compute_rfm(df, mapping)
    print(f"RFM computed for {len(rfm):,} customers", file=sys.stderr)

    # ─── Clustering ─────────────────────────────────────────
    n_clusters = args.n_clusters
    if n_clusters == 0:
        print("Finding optimal K...", file=sys.stderr)
        n_clusters = find_optimal_k(rfm)
        print(f"Optimal K = {n_clusters}", file=sys.stderr)

    print(f"Running K-Means with {n_clusters} clusters...", file=sys.stderr)
    rfm = run_clustering(rfm, n_clusters)

    # ─── Save Outputs ───────────────────────────────────────
    os.makedirs(args.output_dir, exist_ok=True)

    # CSV
    csv_path = os.path.join(args.output_dir, "rfm_segments.csv")
    rfm.to_csv(csv_path, index=False)
    print(f"Saved: {csv_path}", file=sys.stderr)

    # Cluster profiles JSON
    cluster_profiles = rfm.groupby("cluster").agg(
        customers=("customer_id", "count"),
        avg_recency=("recency", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_monetary=("monetary", "mean"),
        total_revenue=("monetary", "sum"),
        top_segment=("segment", lambda x: x.mode().iloc[0]),
    ).reset_index()
    profiles_path = os.path.join(args.output_dir, "cluster_profiles.json")
    cluster_profiles.round(2).to_json(profiles_path, orient="records", indent=2)
    print(f"Saved: {profiles_path}", file=sys.stderr)

    # Segment summary JSON (for LLM consumption)
    seg_summary = rfm.groupby("segment").agg(
        customers=("customer_id", "count"),
        avg_recency=("recency", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_monetary=("monetary", "mean"),
        total_revenue=("monetary", "sum"),
    ).reset_index()
    seg_summary["pct_customers"] = (seg_summary["customers"] / len(rfm) * 100).round(1)
    seg_summary["pct_revenue"] = (seg_summary["total_revenue"] / rfm["monetary"].sum() * 100).round(1)
    summary_path = os.path.join(args.output_dir, "segment_summary.json")
    seg_summary.round(2).to_json(summary_path, orient="records", indent=2)
    print(f"Saved: {summary_path}", file=sys.stderr)

    # HTML Report
    report_path = os.path.join(args.output_dir, "rfm_report.html")
    generate_report(rfm, report_path, business_context, df, mapping)
    print(f"Saved: {report_path}", file=sys.stderr)

    # Print summary to stdout (for LLM to read)
    result = {
        "total_customers": int(len(rfm)),
        "total_revenue": float(rfm["monetary"].sum()),
        "n_clusters": n_clusters,
        "segments": seg_summary.to_dict(orient="records"),
        "clusters": cluster_profiles.round(2).to_dict(orient="records"),
        "files": {
            "segments_csv": csv_path,
            "report_html": report_path,
            "cluster_profiles": profiles_path,
            "segment_summary": summary_path,
        },
    }
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
