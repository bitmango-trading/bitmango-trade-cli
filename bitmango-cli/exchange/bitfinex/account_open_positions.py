import sys
from bitmango.exchange.base_exchange import BaseExchange
from bitmango.output import display_message
from bitmango.exchange.exchange_errors import UnsupportedError
from bitmango.messages import get_message

class BitfinexAccountPositions(BaseExchange):
    def __init__(self, args):
        super().__init__('bitfinex', args)

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

    def fetch_open_orders(self, args):
        """
        Fetch open orders.
        """
        return super().fetch_open_orders(args)

    def query_order_book(self, args):
        return super().query_order_book(args)

    def entry(self, args):
        """
        Places an entry order (Spot/Margin/Derivative).
        """
        symbol = self._adapt_pair(args.pair)
        side = 'buy' if args.direction in ['buy', 'long'] else 'sell'
        order_type = args.order_type
        size = float(args.size)
        price = float(args.price) if args.price else None
        
        params = {}
        # Bitfinex uses 'type' in params to distinguish between 'exchange' (spot) and 'margin'
        # CCXT usually handles this via options['defaultType'], but we can be explicit.
        market_type = getattr(self.args, 'market_type', 'spot')
        
        if market_type == 'spot':
            # Bitfinex V2 types: 'exchange market', 'exchange limit', 'market', 'limit'
            if order_type == 'market':
                bitfinex_type = 'exchange market'
            else:
                bitfinex_type = 'exchange limit'
        else:
            # Margin or Derivatives
            if order_type == 'market':
                bitfinex_type = 'market'
            else:
                bitfinex_type = 'limit'
                
        # We use CCXT's create_order which handles the type translation usually
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
        Bitfinex handles leverage differently (it's often a per-order or per-account setting).
        For V2, leverage can be set per position.
        """
        symbol = self._adapt_pair(args.pair)
        leverage = int(args.leverage)
        msg = get_message("trade.set_leverage", leverage=leverage, symbol=symbol)
        display_message('action_start', msg)
        try:
            # Try CCXT unified method
            res = self.exchange.set_leverage(leverage, symbol)
            display_message('action_stop', msg, result_icon="✓")
            return res
        except Exception as e:
            # Fallback for Bitfinex: it might not be supported via a simple call
            display_message('action_stop', msg, result_icon="❌")
            display_message('error', get_message("exchange.bitfinex_leverage_error", error=e))
            return None

    def set_margin_mode(self, args):
        """
        Bitfinex doesn't have a 'cross' vs 'isolated' toggle like Binance; 
        it depends on whether you use the 'Margin' wallet (isolated-ish) or 'Derivatives' (cross).
        """
        display_message('warning', get_message("exchange.bitfinex_margin_mode_warning"))
        return None

    def fetch_funding_rate(self, args):
        """
        Fetches the current funding rate.
        """
        return super().fetch_funding_rate(args)
