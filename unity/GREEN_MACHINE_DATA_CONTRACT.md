# Green Machine Data Contract for XIV World

**Status:** canonical interface draft for Unity and Green Machine integration.
**Repo:** `quant`
**Unity project:** `unity/`
**Last updated:** 2026-08-30

This document is the shared contract between the XIV Unity world and the Green
Machine local research tools. It exists so Unity, Codex, Claude, and future
manual work can build against the same interface without drifting.

The rule is simple:

> Unity is the cockpit. Green Machine produces research evidence. XIV gates and
> receipts are the truth boundary. The game can display and propose review
> intents, but it cannot execute trades, commits, deployments, payments, or
> destructive file actions.

## 1. Ownership

| Surface | Owner | May write | May read |
|---|---|---|---|
| Unity world | Unity scripts | `unity/LocalState/xiv_intents.jsonl`, Unity saves | exported state, evidence cards, receipts, Rosco lines |
| Green Machine tools | `src/quant_live/` | evidence cards, review artifacts | gate config, local data, intents |
| XIV orchestration | local runner / Codex workflow | signed receipts, exported world state | intents, evidence cards, gate config |
| Player | local human | config and approval decisions | everything local |

Unity never writes signed receipts. Green Machine never writes Unity scenes.
XIV/runner code is the only writer for signed receipt records.

## 2. File Layout

Runtime files live outside tracked source:

```text
unity/LocalState/
  receipts.jsonl
  xiv_intents.jsonl
  xiv_state.json
  green_machine_gate_config.json
  evidence_cards/
  rosco_lines.local.json
```

Tracked examples live in the repo:

```text
unity/Examples/
  receipts.example.jsonl
  xiv_intents.example.jsonl
  xiv_state.example.json
  green_machine_gate_config.example.json
  evidence_cards/
  rosco_lines.example.json
```

`unity/LocalState/` is ignored by Git. It may contain local market/account
summaries, personal notes, and signed receipts. Do not commit it.

## 3. Receipt JSONL

Receipts are append-only JSONL. Each line is one complete JSON object.

Canonical local path:

```text
unity/LocalState/receipts.jsonl
```

Tracked example path:

```text
unity/Examples/receipts.example.jsonl
```

Required fields:

```json
{
  "schema_version": "xiv.receipt.v1",
  "receipt_id": "2026-08-30T14-05-22Z_green_machine_risk_wall_001",
  "timestamp_utc": "2026-08-30T14:05:22Z",
  "source": "green_machine",
  "world_zone": "risk_wall",
  "task_id": "green_machine.risk_review.sample_001",
  "mode": "dry_run",
  "decision": "blocked",
  "outcome": "failed_gate",
  "evidence_hash": "sha256:3b7b3d68e6d8b4e1a3ce6ad0b1a4dfcfbe7d5a798d5e64d647f79f82e4f8f831",
  "state_before_hash": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
  "state_after_hash": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
  "gates_evaluated": [
    {
      "gate_id": "stale_data",
      "status": "passed",
      "threshold": "max_age_seconds=300",
      "observed": "age_seconds=42"
    },
    {
      "gate_id": "abnormal_spread",
      "status": "failed",
      "threshold": "max_spread_bps=50",
      "observed": "spread_bps=118"
    }
  ],
  "gates_passed": false,
  "execution_payload_created": false,
  "human_approval_required": true,
  "notes": "Review blocked because abnormal spread exceeded threshold.",
  "previous_record_hash": "sha256:GENESIS",
  "record_hash": "sha256:2d0c5c0a4f2e4d8f7f6c5a0c44e4a9d7f2a221ed7ea9dc8b2e0f23b0e43c5421",
  "signature_scheme": "ed25519-sha256-local-jsonl-v1",
  "signature": "base64:example-signature"
}
```

Receipt invariants:

- If `gates_passed` is `false`, `execution_payload_created` must be `false`.
- If the ledger cannot be parsed or verified, Unity displays `UNKNOWN`.
- Receipts are evidence of review, not performance claims.
- A dry-run may create an in-memory receipt preview, but it must not append to
  the signed ledger unless a future explicit "dry-run receipt persistence" mode
  is designed and approved.

## 4. Green Machine StateGraph

XIV owns the StateGraph vocabulary. Green Machine is one subgraph inside XIV.

