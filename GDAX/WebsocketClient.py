#
# GDAX/WebsocketClient.py
# Daniel Paquin
#
# Template object to receive messages from the GDAX Websocket Feed

import json, time
from   threading import Thread
from   websocket import create_connection

class WebsocketClient(object):
    def __init__(self, ws_url="wss://ws-feed-public.sandbox.gdax.com", product_id="BTC-USD"):
        if ws_url[-1] == "/":
            self.url = ws_url[:-1]
        else:
            self.url = ws_url
        self.product_id = product_id

        def go():
            self.connect()
            self.listen()

        self.thread = Thread(target=go)
        self.thread.start()

    def connect(self):
        self.open()
        self.stop = False
        self.ws = create_connection(self.url)
        if type(self.product_id) is list:
            #product_ids - plural for multiple products
            subParams = json.dumps({"type": "subscribe", "product_ids": self.product_id})
        else:
            subParams = json.dumps({"type": "subscribe", "product_id": self.product_id})
        self.ws.send(subParams)

    def open(self):
        print("-- Subscribed! --")

    def listen(self):
        while not self.stop:
            try:
                msg = json.loads(self.ws.recv())
            except Exception as e:
                self.on_error(e)
            else:
                self.message(msg)

    def on_error(self, e):
        self.close()

    def message(self, msg):
        print(msg)

    def close(self):
        self.stop = True
        if self.ws and self.ws.connected:
            self.ws.close()
        self.ws = None
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
