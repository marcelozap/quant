"""Regression tests for the fail-closed invariant of the Risk Wall.

Every test here corresponds to a defect that was live in the working tree on
2026-08-30. They exist so those five paths cannot silently come back.

The single invariant under test:

    gates_passed is true ONLY when all five required gates were evaluated and
    all five passed. Never because nothing was evaluated.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from green_machine.gates import REQUIRED_GATES, GateEvaluator  # noqa: E402

EXAMPLE_CONFIG = Path(__file__).resolve().parents[1] / "unity" / "Examples" / "green_machine_gate_config.example.json"


def _base_config() -> dict:
    return json.loads(EXAMPLE_CONFIG.read_text(encoding="utf-8"))


def _write(tmp_path: Path, config: dict, name: str = "gates.json") -> str:
    path = tmp_path / name
    path.write_text(json.dumps(config), encoding="utf-8")
    return str(path)


def _clean_inputs() -> tuple[dict, dict, dict]:
    """Inputs that pass every gate, so a test failure is about the gate logic."""
    market = {"age_seconds": 42, "spread_bps": 10}
    positions = {"AAA": {"percent": 4.0}, "drawdown_percent": -1.0}
    body = {"player_cleared": True}
    return market, positions, body


# --------------------------------------------------------------- the baseline


def test_valid_config_loads_without_recursing(tmp_path):
    """A valid config file must load.

    Regression: `data.get("gates", self._load_config())` evaluated its default
    eagerly, so every successful load recursed until RecursionError.
    """
    evaluator = GateEvaluator(_write(tmp_path, _base_config()))
    assert evaluator.config_state == "ok"
    assert set(evaluator.config) >= REQUIRED_GATES


def test_clean_inputs_pass_all_five(tmp_path):
    evaluator = GateEvaluator(_write(tmp_path, _base_config()))
    result = evaluator.evaluate(*_clean_inputs())
    assert result["gates_passed"] is True
    assert len(result["gates_evaluated"]) == len(REQUIRED_GATES)


# ------------------------------------------------------- the fail-open paths


def test_all_gates_disabled_does_not_pass(tmp_path):
    """Regression: disabled gates were skipped, leaving all([]) == True."""
    config = _base_config()
    for gate in config["gates"].values():
        gate["enabled"] = False

    result = GateEvaluator(_write(tmp_path, config)).evaluate(*_clean_inputs())

    assert result["gates_passed"] is False
    assert len(result["gates_evaluated"]) == len(REQUIRED_GATES), "a disabled gate must still be reported"
    assert all(entry["status"] == "blocked" for entry in result["gates_evaluated"])


def test_one_gate_disabled_does_not_pass(tmp_path):
    config = _base_config()
    config["gates"]["drawdown_guard"]["enabled"] = False

    result = GateEvaluator(_write(tmp_path, config)).evaluate(*_clean_inputs())

    assert result["gates_passed"] is False
    statuses = {e["gate_id"]: e["status"] for e in result["gates_evaluated"]}
    assert statuses["drawdown_guard"] == "blocked"


def test_empty_gates_object_fails_closed(tmp_path):
    """Regression: `config.get("gates", {})` gave an empty dict and passed."""
    result = GateEvaluator(_write(tmp_path, {"schema_version": "x", "gates": {}})).evaluate(*_clean_inputs())

    assert result["gates_passed"] is False
    assert result["config_state"] == "invalid"
    assert len(result["gates_evaluated"]) == len(REQUIRED_GATES)


def test_config_missing_a_required_gate_fails_closed(tmp_path):
    config = _base_config()
    del config["gates"]["behavioral_gate"]

    result = GateEvaluator(_write(tmp_path, config)).evaluate(*_clean_inputs())

    assert result["gates_passed"] is False
    assert result["config_state"] == "invalid"


def test_malformed_config_fails_closed(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{not json", encoding="utf-8")

    result = GateEvaluator(str(path)).evaluate(*_clean_inputs())

    assert result["gates_passed"] is False
    assert result["config_state"] == "invalid"
    assert all(e["status"] == "blocked" for e in result["gates_evaluated"])


def test_missing_config_reports_unknown_not_passed(tmp_path):
    """Contract section 5: missing config means gates display UNKNOWN."""
    result = GateEvaluator(str(tmp_path / "absent.json")).evaluate(*_clean_inputs())

    assert result["gates_passed"] is False
    assert result["config_state"] == "missing"
    assert all(e["status"] == "unknown" for e in result["gates_evaluated"])


def test_absent_positions_block_concentration(tmp_path):
    """Regression: empty positions returned `passed` ("no_positions")."""
    market, _positions, body = _clean_inputs()
    result = GateEvaluator(_write(tmp_path, _base_config())).evaluate(market, {}, body)

    assert result["gates_passed"] is False
    statuses = {e["gate_id"]: e["status"] for e in result["gates_evaluated"]}
    assert statuses["concentration_limit"] == "blocked"


def test_behavioral_gate_cannot_self_clear(tmp_path):
    """Regression: requires_manual_clear=false made the gate pass automatically."""
    config = _base_config()
    config["gates"]["behavioral_gate"]["requires_manual_clear"] = False

    result = GateEvaluator(_write(tmp_path, config)).evaluate(*_clean_inputs())

    assert result["gates_passed"] is False
    statuses = {e["gate_id"]: e["status"] for e in result["gates_evaluated"]}
    assert statuses["behavioral_gate"] == "blocked"


def test_uncleared_body_state_does_not_pass(tmp_path):
    market, positions, _body = _clean_inputs()
    result = GateEvaluator(_write(tmp_path, _base_config())).evaluate(market, positions, {})

    assert result["gates_passed"] is False


# ------------------------------------------------------------- the invariant


@pytest.mark.parametrize(
    "market,positions,body",
    [
        ({}, {}, {}),
        ({"age_seconds": 99999, "spread_bps": 10}, {"AAA": {"percent": 4.0}, "drawdown_percent": -1.0}, {"player_cleared": True}),
        ({"age_seconds": 42, "spread_bps": 9999}, {"AAA": {"percent": 4.0}, "drawdown_percent": -1.0}, {"player_cleared": True}),
        ({"age_seconds": 42, "spread_bps": 10}, {"AAA": {"percent": 99.0}, "drawdown_percent": -1.0}, {"player_cleared": True}),
        ({"age_seconds": 42, "spread_bps": 10}, {"AAA": {"percent": 4.0}, "drawdown_percent": -80.0}, {"player_cleared": True}),
    ],
)
def test_any_bad_input_blocks_the_wall(tmp_path, market, positions, body):
    """No single bad input may ever produce gates_passed."""
    result = GateEvaluator(_write(tmp_path, _base_config())).evaluate(market, positions, body)
    assert result["gates_passed"] is False


def test_gates_passed_never_true_on_empty_results(tmp_path):
    """The invariant stated directly: an empty evaluation is never a pass."""
    evaluator = GateEvaluator(_write(tmp_path, _base_config()))
    assert evaluator._summarize([])["gates_passed"] is False
