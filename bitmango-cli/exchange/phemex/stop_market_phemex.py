import argparse
import sys
import time
from ccxt import phemex as Exchange
from api_keys import API_KEYS
from bitmango.exchange.base_exchange import BaseExchange # Import BaseExchange

class PhemexStopMarket(BaseExchange):
    def __init__(self, args):
        super().__init__('phemex', args) # Initialize BaseExchange with exchange_name 'phemex'

    def stop(self, args):
        """
        Places a stop-market order on Phemex.
        """
        current_price = float(args.current_price)
        stop_loss_percentage = float(args.stop_loss_percentage)
        take_profit_percentage = float(args.take_profit_percentage)
        order_type = args.order_type # 'stop_loss' or 'take_profit'

        is_buy = args.direction in ['buy', 'long']

        if is_buy: # Long position
            stop_loss_price = current_price * (1 - stop_loss_percentage)
            take_profit_price = current_price * (1 + take_profit_percentage)
        else: # Short position
            stop_loss_price = current_price * (1 + stop_loss_percentage)
            take_profit_price = current_price * (1 - take_profit_percentage)

        if order_type == 'stop_loss':
            trigger_price_float = stop_loss_price
            trigger_direction = 'descending' if is_buy else 'ascending'
        elif order_type == 'take_profit':
            trigger_price_float = take_profit_price
            trigger_direction = 'descending' if is_buy else 'ascending' # Changed for take profit
        else:
            raise ValueError("order_type must be 'stop_loss' or 'take_profit'")

        pair = self._adapt_pair(args.pair)
        
        # For a stop-market order, the price is 0, and we use a trigger.
        order_price = 0 
        
        market_symbol = pair # Phemex uses symbols like 'BTC/USDT:USDT'
        side = 'sell' if is_buy else 'buy' # Corrected: exit trade direction
        
        from bitmango.messages import get_message
        self.display_message('info', get_message("trade.placing_order", side=side.upper(), type=order_type.upper(), amount=args.size, symbol=pair, exchange="Phemex"))
        
        # Ensure size and price are floats
        size_float = float(args.size)
        
        # Format trigger_price_float to string with 1 decimal place
        formatted_trigger_price = f"{trigger_price_float:.1f}"

        params = {'stopPrice': formatted_trigger_price, 'triggerDirection': trigger_direction}
        
        order_result = self._execute_order(market_symbol, 'market', side, size_float, trigger_price_float, params)
        return order_result # Return the order_result
