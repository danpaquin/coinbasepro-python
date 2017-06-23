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
import GDAX as gdax
public_client = gdax.PublicClient()
# Set a default product
public_client = gdax.PublicClient(product_id="ETH-USD")
```

### PublicClient Methods
- [getProducts](https://docs.gdax.com/#get-products)
```python
public_client.getProducts()
```

- [getProductOrderBook](https://docs.gdax.com/#get-product-order-book)
```python
# Get the order book at the default level.
public_client.getProductOrderBook()
# Get the order book at a specific level.
public_client.getProductOrderBook(level=1)
```

- [getProductTicker](https://docs.gdax.com/#get-product-ticker)
```python
# Get the product ticker for the default product.
public_client.getProductTicker()
# Get the product ticker for a specific product.
public_client.getProductTicker(product="ETH-USD")
```

- [getProductTrades](https://docs.gdax.com/#get-trades)
```python
# Get the product trades for the default product.
public_client.getProductTrades()
# Get the product trades for a specific product.
public_client.getProductTrades(product="ETH-USD")
```

- [getProductHistoricRates](https://docs.gdax.com/#get-historic-rates)
```python
public_client.getProductHistoricRates()
# To include other parameters, see official documentation:
public_client.getProductHistoricRates(granularity=3000)
```

- [getProduct24HrStates](https://docs.gdax.com/#get-24hr-stats)
```python
public_client.get_product_24hr_stats()
```

- [getCurrencies](https://docs.gdax.com/#get-currencies)
```python
public_client.getCurrencies()
```

- [getTime](https://docs.gdax.com/#time)
```python
public_client.getTime()
```

#### *In Development* JSON Parsing
Only available for the `PublicClient`, you may pass any function above raw JSON data.  This may be useful for some applications of the project and should not hinder performance, but we are looking into this.  *Do you love or hate this?  Please share your thoughts within the issue tab!*

- Both of these calls send the same request:
```python
import GDAX as gdax
public_client = gdax.PublicClient()

method1 = public_client.getProductHistoricRates(granularity='3000')

params = {
'granularity': '3000'
}
method2 = public_client.getProductHistoricRates(params)

# Both methods will send the same request, but not always return the same data if run in series.
print (method1, method2)
```



### Authenticated Client

Not all API endpoints are available to everyone.
Those requiring user authentication can be reached using `AuthenticatedClient`.
You must setup API access within your
[account settings](https://www.gdax.com/settings/api).
The `AuthenticatedClient` inherits all methods from the `PublicClient`
class, so you will only need to initialize one if you are planning to
integrate both into your script.

```python
import gdax
auth_client = gdax.AuthenticatedClient(key, b64secret, passphrase)
# Set a default product
auth_client = gdax.AuthenticatedClient(key, b64secret, passphrase, product_id="ETH-USD")
# Use the sandbox API (requires a different set of API access credentials)
auth_client = gdax.AuthenticatedClient(key, b64secret, passphrase, api_url="https://api-public.sandbox.gdax.com")
```

### Pagination
Some calls are [paginated](https://docs.gdax.com/#pagination), meaning multiple calls must be made to receive the full set of data.  Each page/request is a list of dict objects that are then appended to a master list, making it easy to navigate pages (e.g. ```request[0]``` would return the first page of data in the example below). *This feature is under consideration for redesign.  Please provide feedback if you have issues or suggestions*
```python
request = auth_client.get_fills(limit=100)
request[0] # Page 1 always present
request[1] # Page 2+ present only if the data exists
```
It should be noted that limit does not behave exactly as the official documentation specifies.  If you request a limit and that limit is met, additional pages will not be returned.  This is to ensure speedy response times when less data is prefered.

### AuthenticatedClient Methods
- [getAccounts](https://docs.gdax.com/#list-accounts)
```python
auth_client.getAccounts()
```

- [getAccount](https://docs.gdax.com/#get-an-account)
```python
auth_client.getAccount("7d0f7d8e-dd34-4d9c-a846-06f431c381ba")
```

- [getAccountHistory](https://docs.gdax.com/#get-account-history) (paginated)
```python
auth_client.getAccountHistory("7d0f7d8e-dd34-4d9c-a846-06f431c381ba")
```

- [getAccountHolds](https://docs.gdax.com/#get-holds) (paginated)
```python
auth_client.getAccountHolds("7d0f7d8e-dd34-4d9c-a846-06f431c381ba")
```

- [buy & sell](https://docs.gdax.com/#place-a-new-order)
```python
# Buy 0.01 BTC @ 100 USD
auth_client.buy(price='100.00', #USD
               size='0.01', #BTC
               product_id='BTC-USD')
