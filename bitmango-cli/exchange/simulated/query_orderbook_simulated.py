import requests
from bitmango.exchange.base_exchange import BaseExchange
from bitmango.output import display_message
from bitmango.messages import get_message

class SimulatedQueryOrderBook(BaseExchange):
    def __init__(self, args):
        self.exchange_name = 'simulated'
        self.args = args
        self.api_base = "http://127.0.0.1:8080"
        display_message('debug', get_message("exchange.simulated_init"))

    def _request(self, method, path, **kwargs):
        url = f"{self.api_base}{path}"
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            display_message('error', get_message("exchange.simulated_request_error", error=e))
            raise e

    def query_order_book(self, args):
        symbol = args.pair.replace("-", "").upper()
        msg = get_message("market.fetching_order_book", symbol=symbol, exchange="simulated")
        display_message('action_start', msg)
        try:
            order_book = self._request('GET', "/api/v3/depth", params={"symbol": symbol})
            display_message('action_stop', msg, result_icon="✓")
            
            display_message('info', get_message("exchange.simulated_order_book", symbol=symbol))
            display_message('info', "  Bids:")
            for bid in order_book.get('bids', [])[:5]:
                display_message('info', get_message("market.order_book_entry", price=bid[0], amount=bid[1]))
            
            display_message('info', "  Asks:")
            for ask in order_book.get('asks', [])[:5]:
                display_message('info', get_message("market.order_book_entry", price=ask[0], amount=ask[1]))
            
            return {
                "type": "order_book",
                "exchange": "simulated",
                "symbol": symbol,
                "bids": [[float(b[0]), float(b[1])] for b in order_book.get('bids', [])],
                "asks": [[float(a[0]), float(a[1])] for a in order_book.get('asks', [])]
            }
                
        except Exception as e:
            display_message('action_stop', msg, result_icon="❌")
            return {"type": "order_book", "status": "error", "message": str(e)}
