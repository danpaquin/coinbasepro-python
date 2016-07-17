#
# CoinbaseExchange/AuthenticatedClient.py
# Daniel Paquin
#
# For authenticated requests to the GDAX exchange

import hmac, hashlib, time, requests, base64
from requests.auth import AuthBase

class AuthenticatedClient():
    def __init__(self, key, b64secret, passphrase, api_url="https://api.gdax.com", product_id="BTC-USD"):
        self.url = api_url
        self.productId = product_id
        self.auth = CoinbaseExchangeAuth(key, b64secret, passphrase)

    def getAccount(self, accountId):
        r = requests.get(self.url + '/accounts/' + accountId, auth=self.auth)
        return r.json()

    def getAccounts(self):
        return self.getAccount('')

    def getAccountHistory(self, accountId):
        list = []
        r = requests.get(self.url + '/accounts/%s/ledger' %accountId, auth=self.auth)
        list.append(r.json())
        if "cb-after" in r.headers:
            self.historyPagination(accountId, list, r.headers["cb-after"])
        else:
            return list

    def historyPagination(self, accountId, list, after):
        r = requests.get(self.url + '/accounts/%s/ledger?after=%s' %(accountId, str(after)), auth=self.auth)
        if r.json():
            list.append(r.json())
        if "cb-after" in r.headers:
            self.historyPagination(accountId, list, r.headers["cb-after"])
        else:
            return list

    def getAccountHolds(self, accountId):
        list = []
        r = requests.get(self.url + '/accounts/%s/holds' %accountId, auth=self.auth)
        list.append(r.json())
        if "cb-after" in r.headers:
            self.holdsPagination(accountId, list, r.headers["cb-after"])
        else:
            return list

    def holdsPagination(self, accountId, list, after):
        r = requests.get(self.url + '/accounts/%s/holds?after=%s' %(accountId, str(after)), auth=self.auth)
        if r.json():
            list.append(r.json())
        if "cb-after" in r.headers:
            self.holdsPagination(accountId, list, r.headers["cb-after"])
        else:
            return list

    def buy(self, buyParams):
        buyParams["side"] = "buy"
        if not buyParams["product_id"]:
            buyParams["product_id"] = self.productId
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
        list = []
        r = requests.get(self.url + '/orders/', auth=self.auth)
        list.append(r.json())
        if 'cb-after' in r.headers:
            self.paginateOrders(list, r.headers['cb-after'])
        else:
            return list

    def paginateOrders(self, list, after):
        r = requests.get(self.url + '/orders?after=%s' %str(after))
        if r.json():
            list.append(r.json())
        if 'cb-after' in r.headers:
            self.paginateOrders(list, r.headers['cb-after'])
        else:
            return list

    def getFills(self, orderId='', productId='', before='', after='', limit=''):
        list = []
        url = self.url + '/fills?'
        if orderId: url += "order_id=%s&" %str(orderId)
        if productId: url += "product_id=%s&" %(productId or self.productId)
        if before: url += "before=%s&" %str(before)
        if after: url += "after=%s&" %str(after)
        if limit: url += "limit=%s&" %str(limit)
        r = requests.get(url, auth=self.auth)
        list.append(r.json())
        if 'cb-after' in r.headers and limit is not len(r.json()):
            return self.paginateFills(list, r.headers['cb-after'], orderId=orderId, productId=productId)
        else:
            return list

    def paginateFills(self, list, after, orderId='', productId=''):
        url = self.url + '/fills?after=%s&' % str(after)
        if orderId: url += "order_id=%s&" % str(orderId)
        if productId: url += "product_id=%s&" % (productId or self.productId)
        r = requests.get(url, auth=self.auth)
        if r.json():
            list.append(r.json())
        if 'cb-after' in r.headers:
            return self.paginateFills(list, r.headers['cb-after'], orderId=orderId, productId=productId)
        else:
            return list

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