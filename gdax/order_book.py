#
# gdax/order_book.py
# David Caseria
#
# Live order book updated from the gdax Websocket Feed

from operator import itemgetter
from bintrees import RBTree
from decimal import Decimal
import pickle

from gdax.public_client import PublicClient
from gdax.websocket_client import WebsocketClient


class OrderBook(WebsocketClient):
    def __init__(self, product_id='BTC-USD', log_to=None):
        super(OrderBook, self).__init__(products=product_id)
        self._asks = RBTree()
        self._bids = RBTree()
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
            # Initialize order book
            self._asks = RBTree()
            self._bids = RBTree()
            res = self._client.get_product_order_book(product_id=self.product_id, level=3)
            for bid in res['bids']:
                self.add({
                    'id': bid[2],
                    'side': 'buy',
                    'price': Decimal(bid[0]),
                    'size': Decimal(bid[1])
                })
            for ask in res['asks']:
                self.add({
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

        msg_type = message['type']
        if msg_type == 'open':
            self.add(message)
        elif msg_type == 'done' and 'price' in message:
            self.remove(message)
        elif msg_type == 'match':
            self.match(message)
            self._current_ticker = message
        elif msg_type == 'change':
            self.change(message)

        self._sequence = sequence

        # bid = self.get_bid()
        # bids = self.get_bids(bid)
        # bid_depth = sum([b['size'] for b in bids])
        # ask = self.get_ask()
        # asks = self.get_asks(ask)
        # ask_depth = sum([a['size'] for a in asks])
        # print('bid: %f @ %f - ask: %f @ %f' % (bid_depth, bid, ask_depth, ask))

    def on_error(self, e):
        self._sequence = -1
        self.close()
        self.start()

    def add(self, order):
        order = {
            'id': order.get('order_id') or order['id'],
            'side': order['side'],
            'price': Decimal(order['price']),
            'size': Decimal(order.get('size') or order['remaining_size'])
        }
        if order['side'] == 'buy':
            bids = self.get_bids(order['price'])
            if bids is None:
                bids = [order]
            else:
                bids.append(order)
            self.set_bids(order['price'], bids)
        else:
            asks = self.get_asks(order['price'])
            if asks is None:
                asks = [order]
            else:
                asks.append(order)
            self.set_asks(order['price'], asks)

    def remove(self, order):
        price = Decimal(order['price'])
        if order['side'] == 'buy':
            bids = self.get_bids(price)
            if bids is not None:
                bids = [o for o in bids if o['id'] != order['order_id']]
                if len(bids) > 0:
                    self.set_bids(price, bids)
                else:
                    self.remove_bids(price)
        else:
            asks = self.get_asks(price)
            if asks is not None:
                asks = [o for o in asks if o['id'] != order['order_id']]
                if len(asks) > 0:
                    self.set_asks(price, asks)
                else:
                    self.remove_asks(price)

    def match(self, order):
        size = Decimal(order['size'])
        price = Decimal(order['price'])

        side = order['side']
        if side == 'buy':
            orders = self.get_bids(price)
            set_func = self.set_bids
        elif side == 'sell':
            orders = self.get_asks(price)
            set_func = self.set_asks
        else:
            raise AssertionError('Invalid side. Expected "buy" or "sell". Found: {}.'.format(side))

        if not orders:
            return

        assert orders[0]['id'] == order['maker_order_id']

        if orders[0]['size'] == size:
            set_func(price, orders[1:])
        else:
            orders[0]['size'] -= size
            set_func(price, orders)

    def change(self, order):
        new_size = Decimal(order['new_size'])
        price = Decimal(order['price'])
        side = order['side']

        if side == 'buy':
            orders = self.get_bids(price)
            set_func = self.set_bids
        elif side == 'sell':
            orders = self.get_asks(price)
            set_func = self.set_asks
        else:
            raise AssertionError('Invalid side. Expected "buy" or "sell". Found: {}.'.format(side))

        # If the order_id isn't in the order book, no further action to take
        if orders is None or not any(o['id'] == order['order_id'] for o in orders):
            return

        # If it is in the order book, update the size
        index = list(map(itemgetter('id'), orders)).index(order['order_id'])
        orders[index]['size'] = new_size

        set_func(price, orders)

    def get_current_ticker(self):
        return self._current_ticker

    def get_current_book(self):
        result = {
            'sequence': self._sequence,
            'asks': [],
            'bids': [],
        }
        for ask in self._asks:
            try:
                # There can be a race condition here, where a price point is removed
                # between these two ops
                this_ask = self._asks[ask]
            except KeyError:
                continue
            for order in this_ask:
                result['asks'].append([order['price'], order['size'], order['id']])
        for bid in self._bids:
            try:
                # There can be a race condition here, where a price point is removed
                # between these two ops
                this_bid = self._bids[bid]
            except KeyError:
                continue

            for order in this_bid:
                result['bids'].append([order['price'], order['size'], order['id']])
        return result

    def get_ask(self):
        return self._asks.min_key()

    def get_asks(self, price):
        return self._asks.get(price)

    def remove_asks(self, price):
        self._asks.remove(price)

    def set_asks(self, price, asks):
        self._asks.insert(price, asks)

    def get_bid(self):
        return self._bids.max_key()

    def get_bids(self, price):
        return self._bids.get(price)

    def remove_bids(self, price):
        self._bids.remove(price)

    def set_bids(self, price, bids):
        self._bids.insert(price, bids)


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
                print('{}\tbid: {:.3f} @ {:.2f}\task: {:.3f} @ {:.2f}'.format(dt.datetime.now(), bid_depth, bid,
                                                                              ask_depth, ask))

    order_book = OrderBookConsole()
    order_book.start()
    time.sleep(10)
    order_book.close()
