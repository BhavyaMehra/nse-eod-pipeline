import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os
from datetime import date

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import run_query

st.set_page_config(
    page_title="NSE Market Dashboard",
    layout='wide'
)

st.title(' NSE EOD Market Dashboard')
st.caption("Production-style data pipeline } 135 NSE large-cap stocks | Refreshsed daily at 4:15 pm IST")

st.divider()

latest_date = run_query('select max(trade_date) as latest from marts.mart_eod_returns')['latest'][0]

df = run_query(f"""
    select ticker, daily_return_pct
               from marts.mart_eod_returns
               where trade_date = '{latest_date}'
               and daily_return_pct IS NOT NULL
               order by daily_return_pct desc
""")

total = len(df)
gainers = len(df[df['daily_return_pct'] > 0])
losers = len(df[df['daily_return_pct'] < 0])
best = df.iloc[0]
worst = df.iloc[-1]

st.subheader(f"Market Pulse - {latest_date}")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric('Universe', total)
col2.metric('Gainers', gainers, delta=f"{round(gainers/total*100)}% of market")
col3.metric('Losers', losers, delta=f"{round(losers/total*100)}% of market", delta_color="inverse")
col4.metric(f"Best Performer: {best['ticker']}", f"{best['daily_return_pct'].round(2)}%", delta='today')
col5.metric(f"Worst Performer: {worst['ticker']}", f"{worst['daily_return_pct'].round(2)}%", delta='today', delta_color="inverse")

st.markdown("**Market Breadth**")

breadth_df = pd.DataFrame({
    'Category': ['Gainers', 'Losers', 'Flat'],
    'Count': [gainers, losers, total - gainers - losers],
    'Label': [f'▲ {gainers}', f'▼ {losers}', f'— {total - gainers - losers}']
})

fig = px.bar(
    breadth_df,
    x='Count',
    y=['Market'] * 3,
    orientation='h',
    color='Category',
    color_discrete_map={'Gainers': '#00cc44', 'Losers': '#ff4444', 'Flat': '#888888'},
    text='Label',
    barmode='stack'
)
fig.update_layout(
    template='plotly_dark',
    showlegend=False,
    height=80,
    margin=dict(t=0, l=0, r=0, b=0),
    xaxis_visible=False,
    yaxis_visible=False,
)
fig.update_traces(textposition='inside', textfont_size=14)
st.plotly_chart(fig, use_container_width=True)

st.divider()

st.info("Use the sidebar to explore pages.")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Market Overview**")
    st.markdown("Daily return heatmap, top gainers, top losers, market breadth.")

with col2:
    st.markdown("**Stock Deep Dive**")
    st.markdown("Price chart with 20d and 50d moving averages, returns and volatilty.")

with col3:
    st.markdown("**Screener**")
    st.markdown("Filter stocks by return and volatility, download as CSV.")

st.divider()
st.caption("Built with Apache Airflow | dbt | PostgreSQL | Docker | Kite Connect | Streamlit", text_alignment='center')
st.markdown("[View repo on GitHub](https://github.com/BhavyaMehra/nse-eod-pipeline)", text_alignment='center')