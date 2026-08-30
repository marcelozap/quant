"""
Green Machine Risk Gates

Five fail-closed gates that must all pass before a review can proceed.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass


#: The gates the Risk Wall is defined by. All of them must be present AND
#: passed for ``gates_passed`` to be true. Adding an id here makes it mandatory.
REQUIRED_GATES = frozenset(
    {
        "stale_data",
        "abnormal_spread",
        "concentration_limit",
        "drawdown_guard",
        "behavioral_gate",
    }
)

CONFIG_OK = "ok"
CONFIG_MISSING = "missing"
CONFIG_INVALID = "invalid"


@dataclass
class GateResult:
    """Result of a single gate evaluation."""
    gate_id: str
    status: str  # "passed" | "failed" | "blocked" | "unknown"
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
        self.config_state = CONFIG_OK
        self.config_error = None
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load gate configuration from JSON file.

        Contract section 5 draws a distinction this method preserves:
          missing config -> gates are UNKNOWN (nothing is known yet)
          invalid config -> gates are BLOCKED (something is wrong)
        Both make ``gates_passed`` false. Neither ever returns a usable config.

        This method must not call itself. A previous version used
        ``data.get("gates", self._load_config())``; Python evaluates that default
        argument eagerly, so every successful load recursed until RecursionError.
        """
        if self.config_path is None or not self.config_path.exists():
            self.config_state = CONFIG_MISSING
            self.config_error = f"config not found: {self.config_path}"
            return {}

        try:
            with open(self.config_path, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError, OSError) as exc:
            self.config_state = CONFIG_INVALID
            self.config_error = f"config unreadable: {exc}"
            return {}

        if not isinstance(data, dict):
            self.config_state = CONFIG_INVALID
            self.config_error = "config root is not an object"
            return {}

        gates = data.get("gates")
        if not isinstance(gates, dict) or not gates:
            self.config_state = CONFIG_INVALID
            self.config_error = "config has no gates object"
            return {}

        absent = REQUIRED_GATES - set(gates)
        if absent:
            self.config_state = CONFIG_INVALID
            self.config_error = f"config missing required gates: {sorted(absent)}"
            return {}

        self.config_state = CONFIG_OK
        self.config_error = None
        return gates

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

        # A config problem short-circuits every gate, but each gate is still
        # REPORTED so the Risk Wall has something to render.
        if self.config_state != CONFIG_OK:
            status = "unknown" if self.config_state == CONFIG_MISSING else "blocked"
            results = [
                GateResult(
                    gate_id=gate_id,
                    status=status,
                    threshold="UNKNOWN",
                    observed="UNKNOWN",
                    reason=self.config_error or "config unavailable",
                )
                for gate_id in sorted(REQUIRED_GATES)
            ]
            return self._summarize(results)

        checks = {
            "stale_data": lambda cfg: self._check_stale_data(
                market_data, cfg.get("max_age_seconds", 300)
            ),
            "abnormal_spread": lambda cfg: self._check_abnormal_spread(
                market_data, cfg.get("max_spread_bps", 50)
            ),
            "concentration_limit": lambda cfg: self._check_concentration(
                positions, cfg.get("max_single_name_percent", 10)
            ),
            "drawdown_guard": lambda cfg: self._check_drawdown(
                positions, cfg.get("max_drawdown_percent", -5)
            ),
            "behavioral_gate": lambda cfg: self._check_behavioral(
                body_state, cfg.get("requires_manual_clear", True)
            ),
        }

        results = []
        for gate_id in sorted(REQUIRED_GATES):
            cfg = self.config.get(gate_id)

            if not isinstance(cfg, dict):
                results.append(
                    GateResult(
                        gate_id=gate_id,
                        status="blocked",
                        threshold="UNKNOWN",
                        observed="UNKNOWN",
                        reason="Gate config missing.",
                    )
                )
                continue

            # A disabled gate is BLOCKED, never skipped. Skipping is what lets an
            # empty result list reach all([]) and answer True.
            if not cfg.get("enabled", False):
                results.append(
                    GateResult(
                        gate_id=gate_id,
                        status="blocked",
                        threshold="UNKNOWN",
                        observed="disabled",
                        reason="Gate is disabled in config; a disabled safety gate never passes.",
                    )
                )
                continue

            # A gate that raises must become a BLOCKED gate, never an exception
            # that escapes to the caller. An unhandled error mid-evaluation would
            # abandon the wall entirely instead of failing closed.
            try:
                results.append(checks[gate_id](cfg))
            except Exception as exc:  # noqa: BLE001 - deliberate catch-all
                results.append(
                    GateResult(
                        gate_id=gate_id,
                        status="blocked",
                        threshold="UNKNOWN",
                        observed="UNKNOWN",
                        reason=f"Gate raised {type(exc).__name__}: {exc}",
                    )
                )

        return self._summarize(results)

    def _summarize(self, results: List[GateResult]) -> Dict[str, Any]:
        """Collapse gate results into the contract's result block.

        ``gates_passed`` requires the complete required set to be present and
        every one of them to have passed. It is deliberately not the bare
        ``all(...)`` of whatever happened to be evaluated, because ``all([])``
        is True and that is a fail-OPEN.
        """
        evaluated = {r.gate_id for r in results}
        complete = REQUIRED_GATES.issubset(evaluated)
        all_passed = (
            bool(results)
            and complete
            and all(r.status == "passed" for r in results)
        )
        blocking_gates = [r.gate_id for r in results if r.status != "passed"]

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
            "config_state": self.config_state,
            "config_error": self.config_error,
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
        """Gate 3: No position over limit.

        Absent position data is UNKNOWN, not "no concentration". Contract
        section 6: missing evidence is UNKNOWN, not 0, not blank, not guessed.
        """
        if not positions:
            return GateResult(
                gate_id="concentration_limit",
                status="blocked",
                threshold=f"max_single_name_percent={max_percent}",
                observed="positions=UNKNOWN",
                reason="No position data available; concentration cannot be shown to be within limit.",
            )

        # `positions` legitimately carries scalar keys alongside per-name
        # entries (drawdown_percent lives here too), so only dict values with a
        # "percent" field are positions. Anything unreadable blocks.
        weights = []
        for name, entry in positions.items():
            if not isinstance(entry, dict) or "percent" not in entry:
                continue
            try:
                weights.append(float(entry["percent"]))
            except (TypeError, ValueError):
                return GateResult(
                    gate_id="concentration_limit",
                    status="blocked",
                    threshold=f"max_single_name_percent={max_percent}",
                    observed=f"{name}.percent=UNKNOWN",
                    reason=f"Position {name!r} has an unreadable percent.",
                )

        if not weights:
            return GateResult(
                gate_id="concentration_limit",
                status="blocked",
                threshold=f"max_single_name_percent={max_percent}",
                observed="positions=UNKNOWN",
                reason="No readable position weights; concentration cannot be shown to be within limit.",
            )

        largest = max(weights)
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
        """Gate 5: Player behavioral/body state.

        Manual clear only. Config cannot turn this into an automatic pass --
        a flag that makes a hard_block gate self-clear would defeat the gate.
        """
        if not requires_manual_clear:
            return GateResult(
                gate_id="behavioral_gate",
                status="blocked",
                threshold="manual_clear_required",
                observed="requires_manual_clear=false",
                reason="requires_manual_clear must stay true; this gate cannot self-clear.",
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
