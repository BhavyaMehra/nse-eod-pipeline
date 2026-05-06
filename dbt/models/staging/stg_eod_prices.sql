with source as (
    select * from {{ source('raw', 'eod_prices') }}
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