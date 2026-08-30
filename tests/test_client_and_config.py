"""Tests for config loading and request construction."""

from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile
from unittest import TestCase, main
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
src_str = str(SRC)
if src_str not in sys.path:
    sys.path.insert(0, src_str)

from quant_live.auth import refresh_access_token
from quant_live.activity import build_daily_readme, summarize_activities
from quant_live.client import SchwabClient
from quant_live.cli import build_parser
from quant_live.config import Settings
from quant_live.execution import load_execution_rows, render_execution_report_markdown, summarize_execution_rows
from quant_live.green_machine_intake import inventory_candidates
from quant_live.green_machine_store import GreenMachineStore, sqlite_development_connection
from quant_live.rate_limit import RateLimiter
from quant_live.research import flatten_quote_payload, render_snapshot_markdown, summarize_snapshot
from quant_live.research import (
    build_signal_sheet_entries,
    bundle_end_of_day,
    compare_snapshot_rows,
    load_signal_sheet_entries,
    markdown_to_basic_html,
    render_dashboard_markdown,
    render_history_sheet_markdown,
    render_signal_sheet_markdown,
    render_snapshot_comparison_markdown,
    summarize_watchlist_history,
)
from quant_live.templates import WATCHLIST_TEMPLATES


class SettingsTests(TestCase):
    def test_settings_build_default_urls(self) -> None:
        old = dict(os.environ)
        try:
            os.environ["SCHWAB_ACCESS_TOKEN"] = "abc"
            os.environ["SCHWAB_API_BASE_URL"] = "https://example.com/"
            settings = Settings.from_env()
            self.assertEqual(settings.marketdata_base_url, "https://example.com/marketdata/v1")
            self.assertEqual(settings.trader_base_url, "https://example.com/trader/v1")
            self.assertEqual(settings.effective_calls_per_minute, 40)
            self.assertEqual(settings.rate_limit_state_path, "/tmp/quant_live_schwab_rate_limit.json")
            self.assertEqual(settings.max_retries, 3)
            self.assertEqual(settings.quote_batch_size, 25)
            self.assertEqual(settings.activity_log_path, "data/activity_log.jsonl")
            self.assertEqual(settings.daily_readme_dir, "reports/daily")
            self.assertEqual(settings.research_snapshot_dir, "reports/watchlists")
            self.assertEqual(settings.signal_sheet_dir, "reports/signal_sheets")
            self.assertEqual(settings.dashboard_dir, "reports/dashboard")
            self.assertEqual(settings.end_of_day_bundle_dir, "reports/end_of_day")
            self.assertEqual(settings.html_export_dir, "reports/html")
            self.assertEqual(settings.score_average_weight, 0.6)
            self.assertEqual(settings.score_dispersion_weight, 0.4)
            self.assertEqual(settings.history_dir, "reports/history")
            self.assertEqual(settings.execution_report_dir, "reports/execution")
            self.assertEqual(settings.green_machine_data_dir, "~/.green-machine")
        finally:
            os.environ.clear()
            os.environ.update(old)

    def test_settings_allow_custom_reserve(self) -> None:
        old = dict(os.environ)
        try:
            os.environ["SCHWAB_ACCESS_TOKEN"] = "abc"
            os.environ["SCHWAB_RATE_LIMIT_PER_MINUTE"] = "60"
            os.environ["SCHWAB_RESERVE_CALLS_PER_MINUTE"] = "45"
            os.environ["SCHWAB_MAX_RETRIES"] = "5"
            os.environ["SCHWAB_QUOTE_BATCH_SIZE"] = "10"
            os.environ["QUANT_LIVE_ACTIVITY_LOG_PATH"] = "/tmp/ql-log.jsonl"
            os.environ["QUANT_LIVE_DAILY_README_DIR"] = "/tmp/ql-daily"
            os.environ["QUANT_LIVE_RESEARCH_SNAPSHOT_DIR"] = "/tmp/ql-watchlists"
            os.environ["QUANT_LIVE_SIGNAL_SHEET_DIR"] = "/tmp/ql-sheets"
            os.environ["QUANT_LIVE_DASHBOARD_DIR"] = "/tmp/ql-dashboard"
            os.environ["QUANT_LIVE_END_OF_DAY_BUNDLE_DIR"] = "/tmp/ql-eod"
            os.environ["QUANT_LIVE_HTML_EXPORT_DIR"] = "/tmp/ql-html"
            os.environ["QUANT_LIVE_SCORE_AVERAGE_WEIGHT"] = "0.7"
            os.environ["QUANT_LIVE_SCORE_DISPERSION_WEIGHT"] = "0.3"
            os.environ["QUANT_LIVE_HISTORY_DIR"] = "/tmp/ql-history"
            os.environ["QUANT_LIVE_EXECUTION_REPORT_DIR"] = "/tmp/ql-execution"
            settings = Settings.from_env()
            self.assertEqual(settings.effective_calls_per_minute, 15)
            self.assertEqual(settings.max_retries, 5)
            self.assertEqual(settings.quote_batch_size, 10)
            self.assertEqual(settings.activity_log_path, "/tmp/ql-log.jsonl")
            self.assertEqual(settings.daily_readme_dir, "/tmp/ql-daily")
            self.assertEqual(settings.research_snapshot_dir, "/tmp/ql-watchlists")
            self.assertEqual(settings.signal_sheet_dir, "/tmp/ql-sheets")
            self.assertEqual(settings.dashboard_dir, "/tmp/ql-dashboard")
            self.assertEqual(settings.end_of_day_bundle_dir, "/tmp/ql-eod")
            self.assertEqual(settings.html_export_dir, "/tmp/ql-html")
            self.assertEqual(settings.score_average_weight, 0.7)
            self.assertEqual(settings.score_dispersion_weight, 0.3)
            self.assertEqual(settings.history_dir, "/tmp/ql-history")
            self.assertEqual(settings.execution_report_dir, "/tmp/ql-execution")
        finally:
            os.environ.clear()
            os.environ.update(old)


