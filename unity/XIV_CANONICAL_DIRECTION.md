# XIV World / Green Machine — Canonical Direction

**Status:** canonical. This document wins over any other plan in this repo.
**Purpose:** stop overbuilding. Everything not described here is a path, not the thing.
**Last updated:** 2026-08-30

---

## The whole thing

**Green Machine is an agent.**

It runs nightly, pulls market data through approved local/MCP connectors, scores
new market conditions against my prior calls, and writes one canonical local
state file.

**XIV World is an isometric skyline.**

It does not trade. It does not call brokers. It does not run market logic. It
reads only the Green Machine state file and renders the state of the world.

Buildings wear, crack, brighten, recover, or evolve based on how prior conviction
played out against later evidence.

One in-world agent can take my new read, structure it, and write it back as a
pending review/intention. Green Machine processes that later through the nightly
agent loop.

**MaloSound plays underneath** as the emotional/audio layer.

That is the whole thing. Everything else is paths.

---

## Hard architecture

```text
MCP / local market connectors
        |
        v
Green Machine nightly agent
        |
        v
prior calls + current data + scoring logic
        |
        v
one canonical state file
        |
        v
XIV World isometric skyline
        |
        v
visual wear / cracks / light / recovery / agent movement
        |
        v
player writes a new read through one safe in-world agent
        |
        v
pending local read file
        |
        v
next Green Machine nightly run
```

---

## Ownership

**Green Machine owns:**

- market data pull
- prior-call scoring
- conviction review
- nightly agent loop
- canonical state file

**XIV World owns:**

- isometric skyline
- visual state
- buildings
- wear/crack/repair language
- one safe read-capture agent
- local-only display

**MaloSound owns:**

- audio atmosphere
- movement/music layer
- emotional state underneath the world

---

## Green Machine output

One file:

```text
green_machine_state.json
```

Minimum shape:

```json
{
  "schema_version": "green_machine.state.v1",
  "generated_at": "2026-08-30T22:00:00Z",
  "mode": "nightly_review",
  "market_weather": "risk_off",
  "overall_score": 62,
  "reads": [
    {
      "read_id": "2026-08-29_spy_range_expansion",
      "ticker": "SPY",
      "original_read": "Opening range expansion likely matters more than headline noise.",
      "conviction": "medium",
      "status": "aging",
      "score": 71,
      "evidence": {
        "price_followthrough": "confirmed",
        "volume_context": "mixed",
        "data_quality": "partial"
      },
      "world_effect": {
        "district": "green_gate",
        "building_state": "weathered_but_lit",
        "crack_level": 2,
        "light_level": 0.7
      }
    }
  ],
  "pending_reviews": [],
  "warnings": [
    "Missing options flow data; marked UNKNOWN."
  ]
}
```

---

## XIV World rules

XIV World:

- reads `green_machine_state.json`
- renders visual consequence
- captures new reads
- writes pending read/intention files

XIV World does **not**:

- trade
- advise
- call brokers
- score markets itself
- fetch market data
- create execution payloads
- overexplain the system in UI

---

## In-world agent

The one agent inside XIV World has one job:

> Take my read, structure it, and save it for Green Machine.

It can ask:

- What ticker or theme is this about?
- What is your read?
- What would prove you wrong?
- What timeframe?
- How strong is your conviction?
- What evidence are you using?

It writes:

```text
pending_reads/*.json
```

Green Machine picks these up on the nightly run.

---

## Visual model

Buildings represent reads. A building can:

- rise
- brighten
- dim
- crack
- weather
- repair
- archive
- become overgrown
- gain scaffolding
- light a window
- shut down a floor

**This is not P&L theater. It is evidence memory.**

---

## One sentence

Green Machine remembers and scores my market reads; XIV World turns that memory
into a living isometric skyline, with MaloSound underneath.

**Shorter:** Green Machine thinks at night. XIV World shows what it learned.
MaloSound makes it feel alive.

---

## Implementation notes

*Not part of the canon above. Reconciliation items for whoever builds next.*

### Two state files are currently specified

| Source | File | Shape |
|---|---|---|
| This document | `green_machine_state.json` | `green_machine.state.v1` — reads, scores, `world_effect` per read |
| `GREEN_MACHINE_DATA_CONTRACT.md` §9 | `unity/LocalState/xiv_state.json` | `xiv.world_state.v1` — per-zone status/headline/last_receipt_id |

These are not the same file and not the same shape. One of them has to be the
canonical state file, because this document says **one**. They are not in
conflict about *meaning* — the zone view is a summary, the reads view is the
substance — so the likely resolution is that `green_machine_state.json` is the
real output and the zone block becomes a section inside it. **Decide before
either is implemented.** Do not build both.

### What this direction does not change

The fail-closed machinery already built and tested still stands, because
"XIV World creates no execution payloads" is the same rule from the other side:

- gates fail closed; a disabled, absent, or unreadable gate never passes
- `gates_passed=false` implies `execution_payload_created=false`
- a dry-run never appends to the signed ledger
- intents are validated against an allowlist, never against their own
  `forbidden_actions` field
- Rosco lines are scanned for advice language before they ship

### What is not built yet

The nightly agent loop, the MCP/local connectors, prior-call scoring, the
skyline, buildings, wear/crack/repair, the in-world read-capture agent, and
`pending_reads/`. None of it exists. This document is direction, not status.
