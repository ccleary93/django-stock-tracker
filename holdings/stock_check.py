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
            if response_json['quoteResponse']['result'][0]['currency'] == 'USD':
                stock_price = response_json['quoteResponse']['result'][0]['regularMarketPrice']
            else:
                for rate in Rate.objects.all():
                    if response_json['quoteResponse']['result'][0]['currency'].lower() == rate.name.lower():
                        stock_price = response_json['quoteResponse']['result'][0]['regularMarketPrice'] / float(rate.rate)
            return stock_price
        except:
            return False

    def update_all(self, holdings):

        # yahoo finance api limits to 10 holdings per call
        querystrings = []
        for i in range(0,len(holdings),10):
            querystring = {"symbols": ','.join(holdings[i:i+10])}
            querystrings.append(querystring)

        headers = {
            'x-api-key': self.yahoo_api_key,
        }

        print(querystrings)

        # add j counter for individual holdings - sits outside querystring loop
        j = 0
        return_dict = {}
        for querystring in querystrings:
            response = requests.request("GET", self.yahoo_url, headers=headers, params=querystring)
            response_json = response.json()
            for result in response_json['quoteResponse']['result']:
                # for equities we must check whether the currency is USD
                if result['quoteType'] == 'EQUITY':
                    if result['financialCurrency'] == 'USD':
                        return_dict[holdings[j]] = result['regularMarketPrice']
                    else:
                        # if not USD check for match against rate object and divide by rate to get USD value
                        for rate in Rate.objects.all():
                            if result['financialCurrency'] == rate.name:
                                return_dict[holdings[j]] = result['regularMarketPrice'] / float(rate.rate)
                # if result is not an equity it should be a rate
                else:
                    return_dict[holdings[j]] = result['regularMarketPrice']
                # increment j
                j += 1
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