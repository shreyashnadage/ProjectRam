import talib
import pandas as pd

def GetPatternForData(stock_data_df):
    candle_name_list = talib.get_function_groups()['Pattern Recognition']
    tech_analysis_df = stock_data_df.iloc[-10:].copy()
    op_df = tech_analysis_df.Open
    hi_df = tech_analysis_df.High
    lo_df = tech_analysis_df.Low
    cl_df = tech_analysis_df.Close

    for candle in candle_name_list:
        tech_analysis_df[candle] = getattr(talib, candle)(op_df, hi_df, lo_df, cl_df)

    result = pd.DataFrame(tech_analysis_df[['Date']+candle_name_list].sum(),columns=['Count'])
    filtered_results = result[result.Count!=0]

    if filtered_results.empty:
        return None,tech_analysis_df
    else:
        return filtered_results[filtered_results.Count == filtered_results.Count.max()].index[0],tech_analysis_df

    return None,tech_analysis_df