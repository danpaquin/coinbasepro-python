#
# GDAX/PublicClient.py
# Daniel Paquin
#
# For public requests to the GDAX exchange

import requests


class PublicClient(object):
    def __init__(self, api_url="https://api.gdax.com", product_id="BTC-USD"):
        self.url = api_url.rstrip("/")
        self.product_id = product_id

    def get_products(self):
        r = requests.get(self.url + '/products')
        # r.raise_for_status()
        return r.json()

    def get_product_order_book(self, json=None, level=2, product=''):
        if type(json) is dict:
            if "product" in json:
                product = json["product"]
            if "level" in json:
                level = json['level']
        r = requests.get(self.url + '/products/%s/book?level=%s' % (product or self.product_id, str(level)))
        # r.raise_for_status()
        return r.json()

    def get_product_ticker(self, json=None, product=''):
        if type(json) is dict:
            if "product" in json:
                product = json["product"]
        r = requests.get(self.url + '/products/%s/ticker' % (product or self.product_id))
        # r.raise_for_status()
        return r.json()

    def get_product_trades(self, json=None, product=''):
        if type(json) is dict:
            if "product" in json:
                product = json["product"]
        r = requests.get(self.url + '/products/%s/trades' % (product or self.product_id))
        # r.raise_for_status()
        return r.json()

    def get_product_historic_rates(self, json=None, product='', start='', end='', granularity=''):
        payload = {}
        if type(json) is dict:
            if "product" in json:
                product = json["product"]
            payload = json
        else:
            payload["start"] = start
            payload["end"] = end
            payload["granularity"] = granularity
        r = requests.get(self.url + '/products/%s/candles' % (product or self.product_id), params=payload)
        # r.raise_for_status()
        return r.json()

    def get_product_24hr_stats(self, json=None, product=''):
        if type(json) is dict:
            if "product" in json:
                product = json["product"]
        r = requests.get(self.url + '/products/%s/stats' % (product or self.product_id))
        # r.raise_for_status()
        return r.json()

    def get_currencies(self):
        r = requests.get(self.url + '/currencies')
        # r.raise_for_status()
        return r.json()

    def get_time(self):
        r = requests.get(self.url + '/time')
        # r.raise_for_status()
        return r.json()
