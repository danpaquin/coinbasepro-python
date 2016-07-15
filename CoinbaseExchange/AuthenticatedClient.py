#
# CoinbaseExchange/AuthenticatedClient.py
# Daniel Paquin
#
# For authenticated requests to the GDAX exchange

import hmac, hashlib, time, requests, base64
from requests.auth import AuthBase

class CoinbaseExchangeAuth(AuthBase):
    # Provided by Coinbase: https://docs.gdax.com/#signing-a-message
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or '')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature_b64 = signature.digest().encode('base64').rstrip('\n')
        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
        })
        return request

class AuthenticatedClient():
    def __init__(self, key, b64secret, passphrase, api_url="https://api.gdax.com", product_id="BTC-USD"):
        self.url = api_url
        #self.productId = product_id #TODO: Allow a default product
        self.auth = CoinbaseExchangeAuth(key, b64secret, passphrase)

    def getAccount(self, accountId):
        r = requests.get(self.url + '/accounts/' + accountId, auth=self.auth)
        return r.json()

    def getAccounts(self):
        return self.getAccount('')

    def getAccountHistory(self, accountId):
        r = requests.get(self.url + '/accounts/%s/ledger' %accountId, auth=self.auth)
        return r.json()

    def getAccountHolds(self, accountId):
        #TODO: Anticipate pagination
        r = requests.get(self.url + '/accounts/%s/holds' % accountId, auth=self.auth)
        return r.json()

    def buy(self, buyParams):
        buyParams["side"] = "buy"
        r = requests.post(self.url + '/orders', json=buyParams, auth=self.auth)
        return r.json()

    def sell(self, sellParams):
        sellParams["side"] = "sell"
        r = requests.post(self.url + '/orders', json=sellParams, auth=self.auth)
        return r.json()

    def cancelOrder(self, orderId):
        r = requests.delete(self.url + '/orders/' + orderId, auth=self.auth)
        return r.json()

    def getOrder(self, orderId):
        r = requests.get(self.url + '/orders/' + orderId, auth=self.auth)
        return r.json()

    def getOrders(self):
        return self.getOrder("")

    def getFills(self, orderId='', productId='', before='', after='', limit=''):
        url = self.url + '/fills?'
        if orderId: url += "order_id=%s&" %str(orderId)
        if productId: url += "product_id=%s&" %str(productId)

        # TODO: Allow before, after, limit -- not working
        """if before: url += "before=%s&" %str(before)
        if after: url += "after=%s&" %str(after)
        if limit: url += "limit=%s&" %str(limit)"""

        r = requests.get(url, auth=self.auth)
        return r.json()

    def deposit(self, amount="", accountId=""):
        payload = {
            "type": "deposit",
            "amount": amount,
            "accountId": accountId
        }
        r = requests.post(self.url + "/transfers", json=payload, auth=self.auth)
        return r.json()

    def withdraw(self, amount="", accountId=""):
        payload = {
            "type": "withdraw",
            "amount": amount,
            "accountId": accountId
        }
        r = requests.post(self.url + "/transfers", json=payload, auth=self.auth)
        return r.json()