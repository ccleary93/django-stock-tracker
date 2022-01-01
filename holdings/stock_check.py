import environ
import requests
from holdings.models import Rate

# Initialise environment variables
env = environ.Env()
environ.Env.read_env()

class StockCheck():
    def __init__(self):
        self.alpha_api_key = env('API_KEY')
        self.yahoo_api_key = env('YAHOO_API_KEY')
        self.yahoo_url = "https://yfapi.net/v6/finance/quote"

    def price_check(self, ticker):

        querystring = {"symbols": ticker}

        headers = {
            'x-api-key': self.yahoo_api_key,
        }
        print(ticker)
        response = requests.request("GET", self.yahoo_url, headers=headers, params=querystring)
        response_json = response.json()
        try:
            if response_json['quoteResponse']['result'][0]['financialCurrency'] == 'USD':
                stock_price = response_json['quoteResponse']['result'][0]['regularMarketPrice']
            else:
                for rate in Rate.objects.all():
                    if response_json['quoteResponse']['result'][0]['financialCurrency'] == rate.name:
                        stock_price = response_json['quoteResponse']['result'][0]['regularMarketPrice'] / float(rate.rate)
            return stock_price
        except:
            return False

    def update_all(self, holdings):

        querystring = {"symbols": ','.join(holdings)}

        headers = {
            'x-api-key': self.yahoo_api_key,
        }

        response = requests.request("GET", self.yahoo_url, headers=headers, params=querystring)
        response_json = response.json()
        return_dict = {}
        for i in range(len(holdings)):
            if response_json['quoteResponse']['result'][i]['quoteType'] == 'EQUITY':
                if response_json['quoteResponse']['result'][i]['financialCurrency'] == 'USD':
                    return_dict[holdings[i]] = response_json['quoteResponse']['result'][i]['regularMarketPrice']
                else:
                    for rate in Rate.objects.all():
                        if response_json['quoteResponse']['result'][i]['financialCurrency'] == rate.name:
                            return_dict[holdings[i]] = response_json['quoteResponse']['result'][i]['regularMarketPrice'] / float(rate.rate)
            else:
                return_dict[holdings[i]] = response_json['quoteResponse']['result'][i]['regularMarketPrice']
        print(return_dict)
        return return_dict

    def add_rate(self, ticker):

        querystring = {"symbols": ticker}

        headers = {
            'x-api-key': self.yahoo_api_key,
        }
        print(ticker)
        response = requests.request("GET", self.yahoo_url, headers=headers, params=querystring)
        response_json = response.json()
        exchange_rate = response_json['quoteResponse']['result'][0]['regularMarketPrice']
        if exchange_rate:
            return exchange_rate
        return False