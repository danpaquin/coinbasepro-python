#
# cbpro/order_logger.py
# Shashwat Saxena
#
# Live order logger, using updates from orderbook using Coinbase Websocket Feed
import pickle
import sys
import time

from cbpro.order_book import OrderBook
from cbpro.cancellation_entry import CancellationEntry


class OrderLogger(OrderBook):
    def __init__(self, product_id='BTC-USD', log_to=None):
        super().__init__(product_id=product_id, log_to=log_to)
        self.cancellations = list()

    def on_open(self):
        self._sequence = -1
        print("-- Subscribed to OrderLogger! --\n")

    def on_close(self):
        print("\n-- OrderLogger Socket Closed! --")

    def remove(self, message):
        if message['reason'] == 'canceled':
            self.add_cancel(CancellationEntry(message, (self.get_bid() + self.get_ask()) / 2))
        super(OrderLogger, self).remove(message)

    def reset_cancellations(self):
        self.cancellations = list()

    def add_cancel(self, cancellation_entry):
        self.cancellations.append(cancellation_entry)


if __name__ == '__main__':
    import sys
    import time
    import datetime as dt

    class OrderLoggerConsole(OrderLogger):
        '''Log real-time changes to Order Book, as well as cancellations'''

        def __init__(self, product_id='BTC-USD', log_to=None):
            super(OrderLoggerConsole, self).__init__(product_id=product_id, log_to=log_to)

            # latest values of bid-ask spread
            self._bid = None
            self._ask = None
            self._bid_depth = None
            self._ask_depth = None

        def on_message(self, message):
            super(OrderLoggerConsole, self).on_message(message)

            # Calculate newest bid-ask spread
            bid = self.get_bid()
            bids = self.get_bids(bid)
            bid_depth = sum([b['size'] for b in bids])
            ask = self.get_ask()
            asks = self.get_asks(ask)
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
                print('{} {} bid: {:.3f} @ {:.2f}\task: {:.3f} @ {:.2f}'.format(
                    dt.datetime.now(), self.product_id, bid_depth, bid, ask_depth, ask))

    order_logger = OrderLoggerConsole()
    order_logger.start()

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        order_logger.close()

    if order_logger.error:
        sys.exit(1)
    else:
        sys.exit(0)
