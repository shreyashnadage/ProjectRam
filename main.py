import streamlit as st
from nsetools import Nse
from nsepy import get_history
from datetime import date, timedelta
from PatternRecognition import *
from VixAnalysis import *
from TopMovers import *
import time
from scipy.stats import norm
from math import exp, log, sqrt
import numpy as np
import pandas as pd
import yfinance as yf
from plotly.subplots import make_subplots
from random import randrange

buy_sell_color_dict = {"Buy":"green", "Sell":"red", "Hold":"yellow"}

today = date.today()
nse = Nse()
all_stock_codes = nse.get_stock_codes()
all_stock_names = dict(zip(nse.get_stock_codes().values(),nse.get_stock_codes().keys()))
del all_stock_names['NAME OF COMPANY']

st.set_page_config(page_title='Jarvis', page_icon=':money_with_wings:', layout='wide', initial_sidebar_state='auto')
pd.options.plotting.backend = "plotly"
st.title('Jarvis')
stock_tab, mf_tab, intraday_tab = st.tabs(['Stocks', 'Mutual Funds', 'Intraday'])

main_sidebar = st.sidebar
with main_sidebar:

    vix_container = st.container()
    with vix_container:

        with st.spinner(text='Loading VIX Analysis...'):
            try:
                st.subheader("VIX Analysis")
                vix_df = get_history(symbol="India VIX", start=today-timedelta(30), end=today, index=True)
                vix_analysis_df = ProcessVixData(vix_df)
                value = vix_analysis_df.Norm_Class[-30:].mean()
                st.metric("Current Market Mood", GetMood(value), '{:.2f}'.format(value))
                mood_dict = {'Greed': 'Markets are in bullish state. Good time to book profits.',
                             'Holding Steady': 'Markets are indecisive. its good to hold onto existing portfolio.',
                             'Fear': "Markets are in bearish state. Good time to pick good stocks for cheap prices."}

                with st.expander(GetMood(value)):
                    st.write(mood_dict[GetMood(value)])
            except:
                st.error("Issues fetching VIX Data!")

    top_losers = st.container()
    with top_losers:
        if GetTopLosers() is not None:
            st.subheader('Top Losers')
            st.table(GetTopLosers())

    top_gainers = st.container()
    with top_gainers:
        if GetTopGainers() is not None:
            st.subheader('Top Gainers')
            st.table(GetTopGainers())

