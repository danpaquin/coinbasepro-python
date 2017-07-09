import time
import datetime

def gdax_to_sqlevent(d):

    if 'order_type' in d:
        d['type'] = d.pop('order_type')
    if 'reason' in d:
        d['type'] = d.pop('reason')
    if 'size' in d:
        d['qty'] = d.pop('size')
    if 'remaining_size' in d:
        d['qty'] = d.pop('remaining_size')
    if 'funds' in d:
        d['qty'] = d.pop('funds')
    if 'taker_order_id' in d:
        d['order_id'] = d.pop('taker_order_id')

    return {'venue': 'gdax',
            'seq': d['sequence'],
            'baseTicker': d['product_id'].split('-')[0],
            'quotedTicker': d['product_id'].split('-')[1],
            'type': d['type'],
            'px': d['price'] if 'price' in d else None,
            'qty': d['qty'],
            'side': d['side'],
            'orderId': d['order_id'],
            'makerOrderId': d['maker_order_id'] if 'maker_order_id' in d else None,
            'tradeId': d['trade_id'] if 'trade_id' in d else None,
            'exchangeTime': int(datetime.datetime.strptime(d['time'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp() *1e6),
            'receiveTime': int(time.time()*1e6),
           }

def sqlevent_to_gdax(d):
    pass
