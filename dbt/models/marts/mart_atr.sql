with base as (
    select * from {{ ref('stg_eod_prices') }}
),

prev_close as (
    select
        ticker,
        trade_date,
        high,
        low,
        close,
        lag(close) over (partition by ticker order by trade_date) as prev_close
    from base
),

true_range as (
    select
        ticker,
        trade_date,
        greatest(
            high - low,
            abs(high - prev_close),
            abs(low - prev_close)
        ) as true_range
    from prev_close
    where prev_close is not null
)

select
    ticker,
    trade_date,
    true_range,
    round(avg(true_range) over (
        partition by ticker
        order by trade_date
        rows between 13 preceding and current row
    ), 4) as atr_14d
from true_range
