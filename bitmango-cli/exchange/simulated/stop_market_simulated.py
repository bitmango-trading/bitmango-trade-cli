from bitmango.exchange.base_exchange import BaseExchange
from bitmango.output import display_message, output as output_manager
from bitmango.messages import get_message

class StopMarketSimulated(BaseExchange):
    """Mock stop market for testing."""
    def stop_market(self, args):
        symbol = self._adapt_pair(args.pair)
        trigger_price = self._calculate_trigger_price(args)
        exit_side = 'sell' if args.direction in ['buy', 'long'] else 'buy'
        size = float(args.size)
        
        msg = get_message("exchange.simulated_placing_stop", side=exit_side, amount=size, symbol=symbol, price=trigger_price)
        display_message('action_start', msg)
        
        try:
            # Risk Management check (using the real logic)
            from bitmango.exchange.risk_manager import RiskManager
            RiskManager.validate_order(self, symbol, 'stop_loss', exit_side, size, trigger_price)
            
            display_message('action_stop', msg, result_icon="✓")
            return {
                "type": "stop_order",
                "exchange": "simulated",
                "symbol": symbol,
                "order": {
                    "id": "sim-stop-123",
                    "symbol": symbol,
                    "status": "open",
                    "stopPrice": float(trigger_price)
                },
                "status": "success"
            }
        except Exception as e:
            if output_manager.json_mode: raise e
            display_message('action_stop', msg, result_icon="❌")
            display_message('error', get_message("exchange.simulated_stop_error", error=e))
            raise e

    def _fetch_current_price(self, symbol, is_buy):
        # Mock price
        return 70000.0
