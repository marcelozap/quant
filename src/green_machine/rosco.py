"""
Rosco NPC Responder

Rosco is a grounding guide who:
- Routes back to evidence, receipts, or pause
- Never gives financial advice or trade calls
- Asks questions instead of answering
- Connects to body state (sleep, mood)

Responses are data-driven from rosco_lines.json.
"""

import json
from pathlib import Path
from typing import Dict, Optional, List


class RoscoResponder:
    """
    Generate safe Rosco responses based on game state and triggers.

    All responses are grounding, never advice-giving.
    """

    def __init__(self, lines_path: str = None):
        self.lines_path = Path(lines_path) if lines_path else None
        self.lines = self._load_lines()

    def _load_lines(self) -> Dict[str, list]:
        """
        Load Rosco response lines from JSON file.
        Organized by zone and trigger.
        """
        if self.lines_path is None or not self.lines_path.exists():
            # Fallback: hard-coded safe responses
            return self._get_default_lines()

        try:
            with open(self.lines_path) as f:
                data = json.load(f)
            return data.get("lines", self._get_default_lines())
        except (json.JSONDecodeError, IOError):
            return self._get_default_lines()

    def _get_default_lines(self) -> List[Dict]:
        """Fallback safe responses when file is unavailable."""
        return [
            {
                "line_id": "risk_wall_failed_gate_001",
                "zone": "risk_wall",
                "trigger": "failed_gate",
                "text": "Let's pause here. The gate is barred for a reason. What does it tell us?",
            },
            {
                "line_id": "missing_data_unknown_001",
                "zone": "evidence_trail",
                "trigger": "missing_data",
                "text": "This part is unknown. We can keep walking, but we shouldn't pretend it's proven.",
            },
            {
                "line_id": "behavioral_gate_failed_001",
                "zone": "risk_wall",
                "trigger": "behavioral_gate_failed",
                "text": "Your body is telling you something. Let's go sit in the Archive Garden for a minute.",
            },
            {
                "line_id": "receipt_ledger_invite_001",
                "zone": "any",
                "trigger": "player_asks_what_to_do",
                "text": "Let's go look at what we actually recorded. The receipts show us what worked before.",
            },
        ]

    def respond_to_failed_gate(self, blocked_gates: List[str]) -> str:
        """Generate response when a gate fails."""
        if not blocked_gates:
            return "All gates passed. Ready for review."

        # Match first blocking gate to a response
        for gate_id in blocked_gates:
            response = self._find_response(zone="risk_wall", trigger=f"{gate_id}_failed")
            if response:
                return response

        # Generic gate failure response
        return "One or more gates are barred. Let's look at what changed."

    def respond_to_missing_data(self, missing_fields: List[str]) -> str:
        """Generate response when data is UNKNOWN."""
        if not missing_fields:
            return "All data is present."

        fields_str = ", ".join(missing_fields)
        return f"We don't have {fields_str}. We can keep walking, but we shouldn't pretend we know for sure."

    def respond_to_decision(self, decision: str, blocking_gates: List[str]) -> str:
        """
        Generate response based on review decision.

        Args:
            decision: "paper_review_ready" or "blocked"
            blocking_gates: list of gates that failed

        Returns:
            Safe Rosco response text
        """
        if decision == "blocked":
            return self.respond_to_failed_gate(blocking_gates)
        elif decision == "paper_review_ready":
            return "All gates opened. Let's look at the receipts to see if this matches what we know."
        else:
            return "Let's sit in the Archive Garden and think about what we've learned."

    def _find_response(self, zone: str, trigger: str) -> Optional[str]:
        """
        Find a Rosco response matching zone and trigger.

        Args:
            zone: world location (risk_wall, evidence_trail, archive_garden, any)
            trigger: event trigger (failed_gate, missing_data, etc.)

        Returns:
            Response text or None
        """
        for line in self.lines:
            line_zone = line.get("zone", "")
            line_trigger = line.get("trigger", "")

            # Match exact zone and trigger
            if line_zone == zone and line_trigger == trigger:
                return line.get("text", "")

            # Match "any" zone
            if line_zone == "any" and line_trigger == trigger:
                return line.get("text", "")

        return None

    #: Word-boundary patterns for language Rosco must never use.
    #:
    #: These are regexes, not substrings. A previous version matched only long
    #: phrases like "should buy", so "Buy SPY here.", "Target price is 500.",
    #: "go long", "Hold your position." and "Short it." all passed as safe --
    #: a check that returns True on every real violation is worse than none.
    FORBIDDEN_PATTERNS = [
        # direction
        r"\bbuy(s|ing)?\b",
        r"\bsell(s|ing)?\b",
        r"\bshort(ing)?\s+(it|this|that|the\b)",
        r"\bgo(ing)?\s+long\b",
        r"\blong\s+position\b",
        r"\bhold(ing)?\s+(your|the|this|that)\b",
        r"\btake\s+(a\s+)?(position|profit)\b",
        r"\bentry\b|\bexit\b",
        # levels and sizing
        r"\btarget\s+price\b|\bprice\s+target\b",
        r"\bstop\s+loss\b",
        r"\bposition\s+siz(e|ing)\b|\baccount\s+siz(e|ing)\b",
        r"\ballocat(e|ion)\b",
        # prediction and guarantee
        r"\bguarantee(d|s)?\b",
        r"\bwill\s+(profit|outperform|underperform|rally|drop|rise|fall)\b",
        r"\bi\s+recommend\b|\bmy\s+advice\b|\byou\s+should\b|\byou\s+must\b",
        r"\bstrong\s+(buy|sell)\b",
        # market timing calls
        r"\b(not|now)\s+(is|the)\s+(the\s+)?time\s+to\b",
        r"\btime\s+to\s+(move|act|enter|exit|buy|sell)\b",
    ]

    #: Tickers are matched on the raw text, so case carries the signal.
    TICKER_PATTERN = r"\b[A-Z]{2,5}\b"

    #: All-caps words that are legitimate world vocabulary, not tickers.
    TICKER_ALLOWLIST = frozenset({"UNKNOWN", "XIV", "OK", "A", "I"})

    def find_violations(self) -> List[Dict[str, str]]:
        """Return every line that breaks the no-advice rule.

        Contract section 7: no ticker-specific advice; no buy, sell, hold,
        target, account size, or live call language.
        """
        import re

        violations: List[Dict[str, str]] = []
        for line in self.lines:
            raw = line.get("text", "")
            lowered = raw.lower()

            for pattern in self.FORBIDDEN_PATTERNS:
                if re.search(pattern, lowered):
                    violations.append(
                        {
                            "line_id": line.get("line_id", "?"),
                            "pattern": pattern,
                            "text": raw,
                        }
                    )
                    break
            else:
                tickers = [
                    t for t in re.findall(self.TICKER_PATTERN, raw)
                    if t not in self.TICKER_ALLOWLIST
                ]
                if tickers:
                    violations.append(
                        {
                            "line_id": line.get("line_id", "?"),
                            "pattern": f"ticker:{tickers[0]}",
                            "text": raw,
                        }
                    )

        return violations

    def verify_no_advice(self) -> bool:
        """
        Verify all loaded lines contain no financial advice.

        Returns:
            True if every line is safe; False if any line contains advice.
        """
        violations = self.find_violations()
        for violation in violations:
            print(
                f"WARNING: Rosco line {violation['line_id']} matches "
                f"{violation['pattern']}: {violation['text']!r}"
            )
        return not violations

    def three_safe_routes(self) -> Dict[str, str]:
        """
        Rosco's three canonical safe responses.
        These are the only responses allowed in production.
        """
        return {
            "route_to_receipts": "Let's go look at what we actually recorded.",
            "route_to_evidence": "Where did that come from?",
            "route_to_pause": "Let's sit down for a minute.",
        }
