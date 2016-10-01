#
# GDAX/WebsocketClient.py
# Daniel Paquin
#
# Template object to receive messages from the GDAX Websocket Feed

import json
from   threading import Thread
import time
from   websocket import create_connection

class WebsocketClient():
    def __init__(self, ws_url="wss://ws-feed.gdax.com", product_id="BTC-USD"):
        self.stop = False
        self.url = ws_url
        self.product_id = product_id
        self.thread = Thread(target=self.setup)
        self.thread.start()

    def setup(self):
        self.open()
        self.ws = create_connection(self.url)
        if type(self.product_id) is list:
            #product_ids - plural for multiple products
            subParams = json.dumps({"type": "subscribe", "product_ids": self.product_id})
        else:
            subParams = json.dumps({"type": "subscribe", "product_id": self.product_id})
        self.ws.send(subParams)
        self.listen()

    def open(self):
        print("-- Subscribed! --")

    def listen(self):
        while not self.stop:
            try:
                msg = json.loads(self.ws.recv())
            except Exception as e:
                #print e
                break
            else:
                self.message(msg)

    def message(self, msg):
        print(msg)

    def close(self):
        self.ws.close()
        self.closed()

    def closed(self):
        print("Socket Closed")

if __name__ == "__main__":
    newWS = WebsocketClient() # Runs in a separate thread
    try:
      while True:
        time.sleep(0.1)
    except KeyboardInterrupt:
      newWS.stop = True
      newWS.thread.join()
    newWS.close()
