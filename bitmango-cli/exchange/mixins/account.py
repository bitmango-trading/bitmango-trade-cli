import sys
from bitmango.output import display_message, output as output_manager
from bitmango.exchange.exchange_errors import UnsupportedError
from bitmango.messages import get_message

class AccountMixin:
    """Mixin for account-related methods (balance, history, ledger, etc.)."""

    def fetch_deposits(self, args):
        """Fetches deposit history."""
        code = args.currency.upper() if hasattr(args, 'currency') and args.currency else None
        msg = get_message("account.fetching_deposits", exchange=self.exchange_name)
        display_message('action_start', msg)
        try:
            deposits = self.exchange.fetch_deposits(code)
            display_message('action_stop', msg, result_icon="✓")
            if deposits:
                for d in deposits[-10:]:
                    display_message('info', get_message("account.deposit_entry", dt=d['datetime'], amount=d['amount'], code=d['code'], status=d['status'], id=d.get('id')))
            else:
                display_message('warning', get_message("account.no_deposits"))
            return {
                "type": "deposits",
                "exchange": self.exchange_name,
                "currency": code,
                "data": deposits if deposits else [],
                "status": "success"
            }
        except Exception as e:
            if output_manager.json_mode: raise e
            display_message('action_stop', msg, result_icon="❌")
            display_message('error', get_message("exchange.fetch_error", item="deposits", exchange=self.exchange_name, error=e))
            raise e


    def fetch_withdrawals(self, args):
        """Fetches withdrawal history."""
        code = args.currency.upper() if hasattr(args, 'currency') and args.currency else None
        msg = get_message("account.fetching_withdrawals", exchange=self.exchange_name)
        display_message('action_start', msg)
        try:
            withdrawals = self.exchange.fetch_withdrawals(code)
            display_message('action_stop', msg, result_icon="✓")
            if withdrawals:
                for w in withdrawals[-10:]:
                    display_message('info', get_message("account.withdrawal_entry", dt=w['datetime'], amount=w['amount'], code=w['code'], status=w['status'], id=w.get('id')))
            else:
                display_message('warning', get_message("account.no_withdrawals"))
            return {
                "type": "withdrawals",
                "exchange": self.exchange_name,
                "currency": code,
                "data": withdrawals if withdrawals else [],
                "status": "success"
            }
        except Exception as e:
            if output_manager.json_mode: raise e
            display_message('action_stop', msg, result_icon="❌")
            display_message('error', get_message("exchange.fetch_error", item="withdrawals", exchange=self.exchange_name, error=e))
            raise e


    def fetch_position_risk(self, args):
        """Fetches risk metrics for positions (liquidation price, margin ratio)."""
        symbol = self._adapt_pair(args.pair) if hasattr(args, 'pair') and args.pair else None
        msg = get_message("account.fetching_position_risk", symbol=symbol if symbol else "all positions")
        display_message('action_start', msg)
        try:
            positions = self.exchange.fetch_positions([symbol] if symbol else None)
            display_message('action_stop', msg, result_icon="✓")
            
            risk_data = []
            if positions:
                for p in positions:
                    size = float(p.get('contracts', p.get('amount', 0)))
                    if size != 0:
                        liq = p.get('liquidationPrice')
                        m_ratio = p.get('marginRatio')
                        display_message('info', get_message("account.position_risk_entry", symbol=p['symbol'], side=p['side'].upper(), size=size, liq=liq, m_ratio=m_ratio))
                        risk_data.append({
                            "symbol": p['symbol'],
                            "liquidation_price": liq,
                            "margin_ratio": m_ratio,
                            "leverage": p.get('leverage')
                        })
            else:
                display_message('warning', get_message("account.no_active_positions_risk"))
            
            return {
                "type": "position_risk",
                "exchange": self.exchange_name,
                "positions": risk_data
            }
        except Exception as e:
            if output_manager.json_mode: raise e
            display_message('action_stop', msg, result_icon="❌")
            display_message('error', get_message("exchange.fetch_error", item="position risk", exchange=self.exchange_name, error=e))
            raise e

    def history(self, args):
        """Standardized order history."""
        symbol = self._adapt_pair(args.pair) if hasattr(args, 'pair') and args.pair else None
        msg = get_message("account.fetching_history", symbol=symbol or "all symbols")
        display_message('action_start', msg)
        try:
            orders = self.exchange.fetch_orders(symbol)
            display_message('action_stop', msg, result_icon="✓")
            
            standardized_orders = []
            if orders:
                for o in orders[-10:]:
                    display_message('info', get_message("account.history_entry", dt=o['datetime'], symbol=o['symbol'], side=o['side'], type=o['type'], status=o['status'], filled=o['filled'], amount=o['amount']))
                
                for o in orders:
                    standardized_orders.append({
                        "id": str(o['id']),
                        "datetime": o['datetime'],
                        "symbol": o['symbol'],
                        "side": o['side'].lower(),
                        "type": o['type'].lower(),
                        "amount": float(o['amount']),
                        "price": float(o['price']) if o.get('price') else None,
                        "status": o['status'].lower(),
                        "filled": float(o['filled']),
                        "remaining": float(o['remaining'])
                    })
            else:
                display_message('warning', get_message("account.no_history"))
            
            return {
                "type": "history",
                "exchange": self.exchange_name,
                "symbol": symbol,
                "data": standardized_orders,
                "status": "success"
            }
        except Exception as e:
            if output_manager.json_mode: raise e
            display_message('action_stop', f"Error: {e}", result_icon="❌")
            return {"type": "history", "status": "error", "message": str(e)}

    def set_position_mode(self, args):
        """Sets position mode (OneWay or Hedged)."""
        symbol = self._adapt_pair(args.pair)
        mode = args.mode # 'oneway' or 'hedge'
        msg = get_message("account.set_position_mode", mode=mode.upper(), symbol=symbol)
        display_message('action_start', msg)
        
        hedged = (mode == 'hedge')
        
        try:
            if self.exchange_name == 'phemex':
                target = 'Hedged' if hedged else 'OneWay'
                s = symbol.split(':')[0].replace('/', '')
                res = self.exchange.private_put_g_positions_switch_pos_mode_sync({
                    'symbol': s,
                    'targetPosMode': target
                })
            else:
                res = self.exchange.set_position_mode(hedged, symbol)
            
            display_message('action_stop', msg, result_icon="✓")
            return {
                "type": "set_position_mode",
                "exchange": self.exchange_name,
                "symbol": symbol,
                "mode": mode,
                "status": "success",
                "raw": res
            }
        except Exception as e:
            if output_manager.json_mode: raise e
            display_message('action_stop', f"Error: {e}", result_icon="❌")
            return {"type": "set_position_mode", "status": "error", "message": str(e)}

    def fetch_my_trades(self, args):
        """Standardized fetch my trades."""
        symbol = self._adapt_pair(args.pair) if hasattr(args, 'pair') and args.pair else None
        msg = get_message("account.fetching_trades", symbol=symbol or "all symbols")
        display_message('action_start', msg)
        try:
            trades = self.exchange.fetch_my_trades(symbol)
            display_message('action_stop', msg, result_icon="✓")
            
            standardized_trades = []
            if trades:
                for t in trades[-10:]:
                    fee_cost = t.get('fee', {}).get('cost', 0) if t.get('fee') else 0
                    fee_currency = t.get('fee', {}).get('currency', '') if t.get('fee') else ''
                    display_message('info', get_message("account.trade_entry", dt=t['datetime'], symbol=t['symbol'], side=t['side'], price=t['price'], amount=t['amount'], fee_cost=fee_cost, fee_currency=fee_currency))
                
                for t in trades:
                    standardized_trades.append({
                        "id": str(t.get('id')),
                        "order": str(t.get('order')),
                        "datetime": t['datetime'],
                        "symbol": t['symbol'],
                        "side": t['side'].lower(),
                        "price": float(t['price']),
                        "amount": float(t['amount']),
                        "cost": float(t['cost']),
                        "fee": t.get('fee')
                    })
            else:
                display_message('warning', get_message("account.no_trades"))
            
            return {
                "type": "trades",
                "exchange": self.exchange_name,
                "trades": standardized_trades,
                "status": "success"
            }
        except Exception as e:
            if output_manager.json_mode: raise e
            display_message('action_stop', f"Error: {e}", result_icon="❌")
            return {"type": "trades", "status": "error", "message": str(e)}

    def funding_history(self, args):
        """Fetches historical funding payments."""
        symbol = self._adapt_pair(args.pair) if hasattr(args, 'pair') and args.pair else None
        msg = get_message("account.fetching_funding", symbol=symbol or "all symbols")
        display_message('action_start', msg)
        try:
            if not self.exchange.has.get('fetchFundingHistory'):
                 raise UnsupportedError(f"fetch_funding_history not supported by {self.exchange_name}")

            history = self.exchange.fetch_funding_history(symbol)
            display_message('action_stop', msg, result_icon="✓")
            
            standardized_history = []
            if history:
                for entry in history[-10:]:
                    display_message('info', get_message("account.funding_entry", dt=entry['datetime'], symbol=entry['symbol'], rate=entry.get('fundingRate'), amount=entry.get('amount')))
                
                for entry in history:
                    standardized_history.append({
                        "id": str(entry.get('id')),
                        "datetime": entry['datetime'],
                        "symbol": entry['symbol'],
                        "rate": float(entry.get('fundingRate', 0)) if entry.get('fundingRate') else None,
                        "amount": float(entry.get('amount', 0)) if entry.get('amount') else None,
                    })
            else:
                display_message('warning', get_message("account.no_funding"))
            
            return {
                "type": "funding_history",
                "exchange": self.exchange_name,
                "history": standardized_history
            }
        except Exception as e:
            if output_manager.json_mode: raise e
            display_message('action_stop', f"Error: {e}", result_icon="❌")
            return {"type": "funding_history", "status": "error", "message": str(e)}

    def balance(self, args):
        """
        Standardized balance fetcher.
        """
        market_type = getattr(args, 'market_type', 'spot')
        msg = get_message("account.fetching_balance", exchange=self.exchange_name.capitalize(), type=market_type.upper())
        display_message('action_start', msg)
        try:
            params = {}
            if self.exchange_name == 'binance':
                params = {'type': 'spot' if market_type == 'spot' else 'swap'}
            
            balance = self.exchange.fetch_balance(params=params)
            display_message('action_stop', msg, result_icon="✓")
            
            if 'total' in balance:
                for currency, total in balance['total'].items():
                    if total > 0:
                        free = balance['free'].get(currency, 0)
                        used = balance['used'].get(currency, 0)
                        display_message('info', get_message("account.balance_entry", currency=currency, total=total, free=free, used=used))
            
            return {
                "type": "balance",
                "exchange": self.exchange_name,
                "market_type": market_type,
                "data": balance,
                "status": "success"
            }
        except Exception as e:
            if output_manager.json_mode: raise e
            display_message('action_stop', msg, result_icon="❌")
            display_message('error', get_message("exchange.fetch_error", item="balance", exchange=self.exchange_name, error=e))
            raise e


    def positions(self, args):
        """
        Standardized position fetcher.
        """
        msg = get_message("account.fetching_positions", exchange=self.exchange_name.capitalize())
        display_message('action_start', msg)
        try:
            positions = self.exchange.fetch_positions()
            if positions is None:
                positions = []
            display_message('action_stop', msg, result_icon="✓")
            
            if positions:
                # Filter for active positions only
                open_positions = [pos for pos in positions if float(pos.get('contracts', 0)) > 0 or float(pos.get('amount', 0)) > 0]
                if open_positions:
                    for pos in open_positions:
                        symbol = pos.get('symbol')
                        side = pos.get('side', 'Unknown')
                        size = pos.get('contracts', pos.get('amount', 0))
                        entry = pos.get('entryPrice', 0)
                        pnl = pos.get('unrealizedPnl', 0)
                        leverage = pos.get('leverage', 1)
                        
                        display_message('info', get_message("account.position_entry", symbol=symbol, side=side.upper(), size=size, entry=entry, pnl=pnl, leverage=leverage))
                else:
                    display_message('warning', get_message("account.no_positions", exchange=self.exchange_name.capitalize()))
            else:
                display_message('warning', get_message("account.no_positions", exchange=self.exchange_name.capitalize()))
            
            return {
                "type": "positions",
                "exchange": self.exchange_name,
                "data": positions if positions else [],
                "open_only": open_positions if 'open_positions' in locals() else [],
                "status": "success"
            }
        except Exception as e:
            if output_manager.json_mode: raise e
            display_message('action_stop', msg, result_icon="❌")
            display_message('error', get_message("exchange.fetch_error", item="positions", exchange=self.exchange_name, error=e))
            raise e


    def fetch_balance(self, args=None):
        """Standardized fetch balance."""
        return self.exchange.fetch_balance()

    def fetch_ledger(self, args):
        """Fetches account ledger with fallbacks for unsupported exchanges."""
        code = args.currency.upper()
        msg = get_message("account.fetching_ledger", code=code, exchange=self.exchange_name)
        display_message('action_start', msg)
        
        try:
            standardized_ledger = []
            if self.exchange.has.get('fetchLedger'):
                ledger = self.exchange.fetch_ledger(code)
                if ledger:
                    for entry in ledger:
                        standardized_ledger.append({
                            "id": str(entry.get('id')),
                            "datetime": entry['datetime'],
                            "type": entry['type'],
                            "amount": float(entry['amount']),
                            "currency": entry['code'],
                            "status": entry['status']
                        })
            
            if not standardized_ledger:
                display_message('debug', get_message("account.debug_ledger_fallback", exchange=self.exchange_name))
                if self.exchange.has.get('fetchMyTrades'):
                    try:
                        trades = self.exchange.fetch_my_trades(None)
                        for t in trades:
                            if t.get('fee') and t['fee'].get('currency') == code:
                                standardized_ledger.append({
                                    "id": f"fee-{t['id']}", "datetime": t['datetime'], "type": "fee",
                                    "amount": -float(t['fee']['cost']), "currency": code, "status": "ok"
                                })
                    except: pass

                if self.exchange.has.get('fetchDeposits'):
                    try:
                        deposits = self.exchange.fetch_deposits(code)
                        for d in deposits:
                            standardized_ledger.append({
                                "id": str(d.get('id')), "datetime": d['datetime'], "type": "deposit",
                                "amount": float(d['amount']), "currency": d['code'], "status": d['status']
                            })
                    except: pass

                if self.exchange.has.get('fetchWithdrawals'):
                    try:
                        withdrawals = self.exchange.fetch_withdrawals(code)
                        for w in withdrawals:
                            standardized_ledger.append({
                                "id": str(w.get('id')), "datetime": w['datetime'], "type": "withdrawal",
                                "amount": -float(w['amount']), "currency": w['code'], "status": w['status']
                            })
                    except: pass

            if standardized_ledger:
                standardized_ledger.sort(key=lambda x: x['datetime'], reverse=True)
                for entry in standardized_ledger[:10]:
                    display_message('info', get_message("account.ledger_entry", dt=entry['datetime'], type=entry['type'], amount=entry['amount'], currency=entry['currency'], status=entry['status']))
                
                display_message('action_stop', msg, result_icon="✓")
                return {"type": "ledger", "exchange": self.exchange_name, "currency": code, "entries": standardized_ledger}
            else:
                display_message('action_stop', msg, result_icon="⚠️")
                display_message('warning', get_message("account.no_ledger", code=code))
                if output_manager.json_mode:
                    return {"type": "ledger", "status": "error", "message": f"No ledger entries found for {code}"}
                return {"type": "ledger", "exchange": self.exchange_name, "currency": code, "entries": []}

        except Exception as e:
            if output_manager.json_mode: raise e
            display_message('action_stop', f"Error: {e}", result_icon="❌")
            return {"type": "ledger", "status": "error", "message": str(e)}
