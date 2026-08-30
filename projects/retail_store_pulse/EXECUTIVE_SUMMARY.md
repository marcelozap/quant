# Executive Summary

## Project

`Store Pulse`: A Databricks retail lakehouse MVP for replenishment, promo, and
fresh-risk visibility.

## Why this matters

Retail teams often have the data they need, but not in one operational view.
Sales, inventory, deliveries, labor, and promotions sit across different
systems and timelines. That makes it harder to answer simple questions quickly:

- What is at risk of stocking out?
- Which promos are actually moving units?
- Where should a manager or replenishment analyst focus first?

## Proposed solution

Build a small Databricks medallion pipeline that lands raw operational data in
bronze, standardizes it in silver, and publishes a few high-signal gold tables
for reporting and alerts.

## Initial outputs

### 1. Replenishment Priority

Rank store-item pairs based on:

- on-hand units
- recent demand velocity
- promo intensity
- category perishability
- delivery recency

### 2. Promo Review

Compare promo periods versus recent baseline demand to identify:

- strong lift
- weak lift
- possible execution gaps

### 3. Fresh Risk

Surface perishables with combinations of:

- elevated waste
- low hours of supply
- recent demand spikes

## Databricks fit

This is a good Databricks assignment because it uses:

- lakehouse medallion structure
- batch or streaming-friendly raw ingestion
- SQL and PySpark-friendly transformations
- dashboard-ready gold tables
- governance and observability patterns the team can extend

## MVP scope

The first version can be kept small:

- 3 stores
- 15 to 25 items
- 2 weeks of synthetic or sampled data
- 3 gold tables
- one simple dashboard or SQL query set

## Value to the team

- practical retail use case
- reusable pipeline pattern
- faster operational decision support
- clear next steps for scaling to real store and item volumes
