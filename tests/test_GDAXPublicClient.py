import unittest
from GDAX import PublicClient

import vcr

my_vcr = vcr.VCR(
    serializer='yaml',
    cassette_library_dir='tests/cassettes/public',
    record_mode='once',
    match_on=['uri', 'method'],
)

#NOTE THAT THESE TESTS ARE FOCUSED ON BTC-USD
TEST_PRODUCT_ID = 'BTC-USD'

class TestGDAXPublicClient(unittest.TestCase):
    def setUp(self):
        #Only testing for BTC-USD
        self.GDAX = PublicClient(product_id=TEST_PRODUCT_ID)

    def test_PublicClientInitCorrectProductID(self):
        self.assertEquals(self.GDAX.productId,TEST_PRODUCT_ID)

    def test_PublicClientInitWrongProductID(self):
        EurProductIdClient = PublicClient(product_id="BTC-EUR")
        self.assertNotEquals(self.GDAX,EurProductIdClient)

    @my_vcr.use_cassette()
    def test_getProducts(self):
        #Results from direct browser run on Jan 7, 2017
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
        #test for first level depth
        test_depth = 1

        #Results from direct browser run on Jan 7, 2017
        correct_sequence = 1974627815
        results = self.GDAX.getProductOrderBook(level=test_depth,\
                                                       product=TEST_PRODUCT_ID)
        self.assertEqual(results['sequence'], correct_sequence)

if __name__ == '__main__':
    unittest.main()