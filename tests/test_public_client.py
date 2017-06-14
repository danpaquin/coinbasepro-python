import pytest
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
        r = client.get_product_order_book()
        assert type(r) is dict
        r = client.get_product_order_book(level=2)
        assert type(r) is dict
        assert 'asks' in r
        assert 'bids' in r

    def test_get_product_ticker(self, client):
        r = client.get_product_ticker()
        assert type(r) is dict
        assert 'ask' in r
        assert 'trade_id' in r

    def test_get_product_trades(self, client):
        r = client.get_product_trades()
        assert type(r) is list
        assert 'trade_id' in r[0]

    def test_get_historic_rates(self, client):
        r = client.get_product_historic_rates()
        assert type(r) is list

    def test_get_product_24hr_stats(self, client):
        r = client.get_product_24hr_stats()
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
