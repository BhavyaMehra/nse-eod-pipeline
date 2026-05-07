import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import run_query

st.set_page_config(page_title='Market Overview', layout='wide')
st.title('Market Overview')

dates = run_query('select distinct trade_date from marts.mart_eod_returns order by trade_date desc')
date_list = pd.to_datetime(dates['trade_date']).dt.date.tolist()

selected_date = st.date_input(
    'Select Date',
    value=max(date_list),
    min_value=min(date_list),
    max_value=max(date_list)
)

# Only show data if selected date has data
if selected_date not in date_list:
    st.warning('No data available for this date. Please select a trading day.')
    st.stop()

st.session_state['selected_date'] = selected_date

# Daily returns for latest date
df = run_query(f"""
               SELECT ticker, daily_return_pct
               FROM marts.mart_eod_returns
               WHERE trade_date = '{selected_date}'
               AND daily_return_pct IS NOT NULL
               ORDER BY daily_return_pct DESC 
""")

# Market breadth
total = len(df)
gainers = len(df[df['daily_return_pct'] > 0])
losers = len(df[df['daily_return_pct'] < 0])
flat = total - gainers - losers

col1, col2, col3, col4 = st.columns(4)
col1.metric('Total Stocks', total)
col2.metric('Gainers', gainers)
col3.metric('Losers', losers)
col4.metric('Flat', flat)

# Heatmap

st.subheader('Return Heatmap')
fig = px.treemap(
    df,
    path=['ticker'],
    values=df['daily_return_pct'].abs(),
    color='daily_return_pct',
    color_continuous_scale='RdYlGn',
    color_continuous_midpoint=0,
    range_color=[-5,5],
    hover_data={'daily_return_pct': ':.2f'}
)
fig.update_layout(margin=dict(t=0, l=0, r=0, b=0))
st.plotly_chart(fig, width='stretch')

st.divider()

# Top gainers and loser
col1, col2 = st.columns(2)

with col1:
    st.subheader('Top 10 Gainers')
    st.dataframe(
        df.head(10).round(2).rename(columns={'ticker': 'Ticker', 'daily_return_pct': 'Return %'}),
        hide_index=True,
        width='stretch'
    )

with col2:
    st.subheader('Top 10 Losers')
    st.dataframe(
        df.tail(10).round(2).rename(columns={'ticker': 'Ticker', 'daily_return_pct': 'Return %'}),
        hide_index=True,
        width='stretch'
    )