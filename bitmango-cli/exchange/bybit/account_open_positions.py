import sys
from bitmango.exchange.base_exchange import BaseExchange
from bitmango.output import display_message
from bitmango.exchange.exchange_errors import UnsupportedError

class BybitAccountPositions(BaseExchange):
    def __init__(self, args):
        super().__init__('bybit', args)

    def ledger(self, args):
        """
        Fetches account ledger.
        """
        return self.fetch_ledger(args)

    def markets(self, args):
        """
        List available markets.
        """
        return super().markets(args)

    def history(self, args):
        """
        Order history.
        """
        return super().history(args)

    def ticker(self, args):
        """
        Standardized ticker.
        """
        return super().ticker(args)

    def ohlcv(self, args):
        """
        Standardized OHLCV.
        """
        return super().ohlcv(args)

    def fetch_open_orders(self, args):
        """
        Fetch open orders.
        """
        return super().fetch_open_orders(args)

    def query_order_book(self, args):
        return super().query_order_book(args)

    def entry(self, args):
        """
        Places an entry order.
        """
        symbol = self._adapt_pair(args.pair)
        side = 'buy' if args.direction in ['buy', 'long'] else 'sell'
        order_type = args.order_type
        size = float(args.size)
        price = float(args.price) if args.price else None
        
        params = {}
        return self._execute_order(symbol, order_type, side, size, price, params)

    def exit(self, args):
        """
        Places an exit order (reduce-only).
        """
        symbol = self._adapt_pair(args.pair)
        side = 'buy' if args.direction in ['buy', 'long'] else 'sell'
        order_type = args.order_type
        size = float(args.size)
        price = float(args.price) if args.price else None
        
        params = {'reduceOnly': True}
        return self._execute_order(symbol, order_type, side, size, price, params)

    def set_leverage(self, args):
        """
        Standard leverage setter.
        """
        return super().set_leverage(args)

    def set_margin_mode(self, args):
        """
        Standard margin mode setter.
        """
        return super().set_margin_mode(args)

    def transfer(self, args):
        """
        Transfers funds between accounts.
        """
        return super().transfer(args)

    def fetch_funding_rate(self, args):
        """
        Fetches the current funding rate.
        """
        return super().fetch_funding_rate(args)
