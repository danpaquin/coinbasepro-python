#
# gdax/AuthenticatedClient.py
# Daniel Paquin
#
# For authenticated requests to the gdax exchange

import hmac
import hashlib
import time
import requests
import base64
import json
from requests.auth import AuthBase
from gdax.public_client import PublicClient
from gdax.gdax_auth import GdaxAuth


class AuthenticatedClient(PublicClient):
    def __init__(self, key, b64secret, passphrase, api_url="https://api.gdax.com", timeout=30):
        super(AuthenticatedClient, self).__init__(api_url)
        self.auth = GdaxAuth(key, b64secret, passphrase)
        self.timeout = timeout

    def get_account(self, account_id):
        r = requests.get(self.url + '/accounts/' + account_id, auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def get_accounts(self):
        return self.get_account('')

    def get_account_history(self, account_id):
        result = []
        r = requests.get(self.url + '/accounts/{}/ledger'.format(account_id), auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        result.append(r.json())
        if "cb-after" in r.headers:
            self.history_pagination(account_id, result, r.headers["cb-after"])
        return result

    def history_pagination(self, account_id, result, after):
        r = requests.get(self.url + '/accounts/{}/ledger?after={}'.format(account_id, str(after)), auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        if r.json():
            result.append(r.json())
        if "cb-after" in r.headers:
            self.history_pagination(account_id, result, r.headers["cb-after"])
        return result

    def get_account_holds(self, account_id):
        result = []
        r = requests.get(self.url + '/accounts/{}/holds'.format(account_id), auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        result.append(r.json())
        if "cb-after" in r.headers:
            self.holds_pagination(account_id, result, r.headers["cb-after"])
        return result

    def holds_pagination(self, account_id, result, after):
        r = requests.get(self.url + '/accounts/{}/holds?after={}'.format(account_id, str(after)), auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        if r.json():
            result.append(r.json())
        if "cb-after" in r.headers:
            self.holds_pagination(account_id, result, r.headers["cb-after"])
        return result

    def buy(self, **kwargs):
        kwargs["side"] = "buy"
        if "product_id" not in kwargs:
            kwargs["product_id"] = self.product_id
        r = requests.post(self.url + '/orders',
                          data=json.dumps(kwargs),
                          auth=self.auth,
                          timeout=self.timeout)
        return r.json()

    def sell(self, **kwargs):
        kwargs["side"] = "sell"
        r = requests.post(self.url + '/orders',
                          data=json.dumps(kwargs),
                          auth=self.auth,
                          timeout=self.timeout)
        return r.json()

    def cancel_order(self, order_id):
        r = requests.delete(self.url + '/orders/' + order_id, auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def cancel_all(self, product_id=''):
        url = self.url + '/orders/'
        params = {}
        if product_id:
            params["product_id"] = product_id
        r = requests.delete(url, auth=self.auth, params=params, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def get_order(self, order_id):
        r = requests.get(self.url + '/orders/' + order_id, auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def get_orders(self, product_id='', status=[]):
        result = []
        url = self.url + '/orders/'
        params = {}
        if product_id:
            params["product_id"] = product_id
        if status:
            params["status"] = status
        r = requests.get(url, auth=self.auth, params=params, timeout=self.timeout)
        # r.raise_for_status()
        result.append(r.json())
        if 'cb-after' in r.headers:
            self.paginate_orders(product_id, status, result, r.headers['cb-after'])
        return result

    def paginate_orders(self, product_id, status, result, after):
        url = self.url + '/orders'

        params = {
            "after": str(after),
        }
        if product_id:
            params["product_id"] = product_id
        if status:
            params["status"] = status
        r = requests.get(url, auth=self.auth, params=params, timeout=self.timeout)
        # r.raise_for_status()
        if r.json():
            result.append(r.json())
        if 'cb-after' in r.headers:
            self.paginate_orders(product_id, status, result, r.headers['cb-after'])
        return result

    def get_fills(self, order_id='', product_id='', before='', after='', limit=''):
        result = []
        url = self.url + '/fills?'
        if order_id:
            url += "order_id={}&".format(str(order_id))
        if product_id:
            url += "product_id={}&".format(product_id)
        if before:
            url += "before={}&".format(str(before))
        if after:
            url += "after={}&".format(str(after))
        if limit:
            url += "limit={}&".format(str(limit))
        r = requests.get(url, auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        result.append(r.json())
        if 'cb-after' in r.headers and limit is not len(r.json()):
            return self.paginate_fills(result, r.headers['cb-after'], order_id=order_id, product_id=product_id)
        return result

    def paginate_fills(self, result, after, order_id='', product_id=''):
        url = self.url + '/fills?after={}&'.format(str(after))
        if order_id:
            url += "order_id={}&".format(str(order_id))
        if product_id:
            url += "product_id={}&".format(product_id)
        r = requests.get(url, auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        if r.json():
            result.append(r.json())
        if 'cb-after' in r.headers:
            return self.paginate_fills(result, r.headers['cb-after'], order_id=order_id, product_id=product_id)
        return result

    def get_fundings(self, result='', status='', after=''):
        if not result:
            result = []
        url = self.url + '/funding?'
        if status:
            url += "status={}&".format(str(status))
        if after:
            url += 'after={}&'.format(str(after))
        r = requests.get(url, auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        result.append(r.json())
        if 'cb-after' in r.headers:
            return self.get_fundings(result, status=status, after=r.headers['cb-after'])
        return result

    def repay_funding(self, amount='', currency=''):
        payload = {
            "amount": amount,
            "currency": currency  # example: USD
        }
        r = requests.post(self.url + "/funding/repay", data=json.dumps(payload), auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def margin_transfer(self, margin_profile_id="", transfer_type="", currency="", amount=""):
        payload = {
            "margin_profile_id": margin_profile_id,
            "type": transfer_type,
            "currency": currency,  # example: USD
            "amount": amount
        }
        r = requests.post(self.url + "/profiles/margin-transfer", data=json.dumps(payload), auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def get_position(self):
        r = requests.get(self.url + "/position", auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def close_position(self, repay_only=""):
        payload = {
            "repay_only": repay_only or False
        }
        r = requests.post(self.url + "/position/close", data=json.dumps(payload), auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def deposit(self, amount="", currency="", payment_method_id=""):
        payload = {
            "amount": amount,
            "currency": currency,
            "payment_method_id": payment_method_id
        }
        r = requests.post(self.url + "/deposits/payment-method", data=json.dumps(payload), auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def coinbase_deposit(self, amount="", currency="", coinbase_account_id=""):
        payload = {
            "amount": amount,
            "currency": currency,
            "coinbase_account_id": coinbase_account_id
        }
        r = requests.post(self.url + "/deposits/coinbase-account", data=json.dumps(payload), auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def withdraw(self, amount="", currency="", payment_method_id=""):
        payload = {
            "amount": amount,
            "currency": currency,
            "payment_method_id": payment_method_id
        }
        r = requests.post(self.url + "/withdrawals/payment-method", data=json.dumps(payload), auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def coinbase_withdraw(self, amount="", currency="", coinbase_account_id=""):
        payload = {
            "amount": amount,
            "currency": currency,
            "coinbase_account_id": coinbase_account_id
        }
        r = requests.post(self.url + "/withdrawals/coinbase", data=json.dumps(payload), auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def crypto_withdraw(self, amount="", currency="", crypto_address=""):
        payload = {
            "amount": amount,
            "currency": currency,
            "crypto_address": crypto_address
        }
        r = requests.post(self.url + "/withdrawals/crypto", data=json.dumps(payload), auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def get_payment_methods(self):
        r = requests.get(self.url + "/payment-methods", auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def get_coinbase_accounts(self):
        r = requests.get(self.url + "/coinbase-accounts", auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def create_report(self, report_type="", start_date="", end_date="", product_id="", account_id="", report_format="",
                      email=""):
        payload = {
            "type": report_type,
            "start_date": start_date,
            "end_date": end_date,
            "product_id": product_id,
            "account_id": account_id,
            "format": report_format,
            "email": email
        }
        r = requests.post(self.url + "/reports", data=json.dumps(payload), auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def get_report(self, report_id=""):
        r = requests.get(self.url + "/reports/" + report_id, auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def get_trailing_volume(self):
        r = requests.get(self.url + "/users/self/trailing-volume", auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()
