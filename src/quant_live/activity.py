"""Activity logging and daily markdown summaries for quant-live."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Dict, Iterable, List


@dataclass(frozen=True)
class DailySummary:
    date: str
    total_events: int
    commands: Dict[str, int]
    symbols: List[str]
    notes: List[str]


def append_activity(log_path: str, payload: Dict[str, object]) -> None:
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = dict(payload)
    entry["timestamp"] = datetime.now().astimezone().isoformat()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True))
        handle.write("\n")


def load_activities_for_date(log_path: str, date_str: str) -> List[Dict[str, object]]:
    path = Path(log_path)
    if not path.exists():
        return []

    rows: List[Dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            raw = line.strip()
            if not raw:
                continue
            payload = json.loads(raw)
            timestamp = str(payload.get("timestamp", ""))
            if timestamp.startswith(date_str):
                rows.append(payload)
    return rows


def summarize_activities(entries: Iterable[Dict[str, object]], date_str: str) -> DailySummary:
    commands = Counter()
    symbols = Counter()
    notes: List[str] = []

    for entry in entries:
        command = str(entry.get("command", "unknown"))
        commands[command] += 1

        for symbol in entry.get("symbols", []) or []:
            symbols[str(symbol)] += 1

        note = str(entry.get("note", "")).strip()
        if note:
            notes.append(note)

    return DailySummary(
        date=date_str,
        total_events=sum(commands.values()),
        commands=dict(commands),
        symbols=list(symbols.keys()),
        notes=notes,
    )


def build_daily_readme(summary: DailySummary) -> str:
    lines = [
        f"# Daily Readme - {summary.date}",
        "",
        "## What happened today",
        "",
        f"- Total tracked actions: {summary.total_events}",
    ]

    if summary.commands:
        lines.append("- Commands run:")
        for command, count in sorted(summary.commands.items()):
            lines.append(f"  - `{command}` x {count}")
    else:
        lines.append("- No tracked commands yet today.")

    lines.extend(["", "## Symbols touched", ""])
    if summary.symbols:
        lines.append("- " + ", ".join(summary.symbols))
    else:
        lines.append("- None recorded today.")

    lines.extend(["", "## Quick review", ""])
    lines.append("- What was the most useful signal or data pull today?")
    lines.append("- Which call or workflow felt noisy, wasteful, or unclear?")
    lines.append("- What would make tomorrow's run more deliberate?")

    if summary.notes:
        lines.extend(["", "## Notes captured", ""])
        for note in summary.notes:
            lines.append(f"- {note}")

    lines.extend(["", "## Next night check", ""])
    lines.append("- Re-read the largest symbol group you touched today and explain why it mattered.")
    lines.append("- Check whether your call budget matched what you actually learned.")

    return "\n".join(lines) + "\n"


def write_daily_readme(output_dir: str, date_str: str, markdown: str) -> str:
    path = Path(output_dir) / f"{date_str}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")
    return str(path)
