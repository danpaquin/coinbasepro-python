# coinbase-gdax-python
A Python wrapper for the [GDAX Exchange API](https://docs.gdax.com/), formerly known as the Coinbase Exchange API

##### Provided under MIT License by Daniel Paquin.
*Note: this library may be subtly broken or buggy. The code is released under the MIT License – please take the following message to heart:*
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Benefits
- In about 10 minutes, you could be programmatically trading on one of the largest Bitcoin exchanges in the *world*!
- Do not worry about handling the nuances of the API with easy-to-use methods for every API endpoint.
- Have an advantage in the market by getting under the hood of GDAX & Coinbase to learn what and who is *really* behind every tick.

## Under Development
- Authenticated Client **testing**

## Usage
This README is only to inform you on the intricacies of the python wrapper presented in this repository.  In order to use it to its potential, you must familiarize yourself with the official documentation.
- https://docs.gdax.com/

- Afterwards, download/clone this repository into your active directory and acquire the dependencies:
```python
pip install requests
```

### Public Client
Only some endpoints in the API available to everyone.  Those endpoints can be reached using *PublicClient*

```python
import CoinbaseExchange
publicClient = CoinbaseExchange.PublicClient()
```

### Public Methods
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
# To include other paramters, see official documentation:
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