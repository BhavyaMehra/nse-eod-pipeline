with base as (
    select * from "nse_warehouse"."staging"."stg_eod_prices"
),

returns as (
    select 
        ticker,
        trade_date,
        close,
        lag(close) over (partition by ticker order by trade_date) as prev_close,
        round((close - lag(close) over (partition by ticker order by trade_date)) / nullif(lag(close) over (partition by ticker order by trade_date), 0) * 100, 4) 
            as daily_return_pct
    from base
)

select * from returns