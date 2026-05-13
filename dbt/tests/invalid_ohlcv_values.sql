select *
from {{ ref('stg_eod_prices' )}}
where ticker <> 'NIFTY 50'
    and ( 
        close <= 0
        or open <= 0
        or high <= 0
        or low <= 0
        or volume < 0
        or high < low
    )