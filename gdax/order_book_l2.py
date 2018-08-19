#
# gdax/order_book_l2.py
# Lawrence Zhou
#
# L2 Order Book - does NOT depend on websocket (update with process_message) from WebSocketClient. This is COMPLETELY experimental and works differently from the current L3 orderbook

from bintrees import RBTree
from decimal import Decimal
import pickle

class OrderBookL2():
    def __init__(self, product_id='BTC-USD'):
        self._asks = RBTree()
        self._bids = RBTree()
        self._product_id = product_id

    @property
    def product_id(self):
        return self._product_id

    def process_snapshot(self, message):
        ''' Process a snapshot message '''

        self._asks = RBTree()
        self._bids = RBTree()

        for ask in message['asks']:
          price, size = ask
          price = Decimal(price)
          size = Decimal(size)

          self._asks.insert(price, size)

        for bid in message['bids']:
          price, size = bid
          price = Decimal(price)
          size = Decimal(size)

          self._bids.insert(price, size)

    def process_update(self, message):
        ''' Process an update message '''

        changes = message['changes']

        for change in changes:
          side, price, size = change

          price = Decimal(price)
          size = Decimal(size)

          if side == 'buy':
            if size <= 0:
              self._bids.remove(price)
            else:
              self._bids.insert(price, size)
          elif side == 'sell':
            if size <= 0:
              self._asks.remove(price)
            else:
              self._asks.insert(price, size)

        
    def process_message(self, message):
        msg_type = message['type']
        
        # dropped - not same product id
        if (message.get('product_id', None) != self._product_id):
          return

        if msg_type == 'snapshot':
            self.process_snapshot(message)
        elif msg_type == 'l2update':
            self.process_update(message)

    def get_current_book(self):
        result = { 'asks': [], 'bids': [] }

        for ask in self._asks:
            try:
                size = self._asks[ask]
            except KeyError:
                continue
            result['asks'].append([ask, size])

        for bid in self._bids:
            try:
                size = self._bids[bid]
            except KeyError:
                continue
            result['bids'].append([bid, size])
        return result

    def get_ask(self):
        price = self._asks.min_key()

        try:
          size = self._asks[price]
        except KeyError:
          return (price, 0)

        return (price, size)

    def get_bid(self):
        price = self._bids.max_key()

        try:
          size = self._bids[price]
        except KeyError:
          return (price, 0)

        return (price, size)
  
if __name__ == '__main__':
    import sys
    import time
    import datetime as dt
    import gdax

    class OrderBookConsole(gdax.WebsocketClient):
        def on_open(self):
            self.url = "wss://ws-feed.gdax.com/"
            self.products = ["ETH-USD"]
            self.channels = ['level2']

            self.order_book = OrderBookL2("ETH-USD")
						
						# Order Book Console Setup
            self._bid = None
            self._ask = None
            self._bid_depth = None
            self._ask_depth = None

        def on_message(self, msg):
            order_book = self.order_book
            order_book.process_message(msg)

            bid, bid_depth = order_book.get_bid()
            ask, ask_depth = order_book.get_ask()

            if self._bid == bid and self._ask == ask and self._bid_depth == bid_depth and self._ask_depth == ask_depth:
								pass
            else:
                self._bid = bid
                self._ask = ask
                self._bid_depth = bid_depth
                self._ask_depth = ask_depth

                print('{} {} bid: {:.3f} @ {:.2f}\task: {:.3f} @ {:.2f}'.format(
                    dt.datetime.now(), order_book.product_id, bid_depth, bid, ask_depth, ask))

        def on_close(self):
            print("-- Goodbye! --")


    orderbook_console = OrderBookConsole()
    orderbook_console.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        orderbook_console.close()

    if orderbook_console.error:
        sys.exit(1)
    else:
        sys.exit(0)
