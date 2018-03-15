#!/usr/bin/env python

import gdax
from gdax_config import settings

def client():
    return gdax.AuthenticatedClient(settings.api_key, settings.api_secret, settings.passphrase)

if __name__=='__main__':
    client = client()
    print(client.get_product_historic_rates("BCH-BTC"))