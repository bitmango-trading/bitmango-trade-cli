import importlib
import sys
import time 
from bitmango.output import display_message, start_boxed_mode, stop_boxed_mode, output as output_manager
from bitmango.exchange.functions import get_exchange_class
from bitmango.license import require_pro
from bitmango.messages import get_message

def execute_stop_order(exchange_name, args):
    """
    Dispatches stop order execution to the appropriate logic (native, trailing, ghost).
    """
    try:
        # Default to native if no type or native specified
        stop_type = getattr(args, 'stop_type', 'native')
        
        if getattr(args, 'smart_stop', False):
            require_pro("Smart Stops")
            return run_smart_stop(exchange_name, args)

        if stop_type == 'native':
            return run_native_stop(exchange_name, args)
        elif stop_type == 'trailing':
            return run_trailing_stop(exchange_name, args)
        elif stop_type == 'ghost':
            require_pro("Ghost Stops")
            return run_ghost_stop(exchange_name, args)
        else:
            display_message('error', get_message("stop.unsupported_type", type=stop_type))
            raise ValueError(f"Unsupported stop type: {stop_type}")

    except Exception as e:
        if output_manager.json_mode: raise e
        display_message('error', get_message("stop.execution_error", error=e))
        from bitmango.output import display_traceback
        display_traceback()
        raise e

def run_native_stop(exchange_name, args):
    """Places a native exchange-side stop order."""
    ExchangeClass = get_exchange_class(exchange_name, command='stop')
    if not ExchangeClass:
        display_message('error', get_message("exchange.no_implementation", exchange=exchange_name))
        raise ValueError(f"No implementation found for exchange {exchange_name}")

    exchange_instance = ExchangeClass(args)
    # Map 'stop' to stop_market logic
    order_result = exchange_instance.stop_market(args)
    if order_result:
        market_symbol = exchange_instance._adapt_pair(args.pair)
        exchange_instance.verify_order_fulfillment(market_symbol, order_result, 'stop')
    return order_result

def run_trailing_stop(exchange_name, args):
    """Executes a CLI-side trailing stop."""
    ExchangeClass = get_exchange_class(exchange_name, command='stop')
    exchange_instance = ExchangeClass(args)
    market_symbol = exchange_instance._adapt_pair(args.pair)
    
    is_buy_order = args.direction in ['buy', 'long']
    current_price = exchange_instance._fetch_current_price(market_symbol, is_buy_order)
    peak_price = current_price
    
    # Use callback percentage if provided
    callback = getattr(args, 'callback_percentage', 0.01)
    if not callback: callback = 0.01 # default 1%
    
    # If we are BUYING to exit, we are in a SHORT position. 
    #   Trigger is ABOVE us (peak is the minimum).
    # If we are SELLING to exit, we are in a LONG position.
    #   Trigger is BELOW us (peak is the maximum).
    if is_buy_order:
        trigger_price = current_price * (1 + callback)
    else:
        trigger_price = current_price * (1 - callback)

    display_message('info', get_message("stop.trailing_start", symbol=args.pair))
    display_message('info', get_message("stop.side", side='SHORT' if is_buy_order else 'LONG'))
    display_message('info', get_message("stop.trailing_initial", price=current_price, trigger=trigger_price))

    try:
        while True:
            msg = get_message("stop.monitoring", symbol=args.pair, price=current_price, item="Stop", trigger=trigger_price)
            display_message('action_start', msg)
            current_price = exchange_instance._fetch_current_price(market_symbol, is_buy_order)
            
            updated = False
            if not is_buy_order: # LONG Position (Peak is Maximum)
                if current_price > peak_price:
                    peak_price = current_price
                    new_trigger = peak_price * (1 - callback)
                    if new_trigger > trigger_price:
                        trigger_price = new_trigger
                        updated = True
                if current_price <= trigger_price:
                    display_message('action_stop', get_message("stop.triggered", type="TRAILING", price=current_price, direction="<=", trigger=trigger_price), result_icon="💥")
                    break
            else: # SHORT Position (Peak is Minimum)
                if current_price < peak_price:
                    peak_price = current_price
                    new_trigger = peak_price * (1 + callback)
                    if new_trigger < trigger_price:
                        trigger_price = new_trigger
                        updated = True
                if current_price >= trigger_price:
                    display_message('action_stop', get_message("stop.triggered", type="TRAILING", price=current_price, direction=">=", trigger=trigger_price), result_icon="💥")
                    break
            
            if updated:
                display_message('action_stop', get_message("stop.trailing_update", peak=peak_price, trigger=trigger_price), result_icon="📈")
            else:
                display_message('action_stop', msg, result_icon="⏳")
            
            # Use faster polling for tests if needed, otherwise 5s
            time.sleep(float(getattr(args, 'poll_interval', 5)))
    except KeyboardInterrupt:
        display_message('warning', get_message("stop.suspended", type="Trailing"))
        return

    display_message('info', get_message("stop.market_exit"))
    args.order_type = 'market'
    return exchange_instance.entry(args)

def run_ghost_stop(exchange_name, args):
    """Executes a CLI-side ghost stop."""
    ExchangeClass = get_exchange_class(exchange_name, command='stop')
    exchange_instance = ExchangeClass(args)
    market_symbol = exchange_instance._adapt_pair(args.pair)
    is_buy_order = args.direction in ['buy', 'long']
    
    # Use stop price as trigger
    trigger_price = float(args.stop_price)

    display_message('info', get_message("stop.ghost_start", symbol=args.pair, price=trigger_price))
    display_message('info', get_message("stop.side", side='SHORT' if is_buy_order else 'LONG'))
    
    try:
        while True:
            current_price = exchange_instance._fetch_current_price(market_symbol, is_buy_order)
            msg = get_message("stop.monitoring", symbol=args.pair, price=current_price, item="Trigger", trigger=trigger_price)
            display_message('action_start', msg)
            
            # If LONG (is_buy_order is False), trigger if price drops below stop
            # If SHORT (is_buy_order is True), trigger if price rises above stop
            triggered = (not is_buy_order and current_price <= trigger_price) or \
                        (is_buy_order and current_price >= trigger_price)
            
            if triggered:
                display_message('action_stop', get_message("stop.triggered", type="GHOST", price=current_price, direction="hit trigger", trigger=trigger_price), result_icon="💥")
                break
            
            display_message('action_stop', msg, result_icon="⏳")
            time.sleep(float(getattr(args, 'poll_interval', 5)))
    except KeyboardInterrupt:
        display_message('warning', get_message("stop.suspended", type="Ghost"))
        return

    display_message('info', get_message("stop.market_exit"))
    args.order_type = 'market'
    return exchange_instance.entry(args)

def run_smart_stop(exchange_name, args):
    """Placeholder for specialized Pro Smart Stop logic."""
    display_message('info', get_message("stop.smart_init", symbol=args.pair))
    # In a real implementation, this would dispatch to exchange-specific smart logic
    # like bitmango/exchange/phemex/smart_stop_phemex.py
    # For now, we fallback to native stop or a basic implementation
    return run_native_stop(exchange_name, args)
