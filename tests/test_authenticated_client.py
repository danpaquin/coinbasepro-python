import pytest
import json
import time
from itertools import islice
from cbpro.authenticated_client import AuthenticatedClient


@pytest.fixture(scope='module')
def dc():
    """Dummy client for testing."""
    return AuthenticatedClient('test', 'test', 'test')


@pytest.mark.usefixtures('dc')
class TestAuthenticatedClientSyntax(object):
    def test_place_order_input_1(self, dc):
        with pytest.raises(ValueError):
            r = dc.place_order('BTC-USD', 'buy', 'market',
                               overdraft_enabled='true', funding_amount=10)

    def test_place_order_input_2(self, dc):
        with pytest.raises(ValueError):
            r = dc.place_order('BTC-USD', 'buy', 'limit',
                               cancel_after='123', time_in_force='ABC')

    def test_place_order_input_3(self, dc):
        with pytest.raises(ValueError):
            r = dc.place_order('BTC-USD', 'buy', 'limit',
                               post_only='true', time_in_force='FOK')

    def test_place_order_input_4(self, dc):
        with pytest.raises(ValueError):
            r = dc.place_order('BTC-USD', 'buy', 'market',
                               size=None, funds=None)

    def test_place_order_input_5(self, dc):
        with pytest.raises(ValueError):
            r = dc.place_order('BTC-USD', 'buy', 'market',
                               size=1, funds=1)


@pytest.fixture(scope='module')
def client():
    """Client that connects to sandbox API. Relies on authentication information
    provided in api_config.json"""
    with open('api_config.json.example') as file:
        api_config = json.load(file)
    c = AuthenticatedClient(
        api_url='https://api-public.sandbox.pro.coinbase.com', **api_config)

    # Set up account with deposits and orders. Do this by depositing from
    # the Coinbase USD wallet, which has a fixed value of > $10,000.
    #
    # Only deposit if the balance is below some nominal amount. The
    # exchange seems to freak out if you run up your account balance.
    coinbase_accounts = c.get_coinbase_accounts()
    account_info = [x for x in coinbase_accounts
                    if x['name'] == 'USD Wallet'][0]
    account_usd = account_info['id']
    if float(account_info['balance']) < 70000:
        c.coinbase_deposit(10000, 'USD', account_usd)
    # Place some orders to generate history
    c.place_limit_order('BTC-USD', 'buy', 1, 0.01)
    c.place_limit_order('BTC-USD', 'buy', 2, 0.01)
    c.place_limit_order('BTC-USD', 'buy', 3, 0.01)

    return c


@pytest.mark.usefixtures('dc')
@pytest.mark.skip(reason="these test require authentication")
class TestAuthenticatedClient(object):
    """Test the authenticated client by validating basic behavior from the
    sandbox exchange."""
    def test_get_accounts(self, client):
        r = client.get_accounts()
        assert type(r) is list
        assert 'currency' in r[0]
        # Now get a single account
        r = client.get_account(account_id=r[0]['id'])
        assert type(r) is dict
        assert 'currency' in r

    def test_account_history(self, client):
        accounts = client.get_accounts()
        account_usd = [x for x in accounts if x['currency'] == 'USD'][0]['id']
        r = list(islice(client.get_account_history(account_usd), 5))
        assert type(r) is list
        assert 'amount' in r[0]
        assert 'details' in r[0]

        # Now exercise the pagination abstraction. Setting limit to 1 means
        # each record comes in a separate HTTP response.
        history_gen = client.get_account_history(account_usd, limit=1)
        r = list(islice(history_gen, 2))
        r2 = list(islice(history_gen, 2))
        assert r != r2
        # Now exercise the `before` parameter.
        r3 = list(client.get_account_history(account_usd, before=r2[0]['id']))
        assert r3 == r

    def test_get_account_holds(self, client):
        accounts = client.get_accounts()
        account_usd = [x for x in accounts if x['currency'] == 'USD'][0]['id']
        r = list(client.get_account_holds(account_usd))
        assert type(r) is list
        assert 'type' in r[0]
        assert 'ref' in r[0]

    def test_place_order(self, client):
        r = client.place_order('BTC-USD', 'buy', 'limit',
                               price=0.62, size=0.0144)
        assert type(r) is dict
        assert r['stp'] == 'dc'

    def test_place_limit_order(self, client):
        r = client.place_limit_order('BTC-USD', 'buy', 4.43, 0.01232)
        assert type(r) is dict
        assert 'executed_value' in r
        assert not r['post_only']
        client.cancel_order(r['id'])

    def test_place_market_order(self, client):
        r = client.place_market_order('BTC-USD', 'buy', size=0.01)
        assert 'status' in r
        assert r['type'] == 'market'
        client.cancel_order(r['id'])

        # This one probably won't go through
        r = client.place_market_order('BTC-USD', 'buy', funds=100000)
        assert type(r) is dict

    @pytest.mark.parametrize('stop_type, side', [('entry', 'buy'), ('loss', 'sell')])
    def test_place_stop_order(self, client, stop_type, side):
        client.cancel_all()
        r = client.place_stop_order('BTC-USD', side, stop_type, 100, 0.01)
        assert type(r) is dict
        assert r['stop'] == stop_type
        assert r['stop_price'] == '100.00000000'
        assert r['type'] == 'limit'
        client.cancel_order(r['id'])

    def test_place_invalid_stop_order(self, client):
        client.cancel_all()
        with pytest.raises(ValueError):
            client.place_stop_order('BTC-USD', 'buy', 'loss', 5.65, 0.01)

    def test_cancel_order(self, client):
        r = client.place_limit_order('BTC-USD', 'buy', 4.43, 0.01232)
        time.sleep(0.2)
        r2 = client.cancel_order(r['id'])
        assert r2[0] == r['id']

    def test_cancel_all(self, client):
        r = client.cancel_all()
        assert type(r) is list

    def test_get_order(self, client):
        r = client.place_limit_order('BTC-USD', 'buy', 4.43, 0.01232)
        time.sleep(0.2)
        r2 = client.get_order(r['id'])
        assert r2['id'] == r['id']

    def test_get_orders(self, client):
        r = list(islice(client.get_orders(), 10))
        assert type(r) is list
        assert 'created_at' in r[0]

    def test_get_fills(self, client):
        r = list(islice(client.get_orders(), 10))
        assert type(r) is list
        assert 'fill_fees' in r[0]

    def test_get_fundings(self, client):
        r = list(islice(client.get_fundings(), 10))
        assert type(r) is list

    def test_repay_funding(self, client):
        # This request gets denied
        r = client.repay_funding(2.1, 'USD')

    def test_get_position(self, client):
        r = client.get_position()
        assert 'accounts' in r

    def test_get_payment_methods(self, client):
        r = client.get_payment_methods()
        assert type(r) is list

    def test_get_coinbase_accounts(self, client):
        r = client.get_coinbase_accounts()
        assert type(r) is list

    def test_get_trailing_volume(self, client):
        r = client.get_trailing_volume()
        assert type(r) is list

    def test_get_fees(self, client):
        r = client.get_fees()
        assert type(r) is dict
