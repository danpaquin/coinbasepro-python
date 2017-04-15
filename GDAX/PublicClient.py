#
# GDAX/PublicClient.py
# Daniel Paquin
#
# For public requests to the GDAX exchange

import requests

class PublicClient():
    def __init__(self, api_url="https://api.gdax.com", product_id="BTC-USD"):
        self.url = api_url
        if api_url[-1] == "/":
            self.url = api_url[:-1]
        self.productId = product_id

    def getProducts(self):
        r = requests.get(self.url + '/products')
        r.raise_for_status()
        return r.json()

    def getProductOrderBook(self, json=None, level=2, product=''):
        if type(json) is dict:
            if "product" in json: product = json["product"]
            if "level" in json: level = json['level']
        r = requests.get(self.url + '/products/%s/book?level=%s' % (product or self.productId, str(level)))
        r.raise_for_status()
        return r.json()

    def getProductTicker(self, json=None, product=''):
        if type(json) is dict:
            if "product" in json: product = json["product"]
        r = requests.get(self.url + '/products/%s/ticker' % (product or self.productId))
        r.raise_for_status()
        return r.json()

    def getProductTrades(self, json=None, product=''):
        if type(json) is dict:
            if "product" in json: product = json["product"]
        r = requests.get(self.url + '/products/%s/trades' % (product or self.productId))
        r.raise_for_status()
        return r.json()

    def getProductHistoricRates(self, json=None, product='', start='', end='', granularity=''):
        payload = {}
        if type(json) is dict:
            if "product" in json: product = json["product"]
            payload = json
        else:
            payload["start"] = start
            payload["end"] = end
            payload["granularity"] = granularity
        r = requests.get(self.url + '/products/%s/candles' % (product or self.productId), params=payload)
        r.raise_for_status()
        return r.json()

    def getProduct24HrStats(self, json=None, product=''):
        if type(json) is dict:
            if "product" in json: product = json["product"]
        r = requests.get(self.url + '/products/%s/stats' % (product or self.productId))
        r.raise_for_status()
        return r.json()

    def getCurrencies(self):
        r = requests.get(self.url + '/currencies')
        r.raise_for_status()
        return r.json()

    def getTime(self):
        r = requests.get(self.url + '/time')
        r.raise_for_status()
        return r.json()
