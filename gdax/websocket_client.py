#
# gdax/WebsocketClient.py
# Daniel Paquin
#
# Template object to receive messages from the gdax Websocket Feed

import json
from threading import Thread
from websocket import create_connection, WebSocketConnectionClosedException

class WebsocketClient(object):
    def __init__(self, url="wss://ws-feed.gdax.com", products=["BTC-USD"]):
        self.url = url
        self.products = products
        self.ws = None
        self.thread = None

    def connect(self):
        if not isinstance(self.products, list):
            self.products = [self.products]

        if self.url[-1] == "/":
            self.url = self.url[:-1]

        self.ws = create_connection(self.url)
        print("-- Subscribed! --\n")

        sub_params = {'type': 'subscribe', 'product_ids': self.products}
        self.ws.send(json.dumps(sub_params))

    def poll(self):
        try:
            msg = json.loads(self.ws.recv())
        except Exception as e:
            print("Websocket unable to load message", e)
            self.close()
            sys.exit(1)
        else:
            return msg

    def listen(self, listener):
        def _go():
            self.connect()
            while True:
                listener(self.poll())

        self.thread = Thread(target=_go)
        self.thread.start()

    def close(self):
        try:
            self.ws.close()
        except WebSocketConnectionClosedException as e:
            pass
        print("\n-- Socket Closed --")

if __name__ == "__main__":
    import time

    count = 0
    def exp_counter(msg):
        global count
        count += 1
        if ((count & (count - 1)) == 0) and count != 0:
            print("MessageCount =", "%i" % count)
            if 'price' in msg and 'type' in msg:
                print("Message type:", msg["type"], "\t@ %.3f" % float(msg["price"]))

    ws = WebsocketClient(url="wss://ws-feed.gdax.com/", products=["BTC-USD", "ETH-USD"])
    ws.connect()
    print("Let's count the messages!")
    print(ws.url, ws.products)
    time.sleep(1)
    t = time.time()
    while(time.time() < t + 1000):
        exp_counter(ws.poll())
    ws.close()

