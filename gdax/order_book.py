#
# gdax/order_book.py
# David Caseria
#
# Live order book updated from the gdax Websocket Feed

from bintrees import RBTree
from decimal import Decimal
import pickle

from gdax.public_client import PublicClient
from gdax.websocket_client import WebsocketClient
from gdax.book_builder import BookBuilder


class OrderBook(WebsocketClient):
    def __init__(self, product_id='BTC-USD', log_to=None):
        super(OrderBook, self).__init__(products=product_id)
        self.book_builder = BookBuilder()
        self._client = PublicClient()
        self._sequence = -1
        self._log_to = log_to
        if self._log_to:
            assert hasattr(self._log_to, 'write')
        self._current_ticker = None

    @property
    def product_id(self):
        ''' Currently OrderBook only supports a single product even though it is stored as a list of products. '''
        return self.products[0]

    def on_message(self, message):
        if self._log_to:
            pickle.dump(message, self._log_to)

        sequence = message['sequence']
        if self._sequence == -1:
            self.book_builder = BookBuilder()
            res = self._client.get_product_order_book(product_id=self.product_id, level=3)
            for bid in res['bids']:
                self.book_builder.add({
                    'id': bid[2],
                    'side': 'buy',
                    'price': Decimal(bid[0]),
                    'size': Decimal(bid[1])
                })
            for ask in res['asks']:
                self.book_builder.add({
                    'id': ask[2],
                    'side': 'sell',
                    'price': Decimal(ask[0]),
                    'size': Decimal(ask[1])
                })
            self._sequence = res['sequence']

        if sequence <= self._sequence:
            # ignore older messages (e.g. before order book initialization from getProductOrderBook)
            return
        elif sequence > self._sequence + 1:
            print('Error: messages missing ({} - {}). Re-initializing websocket.'.format(sequence, self._sequence))
            self.close()
            self.start()
            return
        
        self.book_builder.handle(message)

        if message['type'] == 'match':
            self._current_ticker = message

        self._sequence = sequence

    def on_error(self, e):
        self._sequence = -1
        self.close()
        self.start()

    def get_current_ticker(self):
        return self._current_ticker


if __name__ == '__main__':
    import time
    import datetime as dt


    class OrderBookConsole(OrderBook):
        ''' Logs real-time changes to the bid-ask spread to the console '''

        def __init__(self, product_id=None):
            super(OrderBookConsole, self).__init__(product_id=product_id)

            # latest values of bid-ask spread
            self._bid = None
            self._ask = None
            self._bid_depth = None
            self._ask_depth = None

        def on_message(self, message):
            super(OrderBookConsole, self).on_message(message)

            # Calculate newest bid-ask spread
            bid = self.book_builder.get_bid()
            bids = self.book_builder.get_bids(bid)
            bid_depth = sum([b['size'] for b in bids])
            ask = self.book_builder.get_ask()
            asks = self.book_builder.get_asks(ask)
            ask_depth = sum([a['size'] for a in asks])

            if self._bid == bid and self._ask == ask and self._bid_depth == bid_depth and self._ask_depth == ask_depth:
                # If there are no changes to the bid-ask spread since the last update, no need to print
                pass
            else:
                # If there are differences, update the cache
                self._bid = bid
                self._ask = ask
                self._bid_depth = bid_depth
                self._ask_depth = ask_depth
                print('{}\tbid: {:.3f} @ {:.2f}\task: {:.3f} @ {:.2f}'.format(dt.datetime.now(), bid_depth, bid,
                                                                              ask_depth, ask))

    order_book = OrderBookConsole()
    order_book.start()
    time.sleep(10)
    order_book.close()
