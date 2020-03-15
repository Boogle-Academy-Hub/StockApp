from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, QueryDict, HttpResponseRedirect, Http404, JsonResponse
import requests
import pandas as pd
from datetime import datetime
# from stocks import app, db
# from stocks.models import StockPrice
from .models import StockPrice
# from flask import request, jsonify, render_template, Response
from bs4 import BeautifulSoup
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, NumeralTickFormatter
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn
from bokeh.layouts import widgetbox
from bokeh.embed import components

# Create your views here.

def live_price(request):

	ticker = request.GET.get('ticker', None)
	context_data = {'ticker' : ticker}
	if ticker is None:
		return render(request=request, template_name='live_price.html', context=context_data)

	url = 'http://quotes.wsj.com/{}'.format(ticker)
	# https://www.wsj.com/market-data/quotes/AAPL
	r = requests.get('https://www.wsj.com/market-data/quotes/AAPL')
	soup = BeautifulSoup(r.content, 'html.parser')
	return HttpResponse(content=r.text, content_type="text/html")
	try:
		realtime_price_el = soup.find('span', attrs={'id': 'quote_val'})
		return HttpResponse(content=realtime_price_el, content_type="application/json")
		range_el = soup.find('ul', attrs={'class': 'cr_charts_info'})\
					.find_all('li')[2]\
					.find('span', attrs={'class': 'data_data'})
	except AttributeError:
		realtime_price = None
		open_price = None
		close_price = None
	else:
		if realtime_price_el is not None:
			realtime_price = float(realtime_price_el.text.replace(',', ''))
		else:
			realtime_price = None
		if range_el is not None:
			prices = range_el.text.split(' - ')
			open_price = float(prices[0].replace(',', ''))
			close_price = float(prices[1].replace(',', ''))
		else:
			open_price = None
			close_price = None

		prices = StockPrice(ticker=ticker.upper(), open_price=open_price, close_price=close_price, realtime_price=realtime_price, created_at=datetime.now())
		# db.session.add(prices)
		# db.session.commit()
	context = {
			'ticker' : ticker.upper(),
			'open_price' : open_price,
			'close_price' : close_price,
			'realtime_price' : realtime_price
		}
	return render(request=request , template_name='live_price.html', context=context)

def trading_volume(request):
    	
	# return HttpResponse(content=request.GET.get, content_type="application/json")
	# ticker = None if request.GET['ticker'] == None else request.GET['ticker']
	ticker = request.GET.get('ticker', '')
	# time_range = None if request.GET['range'] == None else request.GET['range']
	time_range = request.GET.get('range', '')
	time_range_options = ["Daily", "Weekly", "Monthly"]
	
	context = {
        'ticker' : ticker,
        'time_range' : time_range,
        'time_range_options' : time_range_options,
    }

	if ticker is None or time_range is None:
    		return render(request=request, template_name='trading_volume.html', context=context)

	url = 'https://www.alphavantage.co/query?function=TIME_SERIES_{}&symbol={}&apikey=6IPKGXBQSR1WLQUK'.format(time_range.upper(), ticker.upper())
	res = requests.get(url)
	data = res.json()
	
	key_dict = {
		"Daily" : "Time Series (Daily)",
		"Weekly" : "Weekly Time Series",
		"Monthly" : "Monthly Time Series",
	}

	try:
		df = pd.DataFrame.from_dict(data[key_dict[time_range]], orient='index')
	except KeyError:
		script = None
		div = None
		time_range = None
	else:
		df['date'] = pd.to_datetime(df.index)
		source = ColumnDataSource(data=df)

		ticker = ticker.upper()
		p = figure(plot_width=800, plot_height=500, x_axis_type="datetime")
		p.title.text = "{} Trading Volume for {}".format(time_range, ticker)
		p.line(x='date', y='5. volume', source=source)
		p.yaxis[0].formatter = NumeralTickFormatter(format="0.0a")

		script, div = components(p)

		context = {
			'script' : script,
			'div' : div, 
			'ticker' : ticker, 
			'time_range' : time_range,
			'time_range_options' : time_range_options
		}

	return render(request=request, template_name='trading_volume.html', context=context)

def price_history(request):
    
	query = StockPrice.objects.all()

	# return HttpResponse(content=query[0].ticker, content_type='text/html')

	df = pd.DataFrame(data=query)
	# df = pd.read_sql(query.statement, query.session.bind)
	# df.sort_values('created_at', ascending=False, inplace=True)
	source = ColumnDataSource(df)

	columns = [
	        # TableColumn(field="created_at", title="Created At", formatter=DateFormatter(format="%F %T")),
	        TableColumn(field="ticker", title="Ticker"),
	        TableColumn(field="open_price", title="Open Price"),
	        TableColumn(field="close_price", title="Close Price"),
	        TableColumn(field="realtime_price", title="Real Time Price"),
	    ]
	data_table = DataTable(source=source, columns=columns, width=800, height=280)
	script, div = components(widgetbox(data_table))

	context_data = {
		'script' : script,
		'div'	 : div
	}
	return render(request=request, template_name='price_history.html', context=context_data)

def price_json(request):
	ticker = request.GET.get('ticker', None)
	if ticker is None:
		return "No ticker provided"

	res = {}

	# scrape website
	r = requests.get('http://quotes.wsj.com/{}'.format(ticker))
	soup = BeautifulSoup(r.content, 'html.parser')

	real_time_el = soup.find('span', attrs={'id': 'quote_val'})
	
	range_el = soup.find('ul', attrs={'class': 'cr_charts_info'})\
				.find_all('li')[2]\
				.find('span', attrs={'class': 'data_data'})

	if real_time_el is not None:
		res['real_time'] = float(real_time_el.text)
	else:
		res['real_time'] = None
	if range_el is not None:
		prices = range_el.text.split(' - ')
		res['open_price'] = float(prices[0])
		res['close_price'] = float(prices[1])
	else:
		res['open_price'] = None
		res['close_price'] = None

	return JsonResponse(res)