from cbpro.websocket_client import WebsocketClient
from cbpro.public_client import PublicClient
import sys
import time
from pymongo import MongoClient
import urllib.parse

class mongoSyncGdax(WebsocketClient):

	def __init__(self, product_id="BTC-USD", username=None, password=None, database="Coinbase", url='mongodb://localhost:27017/'):
		super(mongoSyncGdax, self).__init__(products=product_id)

		self.mongocollection = product_id.replace("-","_")
		self.database = database
		if (username and password):
			self.username = urllib.parse.quote_plus(username)
			self.password = urllib.parse.quote_plus(password)
			self.mongo_client = MongoClient(url)
			self.db = self.mongo_client[database]
			self.db.authenticate(self.username, self.password)
		else:
			self.mongo_client = MongoClient(url)
			self.db = self.mongo_client[database]

		self.MCBids = self.db[self.mongocollection+"_CB_Bids"]
		self.MCAsks = self.db[self.mongocollection+"_CB_Asks"]
		self._sequence = -1
		self._client = PublicClient()
		self.product_id= product_id


	def on_open(self):
		self._sequence = -1
		print("Syncronizing to Mongo-database:", self.database, "Crypto:", self.product_id)

	def on_close(self):
		print("Sync Stopped")

	def reset_book(self):
		self.MCBids.drop()
		self.MCAsks.drop()
		res = self._client.get_product_order_book(product_id=self.product_id, level=3)
		for bid in res['bids']:
			self.add({
				'id': bid[2],
				'side': 'buy',
				'price': float(bid[0]),
				'size': float(bid[1])
			})
		for ask in res['asks']:
			self.add({
				'id': ask[2],
				'side': 'sell',
				'price': float(ask[0]),
				'size': float(ask[1])
			})

		self._sequence = res['sequence']
		print("reseted "+(str(self.product_id)))

	def on_message(self, message):

		sequence = message.get('sequence', -1)
		if self._sequence == -1:
			self.reset_book()
			return
		if sequence <= self._sequence:
			# ignore older messages (e.g. before order book initialization from getProductOrderBook)
			return
		elif sequence > self._sequence + 1:
			self.reset_book()
			print("Reseting Book due to Gap on Sequence Number")
			return

		msg_type = message['type']
		if msg_type == 'open':
			self.add(message)
		elif msg_type == 'done' and 'price' in message:
			self.remove(message)
			pass
		elif msg_type == 'match':
			self.match(message)
			print("match "+(str(self.product_id)))
		elif msg_type == 'change':
			self.change(message)
			print("change "+(str(self.product_id)))
		self._sequence = sequence

	def change(self, order):

		new_size = order['new_size'] or order['new_funds']

		oid = order['order_id']

		if (order['side'] == 'buy'):
			self.MCBids.update_one(
				{'_id': oid},
			 	{'$set': {'size': new_size}}
			 	)
		else:
			self.MCAsks.update_one(
				{'_id': oid},
			 	{'$set': {'size': new_size}}
			 	)


	def add(self, order):

		order = {
			'_id': order.get('order_id') or order['id'],
			'side': order['side'],
			'price': float(order['price']),
			'size': float(order.get('size') or order['remaining_size'])
		}

		if order['side'] == 'buy':
			self.MCBids.insert_one(order)

		else:
			self.MCAsks.insert_one(order)

	def remove(self, order):
		oid =  order.get('order_id') or order['id']

		if (order['side'] == "buy"):
			self.MCBids.delete_one({'_id':oid})
		else:
			self.MCAsks.delete_one({'_id':oid})

	def match(self,order):
		moid = order.get('maker_order_id')

		if (order['side'] == "buy"):
			self.MCBids.delete_one({'_id':moid})
		else:
			self.MCAsks.delete_one({'_id':moid})

if __name__ == '__main__':
	import time
	ETHBTC = mongoSyncGdax(product_id="ETH-BTC", database="Coinbase", username="user", password="password")
	BTCUSD = mongoSyncGdax(product_id="BTC-USD", database="Coinbase", username="user", password="password")
	LTCUSD = mongoSyncGdax(product_id="LTC-USD", database="Coinbase", username="user", password="password")
	BCHUSD = mongoSyncGdax(product_id="BCH-USD", database="Coinbase", username="user", password="password")
	ETHUSD = mongoSyncGdax(product_id="ETH-USD", database="Coinbase", username="user", password="password")
	BCHBTC = mongoSyncGdax(product_id="BCH-BTC", database="Coinbase", username="user", password="password")


	BTCUSD.start()
	time.sleep(45)
	LTCUSD.start()
	time.sleep(45)
	BCHUSD.start()
	time.sleep(45)
	ETHUSD.start()
	time.sleep(45)
