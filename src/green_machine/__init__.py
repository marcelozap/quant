"""
Green Machine Orchestration Engine for XIV World

A local-first research and risk-review laboratory.
Processes intents -> evaluates gates -> writes receipts.
Never executes. Only proposes and logs.

All data is local. All logic is transparent.
"""

__version__ = "0.1.0"
__author__ = "Green Machine Team"

from .gates import GateEvaluator
from .receipts import ReceiptWriter
from .orchestrator import StateGraphRunner
from .rosco import RoscoResponder
from .intent_handler import IntentHandler

__all__ = [
    "GateEvaluator",
    "ReceiptWriter",
    "StateGraphRunner",
    "RoscoResponder",
    "IntentHandler",
]
