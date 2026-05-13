with base as (
    select * from {{ ref('mart_eod_returns') }}
),

gains_losses as (
    select
        ticker,
        trade_date,
        case when daily_return_pct > 0 then daily_return_pct else 0 end as gain,
        case when daily_return_pct < 0 then abs(daily_return_pct) else 0 end as loss
    from base
),

rolling as (
    select
        ticker,
        trade_date,
        avg(gain) over (
            partition by ticker
            order by trade_date
            rows between 13 preceding and current row
        ) as avg_gain_14d,
        avg(loss) over (
            partition by ticker
            order by trade_date
            rows between 13 preceding and current row
        ) as avg_loss_14d
    from gains_losses
)

select
    ticker,
    trade_date,
    case
        when avg_loss_14d = 0 then 100
        else round(100 - (100 / (1 + avg_gain_14d / nullif(avg_loss_14d, 0))), 2)
    end as rsi_14d
from rolling