Canonical Green Machine phases:

```text
local_data_ingestion
  -> evidence_normalization
  -> assumption_cards
  -> risk_gate_evaluation
  -> paper_review_decision
  -> receipt_write
  -> archive_update
  -> unity_state_export
```

Unity renders these phases as:

```text
Green Gate
  -> Evidence Trail
  -> Risk Wall
  -> Receipt Ledger
  -> Archive Garden
```

There is no Unity-facing `execution` phase. Use `paper_review_decision`.

## 5. Gate Config

Gates are configurable, versioned, local, and fail-closed.

Canonical local path:

```text
unity/LocalState/green_machine_gate_config.json
```

Tracked example path:

```text
unity/Examples/green_machine_gate_config.example.json
```

Default config:

```json
{
  "schema_version": "xiv.green_machine.gates.v1",
  "updated_by": "local_user",
  "updated_at_utc": "2026-08-30T14:00:00Z",
  "gates": {
    "stale_data": {
      "enabled": true,
      "max_age_seconds": 300,
      "severity": "hard_block"
    },
    "abnormal_spread": {
      "enabled": true,
      "max_spread_bps": 50,
      "severity": "hard_block"
    },
    "concentration_limit": {
      "enabled": true,
      "max_single_name_percent": 10,
      "severity": "hard_block"
    },
    "drawdown_guard": {
      "enabled": true,
      "max_drawdown_percent": 5,
      "severity": "hard_block"
    },
    "behavioral_gate": {
      "enabled": true,
      "requires_manual_clear": true,
      "severity": "hard_block"
    }
  }
}
```

Gate rules:

- Missing config means all gates display `UNKNOWN`.
- Invalid config means all gates fail closed.
- Threshold changes require a signed receipt once the receipt writer exists.
- Unity may display thresholds, but may not change thresholds in runtime play.

## 6. Evidence Cards

Evidence cards are local JSON files written by Green Machine tooling and read by
Unity and XIV.

Canonical local folder:

```text
unity/LocalState/evidence_cards/
```

Tracked example folder:

```text
unity/Examples/evidence_cards/
```

Card schema:

```json
{
  "schema_version": "xiv.evidence_card.v1",
  "card_id": "gm_spy_replay_2026_08_30_001",
  "created_at_utc": "2026-08-30T14:10:00Z",
  "source": "green_machine",
  "ticker": "SPY",
  "timeframe": "intraday",
  "claim_type": "research_observation",
  "claim": "Momentum expanded after the opening range.",
  "assumptions": [
    "Replay data is complete for the tested window.",
    "Spread data is representative of executable conditions."
  ],
  "data_inputs": [
    {
      "name": "ohlcv_bars",
      "path": "local-only/redacted-or-relative-path.csv",
      "hash": "sha256:example"
    }
  ],
  "known_missing_data": [
    "No live broker confirmation.",
    "No audited slippage record."
  ],
  "confidence": "limited",
  "status": "research_only",
  "allowed_world_use": [
    "display",
    "risk_review",
    "archive"
  ],
  "forbidden_world_use": [
    "investment_advice",
    "live_trade_alert",
    "order_generation"
  ]
}
```

Missing evidence is `UNKNOWN`, not `0`, not blank, and not guessed.

## 7. Rosco Lines

Rosco is data-driven. He is a grounding companion, not a market agent.

Tracked example:

```text
unity/Examples/rosco_lines.example.json
```

Local override:

```text
unity/LocalState/rosco_lines.local.json
```

Schema:

```json
{
  "schema_version": "xiv.rosco_lines.v1",
  "lines": [
    {
      "line_id": "risk_wall_failed_gate_001",
      "zone": "risk_wall",
      "trigger": "failed_gate",
      "text": "Let's pause here and check the evidence before moving on.",
      "allowed_modes": ["dry_run", "review"],
      "forbidden_topics": ["financial_advice", "live_trade_call"]
    },
    {
      "line_id": "missing_data_unknown_001",
      "zone": "evidence_trail",
      "trigger": "missing_data",
      "text": "This part is unknown. We can keep walking, but we should not pretend it is proven.",
      "allowed_modes": ["review"],
      "forbidden_topics": ["prediction", "recommendation"]
    }
  ]
}
```

Rosco line rules:

