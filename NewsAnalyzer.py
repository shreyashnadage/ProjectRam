from pygooglenews import GoogleNews
from transformers import BertTokenizer, BertForSequenceClassification
from transformers import pipeline
import pandas as pd

finbert = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone',num_labels=3)
tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-tone')
nlp = pipeline("sentiment-analysis", model=finbert, tokenizer=tokenizer)

num_top_headlines = 10

gn = GoogleNews(lang='en',country='IN')

def get_headlines(searchterm='Nifty'):
    test = gn.search(searchterm, when='5d')
    newslist = [i['title'] for i in test['entries']]
    return newslist[:num_top_headlines]

def get_sentimental_analysis(newslist):
    results = nlp(newslist)
    df = pd.DataFrame({'headlines': newslist, \
                       'results': [i['label'] for i in results]})
    return df.results.value_counts().sort_values(ascending=False).index[0]

def get_nifty_sentiment():
    newslist = get_headlines()
    return get_sentimental_analysis(newslist)


