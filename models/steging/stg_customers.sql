{{ config(materialized='view') }}

with src as (
  select * from {{ source('raw', 'customers') }}
)

select
  case 
    when trim(customer_id::text) ~ '^[0-9]+$' then trim(customer_id::text)::bigint
    else null 
  end as customer_id,

  trim(name) as full_name,

  split_part(trim(name), ' ', 1) as first_name,

  case 
    when position(' ' in trim(name)) > 0 
    then substr(trim(name), position(' ' in trim(name)) + 1) 
    else null 
  end as last_name,

  lower(nullif(trim(email), '')) as email,

  nullif(trim(region), '') as region,

  case
    when trim(signup_date::text) ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}' 
    then trim(signup_date::text)::date
    else null
end as signup_date,

  now() at time zone 'utc' as ingestion_ts

from src

