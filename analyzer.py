from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from nltk.sentiment.vader import SentimentIntensityAnalyzer as sid
import pandas as pd
import datetime

newsurl = "https://finviz.com/quote.ashx?t="
tickers = ['NVDA']

tables= {}
for ticker in tickers:
    url = newsurl + ticker
    req = Request(url, headers={'User-Agent':'winOS'},method='GET')
    response = urlopen(req)

    html = BeautifulSoup(response,'html.parser')
    news_table = html.find(id='news-table')
    tables[ticker] = news_table

parsed_data = []
for ticker, value in tables.items():
    rows = value.find_all('tr')

    for row in rows:
        title= row.a.text
        date_time = row.td.text.strip().split(' ')

        if len(date_time) == 1:
            time = date_time[0]
        else:
            date = date_time[0]
            time = date_time[1]

        parsed_data.append([ticker,date,time,title])
    
df = pd.DataFrame(parsed_data, columns=['ticker','date','time','title'])

valid_date = []
for date in df['date']:
    if date == "Today":
        date = datetime.date.today()
    valid_date.append(date)
    
df['date'] = valid_date
df['date'] = pd.to_datetime(df['date'])

vader = sid()
score = lambda title: vader.polarity_scores(title)['compound']
df['compound'] = df['title'].apply(score)

mean_df = df.groupby(['ticker','date']).mean(numeric_only=True)
mean_df = mean_df.unstack()
mean_df = mean_df.xs('compound',axis='columns').transpose()  
mean_df.plot(kind='line')
