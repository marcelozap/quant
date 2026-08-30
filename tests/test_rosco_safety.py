"""Rosco safety tests.

Contract section 7: Rosco is a grounding companion, not a market agent.

    No ticker-specific advice. No buy, sell, hold, target, account size, or
    live call language. Route the player to evidence, receipts, or pause.

The important tests here are the ones that check the CHECKER. A safety scan
that returns True on every real violation is worse than no scan, because it
manufactures confidence. `test_checker_catches_*` is the reason this file
exists.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from green_machine.rosco import RoscoResponder  # noqa: E402

EXAMPLES = Path(__file__).resolve().parents[1] / "unity" / "Examples"
EXAMPLE_LINES = EXAMPLES / "rosco_lines.example.json"


def _responder_with(tmp_path: Path, text: str) -> RoscoResponder:
    path = tmp_path / "lines.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "xiv.rosco_lines.v1",
                "lines": [{"line_id": "probe", "zone": "any", "trigger": "t", "text": text}],
            }
        ),
        encoding="utf-8",
    )
    return RoscoResponder(str(path))


# ------------------------------------------------------- the checker itself


@pytest.mark.parametrize(
    "text",
    [
        "Buy SPY here.",
        "I would sell NVDA now.",
        "Target price is 500.",
        "This is a strong buy signal.",
        "You should go long.",
        "Hold your position.",
        "Short it.",
        "Guaranteed returns.",
        "Now is the time to buy.",
        "This is not the time to move.",
        "My advice is to wait for the entry.",
        "Set a stop loss below the level.",
        "Increase your position size.",
        "AAPL looks ready.",
    ],
)
def test_checker_catches_unsafe_lines(tmp_path, text):
    """Every one of these passed the original substring checker."""
    responder = _responder_with(tmp_path, text)
    assert responder.verify_no_advice() is False, f"unsafe line slipped through: {text!r}"
    assert responder.find_violations(), "a violation must be reported, not just a False"


@pytest.mark.parametrize(
    "text",
    [
        "Let's pause here. The gate is barred for a reason. What does it tell us?",
        "This part is unknown. We can keep walking, but we shouldn't pretend it's proven.",
        "Let's go look at what we actually recorded.",
        "The Archive Garden has the full story. Let's walk there and sit for a bit.",
        "The data is too old. We need to wait for fresh information before we can see clearly.",
        "Your body is telling you something. Let's go sit for a minute.",
    ],
)
def test_checker_allows_safe_grounding_lines(tmp_path, text):
    """The checker must not be so blunt that Rosco cannot speak."""
    assert _responder_with(tmp_path, text).verify_no_advice() is True


# ------------------------------------------------------ the shipped content


def test_shipped_example_lines_are_safe():
    """The tracked example file is what ships. It must pass its own rule."""
    responder = RoscoResponder(str(EXAMPLE_LINES))
    violations = responder.find_violations()
    assert violations == [], f"unsafe shipped lines: {violations}"


def test_shipped_lines_route_somewhere_safe():
    """Contract section 7: route to evidence, receipts, or pause."""
    data = json.loads(EXAMPLE_LINES.read_text(encoding="utf-8"))
    assert data["lines"], "example file must contain lines"
    for line in data["lines"]:
        assert line.get("text", "").strip(), f"line {line.get('line_id')} has no text"
        assert line.get("zone"), f"line {line.get('line_id')} has no zone"
        assert line.get("trigger"), f"line {line.get('line_id')} has no trigger"


def test_default_lines_are_safe():
    """The built-in fallback lines ship too, even with no file present."""
    assert RoscoResponder(None).verify_no_advice() is True
