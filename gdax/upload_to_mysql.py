from gdax.order_book import OrderBook
from gdax.websocket_client import WebsocketClient
from gdax.book_recovery import BookRecovery
from gdax import translations
from gdax import mysql_dbi
from gdax import sql_defs

if __name__ == '__main__':
    db = mysql_dbi.Database()
    create_query = sql_defs.ORDER_BOOK_TABLE_DEF
    db.write(create_query)

    book_recovery = BookRecovery()

    def upload_to_mysql(message):
        global db
        global book_recovery
        messages = book_recovery.on_message(message)
        for m in messages:
            mdevent = translations.gdax_to_sqlevent(m)
            db.write_dict(sql_defs.ORDER_BOOK_TABLE_DEF, mdevent)

    ws = WebsocketClient(url="wss://ws-feed.gdax.com/", products=["BTC-USD"])
    ws.listen(upload_to_mysql)
