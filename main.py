import streamlit as st
from nsetools import Nse
from nsepy import get_history
from datetime import date, timedelta
from PatternRecognition import GetPatternForData
from VixAnalysis import *

import yfinance as yf

today = date.today()
nse = Nse()
all_stock_codes = nse.get_stock_codes()
all_stock_names = dict(zip(nse.get_stock_codes().values(),nse.get_stock_codes().keys()))
del all_stock_names['NAME OF COMPANY']

st.set_page_config(page_title='Jarvis', page_icon='N', layout='wide', initial_sidebar_state='auto')
st.title('Jarvis')
stock_tab, mf_tab = st.tabs(['Stocks', 'Mutual Funds'])

with stock_tab:
    stock_selector_col, tenure_selector_start_col, tenure_selector_end_col = st.columns(3)
    with stock_selector_col:
        selected_stock = st.selectbox('Please select a stock for analysis',
                                        list(all_stock_names.keys()),help='Choose stock to analyze')
        ticker_yf = all_stock_names[selected_stock]+".NS"

    with tenure_selector_start_col:
        start_date = st.date_input("Start Date", today-timedelta(40))

    with tenure_selector_end_col:
        end_date = st.date_input("End Date", today)

    if (end_date<start_date):
        st.error('Start date should be before End date')

    time_delta = end_date-start_date
    if time_delta.days < 35:
        st.error('Please extend the range of dates. We need atleast 30 days of data for analysis.')

    with st.spinner(text=f'Please Wait...Loading data for {selected_stock}'):
        tk = yf.Ticker(ticker_yf)
        stock_data_df = tk.history(start=start_date, end=end_date, interval="1d").reset_index()

    chart_title_col, download_button_col = st.columns(2)
    with chart_title_col:
        st.subheader(f'OHLC Chart for {selected_stock}')

    with download_button_col:
        @st.cache
        def convert_df(df):
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return df.to_csv().encode('utf-8')

        csv = convert_df(stock_data_df)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name=f'{selected_stock}.csv',
            mime='text/csv',
        )

    fig_main_cs = go.Figure(data=[go.Candlestick(x=stock_data_df['Date'],
                                         open=stock_data_df['Open'],
                                         high=stock_data_df['High'],
                                         low=stock_data_df['Low'],
                                         close=stock_data_df['Close'])])
    st.plotly_chart(fig_main_cs, use_container_width=True)

    st.subheader('Candlestick Matched pattern:')
    pattern_expander_col, cs_gauge_col = st.columns((1,3))

    matched_pattern, tech_df = GetPatternForData(stock_data_df=stock_data_df)
    if matched_pattern is not None:
        with pattern_expander_col:
            with st.expander(matched_pattern):
                st.write("Will add description here")

    else:
        with pattern_expander_col:
            with st.expander("No Pattern Matched"):
                st.write("It seems there were no pattern formations for last 10 days.")

with st.sidebar:
    vix_container = st.container()
    with vix_container:
        st.subheader("VIX Analysis")
        with st.spinner(text='Loading VIX Analysis...'):
            vix_df = get_history(symbol="India VIX", start=today-timedelta(30), end=today, index=True)
            vix_analysis_df = ProcessVixData(vix_df)
        value = vix_analysis_df.Norm_Class[-30:].mean()
        st.metric("Current Market Mood", GetMood(value), '{:.2f}'.format(value))
        mood_dict = {'Greed': 'Markets are in bullish state. Good time to book profits.',
                     'Holding Steady': 'Markets are indecisive. its good to hold onto existing portfolio.',
                     'Fear': "Markets are in bearish state. Good time to pick good stocks for cheap prices."}

        with st.expander(GetMood(value)):
            st.write(mood_dict[GetMood(value)])


