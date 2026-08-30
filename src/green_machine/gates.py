"""
Green Machine Risk Gates

Five fail-closed gates that must all pass before a review can proceed.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class GateResult:
    """Result of a single gate evaluation."""
    gate_id: str
    status: str  # "passed" or "failed"
    threshold: str  # human-readable threshold
    observed: str  # human-readable observed value
    reason: str = ""  # optional explanation


class GateEvaluator:
    """
    Evaluate all five Green Machine risk gates.

    Fail-closed: if any gate fails, no execution payload is created.
    """

    def __init__(self, config_path: str = None):
        self.config_path = Path(config_path) if config_path else None
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load gate configuration from JSON file.
        If file is missing or invalid, fail-closed: all gates blocked.
        """
        if self.config_path is None or not self.config_path.exists():
            # Default: all gates enabled, fail-closed
            return {
                "stale_data": {"enabled": True, "max_age_seconds": 300},
                "abnormal_spread": {"enabled": True, "max_spread_bps": 50},
                "concentration_limit": {"enabled": True, "max_single_name_percent": 10},
                "drawdown_guard": {"enabled": True, "max_drawdown_percent": -5},
                "behavioral_gate": {"enabled": True, "requires_manual_clear": True},
            }

        try:
            with open(self.config_path) as f:
                data = json.load(f)
            return data.get("gates", self._load_config())
        except (json.JSONDecodeError, IOError):
            # Invalid config = fail-closed
            return self._load_config()

    def evaluate(
        self,
        market_data: Dict[str, Any] = None,
        positions: Dict[str, Any] = None,
        body_state: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate all gates against provided data.

        Args:
            market_data: current market snapshot (price, spread, age, etc.)
            positions: current positions (size, concentration)
            body_state: player state (slept, cleared, etc.)

        Returns:
            {
                "gates_evaluated": [GateResult, ...],
                "gates_passed": bool,
                "blocking_gates": [gate_ids that failed],
            }
        """
        market_data = market_data or {}
        positions = positions or {}
        body_state = body_state or {}

        results = []

        # Gate 1: Stale Data
        if self.config.get("stale_data", {}).get("enabled"):
            results.append(
                self._check_stale_data(
                    market_data,
                    self.config["stale_data"].get("max_age_seconds", 300),
                )
            )

        # Gate 2: Abnormal Spread
        if self.config.get("abnormal_spread", {}).get("enabled"):
            results.append(
                self._check_abnormal_spread(
                    market_data,
                    self.config["abnormal_spread"].get("max_spread_bps", 50),
                )
            )

        # Gate 3: Concentration Limit
        if self.config.get("concentration_limit", {}).get("enabled"):
            results.append(
                self._check_concentration(
                    positions,
                    self.config["concentration_limit"].get("max_single_name_percent", 10),
                )
            )

        # Gate 4: Drawdown Guard
        if self.config.get("drawdown_guard", {}).get("enabled"):
            results.append(
                self._check_drawdown(
                    positions,
                    self.config["drawdown_guard"].get("max_drawdown_percent", -5),
                )
            )

        # Gate 5: Behavioral Gate
        if self.config.get("behavioral_gate", {}).get("enabled"):
            results.append(
                self._check_behavioral(
                    body_state,
                    self.config["behavioral_gate"].get("requires_manual_clear", True),
                )
            )

        # Fail-closed: ALL gates must pass
        all_passed = all(r.status == "passed" for r in results)
        blocking_gates = [r.gate_id for r in results if r.status == "failed"]

        return {
            "gates_evaluated": [
                {
                    "gate_id": r.gate_id,
                    "status": r.status,
                    "threshold": r.threshold,
                    "observed": r.observed,
                    "reason": r.reason,
                }
                for r in results
            ],
            "gates_passed": all_passed,
            "blocking_gates": blocking_gates,
        }

    def _check_stale_data(self, market_data: Dict, max_age_seconds: int) -> GateResult:
        """Gate 1: Market data must be fresh."""
        age = market_data.get("age_seconds", None)

        if age is None:
            return GateResult(
                gate_id="stale_data",
                status="failed",
                threshold=f"max_age_seconds={max_age_seconds}",
                observed="age_seconds=UNKNOWN",
                reason="No timestamp data available.",
            )

        passed = age <= max_age_seconds

        return GateResult(
            gate_id="stale_data",
            status="passed" if passed else "failed",
            threshold=f"max_age_seconds={max_age_seconds}",
            observed=f"age_seconds={age}",
            reason=""
            if passed
            else f"Data is {age}s old; max allowed is {max_age_seconds}s.",
        )

    def _check_abnormal_spread(self, market_data: Dict, max_spread_bps: int) -> GateResult:
        """Gate 2: Bid-ask spread must be normal."""
        spread = market_data.get("spread_bps", None)

        if spread is None:
            return GateResult(
                gate_id="abnormal_spread",
                status="failed",
                threshold=f"max_spread_bps={max_spread_bps}",
                observed="spread_bps=UNKNOWN",
                reason="No spread data available.",
            )

        passed = spread <= max_spread_bps

        return GateResult(
            gate_id="abnormal_spread",
            status="passed" if passed else "failed",
            threshold=f"max_spread_bps={max_spread_bps}",
            observed=f"spread_bps={spread}",
            reason="" if passed else f"Spread {spread}bps exceeds max {max_spread_bps}bps.",
        )

    def _check_concentration(
        self, positions: Dict, max_percent: int
    ) -> GateResult:
        """Gate 3: No position over limit."""
        if not positions:
            return GateResult(
                gate_id="concentration_limit",
                status="passed",
                threshold=f"max_single_name_percent={max_percent}",
                observed="no_positions",
            )

        largest = max(
            (float(p.get("percent", 0)) for p in positions.values()),
            default=0,
        )

        passed = largest <= max_percent

        return GateResult(
            gate_id="concentration_limit",
            status="passed" if passed else "failed",
            threshold=f"max_single_name_percent={max_percent}",
            observed=f"largest_position_pct={largest}",
            reason="" if passed else f"Largest position {largest}% exceeds {max_percent}%.",
        )

    def _check_drawdown(self, positions: Dict, max_drawdown_percent: float) -> GateResult:
        """Gate 4: Equity drawdown within guard."""
        drawdown = positions.get("drawdown_percent", None)

        if drawdown is None:
            return GateResult(
                gate_id="drawdown_guard",
                status="failed",
                threshold=f"max_drawdown_percent={max_drawdown_percent}",
                observed="drawdown_percent=UNKNOWN",
                reason="No drawdown data available.",
            )

        passed = drawdown >= max_drawdown_percent  # max_drawdown is negative

        return GateResult(
            gate_id="drawdown_guard",
            status="passed" if passed else "failed",
            threshold=f"max_drawdown_percent={max_drawdown_percent}",
            observed=f"drawdown_percent={drawdown}",
            reason=""
            if passed
            else f"Drawdown {drawdown}% exceeds guard {max_drawdown_percent}%.",
        )

    def _check_behavioral(
        self, body_state: Dict, requires_manual_clear: bool
    ) -> GateResult:
        """Gate 5: Player behavioral/body state."""
        if not requires_manual_clear:
            return GateResult(
                gate_id="behavioral_gate",
                status="passed",
                threshold="behavioral_gate_disabled",
                observed="N/A",
            )

        cleared = body_state.get("player_cleared", False)
        reason = body_state.get("reason", "not_cleared")

        if cleared:
            return GateResult(
                gate_id="behavioral_gate",
                status="passed",
                threshold="manual_clear_required",
                observed="cleared_by_player",
            )
        else:
            return GateResult(
                gate_id="behavioral_gate",
                status="failed",
                threshold="manual_clear_required",
                observed="not_cleared",
                reason=reason,
            )
