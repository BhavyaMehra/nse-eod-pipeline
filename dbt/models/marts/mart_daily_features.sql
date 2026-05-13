-- Wide mart joining all indicators. This is the primary table for the screener.
-- Query only the latest trade_date in Streamlit to get today's snapshot.

with returns as (
    select ticker, trade_date, close, daily_return_pct
    from {{ ref('mart_eod_returns') }}
),

ma as (
    select ticker, trade_date, ma_20d, ma_50d
    from {{ ref('mart_moving_averages') }}
),

volatility as (
    select ticker, trade_date, vol_20d
    from {{ ref('mart_volatility') }}
),

rsi as (
    select ticker, trade_date, rsi_14d
    from {{ ref('mart_rsi') }}
),

atr as (
    select ticker, trade_date, atr_14d
    from {{ ref('mart_atr') }}
),

vol_ratio as (
    select ticker, trade_date, vol_ratio, high_52w, pct_of_52w_high
    from {{ ref('mart_vol_ratio') }}
),

relative_strength as (
    select
        ticker,
        trade_date,
        stock_20d_return,
        nifty_20d_return,
        relative_strength_20d
    from {{ ref('mart_relative_strength') }}
)

select
    r.ticker,
    r.trade_date,
    r.close,
    r.daily_return_pct,
    ma.ma_20d,
    ma.ma_50d,
    v.vol_20d,
    rsi.rsi_14d,
    atr.atr_14d,
    vr.vol_ratio,
    vr.high_52w,
    vr.pct_of_52w_high,
    rs.stock_20d_return,
    rs.nifty_20d_return,
    rs.relative_strength_20d
from returns r
left join ma          on r.ticker = ma.ticker       and r.trade_date = ma.trade_date
left join volatility v on r.ticker = v.ticker        and r.trade_date = v.trade_date
left join rsi         on r.ticker = rsi.ticker       and r.trade_date = rsi.trade_date
left join atr         on r.ticker = atr.ticker       and r.trade_date = atr.trade_date
left join vol_ratio vr on r.ticker = vr.ticker       and r.trade_date = vr.trade_date
left join relative_strength rs on r.ticker = rs.ticker and r.trade_date = rs.trade_date
