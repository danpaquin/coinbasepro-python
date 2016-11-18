#
# GDAX/PublicClient.py
# Daniel Paquin
#
# For public requests to the GDAX exchange

import requests

class PublicClient():
    def __init__(self, api_url="https://api.gdax.com", product_id="BTC-USD"):
        if api_url[-1] == "/":
            self.url = api_url[:-1]
        else:
            self.url = api_url
        self.productId = product_id

    def getProducts(self):
        response = requests.get(self.url + '/products')
        return response.json()

    def getProductOrderBook(self, level=2, product=''):
        response = requests.get(self.url + '/products/%s/book?level=%s' % (product or self.productId, str(level)))
        return response.json()

    def getProductTicker(self, product=''):
        response = requests.get(self.url + '/products/%s/ticker' % (product or self.productId))
        return response.json()

    def getProductTrades(self, product=''):
        response = requests.get(self.url + '/products/%s/trades' % (product or self.productId))
        return response.json()

    def getProductHistoricRates(self, product='', start='', end='', granularity=''):
        payload = {
            "start" : start,
            "end" : end,
            "granularity" : granularity
        }
        response = requests.get(self.url + '/products/%s/candles' % (product or self.productId), params=payload)
        return response.json()

    def getProduct24HrStats(self, product=''):
        response = requests.get(self.url + '/products/%s/stats' % (product or self.productId))
        return response.json()

    def getCurrencies(self):
        response = requests.get(self.url + '/currencies')
        return response.json()

    def getTime(self):
        response = requests.get(self.url + '/time')
        return response.json()