with stock_tab:
    min_days = 60
    stock_selector_col, tenure_selector_start_col, tenure_selector_end_col = st.columns(3)
    with stock_selector_col:
        selected_stock = st.selectbox('Please select a stock for analysis',
                                      list(all_stock_names.keys()),
                                      help='Choose stock to analyze')
        ticker_yf = all_stock_names[selected_stock]+".NS"

    with tenure_selector_start_col:
        start_date = st.date_input("Start Date", today-timedelta(min_days))

    with tenure_selector_end_col:
        end_date = st.date_input("End Date", today)

    if (end_date<start_date):
        st.error('Start date should be before End date')

    time_delta = end_date-start_date
    if time_delta.days < min_days:
        st.error(f'Please extend the range of dates. We need atleast {min_days} days of data for analysis.')

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
            return df.to_csv(index=False).encode('utf-8')

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

    st.markdown("***")

    st.subheader('Candlestick Matched pattern:')
    pattern_expander_col, cs_gauge_col = st.columns((1, 1))

    matched_pattern, tech_df = GetPatternForData(stock_data_df=stock_data_df)
    if matched_pattern is not None:
        with pattern_expander_col:
            with st.expander(matched_pattern):
                st.write("Will add description here")
        with cs_gauge_col:
            score_cs_pattern = tech_df[[matched_pattern]].astype(float).sum()[0]
            if score_cs_pattern < 0:
                value = "Bearish Outlook"
                delta = -1
            elif score_cs_pattern == 0:
                value = "Indecisive Outlook"
                delta = 0
            else:
                value = "Bullish Outlook"
                delta = 1

            st.metric(label='Pattern Verdict', value=value, delta=delta, help="Outlook from detected CandleStick pattern")
    else:
        with pattern_expander_col:
            with st.expander("No Pattern Matched"):
                st.write("It seems there were no pattern formations for last 10 days.")

        with cs_gauge_col:
            st.metric(label='Pattern Verdict', value="Indecisive Outlook", delta=0,
                      help="Outlook from detected CandleStick pattern")

    st.markdown("***")
    st.subheader('Volume Analysis Pattern:')
    chaikin_curr_trend_col, MACD_curr_trend_col = st.columns(2)
    with chaikin_curr_trend_col:
        st.subheader("Chaikin Indicator")
        chaikin_osc_df = ComputeChaikinADSignal(stock_data_df)
        chaikin_osc_trend = chaikin_osc_df.ADOSC.iloc[-10:].mean()
        chaikin_osc_trend_chg = chaikin_osc_df.ADOSC_chg.iloc[-10:].mean()

        if chaikin_osc_trend >= 0:
            chaikin_trend = "Bullish"
        else:
            chaikin_trend = "Bearish"

            st.metric(label="Chaikin Current Trend", value=chaikin_trend,
                      delta="{:.2f}%".format(chaikin_osc_trend_chg*100),
                      help="Chaikin Oscillator is an indicator of buy/sell pressure in the market for give stock.")
    with MACD_curr_trend_col:
        st.subheader("MACD Indicator")
        macd_df = ComputeMACDSignal(stock_data_df.set_index('Date'))
        macd_bull_bear_signal = "Bullish" if macd_df.macd.iloc[-1] >= macd_df.macdsignal.iloc[-1] else "Bearish"
        st.metric(label="MACD Signal", value=macd_bull_bear_signal, delta="{:.2f}".format(macd_df.macdhist.iloc[-1]),
                  help="Helpful in analyzing momentum of price.")

    momentum_plot_column = st.container()

    with momentum_plot_column:
        st.subheader("MACD Chart")
        fig_macd = go.Figure()
        fig_macd = make_subplots(rows=3, cols=1, shared_xaxes=True,
                                 vertical_spacing=0.01, row_heights=[0.5, 0.3, 0.3])
        fig_macd.add_trace(go.Candlestick(x=macd_df.index,
                 open=macd_df['Open'],
                 high=macd_df['High'],
                 low=macd_df['Low'],
                 close=macd_df['Close'], name=f"OHLC Chart : {ticker_yf}"), row=1, col=1)

        colors = ['green' if row['Open'] - row['Close'] >= 0
                  else 'red' for index, row in macd_df.iterrows()]
        fig_macd.add_trace(go.Bar(x=macd_df.index, y=macd_df['Volume'], marker_color=colors, name="Volume"),
                           row=2, col=1)
        colors = ['green' if val >= 0
                  else 'red' for val in macd_df.macdhist]
        fig_macd.add_trace(go.Bar(x=macd_df.index, y=macd_df.macdhist, marker_color=colors, name="MACD Histogram"), row=3, col=1)
        fig_macd.add_trace(go.Scatter(x=macd_df.index, y=macd_df.macd, line=dict(color='black', width=2), name="MACD"),
                           row=3, col=1)
        fig_macd.add_trace(go.Scatter(x=macd_df.index, y=macd_df.macdsignal,
                                      line=dict(color='blue', width=1), name="MACD Signal"), row=3, col=1)
        fig_macd.update_yaxes(title_text="Price", row=1, col=1)
        fig_macd.update_yaxes(title_text="Volume", row=2, col=1)
        fig_macd.update_yaxes(title_text="MACD", showgrid=False, row=3, col=1)
        st.plotly_chart(fig_macd, use_container_width=True)



