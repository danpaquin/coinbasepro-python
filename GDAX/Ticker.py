#
# GDAX/OrderBook.py
# David Caseria
#
# Live order book updated from the GDAX Websocket Feed

from GDAX.PublicClient import PublicClient
from GDAX.WebsocketClient import WebsocketClient

class Ticker(WebsocketClient):

    def __init__(self, product_id='BTC-USD', log_to=None):
        ticker_url = PublicClient(
            api_url='wss://ws-feed.gdax.com',
            product_id=product_id,
            url_only=True
        ).getProductTicker()

        WebsocketClient.__init__(self, url=ticker_url, products=product_id)

        if log_to:
            assert hasattr(log_to, 'write')
        self._log_to = log_to
        self._current_ticker = None

    def onMessage(self, message):
        if 'type' in message and message['type'] == 'match':
            self._current_ticker = message
            if self._log_to:
                pickle.dump(message, self._log_to)

    def get_current_ticker(self):
        return self._current_ticker

if __name__ == '__main__':
    import time
    ticker = Ticker()
    ticker.start()
    while True:
        print(ticker.get_current_ticker())
        time.sleep(10)
    ticker.close()
