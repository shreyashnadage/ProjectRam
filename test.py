import streamlit as st
from nsetools import Nse
from datetime import date, timedelta
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf


with st.spinner(text=f'Please Wait...Loading data for Reliance'):
    tk = yf.Ticker('RELIANCE.NS')
    stock_data_df = tk.history(start='2022-11-01', end='2022-12-01', interval="1d").reset_index()
st.success('Done!')

fig = go.Figure(data=[go.Candlestick(x=stock_data_df['Date'],
                                     open=stock_data_df['Open'],
                                     high=stock_data_df['High'],
                                     low=stock_data_df['Low'],
                                     close=stock_data_df['Close'])])
st.plotly_chart(fig)