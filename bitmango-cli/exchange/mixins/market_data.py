import sys
from bitmango.output import display_message, output as output_manager
from bitmango.exchange.risk_manager import RiskManager
from bitmango.messages import get_message

class MarketDataMixin:
    """Mixin for market data related methods."""

    def fetch_funding_rate(self, args):
        """Fetches the current funding rate for a symbol."""
        symbol = self._adapt_pair(args.pair)
        msg = get_message("market.fetching_funding", symbol=symbol, exchange=self.exchange_name)
        display_message('action_start', msg)
        try:
            res = self.exchange.fetch_funding_rate(symbol)
            
            # Risk Management: Data Freshness Check
            is_sandbox = getattr(self.args, 'sandbox', False)
            RiskManager.validate_market_data(res, is_sandbox=is_sandbox)
            
            rate = res.get('rate') or res.get('fundingRate')
            display_message('action_stop', get_message("market.funding_rate_msg", rate=rate), result_icon="✓")
            return {
                "type": "funding_rate",
                "exchange": self.exchange_name,
                "symbol": symbol,
                "rate": float(rate),
                "status": "success",
                "raw": res
            }
        except Exception as e:
            if output_manager.json_mode: raise e
            display_message('action_stop', get_message("exchange.action_failed", action="Fetch Funding", symbol=symbol, exchange=self.exchange_name, error=e), result_icon="❌")
            return {"type": "funding_rate", "status": "error", "message": str(e)}

    def markets(self, args):
        """Standardized list markets."""
        display_message('info', get_message("market.loading_markets", exchange=self.exchange_name))
        try:
            markets = self.exchange.load_markets()
            # Show first 20 symbols to avoid flooding
            symbols = list(markets.keys())
            for symbol in symbols[:20]:
                display_message('info', f"  {symbol}")
            if len(symbols) > 20:
                display_message('info', f"  ... and {len(symbols) - 20} more.")
            
            return {
                "type": "markets",
                "exchange": self.exchange_name,
                "symbols": symbols,
                "status": "success"
            }
        except Exception as e:
            if output_manager.json_mode: raise e
            display_message('error', get_message("exchange.fetch_error", item="markets", exchange=self.exchange_name, error=e))
            return {"type": "markets", "status": "error", "message": str(e)}

    def query_order_book(self, args):
        """
        Query the order book for a specific pair.
        """
        symbol = self._adapt_pair(args.pair)
        msg = get_message("market.fetching_order_book", symbol=symbol, exchange=self.exchange_name)
        display_message('action_start', msg)
        try:
            order_book = self.exchange.fetch_order_book(symbol)
            
            # Risk Management: Data Freshness Check
            is_sandbox = getattr(self.args, 'sandbox', False)
            RiskManager.validate_market_data(order_book, is_sandbox=is_sandbox)
            
            display_message('action_stop', msg, result_icon="✓")
            
            display_message('info', get_message("market.order_book_asks", symbol=symbol))
            for entry in order_book['asks'][:5]:
                price = entry[0]
                amount = entry[1]
                display_message('info', get_message("market.order_book_entry", price=price, amount=amount))
            
            display_message('info', "-" * 30)
            
            display_message('info', get_message("market.order_book_bids", symbol=symbol))
            for entry in order_book['bids'][:5]:
                price = entry[0]
                amount = entry[1]
                display_message('info', get_message("market.order_book_entry", price=price, amount=amount))
            
            return {
                "type": "order_book",
                "exchange": self.exchange_name,
                "symbol": symbol,
                "data": order_book,
                "status": "success"
            }
        except Exception as e:
            if output_manager.json_mode: raise e
            display_message('action_stop', msg, result_icon="❌")
            display_message('error', get_message("exchange.fetch_error", item="order book", exchange=self.exchange_name, error=e))
            raise e

    def ticker(self, args):
        """Standardized fetch ticker."""
        symbol = self._adapt_pair(args.pair)
        msg = get_message("market.fetching_ticker", symbol=symbol, exchange=self.exchange_name)
        display_message('action_start', msg)
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            
            # Risk Management: Stale Data Check
            is_sandbox = getattr(self.args, 'sandbox', False)
            RiskManager.validate_market_data(ticker, is_sandbox=is_sandbox)
            
            display_message('action_stop', msg, result_icon="✓")
            
            last = ticker.get('last')
            bid = ticker.get('bid')
            ask = ticker.get('ask')
            change = ticker.get('percentage')
            
            display_message('info', get_message("market.ticker_symbol", symbol=symbol))
            display_message('info', get_message("market.ticker_last", last=last))
            display_message('info', get_message("market.ticker_bid", bid=bid))
            display_message('info', get_message("market.ticker_ask", ask=ask))
            if change is not None:
                display_message('info', get_message("market.ticker_change", change=change))
                
            return {
                "type": "ticker",
                "exchange": self.exchange_name,
                "symbol": symbol,
                "data": ticker,
                "status": "success"
            }
        except Exception as e:
            if output_manager.json_mode: raise e
            display_message('action_stop', msg, result_icon="❌")
            display_message('error', get_message("exchange.fetch_error", item="ticker", exchange=self.exchange_name, error=e))
            raise e

    def ohlcv(self, args):
        """Standardized fetch OHLCV."""
        symbol = self._adapt_pair(args.pair)
        timeframe = getattr(args, 'timeframe', '1h')
        requested_limit = getattr(args, 'limit', 10)
        
        # 1. TIMEFRAME VALIDATION
        if self.exchange and hasattr(self.exchange, 'timeframes'):
            if timeframe not in self.exchange.timeframes:
                supported = ", ".join(list(self.exchange.timeframes.keys()))
                display_message('error', get_message("market.unsupported_timeframe", timeframe=timeframe, exchange=self.exchange_name))
                display_message('info', get_message("market.supported_timeframes", supported=supported))
                if output_manager.json_mode:
                    return {
                        "error": f"Unsupported timeframe: {timeframe}",
                        "status": "error",
                        "supported_timeframes": list(self.exchange.timeframes.keys())
                    }
                raise ValueError(f"Unsupported timeframe: {timeframe}")

        # We fetch enough candles for potential indicator calculation in plugins
        # If rsi/ema requested, we fetch extra
        fetch_limit = requested_limit
        if hasattr(args, 'rsi') and args.rsi:
            fetch_limit = max(fetch_limit, args.rsi + requested_limit + 10)
        if hasattr(args, 'ema') and args.ema:
            fetch_limit = max(fetch_limit, args.ema + requested_limit + 10)

        # 2. EXCHANGE-SPECIFIC ADAPTATION
        if self.exchange_name == 'phemex':
            # Phemex public OHLCV API often fails with code 30000 if limit is < 50
            fetch_limit = max(fetch_limit, 50)

        msg = get_message("market.fetching_ohlcv", limit=requested_limit, timeframe=timeframe, symbol=symbol, exchange=self.exchange_name)
        display_message('action_start', msg)
        try:
            candles = self.exchange.fetch_ohlcv(symbol, timeframe, limit=fetch_limit)
            display_message('action_stop', msg, result_icon="✓")
            
            # Risk Management: Stale Data Check (on latest candle)
            if candles:
                latest = candles[-1]
                is_sandbox = getattr(self.args, 'sandbox', False)
                RiskManager.validate_market_data({"timestamp": latest[0]}, is_sandbox=is_sandbox, timeframe=timeframe)

            # Construct final result
            result_candles = []
            # We only return the LAST requested_limit candles
            start_idx = max(0, len(candles) - requested_limit)
            
            for i in range(start_idx, len(candles)):
                c = candles[i]
                candle_data = {
                    "timestamp": c[0],
                    "open": c[1],
                    "high": c[2],
                    "low": c[3],
                    "close": c[4],
                    "volume": c[5],
                    "indicators": {}
                }
                result_candles.append(candle_data)

            # Display table (last 10 of the requested limit)
            table_limit = min(10, len(result_candles))
            header = get_message("market.ohlcv_header", timestamp="Timestamp", close="Close", volume="Volume")
            
            display_message('info', header)
            display_message('info', "-" * len(header))
            
            import datetime
            for rc in result_candles[-table_limit:]:
                dt = datetime.datetime.fromtimestamp(rc['timestamp'] / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
                line = get_message("market.ohlcv_entry", dt=dt, close=rc['close'], volume=rc['volume'])
                display_message('info', line)
            
            return {
                "type": "ohlcv",
                "exchange": self.exchange_name,
                "symbol": symbol,
                "timeframe": timeframe,
                "data": result_candles,
                "status": "success"
            }
        except Exception as e:
            if output_manager.json_mode: raise e
            display_message('action_stop', msg, result_icon="❌")
            display_message('error', get_message("exchange.fetch_error", item="OHLCV", exchange=self.exchange_name, error=e))
            raise e

    def watch_ticker(self, args):
        """Streams ticker updates via WebSocket."""
        import asyncio
        import ccxt.pro as ccxtpro
        
        async def stream_ticker():
            exchange_class = getattr(ccxtpro, self.exchange_name)
            pro_exchange = exchange_class({
                'apiKey': self.exchange.apiKey,
                'secret': self.exchange.secret,
                'privateKey': getattr(self.exchange, 'privateKey', None),
                'enableRateLimit': True,
                'options': self.exchange.options.copy()
            })
            if self.args.sandbox:
                try: await pro_exchange.set_sandbox_mode(True)
                except: pass
            
            symbol = self._adapt_pair(args.pair)
            display_message('info', get_message("market.streaming_ticker", symbol=symbol, exchange=self.exchange_name))
            try:
                while True:
                    ticker = await pro_exchange.watch_ticker(symbol)
                    last = ticker.get('last')
                    bid = ticker.get('bid')
                    ask = ticker.get('ask')
                    msg = f"{symbol} | Last: {last:<10} | Bid: {bid:<10} | Ask: {ask:<10}"
                    display_message('info', msg)
            except Exception as e:
                display_message('error', get_message("exchange.fetch_error", item="streaming ticker", exchange=self.exchange_name, error=e))
            finally:
                await pro_exchange.close()

        try:
            asyncio.run(stream_ticker())
        except KeyboardInterrupt:
            sys.stderr.write("\n")
            display_message('warning', get_message("market.streaming_stopped"))
        return None

    def watch_ohlcv(self, args):
        """Streams OHLCV updates via WebSocket."""
        import asyncio
        import ccxt.pro as ccxtpro
        import datetime
        
        async def stream_ohlcv():
            exchange_class = getattr(ccxtpro, self.exchange_name)
            pro_exchange = exchange_class({
                'apiKey': self.exchange.apiKey,
                'secret': self.exchange.secret,
                'enableRateLimit': True,
                'options': self.exchange.options.copy()
            })
            if self.args.sandbox:
                try: await pro_exchange.set_sandbox_mode(True)
                except: pass
            
            symbol = self._adapt_pair(args.pair)
            timeframe = getattr(args, 'timeframe', '1h')
            display_message('info', get_message("market.streaming_ohlcv", timeframe=timeframe, symbol=symbol))
            try:
                while True:
                    candles = await pro_exchange.watch_ohlcv(symbol, timeframe)
                    c = candles[-1]
                    dt = datetime.datetime.fromtimestamp(c[0] / 1000.0).strftime('%H:%M:%S')
                    msg = f"{dt} | O: {c[1]:<8} | H: {c[2]:<8} | L: {c[3]:<8} | C: {c[4]:<8} | V: {c[5]:<8}"
                    display_message('info', msg)
            except Exception as e:
                display_message('error', get_message("exchange.fetch_error", item="streaming OHLCV", exchange=self.exchange_name, error=e))
            finally:
                await pro_exchange.close()

        try:
            asyncio.run(stream_ohlcv())
        except KeyboardInterrupt:
            sys.stderr.write("\n")
            display_message('warning', get_message("market.streaming_stopped"))
        return None

    def watch_order_book(self, args):
        """Streams Order Book updates via WebSocket."""
        import asyncio
        import ccxt.pro as ccxtpro
        
        async def stream_ob():
            exchange_class = getattr(ccxtpro, self.exchange_name)
            pro_exchange = exchange_class({
                'apiKey': self.exchange.apiKey,
                'secret': self.exchange.secret,
                'enableRateLimit': True,
                'options': self.exchange.options.copy()
            })
            if self.args.sandbox:
                try: await pro_exchange.set_sandbox_mode(True)
                except: pass
            
            symbol = self._adapt_pair(args.pair)
            display_message('info', get_message("market.streaming_order_book", symbol=symbol))
            try:
                while True:
                    ob = await pro_exchange.watch_order_book(symbol)
                    best_bid = ob['bids'][0] if ob['bids'] else [0, 0]
                    best_ask = ob['asks'][0] if ob['asks'] else [0, 0]
                    msg = f"{symbol} | Bid: {best_bid[0]:<10} ({best_bid[1]:<8}) | Ask: {best_ask[0]:<10} ({best_ask[1]:<8})"
                    display_message('info', msg)
            except Exception as e:
                display_message('error', get_message("exchange.fetch_error", item="streaming order book", exchange=self.exchange_name, error=e))
            finally:
                await pro_exchange.close()

        try:
            asyncio.run(stream_ob())
        except KeyboardInterrupt:
            sys.stderr.write("\n")
            display_message('warning', get_message("market.streaming_stopped"))
        return None
