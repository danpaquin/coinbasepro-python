#
# CoinbaseExchange/WebsocketClient.py
# Daniel Paquin
#
# Listen to the Coinbase Websocket Feed
import websocket
import thread
import time
import json

class WebsocketClient():
    pass

def on_message(ws, message):
    msg = json.loads(message)
    print msg['type']


def on_error(ws, error):
    print "### socket error###"
    print error


def on_close(ws):
    print "### socket closed ###\n"


def on_open(ws):
    # Setup Environment

    print "\n### socket opened ###"

    subscribe = json.dumps({
        "type": "subscribe",
        "product_id": "BTC-USD"
    })

    ws.send(subscribe)

    def run(*args):
        # While running...
        print "tread starting..."
        time.sleep(10)
        ws.close()
        print "thread terminating..."

    thread.start_new_thread(run, ())

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://ws-feed.exchange.coinbase.com",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open

    ws.run_forever()