class ClientTests(TestCase):
    def test_quotes_request_shape(self) -> None:
        settings = Settings(
            access_token="abc",
            refresh_token="",
            app_key="",
            app_secret="",
            token_url="https://token.example.com",
            marketdata_base_url="https://md.example.com",
            trader_base_url="https://trader.example.com",
            account_hash="",
            rate_limit_per_minute=60,
            reserve_calls_per_minute=20,
            rate_limit_state_path="/tmp/test-rate-limit.json",
            max_retries=3,
            backoff_seconds=1.0,
            quote_batch_size=25,
            activity_log_path="data/test_activity.jsonl",
            daily_readme_dir="reports/test_daily",
            research_snapshot_dir="reports/test_watchlists",
            signal_sheet_dir="reports/test_signal_sheets",
            dashboard_dir="reports/test_dashboard",
            end_of_day_bundle_dir="reports/test_eod",
            html_export_dir="reports/test_html",
            score_average_weight=0.6,
            score_dispersion_weight=0.4,
            history_dir="reports/test_history",
        )
        mock_response = Mock()
        mock_response.json.return_value = {"ok": True}
        mock_response.raise_for_status.return_value = None

        session = Mock()
        session.get.return_value = mock_response

        client = SchwabClient(settings, session=session)
        payload = client.quotes(["AAPL", "MSFT"])

        self.assertEqual(payload, {"ok": True})
        session.get.assert_called_once()
        _, kwargs = session.get.call_args
        self.assertEqual(kwargs["params"]["symbols"], "AAPL,MSFT")
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer abc")

    def test_quote_batches_reduce_request_count(self) -> None:
        settings = Settings(
            access_token="abc",
            refresh_token="",
            app_key="",
            app_secret="",
            token_url="https://token.example.com",
            marketdata_base_url="https://md.example.com",
            trader_base_url="https://trader.example.com",
            account_hash="",
            rate_limit_per_minute=60,
            reserve_calls_per_minute=20,
            rate_limit_state_path="/tmp/test-rate-limit.json",
            max_retries=3,
            backoff_seconds=1.0,
            quote_batch_size=2,
            activity_log_path="data/test_activity.jsonl",
            daily_readme_dir="reports/test_daily",
            research_snapshot_dir="reports/test_watchlists",
            signal_sheet_dir="reports/test_signal_sheets",
            dashboard_dir="reports/test_dashboard",
            end_of_day_bundle_dir="reports/test_eod",
            html_export_dir="reports/test_html",
            score_average_weight=0.6,
            score_dispersion_weight=0.4,
            history_dir="reports/test_history",
        )
        mock_response = Mock()
        mock_response.json.return_value = {"ok": True}
        mock_response.raise_for_status.return_value = None
        mock_response.status_code = 200
        session = Mock()
        session.get.return_value = mock_response
        client = SchwabClient(settings, session=session)

        payloads = client.quote_batches(["AAPL", "MSFT", "NVDA"], batch_size=2)
        self.assertEqual(len(payloads), 2)
        self.assertEqual(session.get.call_count, 2)

    def test_retries_on_429(self) -> None:
        settings = Settings(
            access_token="abc",
            refresh_token="",
            app_key="",
            app_secret="",
            token_url="https://token.example.com",
            marketdata_base_url="https://md.example.com",
            trader_base_url="https://trader.example.com",
            account_hash="",
            rate_limit_per_minute=60,
            reserve_calls_per_minute=20,
            rate_limit_state_path="/tmp/test-rate-limit.json",
            max_retries=2,
            backoff_seconds=0.5,
            quote_batch_size=25,
            activity_log_path="data/test_activity.jsonl",
            daily_readme_dir="reports/test_daily",
            research_snapshot_dir="reports/test_watchlists",
            signal_sheet_dir="reports/test_signal_sheets",
            dashboard_dir="reports/test_dashboard",
            end_of_day_bundle_dir="reports/test_eod",
            html_export_dir="reports/test_html",
            score_average_weight=0.6,
            score_dispersion_weight=0.4,
            history_dir="reports/test_history",
        )
        first = Mock()
        first.status_code = 429
        first.headers = {"Retry-After": "0"}
        second = Mock()
        second.status_code = 200
        second.json.return_value = {"ok": True}
        second.raise_for_status.return_value = None
        session = Mock()
        session.get.side_effect = [first, second]

        client = SchwabClient(settings, session=session)
        slept = []
        client.rate_limiter._sleep = lambda seconds: slept.append(seconds)

        payload = client.quotes(["AAPL"])
        self.assertEqual(payload, {"ok": True})
        self.assertEqual(session.get.call_count, 2)
        self.assertEqual(slept, [0.5])

    def test_client_exposes_rate_limit_status(self) -> None:
        settings = Settings(
            access_token="abc",
            refresh_token="",
            app_key="",
            app_secret="",
            token_url="https://token.example.com",
            marketdata_base_url="https://md.example.com",
            trader_base_url="https://trader.example.com",
            account_hash="",
            rate_limit_per_minute=60,
            reserve_calls_per_minute=15,
            rate_limit_state_path="/tmp/test-rate-limit.json",
            max_retries=3,
            backoff_seconds=1.0,
            quote_batch_size=25,
            activity_log_path="data/test_activity.jsonl",
            daily_readme_dir="reports/test_daily",
            research_snapshot_dir="reports/test_watchlists",
            signal_sheet_dir="reports/test_signal_sheets",
            dashboard_dir="reports/test_dashboard",
            end_of_day_bundle_dir="reports/test_eod",
            html_export_dir="reports/test_html",
            score_average_weight=0.6,
            score_dispersion_weight=0.4,
            history_dir="reports/test_history",
        )
        client = SchwabClient(settings, session=Mock())
        snapshot = client.rate_limit_status()
        self.assertEqual(snapshot.max_calls_per_minute, 45)
        self.assertGreaterEqual(snapshot.available_now, 0)

    def test_account_needs_hash(self) -> None:
        settings = Settings(
            access_token="abc",
            refresh_token="",
            app_key="",
            app_secret="",
            token_url="https://token.example.com",
            marketdata_base_url="https://md.example.com",
            trader_base_url="https://trader.example.com",
            account_hash="",
            rate_limit_per_minute=60,
            reserve_calls_per_minute=20,
            rate_limit_state_path="/tmp/test-rate-limit.json",
            max_retries=3,
            backoff_seconds=1.0,
            quote_batch_size=25,
            activity_log_path="data/test_activity.jsonl",
            daily_readme_dir="reports/test_daily",
            research_snapshot_dir="reports/test_watchlists",
            signal_sheet_dir="reports/test_signal_sheets",
            dashboard_dir="reports/test_dashboard",
            end_of_day_bundle_dir="reports/test_eod",
            html_export_dir="reports/test_html",
            score_average_weight=0.6,
            score_dispersion_weight=0.4,
            history_dir="reports/test_history",
        )
        client = SchwabClient(settings, session=Mock())
        with self.assertRaises(ValueError):
            client.account()


