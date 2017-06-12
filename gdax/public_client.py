#
# GDAX/PublicClient.py
# Daniel Paquin
#
# For public requests to the GDAX exchange

import requests


class PublicClient(object):
    """GDAX public client API.

    All requests default to the `product_id` specified at object creation if not otherwise specified.

    Attributes:
        url (str): API endpoint URL
        product_id (str): Default product used for requests

    """

    def __init__(self, api_url='https://api.gdax.com', product_id='BTC-USD'):
        """Create GDAX API public client.

        Args:
            api_url (str): API endpoint URL
            product_id (str): Default product to use for all requests

        """
        self.url = api_url.rstrip('/')
        self.product_id = product_id

    def get_products(self):
        """Get a list of available currency pairs for trading.

        Returns:
            dict: Info about all currency pairs

        """
        r = requests.get(self.url + '/products')
        # r.raise_for_status()
        return r.json()

    def get_product_order_book(self, level=1, product_id=None):
        """Get a list of open orders for a product.

        The amount of detail shown can be customized with the `level` parameter:
        * 1: Only the best bid and ask
        * 2: Top 50 bids and asks (aggregated)
        * 3: Full order book (non aggregated)

        Level 1 and Level 2 are recommended for polling. For the most up-to-date data, consider using the websocket
        stream.
        
        **Caution**: Level 3 is only recommended for users wishing to maintain a full real-time order book using the
        websocket stream. Abuse of Level 3 via polling will cause your access to be limited or blocked.

        Args:
            level (int): Order book level
            product_id (str): (Optional) Product

        Returns:
            dict: Order book

        """
        params = {'level': level}
        r = requests.get(self.url + '/products/{}/book'.format(product_id or self.product_id), params=params)
        # r.raise_for_status()
        return r.json()

    def get_product_ticker(self, product_id=None):
        """Snapshot information about the last trade (tick), best bid/ask and 24h volume.

        **Caution**: Polling is discouraged in favor of connecting via the websocket stream and listening for match
        messages.

        Args:
            product_id (str): (Optional) Product

        Returns:
            dict: Ticker info

        """
        r = requests.get(self.url + '/products/{}/ticker'.format(product_id or self.product_id))
        # r.raise_for_status()
        return r.json()

    def get_product_trades(self, product_id=None):
        """List the latest trades for a product.

        Args:
            product_id (str): (Optional) Product

        Returns:
        dict: Latest trades

        """
        r = requests.get(self.url + '/products/{}/trades'.format(product_id or self.product_id))
        # r.raise_for_status()
        return r.json()

    def get_product_historic_rates(self, start=None, end=None, granularity=None, product_id=None):
        """Historic rates for a product.

        Rates are returned in grouped buckets based on requested `granularity`. If start, end, and granularity aren't
        provided, the exchange will assume some (currently unknown) default values.

        Historical rate data may be incomplete. No data is published for intervals where there are no ticks.

        **Caution**: Historical rates should not be polled frequently. If you need real-time information, use the trade
        and book endpoints along with the websocket feed.

        The maximum number of data points for a single request is 200 candles. If your selection of start/end time and
        granularity will result in more than 200 data points, your request will be rejected. If you wish to retrieve
        fine granularity data over a larger time range, you will need to make multiple requests with new start/end
        ranges.

        Args:
            start (str): (Optional) Start time in ISO 8601
            end (str): (Optional) End time in ISO 8601
            granularity (str): (Optional) Desired time slice in seconds
            product_id (str): (Optional) Product

        Returns:
            dict: Historic candle data

        """
        params = {}
        if start is not None:
            params['start'] = start
        if end is not None:
            params['end'] = end
        if granularity is not None:
            params['granularity'] = granularity
        r = requests.get(self.url + '/products/{}/candles'.format(product_id or self.product_id), params=params)
        # r.raise_for_status()
        return r.json()

    def get_product_24hr_stats(self, product_id=None):
        """Get 24 hr stats for the product.

        Args:
            product_id (str): (Optional) Product

        Returns:
            dict: 24 hour stats. Volume is in base currency units. Open, high, low are in quote currency units.

        """
        r = requests.get(self.url + '/products/{}/stats'.format(product_id or self.product_id))
        # r.raise_for_status()
        return r.json()

    def get_currencies(self):
        """List known currencies.

        Returns:
            dict: List of currencies

        """
        r = requests.get(self.url + '/currencies')
        # r.raise_for_status()
        return r.json()

    def get_time(self):
        """Get the API server time.

        Returns:
            dict: Server time in ISO and epoch format (decimal seconds since Unix epoch)

        """
        r = requests.get(self.url + '/time')
        # r.raise_for_status()
        return r.json()
