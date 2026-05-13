with prices as (
    select
        ticker,
        trade_date,
        close
    from {{ ref('stg_eod_prices') }}
),

returns_20d as (
    select
        ticker,
        trade_date,
        close,
        lag(close, 20) over (
            partition by ticker
            order by trade_date
        ) as close_20d_ago
    from prices
),

stock_returns as (
    select
        ticker,
        trade_date,
        case
            when close_20d_ago is null or close_20d_ago = 0 then null
            else ((close / close_20d_ago) - 1) * 100
        end as stock_20d_return
    from returns_20d
),

nifty_returns as (
    select
        trade_date,
        stock_20d_return as nifty_20d_return
    from stock_returns
    where ticker = 'NIFTY 50'
)

select
    s.ticker,
    s.trade_date,
    s.stock_20d_return,
    n.nifty_20d_return,
    s.stock_20d_return - n.nifty_20d_return as relative_strength_20d
from stock_returns s
left join nifty_returns n
    on s.trade_date = n.trade_date
where s.ticker <> 'NIFTY 50'