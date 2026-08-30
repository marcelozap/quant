# Green Machine Gate Evaluation Spec

**Status:** implementation spec for local research and risk-review gates.
**Repo:** `quant`
**Last updated:** 2026-08-30

Green Machine gates are review gates, not trading instructions. They determine
whether a research card can be marked `Paper Review Ready` inside XIV World.
They do not produce live trade alerts, broker orders, copy-trading messages, or
investment advice.

## Canonical Gate Sequence

```text
stale_data
  -> abnormal_spread
  -> concentration_limit
  -> drawdown_guard
  -> behavioral_gate
  -> paper_review_decision
```

All enabled gates must pass before `paper_review_decision` can be ready. Any
missing input, invalid input, or unreadable config produces `UNKNOWN` or
`blocked`, never an allow decision.

## Gate Defaults

| Gate | Default threshold | Unit | Failure result |
|---|---:|---|---|
| `stale_data` | 300 | seconds | `blocked` |
| `abnormal_spread` | 50 | basis points | `blocked` |
| `concentration_limit` | 10 | percent of portfolio | `blocked` |
| `drawdown_guard` | 5 | percent drawdown from local high-water mark | `blocked` |
| `behavioral_gate` | manual clear required | boolean | `blocked` |

Thresholds are loaded from
`unity/LocalState/green_machine_gate_config.json`. If that file is absent,
Unity displays `UNKNOWN` and the evaluator fails closed.

## Inputs

Required fields by gate:

| Gate | Required inputs |
|---|---|
| `stale_data` | `snapshot_timestamp_utc`, `evaluation_timestamp_utc` |
| `abnormal_spread` | `bid`, `ask`, optional `reference_price` |
| `concentration_limit` | `symbol_exposure_percent` |
| `drawdown_guard` | `current_equity`, `high_water_equity` |
| `behavioral_gate` | `manual_clear`, optional `notes` |

Missing required input means the gate status is `unknown` and the final decision
is `blocked`.

## Output

Gate evaluation output:

```json
{
  "schema_version": "xiv.green_machine.gate_result.v1",
  "evaluated_at_utc": "2026-08-30T14:40:00Z",
  "research_card_id": "gm_spy_replay_2026_08_30_001",
  "decision": "blocked",
  "paper_review_ready": false,
  "execution_payload_created": false,
  "gates": [
    {
      "gate_id": "stale_data",
      "status": "passed",
      "threshold": {
        "max_age_seconds": 300
      },
      "observed": {
        "age_seconds": 42
      },
      "message": "Snapshot is fresh enough for review."
    },
    {
      "gate_id": "abnormal_spread",
      "status": "failed",
      "threshold": {
        "max_spread_bps": 50
      },
      "observed": {
        "spread_bps": 118
      },
      "message": "Spread is outside the review band."
    }
  ]
}
```

Allowed `status` values:

- `passed`
- `failed`
- `unknown`

Allowed `decision` values:

- `paper_review_ready`
- `blocked`
- `unknown`

Invariant:

```text
decision != paper_review_ready  =>  execution_payload_created == false
```

For Unity, prefer `paper_review_ready` over any wording like `proceed`.

## Gate Math

### Stale Data

```text
age_seconds = evaluation_timestamp_utc - snapshot_timestamp_utc
passed = age_seconds <= max_age_seconds
```

If either timestamp is missing or unparsable, status is `unknown`.

### Abnormal Spread

```text
mid = (bid + ask) / 2
spread_bps = ((ask - bid) / mid) * 10000
passed = spread_bps <= max_spread_bps
```

If `bid <= 0`, `ask <= 0`, or `ask < bid`, status is `unknown`.

### Concentration Limit

```text
passed = symbol_exposure_percent <= max_single_name_percent
```

If exposure cannot be calculated locally, status is `unknown`.

### Drawdown Guard

```text
drawdown_percent = ((high_water_equity - current_equity) / high_water_equity) * 100
passed = drawdown_percent <= max_drawdown_percent
```

If `high_water_equity <= 0`, status is `unknown`.

### Behavioral Gate

```text
passed = manual_clear == true
```

This gate intentionally starts manual. It should not read health, sleep, or mood
data until a local-only source is explicitly designed.

## Unity Rendering

Gate states map to Risk Wall visuals:

| Gate status | Visual |
|---|---|
| `passed` | lit, open |
| `failed` | barred, warm red/orange, reason visible |
| `unknown` | grey, unlit, label reads `UNKNOWN` |

No gate should render a profit/loss state. The wall is about review quality, not
performance.

## Forbidden Outputs

The evaluator must not output:

- broker orders
- buy/sell recommendations
- position sizes
- target prices
- live trade alerts
- guaranteed outcomes
- copy-trading instructions

The evaluator may output:

- research card status
- missing evidence
- gate pass/fail/unknown
- paper-review readiness
- receipt fields
- archive-ready summaries
