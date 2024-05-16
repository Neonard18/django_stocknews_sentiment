import yfinance as yf
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request


symbols= ['TSLA','META']
stock_data = []
for symbol in symbols:
    ticker = yf.Ticker(symbol)
    hist1 = ticker.history(period='5d')['Close'].iloc[-1]
    hist2 = ticker.history(period='5d')['Close'].iloc[-2]
    day_change = hist1 - hist2
    percent_change = day_change * 100 /hist2
    metadata = ticker.history_metadata
    info = ticker.fast_info['market_cap']

    
    # stock_data['ticker'] = symbol
    # stock_data['close'] = round(hist1,2)
    # stock_data['per_chg'] = percent_change
    # stock_data['cap'] = info

    stock_data.append({symbol:{'symbol':symbol,'close':round(hist1,2),'per_chg':round(percent_change,2),'Cap':f'{info:,.2f}'}})

# print(stock_data)
def get_stock_data(symbol):
    ticker = yf.Ticker(symbol)
    info = ticker.get_info()
    print(info)

get_stock_data('AAPL')