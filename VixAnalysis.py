from hmmlearn import hmm
import plotly.graph_objects as go
import streamlit as st

original_map = {'max': 2, 'mid': 1, 'low': 0}

@st.cache
def GetMood(indval):
    if indval <= 1/3:
        return "Greed"
    elif 1/3 < indval < 2/3:
        return "Holding Steady"
    else:
        return "Fear"

@st.cache
def ProcessVixData(vix_df):
    X = vix_df[['Close']].copy()
    model = hmm.GaussianHMM(n_components=3, covariance_type="full", n_iter=100)
    model.fit(X)
    res = X.copy()
    res['Class'] = model.predict(X)
    resmap = res.groupby('Class').agg({'Close': 'mean'}).sort_values(by='Close')
    resmap = dict(zip(resmap.index, ['low', 'mid', 'max']))
    res['Class_name'] = res.Class.apply(lambda x:resmap[x])
    res['Class_proc'] = res.Class_name.apply(lambda x:original_map[x])
    res['Norm_Class'] = (res['Class_proc']-res['Class_proc'].min())/(res['Class_proc'].max()-res['Class_proc'].min())
    return res

@st.cache
def GetIndicatorChart(res):
    value = res.Norm_Class[-30:].mean()
    fig = go.Figure(go.Indicator(
        domain={'x': [0, 1], 'y': [0, 1]},
        value=value,
        mode="gauge+number",
        title={'text': f"VIX Analysis\nMood : {GetMood(value)}"},
        gauge={'axis': {'range': [None, res.Norm_Class.max()]},
               'steps': [
                   {'range': [0, 1/3], 'color': "green"},
                   {'range': [1/3, 2/3], 'color': "gray"},
                   {'range': [2/3, 1], 'color': "red"}],
               'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': value}}))
    return fig



