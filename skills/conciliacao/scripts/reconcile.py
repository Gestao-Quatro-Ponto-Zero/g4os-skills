#!/usr/bin/env python3
"""
Financial Reconciliation Engine
Matches transactions from two sides (reference vs bank) using multi-pass strategy.
Input: two CSV files in canonical schema + config JSON.
Output: JSON with matched, divergences, unmatched arrays.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from itertools import combinations

import pandas as pd


def load_canonical(path: str, side: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    df["side"] = side
    df["_matched"] = False
    df["_match_pass"] = None
    df["_match_idx"] = None
    df["_match_delta_amount"] = None
    df["_match_delta_days"] = None
    return df


def exact_match(a: pd.DataFrame, b: pd.DataFrame) -> list[dict]:
    """Pass 1: Exact date + exact amount."""
    matches = []
    for i, row_a in a[~a["_matched"]].iterrows():
        candidates = b[
            (~b["_matched"])
            & (b["date"] == row_a["date"])
            & ((b["amount"] - row_a["amount"]).abs() < 0.005)
        ]
        if len(candidates) >= 1:
            j = candidates.index[0]
            matches.append(_record_match(a, b, i, j, "exact"))
    return matches


def date_flex_match(a: pd.DataFrame, b: pd.DataFrame, days_tolerance: int = 3) -> list[dict]:
    """Pass 2: Exact amount, date within ±N business days."""
    matches = []
    for i, row_a in a[~a["_matched"]].iterrows():
        date_lo = row_a["date"] - timedelta(days=days_tolerance + 2)  # extra for weekends
        date_hi = row_a["date"] + timedelta(days=days_tolerance + 2)
        candidates = b[
            (~b["_matched"])
            & (b["date"] >= date_lo)
            & (b["date"] <= date_hi)
            & ((b["amount"] - row_a["amount"]).abs() < 0.005)
        ]
        if len(candidates) >= 1:
            # Pick closest date
            deltas = (candidates["date"] - row_a["date"]).abs()
            j = deltas.idxmin()
            delta_days = int((b.loc[j, "date"] - row_a["date"]).days)
            matches.append(_record_match(a, b, i, j, "date_flex", delta_days=delta_days))
    return matches


def amount_flex_match(
    a: pd.DataFrame, b: pd.DataFrame, amount_tolerance_pct: float = 0.01, amount_tolerance_abs: float = 0.50
) -> list[dict]:
    """Pass 3: Exact date, amount within tolerance."""
    matches = []
    for i, row_a in a[~a["_matched"]].iterrows():
        candidates = b[(~b["_matched"]) & (b["date"] == row_a["date"])]
        for j, row_b in candidates.iterrows():
            delta = abs(row_b["amount"] - row_a["amount"])
            pct = delta / row_a["amount"] if row_a["amount"] != 0 else float("inf")
            if delta <= amount_tolerance_abs or pct <= amount_tolerance_pct:
                matches.append(
                    _record_match(a, b, i, j, "amount_flex", delta_amount=round(row_b["amount"] - row_a["amount"], 2))
                )
                break
    return matches


def fuzzy_match(
    a: pd.DataFrame,
    b: pd.DataFrame,
    days_tolerance: int = 3,
    amount_tolerance_pct: float = 0.01,
    amount_tolerance_abs: float = 0.50,
) -> list[dict]:
    """Pass 4: Both date and amount within tolerance."""
    matches = []
    for i, row_a in a[~a["_matched"]].iterrows():
        date_lo = row_a["date"] - timedelta(days=days_tolerance + 2)
        date_hi = row_a["date"] + timedelta(days=days_tolerance + 2)
        candidates = b[(~b["_matched"]) & (b["date"] >= date_lo) & (b["date"] <= date_hi)]
        for j, row_b in candidates.iterrows():
            delta = abs(row_b["amount"] - row_a["amount"])
            pct = delta / row_a["amount"] if row_a["amount"] != 0 else float("inf")
            if delta <= amount_tolerance_abs or pct <= amount_tolerance_pct:
                delta_days = int((row_b["date"] - row_a["date"]).days)
                delta_amount = round(row_b["amount"] - row_a["amount"], 2)
                matches.append(
                    _record_match(a, b, i, j, "fuzzy", delta_days=delta_days, delta_amount=delta_amount)
                )
                break
    return matches


def batch_match(a: pd.DataFrame, b: pd.DataFrame, days_tolerance: int = 3) -> list[dict]:
    """Pass 5: Multiple items on side A sum to one item on side B."""
    matches = []
    unmatched_b = b[~b["_matched"]]
    unmatched_a = a[~a["_matched"]]

    for j, row_b in unmatched_b.iterrows():
        date_lo = row_b["date"] - timedelta(days=days_tolerance + 2)
        date_hi = row_b["date"] + timedelta(days=days_tolerance + 2)
        candidates_a = unmatched_a[
            (~unmatched_a["_matched"]) & (unmatched_a["date"] >= date_lo) & (unmatched_a["date"] <= date_hi)
        ]
        if len(candidates_a) < 2 or len(candidates_a) > 15:
            continue

        target = round(row_b["amount"], 2)
        # Try subsets of size 2..min(len, 6)
        found = False
        for size in range(2, min(len(candidates_a) + 1, 7)):
            for combo in combinations(candidates_a.index, size):
                combo_sum = round(sum(a.loc[idx, "amount"] for idx in combo), 2)
                if abs(combo_sum - target) < 0.01:
                    # Mark all as matched
                    b.at[j, "_matched"] = True
                    b.at[j, "_match_pass"] = "batch"
                    for idx in combo:
                        a.at[idx, "_matched"] = True
                        a.at[idx, "_match_pass"] = "batch"
                        a.at[idx, "_match_idx"] = int(j)
                    matches.append({
                        "pass": "batch",
                        "side_a_indices": [int(idx) for idx in combo],
                        "side_b_index": int(j),
                        "amount_a_total": combo_sum,
                        "amount_b": target,
                        "items_a": [
                            {
                                "date": str(a.loc[idx, "date"].date()),
                                "amount": a.loc[idx, "amount"],
                                "description": a.loc[idx, "description"],
                            }
                            for idx in combo
                        ],
                        "item_b": {
                            "date": str(row_b["date"].date()),
                            "amount": row_b["amount"],
                            "description": row_b["description"],
                        },
                    })
                    # Update unmatched_a view
                    unmatched_a = a[~a["_matched"]]
                    found = True
                    break
            if found:
                break
    return matches


def _record_match(
    a: pd.DataFrame,
    b: pd.DataFrame,
    i: int,
    j: int,
    pass_name: str,
    delta_days: int = 0,
    delta_amount: float = 0.0,
) -> dict:
    a.at[i, "_matched"] = True
    a.at[i, "_match_pass"] = pass_name
    a.at[i, "_match_idx"] = j
    a.at[i, "_match_delta_amount"] = delta_amount
    a.at[i, "_match_delta_days"] = delta_days
    b.at[j, "_matched"] = True
    b.at[j, "_match_pass"] = pass_name
    b.at[j, "_match_idx"] = i
    return {
        "pass": pass_name,
        "side_a": {
            "index": int(i),
            "date": str(a.loc[i, "date"].date()),
            "amount": a.loc[i, "amount"],
            "description": a.loc[i, "description"],
            "reference_id": a.loc[i].get("reference_id", ""),
        },
        "side_b": {
            "index": int(j),
            "date": str(b.loc[j, "date"].date()),
            "amount": b.loc[j, "amount"],
            "description": b.loc[j, "description"],
            "reference_id": b.loc[j].get("reference_id", ""),
        },
        "delta_days": delta_days,
        "delta_amount": delta_amount,
    }


def run(config: dict):
    a = load_canonical(config["side_a_file"], "A")
    b = load_canonical(config["side_b_file"], "B")

    days_tol = config.get("days_tolerance", 3)
    amt_pct = config.get("amount_tolerance_pct", 0.01)
    amt_abs = config.get("amount_tolerance_abs", 0.50)

    all_matches = []
    batch_matches = []

    # Pass 1: exact
    all_matches.extend(exact_match(a, b))
    # Pass 2: date flex
    all_matches.extend(date_flex_match(a, b, days_tol))
    # Pass 3: amount flex
    all_matches.extend(amount_flex_match(a, b, amt_pct, amt_abs))
    # Pass 4: fuzzy
    all_matches.extend(fuzzy_match(a, b, days_tol, amt_pct, amt_abs))
    # Pass 5: batch
    batch_matches.extend(batch_match(a, b, days_tol))

    # Separate exact matches from divergences
    matched = [m for m in all_matches if m["pass"] == "exact"]
    divergences = [m for m in all_matches if m["pass"] != "exact"]

    # Unmatched
    unmatched_a = []
    for i, row in a[~a["_matched"]].iterrows():
        unmatched_a.append({
            "index": int(i),
            "date": str(row["date"].date()),
            "amount": row["amount"],
            "description": row["description"],
            "reference_id": row.get("reference_id", ""),
            "source_file": row.get("source_file", ""),
        })

    unmatched_b = []
    for j, row in b[~b["_matched"]].iterrows():
        unmatched_b.append({
            "index": int(j),
            "date": str(row["date"].date()),
            "amount": row["amount"],
            "description": row["description"],
            "reference_id": row.get("reference_id", ""),
            "source_file": row.get("source_file", ""),
        })

    result = {
        "summary": {
            "total_side_a": len(a),
            "total_side_b": len(b),
            "matched_exact": len(matched),
            "matched_divergent": len(divergences),
            "matched_batch": len(batch_matches),
            "unmatched_side_a": len(unmatched_a),
            "unmatched_side_b": len(unmatched_b),
            "total_amount_side_a": round(a["amount"].sum(), 2),
            "total_amount_side_b": round(b["amount"].sum(), 2),
            "amount_difference": round(b["amount"].sum() - a["amount"].sum(), 2),
        },
        "matched": matched,
        "divergences": divergences,
        "batch_matches": batch_matches,
        "unmatched_side_a": unmatched_a,
        "unmatched_side_b": unmatched_b,
    }

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Financial Reconciliation Engine")
    parser.add_argument("config_json", help="Path to config JSON file")
    parser.add_argument("--output", "-o", help="Output JSON path (default: stdout)")
    args = parser.parse_args()

    with open(args.config_json) as f:
        config = json.load(f)

    result = run(config)

    output = json.dumps(result, indent=2, ensure_ascii=False, default=str)
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Results written to {args.output}")
    else:
        print(output)
