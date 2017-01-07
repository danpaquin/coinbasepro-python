import unittest
from GDAX import PublicClient

import pytz
from datetime import datetime

import vcr

# SET UP VCR TO SAVE YAML CASSETTETTES TO PUBLIC FOLDER
my_vcr = vcr.VCR(
    serializer='yaml',
    cassette_library_dir='tests/cassettes/public',
    record_mode='once',
    match_on=['uri', 'method'],
)

# NOTE THAT THESE TESTS ARE FOCUSED ON BTC-USD
TEST_PRODUCT_ID = 'BTC-USD'

# NON-EXISTENT PRODUCT ID AS OF Jan 7, 2017
BAD_TEST_PRODUCT_ID = 'BTC-USR'


class TestGDAXPublicClient(unittest.TestCase):
    def setUp(self):
        # Only testing for BTC-USD
        self.GDAX = PublicClient(product_id=TEST_PRODUCT_ID)

    def test_PublicClientInitCorrectProductID(self):
        self.assertEquals(self.GDAX.productId, TEST_PRODUCT_ID)

    def test_PublicClientInitWrongProductID(self):
        eur_product_client = PublicClient(product_id="BTC-EUR")
        self.assertNotEquals(self.GDAX, eur_product_client)

    @my_vcr.use_cassette()
    def test_getProducts(self):
        # Results from direct browser run on Jan 7, 2017
        correct = [
             {"id": "BTC-GBP", "base_currency": "BTC", "quote_currency": "GBP", "base_min_size": "0.01",
              "base_max_size": "10000", "quote_increment": "0.01", "display_name": "BTC/GBP"},
             {"id": "BTC-EUR", "base_currency": "BTC", "quote_currency": "EUR", "base_min_size": "0.01",
              "base_max_size": "10000", "quote_increment": "0.01", "display_name": "BTC/EUR"},
             {"id": "ETH-USD", "base_currency": "ETH", "quote_currency": "USD", "base_min_size": "0.01",
              "base_max_size": "1000000", "quote_increment": "0.01", "display_name": "ETH/USD"},
             {"id": "ETH-BTC", "base_currency": "ETH", "quote_currency": "BTC", "base_min_size": "0.01",
              "base_max_size": "1000000", "quote_increment": "0.00001", "display_name": "ETH/BTC"},
             {"id": "LTC-USD", "base_currency": "LTC", "quote_currency": "USD", "base_min_size": "0.01",
              "base_max_size": "1000000", "quote_increment": "0.01", "display_name": "LTC/USD"},
             {"id": "LTC-BTC", "base_currency": "LTC", "quote_currency": "BTC", "base_min_size": "0.01",
              "base_max_size": "1000000", "quote_increment": "0.00001", "display_name": "LTC/BTC"},
             {"id": "BTC-USD", "base_currency": "BTC", "quote_currency": "USD", "base_min_size": "0.01",
              "base_max_size": "10000", "quote_increment": "0.01", "display_name": "BTC/USD"}
        ]
        self.assertEqual(self.GDAX.getProducts(), correct)

    @my_vcr.use_cassette()
    def test_getProductOrderBook_level_1(self):
        # Test for first level depth
        test_depth = 1

        # Results from run on Jan 7, 2017
        correct_sequence = 1974671651
        results = self.GDAX.getProductOrderBook(level=test_depth, product=TEST_PRODUCT_ID)
        self.assertEqual(results['sequence'], correct_sequence)

    @my_vcr.use_cassette()
    def test_getProductOrderBook_level_2(self):
        # Test for second level depth
        test_depth = 2

        # Results from direct browser run on Jan 7, 2017
        correct_sequence = 1974823003
        results = self.GDAX.getProductOrderBook(level=test_depth, product=TEST_PRODUCT_ID)
        self.assertEqual(results['sequence'], correct_sequence)

    @my_vcr.use_cassette()
    def test_getProductOrderBook_level_3(self):
        # Test for third level depth
        test_depth = 3

        # Results from direct browser run on Jan 7, 2017
        correct_sequence = 1974823009
        results = self.GDAX.getProductOrderBook(level=test_depth, product=TEST_PRODUCT_ID)
        self.assertEqual(results['sequence'], correct_sequence)

    # TODO: it may be better functionality for library to throw exception for invalid level
    @my_vcr.use_cassette()
    def test_getProductOrderBook_level_bad(self):
        # test for non-existent level depth
        test_depth = 4

        results = self.GDAX.getProductOrderBook(level=test_depth, product=TEST_PRODUCT_ID)
        self.assertEqual(results['message'], "Invalid level")

    # TODO: it may be better functionality for library to throw exception for invalid product
    @my_vcr.use_cassette()
    def test_getProductOrderBook_product_bad(self):
        # test for non-existent level depth
        test_depth = 1

        results = self.GDAX.getProductOrderBook(level=test_depth, product=BAD_TEST_PRODUCT_ID)
        self.assertEqual(results['message'], "NotFound")

    @my_vcr.use_cassette()
    def test_getProductTicker(self):
        correct = {u"ask": u"905.99",
                   u"bid": u"905.98",
                   u"price": u"905.99000000",
                   u"size": u"0.70384000",
                   u"time": u"2017-01-07T18:06:01.618000Z",
                   u"trade_id": 12502526,
                   u"volume": u"12904.32111369"
                   }
        results = self.GDAX.getProductTicker(product=TEST_PRODUCT_ID)
        self.assertEqual(results, correct)

    @my_vcr.use_cassette('test_getProductTicker')
    def test_getProductTicker_product_none(self):
        correct = {u"ask": u"905.99",
                   u"bid": u"905.98",
                   u"price": u"905.99000000",
                   u"size": u"0.70384000",
                   u"time": u"2017-01-07T18:06:01.618000Z",
                   u"trade_id": 12502526,
                   u"volume": u"12904.32111369"
                   }
        results = self.GDAX.getProductTicker()
        self.assertEqual(results, correct)

    @my_vcr.use_cassette()
    def test_getProductTicker_product_bad(self):
        results = self.GDAX.getProductTicker(product=BAD_TEST_PRODUCT_ID)
        self.assertEqual(results['message'], "NotFound")

    @my_vcr.use_cassette()
    def test_getProductTrades(self):
        correct_top_one = {u'trade_id': 12503748, u'size': u'0.00816557', u'side': u'sell', u'price': u'900.81000000', u'time': u'2017-01-07T18:46:40.988Z'}
        results = self.GDAX.getProductTrades(product=TEST_PRODUCT_ID)
        self.assertEqual(results[0], correct_top_one)

        # TODO: Add additional tests for pagination
        self.assertEqual(len(results), 100)

    @my_vcr.use_cassette()
    def test_getProductTrades_product_bad(self):
        results = self.GDAX.getProductTrades(product=BAD_TEST_PRODUCT_ID)
        self.assertEqual(results['message'], "NotFound")

    @my_vcr.use_cassette()
    def test_getProductHistoricRates(self):
        # Test for default one minute BTC-USD candle poll - without start/end pull last hour
        correct_top_one = [1483815960, 900.92, 904.94, 904.94, 904.33, 10.113950419999998]
        results = self.GDAX.getProductHistoricRates(product=TEST_PRODUCT_ID)

        self.assertEqual(results[0], correct_top_one)
        self.assertEqual(len(results), 61)

    # TODO: Consider making API give Unix seconds to format to ISO 8601 for users
    @my_vcr.use_cassette()
    def test_getProductHistoricRates_start_end_good(self):
        tz = pytz.timezone('America/Chicago')

        start_time = datetime.fromtimestamp(1483813680, tz).isoformat()
        end_time = datetime.fromtimestamp(1483817160, tz).isoformat()

        # Test for default one minute BTC-USD candle poll - without start/end pull last hour
        correct_top_one = [1483817100, 904.9, 904.9, 904.9, 904.9, 0.02472]
        results = self.GDAX.getProductHistoricRates(product=TEST_PRODUCT_ID,start=start_time,end=end_time)

        self.assertEqual(results[0], correct_top_one)
        self.assertEqual(len(results), 58)

    # TODO: Add tests for valid start, end, granularity to avoid bad requests to upstream

    @my_vcr.use_cassette()
    def test_getProductHistoricRates_5mins(self):
        test_5min_granularity = 5 * 60

        # Test for default five minute BTC-USD candle poll - without start/end pull last hour
        correct_top_one = [1483816200, 904.01, 904.5, 904.49, 904.49, 18.09471826]
        results = self.GDAX.getProductHistoricRates(product=TEST_PRODUCT_ID,granularity=test_5min_granularity)

        self.assertEqual(results[0], correct_top_one)
        self.assertEqual(len(results), 13)

    @my_vcr.use_cassette()
    def test_getProduct24HrStats(self):
        correct = { u"high":    u"911.14000000",
                    u"last":    u"896.07000000",
                    u"low":     u"802.07000000",
                    u"open":    u"893.63000000",
                    u"volume":  u"12133.46704037",
                    u"volume_30day": u"220351.04630033"
                   }
        results = self.GDAX.getProduct24HrStats(product=TEST_PRODUCT_ID)
        self.assertEqual(results, correct)

    @my_vcr.use_cassette()
    def test_getProduct24HrStats_product_bad(self):
        results = self.GDAX.getProduct24HrStats(product=BAD_TEST_PRODUCT_ID)
        self.assertEqual(results['message'], "NotFound")

    @my_vcr.use_cassette()
    def test_getCurrencies(self):
        correct = [
                    {u'min_size': u'0.00000001', u'id': u'BTC', u'name': u'Bitcoin'},
                    {u'min_size': u'0.00000100', u'id': u'ETH', u'name': u'Ether'},
                    {u'min_size': u'0.01000000', u'id': u'EUR', u'name': u'Euro'},
                    {u'min_size': u'0.00000001', u'id': u'LTC', u'name': u'Litecoin'},
                    {u'min_size': u'0.01000000', u'id': u'GBP', u'name': u'British Pound'},
                    {u'min_size': u'0.01000000', u'id': u'USD', u'name': u'United States Dollar'}
                   ]
        results = self.GDAX.getCurrencies()
        self.assertEqual(results, correct)

if __name__ == '__main__':
    unittest.main()
