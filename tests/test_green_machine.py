"""Focused coverage for Green Machine's private local foundation."""

from __future__ import annotations

from pathlib import Path
import sys
import tempfile
from unittest import TestCase, main

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from quant_live.green_machine_intake import inventory_candidates
from quant_live.green_machine_imports import import_options_trade_csv, preview_trade_csv
from quant_live.green_machine_analytics import summarize_closed_trades
from quant_live.green_machine_store import GreenMachineStore, sqlite_development_connection
from quant_live.green_machine_api import create_app
from quant_live.config import Settings


class GreenMachineStoreTests(TestCase):
    def test_put_and_list_preserves_record_payload(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = GreenMachineStore(directory, connection_factory=sqlite_development_connection)
            store.initialize()
            stored = store.put("thesis", {"symbol": "NVDA", "premise": "Test thesis"})
            records = store.list("thesis")

            self.assertEqual(records[0]["id"], stored["id"])
            self.assertEqual(records[0]["payload"]["symbol"], "NVDA")
            self.assertTrue((Path(directory) / "raw_imports").is_dir())

    def test_sqlcipher_store_does_not_write_plaintext_payload(self) -> None:
        class FakeKeychain:
            def get_or_create_key(self) -> str:
                return "test-only-key-not-from-macos-keychain"

        with tempfile.TemporaryDirectory() as directory:
            store = GreenMachineStore(directory, keychain=FakeKeychain())
            store.initialize()
            store.put("thesis", {"premise": "private thesis must stay encrypted"})
            database_bytes = (Path(directory) / "green_machine.db").read_bytes()

            self.assertNotIn(b"private thesis must stay encrypted", database_bytes)


class GreenMachineIntakeTests(TestCase):
    def test_inventory_returns_metadata_without_opening_contents(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "Schwab_trades.csv"
            candidate.write_text("private contents", encoding="utf-8")
            results = inventory_candidates([directory])

            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["name"], "Schwab_trades.csv")
            self.assertEqual(results[0]["category"], "trading_export")
            self.assertNotIn("private contents", str(results[0]))


class GreenMachineImportTests(TestCase):
    def test_options_import_is_mapped_and_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "clean_trades.csv"
            source.write_text(
                "symbol,underlying,option_type,closed_date,quantity,proceeds,cost_basis,gain_loss,return_pct,expiration,strike,dte_at_close,wash_sale,disallowed_loss\n"
                "SPY 01/17/2026 600.00 C,SPY,CALL,2026-01-17,2,500,400,100,0.25,2026-01-17,600,0,No,0\n",
                encoding="utf-8",
            )
            store = GreenMachineStore(Path(directory) / "store", connection_factory=sqlite_development_connection)
            store.initialize()

            preview = preview_trade_csv(str(source))
            first = import_options_trade_csv(str(source), store)
            second = import_options_trade_csv(str(source), store)

            self.assertEqual(preview["mapping"], "options_closed_trades")
            self.assertEqual(first["trades_written"], 1)
            self.assertEqual(second["trades_written"], 0)
            self.assertTrue(second["import"]["is_duplicate"])
            self.assertEqual(store.list("trade")[0]["payload"]["underlying"], "SPY")


class GreenMachineAnalyticsTests(TestCase):
    def test_summary_groups_by_underlying_and_dte(self) -> None:
        records = [
            {"payload": {"underlying": "SPY", "option_type": "CALL", "gain_loss": 10, "return_pct": 0.1, "dte_at_close": 0, "closed_date": "2026-01-02"}},
            {"payload": {"underlying": "SPY", "option_type": "PUT", "gain_loss": -5, "return_pct": -0.1, "dte_at_close": 3, "closed_date": "2026-01-02"}},
            {"payload": {"underlying": "NVDA", "option_type": "CALL", "gain_loss": 20, "return_pct": 0.2, "dte_at_close": 14, "closed_date": "2026-02-02"}},
        ]
        summary = summarize_closed_trades(records)

        self.assertEqual(summary["trade_count"], 3)
        self.assertEqual(summary["win_count"], 2)
        self.assertAlmostEqual(summary["total_gain_loss"], 25.0)
        self.assertEqual(summary["by_underlying"][0]["group"], "SPY")
        self.assertEqual(summary["by_dte_bucket"][0]["group"], "0 DTE")


class GreenMachineApiTests(TestCase):
    def test_local_api_requires_token_and_round_trips_research(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = GreenMachineStore(directory, connection_factory=sqlite_development_connection)
            store.initialize()
            settings = Settings(
                access_token="",
                refresh_token="",
                app_key="",
                app_secret="",
                token_url="https://token.example.com",
                marketdata_base_url="https://market.example.com",
                trader_base_url="https://trader.example.com",
                account_hash="",
                rate_limit_per_minute=60,
                reserve_calls_per_minute=20,
                rate_limit_state_path="/tmp/green-machine-test-rate-limit.json",
                max_retries=3,
                backoff_seconds=1.0,
                quote_batch_size=25,
                activity_log_path="data/activity.jsonl",
                daily_readme_dir="reports/daily",
                research_snapshot_dir=str(Path(directory) / "watchlists"),
                signal_sheet_dir="reports/signal_sheets",
                dashboard_dir="reports/dashboard",
                end_of_day_bundle_dir="reports/end_of_day",
                html_export_dir="reports/html",
                score_average_weight=0.6,
                score_dispersion_weight=0.4,
                history_dir="reports/history",
            )
            client = TestClient(create_app(settings, store, token="test-token"))

            self.assertEqual(client.get("/health").status_code, 200)
            self.assertEqual(client.get("/research/thesis").status_code, 401)
            headers = {"X-Green-Machine-Token": "test-token"}
            response = client.post("/research/thesis", headers=headers, json={"payload": {"symbol": "NVDA"}})
            self.assertEqual(response.status_code, 200)
            records = client.get("/research/thesis", headers=headers).json()["records"]
            self.assertEqual(records[0]["payload"]["symbol"], "NVDA")

    def test_world_today_returns_review_and_song(self) -> None:
        from datetime import datetime

        with tempfile.TemporaryDirectory() as directory:
            store = GreenMachineStore(directory, connection_factory=sqlite_development_connection)
            store.initialize()
            today = datetime.now().astimezone().date().isoformat()
            store.put("daily_review", {"date": today, "focus": "NVDA"})
            store.put("song_memory", {"date": today, "title": "Test Song"})
            settings = _settings_for(directory)
            client = TestClient(create_app(settings, store, token="test-token"))
            payload = client.get("/world/today", headers={"X-Green-Machine-Token": "test-token"}).json()

            self.assertEqual(payload["daily_review"]["payload"]["focus"], "NVDA")
            self.assertEqual(payload["song_memory"]["payload"]["title"], "Test Song")

    def test_symbol_trade_path_returns_only_descriptive_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = GreenMachineStore(directory, connection_factory=sqlite_development_connection)
            store.initialize()
            store.put("trade", {"underlying": "NVDA", "closed_date": "2026-02-10", "gain_loss": -12.5, "return_pct": -0.1, "dte_at_close": 2, "secret_note": "not exposed"})
            store.put("trade", {"underlying": "SPY", "closed_date": "2026-02-10", "gain_loss": 5})
            client = TestClient(create_app(_settings_for(directory), store, token="test-token"))

            response = client.get("/journal/symbol/nvda/trades", headers={"X-Green-Machine-Token": "test-token"})
            payload = response.json()

            self.assertEqual(response.status_code, 200)
            self.assertEqual(payload["trade_count"], 1)
            self.assertEqual(payload["trades"][0]["gain_loss"], -12.5)
            self.assertNotIn("secret_note", payload["trades"][0])


def _settings_for(directory: str) -> Settings:
    return Settings(
        access_token="", refresh_token="", app_key="", app_secret="", token_url="https://token.example.com",
        marketdata_base_url="https://market.example.com", trader_base_url="https://trader.example.com", account_hash="",
        rate_limit_per_minute=60, reserve_calls_per_minute=20, rate_limit_state_path="/tmp/green-machine-test-rate-limit.json",
        max_retries=3, backoff_seconds=1.0, quote_batch_size=25, activity_log_path="data/activity.jsonl",
        daily_readme_dir="reports/daily", research_snapshot_dir=str(Path(directory) / "watchlists"),
        signal_sheet_dir="reports/signal_sheets", dashboard_dir="reports/dashboard", end_of_day_bundle_dir="reports/end_of_day",
        html_export_dir="reports/html", score_average_weight=0.6, score_dispersion_weight=0.4, history_dir="reports/history",
    )


if __name__ == "__main__":
    main()