class AuthTests(TestCase):
    def test_refresh_uses_basic_auth_and_form_data(self) -> None:
        settings = Settings(
            access_token="",
            refresh_token="refresh-value",
            app_key="key",
            app_secret="secret",
            token_url="https://token.example.com",
            marketdata_base_url="https://md.example.com",
            trader_base_url="https://trader.example.com",
            account_hash="",
            rate_limit_per_minute=60,
            reserve_calls_per_minute=20,
            rate_limit_state_path="/tmp/test-rate-limit.json",
            max_retries=3,
            backoff_seconds=1.0,
            quote_batch_size=25,
            activity_log_path="data/test_activity.jsonl",
            daily_readme_dir="reports/test_daily",
            research_snapshot_dir="reports/test_watchlists",
            signal_sheet_dir="reports/test_signal_sheets",
            dashboard_dir="reports/test_dashboard",
            end_of_day_bundle_dir="reports/test_eod",
            html_export_dir="reports/test_html",
            score_average_weight=0.6,
            score_dispersion_weight=0.4,
            history_dir="reports/test_history",
        )
        mock_response = Mock()
        mock_response.json.return_value = {"access_token": "new-token"}
        mock_response.raise_for_status.return_value = None

        session = Mock()
        session.post.return_value = mock_response

        payload = refresh_access_token(settings, session=session)
        self.assertEqual(payload["access_token"], "new-token")
        session.post.assert_called_once()


