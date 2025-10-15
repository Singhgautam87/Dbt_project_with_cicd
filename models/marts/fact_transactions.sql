{{ config(materialized='incremental',unique_key='transaction_id') }}

with src as (
  select
    transaction_id,
    customer_id,
    amount_clean as amount,         
    transaction_date,
    status,
    is_success,
    ingestion_ts
  from {{ ref('stg_transactions') }}
)

select
  transaction_id,
  customer_id,
  amount,
  transaction_date,
  status,
  is_success,
  ingestion_ts
from src

{% if is_incremental() %}
  -- ✅ Incremental load with watermark (1-day buffer for late-arriving data)
  where transaction_date >= (
    select coalesce(max(transaction_date)::date - 1, '1970-01-01'::date)
    from {{ this }}
  )
{% endif %}

