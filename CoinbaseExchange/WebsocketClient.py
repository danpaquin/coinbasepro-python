#
# CoinbaseExchange/WebsocketClient.py
# Daniel Paquin
#
# Listen to the Coinbase Websocket Feed
import thread
import time
import json
from websocket import create_connection

class WebsocketClient():
    def __init__(self, ws_url="wss://ws-feed.gdax.com", product_id="BTC-USD"):
        self.url = ws_url
        self.product_id = product_id
        thread.start_new_thread(self.setup, ())

    def setup(self):
        self.open()
        self.ws = create_connection(self.url)
        subParams = json.dumps({"type": "subscribe", "product_id": self.product_id})
        self.ws.send(subParams)
        self.listen()

    def open(self):
        print "-- Subscribed! --"

    def listen(self):
        while True:
            try:
                msg = json.loads(self.ws.recv())
            except Exception as e:
                #print e
                break
            else:
                self.message(msg)

    def message(self, msg):
        print msg

    def close(self):
        self.ws.close()
        self.closed()

    def closed(self):
        print "Socket Closed"

if __name__ == "__main__":
    newWS = WebsocketClient() # Runs in a separate thread
    # Do other stuff...
    time.sleep(5)
    newWS.close()