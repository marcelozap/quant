"""Descriptive analytics for Green Machine's imported closed-trade history."""

from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Any, Dict, Iterable


def summarize_closed_trades(records: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    trades = [record["payload"] for record in records if isinstance(record.get("payload"), dict)]
    gains = [_number(trade.get("gain_loss")) for trade in trades]
    returns = [_number(trade.get("return_pct")) for trade in trades]
    gains = [value for value in gains if value is not None]
    returns = [value for value in returns if value is not None]

    by_underlying: dict[str, list[Dict[str, Any]]] = defaultdict(list)
    by_option_type: dict[str, list[Dict[str, Any]]] = defaultdict(list)
    by_month: dict[str, list[Dict[str, Any]]] = defaultdict(list)
    by_dte_bucket: dict[str, list[Dict[str, Any]]] = defaultdict(list)
    for trade in trades:
        by_underlying[str(trade.get("underlying") or "UNKNOWN")].append(trade)
        by_option_type[str(trade.get("option_type") or "OTHER")].append(trade)
        by_month[str(trade.get("closed_date") or "UNKNOWN")[:7]].append(trade)
        by_dte_bucket[_dte_bucket(_number(trade.get("dte_at_close")))].append(trade)

    return {
        "trade_count": len(trades),
        "win_count": sum(value > 0 for value in gains),
        "loss_count": sum(value < 0 for value in gains),
        "flat_count": sum(value == 0 for value in gains),
        "win_rate": (sum(value > 0 for value in gains) / len(gains)) if gains else None,
        "total_gain_loss": sum(gains),
        "average_gain_loss": mean(gains) if gains else None,
        "average_return_pct": mean(returns) if returns else None,
        "by_underlying": _group_rows(by_underlying),
        "by_option_type": _group_rows(by_option_type),
        "by_month": _group_rows(by_month),
        "by_dte_bucket": _group_rows(by_dte_bucket),
        "caveat": (
            "Descriptive closed-trade history only. It does not include entry timing, position sizing context, "
            "open positions, or a controlled market-regime comparison. Treat groups as review prompts, not signals."
        ),
    }


def _group_rows(groups: Dict[str, list[Dict[str, Any]]]) -> list[Dict[str, Any]]:
    rows = []
    for name, trades in groups.items():
        gains = [_number(trade.get("gain_loss")) for trade in trades]
        gains = [value for value in gains if value is not None]
        rows.append(
            {
                "group": name,
                "trade_count": len(trades),
                "total_gain_loss": sum(gains),
                "average_gain_loss": mean(gains) if gains else None,
                "win_rate": (sum(value > 0 for value in gains) / len(gains)) if gains else None,
            }
        )
    return sorted(rows, key=lambda row: (-row["trade_count"], row["group"]))


def _number(value: object) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _dte_bucket(value: float | None) -> str:
    if value is None:
        return "Unknown"
    if value <= 0:
        return "0 DTE"
    if value <= 7:
        return "1-7 DTE"
    if value <= 30:
        return "8-30 DTE"
    return "31+ DTE"