class RateLimiterTests(TestCase):
    def test_limiter_reports_window_usage(self) -> None:
        now = [100.0]

        def clock() -> float:
            return now[0]

        def sleeper(seconds: float) -> None:
            now[0] += seconds

        with tempfile.TemporaryDirectory() as tmpdir:
            limiter = RateLimiter(
                2,
                state_path=str(Path(tmpdir) / "shared.json"),
                clock=clock,
                sleeper=sleeper,
            )
            limiter.acquire()
            limiter.acquire()
            snapshot = limiter.snapshot()
            self.assertEqual(snapshot.calls_in_window, 2)
            self.assertEqual(snapshot.available_now, 0)

    def test_limit_is_shared_across_instances(self) -> None:
        now = [100.0]

        def clock() -> float:
            return now[0]

        def sleeper(seconds: float) -> None:
            now[0] += seconds

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = str(Path(tmpdir) / "shared.json")
            first = RateLimiter(2, state_path=state_path, clock=clock, sleeper=sleeper)
            second = RateLimiter(2, state_path=state_path, clock=clock, sleeper=sleeper)
            first.acquire()
            second.acquire()
            snapshot = first.snapshot()
            self.assertEqual(snapshot.calls_in_window, 2)
            self.assertEqual(snapshot.available_now, 0)


class ActivityTests(TestCase):
    def test_daily_readme_contains_commands_and_symbols(self) -> None:
        summary = summarize_activities(
            [
                {"command": "quote", "symbols": ["AAPL", "MSFT"], "note": "fields=quote"},
                {"command": "price-history", "symbols": ["AAPL"], "note": "period=5"},
            ],
            "2026-05-28",
        )
        markdown = build_daily_readme(summary)
        self.assertIn("# Daily Readme - 2026-05-28", markdown)
        self.assertIn("`quote` x 1", markdown)
        self.assertIn("AAPL, MSFT", markdown)
        self.assertIn("fields=quote", markdown)


