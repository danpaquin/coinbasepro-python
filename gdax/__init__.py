from gdax.authenticated_client import AuthenticatedClient
from gdax.public_client import PublicClient
from gdax.websocket_client import WebsocketClient
from gdax.order_book import OrderBook

import json
import os

# Import API Keys
with open('credentials.json') as creds:
    credentials = json.load(creds)
    os.environ.update(credentials)
