"""Environment-backed configuration for the live-data CLI."""

from __future__ import annotations

from dataclasses import dataclass
import os


def _clean(value: str) -> str:
    return value.rstrip("/")


@dataclass(frozen=True)
class Settings:
    access_token: str
    refresh_token: str
    app_key: str
    app_secret: str
    token_url: str
    marketdata_base_url: str
    trader_base_url: str
    account_hash: str
    rate_limit_per_minute: int
    reserve_calls_per_minute: int
    rate_limit_state_path: str
    max_retries: int
    backoff_seconds: float
    quote_batch_size: int
    activity_log_path: str
    daily_readme_dir: str
    research_snapshot_dir: str
    signal_sheet_dir: str
    dashboard_dir: str
    end_of_day_bundle_dir: str
    html_export_dir: str
    score_average_weight: float
    score_dispersion_weight: float
    history_dir: str
    execution_report_dir: str = "reports/execution"
    green_machine_data_dir: str = "~/.green-machine"

    @classmethod
    def from_env(cls) -> "Settings":
        api_base = _clean(os.getenv("SCHWAB_API_BASE_URL", "https://api.schwabapi.com"))
        marketdata_base = _clean(os.getenv("SCHWAB_MARKETDATA_BASE_URL", f"{api_base}/marketdata/v1"))
        trader_base = _clean(os.getenv("SCHWAB_TRADER_BASE_URL", f"{api_base}/trader/v1"))
        token_url = _clean(os.getenv("SCHWAB_TOKEN_URL", "https://api.schwabapi.com/v1/oauth/token"))
        return cls(
            access_token=os.getenv("SCHWAB_ACCESS_TOKEN", ""),
            refresh_token=os.getenv("SCHWAB_REFRESH_TOKEN", ""),
            app_key=os.getenv("SCHWAB_APP_KEY", ""),
            app_secret=os.getenv("SCHWAB_APP_SECRET", ""),
            token_url=token_url,
            marketdata_base_url=marketdata_base,
            trader_base_url=trader_base,
            account_hash=os.getenv("SCHWAB_ACCOUNT_HASH", ""),
            rate_limit_per_minute=int(os.getenv("SCHWAB_RATE_LIMIT_PER_MINUTE", "60")),
            reserve_calls_per_minute=int(os.getenv("SCHWAB_RESERVE_CALLS_PER_MINUTE", "20")),
            rate_limit_state_path=os.getenv(
                "SCHWAB_RATE_LIMIT_STATE_PATH",
                "/tmp/quant_live_schwab_rate_limit.json",
            ),
            max_retries=int(os.getenv("SCHWAB_MAX_RETRIES", "3")),
            backoff_seconds=float(os.getenv("SCHWAB_BACKOFF_SECONDS", "1.0")),
            quote_batch_size=int(os.getenv("SCHWAB_QUOTE_BATCH_SIZE", "25")),
            activity_log_path=os.getenv(
                "QUANT_LIVE_ACTIVITY_LOG_PATH",
                "data/activity_log.jsonl",
            ),
            daily_readme_dir=os.getenv(
                "QUANT_LIVE_DAILY_README_DIR",
                "reports/daily",
            ),
            research_snapshot_dir=os.getenv(
                "QUANT_LIVE_RESEARCH_SNAPSHOT_DIR",
                "reports/watchlists",
            ),
            signal_sheet_dir=os.getenv(
                "QUANT_LIVE_SIGNAL_SHEET_DIR",
                "reports/signal_sheets",
            ),
            dashboard_dir=os.getenv(
                "QUANT_LIVE_DASHBOARD_DIR",
                "reports/dashboard",
            ),
            end_of_day_bundle_dir=os.getenv(
                "QUANT_LIVE_END_OF_DAY_BUNDLE_DIR",
                "reports/end_of_day",
            ),
            html_export_dir=os.getenv(
                "QUANT_LIVE_HTML_EXPORT_DIR",
                "reports/html",
            ),
            score_average_weight=float(os.getenv("QUANT_LIVE_SCORE_AVERAGE_WEIGHT", "0.6")),
            score_dispersion_weight=float(os.getenv("QUANT_LIVE_SCORE_DISPERSION_WEIGHT", "0.4")),
            history_dir=os.getenv(
                "QUANT_LIVE_HISTORY_DIR",
                "reports/history",
            ),
            execution_report_dir=os.getenv(
                "QUANT_LIVE_EXECUTION_REPORT_DIR",
                "reports/execution",
            ),
            green_machine_data_dir=os.getenv(
                "GREEN_MACHINE_DATA_DIR",
                "~/.green-machine",
            ),
        )

    def require_access_token(self) -> None:
        if not self.access_token:
            raise ValueError("SCHWAB_ACCESS_TOKEN is required for API calls")

    @property
    def effective_calls_per_minute(self) -> int:
        value = self.rate_limit_per_minute - self.reserve_calls_per_minute
        return max(1, value)
