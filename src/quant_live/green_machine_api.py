"""Loopback-only FastAPI service for the Unity Green Machine client."""

from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
import secrets
from typing import Any, Dict

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from quant_live.config import Settings
from quant_live.green_machine_store import GreenMachineStore
from quant_live.green_machine_analytics import summarize_closed_trades
from quant_live.research import available_watchlists, latest_snapshot_path, load_snapshot


class RecordInput(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict)


def _api_token() -> str:
    token = os.getenv("GREEN_MACHINE_API_TOKEN", "").strip()
    if not token:
        raise RuntimeError("GREEN_MACHINE_API_TOKEN must be set before starting the local API")
    return token


def create_app(settings: Settings, store: GreenMachineStore, token: str | None = None) -> FastAPI:
    expected_token = token or _api_token()
    app = FastAPI(title="Green Machine Local API", docs_url=None, redoc_url=None)

    def require_token(x_green_machine_token: str = Header(default="")) -> None:
        if not secrets.compare_digest(x_green_machine_token, expected_token):
            raise HTTPException(status_code=401, detail="local API token required")

    @app.get("/health")
    def health() -> Dict[str, object]:
        return {"status": "ok", "service": "green-machine", "captured_at": datetime.now(timezone.utc).isoformat()}

    @app.get("/market/overview", dependencies=[Depends(require_token)])
    def market_overview() -> Dict[str, object]:
        watchlists = []
        for name in available_watchlists(settings.research_snapshot_dir):
            path = latest_snapshot_path(settings.research_snapshot_dir, name)
            if not path:
                continue
            payload = load_snapshot(path)
            watchlists.append({"name": name, "snapshot": payload, "source_path": path, "is_demo": False})
        return {"watchlists": watchlists, "captured_at": datetime.now(timezone.utc).isoformat()}

    @app.get("/accounts/latest", dependencies=[Depends(require_token)])
    def latest_account_snapshot() -> Dict[str, object]:
        snapshots = store.list("account_snapshot", limit=1)
        if not snapshots:
            return {"snapshot": None, "status": "unavailable", "reason": "No encrypted account snapshot captured yet."}
        return {"snapshot": snapshots[0], "status": "ok"}

    @app.get("/journal/analytics", dependencies=[Depends(require_token)])
    def journal_analytics() -> Dict[str, object]:
        return summarize_closed_trades(store.list("trade", limit=10_000))

    @app.get("/journal/symbol/{symbol}/trades", dependencies=[Depends(require_token)])
    def symbol_trade_stones(symbol: str) -> Dict[str, object]:
        """Return the minimal, descriptive trade fields needed for a symbol path."""
        normalized_symbol = symbol.strip().upper()
        trades = []
        for record in store.list("trade", limit=10_000):
            payload = record["payload"]
            if str(payload.get("underlying", "")).upper() != normalized_symbol:
                continue
            trades.append(
                {
                    "closed_date": payload.get("closed_date"),
                    "gain_loss": payload.get("gain_loss"),
                    "return_pct": payload.get("return_pct"),
                    "dte_at_close": payload.get("dte_at_close"),
                    "option_type": payload.get("option_type"),
                }
            )
        trades.sort(key=lambda trade: str(trade.get("closed_date") or ""))
        return {
            "symbol": normalized_symbol,
            "trade_count": len(trades),
            "trades": trades,
            "caveat": "Trade stones are a visual memory aid, not a signal. Review sample size and linked records before drawing conclusions.",
        }

    @app.get("/world/today", dependencies=[Depends(require_token)])
    def world_today() -> Dict[str, object]:
        today = datetime.now().astimezone().date().isoformat()
        daily_reviews = [record for record in store.list("daily_review") if record["payload"].get("date") == today]
        songs = [record for record in store.list("song_memory") if record["payload"].get("date") == today]
        return {
            "date": today,
            "daily_review": daily_reviews[0] if daily_reviews else None,
            "song_memory": songs[0] if songs else None,
            "review_streak": _review_streak(store.list("daily_review", limit=500)),
        }

    @app.get("/research/{record_type}", dependencies=[Depends(require_token)])
    def list_records(record_type: str) -> Dict[str, object]:
        return {"records": store.list(record_type)}

    @app.post("/research/{record_type}", dependencies=[Depends(require_token)])
    def save_record(record_type: str, record: RecordInput) -> Dict[str, object]:
        return store.put(record_type, record.payload)

    return app


def run_local_server(settings: Settings, store: GreenMachineStore) -> None:
    import uvicorn

    host = os.getenv("GREEN_MACHINE_API_HOST", "127.0.0.1")
    if host != "127.0.0.1":
        raise ValueError("Green Machine API only supports 127.0.0.1")
    port = int(os.getenv("GREEN_MACHINE_API_PORT", "8788"))
    store.initialize()
    uvicorn.run(create_app(settings, store), host=host, port=port, log_level="warning")


def _review_streak(reviews: list[Dict[str, Any]]) -> int:
    dates = {record["payload"].get("date") for record in reviews if record["payload"].get("date")}
    cursor = datetime.now().astimezone().date()
    streak = 0
    while cursor.isoformat() in dates:
        streak += 1
        cursor = cursor.fromordinal(cursor.toordinal() - 1)
    return streak
