#
# GDAX/OrderBook.py
# David Caseria
#
# Live order book updated from the GDAX Websocket Feed

from operator import itemgetter
from bintrees import RBTree
from decimal import Decimal
import pickle

from GDAX.PublicClient import PublicClient
from GDAX.WebsocketClient import WebsocketClient


class OrderBook(WebsocketClient):

    def __init__(self, product_id='BTC-USD', log_to=None):
        WebsocketClient.__init__(self, products=product_id)
        self._asks = RBTree()
        self._bids = RBTree()
        self._client = PublicClient(product_id=product_id)
        self._sequence = -1
        if log_to:
            assert hasattr(log_to, 'write')
        self._log_to = log_to

    def onMessage(self, message):
        if self._log_to:
            pickle.dump(message, self._log_to)

        sequence = message['sequence']
        if self._sequence == -1:
            self._asks = RBTree()
            self._bids = RBTree()
            res = self._client.getProductOrderBook(level=3)
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
            return #ignore old messages
        elif sequence > self._sequence + 1:
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

    def add(self, order):
        order = {
            'id': order['order_id'] if 'order_id' in order else order['id'],
            'side': order['side'],
            'price': Decimal(order['price']),
            'size': Decimal(order['size'] if 'size' in order else order['remaining_size'])
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

        if order['side'] == 'buy':
            bids = self.get_bids(price)
            if not bids:
                return
            assert bids[0]['id'] == order['maker_order_id']
            if bids[0]['size'] == size:
                self.set_bids(price, bids[1:])
            else:
                bids[0]['size'] -= size
                self.set_bids(price, bids)
        else:
            asks = self.get_asks(price)
            if not asks:
                return
            assert asks[0]['id'] == order['maker_order_id']
            if asks[0]['size'] == size:
                self.set_asks(price, asks[1:])
            else:
                asks[0]['size'] -= size
                self.set_asks(price, asks)

    def change(self, order):
        new_size = Decimal(order['new_size'])
        price = Decimal(order['price'])

        if order['side'] == 'buy':
            bids = self.get_bids(price)
            if bids is None or not any(o['id'] == order['order_id'] for o in bids):
                return
            index = map(itemgetter('id'), bids).index(order['order_id'])
            bids[index]['size'] = new_size
            self.set_bids(price, bids)
        else:
            asks = self.get_asks(price)
            if asks is None or not any(o['id'] == order['order_id'] for o in asks):
                return
            index = map(itemgetter('id'), asks).index(order['order_id'])
            asks[index]['size'] = new_size
            self.set_asks(price, asks)

        tree = self._asks if order['side'] == 'sell' else self._bids
        node = tree.get(price)

        if node is None or not any(o['id'] == order['order_id'] for o in node):
            return

    def get_current_book(self):
        result = dict()
        result['sequence'] = self._sequence
        result['asks'] = list()
        result['bids'] = list()
        for ask in self._asks:
            try:
                # There can be a race condition here, where a price point is removed
                # between these two ops
                thisAsk = self._asks[ask]
            except KeyError:
                continue
            for order in thisAsk:
                result['asks'].append([
                    order['price'],
                    order['size'],
                    order['id'],
                ])
        for bid in self._bids:
            try:
                # There can be a race condition here, where a price point is removed
                # between these two ops
                thisBid = self._bids[bid]
            except KeyError:
                continue

            for order in thisBid:
                result['bids'].append([
                    order['price'],
                    order['size'],
                    order['id'],
                ])
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
    order_book = OrderBook()
    order_book.start()
    time.sleep(10)
    order_book.close()
