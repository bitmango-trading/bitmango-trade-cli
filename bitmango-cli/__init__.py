import argparse
from bitmango.cli.executor import execute_command
from bitmango.output import output as output_manager

class BitMango:
    """
    Standard Python SDK for BitMango.
    Allows programmatic access to trading and market data without CLI overhead.
    """
    
    def __init__(self, exchange, sandbox=False, market_type='futures', output='json'):
        self.exchange = exchange
        self.sandbox = sandbox
        self.market_type = market_type
        
        # Configure output manager for SDK usage
        output_manager.json_mode = (output == 'json')
        # In SDK mode, we should default to no colors if redirected
        output_manager.use_colors = False

    def _create_args(self, command, **kwargs):
        """Helper to create a namespace that looks like CLI args."""
        d = {
            "command": command,
            "exchange": self.exchange,
            "sandbox": self.sandbox,
            "market_type": self.market_type,
            "no_confirm": True, # Always auto-confirm in SDK
            "output": "json",
            "verbose": kwargs.get('verbose', False)
        }
        d.update(kwargs)
        return argparse.Namespace(**d)

    def balance(self):
        """Returns the current account balance."""
        args = self._create_args('account', positions=False)
        return execute_command(args, output_manager)

    def positions(self):
        """Returns open positions."""
        args = self._create_args('account', positions=True)
        return execute_command(args, output_manager)

    def ticker(self, pair):
        """Returns market ticker for a pair."""
        args = self._create_args('ticker', pair=pair)
        return execute_command(args, output_manager)

    def ohlcv(self, pair, timeframe='1h', limit=10, rsi=None, ema=None):
        """Returns historical candlestick data."""
        args = self._create_args('ohlcv', pair=pair, timeframe=timeframe, limit=limit, rsi=rsi, ema=ema)
        return execute_command(args, output_manager)

    def buy(self, pair, size, order_type='market', price=None, wait=False):
        """Places a buy order."""
        args = self._create_args('entry', direction='buy', pair=pair, size=size, order_type=order_type, price=price, wait=wait)
        return execute_command(args, output_manager)

    def sell(self, pair, size, order_type='market', price=None, wait=False):
        """Places a sell order."""
        args = self._create_args('entry', direction='sell', pair=pair, size=size, order_type=order_type, price=price, wait=wait)
        return execute_command(args, output_manager)

    def cancel_all(self, pair=None):
        """Cancels all open orders."""
        args = self._create_args('cancel', cancel_command='all', pair=pair)
        return execute_command(args, output_manager)
