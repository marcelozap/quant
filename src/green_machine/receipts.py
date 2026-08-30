"""
Green Machine Receipt Writer

Writes signed JSONL receipts per canonical contract.
Each receipt is immutable, timestamped, and hashed.
"""

import json
import hashlib
import hmac
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class Receipt:
    """A single receipt (one line of JSONL)."""

    schema_version: str
    receipt_id: str
    timestamp_utc: str
    source: str
    world_zone: str
    task_id: str
    mode: str
    decision: str
    outcome: str
    evidence_hash: str
    state_before_hash: str
    state_after_hash: str
    gates_evaluated: list
    gates_passed: bool
    execution_payload_created: bool
    human_approval_required: bool
    notes: str
    previous_record_hash: str
    record_hash: str
    signature_scheme: str
    signature: str


class ReceiptWriter:
    """
    Write signed JSONL receipts to local disk.

    Canonical path: C:\Users\Green Machine\quant\unity\LocalState\receipts.jsonl
    """

    def __init__(
        self,
        receipts_path: str = None,
        signing_key: str = None,
    ):
        self.receipts_path = Path(receipts_path) if receipts_path else None
        self.signing_key = signing_key or self._get_local_key()

    def _get_local_key(self) -> str:
        """
        Get local signing key. For Phase 1, use a fixed development key.
        In production, load from secure storage.
        """
        # Phase 1: development key only
        return "local-dev-key-not-for-production"

    def _sha256(self, data: str) -> str:
        """Compute SHA256 hash of data."""
        return "sha256:" + hashlib.sha256(data.encode()).hexdigest()

    def _sign(self, data: str) -> str:
        """
        Sign data with local key.
        Phase 1: HMAC-SHA256 (not full ed25519, but same structure).
        """
        signature = hmac.new(
            self.signing_key.encode(),
            data.encode(),
            hashlib.sha256,
        ).hexdigest()
        return "base64:" + signature[:64]  # Truncate for display

    def create_receipt(
        self,
        world_zone: str,
        task_id: str,
        gate_results: Dict[str, Any],
        mode: str = "dry_run",
        notes: str = "",
        previous_record_hash: str = None,
    ) -> Receipt:
        """
        Create a receipt from gate evaluation results.

        HARD RULE: if gates_passed=False, then execution_payload_created=False.
        """
        timestamp = datetime.utcnow().isoformat() + "Z"
        receipt_id = timestamp.replace(":", "-").replace(".", "-") + "_" + task_id

        # Determine decision
        gates_passed = gate_results.get("gates_passed", False)
        decision = "approved" if gates_passed else "blocked"
        outcome = "all_gates_passed" if gates_passed else "failed_gate"

        # CRITICAL: execution_payload is created only if ALL gates pass
        execution_payload_created = gates_passed is True

        # Create receipt object
        receipt = Receipt(
            schema_version="xiv.receipt.v1",
            receipt_id=receipt_id,
            timestamp_utc=timestamp,
            source="green_machine",
            world_zone=world_zone,
            task_id=task_id,
            mode=mode,
            decision=decision,
            outcome=outcome,
            evidence_hash=self._sha256(json.dumps(gate_results, sort_keys=True)),
            state_before_hash="sha256:0000000000000000000000000000000000000000000000000000000000000000",  # Placeholder
            state_after_hash="sha256:1111111111111111111111111111111111111111111111111111111111111111",  # Placeholder
            gates_evaluated=gate_results.get("gates_evaluated", []),
            gates_passed=gates_passed,
            execution_payload_created=execution_payload_created,
            human_approval_required=not execution_payload_created or mode == "dry_run",
            notes=notes,
            previous_record_hash=previous_record_hash or "sha256:genesis",
            record_hash="",  # Will be computed below
            signature_scheme="ed25519-sha256-local-jsonl-v1",
            signature="",  # Will be computed below
        )

        # Compute record hash (hash of everything except signature)
        receipt_dict = asdict(receipt)
        receipt_dict["signature"] = ""
        receipt_json = json.dumps(receipt_dict, sort_keys=True, separators=(",", ":"))
        receipt.record_hash = self._sha256(receipt_json)

        # Sign the record
        receipt.signature = self._sign(receipt.record_hash)

        return receipt

    def write_receipt(self, receipt: Receipt) -> bool:
        """
        Append receipt to JSONL file (one JSON object per line).

        Returns:
            True if written successfully, False otherwise.
        """
        if self.receipts_path is None:
            return False

        try:
            self.receipts_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.receipts_path, "a") as f:
                f.write(json.dumps(asdict(receipt), separators=(",", ":")) + "\n")

            return True
        except IOError as e:
            print(f"Failed to write receipt: {e}")
            return False

    def read_receipts(self, limit: int = None) -> list:
        """
        Read all receipts from JSONL file.

        Args:
            limit: max number of receipts to read (most recent first)

        Returns:
            List of receipt dicts
        """
        if self.receipts_path is None or not self.receipts_path.exists():
            return []

        receipts = []
        try:
            with open(self.receipts_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        receipts.append(json.loads(line))
        except IOError:
            pass

        # Return in reverse order (most recent first)
        receipts.reverse()

        if limit:
            return receipts[:limit]

        return receipts

    def verify_receipt(self, receipt_dict: Dict[str, Any]) -> bool:
        """
        Verify receipt signature and chain integrity.

        Phase 1: basic verification only.
        Production: full ed25519 verification.
        """
        if "signature" not in receipt_dict:
            return False

        # Extract signature and blank it
        stored_signature = receipt_dict["signature"]
        receipt_dict["signature"] = ""

        # Recompute hash
        receipt_json = json.dumps(receipt_dict, sort_keys=True, separators=(",", ":"))
        expected_hash = self._sha256(receipt_json)

        # Verify signature
        receipt_dict["signature"] = stored_signature
        expected_sig = self._sign(expected_hash)

        return stored_signature == expected_sig
