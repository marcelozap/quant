"""Small HTTP client for Schwab-connected workflows."""

from __future__ import annotations

from typing import Dict, List, Optional

import requests

from quant_live.config import Settings
from quant_live.rate_limit import RateLimiter, RateLimitSnapshot


class SchwabClient:
    """Wrapper around a requests session with a few high-value endpoints."""

    def __init__(self, settings: Settings, session: Optional[requests.Session] = None) -> None:
        self.settings = settings
        self.settings.require_access_token()
        self.session = session or requests.Session()
        self.rate_limiter = RateLimiter(
            settings.effective_calls_per_minute,
            state_path=settings.rate_limit_state_path,
        )

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.settings.access_token}",
            "Accept": "application/json",
        }

    def _get(self, url: str, params: Optional[Dict[str, object]] = None) -> object:
        attempt = 0
        while True:
            self.rate_limiter.acquire()
            response = self.session.get(url, headers=self.headers, params=params, timeout=30)
            if response.status_code == 429 and attempt < self.settings.max_retries:
                retry_after = self._retry_after_seconds(response)
                self.rate_limiter._sleep(retry_after)
                attempt += 1
                continue
            response.raise_for_status()
            return response.json()

    def rate_limit_status(self) -> RateLimitSnapshot:
        return self.rate_limiter.snapshot()

    def quote_batches(self, symbols: List[str], fields: str = "quote", batch_size: Optional[int] = None) -> List[object]:
        if not symbols:
            raise ValueError("at least one symbol is required")
        size = batch_size or self.settings.quote_batch_size
        if size <= 0:
            raise ValueError("batch_size must be positive")
        payloads = []
        for start in range(0, len(symbols), size):
            payloads.append(self.quotes(symbols[start : start + size], fields=fields))
        return payloads

    def account_numbers(self) -> object:
        return self._get(f"{self.settings.trader_base_url}/accounts/accountNumbers")

    def accounts(self, fields: str = "positions") -> object:
        params = {"fields": fields} if fields else None
        return self._get(f"{self.settings.trader_base_url}/accounts", params=params)

    def account(self, account_hash: Optional[str] = None, fields: str = "positions") -> object:
        resolved = account_hash or self.settings.account_hash
        if not resolved:
            raise ValueError("account hash required via argument or SCHWAB_ACCOUNT_HASH")
        params = {"fields": fields} if fields else None
        return self._get(f"{self.settings.trader_base_url}/accounts/{resolved}", params=params)

    def quotes(self, symbols: list[str], fields: str = "quote") -> object:
        if not symbols:
            raise ValueError("at least one symbol is required")
        params = {
            "symbols": ",".join(symbols),
            "fields": fields,
        }
        return self._get(f"{self.settings.marketdata_base_url}/quotes", params=params)

    def price_history(
        self,
        symbol: str,
        period_type: str = "day",
        period: int = 5,
        frequency_type: str = "minute",
        frequency: int = 1,
        need_extended_hours_data: bool = False,
        need_previous_close: bool = False,
    ) -> object:
        params = {
            "symbol": symbol,
            "periodType": period_type,
            "period": period,
            "frequencyType": frequency_type,
            "frequency": frequency,
            "needExtendedHoursData": str(need_extended_hours_data).lower(),
            "needPreviousClose": str(need_previous_close).lower(),
        }
        return self._get(f"{self.settings.marketdata_base_url}/pricehistory", params=params)

    def _retry_after_seconds(self, response: requests.Response) -> float:
        header = response.headers.get("Retry-After", "").strip()
        if header:
            try:
                return max(float(header), self.settings.backoff_seconds)
            except ValueError:
                pass
        return self.settings.backoff_seconds