with intraday_tab:

    stock_selector_container_intraday = st.container()
    stock_selector_container_intraday_placeholder = st.empty()
    with stock_selector_container_intraday:
        selected_stock_intraday_col, _, barrier_probability_calc_input_col, barrier_probability_calc_button_col \
            = st.columns((1, 1, 1, 1))
        with selected_stock_intraday_col:
            selected_stock_intraday = st.selectbox(label='Select stock for intraday analysis',
                                                   options=list(all_stock_names.keys()),
                                                   help='Choose stock to analyze')
        intraday_selected_ticker = all_stock_names[selected_stock_intraday]
        stock_quote_intraday = nse.get_quote(intraday_selected_ticker)

        with barrier_probability_calc_input_col:
            barrier = st.number_input("Enter strike to calculate hit probability", min_value=1.0,
                                      value=100.00, step=0.01, max_value=999999999.99,
                                      help="Use this tool to estimate strike price of options strategy.")
            if barrier < 0:
                st.error("Please enter strike > 0.")
        with barrier_probability_calc_button_col:
            r = 0.073
            tk = yf.Ticker(intraday_selected_ticker + ".NS")
            v = np.log((tk.history(period='365d', interval="1d")['Close'] /
                        tk.history(period='365d', interval="1d")['Close'].shift(1)).dropna()).std()
            live_stock_price_intraday = nse.get_quote(intraday_selected_ticker)['lastPrice']
            barrier_flag = 1 if barrier > live_stock_price_intraday else -1
            T = 1
            d2 = barrier_flag * ((log(live_stock_price_intraday / barrier) + (r - 0.5 * v ** 2)*T) / v*sqrt(T))
            hit_prob = exp(-r) * norm.cdf(d2)
            st.metric(label="Barrier hit probability", value='{:.0f}'.format(hit_prob*100) + '%',
                      help="It gives probability that stock price will hit"
                      " the strike price you entered")

    while True:
        with stock_selector_container_intraday_placeholder.container():
            quote_dict = nse.get_quote(intraday_selected_ticker)
            nifty_quote_dict = nse.get_index_quote('Nifty 50')
            live_stock_col, live_nifty_col = st.columns(2)
            with live_stock_col:
                live_stock_price_intraday = quote_dict['lastPrice']
                st.metric(label=all_stock_names[selected_stock_intraday], value=live_stock_price_intraday,
                          delta=quote_dict['pChange'])
            with live_nifty_col:
                live_nifty_price = nifty_quote_dict['lastPrice']
                st.metric(label="Nifty 50", value=live_nifty_price,
                          delta=nifty_quote_dict['pChange'])

            st.markdown("***")

            tk = yf.Ticker(intraday_selected_ticker+'.NS')
            df_intraday_realtime = tk.history(period='1d', interval='1m')
            df_intraday_realtime['VWAP'] = (((df_intraday_realtime.High + df_intraday_realtime.Low
                                              + df_intraday_realtime.Close) / 3)
                                            * df_intraday_realtime.Volume).cumsum() /\
                                           df_intraday_realtime.Volume.cumsum()
            df_intraday_realtime.dropna(inplace=True)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_intraday_realtime.index, y=df_intraday_realtime.Close,
                                     mode='lines',
                                     name='Price'))
            fig.add_trace(go.Scatter(x=df_intraday_realtime.index, y=df_intraday_realtime.VWAP,
                                     mode='lines',
                                     name='VWAP'))
            fig.update_layout(title=intraday_selected_ticker, xaxis_title="Time",
                              yaxis_title=intraday_selected_ticker+" Price")
            st.plotly_chart(fig, use_container_width=True)

            if df_intraday_realtime.Close.values[-1] < df_intraday_realtime.VWAP.values[-1]:
                VWAP_signal = "Buy"
                vwap_icon = ':thumbsup:'
                vwap_explain = "Currently the market price is less than the VWAP price. Its good time to enter into trade."
            elif df_intraday_realtime.Close.values[-1] == df_intraday_realtime.VWAP.values[-1]:
                VWAP_signal = "Hold"
                vwap_icon = ':open_hands:'
                vwap_explain = "Currently the market price is equal to the VWAP price. Wait for buy or sell signal"
            else:
                VWAP_signal = "Sell"
                vwap_icon = ':thumbsdown:'
                vwap_explain = "Currently the market price is greater than the VWAP price. Its good time to exit the trade."

            vwap_expander_col, _ = st.columns((1, 3))
            with vwap_expander_col:
                with st.expander(f"VWAP Buy/Sell Indicator : {VWAP_signal}"):
                    st.markdown(vwap_explain)
                st.header(vwap_icon)

        time.sleep(5)

with mf_tab:
    st.write("Coming soon...")
