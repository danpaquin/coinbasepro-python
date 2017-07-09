from gdax.public_client import PublicClient

class BookRecovery():
    def __init__(self):
        self._client = PublicClient()
        self._sequence = None

    def on_message(self, message):
        sequence = message['sequence']
        if self._sequence is None:
            messages = []
            res = self._client.get_product_order_book(product_id=message['product_id'], level=3)
            for bid in res['bids']:
                order = {
                    'sequence': res['sequence'],
                    'type': 'open',
                    'product_id': message['product_id'],
                    'id': bid[2],
                    'side': 'buy',
                    'price': bid[0],
                    'size': bid[1],
                }
                messages.append(order)
            for ask in res['asks']:
                order = {
                    'sequence': res['sequence'],
                    'type': 'open',
                    'id': ask[2],
                    'side': 'sell',
                    'price': ask[0],
                    'size': ask[1],
                }
                messages.append(order)
            self._sequence = res['sequence']
            assert sequence <= self._sequence
            return messages

        if sequence <= self._sequence:
            return []
        if sequence == self._sequence + 1:
            self._sequence = sequence
            return [message]
        if sequence > self._sequence + 1:
            self.close()
            raise Exception('Error: messages missing ({} - {}). Exiting.'.format(sequence, self._sequence))

if __name__ == '__main__':
    import time
    import datetime as dt
    from gdax.book_builder import BookBuilder
    from gdax.websocket_client import WebsocketClient

    # latest values of bid-ask spread

    last_bid = None
    last_ask = None
    last_bid_depth = None
    last_ask_depth = None
    book_builder = BookBuilder()
    book_recovery = BookRecovery()

    def on_message(order):
        global last_bid
        global last_ask
        global last_bid_depth
        global last_ask_depth
        global book_builder
        global book_recovery
        messages = book_recovery.on_message(order)
        for message in messages:
            book_builder.handle(message)
        for message in messages:
            # Calculate newest bid-ask spread
            bid = book_builder.get_bid()
            bids = book_builder.get_bids(bid)
            bid_depth = sum([b['size'] for b in bids])
            ask = book_builder.get_ask()
            asks = book_builder.get_asks(ask)
            ask_depth = sum([a['size'] for a in asks])

            if last_bid == bid and last_ask == ask and last_bid_depth == bid_depth and last_ask_depth == ask_depth:
                pass
            else:
                last_bid = bid
                last_ask = ask
                last_bid_depth = bid_depth
                last_ask_depth = ask_depth
                print('{}\tbid: {:.3f} @ {:.2f}\task: {:.3f} @ {:.2f}'.format(dt.datetime.now(), bid_depth, bid,
                                                                      ask_depth, ask))

    ws = WebsocketClient(url="wss://ws-feed.gdax.com/", products=["BTC-USD"])
    ws.listen(on_message)
    time.sleep(1000)
    ws.close()
