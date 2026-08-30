"""Read-only candidate-file discovery for Green Machine's private data audit."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable


INTERESTING_EXTENSIONS = {".csv", ".tsv", ".xlsx", ".xls", ".json", ".pdf", ".txt", ".md", ".png", ".jpg", ".jpeg", ".heic"}
EXCLUDED_DIRS = {".git", ".venv", "node_modules", "Library", "Applications", ".Trash"}
KEYWORDS = ("trade", "schwab", "portfolio", "broker", "market", "stock", "quant", "earning", "watchlist", "journal", "research", "option")


def classify_candidate(path: Path) -> str:
    name = path.name.lower()
    if any(word in name for word in ("trade", "broker", "schwab", "portfolio", "account")):
        return "trading_export"
    if any(word in name for word in ("watchlist", "market", "stock", "earning", "research", "quant")):
        return "market_research"
    if any(word in name for word in ("journal", "note", "thesis")):
        return "notes"
    if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".heic"}:
        return "screenshot_or_image"
    return "other_candidate"


def inventory_candidates(roots: Iterable[str], max_results: int = 500) -> list[Dict[str, object]]:
    """Return metadata only. This never opens candidate file contents."""
    results: list[Dict[str, object]] = []
    for raw_root in roots:
        root = Path(raw_root).expanduser()
        if not root.exists() or not root.is_dir():
            continue
        for path in root.rglob("*"):
            if len(results) >= max_results:
                return sorted(results, key=lambda item: str(item["modified_at"]), reverse=True)
            if not path.is_file() or any(part in EXCLUDED_DIRS or part.startswith(".") for part in path.parts):
                continue
            if path.suffix.lower() not in INTERESTING_EXTENSIONS:
                continue
            lower_name = path.name.lower()
            if not any(keyword in lower_name for keyword in KEYWORDS):
                continue
            stat = path.stat()
            results.append(
                {
                    "path": str(path),
                    "name": path.name,
                    "extension": path.suffix.lower(),
                    "size_bytes": stat.st_size,
                    "modified_at": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                    "category": classify_candidate(path),
                }
            )
    return sorted(results, key=lambda item: str(item["modified_at"]), reverse=True)
