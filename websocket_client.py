# gdax/WebsocketClient.py
# original author: Daniel Paquin
# mongo "support" added by Drew Rice
#
#
# Template object to receive messages from the gdax Websocket Feed

from __future__ import print_function
import json
import base64
import hmac
import hashlib
import time
import socket
import errno
import datetime
from threading import Thread
from websocket import create_connection, WebSocketConnectionClosedException
from pymongo import MongoClient 
from Connections.gdax.gdax_auth import get_auth_headers
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE,SIG_DFL) # this ignores the errno 32, broken pipe

class WebsocketClient(object):
    def __init__(self, url="wss://ws-feed.gdax.com", products=None, message_type="subscribe", channels=None, should_print=False, auth=False, key=None, 
            b64secret=None, passphrase=None, mongo_collection=None, persist=False):
        self.url = url
        self.products = products
        self.channels = channels
        self.type = message_type
        self.stop = False
        self.error = None
        self.ws = None
        self.thread = None
        self.auth = auth
        self.api_key = key
        self.api_secret = b64secret
        self.api_passphrase = passphrase
        self.should_print = should_print
        self.mongo_collection = mongo_collection
        self.persist = persist
        if self.persist:
            self.data = []
        else:
            self.data = None

    def start(self):
        def _go():
            self._connect()
            self._listen()
            self._disconnect()
            if not self.stop:
                print("Attempting to reconnect websocket {}".format(self.channels))
                _go()

        self.stop = False
        self.on_open()
        self.thread = Thread(target=_go)
        self.thread.start()
    

    def _connect(self):
        if self.products is None:
            self.products = ["BTC-USD"]
        elif not isinstance(self.products, list):
            self.products = [self.products]
        # added
        if not isinstance(self.channels, list):
            self.channels = [self.channels]

        if self.url[-1] == "/":
            self.url = self.url[:-1]

        if self.channels is None:
            sub_params = {'type': 'subscribe', 'product_ids': self.products}
        else:
            sub_params = {'type': 'subscribe', 'product_ids': self.products, 'channels': self.channels}

        if self.auth:
            timestamp = str(time.time())
            message = timestamp + 'GET' + '/users/self/verify'
            message = message.encode('ascii')
            hmac_key = base64.b64decode(self.api_secret)
            signature = hmac.new(hmac_key, message, hashlib.sha256)
            signature_b64 = base64.b64encode(signature.digest()).decode('utf-8').rstrip('\n')
            sub_params['signature'] = signature_b64
            sub_params['key'] = self.api_key
            sub_params['passphrase'] = self.api_passphrase
            sub_params['timestamp'] = timestamp
        
        if self.stop:
            return

        try:
            self.ws = create_connection(self.url)
            self.ws.send(json.dumps(sub_params))
        except Exception:
            print("Failed to connect.. Trying again in 10 seconds...")
            time.sleep(10)
            self._connect()
        else:
            print("Connected")
        

    def keepalive(self, interval=25):
        last_update_time = time.time()
        while not self.stop and self.ws:
            try:
                time.sleep(1)
                current_time = time.time()
                if self.ws and (current_time - last_update_time) >= interval:
                    self.ws.ping("keepalive")
                    last_update_time = current_time
            except Exception as e:
                print("{}: Error encountered while pinging the server: {}".format(datetime.datetime.now(), e))
                raise Exception(e)


    def _listen(self):
        keepalive = Thread(target=self.keepalive)
        keepalive.start()
        while not self.stop:
            try:
                data = self.ws.recv()
                msg = json.loads(data)
            except (WebSocketConnectionClosedException, ValueError, Exception) as e:
                if not self.stop:
                   self.on_error(e)
                break
            else:
                self.on_message(msg)
        keepalive.join()


    def _disconnect(self):
        try:
            if self.ws:
                if self.type == "heartbeat":
                    self.ws.send(json.dumps({"type": "heartbeat", "on": False}))
                self.close()
        except Exception as e:
            print("Error while disconnecting:\n     {}".format(e))
            pass
        else:
            self.on_close()

    def close(self):
        try:
            print("Closing websocket connection for channel(s) {}".format(', '.join(self.channels)))
            self.stop = True
            self.ws.abort()
            self.ws = None
            self.thread.join()
        except Exception as e:
            print("Error occured while attempting to close the connection: \n     {}".format(e))

    def on_open(self):
        if self.should_print:
            print("-- Subscribed! --\n")

    def on_close(self):
        if self.should_print:
            print("\n-- Socket Closed --")

    def on_message(self, msg):
        if msg['type'] != "subscriptions":
            if self.persist:
                self.data.append(msg)
            else:
                self.data = msg
        if self.should_print:
            print(msg)
        if self.mongo_collection:  # dump JSON to given mongo collection
            self.mongo_collection.insert_one(self.data)

    def on_error(self, e, data=None):
        self.error = e
        print('{}: {} - data: {}'.format(datetime.datetime.now(), e, data))
        

if __name__ == "__main__":
    import sys
    import gdax
    import time

    class MyWebsocketClient(gdax.WebsocketClient):
        def on_open(self):
            self.url = "wss://ws-feed.gdax.com/"
            self.products = ["BTC-USD", "ETH-USD"]
            self.message_count = 0
            print("Let's count the messages!")

        def on_message(self, msg):
            print(json.dumps(msg, indent=4, sort_keys=True))
            self.message_count += 1

        def on_close(self):
            print("-- Goodbye! --")


    wsClient = MyWebsocketClient()
    wsClient.start()
    print(wsClient.url, wsClient.products)
    try:
        while True:
            print("\nMessageCount =", "%i \n" % wsClient.message_count)
            time.sleep(1)
    except KeyboardInterrupt:
        wsClient.close()

    if wsClient.error:
        sys.exit(1)
    else:
        sys.exit(0)
