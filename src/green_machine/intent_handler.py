"""
Green Machine Intent Handler

Reads intents from Unity (xiv_intents.jsonl), routes to orchestrator,
writes results back to receipts.jsonl.

Intent queue flow:
1. Unity writes intent to xiv_intents.jsonl
2. Intent handler reads it
3. StateGraph runs the intent
4. Receipt is written to receipts.jsonl
5. Unity reads receipt and updates world state
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class IntentHandler:
    """
    Process intents from the local intent queue.

    Intents are proposals. The handler evaluates them but never executes.
    Only the local runner (outside Unity) can execute real actions.
    """

    def __init__(
        self,
        intents_path: str = None,
        orchestrator=None,
        rosco=None,
    ):
        self.intents_path = Path(intents_path) if intents_path else None
        self.orchestrator = orchestrator
        self.rosco = rosco
        self.processed_intents = set()

    def read_intents(self) -> list:
        """
        Read all intents from JSONL queue.

        Returns:
            List of intent dicts
        """
        if self.intents_path is None or not self.intents_path.exists():
            return []

        intents = []
        try:
            with open(self.intents_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        intents.append(json.loads(line))
        except IOError:
            pass

        return intents

    def process_intent(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single intent from the queue.

        Args:
            intent: intent dict from xiv_intents.jsonl

        Returns:
            result dict with receipt_id and decision
        """
        intent_id = intent.get("intent_id", "unknown")

        # Check if already processed
        if intent_id in self.processed_intents:
            return {"status": "already_processed", "intent_id": intent_id}

        # Validate intent schema
        if not self._validate_intent(intent):
            return {"status": "invalid_intent", "intent_id": intent_id}

        # Extract intent data
        world_zone = intent.get("source_zone", "unknown_zone")
        action = intent.get("requested_action", "unknown_action")
        mode = intent.get("mode", "dry_run_requested")
        parameters = intent.get("parameters", {})

        # Route to appropriate handler
        if action == "run_daily_snapshot_review":
            result = self._handle_daily_snapshot(world_zone, intent_id, mode, parameters)
        elif action == "evaluate_gates":
            result = self._handle_gate_evaluation(world_zone, intent_id, mode, parameters)
        else:
            result = {"status": "unknown_action", "action": action}

        self.processed_intents.add(intent_id)
        return result

    def _validate_intent(self, intent: Dict[str, Any]) -> bool:
        """Validate intent against schema."""
        required_fields = [
            "schema_version",
            "intent_id",
            "created_at_utc",
            "source_zone",
            "requested_action",
            "mode",
        ]

        for field in required_fields:
            if field not in intent:
                return False

        # Check forbidden actions
        forbidden = intent.get("forbidden_actions", [])
        if "broker_order" in forbidden or "git_push" in forbidden:
            # Intent explicitly forbids dangerous actions (good sign)
            pass

        return True

    def _handle_daily_snapshot(
        self,
        world_zone: str,
        intent_id: str,
        mode: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Handle daily snapshot review intent.

        This is typically called from Green Gate location.
        """
        if self.orchestrator is None:
            return {"status": "no_orchestrator", "intent_id": intent_id}

        # Simulate market data (in Phase 2, this comes from real data)
        market_data = {
            "age_seconds": 42,
            "spread_bps": 12,
            "price": parameters.get("price", 0),
        }

        positions = {"largest_position_pct": 5}
        body_state = {"player_cleared": True}

        # Run full turn
        turn_result = self.orchestrator.run_full_turn(
            market_data=market_data,
            positions=positions,
            body_state=body_state,
            world_zone=world_zone,
            task_id=intent_id,
            mode=mode,
        )

        return {
            "status": "complete",
            "intent_id": intent_id,
            "receipt_id": turn_result.get("receipt_id"),
            "decision": turn_result.get("final_decision"),
            "gates_passed": turn_result.get("gates_passed"),
        }

    def _handle_gate_evaluation(
        self,
        world_zone: str,
        intent_id: str,
        mode: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Handle gate evaluation intent.

        This is called when player walks through Risk Wall.
        """
        if self.orchestrator is None:
            return {"status": "no_orchestrator", "intent_id": intent_id}

        # Extract market data from parameters
        market_data = parameters.get("market_data", {})
        positions = parameters.get("positions", {})
        body_state = parameters.get("body_state", {"player_cleared": True})

        # Run full turn
        turn_result = self.orchestrator.run_full_turn(
            market_data=market_data,
            positions=positions,
            body_state=body_state,
            world_zone=world_zone,
            task_id=intent_id,
            mode=mode,
        )

        # Get Rosco response if available
        rosco_guidance = None
        if self.rosco:
            rosco_guidance = self.rosco.respond_to_decision(
                turn_result.get("final_decision"),
                turn_result["phases"]
                .get("risk_gates", {})
                .get("blocking_gates", []),
            )

        return {
            "status": "complete",
            "intent_id": intent_id,
            "receipt_id": turn_result.get("receipt_id"),
            "decision": turn_result.get("final_decision"),
            "gates_passed": turn_result.get("gates_passed"),
            "rosco_guidance": rosco_guidance,
        }

    def process_all_intents(self) -> Dict[str, Any]:
        """
        Process all pending intents in the queue.

        Returns:
            summary of processed intents
        """
        intents = self.read_intents()
        results = []

        for intent in intents:
            result = self.process_intent(intent)
            results.append(result)

        return {
            "intents_read": len(intents),
            "intents_processed": len(results),
            "results": results,
        }
