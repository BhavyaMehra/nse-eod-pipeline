import streamlit as st
import pandas as pd
import sys 
import os
from datetime import date

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import run_query

st.set_page_config(page_title='Stock Screener', layout='wide')
st.title('Stock Screener')

selected_date = st.session_state.get('selected_date', date.today())

st.caption(f'Data as of {selected_date}')

df = run_query(f"""
    select r.ticker, r.daily_return_pct, v.vol_20d, ma.ma_20d, ma.ma_50d, r.close
               from marts.mart_eod_returns r
               left join marts.mart_volatility v
                on r.ticker = v.ticker and r.trade_date = v.trade_date
               left join marts.mart_moving_averages ma
                on r.ticker = ma.ticker and r.trade_date = ma.trade_date
               where r.trade_date = '{selected_date}'
               and r.daily_return_pct IS NOT NULL
               order by r.daily_return_pct desc
""")

st.divider()

col1, col2 = st.columns(2)

with col1:
    min_return, max_return = st.slider(
        'Daily Return % Range',
        min_value=float(df['daily_return_pct'].min()),
        max_value=float(df['daily_return_pct'].max()),
        value=(float(df['daily_return_pct'].min()), float(df['daily_return_pct'].max())),
        step=0.1
    )

with col2:
    max_vol = st.slider(
        'Max Volatility',
        min_value=0.0,
        max_value=float(df['vol_20d'].dropna().max()),
        value=float(df['vol_20d'].dropna().max()),
        step=0.1
    )

filtered = df[
    (df['daily_return_pct'] >= min_return) &
    (df['daily_return_pct'] <= max_return) &
    (df['vol_20d'] <= max_vol)
    ]
filtered = filtered.round(2)

st.markdown(f"**{len(filtered)} stocks match your filters**")

st.dataframe(
    filtered.rename(columns={
        'ticker': 'Ticker',
        'daily_return_pct': 'Return %',
        'vol_20d': 'Volatility 20d',
        'ma_20d': 'MA 20d',
        'ma_50d': 'MA 50d',
        'close': 'Close'
    }),
    hide_index=True,
    width='stretch'
)

csv = filtered.to_csv(index=False)
st.download_button(
    label='Download as CSV',
    data=csv,
    file_name=f'screener_{selected_date}.csv',
    mime='text/csv'
)