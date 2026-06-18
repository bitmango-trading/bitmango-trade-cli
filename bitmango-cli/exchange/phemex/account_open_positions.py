import sys
from bitmango.exchange.base_exchange import BaseExchange
from bitmango.output import display_message
from bitmango.exchange.exchange_errors import UnsupportedError
from bitmango.messages import get_message

class PhemexAccountPositions(BaseExchange):
    def __init__(self, args):
        super().__init__('phemex', args)

    def balance(self, args):
        """
        Fetches and prints account balance for Phemex.
        """
        market_type = getattr(args, 'market_type', 'spot')
        msg = get_message("account.fetching_balance", exchange="Phemex", type=market_type.upper())
        display_message('action_start', msg)
        try:
            # Phemex Unified uses a single balance
            balance = self.exchange.fetch_balance()
            display_message('action_stop', msg, result_icon="✓")
            
            if 'total' in balance:
                for currency, total in balance['total'].items():
                    if total > 0:
                        free = balance['free'].get(currency, 0)
                        used = balance['used'].get(currency, 0)
                        display_message('info', get_message("account.balance_entry", currency=currency, total=total, free=free, used=used))
            
            return balance
        except Exception as e:
            display_message('action_stop', msg, result_icon="❌")
            display_message('error', get_message("exchange.fetch_error", item="balance", exchange="Phemex", error=e))
            return None

    def positions(self, args):
        """
        Fetches and prints open positions for Phemex.
        Filters out zero positions to reduce noise.
        """
        msg = get_message("account.fetching_positions", exchange="Phemex")
        display_message('action_start', msg)
        try:
            positions = self.exchange.fetch_positions()
            display_message('action_stop', msg, result_icon="✓")
            
            if positions:
                # Filter out positions with zero size
                open_positions = [pos for pos in positions if abs(float(pos.get('contracts', pos.get('amount', 0)))) > 0]
                if open_positions:
                    for pos in open_positions:
                        symbol = pos.get('symbol')
                        side = pos.get('side', 'Unknown')
                        size = pos.get('contracts', pos.get('amount', 0))
                        entry = pos.get('entryPrice', 0)
                        pnl = pos.get('unrealizedPnl', 0)
                        leverage = pos.get('leverage', 1)
                        
                        display_message('info', get_message("account.position_entry", symbol=symbol, side=side.upper(), size=size, entry=entry, pnl=pnl, leverage=leverage))
                    return open_positions
                else:
                    display_message('warning', get_message("account.no_positions", exchange="Phemex"))
                    return []
            else:
                display_message('warning', get_message("account.no_positions", exchange="Phemex"))
                return []
        except Exception as e:
            display_message('action_stop', msg, result_icon="❌")
            display_message('error', get_message("exchange.fetch_error", item="positions", exchange="Phemex", error=e))
            return None

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
        # Phemex Unified fetch_open_orders is standard
        return super().fetch_open_orders(args)

    def query_order_book(self, args):
        return super().query_order_book(args)

    def _get_position_mode(self, symbol):
        """
        Detects if the account is in 'Hedged' or 'OneWay' mode for Phemex.
        """
        try:
            # Phemex Unified/Contract API through CCXT
            mode_data = self.exchange.fetch_position_mode(symbol)
            # CCXT usually returns {'info': {...}, 'hedged': True/False}
            if mode_data.get('hedged'):
                return 'Hedged'
            return 'OneWay'
        except Exception as e:
            display_message('debug', get_message("exchange.phemex_pos_mode_debug", symbol=symbol, error=e))
            
            # Fallback: check if we have multiple positions for the same symbol
            try:
                positions = self.exchange.fetch_positions([symbol])
                if len(positions) > 1:
                    return 'Hedged'
            except:
                pass
                
            return 'OneWay' # Default safest assumption for CCXT standard params

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
        pos_mode = self._get_position_mode(symbol)
        display_message('debug', get_message("exchange.phemex_entry_debug", symbol=symbol, pos_mode=pos_mode))
        
        if pos_mode == 'Hedged':
            # In hedged mode, buy = Long, sell = Short for entry
            params['posSide'] = 'Long' if side == 'buy' else 'Short'
        else:
            params['posSide'] = 'Merged'
        
        display_message('debug', get_message("exchange.phemex_entry_params_debug", params=params))
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
        pos_mode = self._get_position_mode(symbol)
        if pos_mode == 'Hedged':
            # In hedged mode, to exit a Long we sell Short, to exit a Short we buy Long
            # CCXT 'side' is the order action.
            # If we are 'buy'ing to exit, we must be closing a 'Short'
            params['posSide'] = 'Short' if side == 'buy' else 'Long'
        else:
            params['posSide'] = 'Merged'
            
        return self._execute_order(symbol, order_type, side, size, price, params)

    def cancel_all_orders(self, args):
        """
        Optimized Phemex cancellation. Phemex testnet often hangs on global cancel.
        Uses unified logic with additional Phemex-specific fallbacks.
        """
        try:
            # Call unified logic (handles untriggered=True and basic retries)
            result = super().cancel_all_orders(args)
            
            # Additional Phemex-specific individual cleanup if it failed
            if result.get('status') == 'error':
                symbol = self._adapt_pair(args.pair) if hasattr(args, 'pair') else None
                display_message('info', get_message("exchange.phemex_cancel_fallback"))
                orders = self._get_open_orders(symbol)
                for o in orders:
                    try: self.exchange.cancel_order(o['id'], symbol)
                    except: pass
                return {"type": "cancel_all", "status": "success", "message": "Cancelled via individual fallback"}
            
            return result

        except Exception as e:
            display_message('error', get_message("exchange.phemex_cancel_fatal", error=e))
            return {"type": "cancel_all", "status": "error", "message": str(e)}

    def set_leverage(self, args):
        """
        Standard leverage setter.
        """
        return super().set_leverage(args)

    def set_margin_mode(self, args):
        """
        Phemex-specific margin mode setter.
        Requires no open orders/positions to change mode reliably.
        """
        symbol = self._adapt_pair(args.pair)
        mode = args.mode.upper() if hasattr(args, 'mode') else 'CROSS'
        msg = get_message("trade.set_margin_mode", mode=mode, symbol=symbol)
        display_message('action_start', msg)
        
        try:
            params = {}
            # Phemex Unified requires leverage parameter when changing margin mode for USDT pairs
            if ':USDT' in symbol:
                try:
                    positions = self.exchange.fetch_positions([symbol])
                    current_leverage = positions[0].get('leverage', 1) if positions else 1
                    params['leverage'] = current_leverage
                except:
                    params['leverage'] = 1
            
            res = self.exchange.set_margin_mode(mode, symbol, params)
            display_message('action_stop', msg, result_icon="✓")
            return {
                "type": "set_margin_mode",
                "exchange": self.exchange_name,
                "symbol": symbol,
                "mode": mode,
                "status": "success",
                "raw": res
            }
        except Exception as e:
            err_str = str(e)
            display_message('action_stop', msg, result_icon="❌")
            
            if 'TE_ERR_INCONSISTENT_POS_MODE' in err_str:
                display_message('error', get_message("exchange.phemex_inconsistent_pos_mode"))
                display_message('info', get_message("exchange.phemex_inconsistent_pos_tip1"))
                display_message('info', get_message("exchange.phemex_inconsistent_pos_tip2"))
            else:
                display_message('error', get_message("exchange.phemex_margin_error", error=e))
                
            return {"type": "set_margin_mode", "status": "error", "message": err_str}

    def stop_market(self, args):
        """
        Phemex-specific native stop market. Handles TE_REDUCE_ONLY_ABORT.
        """
        symbol = self._adapt_pair(args.pair)
        trigger_price = self._calculate_trigger_price(args)
        is_buy_entry = args.direction in ['buy', 'long']
        exit_side = 'sell' if is_buy_entry else 'buy'
        size = float(args.size)
        
        msg = get_message("trade.placing_order", side=exit_side.upper(), type="STOP_MARKET", amount=size, symbol=symbol, exchange="Phemex")
        display_message('action_start', msg)
        
        params = {
            'stopPrice': float(trigger_price)
        }
        
        # Phemex requires triggerDirection
        order_type = getattr(args, 'order_type', 'stop_loss')
        if order_type == 'stop_loss':
            params['triggerDirection'] = 'Falling' if exit_side == 'sell' else 'Rising'
        else: # take_profit
            params['triggerDirection'] = 'Rising' if exit_side == 'sell' else 'Falling'
        
        # Determine posSide for Hedged mode
        pos_mode = self._get_position_mode(symbol)
        if pos_mode == 'Hedged':
            params['posSide'] = 'Long' if exit_side == 'sell' else 'Short'
        else:
            params['posSide'] = 'Merged'
            
        # INTELLIGENT REDUCE-ONLY:
        # Phemex testnet throws TE_REDUCE_ONLY_ABORT if reduceOnly=True and no position exists.
        # However, a STOP order is ALMOST ALWAYS intended to reduce a position.
        # We'll check if a position exists. If not, we might still want the stop to be placed
        # but as a regular order (though Phemex might not allow Stop without reduceOnly in some modes).
        try:
            positions = self.exchange.fetch_positions([symbol])
            # Check for position on the correct side
            target_pos = None
            for p in positions:
                if pos_mode == 'Hedged':
                    if p['side'] == ('long' if exit_side == 'sell' else 'short'):
                        target_pos = p
                        break
                else:
                    if float(p.get('contracts', p.get('amount', 0))) != 0:
                        target_pos = p
                        break
            
            has_position = target_pos and float(target_pos.get('contracts', target_pos.get('amount', 0))) != 0
            # If user explicitly asked for reduce_only, honor it. Otherwise, auto-detect.
            params['reduceOnly'] = getattr(args, 'reduce_only', has_position)
            
            if not has_position and params['reduceOnly']:
                display_message('warning', get_message("exchange.phemex_no_pos_warning"))
        except Exception as e:
            display_message('debug', get_message("exchange.phemex_pos_check_failed_debug", error=e))
            params['reduceOnly'] = getattr(args, 'reduce_only', False)

        size_str = self.exchange.amount_to_precision(symbol, size)
        
        try:
            # Phemex Unified API uses ordType: 'Stop' for market stops in create_order
            order = self.exchange.create_order(symbol, 'stop', exit_side, size_str, None, params)
            display_message('action_stop', msg, result_icon="✓")
            display_message('success', get_message("exchange.phemex_stop_placed", id=order.get('id')))
            return {
                "type": "stop_order",
                "exchange": self.exchange_name,
                "symbol": symbol,
                "order": order,
                "status": "success"
            }
        except Exception as e:
            display_message('action_stop', msg, result_icon="❌")
            display_message('error', get_message("exchange.phemex_stop_error", error=e))
            return {"type": "stop_order", "status": "error", "message": str(e)}

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