```
```python
# Sell 0.01 BTC @ 200 USD
auth_client.sell(price='200.00', #USD
                size='0.01', #BTC
                product_id='BTC-USD')
```

- [cancelOrder](https://docs.gdax.com/#cancel-an-order)
```python
auth_client.cancelOrder("d50ec984-77a8-460a-b958-66f114b0de9b")
```
- [cancelAll](https://docs.gdax.com/#cancel-all)
```python
auth_client.cancelAll(product='BTC-USD')
```

- [getOrders](https://docs.gdax.com/#list-orders) (paginated)
```python
auth_client.getOrders()
```

- [getOrder](https://docs.gdax.com/#get-an-order)
```python
auth_client.getOrder("d50ec984-77a8-460a-b958-66f114b0de9b")
```

- [getFills](https://docs.gdax.com/#list-fills) (paginated)
```python
auth_client.getFills()
# Get fills for a specific order
auth_client.getFills(order_id="d50ec984-77a8-460a-b958-66f114b0de9b")
# Get fills for a specific product
auth_client.getFills(product_id="ETH-BTC")
```

- [deposit & withdraw](https://docs.gdax.com/#depositwithdraw)
```python
# Deposit into GDAX from Coinbase Wallet
depositParams = {
        'amount': '25.00', # Currency determined by account specified
        'coinbase_account_id': '60680c98bfe96c2601f27e9c'
}
auth_client.deposit(depositParams)
```
```python
# Withdraw from GDAX into Coinbase Wallet
withdrawParams = {
        'amount': '1.00', # Currency determined by account specified
        'coinbase_account_id': '536a541fa9393bb3c7000023'
}
auth_client.withdraw(withdrawParams)
```

### WebsocketClient
If you would like to receive real-time market updates, you must subscribe to the [websocket feed](https://docs.gdax.com/#websocket-feed).

#### Subscribe to a single product
```python
import gdax
# Paramters are optional
wsClient = gdax.WebsocketClient(url="wss://ws-feed.gdax.com", products="BTC-USD")
# Do other stuff...
wsClient.close()
```

#### Subscribe to multiple products
```python
import gdax
# Paramters are optional
wsClient = gdax.WebsocketClient(url="wss://ws-feed.gdax.com", products=["BTC-USD", "ETH-USD"])
# Do other stuff...
wsClient.close()
```

### WebsocketClient Methods
The ```WebsocketClient``` subscribes in a separate thread upon initialization.  There are three methods which you could overwrite (before initialization) so it can react to the data streaming in.  The current client is a template used for illustration purposes only.

- onOpen - called once, *immediately before* the socket connection is made, this is where you want to add inital parameters.
- onMessage - called once for every message that arrives and accepts one argument that contains the message of dict type.
- onClose - called once after the websocket has been closed.
- close - call this method to close the websocket connection (do not overwrite).
```python
import gdax, time
class myWebsocketClient(gdax.WebsocketClient):
    def on_open(self):
        self.url = "wss://ws-feed.gdax.com/"
        self.products = ["LTC-USD"]
        self.message_count = 0
        print("Lets count the messages!")
    def on_message(self, msg):
        self.message_count += 1
        if 'price' in msg and 'type' in msg:
            print ("Message type:", msg["type"], "\t@ {}.3f".format(float(msg["price"])))
    def on_close(self):
        print("-- Goodbye! --")

wsClient = myWebsocketClient()
wsClient.start()
print(wsClient.url, wsClient.products)
while (wsClient.message_count < 500):
    print ("\nmessage_count =", "{} \n".format(wsClient.message_count))
    time.sleep(1)
wsClient.close()
```

### Real-time OrderBook
The ```OrderBook``` subscribes to a websocket and keeps a real-time record of the orderbook for the product_id input.  Please provide your feedback for future improvements.

```python
import gdax, time
order_book = gdax.OrderBook(product_id='BTC-USD')
order_book.start()
time.sleep(10)
order_book.close()
```

## Change Log
*0.3* **Current PyPI release**
- Added crypto and LTC deposit & withdraw (undocumented).
- Added support for Margin trading (undocumented).
- Enhanced functionality of the WebsocketClient.
- Soft launch of the OrderBook (undocumented).
- Minor bug squashing & syntax improvements.

*0.2.2*
- Added additional API functionality such as cancelAll() and ETH withdrawal.

*0.2.1*
- Allowed ```WebsocketClient``` to operate intuitively and restructured example workflow.

*0.2.0*
- Renamed project to GDAX-Python
- Merged Websocket updates to handle errors and reconnect.

*0.1.2*
- Updated JSON handling for increased compatibility among some users.
- Added support for payment methods, reports, and coinbase user accounts.
- Other compatibility updates.

*0.1.1b2*
- Original PyPI Release.
