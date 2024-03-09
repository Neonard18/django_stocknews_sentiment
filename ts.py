from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from urllib.error import URLError
import pandas as pd
import datetime
from nltk.sentiment.vader import SentimentIntensityAnalyzer as sid
import matplotlib.pyplot as plt

newsurl = "https://finviz.com/quote.ashx?t="
tickers = ['META','NFLX','KO']

tables = {}
for ticker in tickers:
    try:
        url = newsurl + ticker
        request= Request(url, headers={'User-Agent':'winOS'})
        response = urlopen(request)

        html = BeautifulSoup(response, 'html.parser')

        news_table = html.find(id='news-table')
        tables[ticker] = news_table
    except URLError as e:
        print(e.reason)
        break
    

parsed_data = []
try: 
    for ticker, table in tables.items():
        rows = table.find_all('tr')
        
        for row in rows:
            title = row.a.text
            date_time = row.td.text.strip().split()

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
    df['date'] = pd.to_datetime(df['date']).dt.date

    vader = sid()

    compound = lambda title: vader.polarity_scores(title)['compound']
    df['compound'] = df['title'].apply(compound)

    mean_groupby = df.groupby(['ticker','date'])
    mean_df = mean_groupby.mean(numeric_only=True)
    mean_df.to_excel('stack.xlsx')
    mean_df = mean_df.unstack()      #fin


    mean_df = mean_df.xs('compound',axis='columns').transpose()     #find out about the unstack
    
    # kind: bar,line, barh
    fig = mean_df.plot(kind='bar',title='Stock News Sentiment Analysis')


    fig.figure.savefig('graph.png')
    plt.xticks(rotation=30)
    plt.show()

except KeyError as k:
    print(k.__cause__)
