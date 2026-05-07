import streamlit as st

st.set_page_config(
    page_title="NSE Market Dashboard",
    layout='wide'
)

st.title(' NSE EOD Market Dashboard')
st.markdown("""
        A production style data pipeline fetching daily closing prices for 135 NSE large-cap stocks.
                    
        **Data refreshes automatically every weekday 4:15 pm IST.**
                    
        ---

        **Nativate using the sidebar**
        - **Market Overview** - daily return heatmap, top gainers and losers
        - **Stock Deep Dive** - price chart with moving averages and volatility
        - **Screener** - filter stocks by return and volatility
""")

st.sidebar.success('Select a page above.')
