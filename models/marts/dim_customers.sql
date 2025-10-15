{{ config(materialized='table') }}

with latest as (
  select
    customer_id,
    first_name,
    last_name,
    email,
    region,
    signup_date,
    ingestion_ts,
    row_number() over (partition by customer_id order by coalesce(signup_date, ingestion_ts) desc) as rn
  from {{ ref('stg_customers') }}
  where customer_id is not null
)

select
  customer_id,
  md5(customer_id::text) as customer_sk,
  first_name,
  last_name,
  email,
  region,
  signup_date,
  ingestion_ts as loaded_at
from latest
where rn = 1
