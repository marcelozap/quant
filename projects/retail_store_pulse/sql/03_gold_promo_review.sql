-- Databricks SQL sketch
-- Compare promo demand to recent non-promo baseline.

create or replace table analytics.gold_promo_review as
with promo_hours as (
  select
    store_id,
    item_id,
    category,
    avg(units_sold) as promo_avg_units_per_hour,
    avg(net_sales) as promo_avg_sales_per_hour
  from analytics.silver_store_item_hourly_sales
  where promo_flag = 1
  group by store_id, item_id, category
),
baseline_hours as (
  select
    store_id,
    item_id,
    category,
    avg(units_sold) as baseline_avg_units_per_hour,
    avg(net_sales) as baseline_avg_sales_per_hour
  from analytics.silver_store_item_hourly_sales
  where promo_flag = 0
  group by store_id, item_id, category
)
select
  p.store_id,
  p.item_id,
  p.category,
  p.promo_avg_units_per_hour,
  b.baseline_avg_units_per_hour,
  case
    when b.baseline_avg_units_per_hour > 0 then
      p.promo_avg_units_per_hour / b.baseline_avg_units_per_hour
    else null
  end as unit_lift_ratio,
  p.promo_avg_sales_per_hour,
  b.baseline_avg_sales_per_hour
from promo_hours p
left join baseline_hours b
  on p.store_id = b.store_id and p.item_id = b.item_id;
