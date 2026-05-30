import time
import sys
import os
from datetime import datetime
from bitmango.output import display_message, output as output_manager
from bitmango.exchange.risk_manager import RiskManager
from bitmango.messages import get_message
from bitmango.license import is_pro_enabled, get_pro_token, get_public_key

class TradingMixin:
    """Mixin for trading operations (orders, cancels, leverage, etc.)."""

    def _log_pro_trade(self, order_result):
        """Internal helper to log trade to Pro ledger if enabled."""
        if not is_pro_enabled():
            return

        try:
            import bitmango_pro_core
            token = get_pro_token()
            key = get_public_key()
            
            if not token:
                display_message('debug', "Pro logging skipped: No valid token found.")
                return

            order = order_result.get('order', {})
            
            # Extract fee info if available
            fee_cost = 0.0
            if order.get('fee'):
                fee_cost = float(order['fee'].get('cost', 0.0))

            bitmango_pro_core.log_pro_trade(
                token,
                key,
                str(order.get('id')),
                datetime.now().isoformat(), # We need datetime import
                self.exchange_name,
                order.get('symbol'),
                order.get('side'),
                order.get('type'),
                float(order.get('amount', 0.0)),
                float(order.get('price', 0.0)) if order.get('price') else 0.0,
                fee_cost,
                0.0, # PnL is usually 0 at entry, updated on exit/settlement
                order.get('status'),
                None, # error_msg
                os.environ.get("GITHUB_ID", "anonymous") # We need os import
            )
            display_message('debug', f"Pro Trade Logged: {order.get('id')}")
        except Exception as e:
            display_message('debug', f"Pro Logging Error: {e}")

    def _execute_order(self, market_symbol, order_type, side, size, price, params):
        self._check_reliability()
        
        # Risk Management Pre-flight Check
        RiskManager.validate_order(self, market_symbol, order_type, side, size, price)
        
        msg = get_message("trade.placing_order", side=side.upper(), type=order_type, amount=size, symbol=market_symbol, exchange=self.exchange_name)
        display_message('action_start', msg)
        try:
            order_result = self.exchange.create_order(market_symbol, order_type, side, size, price, params)
            display_message('action_stop', msg, result_icon="✓")
            display_message('info', get_message("trade.order_details", id=order_result.get('id'), status=order_result.get('status')))
            
            res = {
                "type": "order",
                "exchange": self.exchange_name,
                "order": {
                    "id": str(order_result.get('id')),
                    "symbol": order_result.get('symbol'),
                    "side": order_result.get('side').lower(),
                    "type": order_result.get('type').lower(),
                    "amount": float(order_result.get('amount', 0)),
                    "price": float(order_result.get('price', 0)) if order_result.get('price') else None,
                    "status": order_result.get('status').lower(),
                    "filled": float(order_result.get('filled', 0)),
                    "remaining": float(order_result.get('remaining', 0)),
                    "fee": order_result.get('fee')
                },
                "status": "success"
            }
            # Log for Pro auditing
            self._log_pro_trade(res)
            return res
        except Exception as e:
            if output_manager.json_mode: raise e
            display_message('action_stop', msg, result_icon="❌")
            display_message('error', get_message("errors.fatal", error=e))
            raise e

    def _verify_position(self, market_symbol, side, size_float):
        max_retries = 5
        retry_delay = 2
        position_verified = False
        for i in range(max_retries):
            time.sleep(retry_delay)
            positions = self.exchange.fetch_positions([market_symbol])
            if positions:
                current_position = positions[0]
                if current_position.get('side') == side and abs(current_position.get('contracts', 0) - size_float) < 0.0001:
                    display_message('success', get_message("trade.position_verified", amount=current_position.get('contracts'), symbol=market_symbol))
                    position_verified = True
                    break
            display_message('warning', get_message("trade.verify_attempt", current=i+1, max=max_retries, item="Position"))
        if not position_verified:
            display_message('warning', get_message("trade.verify_failed", item="Position"))

    def _fetch_open_position(self, market_symbol):
        max_retries = 10
        retry_delay = 3
        for i in range(max_retries):
            try:
                all_positions = self.exchange.fetch_positions()
                if all_positions:
                    for position in all_positions:
                        if position.get('symbol') == market_symbol and position.get('contracts', 0) > 0:
                            return position
                time.sleep(retry_delay)
            except Exception:
                time.sleep(retry_delay)
        display_message('error', get_message("exchange.fetch_error", item="open position", exchange=self.exchange_name, error=market_symbol))
        return None

    def _get_open_orders(self, symbol=None):
        params = {}
        if self.exchange_name == 'phemex':
            params['untriggered'] = True
        return self.exchange.fetch_open_orders(symbol, params=params)

    def _verify_order(self, market_symbol, order_result):
        max_retries = 5
        retry_delay = 2
        order_verified = False
        for i in range(max_retries):
            time.sleep(retry_delay)
            open_orders = self._get_open_orders(symbol=market_symbol)
            if any(order.get('id') == order_result.get('id') for order in open_orders):
                display_message('success', get_message("trade.order_verified_open"))
                order_verified = True
                break
            display_message('warning', get_message("trade.verify_attempt", current=i+1, max=max_retries, item="Order"))
        if not order_verified:
            display_message('warning', get_message("trade.verify_failed", item="Order"))

    def verify_order_fulfillment(self, market_symbol, order_result, order_type):
        if 'order' in order_result:
            order_data = order_result['order']
        else:
            order_data = order_result

        order_id = order_data.get('id')
        total_amount = float(order_data.get('amount', 0))
        
        if not order_id:
            display_message('error', get_message("exchange.fetch_error", item="order ID", exchange=self.exchange_name, error="No order ID returned"))
            return 0.0

        msg = get_message("trade.verifying_order", type=order_type.upper(), id=order_id)
        display_message('info', msg)
        
        filled = 0.0
        is_wait = getattr(self.args, 'wait', False)

        if order_type == 'market' or is_wait:
            max_retries = 30 if is_wait else 10
            for i in range(max_retries):
                wait_msg = get_message("trade.wait_fill", filled=filled, total=total_amount)
                display_message('action_start', wait_msg)
                time.sleep(2)
                status = self._get_order_status(order_id, market_symbol)
                if not status:
                    display_message('action_stop', wait_msg, result_icon="⏳")
                    continue
                
                filled = float(status.get('filled', 0))
                
                # Update the order_data in the original result
                if 'order' in order_result:
                    order_result['order']['status'] = status.get('status', 'unknown').lower()
                    order_result['order']['filled'] = filled
                    order_result['order']['remaining'] = float(status.get('remaining', total_amount - filled))
                    if status.get('average'): order_result['order']['average'] = float(status.get('average'))
                    if status.get('fee'): order_result['order']['fee'] = status.get('fee')

                if filled >= total_amount or status.get('status') in ['closed', 'canceled', 'rejected']:
                    display_message('action_stop', get_message("trade.fill_result", filled=filled, total=total_amount, status=status.get('status')), result_icon="✓")
                    
                    return filled
                
                display_message('action_stop', get_message("trade.partial_fill", filled=filled, total=total_amount), result_icon="⏳")
            
            display_message('warning', get_message("trade.partial_fill", filled=filled, total=total_amount))
            return filled
        else:
            if self._verify_order(market_symbol, order_result):
                return 0.0
            return 0.0

    def verify_cancellation(self, market_symbol, order_id=None):
        msg = get_message("trade.verifying_cancel", symbol=market_symbol)
        display_message('info', msg)
        max_retries = 5
        for i in range(max_retries):
            time.sleep(2)
            open_orders = self._get_open_orders(symbol=market_symbol)
            if order_id:
                if not any(o['id'] == order_id for o in open_orders):
                    display_message('success', get_message("trade.order_verified_closed", id=order_id))
                    return True
            else:
                if not open_orders:
                    display_message('success', get_message("trade.all_orders_cleared", symbol=market_symbol))
                    return True
            display_message('warning', get_message("trade.verify_attempt", current=i+1, max=max_retries, item="Cancellation propagation"))
        display_message('warning', get_message("trade.verify_failed", item="Cancellation"))
        return False

    def verify_position_closure(self, market_symbol):
        msg = get_message("trade.verifying_position_closure", symbol=market_symbol)
        display_message('info', msg)
        max_retries = 5
        for i in range(max_retries):
            time.sleep(2)
            position = self._fetch_open_position(market_symbol)
            if not position or float(position.get('contracts', 0)) == 0:
                display_message('success', get_message("trade.position_closed", symbol=market_symbol))
                return True
            display_message('warning', get_message("trade.verify_attempt", current=i+1, max=max_retries, item="Position closure confirmation"))
        display_message('warning', get_message("trade.verify_failed", item="Position closure confirmation"))
        return False

    def _get_order_status(self, order_id, market_symbol):
        try:
            return self.exchange.fetch_order(order_id, market_symbol)
        except Exception:
            display_message('error', get_message("exchange.fetch_error", item="order status", exchange=self.exchange_name, error=order_id))
            return None

    def _fetch_current_price(self, market_symbol, is_buy):
        try:
            order_book = self.exchange.fetch_order_book(market_symbol)
            
            # Risk Management: Ensure order book is fresh before using it for price/size checks
            is_sandbox = getattr(self.args, 'sandbox', False)
            RiskManager.validate_market_data(order_book, is_sandbox=is_sandbox)
            
            if is_buy:
                return order_book['asks'][0][0] if order_book['asks'] else None
            else:
                return order_book['bids'][0][0] if order_book['bids'] else None
        except Exception as e:
            if "RISK BREACH" in str(e): raise e
            display_message('error', get_message("exchange.fetch_error", item="current price", exchange=self.exchange_name, error=market_symbol))
            return None

    def fetch_open_orders(self, args):
        symbol = self._adapt_pair(args.pair) if hasattr(args, 'pair') and args.pair else None
        msg = get_message("trade.fetching_open_orders", symbol=symbol or "all symbols")
        display_message('action_start', msg)
        try:
            params = {}
            if self.exchange_name == 'phemex':
                params['untriggered'] = True
            
            orders = self.exchange.fetch_open_orders(symbol, params=params)
            display_message('action_stop', msg, result_icon="✓")
            standardized_orders = []
            if orders:
                for o in orders:
                    display_message('info', get_message("trade.order_entry", id=o['id'], symbol=o['symbol'], type=o['type'], side=o['side'], amount=o['amount'], price=o['price'], status=o['status']))
                    standardized_orders.append({
                        "id": str(o['id']), "symbol": o['symbol'], "side": o['side'].lower(), "type": o['type'].lower(),
                        "amount": float(o['amount']), "price": float(o['price']) if o.get('price') else None, "status": o['status'].lower()
                    })
            else:
                display_message('warning', get_message("trade.no_open_orders"))
            return {"type": "open_orders", "exchange": self.exchange_name, "orders": standardized_orders}
        except Exception as e:
            if output_manager.json_mode: raise e
            display_message('action_stop', msg, result_icon="❌")
            display_message('error', get_message("errors.fatal", error=e))
            raise e

    def cancel_all_orders(self, args):
        symbol = self._adapt_pair(args.pair) if (hasattr(args, 'pair') and args.pair) else None
        msg = get_message("trade.cancelling_orders", symbol=symbol if symbol else "ALL symbols", exchange=self.exchange_name)
        display_message('action_start', msg)
        try:
            if not symbol and not self.exchange.has.get('cancelAllOrders'):
                 display_message('action_stop', msg, result_icon="⚠️")
                 return {"type": "cancel_all", "status": "error", "message": "Symbol required"}
            
            params = {}
            if self.exchange_name == 'phemex':
                params['untriggered'] = True
            
            res = self.exchange.cancel_all_orders(symbol, params=params)
            
            # Double check for Phemex due to TE_SO_NUM_EXCEEDS persistent issues
            if self.exchange_name == 'phemex':
                time.sleep(1)
                remaining = self.exchange.fetch_open_orders(symbol, params={'untriggered': True})
                if remaining:
                    display_message('warning', get_message("exchange.phemex_manual_cleanup", count=len(remaining)))
                    for o in remaining:
                        try: self.exchange.cancel_order(o['id'], symbol)
                        except: pass

            display_message('action_stop', msg, result_icon="✓")
            return {"type": "cancel_all", "exchange": self.exchange_name, "symbol": symbol, "status": "success", "raw": res}
        except Exception as e:
            if output_manager.json_mode: raise e
            display_message('action_stop', msg, result_icon="❌")
            display_message('error', get_message("errors.fatal", error=e))
            raise e

    def stop_market(self, args):
        symbol = self._adapt_pair(args.pair)
        trigger_price = self._calculate_trigger_price(args)
        is_buy_entry = args.direction in ['buy', 'long']
        exit_side = 'sell' if is_buy_entry else 'buy'
        size = float(args.size)
        msg = get_message("trade.placing_order", side=exit_side.upper(), type="STOP_MARKET", amount=size, symbol=symbol, exchange=self.exchange_name)
        display_message('action_start', msg)
        params = {'stopPrice': float(trigger_price)}
        if hasattr(args, 'reduce_only'):
            params['reduceOnly'] = args.reduce_only
        size_str = self.exchange.amount_to_precision(symbol, size)
        try:
            if self.exchange_name == 'phemex':
                order = self.exchange.create_order(symbol, 'stop', exit_side, size_str, None, params)
            elif self.exchange.has.get('createStopOrder'):
                order = self.exchange.create_stop_order(symbol, 'market', exit_side, size_str, None, params)
            else:
                order = self.exchange.create_order(symbol, 'market', exit_side, float(size_str), None, params)
            display_message('action_stop', msg, result_icon="✓")
            display_message('success', get_message("trade.order_success", type="Native stop", side="", id=order.get('id')))
            
            res = {
                "type": "stop_order",
                "exchange": self.exchange_name,
                "symbol": symbol,
                "order": order,
                "status": "success"
            }
            self._log_pro_trade(res)
            return res
        except Exception as e:
            if output_manager.json_mode: raise e
            display_message('action_stop', msg, result_icon="❌")
            display_message('error', get_message("exchange.action_failed", action="Place stop", symbol=symbol, exchange=self.exchange_name, error=e))
            raise e

    def cancel_specific_order(self, args):
        symbol = self._adapt_pair(args.pair)
        try:
            display_message('info', get_message("trade.searching_cancel", symbol=symbol))
            orders = self._get_open_orders(symbol=symbol)
            target = next((o for o in orders if float(o['amount']) == float(args.size) and o['side'].lower() == args.direction.lower()), None)
            if target:
                res = self.exchange.cancel_order(target['id'], symbol)
                display_message('success', get_message("trade.cancel_success", id=target['id']))
                return {"type": "cancel_specific", "exchange": self.exchange_name, "order_id": target['id'], "status": "success", "raw": res}
            else:
                display_message('warning', get_message("trade.no_matching_cancel"))
                return {"type": "cancel_specific", "status": "warning", "message": "Order not found"}
        except Exception as e:
            if output_manager.json_mode: raise e
            display_message('error', get_message("errors.fatal", error=e))
            raise e

    def _calculate_trigger_price(self, args):
        if hasattr(args, 'stop_price') and args.stop_price:
            return float(args.stop_price)
        current_price = float(args.current_price)
        is_buy = args.direction in ['buy', 'long']
        percentage = float(args.stop_loss_percentage if args.order_type == 'stop_loss' else args.take_profit_percentage)
        if args.order_type == 'stop_loss':
            return current_price * (1 - percentage) if is_buy else current_price * (1 + percentage)
        else:
            return current_price * (1 + percentage) if is_buy else current_price * (1 - percentage)

    def set_leverage(self, args):
        symbol = self._adapt_pair(args.pair)
        leverage = int(args.leverage)
        msg = get_message("trade.set_leverage", leverage=leverage, symbol=symbol)
        display_message('action_start', msg)
        try:
            params = {}
            if self.exchange_name == 'phemex': params['hedged'] = True
            res = self.exchange.set_leverage(leverage, symbol, params)
            display_message('action_stop', msg, result_icon="✓")
            return {"type": "set_leverage", "exchange": self.exchange_name, "symbol": symbol, "leverage": leverage, "status": "success"}
        except Exception as e:
            if output_manager.json_mode: raise e
            display_message('action_stop', msg, result_icon="❌")
            display_message('error', get_message("errors.fatal", error=e))
            raise e

    def set_margin_mode(self, args):
        symbol = self._adapt_pair(args.pair)
        mode = args.mode.upper()
        msg = get_message("trade.set_margin_mode", mode=mode, symbol=symbol)
        display_message('action_start', msg)
        try:
            res = self.exchange.set_margin_mode(mode, symbol)
            display_message('action_stop', msg, result_icon="✓")
            return {"type": "set_margin_mode", "exchange": self.exchange_name, "symbol": symbol, "mode": mode, "status": "success", "raw": res}
        except Exception as e:
            if output_manager.json_mode: raise e
            display_message('action_stop', msg, result_icon="❌")
            raise e

    def transfer(self, args):
        msg = get_message("exchange.transfer_start", amount=args.amount, currency=args.currency, from_acc=args.from_account, to_acc=args.to_account)
        display_message('action_start', msg)
        try:
            res = self.exchange.transfer(args.currency, args.amount, args.from_account, args.to_account)
            display_message('action_stop', msg, result_icon="✓")
            display_message('success', get_message("account.transfer_success", id=res.get('tranId', res.get('id', 'N/A'))))
            return {"type": "transfer", "status": "success", "raw": res}
        except Exception as e:
            if output_manager.json_mode: raise e
            display_message('action_stop', msg, result_icon="❌")
            display_message('error', get_message("account.transfer_failed", error=e))
            raise e

    def fetch_order(self, args):
        symbol = self._adapt_pair(args.pair)
        msg = get_message("trade.fetching_order", id=args.order_id, symbol=symbol)
        display_message('action_start', msg)
        try:
            order = self.exchange.fetch_order(args.order_id, symbol)
            display_message('action_stop', msg, result_icon="✓")
            status = order.get('status', 'unknown') or 'unknown'
            side = order.get('side', 'unknown') or 'unknown'
            otype = order.get('type', 'unknown') or 'unknown'
            display_message('info', get_message("trade.order_entry_short", id=order['id'], status=status.upper(), side=side.upper(), type=otype.upper()))
            display_message('info', get_message("trade.order_fill_short", filled=order.get('filled', 0), amount=order.get('amount', 0), price=order.get('price', 0)))
            return {
                "type": "order",
                "exchange": self.exchange_name,
                "order": order,
                "status": "success"
            }
        except Exception as e:
            if output_manager.json_mode: raise e
            display_message('action_stop', msg, result_icon="❌")
            display_message('error', get_message("exchange.fetch_error", item="order", exchange=self.exchange_name, error=e))
            raise e

    def fetch_closed_orders(self, args):
        symbol = self._adapt_pair(args.pair)
        limit = int(getattr(args, 'limit', 20))
        msg = get_message("trade.fetching_closed_orders", symbol=symbol)
        display_message('action_start', msg)
        try:
            orders = self.exchange.fetch_closed_orders(symbol, limit=limit)
            display_message('action_stop', msg, result_icon="✓")
            if orders:
                for o in orders[-10:]:
                    status = o.get('status', 'unknown')
                    display_message('info', get_message("trade.closed_order_entry", dt=o['datetime'], id=o['id'], side=o['side'].upper(), status=status.upper(), filled=o['filled'], amount=o['amount']))
            else:
                display_message('warning', get_message("account.no_history"))
            return {
                "type": "closed_orders",
                "exchange": self.exchange_name,
                "symbol": symbol,
                "data": orders if orders else [],
                "status": "success"
            }
        except Exception as e:
            if output_manager.json_mode: raise e
            display_message('action_stop', msg, result_icon="❌")
            display_message('error', get_message("exchange.fetch_error", item="closed orders", exchange=self.exchange_name, error=e))
            raise e
