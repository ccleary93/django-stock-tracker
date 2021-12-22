import environ
import requests

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
            stock_price = float(response_json['quoteResponse']['result'][0]['regularMarketPrice'])
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
            return_dict[holdings[i]] = response_json['quoteResponse']['result'][i]['regularMarketPrice']
        print(return_dict)
        return return_dict