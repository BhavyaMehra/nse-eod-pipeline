with base as (
    select * from "nse_warehouse"."marts"."mart_eod_returns"
),

volatility as (
    select
        ticker,
        trade_date,
        daily_return_pct,
        round(stddev(daily_return_pct) over (
            partition by ticker
            order by trade_date
            rows between 19 preceding and current row
        ), 4) as vol_20d
    from base
)

select * from volatility