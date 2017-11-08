import pytest
from itertools import islice
import gdax


@pytest.fixture(scope='module')
def client():
    return gdax.PublicClient()


@pytest.mark.usefixtures('client')
class TestPublicClient(object):
    def test_get_products(self, client):
        r = client.get_products()
        assert type(r) is list

    def test_get_product_order_book(self, client):
        r = client.get_product_order_book('BTC-USD')
        assert type(r) is dict
        r = client.get_product_order_book('BTC-USD', level=2)
        assert type(r) is dict
        assert 'asks' in r
        assert 'bids' in r

    def test_get_product_ticker(self, client):
        r = client.get_product_ticker('BTC-USD')
        assert type(r) is dict
        assert 'ask' in r
        assert 'trade_id' in r

    def test_get_product_trades(self, client):
        r = list(islice(client.get_product_trades('BTC-USD'), 200))
        assert type(r) is list
        assert 'trade_id' in r[0]

    def test_get_historic_rates(self, client):
        r = client.get_product_historic_rates('BTC-USD')
        assert type(r) is list

    def test_get_product_24hr_stats(self, client):
        r = client.get_product_24hr_stats('BTC-USD')
        assert type(r) is dict
        assert 'volume_30day' in r

    def test_get_currencies(self, client):
        r = client.get_currencies()
        assert type(r) is list
        assert 'name' in r[0]

    def test_get_time(self, client):
        r = client.get_time()
        assert type(r) is dict
        assert 'iso' in r
