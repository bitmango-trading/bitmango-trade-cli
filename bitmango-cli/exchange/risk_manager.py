import time
import os
from bitmango.output import display_message, output as output_manager
from bitmango.messages import get_message

class RiskBreach(ValueError):
    """Exception raised when a risk threshold is exceeded."""
    pass

class SecurityBreach(ValueError):
    """Exception raised when a security policy is violated."""
    pass

class RiskManager:
    """Centralized safety and risk control layer for all trading operations."""
    
    # Defaults
    MAX_PRICE_DEVIATION_PCT = float(os.getenv("BITMANGO_MAX_PRICE_DEVIATION", 0.05)) # 5%
    MAX_ORDER_USD = float(os.getenv("BITMANGO_MAX_ORDER_USD", 100.0)) # Sacred $100 safety default
    MAX_STALE_SECONDS = int(os.getenv("BITMANGO_MAX_STALE_SECONDS", 10)) # 10s data limit (STRICT)
    
    @staticmethod
    def check_config():
        """Warns if risk parameters are configured insecurely."""
        if os.getenv("BITMANGO_SAFETY_OVERRIDE") == "true":
            return

        if RiskManager.MAX_STALE_SECONDS > 30:
            display_message('warning', get_message("risk.insecure_stale", val=RiskManager.MAX_STALE_SECONDS))
        
        if RiskManager.MAX_PRICE_DEVIATION_PCT > 0.20:
            display_message('warning', get_message("risk.insecure_deviation", val=RiskManager.MAX_PRICE_DEVIATION_PCT*100))

        if RiskManager.MAX_ORDER_USD > 100000:
             display_message('warning', get_message("risk.pro_safety_cap", val=RiskManager.MAX_ORDER_USD))

    @staticmethod
    def validate_order(exchange, symbol, order_type, side, amount, price=None):
        """
        Vets an order against safety constraints.
        Raises RiskBreach if risk threshold is breached.
        """
        # 1. Size Check
        try:
            current_price = exchange._fetch_current_price(symbol, side == 'buy')
            
            # Determine Notional Value (USD)
            # Standard: Amount (Base) * Price (Quote/Base) = Notional (Quote)
            # Inverse:  Amount (Contracts/USD) = Notional (Quote) 
            is_inverse = False
            contract_size = 1.0
            
            # Ensure markets are loaded to check inverse status
            if hasattr(exchange, 'ensure_markets'):
                exchange.ensure_markets()
                
            if exchange.exchange and hasattr(exchange.exchange, 'markets') and symbol in exchange.exchange.markets:
                market = exchange.exchange.markets[symbol]
                is_inverse = market.get('inverse', False)
                contract_size = market.get('contractSize', 1.0)

            if is_inverse:
                # For Inverse, CCXT 'amount' is usually contracts (e.g. $1 each on Phemex)
                notional_value = float(amount) * float(contract_size)
                display_message('debug', get_message("risk.debug_inverse_detected", amount=amount, contract_size=contract_size, val=notional_value))
            elif current_price:
                notional_value = float(amount) * float(current_price)
            else:
                # If price cannot be fetched, we use a conservative safe default for calculation 
                display_message('debug', get_message("risk.debug_price_fetch_failed", symbol=symbol))
                notional_value = 100.0 # Safe default
                
            if notional_value > RiskManager.MAX_ORDER_USD:
                raise RiskBreach(get_message("risk.breach_order_value", val=notional_value, cap=RiskManager.MAX_ORDER_USD))
        except Exception as e:
            if isinstance(e, RiskBreach): raise
            display_message('debug', get_message("risk.debug_notional_calc_failed", error=e))

        # 2. Price Protection (Fat-Finger Guard)
        if order_type == 'limit' and price:
            try:
                mid_price = current_price if current_price else exchange.fetch_ticker(symbol)['last']
                deviation = abs(float(price) - mid_price) / mid_price
                if deviation > RiskManager.MAX_PRICE_DEVIATION_PCT:
                    raise RiskBreach(get_message("risk.breach_price_deviation", price=price, dev=deviation*100, mid=mid_price, max_dev=RiskManager.MAX_PRICE_DEVIATION_PCT*100))
            except Exception as e:
                if isinstance(e, RiskBreach): raise
                display_message('debug', get_message("risk.debug_price_protection_skipped", error=e))

        display_message('debug', get_message("risk.debug_passed_checks", amount=amount, symbol=symbol))
        return True

    @staticmethod
    def validate_market_data(data, is_sandbox=False, timeframe=None):
        """Ensures market data is not too old (stale) or from the future (unsynced)."""
        if is_sandbox:
            return True

        now = time.time() * 1000 # ms
        ts = data.get('timestamp')
        if ts:
            diff_ms = now - ts
            age_seconds = diff_ms / 1000
            allowed_stale = RiskManager.MAX_STALE_SECONDS
            if timeframe:
                duration = RiskManager._parse_timeframe(timeframe)
                allowed_stale += duration

            if age_seconds > allowed_stale:
                raise RiskBreach(get_message("risk.breach_stale_data", age=age_seconds, max_age=allowed_stale))
            if age_seconds < -5.0:
                raise RiskBreach(get_message("risk.breach_future_data", age=-age_seconds))
        return True

    @staticmethod
    def _parse_timeframe(tf):
        try:
            amount = int(tf[:-1])
            unit = tf[-1].lower()
            if unit == 's': return amount
            if unit == 'm': return amount * 60
            if unit == 'h': return amount * 3600
            if unit == 'd': return amount * 86400
            if unit == 'w': return amount * 604800
            if unit == 'M': return amount * 2592000
            return 0
        except:
            return 0

    @staticmethod
    def check_api_permissions(exchange):
        """Verifies API keys are correctly scoped."""
        info = getattr(exchange, 'info', {}) if hasattr(exchange, 'info') else exchange
        danger_keywords = ['withdraw', 'withdrawal', 'transfer', 'subaccounttransfer']
        
        def _check_nested(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if any(kw in k.lower() for kw in danger_keywords):
                        if v is True or (isinstance(v, str) and v.lower() in ['true', 'ok', 'enabled']):
                            raise SecurityBreach(get_message("risk.security_insecure_permission", permission=k))
                    _check_nested(v)
            elif isinstance(obj, list):
                for item in obj:
                    if isinstance(item, str):
                        if any(kw in item.lower() for kw in danger_keywords):
                            raise SecurityBreach(get_message("risk.security_insecure_permission", permission=item))
                    _check_nested(item)

        _check_nested(info)
        return True
