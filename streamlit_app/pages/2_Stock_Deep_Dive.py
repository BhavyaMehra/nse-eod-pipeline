import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os 
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import run_query

st.set_page_config(page_title='Stock Deep Dive', layout='wide')
st.title('Stock Deep Dive')

# Stock selector
tickers = run_query('select distinct ticker from marts.mart_eod_returns order by ticker')
selected = st.selectbox('Select a stock', tickers['ticker'].tolist())

# Fetch data
price_df = run_query(f"""
                     select ma.trade_date, ma.close, ma.ma_20d, ma.ma_50d, r.daily_return_pct, v.vol_20d
                     from marts.mart_moving_averages ma
                     left join marts.mart_eod_returns r
                        on ma.ticker = r.ticker and ma.trade_date = r.trade_date
                     left join marts.mart_volatility v
                        on ma.ticker = v.ticker and ma.trade_date = v.trade_date
                     where ma.ticker = '{selected}'
                     order by ma.trade_date
""")

st.divider()

# Price chart with MAs
st.subheader(f'{selected} - Price with Moving Averages')
fig = go.Figure()
fig.add_trace(go.Scatter(x=price_df['trade_date'], y=price_df['close'].round(2), name='Close', line=dict(color='blue', width=2)))
fig.add_trace(go.Scatter(x=price_df['trade_date'], y=price_df['ma_20d'].round(2), name='20d MA', line=dict(color='cyan', width=1.5)))
fig.add_trace(go.Scatter(x=price_df['trade_date'], y=price_df['ma_50d'].round(2), name='50d MA', line=dict(color='orange', width=1.5)))

fig.update_layout(template='plotly_dark', xaxis_title='Date', yaxis_title='Price')
st.plotly_chart(fig, width='stretch')

# Returns bar chart
st.subheader('Daily Returns %')
fig2 = go.Figure()
fig2.add_trace(go.Bar(
    x=price_df['trade_date'],
    y=price_df['daily_return_pct'],
    marker_color=price_df['daily_return_pct'].apply(lambda x: 'green' if x>= 0 else 'red')
))
fig2.update_layout(template='plotly_dark', xaxis_title='Date', yaxis_title='Return %')
st.plotly_chart(fig2, width='stretch')

# Volatility chart
st.subheader('20d Rolling Volatility')
fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=price_df['trade_date'], y=price_df['vol_20d'], name='Volatility', line=dict(color='blue', width=2)))
fig3.update_layout(template='plotly_dark', xaxis_title='Date', yaxis_title='Volatility')
st.plotly_chart(fig3, width='stretch')