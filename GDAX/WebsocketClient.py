#
# GDAX/WebsocketClient.py
# Daniel Paquin
#
# Template object to receive messages from the GDAX Websocket Feed

from __future__ import print_function
import json
import time
from threading import Thread
from websocket import create_connection

class WebsocketClient(object):
    def __init__(self, url=None, products=None, type=None):
        if url is None:
            url = "wss://ws-feed.gdax.com"

        self.url = url
        self.products = products
        self.type = "subscribe" #type or "subscribe"
        self.stop = False
        self.ws = None
        self.thread = None

    def start(self):
        def _go():
            self._connect()
            self._listen()

        self.onOpen()
        self.ws = create_connection(self.url)
        self.thread = Thread(target=_go)
        self.thread.start()

    def _connect(self):
        if self.products is None:
            self.products = ["BTC-USD"]
        elif not isinstance(self.products, list):
            self.products = [self.products]

        if self.url[-1] == "/":
            self.url = self.url[:-1]

        self.stop = False
        sub_params = {'type': 'subscribe', 'product_ids': self.products}
        self.ws.send(json.dumps(sub_params))
        if self.type == "heartbeat":
            sub_params = {"type": "heartbeat", "on": True}
            self.ws.send(json.dumps(sub_params))

    def _listen(self):
        while not self.stop:
            try:
                msg = json.loads(self.ws.recv())
            except Exception as e:
                self.onError(e)
                self.close()
            else:
                self.onMessage(msg)

    def close(self):
        if not self.stop:
            if self.type == "heartbeat":
                self.ws.send(json.dumps({"type": "heartbeat", "on": False}))
            self.onClose()
            self.stop = True
            #self.thread = None
            self.ws.close()

    def onOpen(self):
        print("-- Subscribed! --\n")

    def onClose(self):
        print("\n-- Socket Closed --")

    def onMessage(self, msg):
        print(msg)

    def onError(self, e):
        SystemError(e)


if __name__ == "__main__":
    import GDAX, time
    class myWebsocketClient(GDAX.WebsocketClient):
        def onOpen(self):
            self.url = "wss://ws-feed.gdax.com/"
            self.products = ["BTC-USD", "ETH-USD"]
            self.MessageCount = 0
            print ("Lets count the messages!")

        def onMessage(self, msg):
            print ("Message type:", msg["type"], "\t@ %.3f" % float(msg["price"]))
            self.MessageCount += 1

        def onClose(self):
            print ("-- Goodbye! --")

    wsClient = myWebsocketClient()
    wsClient.start()
    print(wsClient.url, wsClient.products)
    # Do some logic with the data
    while (wsClient.MessageCount < 500):
        print("\nMessageCount =", "%i \n" % wsClient.MessageCount)
        time.sleep(1)
    wsClient.close()
