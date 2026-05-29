import ccxt
from bitmango.exchange.base_exchange import BaseExchange
from bitmango.messages import get_message

class MexcSnipeOrder(BaseExchange):
    def __init__(self, args):
        super().__init__('mexc', args)
        # MEXC specific options for defaultType
        self.exchange.options['defaultType'] = 'margin' # or 'swap' for futures

    def get_account_balance(self):
        """
        Fetches and displays account balance.
        """
        balance = self.exchange.fetch_balance(params={'type': 'margin'})
        perpetual_balance = balance['total']['USDT']
        self.display_message('info', get_message("trade.perpetual_balance", balance=perpetual_balance))
        for key in balance:
            if isinstance(balance[key], dict) and 'total' in balance[key]:
                self.display_message('info', get_message("trade.balance_asset_total", key=key, total=balance[key]['total']))
        return balance

    def create_snipe_order(self, symbol, amount, price, leverage=10):
        """
        Creates a snipe order (limit buy with stop loss).
        """
        self.exchange.load_markets()
        ticker = self.exchange.fetch_ticker(symbol)
        current_price = ticker['last']
        stop_loss = 0.95 * current_price

        try:
            order = self.exchange.create_order(symbol, 'limit', 'buy', amount, price, {
                'stopLossPrice': stop_loss,
            })
            self.display_message('info', get_message("trade.snipe_order_created", id=order.get('id')))
            return order
        except Exception as e:
            self.display_message('error', get_message("trade.snipe_order_error", error=e))
            return None