class ResearchTests(TestCase):
    def test_flatten_quote_payload_and_summary(self) -> None:
        rows = flatten_quote_payload(
            {
                "AAPL": {"quote": {"lastPrice": 100.0, "netChange": 1.0, "netPercentChange": 1.0, "totalVolume": 500}},
                "MSFT": {"quote": {"lastPrice": 95.0, "netChange": -2.0, "netPercentChange": -2.0, "totalVolume": 900}},
            }
        )
        self.assertEqual(len(rows), 2)
        summary = summarize_snapshot(rows)
        self.assertEqual(summary["symbol_count"], 2)
        self.assertEqual(summary["top_gainers"][0]["symbol"], "AAPL")
        self.assertEqual(summary["most_active"][0]["symbol"], "MSFT")
        self.assertIn("average_percent_change", summary)
        self.assertIn("dispersion_percent_change", summary)
        self.assertIn("watchlist_score", summary)

    def test_render_snapshot_markdown_mentions_watchlist(self) -> None:
        markdown = render_snapshot_markdown(
            "semis",
            [
                {"symbol": "NVDA", "percent_change": 2.3, "net_change": 20.1, "total_volume": 1000},
            ],
        )
        self.assertIn("# Watchlist Snapshot - semis", markdown)
        self.assertIn("NVDA", markdown)
        self.assertIn("Dispersion of % change", markdown)
        self.assertIn("Watchlist score", markdown)

    def test_compare_snapshot_rows_orders_by_largest_delta(self) -> None:
        changes = compare_snapshot_rows(
            [
                {"symbol": "AAPL", "percent_change": 1.0, "last_price": 100.0},
                {"symbol": "MSFT", "percent_change": 0.5, "last_price": 90.0},
            ],
            [
                {"symbol": "AAPL", "percent_change": 3.0, "last_price": 102.0},
                {"symbol": "MSFT", "percent_change": -0.5, "last_price": 89.0},
            ],
        )
        self.assertEqual(changes[0]["symbol"], "AAPL")
        self.assertEqual(changes[0]["delta_percent_change"], 2.0)

    def test_render_snapshot_comparison_markdown_mentions_previous_and_current(self) -> None:
        markdown = render_snapshot_comparison_markdown(
            "semis",
            {
                "created_at": "2026-05-28T10:00:00-04:00",
                "rows": [{"symbol": "NVDA", "percent_change": 1.0, "last_price": 100.0}],
            },
            {
                "created_at": "2026-05-28T11:00:00-04:00",
                "rows": [{"symbol": "NVDA", "percent_change": 2.5, "last_price": 101.0}],
            },
        )
        self.assertIn("# Watchlist Comparison - semis", markdown)
        self.assertIn("1.0% -> 2.5%", markdown)

    def test_signal_sheet_ranks_watchlists_and_renders_markdown(self) -> None:
        entries = build_signal_sheet_entries(
            {
                "semis": {
                    "created_at": "2026-05-28T11:00:00-04:00",
                    "summary": {
                        "symbol_count": 4,
                        "average_percent_change": 1.2,
                        "dispersion_percent_change": 2.0,
                        "watchlist_score": 1.52,
                        "top_gainers": [{"symbol": "NVDA"}],
                        "top_losers": [{"symbol": "AMD"}],
                        "most_active": [{"symbol": "NVDA"}],
                    },
                },
                "indexes": {
                    "created_at": "2026-05-28T11:00:00-04:00",
                    "summary": {
                        "symbol_count": 3,
                        "average_percent_change": 0.2,
                        "dispersion_percent_change": 0.4,
                        "watchlist_score": 0.28,
                        "top_gainers": [{"symbol": "QQQ"}],
                        "top_losers": [{"symbol": "DIA"}],
                        "most_active": [{"symbol": "SPY"}],
                    },
                },
            }
        )
        self.assertEqual(entries[0]["watchlist"], "semis")
        markdown = render_signal_sheet_markdown(entries, "2026-05-28")
        self.assertIn("# Nightly Signal Sheet - 2026-05-28", markdown)
        self.assertIn("semis", markdown)
        self.assertIn("score", markdown)

    def test_dashboard_markdown_mentions_files_and_watchlists(self) -> None:
        markdown = render_dashboard_markdown(
            "2026-05-28",
            "reports/signal_sheets/2026-05-28.md",
            "reports/daily/2026-05-28.md",
            [
                {
                    "watchlist": "semis",
                    "watchlist_score": 1.52,
                    "average_percent_change": 1.2,
                    "dispersion_percent_change": 2.0,
                    "top_gainer": "NVDA",
                    "most_active": "NVDA",
                }
            ],
        )
        self.assertIn("# Quant Live Dashboard - 2026-05-28", markdown)
        self.assertIn("semis", markdown)
        self.assertIn("score", markdown)

    def test_templates_include_semis(self) -> None:
        self.assertIn("semis", WATCHLIST_TEMPLATES)

    def test_end_of_day_bundle_writes_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            bundle_path = bundle_end_of_day(
                tmpdir,
                "2026-05-28",
                "reports/signal_sheets/2026-05-28.md",
                "reports/daily/2026-05-28.md",
                "reports/dashboard/2026-05-28.md",
            )
            manifest = Path(bundle_path) / "manifest.json"
            self.assertTrue(manifest.exists())

    def test_markdown_to_basic_html_wraps_headers(self) -> None:
        html = markdown_to_basic_html("test", "# Hello\n\n## World\n- item")
        self.assertIn("<h1>Hello</h1>", html)
        self.assertIn("<h2>World</h2>", html)

    def test_history_sheet_builds_from_signal_rows(self) -> None:
        rows = summarize_watchlist_history(
            [
                {"date": "2026-05-27", "watchlist": "semis", "watchlist_score": 1.0, "average_percent_change": 0.8, "dispersion_percent_change": 1.3},
                {"date": "2026-05-28", "watchlist": "semis", "watchlist_score": 1.5, "average_percent_change": 1.2, "dispersion_percent_change": 2.0},
                {"date": "2026-05-28", "watchlist": "indexes", "watchlist_score": 0.3, "average_percent_change": 0.1, "dispersion_percent_change": 0.4},
            ],
            lookback=5,
        )
        self.assertEqual(rows[0]["watchlist"], "semis")
        markdown = render_history_sheet_markdown(rows, 5)
        self.assertIn("# Watchlist History Sheet - Last 5 Days", markdown)
        self.assertIn("semis", markdown)

    def test_load_signal_sheet_entries_parses_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "2026-05-28.md"
            path.write_text(
                "# Nightly Signal Sheet - 2026-05-28\n\n## Watchlist ranking\n- semis: score 1.520, avg 1.200%, dispersion 2.000, leader NVDA, laggard AMD, active NVDA\n",
                encoding="utf-8",
            )
            rows = load_signal_sheet_entries(tmpdir)
            self.assertEqual(rows[0]["watchlist"], "semis")

    def test_summarize_execution_rows_reports_slippage(self) -> None:
        summary = summarize_execution_rows(
            [
                {
                    "symbol": "AAPL",
                    "side": "BUY",
                    "quantity": 100,
                    "fill_price": 101.0,
                    "arrival_price": 100.5,
                    "decision_price": 100.0,
                    "venue": "XNAS",
                },
                {
                    "symbol": "MSFT",
                    "side": "SELL",
                    "quantity": 200,
                    "fill_price": 99.5,
                    "arrival_price": 100.0,
                    "decision_price": 100.2,
                    "venue": "BATS",
                },
            ]
        )
        self.assertEqual(summary["fills"], 2)
        self.assertIn("avg_arrival_slippage_bps", summary)
        markdown = render_execution_report_markdown("sample", summary)
        self.assertIn("# Execution Report - sample", markdown)
        self.assertIn("Worst venues", markdown)

    def test_load_execution_rows_reads_csv(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "fills.csv"
            path.write_text(
                "symbol,side,quantity,fill_price,arrival_price,decision_price,venue\n"
                "AAPL,BUY,100,101.0,100.5,100.0,XNAS\n",
                encoding="utf-8",
            )
            rows = load_execution_rows(str(path))
            self.assertEqual(rows[0]["symbol"], "AAPL")


class CliTests(TestCase):
    def test_parser_accepts_research_pack(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["research-pack", "semis", "indexes", "--lookback", "7"])
        self.assertEqual(args.command, "research-pack")
        self.assertEqual(args.templates, ["semis", "indexes"])
        self.assertEqual(args.lookback, 7)

    def test_parser_accepts_tca_report(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["tca-report", "fills.csv", "--name", "desk_day"])
        self.assertEqual(args.command, "tca-report")
        self.assertEqual(args.input_path, "fills.csv")
        self.assertEqual(args.name, "desk_day")


if __name__ == "__main__":
    main()
