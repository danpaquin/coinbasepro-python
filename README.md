# GDAX-Python
The Python client for the [GDAX API](https://docs.gdax.com/) (formerly known as the Coinbase Exchange API)

##### Provided under MIT License by Daniel Paquin.
*Note: this library may be subtly broken or buggy. The code is released under the MIT License – please take the following message to heart:*
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Benefits
- A simple to use python wrapper for both public and authenticated endpoints.
- In about 10 minutes, you could be programmatically trading on one of the largest Bitcoin exchanges in the *world*!
- Do not worry about handling the nuances of the API with easy-to-use methods for every API endpoint.
- Gain an advantage in the market by getting under the hood of GDAX to learn what and who is *really* behind every tick.

## Under Development
- Test Scripts **on dev branch**
- Additional Functionality for *WebsocketClient*, including a real-time order book
- FIX API Client **Looking for support**

## Getting Started
This README is documentation on the syntax of the python client presented in this repository.  **In order to use this wrapper to its full potential, you must familiarize yourself with the official GDAX documentation.**

- https://docs.gdax.com/

- You may manually install the project or use ```pip```:
```python
pip install GDAX
```

### Public Client
Only some endpoints in the API are available to everyone.  The public endpoints can be reached using ```PublicClient```

```python
import GDAX
publicClient = GDAX.PublicClient()
# Set a default product
publicClient = GDAX.PublicClient(product_id="ETH-USD")
```

### PublicClient Methods
- [getProducts](https://docs.gdax.com/#get-products)
```python
publicClient.getProducts()
```

- [getProductOrderBook](https://docs.gdax.com/#get-product-order-book)
```python
# Get the order book at the default level.
publicClient.getProductOrderBook()
# Get the order book at a specfific level.
publicClient.getProductOrderBook(level=1)
```

- [getProductTicker](https://docs.gdax.com/#get-product-ticker)
```python
# Get the product ticker for the default product.
publicClient.getProductTicker()
# Get the product ticker for a specific product.
publicClient.getProductTicker(product="ETH-USD")
```

- [getProductTrades](https://docs.gdax.com/#get-trades)
```python
# Get the product trades for the default product.
publicClient.getProductTrades()
# Get the product trades for a specific product.
publicClient.getProductTrades(product="ETH-USD")
```

- [getProductHistoricRates](https://docs.gdax.com/#get-historic-rates)
```python
publicClient.getProductHistoricRates()
# To include other parameters, see official documentation:
publicClient.getProductHistoricRates(granularity=3000)
```

- [getProduct24HrStates](https://docs.gdax.com/#get-24hr-stats)
```python
publicClient.getProduct24HrStats()
```

- [getCurrencies](https://docs.gdax.com/#get-currencies)
```python
publicClient.getCurrencies()
```

- [getTime](https://docs.gdax.com/#time)
```python
publicClient.getTime()
```

#### *In Development* JSON Parsing
Only available for the `PublicClient`, you may pass any function above raw JSON data.  This may be useful for some applications of the project and should not hinder performance, but we are looking into this.  *Do you love or hate this?  Please share your thoughts within the issue tab!*

- Both of these calls send the same request:
```python
import GDAX
publicClient = GDAX.PublicClient()

method1 = public.getProductHistoricRates(granularity='3000')

params = {
'granularity': '3000'
}
method2 = public.getProductHistoricRates(params)

# Both methods will send the same request, but not always return the same data if run in series.
print (method1, method2)
```



### Authenticated Client
Not all API endpoints are available to everyone.  Those requiring user authentication can be reached using ```AuthenticatedClient```. You must setup API access within your [account settings](https://www.gdax.com/settings/api). The ```AuthenticatedClient``` inherits all methods from the ```PrivateClient``` class, so you will only need to initialize one if you are planning to integrate both into your script.

```python
import GDAX
authClient = GDAX.AuthenticatedClient(key, b64secret, passphrase)
# Set a default product
authClient = GDAX.AuthenticatedClient(key, b64secret, passphrase, product_id="ETH-USD")
# Use the sandbox API (requires a different set of API access crudentials)
authClient = GDAX.AuthenticatedClient(key, b64secret, passphrase, api_url="https://api-public.sandbox.gdax.com")
```

### Pagination
Some calls are [paginated](https://docs.gdax.com/#pagination), meaning multiple calls must be made to receive the full set of data.  Each page/request is a list of dict objects that are then appended to a master list, making it easy to navigate pages (e.g. ```request[0]``` would return the first page of data in the example below). *This feature is under consideration for redesign.  Please provide feedback if you have issues or suggestions*
```python
request = authClient.getFills(limit=100)
request[0] # Page 1 always present
request[1] # Page 2+ present only if the data exists
```
It should be noted that limit does not behave exactly as the official documentation specifies.  If you request a limit and that limit is met, additional pages will not be returned.  This is to ensure speedy response times when less data is prefered.

### AuthenticatedClient Methods
- [getAccounts](https://docs.gdax.com/#list-accounts)
```python
authClient.getAccounts()
```

- [getAccount](https://docs.gdax.com/#get-an-account)
```python
authClient.getAccount("7d0f7d8e-dd34-4d9c-a846-06f431c381ba")
```

- [getAccountHistory](https://docs.gdax.com/#get-account-history) (paginated)
```python
authClient.getAccountHistory("7d0f7d8e-dd34-4d9c-a846-06f431c381ba")
```

- [getAccountHolds](https://docs.gdax.com/#get-holds) (paginated)
```python
authClient.getAccountHolds("7d0f7d8e-dd34-4d9c-a846-06f431c381ba")
```

- [buy & sell](https://docs.gdax.com/#place-a-new-order)
```python
# Buy 0.01 BTC @ 100 USD
buyParams = {
        'price': '100.00', #USD
        'size': '0.01', #BTC
        'product_id': 'BTC-USD'
}
authClient.buy(buyParams)
```
```python
# Sell 0.01 BTC @ 200 USD
sellParams = {
        'price': '200.00', #USD
        'size': '0.01', #BTC
        #product_id not needed if default is desired
}
authClient.sell(sellParams)
```

- [cancelOrder](https://docs.gdax.com/#cancel-an-order)
```python
authClient.cancelOrder("d50ec984-77a8-460a-b958-66f114b0de9b")
```
- [cancelAll](https://docs.gdax.com/#cancel-an-order)
```python
authClient.cancelOrder(productId='BTC-USD')
```

- [getOrders](https://docs.gdax.com/#list-orders) (paginated)
```python
authClient.getOrders()
```

- [getOrder](https://docs.gdax.com/#get-an-order)
```python
authClient.getOrder("d50ec984-77a8-460a-b958-66f114b0de9b")
```

- [getFills](https://docs.gdax.com/#list-fills) (paginated)
```python
authClient.getFills()
# Get fills for a specific order
authClient.getFills(orderId="d50ec984-77a8-460a-b958-66f114b0de9b")
# Get fills for a specific product
authClient.getFills(productId="ETH-BTC")
```

- [deposit & withdraw](https://docs.gdax.com/#depositwithdraw)
```python
# Deposit into GDAX from Coinbase Wallet
depositParams = {
        'amount': '25.00', # Currency determined by account specified
        'coinbase_account_id': '60680c98bfe96c2601f27e9c'
}
authClient.deposit(depositParams)
```
```python
# Withdraw from GDAX into Coinbase Wallet
withdrawParams = {
        'amount': '1.00', # Currency determined by account specified
        'coinbase_account_id': '536a541fa9393bb3c7000023'
}
authClient.withdraw(withdrawParams)
```

### WebsocketClient
If you would like to receive real-time market updates, you must subscribe to the [websocket feed](https://docs.gdax.com/#websocket-feed).

#### Subscribe to a single product
```python
import GDAX
# Paramters are optional
wsClient = GDAX.WebsocketClient(ws_url="wss://ws-feed.gdax.com", product_id="BTC-USD")
# Do other stuff...
wsClient.close()
```

#### Subscribe to multiple products
```python
import GDAX
# Paramters are optional
wsClient = GDAX.WebsocketClient(ws_url="wss://ws-feed.gdax.com", product_id=["BTC-USD", "ETH-USD"])
# Do other stuff...
wsClient.close()
```

### WebsocketClient Methods
The ```WebsocketClient``` subscribes in a separate thread upon initialization.  There are three methods which you could overwrite (before initialization) so it can react to the data streaming in.  The current client is a template used for illustration purposes only.

- onOpen - called once, *immediately before* the socket connection is made
- onMessage - called once for every message that arrives and accepts one argument that contains the message of dict type.
- onClose - called once after the websocket has been closed.
- close - call this method to close the websocket connection (do not overwrite).
```python
import GDAX, time
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
    print "\nMessageCount =", "%i \n" % wsClient.MessageCount
    time.sleep(1)
wsClient.close()
```

## Change Log
*0.2.2* **Current PyPI release**
- Added additional API functionality such as cancelAll() and ETH withdrawal.

*0.2.1*
- Allowed ```WebsocketClient``` to operate intuitively and restructured example workflow.

*0.2.0*
- Renamed project to GDAX-Python
- Merged Websocket updates to handle errors and reconnect

*0.1.2*
- Updated JSON handling for increased compatibility among some users
- Added support for payment methods, reports, and coinbase user accounts
- Other compatibility updates

*0.1.1b2*
- Original PyPI Release

### Recommended Additions
The following projects are suggested to improve the functionality of this project.  Please use them at your own risk as I will not take responsibility for the functionality of any of the following projects:

- [**danielktaylor/PyLimitBook**](https://github.com/danielktaylor/PyLimitBook)
   *Python implementation of fast limit-order book.*
- [**PierreRochard/coinbase-exchange-order-book**](https://github.com/PierreRochard/coinbase-exchange-order-book)
    *Real-time Coinbase Exchange order book + basic market maker bot (Python3)*
