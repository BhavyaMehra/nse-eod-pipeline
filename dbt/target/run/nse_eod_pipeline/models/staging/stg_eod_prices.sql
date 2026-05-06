
  create view "nse_warehouse"."staging"."stg_eod_prices__dbt_tmp"
    
    
  as (
    with source as (
    select * from "nse_warehouse"."raw"."eod_prices"
),

renamed as (
    select
        ticker,
        trade_date,
        open,
        high,
        low,
        close,
        volume,
        ingested_at
    from source
    where close is not null
        and volume > 0
)

select * from renamed
  );