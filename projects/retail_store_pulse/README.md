# Retail Store Pulse

A Publix-style Databricks lakehouse project you can present as a practical
operations assignment.

This project is framed around a retail problem, not finance:

- reduce out-of-stocks on fast movers
- surface replenishment urgency earlier
- review promo performance faster
- identify fresh/shrink risk before it becomes waste

It also quietly builds the same transferable skills that matter later in more
quantitative paths:

- time-series aggregation
- event-driven data modeling
- anomaly and risk scoring
- dashboard-ready gold tables
- operational SLAs and data freshness thinking

## Assignment pitch

`Store Pulse` is a lightweight lakehouse MVP that combines POS, inventory,
delivery, labor, promo, and weather data into a single set of retail
operations signals.

The core output is a near-real-time replenishment and execution dashboard for
store managers, replenishment teams, and department leads.

## What you can tell your team

"I want to build a Databricks lakehouse MVP that unifies store sales,
inventory, deliveries, and promotions into a small set of operational gold
tables. The goal is to flag fast-moving items that are at risk of stocking
out, show where promotions are outperforming or underperforming baseline, and
create a repeatable medallion-pattern pipeline the team can extend."

## Business question

Can we use the datalake and Databricks to create a single operational view of:

- which store-item combinations need replenishment attention now
- where promo lift is real versus noise
- which fresh categories are at risk of waste or missed replenishment

## Data model

### Bronze

Raw landed files or streams:

- `bronze_pos_transactions`
- `bronze_inventory_snapshots`
- `bronze_deliveries`
- `bronze_labor_schedule`
- `bronze_promotions`
- `bronze_weather_daily`
- `bronze_waste_events`

### Silver

Cleaned and standardized:

- `silver_pos_transactions`
- `silver_inventory_latest`
- `silver_delivery_events`
- `silver_promo_calendar`
- `silver_store_item_hourly_sales`
- `silver_store_department_labor`
- `silver_weather_daily`
- `silver_waste_daily`

### Gold

Business-facing marts:

- `gold_store_item_hourly`
- `gold_replenishment_priority`
- `gold_promo_review`
- `gold_fresh_risk`

## Folder layout

```text
projects/retail_store_pulse/
  README.md
  EXECUTIVE_SUMMARY.md
  PRESENTATION_TALK_TRACK.md
  ARCHITECTURE.md
  sql/
    01_silver_store_item_hourly.sql
    02_gold_replenishment_priority.sql
    03_gold_promo_review.sql
  scripts/
    generate_sample_data.py
    build_store_pulse_mart.py
  data/
    raw/
    gold/
```

## Demo flow

1. Generate sample retail data.
2. Build gold outputs from the synthetic raw layer.
3. Review the replenishment, promo, and fresh-risk tables.
4. Present the architecture and business use case.

## Run locally

```bash
cd /Users/a14/Documents/quant
python3 projects/retail_store_pulse/scripts/generate_sample_data.py
python3 projects/retail_store_pulse/scripts/build_store_pulse_mart.py
```

## Recommended presentation angle

Keep the story operational:

- "This helps the store react earlier."
- "This makes data more usable for replenishment and promo review."
- "This gives the team a reusable medallion pattern in Databricks."

Do not oversell fancy modeling. The strongest version is:

"Small, useful, extendable."
