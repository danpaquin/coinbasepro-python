#
# cbpro/cancellation_entry.py
# Shashwat Saxena
#
# Live order logger, using updates from orderbook using Coinbase Websocket Feed


class CancellationEntry:
    def __init__(self, message, mid_price) -> None:
        self.message = message
        self.mid_price = mid_price

    @property
    def get_message(self):
        return self.message

    @property
    def get_mid_price(self):
        return self.message