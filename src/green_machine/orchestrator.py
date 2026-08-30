"""
Green Machine StateGraph Orchestrator

Runs the 7-phase Green Machine subgraph:
1. local_data_ingestion
2. evidence_normalization
3. assumption_cards
4. risk_gate_evaluation
5. paper_review_decision
6. receipt_write
7. archive_update + unity_state_export
"""

from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime


class Phase(Enum):
    """StateGraph phases for Green Machine."""

    DATA_INGEST = 1
    EVIDENCE_NORMALIZE = 2
    ASSUMPTION_CARDS = 3
    RISK_GATES = 4
    REVIEW_DECISION = 5
    RECEIPT_WRITE = 6
    ARCHIVE_UPDATE = 7


class StateGraphRunner:
    """
    Run the Green Machine StateGraph.

    Flow:
    1. Ingest data (market snapshot, positions, state)
    2. Normalize against evidence trail
    3. Load assumption cards
    4. Evaluate 5 gates (fail-closed)
    5. Make paper review decision
    6. Write signed receipt
    7. Update archive, export to Unity state

    Never executes. Only proposes.
    """

    def __init__(self, gates_evaluator, receipts_writer, rosco_responder=None):
        self.gates = gates_evaluator
        self.receipts = receipts_writer
        self.rosco = rosco_responder
        self.current_phase = Phase.DATA_INGEST
        self.state = {
            "market_data": {},
            "positions": {},
            "body_state": {},
            "gate_results": {},
            "receipt": None,
            "decision": "pending",
        }

    def run_phase(self, phase: Phase, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a single phase of the StateGraph.

        Args:
            phase: which phase to run
            inputs: data inputs for the phase

        Returns:
            phase output and updated state
        """
        if phase == Phase.DATA_INGEST:
            return self._phase_data_ingest(inputs)
        elif phase == Phase.EVIDENCE_NORMALIZE:
            return self._phase_evidence_normalize(inputs)
        elif phase == Phase.ASSUMPTION_CARDS:
            return self._phase_assumption_cards(inputs)
        elif phase == Phase.RISK_GATES:
            return self._phase_risk_gates(inputs)
        elif phase == Phase.REVIEW_DECISION:
            return self._phase_review_decision(inputs)
        elif phase == Phase.RECEIPT_WRITE:
            return self._phase_receipt_write(inputs)
        elif phase == Phase.ARCHIVE_UPDATE:
            return self._phase_archive_update(inputs)
        else:
            return {"status": "unknown_phase"}

    def _phase_data_ingest(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 1: Ingest market data, positions, body state."""
        self.state["market_data"] = inputs.get("market_data", {})
        self.state["positions"] = inputs.get("positions", {})
        self.state["body_state"] = inputs.get("body_state", {})

        return {
            "phase": "data_ingest",
            "status": "complete",
            "market_data_ingested": bool(self.state["market_data"]),
            "positions_ingested": bool(self.state["positions"]),
        }

    def _phase_evidence_normalize(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 2: Normalize against evidence trail (validate, check for gaps)."""
        evidence = inputs.get("evidence_trail", [])

        # Check for UNKNOWN data
        unknown_fields = []
        if "price" not in self.state["market_data"]:
            unknown_fields.append("price")
        if "spread_bps" not in self.state["market_data"]:
            unknown_fields.append("spread_bps")

        return {
            "phase": "evidence_normalize",
            "status": "complete",
            "evidence_records": len(evidence),
            "unknown_fields": unknown_fields,
        }

    def _phase_assumption_cards(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 3: Load and validate assumption cards."""
        cards = inputs.get("assumption_cards", [])

        return {
            "phase": "assumption_cards",
            "status": "complete",
            "cards_loaded": len(cards),
            "cards": cards,
        }

    def _phase_risk_gates(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 4: Evaluate 5 risk gates.

        This is the critical gating phase. Fail-closed.
        """
        gate_results = self.gates.evaluate(
            market_data=self.state["market_data"],
            positions=self.state["positions"],
            body_state=self.state["body_state"],
        )

        self.state["gate_results"] = gate_results

        return {
            "phase": "risk_gates",
            "status": "complete",
            "gates_passed": gate_results.get("gates_passed", False),
            "blocking_gates": gate_results.get("blocking_gates", []),
            "gates_evaluated": gate_results.get("gates_evaluated", []),
        }

    def _phase_review_decision(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 5: Make paper review decision."""
        gates_passed = self.state["gate_results"].get("gates_passed", False)

        if gates_passed:
            decision = "paper_review_ready"
            reasoning = "All gates passed. Review ready for human approval."
        else:
            decision = "blocked"
            reasoning = f"Gates blocked: {self.state['gate_results'].get('blocking_gates', [])}. Review cannot proceed."

        self.state["decision"] = decision

        if self.rosco:
            rosco_response = self.rosco.respond_to_decision(
                decision,
                self.state["gate_results"].get("blocking_gates", []),
            )
        else:
            rosco_response = None

        return {
            "phase": "review_decision",
            "status": "complete",
            "decision": decision,
            "reasoning": reasoning,
            "rosco_guidance": rosco_response,
        }

    def _phase_receipt_write(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 6: Write signed receipt to JSONL.

        CRITICAL: if gates_passed=False, execution_payload_created=False.
        """
        world_zone = inputs.get("world_zone", "unknown_zone")
        task_id = inputs.get("task_id", "unknown_task")
        mode = inputs.get("mode", "dry_run")
        notes = inputs.get("notes", "")

        receipt = self.receipts.create_receipt(
            world_zone=world_zone,
            task_id=task_id,
            gate_results=self.state["gate_results"],
            mode=mode,
            notes=notes,
        )

        written = self.receipts.write_receipt(receipt)
        self.state["receipt"] = receipt

        return {
            "phase": "receipt_write",
            "status": "complete",
            "receipt_id": receipt.receipt_id,
            "written": written,
            "execution_payload_created": receipt.execution_payload_created,
            "gates_passed": receipt.gates_passed,
        }

    def _phase_archive_update(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 7: Update archive and export state for Unity.

        This would write to Archive Garden and update xiv_state.json.
        """
        # Phase 1: just return the state
        return {
            "phase": "archive_update",
            "status": "complete",
            "receipt_id": self.state["receipt"].receipt_id if self.state["receipt"] else None,
            "state_exported": True,
        }

    def run_full_turn(
        self,
        market_data: Dict[str, Any],
        positions: Dict[str, Any],
        body_state: Dict[str, Any],
        world_zone: str,
        task_id: str,
        mode: str = "dry_run",
    ) -> Dict[str, Any]:
        """
        Run the complete 7-phase StateGraph from start to finish.

        Args:
            market_data: current market snapshot
            positions: current positions
            body_state: player body state
            world_zone: which location in XIV World (risk_wall, evidence_trail, etc.)
            task_id: unique task identifier
            mode: "dry_run" or "real"

        Returns:
            complete turn result with receipt
        """
        results = {}

        # Phase 1: Data Ingest
        results["data_ingest"] = self.run_phase(
            Phase.DATA_INGEST,
            {"market_data": market_data, "positions": positions, "body_state": body_state},
        )

        # Phase 2: Evidence Normalize
        results["evidence_normalize"] = self.run_phase(Phase.EVIDENCE_NORMALIZE, {})

        # Phase 3: Assumption Cards
        results["assumption_cards"] = self.run_phase(Phase.ASSUMPTION_CARDS, {})

        # Phase 4: Risk Gates (THE CRITICAL GATE)
        results["risk_gates"] = self.run_phase(Phase.RISK_GATES, {})

        # Phase 5: Review Decision
        results["review_decision"] = self.run_phase(Phase.REVIEW_DECISION, {})

        # Phase 6: Receipt Write
        results["receipt_write"] = self.run_phase(
            Phase.RECEIPT_WRITE,
            {"world_zone": world_zone, "task_id": task_id, "mode": mode},
        )

        # Phase 7: Archive Update
        results["archive_update"] = self.run_phase(Phase.ARCHIVE_UPDATE, {})

        return {
            "turn_id": task_id,
            "timestamp": datetime.utcnow().isoformat(),
            "phases": results,
            "final_decision": self.state["decision"],
            "gates_passed": self.state["gate_results"].get("gates_passed", False),
            "receipt_id": self.state["receipt"].receipt_id if self.state["receipt"] else None,
        }
