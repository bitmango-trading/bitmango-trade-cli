import sys
import importlib
from bitmango.output import display_message, start_boxed_mode, stop_boxed_mode, display_traceback
from bitmango.exchange.functions import get_exchange_class
from bitmango.cli.parser import confirm_order, verify_admin_session
from bitmango.exchange.risk_manager import RiskManager
from bitmango.messages import get_message

def execute_command(args, output_manager):
    """Dispatches the parsed arguments to the correct exchange method or plugin."""
    
    # Check risk configuration
    RiskManager.check_config()
    
    # 1. Aliases
    if args.command in ['buy', 'sell']:
        args.direction = args.command
        args.command = 'entry'
    elif args.command == 'close':
        args.command = 'exit'
        args.exit_command = 'specific'
        # Direction is determined by the position closure logic in exchange class
        # but we set a default to avoid attribute errors if checked before override
        if not hasattr(args, 'direction'):
            args.direction = 'sell' # Default placeholder
    elif args.command == 'close-all':
        args.command = 'exit'
        args.exit_command = 'all'

    is_trade = args.command in ('entry', 'exit')
    result = None

    if is_trade:
        title = get_message(f"cli.title_{args.command}")
        start_boxed_mode(title)
        module_name = f"bitmango.exchange.order_{args.market_type}"
        try:
            order_module = importlib.import_module(module_name)
            if args.command == 'exit' and args.exit_command == 'all':
                result = order_module.execute_exit_all(args.exchange, args)
            else:
                result = order_module.execute_order(args.exchange, args)
        except Exception as e:
            if output_manager.json_mode: raise
            display_message('error', get_message("cli.error_execution", error=e))
            display_traceback()
        stop_boxed_mode()

    elif args.command == 'stop':
        start_boxed_mode(get_message("cli.title_stop"))
        try:
            stop_mod = importlib.import_module("bitmango.exchange.order_stop")
            result = stop_mod.execute_stop_order(args.exchange, args)
        except Exception as e:
            if output_manager.json_mode: raise
            display_message('error', get_message("cli.error_stop_execution", error=e))
            display_traceback()
        stop_boxed_mode()

    else:
        # Standard Exchange Methods (markets, ticker, balance, etc.)
        exchange_class = get_exchange_class(args.exchange)
        if not exchange_class:
            display_message('error', get_message("errors.no_handler", exchange=args.exchange))
            return None
        
        # Decide which commands should be boxed
        boxed_commands = ('cancel', 'account', 'open_orders', 'leverage', 'margin', 'transfer', 'funding', 
                          'funding-history', 'position-mode', 'ledger', 'ticker', 
                          'ohlcv', 'trades', 'order-status', 'closed-orders', 'deposits', 'withdrawals', 'position-risk', 'query_order_book')
        
        should_box = args.command in boxed_commands
        if should_box:
            title = args.command.upper().replace('_', ' ').replace('-', ' ')
            if args.command == 'account':
                title = get_message("account.fetching_positions", exchange="") if getattr(args, 'positions', False) else get_message("account.fetching_balance", exchange="", type="")
            start_boxed_mode(title)

        instance = exchange_class(args)
        
        try:
            if args.command == 'cancel':
                if args.cancel_command == 'all':
                    if output_manager.json_mode: args.no_confirm = True
                    if confirm_order(get_message("trade.confirm_cancel_all"), args.no_confirm):
                        result = instance.cancel_all_orders(args)
                        instance.verify_cancellation(instance._adapt_pair(args.pair))
                else:
                    result = instance.cancel_specific_order(args)
                    instance.verify_cancellation(instance._adapt_pair(args.pair))
                
            elif args.command == 'account':
                result = instance.positions(args) if getattr(args, 'positions', False) else instance.balance(args)
                
            elif args.command == 'open_orders': 
                result = instance.fetch_open_orders(args)
                
            elif args.command == 'order-status':
                result = instance.fetch_order(args)
                
            elif args.command == 'closed-orders':
                result = instance.fetch_closed_orders(args)
                
            elif args.command == 'position-risk': 
                result = instance.fetch_position_risk(args)

            elif args.command == 'leverage': result = instance.set_leverage(args)
            elif args.command == 'margin': result = instance.set_margin_mode(args)
            elif args.command == 'transfer': 
                verify_admin_session()
                result = instance.transfer(args)
            elif args.command == 'funding': result = instance.fetch_funding_rate(args)
            elif args.command == 'funding-history': result = instance.funding_history(args)
            elif args.command == 'position-mode': result = instance.set_position_mode(args)
            elif args.command == 'ledger': result = instance.fetch_ledger(args)
            elif args.command == 'deposits': result = instance.fetch_deposits(args)
            elif args.command == 'withdrawals': result = instance.fetch_withdrawals(args)
            elif args.command == 'trades': result = instance.fetch_my_trades(args)
            elif args.command == 'markets': result = instance.markets(args)
            elif args.command == 'history': result = instance.history(args)
            elif args.command == 'ticker':
                result = instance.watch_ticker(args) if getattr(args, 'stream', False) else instance.ticker(args)
            elif args.command == 'ohlcv':
                result = instance.watch_ohlcv(args) if getattr(args, 'stream', False) else instance.ohlcv(args)
            elif args.command == 'query_order_book':
                result = instance.watch_order_book(args) if getattr(args, 'stream', False) else instance.query_order_book(args)
            else:
                display_message('error', get_message("errors.unsupported_feature", exchange=args.exchange, error=args.command))

        except Exception as e:
             if output_manager.json_mode: raise
             display_message('error', get_message("cli.error_execution", error=e))
             display_traceback()

        if should_box: stop_boxed_mode()

    return result
