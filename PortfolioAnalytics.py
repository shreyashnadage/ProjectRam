import yfinance as yf
import pandas as pd
from pypfopt.hierarchical_portfolio import HRPOpt


def get_data_for_HRP(asset_list, n=10):
    df = yf.download(' '.join(asset_list), period='5y', interval='1d')['Adj Close']
    df = df.dropna(axis=1, how='all')
    df = df.pct_change().dropna()
    df = df[df.columns[:n]]
    return df

def get_HRP_weights(asset_list):
    prices_data = get_data_for_HRP(asset_list)

    hrp = HRPOpt(prices_data)
    res = hrp.optimize()
    df = pd.DataFrame({'Stock': [key for key in res.keys()], 'Weights': [round(res[key], 2) for key in res.keys()]})
    return df, hrp

def get_portfolio_performance(hrp):
    five_yr_benchmk = yf.download('^NSEI', period='5y', interval='1d')[['Adj Close']]\
        .pct_change().dropna().mean()['Adj Close']
    exp_ret, vol, sharpe = hrp.portfolio_performance(five_yr_benchmk, frequency=252)
    return exp_ret, vol, sharpe

