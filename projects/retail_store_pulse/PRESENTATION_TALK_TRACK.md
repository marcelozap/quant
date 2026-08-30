# Presentation Talk Track

## 30-second intro

"I put together a small Databricks lakehouse MVP for store operations. The
idea is to unify sales, inventory, deliveries, promotions, and waste into a
few gold tables that help answer: what needs attention now, what promos are
working, and where fresh categories may be at risk."

## Business pain point

"A lot of operational questions are simple to ask but slow to answer because
the data sits in different systems and at different grains. This project tries
to bring those signals together in one place."

## Architecture

"I used a bronze/silver/gold pattern. Bronze is raw landed data. Silver is
cleaned and standardized store-item events. Gold is a few operational marts
that a store, replenishment, or analytics team could actually use."

## Gold outputs

### Replenishment Priority

"This ranks store-item combinations by urgency using on-hand, recent velocity,
promo context, perishability, and delivery timing."

### Promo Review

"This compares promo demand to baseline demand so we can quickly see where lift
looks strong, weak, or operationally inconsistent."

### Fresh Risk

"This combines waste and demand context to show where perishable items may need
attention before they become shrink."

## Why it is a good team assignment

"It is small enough to build quickly, but the pattern is reusable. It touches
ingestion, modeling, analytics, and dashboard outputs, so it is a practical
lakehouse assignment rather than just a slide idea."

## Good closing line

"The first version is intentionally simple. The goal is to create a clean,
extendable operations signal layer in Databricks that the team can expand with
real store data and business rules."
