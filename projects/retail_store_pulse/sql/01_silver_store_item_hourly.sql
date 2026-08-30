-- Databricks SQL sketch
-- Build an hourly store-item sales aggregate from silver transactions.

create or replace table analytics.silver_store_item_hourly_sales as
select
  store_id,
  item_id,
  category,
  date_trunc('hour', event_ts) as hour_ts,
  sum(quantity) as units_sold,
  sum(net_sales) as net_sales,
  max(case when promo_flag then 1 else 0 end) as promo_flag
from analytics.silver_pos_transactions
group by
  store_id,
  item_id,
  category,
  date_trunc('hour', event_ts);
