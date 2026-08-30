"""
Test Green Machine Gate Evaluator

Verify all 5 gates work correctly and fail-closed.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from green_machine.gates import GateEvaluator

EXAMPLE_CONFIG = str(
    Path(__file__).resolve().parents[1] / "unity" / "Examples" / "green_machine_gate_config.example.json"
)



def test_all_gates_pass():
    """Test: all gates pass when data is good."""
    evaluator = GateEvaluator(EXAMPLE_CONFIG)

    market_data = {
        "age_seconds": 42,
        "spread_bps": 12,
    }

    positions = {
        "SPY": {"percent": 5},
        "NVDA": {"percent": 3},
        "drawdown_percent": -2.3,
    }

    body_state = {
        "player_cleared": True,
    }

    result = evaluator.evaluate(market_data, positions, body_state)

    assert result["gates_passed"] is True, "All gates should pass"
    assert len(result["blocking_gates"]) == 0, "No gates should be blocked"
    assert len(result["gates_evaluated"]) == 5, "All 5 gates should be evaluated"

    print("[PASS] test_all_gates_pass")


def test_stale_data_gate_fails():
    """Test: stale data gate fails when data is too old."""
    evaluator = GateEvaluator(EXAMPLE_CONFIG)

    market_data = {
        "age_seconds": 400,  # Exceeds 300 second max
        "spread_bps": 12,
    }

    positions = {"drawdown_percent": -2.3}
    body_state = {"player_cleared": True}

    result = evaluator.evaluate(market_data, positions, body_state)

    assert result["gates_passed"] is False, "Should fail due to stale data"
    assert "stale_data" in result["blocking_gates"], "stale_data should block"

    print("[PASS] test_stale_data_gate_fails")


def test_abnormal_spread_gate_fails():
    """Test: abnormal spread gate fails when spread is too wide."""
    evaluator = GateEvaluator(EXAMPLE_CONFIG)

    market_data = {
        "age_seconds": 42,
        "spread_bps": 118,  # Exceeds 50 bps max
    }

    positions = {"drawdown_percent": -2.3}
    body_state = {"player_cleared": True}

    result = evaluator.evaluate(market_data, positions, body_state)

    assert result["gates_passed"] is False, "Should fail due to abnormal spread"
    assert "abnormal_spread" in result["blocking_gates"]

    print("[PASS] test_abnormal_spread_gate_fails")


def test_concentration_gate_fails():
    """Test: concentration gate fails when position is too large."""
    evaluator = GateEvaluator(EXAMPLE_CONFIG)

    market_data = {
        "age_seconds": 42,
        "spread_bps": 12,
    }

    positions = {
        "SPY": {"percent": 25},  # Exceeds 10% max
        "drawdown_percent": -2.3,
    }

    body_state = {"player_cleared": True}

    result = evaluator.evaluate(market_data, positions, body_state)

    assert result["gates_passed"] is False, "Should fail due to concentration"
    assert "concentration_limit" in result["blocking_gates"]

    print("[PASS] test_concentration_gate_fails")


def test_behavioral_gate_fails():
    """Test: behavioral gate fails when player hasn't cleared."""
    evaluator = GateEvaluator(EXAMPLE_CONFIG)

    market_data = {
        "age_seconds": 42,
        "spread_bps": 12,
    }

    positions = {"drawdown_percent": -2.3}
    body_state = {
        "player_cleared": False,
        "reason": "poor_sleep",
    }

    result = evaluator.evaluate(market_data, positions, body_state)

    assert result["gates_passed"] is False, "Should fail due to behavioral gate"
    assert "behavioral_gate" in result["blocking_gates"]

    print("[PASS] test_behavioral_gate_fails")


def test_missing_data_blocks():
    """Test: missing data blocks the gate."""
    evaluator = GateEvaluator(EXAMPLE_CONFIG)

    market_data = {
        # age_seconds missing
        "spread_bps": 12,
    }

    positions = {"drawdown_percent": -2.3}
    body_state = {"player_cleared": True}

    result = evaluator.evaluate(market_data, positions, body_state)

    assert result["gates_passed"] is False, "Missing data should block"
    assert "stale_data" in result["blocking_gates"]

    print("[PASS] test_missing_data_blocks")


def test_fail_closed_rule():
    """Test: one gate failing blocks all."""
    evaluator = GateEvaluator(EXAMPLE_CONFIG)

    # One bad gate, rest OK
    market_data = {
        "age_seconds": 400,  # FAILS
        "spread_bps": 12,  # OK
    }

    positions = {"drawdown_percent": -2.3}  # OK
    body_state = {"player_cleared": True}  # OK

    result = evaluator.evaluate(market_data, positions, body_state)

    # Fail-closed: one failure = all fail
    assert result["gates_passed"] is False, "One gate failure should block all"
    assert len(result["blocking_gates"]) >= 1

    print("[PASS] test_fail_closed_rule")


if __name__ == "__main__":
    test_all_gates_pass()
    test_stale_data_gate_fails()
    test_abnormal_spread_gate_fails()
    test_concentration_gate_fails()
    test_behavioral_gate_fails()
    test_missing_data_blocks()
    test_fail_closed_rule()

    print("\n[SUCCESS] All gate tests passed!")
