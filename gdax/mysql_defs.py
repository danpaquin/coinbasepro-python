ORDER_BOOK_TABLE_NAME = "orderBook"
ORDER_BOOK_TABLE_DEF = """
CREATE TABLE IF NOT EXISTS %s (
  venue VARCHAR(15),
  seq BIGINT,
  baseTicker VARCHAR(6),
  quotedTicker VARCHAR(6),
  type ENUM('limit', 'market', 'open', 'filled', 'canceled', 'match', 'change'),
  px DOUBLE,
  qty DOUBLE,
  side ENUM('buy', 'sell'),
  orderId BIGINT,
  makerOrderId BIGINT,
  tradeId BIGINT,
  exchangeTime BIGINT,
  receiveTime BIGINT,
  PRIMARY KEY(receiveTime)
)
""" % ORDER_BOOK_TABLE_NAME

POLONIEX_TICKER_TABLE_DEF = """
CREATE TABLE IF NOT EXISTS ticker (
  currencyPair VARCHAR(13),
  last DOUBLE,
  lowestAsk DOUBLE,
  highestBid DOUBLE,
  percentChange DOUBLE,
  baseVolume DOUBLE,
  quoteVolume DOUBLE,
  isFrozen integer,
  lastDayHigh DOUBLE,
  lastDayLow DOUBLE
)
"""

