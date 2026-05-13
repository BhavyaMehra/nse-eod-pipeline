import streamlit as st
import pandas as pd
import sys
import os
from datetime import date

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import run_query

st.set_page_config(page_title="Stock Screener", layout="wide")
st.title("Stock Screener")

selected_date = st.session_state.get("selected_date", None)

if selected_date:
    date_filter = f"where trade_date = '{selected_date}'"
else:
    date_filter = """
    where trade_date = (
        select max(trade_date)
        from marts.mart_daily_features
    )
    """

df = run_query(f"""
    select
        ticker,
        trade_date,
        close,
        daily_return_pct,
        ma_20d,
        ma_50d,
        vol_20d,
        rsi_14d,
        atr_14d,
        vol_ratio,
        high_52w,
        pct_of_52w_high,
        stock_20d_return,
        nifty_20d_return,
        relative_strength_20d
    from marts.mart_daily_features
    {date_filter}
    and ticker <> 'NIFTY 50'
    order by daily_return_pct desc
""")

if df.empty:
    st.warning("No data available for selected date.")
    st.stop()

actual_date = df["trade_date"].max()
st.caption(f"Data as of {actual_date}")

st.divider()

preset = st.button("Apply Sweep Setup Preset")

if preset:
    default_rsi = (0.0, 60.0)
    default_vol_ratio = 1.0
    default_rs_only = True
    default_52w = 85.0
else:
    default_rsi = (
        float(df["rsi_14d"].dropna().min()),
        float(df["rsi_14d"].dropna().max())
    )
    default_vol_ratio = 0.0
    default_rs_only = False
    default_52w = 0.0

col1, col2, col3 = st.columns(3)

with col1:
    return_range = st.slider(
        "Daily Return % Range",
        min_value=float(df["daily_return_pct"].dropna().min()),
        max_value=float(df["daily_return_pct"].dropna().max()),
        value=(
            float(df["daily_return_pct"].dropna().min()),
            float(df["daily_return_pct"].dropna().max())
        ),
        step=0.1
    )

with col2:
    rsi_range = st.slider(
        "RSI 14D Range",
        min_value=0.0,
        max_value=100.0,
        value=default_rsi,
        step=1.0
    )

with col3:
    min_52w_proximity = st.slider(
        "Minimum % of 52W High",
        min_value=0.0,
        max_value=100.0,
        value=default_52w,
        step=1.0
    )

col4, col5, col6 = st.columns(3)

with col4:
    max_volatility = st.slider(
        "Max 20D Volatility",
        min_value=0.0,
        max_value=float(df["vol_20d"].dropna().max()),
        value=float(df["vol_20d"].dropna().max()),
        step=0.1
    )

with col5:
    min_vol_ratio = st.slider(
        "Minimum Volume Ratio",
        min_value=0.0,
        max_value=max(5.0, float(df["vol_ratio"].dropna().max())),
        value=default_vol_ratio,
        step=0.1
    )

with col6:
    relative_strength_only = st.checkbox(
        "Only outperforming Nifty over 20D",
        value=default_rs_only
    )

filtered = df[
    (df["daily_return_pct"].between(return_range[0], return_range[1])) &
    (df["rsi_14d"].between(rsi_range[0], rsi_range[1])) &
    (df["pct_of_52w_high"] >= min_52w_proximity) &
    (df["vol_20d"] <= max_volatility) &
    (df["vol_ratio"] >= min_vol_ratio)
]

if relative_strength_only:
    filtered = filtered[
        filtered["relative_strength_20d"].notna() &
        (filtered["relative_strength_20d"] > 0)
    ]

filtered = filtered.sort_values("relative_strength_20d", ascending=False)
filtered = filtered.round(2)

benchmark_series = df["nifty_20d_return"].dropna()

if not benchmark_series.empty:
    benchmark_return = benchmark_series.iloc[0]
    st.metric("Nifty 20D Return", f"{benchmark_return:.2f}%")

st.markdown(f"**{len(filtered)} stocks match your filters**")

display_df = filtered.rename(columns={
    "ticker": "Ticker",
    "trade_date": "Date",
    "close": "Close",
    "daily_return_pct": "Return %",
    "ma_20d": "MA 20D",
    "ma_50d": "MA 50D",
    "vol_20d": "Volatility 20D",
    "rsi_14d": "RSI 14D",
    "atr_14d": "ATR 14D",
    "vol_ratio": "Volume Ratio",
    "high_52w": "52W High",
    "pct_of_52w_high": "% of 52W High",
    "stock_20d_return": "Stock 20D Return %",
    "relative_strength_20d": "Relative Strength 20D"
})

display_df = display_df[[
    "Ticker",
    "Date",
    "Close",
    "Return %",
    "MA 20D",
    "MA 50D",
    "Volatility 20D",
    "RSI 14D",
    "ATR 14D",
    "Volume Ratio",
    "52W High",
    "% of 52W High",
    "Stock 20D Return %",
    "Relative Strength 20D"
]]

st.dataframe(
    display_df,
    hide_index=True,
    width="stretch"
)

csv = filtered.to_csv(index=False)

st.download_button(
    label="Download as CSV",
    data=csv,
    file_name=f"screener_{actual_date}.csv",
    mime="text/csv"
)