"""Shared rate limiting for live API calls."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import tempfile
import time
from typing import Callable, List, Optional

import fcntl


@dataclass(frozen=True)
class RateLimitSnapshot:
    max_calls_per_minute: int
    calls_in_window: int
    available_now: int
    wait_seconds_if_full: float


class RateLimiter:
    """Sliding-window limiter backed by a shared local state file."""

    def __init__(
        self,
        max_calls_per_minute: int,
        state_path: str = "/tmp/quant_live_schwab_rate_limit.json",
        clock: Optional[Callable[[], float]] = None,
        sleeper: Optional[Callable[[float], None]] = None,
    ) -> None:
        if max_calls_per_minute <= 0:
            raise ValueError("max_calls_per_minute must be positive")
        self.max_calls_per_minute = max_calls_per_minute
        self.state_path = Path(state_path)
        self._clock = clock or time.monotonic
        self._sleep = sleeper or time.sleep

    def acquire(self) -> None:
        while True:
            with self._locked_file() as handle:
                calls = self._load_calls(handle)
                calls = self._prune(calls)
                if len(calls) < self.max_calls_per_minute:
                    calls.append(self._clock())
                    self._save_calls(handle, calls)
                    return
                wait_seconds = max(0.0, 60.0 - (self._clock() - calls[0]))
            self._sleep(wait_seconds)

    def snapshot(self) -> RateLimitSnapshot:
        with self._locked_file() as handle:
            calls = self._load_calls(handle)
            calls = self._prune(calls)
            self._save_calls(handle, calls)
            used = len(calls)
            available = max(0, self.max_calls_per_minute - used)
            wait = 0.0 if available > 0 else max(0.0, 60.0 - (self._clock() - calls[0]))
            return RateLimitSnapshot(
                max_calls_per_minute=self.max_calls_per_minute,
                calls_in_window=used,
                available_now=available,
                wait_seconds_if_full=wait,
            )

    def _prune(self, calls: List[float]) -> List[float]:
        now = self._clock()
        return [timestamp for timestamp in calls if now - timestamp < 60.0]

    def _load_calls(self, handle) -> List[float]:
        handle.seek(0)
        raw = handle.read().strip()
        if not raw:
            return []
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            return []
        calls = payload.get("calls", [])
        if not isinstance(calls, list):
            return []
        return [float(item) for item in calls]

    def _save_calls(self, handle, calls: List[float]) -> None:
        handle.seek(0)
        handle.truncate()
        json.dump({"calls": calls}, handle)
        handle.flush()

    def _locked_file(self):
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        handle = open(self.state_path, "a+", encoding="utf-8")
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        return _LockedFileHandle(handle)


class _LockedFileHandle:
    def __init__(self, handle) -> None:
        self.handle = handle

    def __enter__(self):
        return self.handle

    def __exit__(self, exc_type, exc, tb) -> None:
        self.handle.flush()
        fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
        self.handle.close()
