#!/usr/bin/env python

import gdax
from gdax_config import settings
import pytest

@pytest.fixture(scope='module')
def gdax_client():
    return gdax.AuthenticatedClient(settings.api_key, settings.api_secret, settings.passphrase)

@pytest.mark.usefixtures('client')
class TestPublicClient(object):
    @pytest.mark.parametrize('product', ['BCH-BTC'])
    def test_get_products(product):
        historical_rates = client.get_product_historic_rates(product)
        assert type(historical_rates) is dict

    @pytest.mark.parametrize('product', ['BCH-BTC'])
    def test_limit_order(product):
        client = gdax_client()
        response = client.buy(product_id=product, quantity=1, time_in_force='GTC', size=1, price=0.00001)
        assert response['message'] == 'Insufficient funds'

if __name__=='__main__':
    TestPublicClient.test_limit_order('BCH-BTC')