from django.shortcuts import render
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import WatchList, User, Plotting
from .serializers import WatchListSerializer, AdminUserSerializer, UserSerializer, PlottingSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError
from urllib.request import urlopen, Request
from urllib.error import URLError
import pandas as pd
import datetime
import os
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer as sid
import matplotlib.pyplot as plt
import yfinance as yf
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from io import BytesIO
import threading

# Create your views here.
class WatchListViewSet(viewsets.ModelViewSet):
    queryset = WatchList.objects.all()
    serializer_class = WatchListSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        queryset = WatchList.objects.filter(user=request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.POST)

            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data,status.HTTP_201_CREATED)
        except IntegrityError as e:
            msg = {'msg': f'You already have {request.POST["symbol"]} in your watchlist'}
            return Response(msg,status.HTTP_409_CONFLICT)
        

class AdminUserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=['GET'])
    def get_stock_data(self, request, pk):
        stock_data = []
        user = get_object_or_404(User, pk=pk)
        watchlists = WatchList.objects.filter(user=user.id)
        try:
            for watchlist in watchlists:
                news_title = []
                ticker = yf.Ticker(watchlist.symbol)
                news = ticker.news
                for info in news:
                    news_title.append(info['title'])
                hist1 = ticker.history(period='5d')['Close'].iloc[4]
                hist2 = ticker.history(period='5d')['Close'].iloc[3]
                day_change = hist1 - hist2
                percent_change = day_change * 100 /hist2
                info = ticker.fast_info['market_cap']

                stock_data.append({'symbol':watchlist.symbol,'close':round(hist1,2),'per_chg':f'{round(percent_change,2)}%','Cap':f'{info:,.2f}','news':news_title})


            return Response({'Data':stock_data},status.HTTP_200_OK)
        except Exception as e:
            return Response({'Data':'Connection Failed'},status.HTTP_404_NOT_FOUND)


    @action(detail=True, methods=['GET'])
    def plot_stock_data(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        watchlists = WatchList.objects.filter(user=user.id)

        newsurl = "https://finviz.com/quote.ashx?t="

        tables = {}
        for watchlist in watchlists:
            try:
                url = newsurl + watchlist.symbol
                request= Request(url, headers={'User-Agent':'winOS'})
                response = urlopen(request)

                html = BeautifulSoup(response, 'html.parser')

                news_table = html.find(id='news-table')
                tables[watchlist.symbol] = news_table
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
            mean_df = mean_df.unstack()     


            mean_df = mean_df.xs('compound',axis='columns').transpose()     #find out about the unstack
            
            lock = threading.Lock()
            with lock:
                # kind: bar,line, barh
                figure = Figure()
                ax = figure.add_subplot(111)

                fig = mean_df.plot(kind='bar',title='Stock News Sentiment Analysis',ax=ax)

                script_dir = os.path.dirname(__file__)
                parent_dir = os.path.dirname(script_dir)
                static_dir = os.path.join(parent_dir,'static/')
                file_name = 'graph.png'

                if not os.path.isdir(static_dir):
                    os.makedirs(static_dir)
                
                # plt.xticks(rotation=90)
                fig.figure.savefig(static_dir + file_name)

            plotting = Plotting(plot= '/static/graph.png', user=user)
            plotting.save()
            return Response({'data':'Plotted'},status.HTTP_200_OK)    

        except KeyError as k:
            print(k.__cause__)


class PlottingViewSet(viewsets.ModelViewSet):
    queryset = Plotting.objects.all()
    serializer_class = PlottingSerializer
    authentication_classes = (TokenAuthentication,)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.POST)

        if serializer.is_valid():
            serializer.save(user= request.user)
        return Response('Created',status.HTTP_201_CREATED)


            