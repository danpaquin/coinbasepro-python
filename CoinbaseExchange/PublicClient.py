#
# CoinbaseExchange/PublicClient.py
# Daniel Paquin
#
# For public requests to the GDAX exchange

import requests

class PublicClient():

    def __init__(self, api_url="https://api.gdax.com", product_id="BTC-USD"):
        self.url = api_url
        #self.product_id = product_id #TODO: Allow a default product

    def getProducts(self):
        response = requests.get(self.url + '/products')
        return response.json()

    def getProductOrderBook(self, level=2):
        response = requests.get(self.url + '/products/BTC-USD/book?level=%s' %str(level))
        return response.json()

    def getProductTicker(self, product='BTC-USD'):
        response = requests.get(self.url + '/products/%s/ticker' %product)
        return response.json()

    def getProductTrades(self, product='BTC-USD'):
        response = requests.get(self.url + '/products/%s/trades' %product)
        return response.json()

    def getProductHistoricRates(self, product='BTC-USD', start='', end='', granularity=''):
        payload = {
            "start" : start,
            "end" : end,
            "granularity" : granularity
        }
        response = requests.get(self.url + '/products/%s/candles' %product, params=payload)
        if 'message' in response.json():
            print "\nERROR:", response.json()['message']
        return response.json()

    def getProduct24HrStats(self):
        response = requests.get(self.url + '/products/BTC-USD/stats')
        return response.json()

    def getCurrencies(self):
        response = requests.get(self.url + '/currencies')
        return response.json()

    def getTime(self):
        response = requests.get(self.url + '/time')
        return response.json()