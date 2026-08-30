"""Regression tests for XIV intent safety boundaries."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from green_machine.intent_handler import IntentHandler


def _intent(**overrides):
    payload = {
        "schema_version": "xiv.intent.v1",
        "intent_id": "intent_001",
        "created_at_utc": "2026-08-30T14:20:00Z",
        "source_zone": "green_gate",
        "requested_action": "evaluate_gates",
        "mode": "dry_run_requested",
        "parameters": {},
        "forbidden_actions": [
            "broker_order",
            "deployment",
            "payment",
            "file_delete",
            "git_push",
        ],
    }
    payload.update(overrides)
    return payload


def test_intent_allows_known_review_action_without_orchestrator():
    result = IntentHandler().process_intent(_intent())

    assert result["status"] == "no_orchestrator"
    assert result["intent_id"] == "intent_001"


def test_intent_rejects_broker_order_even_if_forbidden_actions_omitted():
    result = IntentHandler().process_intent(
        _intent(requested_action="broker_order", forbidden_actions=[])
    )

    assert result == {"status": "invalid_intent", "intent_id": "intent_001"}


def test_intent_rejects_git_push_even_if_intent_does_not_self_report_it():
    result = IntentHandler().process_intent(
        _intent(requested_action="git_push", forbidden_actions=[])
    )

    assert result == {"status": "invalid_intent", "intent_id": "intent_001"}


def test_intent_rejects_unknown_action_before_processing():
    result = IntentHandler().process_intent(
        _intent(requested_action="run_live_execution", forbidden_actions=[])
    )

    assert result == {"status": "invalid_intent", "intent_id": "intent_001"}


def test_intent_rejects_malformed_forbidden_actions():
    result = IntentHandler().process_intent(
        _intent(forbidden_actions="broker_order")
    )

    assert result == {"status": "invalid_intent", "intent_id": "intent_001"}
