import pytest
import gdax


@pytest.fixture(scope='module')
def dc():
    """Dummy client for testing."""
    return gdax.AuthenticatedClient('test', 'test', 'test')


@pytest.mark.usefixtures('dc')
class TestAuthenticatedClient(object):
    def test_place_order_input_1(self, dc):
        with pytest.raises(ValueError):
            r = dc.place_order('BTC-USD', 'buy', 'market',
                               overdraft_enabled='true', funding_amount=10)

    def test_place_order_input_2(self, dc):
        with pytest.raises(ValueError):
            r = dc.place_order('BTC-USD', 'buy', 'limit',
                               cancel_after='123', tif='ABC')

    def test_place_order_input_3(self, dc):
        with pytest.raises(ValueError):
            r = dc.place_order('BTC-USD', 'buy', 'limit',
                               post_only='true', tif='FOK')

    def test_place_order_input_4(self, dc):
        with pytest.raises(ValueError):
            r = dc.place_order('BTC-USD', 'buy', 'market',
                               size=None, funds=None)

    def test_place_order_input_5(self, dc):
        with pytest.raises(ValueError):
            r = dc.place_order('BTC-USD', 'buy', 'market',
                               size=1, funds=1)
