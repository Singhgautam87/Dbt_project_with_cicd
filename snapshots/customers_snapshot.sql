{% snapshot customers_snapshot %}
{{
  config(
    target_schema='marts',
    unique_key='customer_id',
    strategy='check',
    check_cols=['first_name','last_name','email','region']
  )
}}
select * from {{ ref('stg_customers') }}
{% endsnapshot %}
