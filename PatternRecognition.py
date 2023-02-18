import talib as ta
import pandas as pd
import numpy as np

def GetPatternForData(stock_data_df):
    candle_name_list = ta.get_function_groups()['Pattern Recognition']
    tech_analysis_df = stock_data_df.iloc[-10:].copy()
    op_df = tech_analysis_df.Open
    hi_df = tech_analysis_df.High
    lo_df = tech_analysis_df.Low
    cl_df = tech_analysis_df.Close

    for candle in candle_name_list:
        tech_analysis_df[candle] = getattr(ta, candle)(op_df, hi_df, lo_df, cl_df)

    result = pd.DataFrame(tech_analysis_df[['Date']+candle_name_list].sum(), columns=['Count'])
    filtered_results = result[result.Count != 0]

    if filtered_results.empty:
        return None, tech_analysis_df
    else:
        return filtered_results[filtered_results.Count == filtered_results.Count.max()].index[0], tech_analysis_df

    return None, tech_analysis_df

def ComputeChaikinADSignal(stock_data_df):
    ADOSC_data = stock_data_df.copy()
    ADOSC_data['ADOSC'] = ta.ADOSC(ADOSC_data.High, ADOSC_data.Low, ADOSC_data.Close, ADOSC_data.Volume,
                                   fastperiod=3, slowperiod=10)
    ADOSC_data.dropna(inplace=True)
    ADOSC_data['ADOSC_chg'] = np.log(ADOSC_data['ADOSC']/ADOSC_data['ADOSC'].shift(1))
    ADOSC_data.dropna(inplace=True)
    return ADOSC_data

def ComputeMACDSignal(stock_data_df):
    macd_data_df = stock_data_df.copy()
    macd_data_df['macd'], macd_data_df['macdsignal'], macd_data_df['macdhist'] =\
        ta.MACD(macd_data_df.Close, fastperiod=12, slowperiod=26, signalperiod=9)
    macd_data_df.dropna(inplace=True)
    return macd_data_df

