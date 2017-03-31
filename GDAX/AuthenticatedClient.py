#
# GDAX/AuthenticatedClient.py
# Daniel Paquin
#
# For authenticated requests to the GDAX exchange

import hmac, hashlib, time, requests, base64, json
from requests.auth import AuthBase
from GDAX.PublicClient import PublicClient

class AuthenticatedClient(PublicClient):
    def __init__(self, key, b64secret, passphrase, api_url="https://api.gdax.com", product_id="BTC-USD"):
        self.url = api_url
        if api_url[-1] == "/":
            self.url = api_url[:-1]
        self.productId = product_id
        self.auth = GdaxAuth(key, b64secret, passphrase)

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
        return list

    def historyPagination(self, accountId, list, after):
        r = requests.get(self.url + '/accounts/%s/ledger?after=%s' %(accountId, str(after)), auth=self.auth)
        if r.json():
            list.append(r.json())
        if "cb-after" in r.headers:
            self.historyPagination(accountId, list, r.headers["cb-after"])
        return list

    def getAccountHolds(self, accountId):
        list = []
        r = requests.get(self.url + '/accounts/%s/holds' %accountId, auth=self.auth)
        list.append(r.json())
        if "cb-after" in r.headers:
            self.holdsPagination(accountId, list, r.headers["cb-after"])
        return list

    def holdsPagination(self, accountId, list, after):
        r = requests.get(self.url + '/accounts/%s/holds?after=%s' %(accountId, str(after)), auth=self.auth)
        if r.json():
            list.append(r.json())
        if "cb-after" in r.headers:
            self.holdsPagination(accountId, list, r.headers["cb-after"])
        return list

    def buy(self, buyParams):
        buyParams["side"] = "buy"
        if not buyParams["product_id"]:
            buyParams["product_id"] = self.productId
        r = requests.post(self.url + '/orders', data=json.dumps(buyParams), auth=self.auth)
        return r.json()

    def sell(self, sellParams):
        sellParams["side"] = "sell"
        r = requests.post(self.url + '/orders', data=json.dumps(sellParams), auth=self.auth)
        return r.json()

    def cancelOrder(self, orderId):
        r = requests.delete(self.url + '/orders/' + orderId, auth=self.auth)
        return r.json()

    def cancelAll(self, data=None, product=''):
        if type(data) is dict:
            if "product" in data: product = data["product"]
        r = requests.delete(self.url + '/orders/', data=json.dumps({'product_id':product or self.productId}), auth=self.auth)
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
        return list

    def paginateOrders(self, list, after):
        r = requests.get(self.url + '/orders?after=%s' %str(after))
        if r.json():
            list.append(r.json())
        if 'cb-after' in r.headers:
            self.paginateOrders(list, r.headers['cb-after'])
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
        return list

    def deposit(self, amount="", accountId=""):
        payload = {
            "type": "deposit",
            "amount": amount,
            "accountId": accountId
        }
        r = requests.post(self.url + "/transfers", data=json.dumps(payload), auth=self.auth)
        return r.json()

    def withdraw(self, amount="", accountId=""):
        payload = {
            "type": "withdraw",
            "amount": amount,
            "accountId": accountId
        }
        r = requests.post(self.url + "/transfers", data=json.dumps(payload), auth=self.auth)
        return r.json()

    def getPaymentMethods(self):
        r = requests.get(self.url + "/payment-methods", auth=self.auth)
        return r.json()

    def getCoinbaseAccounts(self):
        r = requests.get(self.url + "/coinbase-accounts", auth=self.auth)
        return r.json()

    def createReport(self, type="", start_date="", end_date="", product_id="", account_id="", format="", email=""):
        payload = {
            "type": type,
            "start_date": start_date,
            "end_date": end_date,
            "product_id": product_id,
            "account_id": account_id,
            "format": format,
            "email": email
        }
        r = requests.post(self.url + "/reports", data=json.dumps(payload), auth=self.auth)
        return r.json()

    def getReport(self, reportId=""):
        r = requests.get(self.url + "/reports/" + reportId, auth=self.auth)
        return r.json()

    def getTrailingVolume(self):
        r = requests.get(self.url + "/users/self/trailing-volume", auth=self.auth)
        return r.json()

class GdaxAuth(AuthBase):
    # Provided by GDAX: https://docs.gdax.com/#signing-a-message
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or '')
        message = message.encode('ascii')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest())
        request.headers.update({
            'Content-Type': 'Application/JSON',
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase
        })
        return request
