# Team Assignment Pitch

## Proposed assignment

Build a small Databricks lakehouse MVP called `Store Pulse` that combines store
sales, inventory, deliveries, promotions, waste, and labor data into a few
operational gold tables.

## Simple goal

Create one reusable retail operations signal layer that helps answer:

- what needs replenishment attention now
- which promotions are truly driving lift
- where fresh categories may be at risk

## Why this is a good assignment

- practical and relevant to store operations
- small enough for an MVP
- demonstrates lakehouse architecture, not just analysis
- produces outputs that can feed a dashboard or alerting workflow
- easy to extend later with real feeds and business rules

## Suggested MVP scope

### Inputs

- POS transactions
- inventory snapshots
- deliveries
- promotions
- waste events
- labor schedule

### Outputs

- `gold_replenishment_priority`
- `gold_promo_review`
- `gold_fresh_risk`

## Suggested delivery plan

### Phase 1

- land sample or limited raw data into bronze
- define silver standardization
- build first gold tables

### Phase 2

- validate thresholds with business users
- add dashboard or Databricks SQL views
- add monitoring for data freshness and quality

## 60-second pitch

"I’d like to build a small Databricks lakehouse MVP for retail operations. The
idea is to unify sales, inventory, deliveries, promotions, and waste into a
few gold tables that can help us prioritize replenishment, review promo
performance, and flag fresh-risk items earlier. It is a useful operational use
case, but it also gives us a repeatable medallion-pattern project that can be
expanded with real store logic over time."

## What to emphasize

- operational usefulness
- reusable data model
- modest MVP scope
- dashboard-ready outputs

## What not to emphasize

- fancy modeling
- huge platform redesign
- anything that sounds too academic or experimental
