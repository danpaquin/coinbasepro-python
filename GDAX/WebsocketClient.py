#
# GDAX/WebsocketClient.py
# Daniel Paquin
#
# Template object to receive messages from the GDAX Websocket Feed

import json, time
from   threading import Thread
from   websocket import create_connection

class WebsocketClient(object):
    def __init__(self, url="wss://ws-feed.gdax.com", products=[ "BTC-USD" ]):
        self.url = url
        if self.url[-1] == "/":
            self.url = self.url[:-1]
        self.products = products

    def start(self):
        def _go():
            self._connect()
            self._listen()

        self.onOpen()
        self.ws = create_connection(self.url)
        self.thread = Thread(target=_go)
        self.thread.start()


    def _connect(self):
        self.stop = False
        subParams = json.dumps({"type": "subscribe", "product_ids": self.products})
        self.ws.send(subParams)

    def _listen(self):
        while not self.stop:
            try:
                msg = json.loads(self.ws.recv())
            except Exception as e:
                self.onError(e)
            else:
                self.onMessage(msg)

    def close(self):
        if self.stop is False:
            self.ws.close()
            self.onClose()
        self.stop = True

    def onOpen(self):
        print("-- Subscribed! --\n")

    def onClose(self):
        print("\n-- Socket Closed --")

    def onMessage(self, msg):
        print(msg)

    def onError(self, e):
        SystemError(e)

if __name__ == "__main__":
    import GDAX
    class myWebsocketClient(GDAX.WebsocketClient):
        def onOpen(self):
            self.MessageCount = 0
            print "Lets count the messages!"
        def onMessage(self, msg):
            print "Message type:", msg["type"], "\t@ %.3f" % float(msg["price"])
            self.MessageCount += 1
        def onClose(self):
            print "-- Goodbye! --"

    wsClient = myWebsocketClient()
    wsClient.start()
    # Do some logic with the data
    while (wsClient.MessageCount < 500):
        print "\nMessageCount =", "%i \n" %wsClient.MessageCount
        time.sleep(1)
    wsClient.close()