from nsetools import Nse
import pandas as pd
from collections import OrderedDict

nse = Nse()

def GetTopLosers():
    try:
        top5losers = nse.get_top_losers()[:5]
        data = OrderedDict({'Symbol': [i['symbol'] for i in top5losers], '%Change': [str(i['netPrice'])+'%' for i in top5losers]})
        return pd.DataFrame(data).set_index('Symbol')
    except:
        return None

def GetTopGainers():
    try:
        top5gainers = nse.get_top_gainers()[:5]
        data = OrderedDict({'Symbol': [i['symbol'] for i in top5gainers], '%Change': [str(i['netPrice'])+'%' for i in top5gainers]})
        return pd.DataFrame(data).set_index('Symbol')
    except:
        return None
