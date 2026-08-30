"""Research helpers for normalizing quote payloads and writing snapshots."""

from __future__ import annotations

from datetime import datetime
import csv
import json
import math
from pathlib import Path
from typing import Dict, Iterable, List


def flatten_quote_payload(payload: object) -> List[Dict[str, object]]:
    """Normalize common quote response shapes into a flat list of rows."""
    if isinstance(payload, list):
        rows: List[Dict[str, object]] = []
        for item in payload:
            rows.extend(flatten_quote_payload(item))
        return rows

    if not isinstance(payload, dict):
        return []

    results: List[Dict[str, object]] = []
    for symbol, value in payload.items():
        if not isinstance(value, dict):
            continue
        quote = value.get("quote", value)
        if not isinstance(quote, dict):
            quote = value
        row = {
            "symbol": symbol,
            "last_price": quote.get("lastPrice"),
            "net_change": quote.get("netChange"),
            "percent_change": quote.get("netPercentChange"),
            "bid_price": quote.get("bidPrice"),
            "ask_price": quote.get("askPrice"),
            "total_volume": quote.get("totalVolume"),
        }
        results.append(row)
    return results


def summarize_snapshot(
    rows: Iterable[Dict[str, object]],
    average_weight: float = 0.6,
    dispersion_weight: float = 0.4,
) -> Dict[str, object]:
    items = list(rows)
    gainers = sorted(
        [row for row in items if isinstance(row.get("percent_change"), (int, float))],
        key=lambda row: float(row["percent_change"]),
        reverse=True,
    )
    losers = list(reversed(gainers))
    active = sorted(
        [row for row in items if isinstance(row.get("total_volume"), (int, float))],
        key=lambda row: float(row["total_volume"]),
        reverse=True,
    )
    pct_changes = [float(row["percent_change"]) for row in items if isinstance(row.get("percent_change"), (int, float))]
    avg_pct = sum(pct_changes) / len(pct_changes) if pct_changes else 0.0
    dispersion = (
        math.sqrt(sum((value - avg_pct) ** 2 for value in pct_changes) / len(pct_changes))
        if pct_changes
        else 0.0
    )
    score = abs(avg_pct) * average_weight + dispersion * dispersion_weight
    return {
        "symbol_count": len(items),
        "top_gainers": gainers[:3],
        "top_losers": losers[:3],
        "most_active": active[:3],
        "average_percent_change": avg_pct,
        "dispersion_percent_change": dispersion,
        "watchlist_score": score,
    }


def write_snapshot(
    output_dir: str,
    watchlist_name: str,
    rows: List[Dict[str, object]],
    average_weight: float = 0.6,
    dispersion_weight: float = 0.4,
) -> str:
    now = datetime.now().astimezone()
    date_str = now.date().isoformat()
    timestamp = now.strftime("%H%M%S")
    path = Path(output_dir) / watchlist_name / date_str / f"{timestamp}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "created_at": now.isoformat(),
        "watchlist": watchlist_name,
        "rows": rows,
        "summary": summarize_snapshot(rows, average_weight=average_weight, dispersion_weight=dispersion_weight),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return str(path)


def write_snapshot_csv(output_dir: str, watchlist_name: str, rows: List[Dict[str, object]]) -> str:
    now = datetime.now().astimezone()
    date_str = now.date().isoformat()
    timestamp = now.strftime("%H%M%S")
    path = Path(output_dir) / watchlist_name / date_str / f"{timestamp}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "symbol",
        "last_price",
        "net_change",
        "percent_change",
        "bid_price",
        "ask_price",
        "total_volume",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name) for name in fieldnames})
    return str(path)


