{{ config(materialized='view') }}

with src as (
  select * from {{ source('raw', 'transactions') }}
),

normalized as (
  select
    -- ✅ transaction_id cleanup
    case 
      when trim(transaction_id::text) ~ '^[0-9]+$' 
      then transaction_id::bigint 
      else null 
    end as transaction_id,

    -- ✅ customer_id cleanup
    case 
      when trim(customer_id::text) ~ '^[0-9]+$' 
      then customer_id::bigint 
      else null 
    end as customer_id,

    -- ✅ amount cleanup + invalid capture
    case 
      when trim(amount::text) ~ '^-?[0-9]+(\.[0-9]+)?$'
      then amount::numeric
      else null
    end as amount_clean,

    case 
      when not (trim(amount::text) ~ '^-?[0-9]+(\.[0-9]+)?$')
           and amount is not null
      then amount::text
    end as amount_invalid_raw,

    -- ✅ transaction_date cleanup
    case
      when trim(transaction_date::text) ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' 
      then transaction_date::date
      else null
    end as transaction_date,

    -- ✅ status normalization
    upper(nullif(trim(status::text), '')) as status,

    case 
      when upper(nullif(trim(status::text), '')) in ('SUCCESS','COMPLETED','PAID') 
      then true 
      else false 
    end as is_success,

    now() at time zone 'utc' as ingestion_ts
  from src
),

deduplicated as (
  select
    *,
    row_number() over (partition by transaction_id order by ingestion_ts desc) as rn
  from normalized
)

select *
from deduplicated
where rn = 1

