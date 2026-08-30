-- Databricks SQL sketch
-- Join hourly sales, latest inventory, and delivery context into a
-- replenishment priority mart.

create or replace table analytics.gold_replenishment_priority as
with velocity as (
  select
    store_id,
    item_id,
    category,
    sum(units_sold) / 6.0 as avg_units_per_hour_6h,
    max(promo_flag) as promo_flag
  from analytics.silver_store_item_hourly_sales
  where hour_ts >= current_timestamp() - interval 6 hours
  group by store_id, item_id, category
),
latest_inventory as (
  select
    store_id,
    item_id,
    category,
    on_hand_units,
    snapshot_ts
  from analytics.silver_inventory_latest
),
latest_delivery as (
  select
    store_id,
    item_id,
    max(delivery_ts) as last_delivery_ts
  from analytics.silver_delivery_events
  group by store_id, item_id
)
select
  v.store_id,
  v.item_id,
  v.category,
  i.on_hand_units,
  v.avg_units_per_hour_6h,
  case
    when v.avg_units_per_hour_6h > 0 then i.on_hand_units / v.avg_units_per_hour_6h
    else null
  end as hours_of_supply,
  v.promo_flag,
  d.last_delivery_ts
from velocity v
left join latest_inventory i
  on v.store_id = i.store_id and v.item_id = i.item_id
left join latest_delivery d
  on v.store_id = d.store_id and v.item_id = d.item_id;
