import pytest
import gdax
import time


@pytest.fixture(scope='module')
def client():
    return gdax.PublicClient()


@pytest.mark.usefixtures('client')
class TestPublicClient(object):

    @staticmethod
    def teardown_method():
        time.sleep(.25)  # Avoid rate limit

    def test_get_products(self, client):
        r = client.get_products()
        assert type(r) is list

    @pytest.mark.parametrize('level', [1, 2, 3, None])
    def test_get_product_order_book(self, client, level):
        r = client.get_product_order_book('BTC-USD', level=level)
        assert type(r) is dict
        assert 'asks' in r
        assert 'bids' in r

        if level in (1, None) and (len(r['asks']) > 1 or len(r['bids']) > 1):
            pytest.fail('Fail: Level 1 should only return the best ask and bid')

        if level is 2 and (len(r['asks']) > 50 or len(r['bids']) > 50):
            pytest.fail('Fail: Level 2 should only return the top 50 asks and bids')

        if level is 2 and (len(r['asks']) < 50 or len(r['bids']) < 50):
            pytest.fail('Fail: Level 3 should return the full order book')

    def test_get_product_ticker(self, client):
        r = client.get_product_ticker('BTC-USD')
        assert type(r) is dict
        assert 'ask' in r
        assert 'trade_id' in r

    def test_get_product_trades(self, client):
        r = client.get_product_trades('BTC-USD')
        assert type(r) is list
        assert 'trade_id' in r[0]

    @pytest.mark.parametrize('start', ('2017-11-01', None))
    @pytest.mark.parametrize('end', ('2017-11-30', None))
    @pytest.mark.parametrize('granularity', (3600, None))
    def test_get_historic_rates(self, client, start, end, granularity):
        r = client.get_product_historic_rates('BTC-USD', start=start, end=end, granularity=granularity)
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
