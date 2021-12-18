import environ
import requests

# Initialise environment variables
env = environ.Env()
environ.Env.read_env()

class StockCheck():
    def __init__(self):
        self.alpha_api_key = env('API_KEY')

    def price_check(self, ticker):
        print(ticker)
        params = {"function": 'GLOBAL_QUOTE',
                  "symbol": ticker,
                  "apikey": self.alpha_api_key}

        data = requests.get("https://www.alphavantage.co/query", params)
        data_json = data.json()
        print(data_json['Global Quote']['05. price'])
        try:
            stock_price = float(data_json['Global Quote']['05. price'])
            print(stock_price)
            return stock_price
        except:
            return False
