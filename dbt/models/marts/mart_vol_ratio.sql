with base as (
    select * from {{ ref('stg_eod_prices') }}
),

vol_stats as (
    select
        ticker,
        trade_date,
        close,
        volume,
        round(avg(volume) over (
            partition by ticker
            order by trade_date
            rows between 19 preceding and current row
        ), 0) as avg_vol_20d,
        max(high) over (
            partition by ticker
            order by trade_date
            rows between 251 preceding and current row
        ) as high_52w
    from base
)

select
    ticker,
    trade_date,
    volume,
    avg_vol_20d,
    round(volume::numeric / nullif(avg_vol_20d, 0), 4) as vol_ratio,
    high_52w,
    round(close / nullif(high_52w, 0) * 100, 2) as pct_of_52w_high
from vol_stats
