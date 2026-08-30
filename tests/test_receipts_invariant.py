"""Tests for the two receipt invariants in GREEN_MACHINE_DATA_CONTRACT.md.

Section 3 states both:

    If `gates_passed` is false, `execution_payload_created` must be false.

    A dry-run may create an in-memory receipt preview, but it must not append
    to the signed ledger.

The second one is the bug XIV already hit and fixed once (commit 7e1b10c in the
XIV repo): a rehearsal that mutates the record of truth is not a rehearsal.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from green_machine.gates import REQUIRED_GATES  # noqa: E402
from green_machine.receipts import ReceiptWriter  # noqa: E402


def _gate_result(passed: bool) -> dict:
    return {
        "gates_evaluated": [
            {
                "gate_id": gate_id,
                "status": "passed" if passed else "failed",
                "threshold": "x",
                "observed": "y",
            }
            for gate_id in sorted(REQUIRED_GATES)
        ],
        "gates_passed": passed,
    }


def _writer(tmp_path: Path) -> ReceiptWriter:
    return ReceiptWriter(receipts_path=str(tmp_path / "receipts.jsonl"))


# --------------------------------------------------- the fail-closed invariant


@pytest.mark.parametrize("passed", [True, False])
def test_payload_follows_gates(tmp_path, passed):
    receipt = _writer(tmp_path).create_receipt("risk_wall", "gm.test", _gate_result(passed), mode="live")
    assert receipt.gates_passed is passed
    assert receipt.execution_payload_created is passed


def test_failed_gates_never_create_a_payload(tmp_path):
    """The one critical rule, stated directly."""
    receipt = _writer(tmp_path).create_receipt("risk_wall", "gm.test", _gate_result(False), mode="live")
    assert receipt.execution_payload_created is False


def test_missing_gates_passed_key_defaults_to_blocked(tmp_path):
    """An absent verdict is not a pass."""
    receipt = _writer(tmp_path).create_receipt("risk_wall", "gm.test", {"gates_evaluated": []}, mode="live")
    assert receipt.gates_passed is False
    assert receipt.execution_payload_created is False


@pytest.mark.parametrize("truthy", ["true", 1, "yes", [1]])
def test_truthy_non_true_values_do_not_create_a_payload(tmp_path, truthy):
    """Only real True counts. A truthy string must not open the gate."""
    receipt = _writer(tmp_path).create_receipt("risk_wall", "gm.test", {"gates_passed": truthy}, mode="live")
    assert receipt.execution_payload_created is False


# ------------------------------------------------------- the dry-run invariant


def test_dry_run_receipt_is_not_appended(tmp_path):
    """Contract section 3: a dry-run preview never touches the signed ledger."""
    ledger = tmp_path / "receipts.jsonl"
    writer = ReceiptWriter(receipts_path=str(ledger))

    receipt = writer.create_receipt("risk_wall", "gm.test", _gate_result(True), mode="dry_run")
    written = writer.write_receipt(receipt)

    assert written is False, "dry-run receipts must be refused"
    assert not ledger.exists(), "dry-run must not create the ledger"


def test_dry_run_leaves_an_existing_ledger_byte_identical(tmp_path):
    ledger = tmp_path / "receipts.jsonl"
    writer = ReceiptWriter(receipts_path=str(ledger))

    writer.write_receipt(writer.create_receipt("risk_wall", "gm.test", _gate_result(True), mode="live"))
    before = ledger.read_bytes()

    writer.write_receipt(writer.create_receipt("risk_wall", "gm.test", _gate_result(True), mode="dry_run"))

    assert ledger.read_bytes() == before


def test_live_receipt_is_appended_as_one_json_line(tmp_path):
    ledger = tmp_path / "receipts.jsonl"
    writer = ReceiptWriter(receipts_path=str(ledger))

    assert writer.write_receipt(writer.create_receipt("risk_wall", "gm.test", _gate_result(True), mode="live")) is True

    lines = [line for line in ledger.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["gates_passed"] is True
    assert record["execution_payload_created"] is True
