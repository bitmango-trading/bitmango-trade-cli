import ccxt
from bitmango.exchange.base_exchange import BaseExchange

class BinanceBuySpreadOrder(BaseExchange):
    def __init__(self, args):
        super().__init__('binance', args)
        # Override defaultType for spot orders if needed
        self.exchange.options['defaultType'] = 'spot'

    def get_total_balance(self, currency):
        """
        Function to get total free balance.
        """
        balances = self.exchange.fetch_balance()
        return balances['free'][currency]

    def create_buy_order(self, symbol, price, amount):
        """
        Function to place a buy order.
        """
        return self.exchange.create_order(symbol, 'LIMIT', 'BUY', amount, price)

    def cancel_order(self, order_id, symbol):
        """
        Function to cancel order.
        """
        return self.exchange.cancel_order(order_id, symbol)

    # The main logic from the original file is removed as this is now a class providing methods.
    # The logic for placing spread orders should be handled by a higher-level strategy.