#
# GDAX/AuthenticatedClient.py
# Daniel Paquin
#
# For authenticated requests to the GDAX exchange

import hmac
import hashlib
import time
import requests
import base64
import json
from requests.auth import AuthBase
from gdax.public_client import PublicClient


class AuthenticatedClient(PublicClient):
    def __init__(self, key, b64secret, passphrase,
                 api_url="https://api.gdax.com"):
        super(self.__class__, self).__init__(api_url)
        self.auth = GdaxAuth(key, b64secret, passphrase)
        self.session = requests.Session()

    def get_account(self, account_id):
        return self._send_message('get', '/accounts/' + account_id)

    def get_accounts(self):
        return self.get_account('')

    def get_account_history(self, account_id, **kwargs):
        endpoint = '/accounts/{}/ledger'.format(account_id)
        return self._send_message('get', endpoint, params=kwargs)[0]

    def get_account_holds(self, account_id, **kwargs):
        endpoint = '/accounts/{}/holds'.format(account_id)
        return self._send_message('get', endpoint, params=kwargs)[0]

    def place_order(self, product_id, side, order_type, **kwargs):
        # Margin parameter checks
        if kwargs.get('overdraft_enabled') is not None and \
                        kwargs.get('funding_amount') is not None:
            raise ValueError('Margin funding must be specified through use of '
                             'overdraft or by setting a funding amount, but not'
                             ' both')

        # Limit order checks
        if order_type == 'limit':
            if kwargs.get('cancel_after') is not None and \
                            kwargs.get('tif') != 'GTT':
                raise ValueError('May only specify a cancel period when time '
                                 'in_force is `GTT`')
            if kwargs.get('post_only') is not None and kwargs.get('tif') in \
                    ['IOC', 'FOK']:
                raise ValueError('post_only is invalid when time in force is '
                                 '`IOC` or `FOK`')

        # Market and stop order checks
        if order_type == 'market' or order_type == 'stop':
            if not (kwargs.get('size') is None) ^ (kwargs.get('funds') is None):
                raise ValueError('Either `size` or `funds` must be specified '
                                 'for market/stop orders (but not both).')

        # Build params dict
        params = {'product_id': product_id,
                  'side': side,
                  'type': order_type
                  }
        params.update(kwargs)
        return self._send_message('post', '/orders', data=json.dumps(params))

    def place_limit_order(self, product_id, side, price, size,
                          client_oid=None,
                          stp=None,
                          tif=None,
                          cancel_after=None,
                          post_only=None,
                          overdraft_enabled=None,
                          funding_amount=None):
        params = {'product_id': product_id,
                  'side': side,
                  'order_type': 'limit',
                  'price': price,
                  'size': size,
                  'client_oid': client_oid,
                  'stp': stp,
                  'tif': tif,
                  'cancel_after': cancel_after,
                  'post_only': post_only,
                  'overdraft_enabled': overdraft_enabled,
                  'funding_amount': funding_amount}
        params = dict((k, v) for k, v in params.items() if v is not None)

        return self.place_order(**params)

    def place_market_order(self, product_id, side, size, funds,
                           client_oid=None,
                           stp=None,
                           overdraft_enabled=None,
                           funding_amount=None):
        params = {'product_id': product_id,
                  'side': side,
                  'order_type': 'market',
                  'size': size,
                  'funds': funds,
                  'client_oid': client_oid,
                  'stp': stp,
                  'overdraft_enabled': overdraft_enabled,
                  'funding_amount': funding_amount}
        params = dict((k, v) for k, v in params.items() if v is not None)

        return self.place_order(**params)

    def place_stop_order(self, product_id, side, price, size, funds,
                         client_oid=None,
                         stp=None,
                         overdraft_enabled=None,
                         funding_amount=None):
        params = {'product_id': product_id,
                  'side': side,
                  'price': price,
                  'order_type': 'stop',
                  'size': size,
                  'funds': funds,
                  'client_oid': client_oid,
                  'stp': stp,
                  'overdraft_enabled': overdraft_enabled,
                  'funding_amount': funding_amount}
        params = dict((k, v) for k, v in params.items() if v is not None)

        return self.place_order(**params)

    def cancel_order(self, order_id):
        return self._send_message('delete', '/orders/' + order_id)

    def cancel_all(self, product_id=None):
        if product_id is not None:
            params = {'product_id': product_id}
            data = json.dumps(params)
        else:
            data = None
        return self._send_message('delete', '/orders', data=data)

    def get_order(self, order_id):
        return self._send_message('get', '/orders/' + order_id)

    def get_orders(self, **kwargs):
        return self._send_message('get', '/orders', params=kwargs)[0]

    def get_fills(self, product_id=None, order_id=None, **kwargs):
        params = {}
        if product_id:
            params['product_id'] = product_id
        if order_id:
            params['order_id'] = order_id
        params.update(kwargs)

        # Return `after` param so client can access more recent fills on next
        # call of get_fills if desired.
        message, r = self._send_message('get', '/fills', params=params)
        return r.headers['cb-after'], message

    def get_fundings(self, status=None, **kwargs):
        params = {}
        if status is not None:
            params['status'] = status
        params.update(kwargs)
        return self._send_message('get', '/funding', params=params)[0]

    def repay_funding(self, amount, currency):
        params = {
            'amount': amount,
            'currency': currency  # example: USD
            }
        return self._send_message('post', '/funding/repay',
                                  data=json.dumps(params))

    def margin_transfer(self, margin_profile_id, transfer_type, currency,
                        amount):
        params = {
            'margin_profile_id': margin_profile_id,
            'type': transfer_type,
            'currency': currency,  # example: USD
            'amount': amount
        }
        return self._send_message('post', '/profiles/margin-transfer',
                                  data=json.dumps(params))

    def get_position(self):
        return self._send_message('get', '/position')[0]

    def close_position(self, repay_only):
        params = {'repay_only': repay_only}
        return self._send_message('post', '/position/close',
                                  data=json.dumps(params))[0]

    def deposit(self, amount, currency, payment_method_id):
        params = {
            'amount': amount,
            'currency': currency,
            'payment_method_id': payment_method_id
        }
        return self._send_message('post', '/deposits/payment-method',
                                  data=json.dumps(params))[0]

    def coinbase_deposit(self, amount, currency, coinbase_account_id):
        params = {
            'amount': amount,
            'currency': currency,
            'coinbase_account_id': coinbase_account_id
        }
        return self._send_message('post', '/deposits/coinbase-account',
                                  data=json.dumps(params))[0]

    def withdraw(self, amount, currency, payment_method_id):
        params = {
            'amount': amount,
            'currency': currency,
            'payment_method_id': payment_method_id
        }
        return self._send_message('post', '/withdrawals/payment-method',
                                  data=json.dumps(params))[0]

    def coinbase_withdraw(self, amount, currency, coinbase_account_id):
        params = {
            'amount': amount,
            'currency': currency,
            'coinbase_account_id': coinbase_account_id
        }
        return self._send_message('post', '/withdrawals/coinbase',
                                  data=json.dumps(params))[0]

    def crypto_withdraw(self, amount, currency, crypto_address):
        params = {
            'amount': amount,
            'currency': currency,
            'crypto_address': crypto_address
        }
        return self._send_message('post', '/withdrawals/crypto',
                                  data=json.dumps(params))[0]

    def get_payment_methods(self):
        return self._send_message('get', '/payment-methods')[0]

    def get_coinbase_accounts(self):
        return self._send_message('get', '/coinbase-accounts')[0]

    def create_report(self, report_type, start_date, end_date, product_id=None,
                      account_id=None, report_format='pdf', email=None):
        params = {
            'type': report_type,
            'start_date': start_date,
            'end_date': end_date,
            'format': report_format,
        }
        if product_id is not None:
            params['product_id'] = product_id
        if account_id is not None:
            params['account_id'] = account_id
        if email is not None:
            params['email'] = email

        return self._send_message('post', '/reports',
                                  data=json.dumps(params))[0]

    def get_report(self, report_id):
        return self._send_message('get', '/reports/' + report_id)[0]

    def get_trailing_volume(self):
        return self._send_message('get', '/users/self/trailing-volume')[0]

    def _send_message(self, method, endpoint, params=None, data=None):
        """Get a paginated response by making multiple http requests.

        Args:
            method (str): HTTP method (get, post, delete, etc.)
            endpoint (str): Endpoint (to be added to base URL)
            params (Optional[dict]): HTTP request parameters
            data (Optional[str]): JSON-encoded string payload for POST

        Returns:
            list: Merged responses from paginated requests
            requests.models.Response: Response object from last HTTP
                response

        """
        if params is None:
            params = {}
        response_data = []
        url = self.url + endpoint
        r = self.session.request(method, url, params=params, data=data,
                                 auth=self.auth)
        if r.json():
            response_data = r.json()
        if method == 'get':
            while 'cb-after' in r.headers:
                params['after'] = r.headers['cb-after']
                r = self.session.get(url, params=params, auth=self.auth)
                if r.json():
                    response_data += r.json()
        return response_data, r


class GdaxAuth(AuthBase):
    # Provided by GDAX: https://docs.gdax.com/#signing-a-message
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + \
                  (request.body or '')
        message = message.encode('ascii')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest())
        request.headers.update({
            'Content-Type': 'Application/json',
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase
        })
        return request