def render_snapshot_markdown(
    watchlist_name: str,
    rows: List[Dict[str, object]],
    average_weight: float = 0.6,
    dispersion_weight: float = 0.4,
) -> str:
    summary = summarize_snapshot(rows, average_weight=average_weight, dispersion_weight=dispersion_weight)
    lines = [
        f"# Watchlist Snapshot - {watchlist_name}",
        "",
        f"- Symbols: {summary['symbol_count']}",
        f"- Average % change: {summary['average_percent_change']:.3f}",
        f"- Dispersion of % change: {summary['dispersion_percent_change']:.3f}",
        f"- Watchlist score: {summary['watchlist_score']:.3f}",
        "",
        "## Top gainers",
    ]
    if summary["top_gainers"]:
        for row in summary["top_gainers"]:
            lines.append(
                f"- {row['symbol']}: {row.get('percent_change')}% ({row.get('net_change')} change)"
            )
    else:
        lines.append("- No gainers available.")

    lines.extend(["", "## Top losers"])
    if summary["top_losers"]:
        for row in summary["top_losers"]:
            lines.append(
                f"- {row['symbol']}: {row.get('percent_change')}% ({row.get('net_change')} change)"
            )
    else:
        lines.append("- No losers available.")

    lines.extend(["", "## Most active"])
    if summary["most_active"]:
        for row in summary["most_active"]:
            lines.append(f"- {row['symbol']}: volume {row.get('total_volume')}")
    else:
        lines.append("- No volume data available.")

    lines.extend(["", "## Review prompts"])
    lines.append("- Which names moved together, and why might that cluster matter?")
    lines.append("- Which move looked large relative to volume or spread?")
    lines.append("- Which symbol deserves a deeper follow-up pull tonight?")
    return "\n".join(lines) + "\n"


def load_snapshot(path: str) -> Dict[str, object]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def latest_snapshot_paths(output_dir: str, watchlist_name: str, limit: int = 2) -> List[str]:
    root = Path(output_dir) / watchlist_name
    if not root.exists():
        return []
    files = sorted(root.glob("*/*.json"))
    return [str(path) for path in files[-limit:]]


def compare_snapshot_rows(previous_rows: Iterable[Dict[str, object]], current_rows: Iterable[Dict[str, object]]) -> List[Dict[str, object]]:
    previous = {str(row.get("symbol")): row for row in previous_rows}
    current = {str(row.get("symbol")): row for row in current_rows}
    symbols = sorted(set(previous) | set(current))
    changes: List[Dict[str, object]] = []

    for symbol in symbols:
        old = previous.get(symbol, {})
        new = current.get(symbol, {})
        old_pct = old.get("percent_change")
        new_pct = new.get("percent_change")
        delta_pct = None
        if isinstance(old_pct, (int, float)) and isinstance(new_pct, (int, float)):
            delta_pct = float(new_pct) - float(old_pct)
        changes.append(
            {
                "symbol": symbol,
                "previous_percent_change": old_pct,
                "current_percent_change": new_pct,
                "delta_percent_change": delta_pct,
                "previous_last_price": old.get("last_price"),
                "current_last_price": new.get("last_price"),
            }
        )

    return sorted(
        changes,
        key=lambda row: abs(float(row["delta_percent_change"])) if isinstance(row.get("delta_percent_change"), (int, float)) else -1.0,
        reverse=True,
    )


def render_snapshot_comparison_markdown(
    watchlist_name: str,
    previous_payload: Dict[str, object],
    current_payload: Dict[str, object],
) -> str:
    previous_rows = previous_payload.get("rows", [])
    current_rows = current_payload.get("rows", [])
    changes = compare_snapshot_rows(previous_rows, current_rows)
    lines = [
        f"# Watchlist Comparison - {watchlist_name}",
        "",
        f"- Previous snapshot: {previous_payload.get('created_at')}",
        f"- Current snapshot: {current_payload.get('created_at')}",
        "",
        "## Largest changes in % move",
    ]
    if changes:
        for row in changes[:5]:
            lines.append(
                f"- {row['symbol']}: {row.get('previous_percent_change')}% -> {row.get('current_percent_change')}% "
                f"(delta {row.get('delta_percent_change')})"
            )
    else:
        lines.append("- No comparable rows found.")

    lines.extend(["", "## Review prompts"])
    lines.append("- Did dispersion widen or narrow between snapshots?")
    lines.append("- Which names reversed hardest, and what event might explain that?")
    lines.append("- Was the basket move broad or carried by only one or two names?")
    return "\n".join(lines) + "\n"


def latest_snapshot_path(output_dir: str, watchlist_name: str) -> str | None:
    paths = latest_snapshot_paths(output_dir, watchlist_name, limit=1)
    return paths[0] if paths else None


def available_watchlists(output_dir: str) -> List[str]:
    root = Path(output_dir)
    if not root.exists():
        return []
    return sorted(path.name for path in root.iterdir() if path.is_dir())


