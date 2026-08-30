"""Preview and import trade exports into Green Machine's encrypted store."""

from __future__ import annotations

import csv
from datetime import datetime
import hashlib
from pathlib import Path
from typing import Any, Dict

from quant_live.green_machine_store import GreenMachineStore


OPTION_COLUMNS = {
    "symbol",
    "underlying",
    "option_type",
    "closed_date",
    "quantity",
    "proceeds",
    "cost_basis",
    "gain_loss",
    "return_pct",
    "expiration",
    "strike",
    "dte_at_close",
}


def preview_trade_csv(source_path: str) -> Dict[str, Any]:
    path = Path(source_path).expanduser()
    content = path.read_bytes()
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        rows = list(reader)
    missing = sorted(OPTION_COLUMNS - set(headers))
    invalid_closed_dates = sum(not _is_date(row.get("closed_date", "")) for row in rows)
    invalid_numbers = sum(not _is_float(row.get("gain_loss", "")) for row in rows)
    return {
        "source_name": path.name,
        "source_path": str(path),
        "sha256": hashlib.sha256(content).hexdigest(),
        "headers": headers,
        "row_count": len(rows),
        "mapping": "options_closed_trades" if not missing else "unsupported",
        "missing_required_columns": missing,
        "invalid_closed_date_rows": invalid_closed_dates,
        "invalid_gain_loss_rows": invalid_numbers,
    }


def import_options_trade_csv(source_path: str, store: GreenMachineStore) -> Dict[str, Any]:
    preview = preview_trade_csv(source_path)
    if preview["mapping"] != "options_closed_trades":
        raise ValueError(f"unsupported trade export; missing columns: {', '.join(preview['missing_required_columns'])}")

    path = Path(source_path).expanduser()
    content = path.read_bytes()
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    import_record = store.register_import(str(path), content, len(rows))
    if import_record["is_duplicate"]:
        return {"preview": preview, "import": import_record, "trades_written": 0}

    import_id = str(import_record["id"])
    items = []
    for index, row in enumerate(rows, start=1):
        trade_id = f"{import_id}:{index}"
        payload = {
            "import_id": import_id,
            "source_row": index,
            "asset_class": "OPTION" if row.get("option_type", "").strip() else "EQUITY",
            "symbol": row.get("symbol", "").strip(),
            "underlying": row.get("underlying", "").strip(),
            "option_type": row.get("option_type", "").strip() or None,
            "closed_date": row.get("closed_date", "").strip(),
            "quantity": _as_float(row.get("quantity")),
            "proceeds": _as_float(row.get("proceeds")),
            "cost_basis": _as_float(row.get("cost_basis")),
            "gain_loss": _as_float(row.get("gain_loss")),
            "return_pct": _as_float(row.get("return_pct")),
            "wash_sale": row.get("wash_sale", "").strip(),
            "disallowed_loss": _as_float(row.get("disallowed_loss")),
            "expiration": row.get("expiration", "").strip() or None,
            "strike": _as_float(row.get("strike")),
            "dte_at_close": _as_float(row.get("dte_at_close")),
            "raw": row,
        }
        items.append((trade_id, payload))
    written = store.put_many("trade", items)
    return {"preview": preview, "import": import_record, "trades_written": written}


def _is_date(value: str) -> bool:
    try:
        datetime.strptime(value.strip(), "%Y-%m-%d")
        return True
    except ValueError:
        return False


def _is_float(value: str) -> bool:
    try:
        float(value.strip())
        return True
    except ValueError:
        return False


def _as_float(value: str | None) -> float | None:
    if value in (None, ""):
        return None
    return float(value)
