"""Execution and TCA-style helpers for desk-oriented analysis."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List


def _to_float(value: object) -> float | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value))
    except ValueError:
        return None


def _slippage_bps(side: str, fill_price: float | None, benchmark_price: float | None) -> float | None:
    if fill_price is None or benchmark_price in (None, 0):
        return None
    if side.upper() == "SELL":
        return ((benchmark_price - fill_price) / benchmark_price) * 10000.0
    return ((fill_price - benchmark_price) / benchmark_price) * 10000.0


def load_execution_rows(path: str) -> List[Dict[str, object]]:
    file_path = Path(path)
    if file_path.suffix.lower() == ".json":
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return [row for row in payload if isinstance(row, dict)]
        if isinstance(payload, dict) and isinstance(payload.get("rows"), list):
            return [row for row in payload["rows"] if isinstance(row, dict)]
        raise ValueError("JSON execution input must be a list of rows or an object with a 'rows' list")

    with file_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [dict(row) for row in reader]


def summarize_execution_rows(rows: Iterable[Dict[str, object]]) -> Dict[str, object]:
    items = list(rows)
    normalized: List[Dict[str, object]] = []
    arrival_weighted = 0.0
    decision_weighted = 0.0
    arrival_weight = 0.0
    decision_weight = 0.0
    buy_count = 0
    sell_count = 0
    total_notional = 0.0
    venue_stats: Dict[str, Dict[str, float]] = {}
    symbol_stats: Dict[str, Dict[str, float]] = {}

    for row in items:
        symbol = str(row.get("symbol", "")).upper()
        side = str(row.get("side", "BUY")).upper()
        quantity = abs(_to_float(row.get("quantity")) or 0.0)
        fill_price = _to_float(row.get("fill_price"))
        arrival_price = _to_float(row.get("arrival_price"))
        decision_price = _to_float(row.get("decision_price"))
        venue = str(row.get("venue", "UNKNOWN")).upper()
        strategy = str(row.get("strategy", "UNSPECIFIED"))
        asset_class = str(row.get("asset_class", "EQUITY")).upper()

        arrival_bps = _slippage_bps(side, fill_price, arrival_price)
        decision_bps = _slippage_bps(side, fill_price, decision_price)
        notional = quantity * (fill_price or 0.0)

        normalized.append(
            {
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "fill_price": fill_price,
                "arrival_price": arrival_price,
                "decision_price": decision_price,
                "arrival_slippage_bps": arrival_bps,
                "decision_slippage_bps": decision_bps,
                "venue": venue,
                "strategy": strategy,
                "asset_class": asset_class,
                "notional": notional,
            }
        )

        total_notional += notional
        if side == "SELL":
            sell_count += 1
        else:
            buy_count += 1

        if arrival_bps is not None and quantity > 0:
            arrival_weighted += arrival_bps * quantity
            arrival_weight += quantity

        if decision_bps is not None and quantity > 0:
            decision_weighted += decision_bps * quantity
            decision_weight += quantity

        venue_entry = venue_stats.setdefault(venue, {"fills": 0.0, "qty": 0.0, "arrival_bps_weighted": 0.0, "arrival_weight": 0.0})
        venue_entry["fills"] += 1
        venue_entry["qty"] += quantity
        if arrival_bps is not None and quantity > 0:
            venue_entry["arrival_bps_weighted"] += arrival_bps * quantity
            venue_entry["arrival_weight"] += quantity

        symbol_entry = symbol_stats.setdefault(symbol, {"fills": 0.0, "qty": 0.0, "arrival_bps_weighted": 0.0, "arrival_weight": 0.0})
        symbol_entry["fills"] += 1
        symbol_entry["qty"] += quantity
        if arrival_bps is not None and quantity > 0:
            symbol_entry["arrival_bps_weighted"] += arrival_bps * quantity
            symbol_entry["arrival_weight"] += quantity

    venue_rows = []
    for venue, entry in venue_stats.items():
        avg_arrival = entry["arrival_bps_weighted"] / entry["arrival_weight"] if entry["arrival_weight"] else 0.0
        venue_rows.append(
            {
                "venue": venue,
                "fills": int(entry["fills"]),
                "quantity": entry["qty"],
                "avg_arrival_slippage_bps": avg_arrival,
            }
        )
    venue_rows.sort(key=lambda row: row["avg_arrival_slippage_bps"], reverse=True)

    symbol_rows = []
    for symbol, entry in symbol_stats.items():
        avg_arrival = entry["arrival_bps_weighted"] / entry["arrival_weight"] if entry["arrival_weight"] else 0.0
        symbol_rows.append(
            {
                "symbol": symbol,
                "fills": int(entry["fills"]),
                "quantity": entry["qty"],
                "avg_arrival_slippage_bps": avg_arrival,
            }
        )
    symbol_rows.sort(key=lambda row: row["avg_arrival_slippage_bps"], reverse=True)

    return {
        "fills": len(normalized),
        "buy_fills": buy_count,
        "sell_fills": sell_count,
        "total_notional": total_notional,
        "avg_arrival_slippage_bps": (arrival_weighted / arrival_weight) if arrival_weight else 0.0,
        "avg_decision_slippage_bps": (decision_weighted / decision_weight) if decision_weight else 0.0,
        "worst_venues": venue_rows[:5],
        "best_venues": list(reversed(venue_rows[-5:])),
        "worst_symbols": symbol_rows[:5],
        "best_symbols": list(reversed(symbol_rows[-5:])),
        "rows": normalized,
    }


def render_execution_report_markdown(report_name: str, summary: Dict[str, object]) -> str:
    lines = [
        f"# Execution Report - {report_name}",
        "",
        "## Desk summary",
        f"- Fills: {summary.get('fills', 0)}",
        f"- Buy fills: {summary.get('buy_fills', 0)}",
        f"- Sell fills: {summary.get('sell_fills', 0)}",
        f"- Total notional: {float(summary.get('total_notional', 0.0)):.2f}",
        f"- Avg arrival slippage: {float(summary.get('avg_arrival_slippage_bps', 0.0)):.3f} bps",
        f"- Avg decision slippage: {float(summary.get('avg_decision_slippage_bps', 0.0)):.3f} bps",
        "",
        "## Worst venues by arrival slippage",
    ]
    worst_venues = summary.get("worst_venues", [])
    if isinstance(worst_venues, list) and worst_venues:
        for row in worst_venues:
            lines.append(
                f"- {row['venue']}: {float(row.get('avg_arrival_slippage_bps', 0.0)):.3f} bps across {int(row.get('fills', 0))} fills"
            )
    else:
        lines.append("- No venue data available.")

    lines.extend(["", "## Worst symbols by arrival slippage"])
    worst_symbols = summary.get("worst_symbols", [])
    if isinstance(worst_symbols, list) and worst_symbols:
        for row in worst_symbols:
            lines.append(
                f"- {row['symbol']}: {float(row.get('avg_arrival_slippage_bps', 0.0)):.3f} bps across {int(row.get('fills', 0))} fills"
            )
    else:
        lines.append("- No symbol data available.")

    lines.extend(["", "## Review prompts"])
    lines.append("- Which venues are repeatedly costing you the most slippage?")
    lines.append("- Are the worst symbols genuinely harder to trade, or is the workflow around them weaker?")
    lines.append("- Which fills deserve a deeper look for urgency, liquidity, or benchmark selection issues?")
    return "\n".join(lines) + "\n"


def write_execution_summary(output_dir: str, report_name: str, summary: Dict[str, object]) -> str:
    now = Path(output_dir)
    now.mkdir(parents=True, exist_ok=True)
    path = now / f"{report_name}.json"
    path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return str(path)
