with base as (
    select * from {{ ref('stg_eod_prices') }}
),

moving_averages as (
    select  
        ticker,
        trade_date,
        close,
        round(avg(close) over (
            partition by ticker
            order by trade_date
            rows between 19 preceding and current row
        ), 4) as ma_20d,
        round(avg(close) over(
            partition by ticker
            order by trade_date
            rows between 49 preceding and current row
        ), 4) as ma_50d
    from base
)

select * from moving_averages