def build_signal_sheet_entries(watchlist_payloads: Dict[str, Dict[str, object]]) -> List[Dict[str, object]]:
    entries: List[Dict[str, object]] = []
    for name, payload in watchlist_payloads.items():
        summary = payload.get("summary", {})
        if not isinstance(summary, dict):
            summary = {}
        entries.append(
            {
                "watchlist": name,
                "created_at": payload.get("created_at"),
                "symbol_count": summary.get("symbol_count", 0),
                "average_percent_change": summary.get("average_percent_change", 0.0),
                "dispersion_percent_change": summary.get("dispersion_percent_change", 0.0),
                "watchlist_score": summary.get("watchlist_score", 0.0),
                "top_gainer": (summary.get("top_gainers") or [{}])[0].get("symbol"),
                "top_loser": (summary.get("top_losers") or [{}])[0].get("symbol"),
                "most_active": (summary.get("most_active") or [{}])[0].get("symbol"),
            }
        )
    return sorted(
        entries,
        key=lambda row: (
            float(row.get("watchlist_score", 0.0)),
            abs(float(row.get("average_percent_change", 0.0))),
        ),
        reverse=True,
    )


def render_signal_sheet_markdown(entries: List[Dict[str, object]], date_str: str) -> str:
    lines = [
        f"# Nightly Signal Sheet - {date_str}",
        "",
        "## Watchlist ranking",
    ]
    if not entries:
        lines.append("- No watchlist snapshots available yet.")
        return "\n".join(lines) + "\n"

    for entry in entries:
        lines.append(
            f"- {entry['watchlist']}: score {float(entry.get('watchlist_score', 0.0)):.3f}, "
            f"avg {float(entry.get('average_percent_change', 0.0)):.3f}%, "
            f"dispersion {float(entry.get('dispersion_percent_change', 0.0)):.3f}, "
            f"leader {entry.get('top_gainer')}, laggard {entry.get('top_loser')}, active {entry.get('most_active')}"
        )

    lines.extend(["", "## Interpretation prompts"])
    lines.append("- Which watchlist showed the broadest move versus a one-name move?")
    lines.append("- Where was dispersion unusually high, and does that suggest rotation or idiosyncratic news?")
    lines.append("- Which basket should you revisit first tomorrow morning?")
    return "\n".join(lines) + "\n"


def write_signal_sheet(output_dir: str, date_str: str, markdown: str) -> str:
    path = Path(output_dir) / f"{date_str}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")
    return str(path)


def markdown_to_basic_html(title: str, markdown: str) -> str:
    body_lines = []
    for line in markdown.splitlines():
        if line.startswith("# "):
            body_lines.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("## "):
            body_lines.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("- "):
            body_lines.append(f"<p>{line}</p>")
        elif line.strip():
            body_lines.append(f"<p>{line}</p>")
    body = "\n".join(body_lines)
    return (
        "<!doctype html>\n"
        "<html><head><meta charset='utf-8'>"
        f"<title>{title}</title>"
        "<style>body{font-family:Georgia,serif;max-width:900px;margin:40px auto;padding:0 20px;line-height:1.5}"
        "h1,h2{font-family:Helvetica,Arial,sans-serif}p{margin:0.5rem 0}</style>"
        "</head><body>\n"
        f"{body}\n"
        "</body></html>\n"
    )


def write_html_export(output_dir: str, name: str, date_str: str, markdown: str) -> str:
    path = Path(output_dir) / name / f"{date_str}.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    html = markdown_to_basic_html(name, markdown)
    path.write_text(html, encoding="utf-8")
    return str(path)


def render_dashboard_markdown(
    date_str: str,
    signal_sheet_path: str | None,
    latest_daily_readme_path: str | None,
    entries: List[Dict[str, object]],
) -> str:
    lines = [
        f"# Quant Live Dashboard - {date_str}",
        "",
        "## Latest files",
        "",
        f"- Signal sheet: {signal_sheet_path or 'not found'}",
        f"- Daily readme: {latest_daily_readme_path or 'not found'}",
        "",
        "## Watchlist pulse",
    ]
    if entries:
        for entry in entries[:5]:
            lines.append(
                f"- {entry['watchlist']}: score {float(entry.get('watchlist_score', 0.0)):.3f}, "
                f"avg {float(entry.get('average_percent_change', 0.0)):.3f}%, "
                f"dispersion {float(entry.get('dispersion_percent_change', 0.0)):.3f}, "
                f"leader {entry.get('top_gainer')}, active {entry.get('most_active')}"
            )
    else:
        lines.append("- No watchlist entries available yet.")

    lines.extend(["", "## Tonight's focus"])
    lines.append("- Review the highest-dispersion watchlist first.")
    lines.append("- Compare the broadest basket move with the largest single-name reversal.")
    lines.append("- Decide which watchlist deserves a fresh snapshot tomorrow morning.")
    return "\n".join(lines) + "\n"