- No ticker-specific advice.
- No buy, sell, hold, target, account size, or live call language.
- Route the player to evidence, receipts, or pause.
- Keep lines warm, short, and human.

## 8. Intent Queue

Unity writes intents. XIV reads them. Intents are requests for review, not
commands to execute.

Canonical local path:

```text
unity/LocalState/xiv_intents.jsonl
```

Tracked example path:

```text
unity/Examples/xiv_intents.example.jsonl
```

Intent schema:

```json
{
  "schema_version": "xiv.intent.v1",
  "intent_id": "2026-08-30T14-20-00Z_green_gate_daily_snapshot",
  "created_at_utc": "2026-08-30T14:20:00Z",
  "created_by": "unity_player",
  "source_zone": "green_gate",
  "requested_action": "run_daily_snapshot_review",
  "mode": "dry_run_requested",
  "parameters": {
    "ticker": "SPY",
    "timeframe": "intraday"
  },
  "forbidden_actions": [
    "broker_order",
    "deployment",
    "payment",
    "file_delete",
    "git_push"
  ]
}
```

Dry-run protocol:

```text
Unity interaction
  -> append intent
  -> XIV runner reads intent
  -> XIV runs dry-run
  -> Unity displays preview
  -> human approval happens outside Unity runtime
  -> XIV runs allowed local action
  -> XIV writes signed receipt
  -> Unity reloads exported state
```

Approval is manual for now. Unity may show `Paper Review Ready`. Unity may not
show `Proceed`.

## 9. Unity Export State

Unity should prefer a compact exported state file instead of parsing every raw
artifact directly.

Canonical local path:

```text
unity/LocalState/xiv_state.json
```

Tracked example path:

```text
unity/Examples/xiv_state.example.json
```

Example:

```json
{
  "schema_version": "xiv.world_state.v1",
  "generated_at_utc": "2026-08-30T14:30:00Z",
  "chain_status": "CHAIN OK",
  "zones": {
    "green_gate": {
      "status": "ready",
      "headline": "Daily snapshot available",
      "last_receipt_id": "2026-08-30T14-05-22Z_green_machine_risk_wall_001"
    },
    "evidence_trail": {
      "status": "unknown",
      "headline": "No evidence card loaded",
      "last_receipt_id": null
    },
    "risk_wall": {
      "status": "blocked",
      "headline": "Abnormal spread gate failed",
      "last_receipt_id": "2026-08-30T14-05-22Z_green_machine_risk_wall_001"
    },
    "receipt_ledger": {
      "status": "ready",
      "headline": "Signed receipt chain verified",
      "last_receipt_id": "2026-08-30T14-05-22Z_green_machine_risk_wall_001"
    },
    "archive_garden": {
      "status": "ready",
      "headline": "One review archived",
      "last_receipt_id": null
    }
  }
}
```

`chain_status` values:

- `CHAIN OK`
- `UNKNOWN`
- `CHAIN FAILED`

If `chain_status` is not `CHAIN OK`, Risk Wall and Receipt Ledger must render as
blocked or unknown.

## 10. Safety Language

Use these Unity-facing names:

| Unsafe | Safe |
|---|---|
| Execution Agent | Simulation Recorder |
| Trading Signal | Research Card |
| Auto Execution | Auto Review |
| Proceed | Paper Review Ready |
| Target Price | Scenario Level |
| P&L | Simulated Outcome / Replay Outcome |
| Buy / Sell | Scenario A / Scenario B |
| Trade Alert | Review Prompt |

Standing sign:

```text
GREEN MACHINE - RESEARCH AND REVIEW
This is a review lab. Nothing here places an order.
No advice. No recommendations. No live calls.
```

Failed gate sign:

```text
GATE BARRED - NO EXECUTION PAYLOAD
This is a review stop, not a signal.
```

## 11. Open Items

These are intentionally not solved in code yet:

- Whether receipts are generated by existing `src/quant_live/` code or a small
  XIV bridge module.
- Whether Unity gets a local file watcher or reloads state on interaction.
- How body-state input is captured. Until there is a local source, it remains
  manual and fail-closed.
- Whether `unity/LocalState/receipts.jsonl` mirrors or replaces any existing
  Green Machine receipt location. Do not create a second active ledger without a
  migration note.
