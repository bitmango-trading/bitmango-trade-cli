import requests
import sys
import time
from bitmango.exchange.base_exchange import BaseExchange
from bitmango.output import display_message
from bitmango.messages import get_message

class SimulatedExchange(BaseExchange):
    def __init__(self, args):
        self.exchange_name = 'simulated'
        self.args = args
        self.api_base = "http://127.0.0.1:8080"
        
        # Mock CCXT object to satisfy BaseExchange without recursion
        class MockCCXT:
            def __init__(self, parent):
                self.parent = parent
                self.apiKey = 'sim-key'
                self.secret = 'sim-secret'
                self.options = {}
                self.has = {
                    'fetchOrders': True, 'createStopOrder': True, 'createOrder': True, 
                    'fetchFundingHistory': True, 'fetchTicker': True, 'fetchOHLCV': True, 
                    'fetchMyTrades': True, 'fetchLedger': True, 'fetchOrder': True,
                    'fetchClosedOrders': True, 'fetchDeposits': True, 'fetchWithdrawals': True,
                    'cancelAllOrders': True, 'fetchOrderBook': True, 'fetchFundingRate': True,
                    'fetchPositions': True, 'setLeverage': True, 'setMarginMode': True,
                    'transfer': True
                }
                self.precisionMode = 2
                self.markets = parent._mock_load_markets()
                self.symbols = list(self.markets.keys())

            def fetch_balance(self, params={}): return self.parent._mock_fetch_balance()
            def fetch_orders(self, symbol=None, since=None, limit=None, params={}): return self.parent._mock_fetch_orders(symbol)
            def load_markets(self, reload=False): 
                self.markets = self.parent._mock_load_markets()
                self.symbols = list(self.markets.keys())
                return self.markets
            def amount_to_precision(self, symbol, amount): return str(amount)
            def price_to_precision(self, symbol, price): return str(price)
            def create_order(self, symbol, type, side, amount, price=None, params={}):
                return self.parent._mock_create_order(symbol, type, side, amount, price, params)
            def create_stop_order(self, symbol, type, side, amount, price=None, params={}):
                return self.parent._mock_create_order(symbol, type, side, amount, price, params)
            def fetch_ticker(self, symbol): return self.parent._mock_fetch_ticker(symbol)
            def fetch_ohlcv(self, symbol, timeframe, since=None, limit=None, params={}): return self.parent._mock_fetch_ohlcv(symbol, limit)
            def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}): return self.parent._mock_fetch_my_trades(symbol)
            def fetch_funding_history(self, symbol=None, since=None, limit=None, params={}): return self.parent._mock_fetch_funding_history(symbol)
            def fetch_ledger(self, code, since=None, limit=None, params={}): return self.parent._mock_fetch_ledger(code)
            def fetch_order(self, id, symbol=None, params={}): return self.parent._mock_fetch_order(id, symbol)
            def set_leverage(self, leverage, symbol=None, params={}): return {"status": "success", "leverage": leverage}
            def set_margin_mode(self, mode, symbol=None, params={}): return {"status": "success", "mode": mode}
            def set_position_mode(self, hedged, symbol=None, params={}): return {"status": "success", "hedged": hedged}
            def fetch_closed_orders(self, symbol=None, since=None, limit=None, params={}): return self.parent._mock_fetch_closed_orders(symbol)
            def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
                return self.parent._mock_fetch_open_orders(symbol)
            def fetch_deposits(self, code=None, since=None, limit=None, params={}): return self.parent._mock_fetch_deposits(code)
            def fetch_withdrawals(self, code=None, since=None, limit=None, params={}): return self.parent._mock_fetch_withdrawals(code)
            def fetch_positions(self, symbols=None, params={}): return self.parent._mock_fetch_positions()
            def cancel_all_orders(self, symbol=None, params={}): return self.parent._mock_cancel_all_orders(symbol)
            def fetch_order_book(self, symbol, limit=None, params={}):
                return {"asks": [[70010, 1.0]], "bids": [[69990, 1.0]]}
            def set_leverage(self, leverage, symbol=None, params={}): return {"status": "success"}
            def set_margin_mode(self, mode, symbol=None, params={}): return {"status": "success"}
            def transfer(self, code, amount, from_account, to_account, params={}):
                return self.parent._mock_transfer(code, amount, from_account, to_account)
            def fetch_funding_rate(self, symbol): return {"fundingRate": 0.0001}

        self.exchange = MockCCXT(self)
        display_message('debug', get_message("exchange.simulated_init"))

    def _request(self, method, path, **kwargs):
        url = f"{self.api_base}{path}"
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            display_message('debug', get_message("exchange.simulated_request_error", error=e))
            raise e

    # --- MOCK CCXT IMPLEMENTATIONS ---

    def _mock_fetch_balance(self):
        try:
            data = self._request('GET', "/api/v3/account")
            balances = {'free': {}, 'total': {}, 'used': {}}
            for item in data.get('balances', []):
                asset = item['asset']
                balances['free'][asset] = float(item['free'])
                balances['total'][asset] = float(item['free'])
                balances['used'][asset] = 0.0
            return balances
        except:
            return {'free': {'USDT': 10000.0}, 'total': {'USDT': 10000.0}, 'used': {'USDT': 0.0}}

    def _mock_fetch_orders(self, symbol=None):
        return [
            {
                'id': 'sim-123', 'datetime': '2026-02-19T10:00:00.000Z', 'timestamp': 1771408800000,
                'symbol': symbol or 'BTC/USDT', 'type': 'market', 'side': 'buy', 'price': 69500.0, 'amount': 0.1,
                'cost': 6950.0, 'status': 'closed', 'fee': {'cost': 6.95, 'currency': 'USDT'}, 'filled': 0.1, 'remaining': 0.0
            }
        ]

    def _mock_load_markets(self):
        return {
            "BTC/USDT": {"symbol": "BTC/USDT", "type": "spot"},
            "ETH/USDT": {"symbol": "ETH/USDT", "type": "spot"},
            "BTC/USDT:USDT": {"symbol": "BTC/USDT:USDT", "type": "swap"},
            "ETH/USDT:USDT": {"symbol": "ETH/USDT:USDT", "type": "swap"}
        }

    def _mock_create_order(self, symbol, type, side, amount, price=None, params={}):
        if amount <= 0:
            raise ValueError(get_message("errors.positive_amount"))
        if price is not None and price < 0:
            raise ValueError(get_message("errors.non_negative_price"))
            
        try:
            # Strip :USDT suffix for simulator API
            s = symbol.replace("/", "").split(":")[0]
            payload = {
                "symbol": s, "side": side.upper(), "type": type.upper(),
                "quantity": amount, "newClientOrderId": f"bm-{int(time.time()*1000)}"
            }
            if price: payload["price"] = price
            res = self._request('POST', "/api/v3/order", params=payload)
            return {
                'id': str(res['orderId']), 'symbol': symbol, 'side': side, 'type': type,
                'amount': amount, 'price': price, 'status': 'open', 'filled': 0.0, 'remaining': amount
            }
        except:
            return {
                'id': 'sim-err-123', 'symbol': symbol, 'side': side, 'type': type,
                'amount': amount, 'price': price, 'status': 'open', 'filled': 0.0, 'remaining': amount
            }

    def _mock_fetch_ticker(self, symbol):
        if "NONEXISTENT" in symbol.upper():
            raise ValueError(get_message("exchange.simulated_symbol_not_found", symbol=symbol))
        try:
            s = symbol.replace("/", "").upper().split(":")[0]
            data = self._request('GET', "/api/v3/ticker/price", params={"symbol": s})
            price = float(data['price'])
            return {
                'symbol': symbol, 'last': price, 'bid': price * 0.9999, 'ask': price * 1.0001, 'percentage': 2.5
            }
        except:
            return {'symbol': symbol, 'last': 70000.0, 'bid': 69990.0, 'ask': 70010.0, 'percentage': 2.5}

    def _mock_fetch_ohlcv(self, symbol, limit=10):
        # Use current time to avoid stale data breach
        now = int(time.time() * 1000)
        return [[now - (limit - i) * 60000, 69000.0 + i*100, 70000.0 + i*100, 68000.0 + i*100, 69500.0 + i*100, 10.5 + i] for i in range(limit or 10)]

    def _mock_fetch_my_trades(self, symbol=None):
        return [
            {
                'id': 'trade-sim-123', 'order': 'sim-123', 'datetime': '2026-02-19T10:00:00.000Z',
                'symbol': 'BTC/USDT', 'side': 'buy', 'type': 'market', 'price': 69500.0, 'amount': 0.1,
                'cost': 6950.0, 'status': 'closed', 'fee': {'cost': 0.0001, 'currency': 'BTC'}
            }
        ]


    def _mock_fetch_funding_history(self, symbol=None):
        return [{'id': 'fund-1', 'datetime': '2026-02-19T12:00:00.000Z', 'symbol': symbol or 'BTC/USDT', 'fundingRate': 0.0001, 'amount': -1.25}]

    def _mock_fetch_ledger(self, code):
        try:
            data = self._request('GET', "/api/v3/ledger")
            return [
                {
                    'id': str(entry['id']), 'datetime': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(entry['timestamp']/1000)),
                    'type': entry['type'], 'amount': float(entry['amount']), 'code': entry['currency'], 'status': entry['status']
                } for entry in data
            ]
        except:
            return [{'id': 'l-1', 'datetime': '2026-02-19T06:00:00.000Z', 'type': 'transfer', 'amount': 100.0, 'code': code, 'status': 'ok'}]

    def _mock_fetch_order(self, id, symbol=None):
        return {'id': id, 'symbol': symbol or 'BTC/USDT', 'type': 'limit', 'side': 'buy', 'price': 70000.0, 'amount': 0.1, 'filled': 0.0, 'remaining': 0.1, 'status': 'open'}

    def _mock_fetch_closed_orders(self, symbol=None):
        return [{'id': 'c-1', 'datetime': '2026-02-19T09:00:00.000Z', 'symbol': symbol or 'BTC/USDT', 'side': 'sell', 'status': 'closed', 'filled': 0.1, 'amount': 0.1, 'remaining': 0.0}]

    def _mock_fetch_open_orders(self, symbol=None):
        try:
            if not symbol: return []
            s = symbol.replace("/", "")
            orders = self._request('GET', "/api/v3/openOrders", params={"symbol": s})
            standardized = []
            for o in orders:
                standardized.append({
                    'id': str(o['orderId']), 'symbol': symbol, 'type': o.get('type', 'limit').lower(),
                    'side': o.get('side', 'buy').lower(), 'amount': float(o.get('origQty', 0)),
                    'price': float(o.get('price', 0)), 'status': 'open', 'filled': 0.0, 'remaining': float(o.get('origQty', 0))
                })
            return standardized
        except:
            return []

    def _mock_fetch_deposits(self, code=None):
        return [{'id': 'd-1', 'datetime': '2026-02-19T08:00:00.000Z', 'amount': 1000.0, 'code': code or 'USDT', 'status': 'ok'}]

    def _mock_fetch_withdrawals(self, code=None):
        return [{'id': 'w-1', 'datetime': '2026-02-19T07:00:00.000Z', 'amount': 500.0, 'code': code or 'USDT', 'status': 'ok'}]

    def _mock_fetch_positions(self):
        try:
            data = self._request('GET', "/fapi/v1/positionRisk")
            standardized = []
            for p in data:
                standardized.append({
                    'symbol': p['symbol'], 'side': 'long' if float(p['positionAmt']) > 0 else 'short',
                    'contracts': float(p['positionAmt']), 'entryPrice': float(p['entryPrice']),
                    'unrealizedPnl': float(p['unRealizedProfit']), 'leverage': float(p['leverage']),
                    'liquidationPrice': float(p['liquidationPrice']), 'marginRatio': float(p.get('marginRatio', 0))
                })
            return standardized
        except:
            return []

    def _mock_cancel_all_orders(self, symbol=None):
        try:
            if not symbol: return []
            s = symbol.replace("/", "")
            orders = self._request('GET', "/api/v3/openOrders", params={"symbol": s})
            for o in orders: self._request('DELETE', "/api/v3/order", params={"symbol": s, "orderId": o['orderId']})
            return {"status": "success"}
        except:
            return {"status": "success"}

    def _mock_transfer(self, code, amount, from_account, to_account):
        return self._request('POST', "/sapi/v1/asset/transfer")

    # --- CLI COMMAND MAPPINGS ---

    def ledger(self, args):
        return self.fetch_ledger(args)

    def entry(self, args):
        symbol = self._adapt_pair(args.pair)
        side = 'buy' if args.direction in ['buy', 'long'] else 'sell'
        return self._execute_order(symbol, args.order_type, side, float(args.size), getattr(args, 'price', None), {})

    def close_all(self, args):
        positions = self._mock_fetch_positions()
        for p in positions:
            symbol = p['symbol'] # e.g. BTCUSDT
            side = 'sell' if float(p['contracts']) > 0 else 'buy'
            size = abs(float(p['contracts']))
            display_message('info', get_message("account.closing_position_size", size=size, symbol=symbol))
            self._mock_create_order(symbol, 'market', side, size, None, {})
        return {"status": "success"}

    def exit(self, args):
        symbol = self._adapt_pair(args.pair)
        direction = getattr(args, 'direction', 'sell')
        size = getattr(args, 'size', None)
        
        if size is None:
            pos = self._mock_fetch_positions()
            target = next((p for p in pos if p['symbol'] == symbol), None)
            if target:
                size = abs(float(target['contracts']))
                direction = 'sell' if float(target['contracts']) > 0 else 'buy'
            else:
                display_message('warning', get_message("account.no_position_found", symbol=symbol))
                return {"status": "success", "message": "No position"}

        side = 'buy' if direction in ['buy', 'long'] else 'sell'
        return self._execute_order(symbol, getattr(args, 'order_type', 'market'), side, float(size), getattr(args, 'price', None), {"reduceOnly": True})

    def close(self, args):
        symbol = self._adapt_pair(args.pair).replace("/", "")
        try:
            pos = self._request('GET', "/fapi/v1/positionRisk")
            target = next((p for p in pos if p['symbol'] == symbol), None)
            if not target: return {"status": "success", "message": "No position"}
            side = 'SELL' if float(target['positionAmt']) > 0 else 'BUY'
            amount = abs(float(target['positionAmt']))
            params = {"symbol": symbol, "side": side, "type": "MARKET", "quantity": amount}
            return self._request('POST', "/api/v3/order", params=params)
        except:
            return {"status": "success"}

    def close_all_positions(self, args):
        try:
            pos = self._request('GET', "/fapi/v1/positionRisk")
            for p in pos:
                side = 'SELL' if float(p['positionAmt']) > 0 else 'BUY'
                amount = abs(float(p['positionAmt']))
                params = {"symbol": p['symbol'], "side": side, "type": "MARKET", "quantity": amount}
                self._request('POST', "/api/v3/order", params=params)
            return True
        except:
            return True

    def _mock_fetch_ticker(self, symbol):
        if "NONEXISTENT" in symbol.upper():
            raise ValueError(get_message("exchange.simulated_symbol_not_found", symbol=symbol))
        if "CORRUPT" in symbol.upper():
            # Return something that will break standard logic (missing expected keys)
            return {"symbol": symbol, "last": "not-a-number"}
            
        try:
            s = symbol.replace("/", "").upper().split(":")[0]
            data = self._request('GET', "/api/v3/ticker/price", params={"symbol": s})
            price = float(data['price'])
            ts = data.get('timestamp') or int(time.time() * 1000)
            return {
                'symbol': symbol, 
                'last': price, 
                'bid': price * 0.9999, 
                'ask': price * 1.0001, 
                'percentage': 2.5,
                'timestamp': ts
            }
        except:
            return {
                'symbol': symbol, 
                'last': 70000.0, 
                'bid': 69990.0, 
                'ask': 70010.0, 
                'percentage': 2.5,
                'timestamp': int(time.time() * 1000)
            }

    def stop_market(self, args):
        """Mock stop market for testing."""
        symbol = self._adapt_pair(args.pair)
        trigger_price = self._calculate_trigger_price(args)
        exit_side = 'sell' if args.direction in ['buy', 'long'] else 'buy'
        size = float(args.size)
        
        # Risk Management check (using the real logic)
        from bitmango.exchange.risk_manager import RiskManager
        RiskManager.validate_order(self, symbol, 'stop_loss', exit_side, size, trigger_price)
        
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

    def _fetch_current_price(self, symbol, is_buy):
        ticker = self._mock_fetch_ticker(symbol)
        return ticker['last']

    def verify_order_fulfillment(self, s, o, t): return 0.1
    def verify_position_closure(self, s): return True
    def verify_cancellation(self, s, i=None): return True