def bundle_end_of_day(
    bundle_dir: str,
    date_str: str,
    signal_sheet_path: str | None,
    daily_readme_path: str | None,
    dashboard_path: str | None,
) -> str:
    root = Path(bundle_dir) / date_str
    root.mkdir(parents=True, exist_ok=True)
    manifest = {
        "date": date_str,
        "signal_sheet": signal_sheet_path,
        "daily_readme": daily_readme_path,
        "dashboard": dashboard_path,
    }
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return str(root)


def load_signal_sheet_entries(signal_sheet_dir: str) -> List[Dict[str, object]]:
    root = Path(signal_sheet_dir)
    if not root.exists():
        return []

    rows: List[Dict[str, object]] = []
    for path in sorted(root.glob("*.md")):
        date_str = path.stem
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.startswith("- ") or ": score " not in line:
                continue
            try:
                watchlist, rest = line[2:].split(": score ", 1)
                score_str, tail = rest.split(", avg ", 1)
                avg_str, tail = tail.split("%, dispersion ", 1)
                dispersion_str = tail.split(",", 1)[0]
                rows.append(
                    {
                        "date": date_str,
                        "watchlist": watchlist.strip(),
                        "watchlist_score": float(score_str),
                        "average_percent_change": float(avg_str),
                        "dispersion_percent_change": float(dispersion_str),
                    }
                )
            except ValueError:
                continue
    return rows


def summarize_watchlist_history(rows: Iterable[Dict[str, object]], lookback: int = 5) -> List[Dict[str, object]]:
    items = list(rows)
    if lookback > 0:
        dates = sorted({str(row.get("date")) for row in items})
        keep = set(dates[-lookback:])
        items = [row for row in items if str(row.get("date")) in keep]

    grouped: Dict[str, List[Dict[str, object]]] = {}
    for row in items:
        grouped.setdefault(str(row.get("watchlist")), []).append(row)

    summary: List[Dict[str, object]] = []
    for watchlist, entries in grouped.items():
        entries = sorted(entries, key=lambda row: str(row.get("date")))
        scores = [float(row.get("watchlist_score", 0.0)) for row in entries]
        avg_moves = [float(row.get("average_percent_change", 0.0)) for row in entries]
        dispersions = [float(row.get("dispersion_percent_change", 0.0)) for row in entries]
        summary.append(
            {
                "watchlist": watchlist,
                "days_seen": len(entries),
                "avg_score": sum(scores) / len(scores) if scores else 0.0,
                "latest_score": scores[-1] if scores else 0.0,
                "score_change": (scores[-1] - scores[0]) if len(scores) >= 2 else 0.0,
                "avg_abs_move": sum(abs(value) for value in avg_moves) / len(avg_moves) if avg_moves else 0.0,
                "avg_dispersion": sum(dispersions) / len(dispersions) if dispersions else 0.0,
            }
        )

    return sorted(
        summary,
        key=lambda row: (
            float(row.get("avg_score", 0.0)),
            float(row.get("latest_score", 0.0)),
        ),
        reverse=True,
    )


def render_history_sheet_markdown(rows: List[Dict[str, object]], lookback: int) -> str:
    lines = [
        f"# Watchlist History Sheet - Last {lookback} Day{'s' if lookback != 1 else ''}",
        "",
        "## Persistent leaders",
    ]
    if not rows:
        lines.append("- No signal-sheet history available yet.")
        return "\n".join(lines) + "\n"

    for row in rows:
        lines.append(
            f"- {row['watchlist']}: avg score {float(row.get('avg_score', 0.0)):.3f}, "
            f"latest {float(row.get('latest_score', 0.0)):.3f}, "
            f"change {float(row.get('score_change', 0.0)):.3f}, "
            f"avg dispersion {float(row.get('avg_dispersion', 0.0)):.3f}"
        )

    lines.extend(["", "## Review prompts"])
    lines.append("- Which watchlist has been persistently elevated instead of just noisy today?")
    lines.append("- Which basket is cooling off and no longer deserves top billing?")
    lines.append("- Which group shows repeated high dispersion and may be a better source of single-name follow-up?")
    return "\n".join(lines) + "\n"
