import sys
import time
import ccxt
import os
from bitmango.exchange.functions import format_symbol, record_operation, get_health_status
from bitmango.output import display_message, output as output_manager
from bitmango.vault import load_vault
from bitmango.exchange.risk_manager import RiskManager
from bitmango.messages import get_message

# Import Mixins
from bitmango.exchange.mixins.market_data import MarketDataMixin
from bitmango.exchange.mixins.account import AccountMixin
from bitmango.exchange.mixins.trading import TradingMixin

class BaseExchange(MarketDataMixin, AccountMixin, TradingMixin):
    def __init__(self, exchange_name, args):
        # Global risk configuration audit
        RiskManager.check_config()
        
        display_message('debug', get_message("exchange.initializing", exchange=exchange_name))
        self.exchange_name = exchange_name
        self.args = args
        if exchange_name == 'simulated':
            self.exchange = None
        else:
            self.exchange = self._initialize_exchange()
            try:
                self.exchange.load_markets()
            except Exception as e:
                display_message('debug', get_message("exchange.failed_load_markets", error=e))

    def display_message(self, m_type, text, icon=None, result_icon=None):
        """Wrapper for the global display_message function."""
        display_message(m_type, text, icon, result_icon)

    def _initialize_exchange(self):
        display_message('debug', get_message("exchange.configuring_ccxt", exchange=self.exchange_name))
        
        is_public = hasattr(self.args, 'command') and self.args.command in ['markets', 'query_order_book', 'funding', 'ticker', 'ohlcv']
        
        # 1. Handle Public Commands Early (No Keys Needed)
        if is_public:
            config = {
                'enableRateLimit': True,
                'options': {'defaultType': 'swap' if self.exchange_name != 'binance' else getattr(self.args, 'market_type', 'spot')},
                'timeout': 20000,
            }
            if self.exchange_name == 'phemex': config['options']['defaultSettle'] = 'USDT'
            exchange_class = getattr(ccxt, getattr(self, 'exchange_class_override', self.exchange_name))
            exchange = exchange_class(config)
            if self.args.sandbox:
                try: exchange.set_sandbox_mode(True)
                except: pass
            
            if hasattr(self.args, 'verbose') and self.args.verbose and not output_manager.json_mode:
                exchange.verbose = True
            return exchange

        # 2. Security Check (Private Commands)
        try:
            api_keys_path = os.path.abspath("api_keys.py")
            if os.path.exists(api_keys_path):
                import stat
                st = os.stat(api_keys_path)
                if st.st_mode & (stat.S_IRWXG | stat.S_IRWXO):
                    display_message('warning', get_message("exchange.api_keys_warning", path=api_keys_path))
        except Exception: pass

        # Config Setup
        api_key, secret, private_key = None, None, None
        env_prefix = self.exchange_name.upper()
        
        if self.args.sandbox:
            api_key = os.environ.get(f"{env_prefix}_TESTNET_API_KEY")
            secret = os.environ.get(f"{env_prefix}_TESTNET_SECRET")
            private_key = os.environ.get(f"{env_prefix}_TESTNET_PRIVATE_KEY")
        
        if not api_key:
            api_key = os.environ.get(f"{env_prefix}_API_KEY")
            secret = os.environ.get(f"{env_prefix}_SECRET")
            private_key = os.environ.get(f"{env_prefix}_PRIVATE_KEY")

        if not api_key:
            vault = load_vault()
            if vault:
                target = f"{self.exchange_name}_testnet" if self.args.sandbox else self.exchange_name
                if self.exchange_name == 'binance' and self.args.sandbox:
                    m_type = getattr(self.args, 'market_type', 'spot')
                    targets = [f"binance_{m_type}_testnet", "binance_testnet_rsa", "binance_testnet"]
                else: targets = [target]

                for t in targets:
                    keys = vault.get("keys", {}).get(t)
                    if keys:
                        api_key, secret, private_key = keys.get("api_key"), keys.get("secret"), keys.get("private_key")
                        break

        if not api_key:
            from api_keys import API_KEYS
            target = f"{self.exchange_name}_testnet" if self.args.sandbox else self.exchange_name
            if self.exchange_name == 'binance' and self.args.sandbox:
                m_type = getattr(self.args, 'market_type', 'spot')
                targets = [f"binance_{m_type}_testnet", "binance_testnet_rsa", "binance_testnet"]
            else: targets = [target]
            if not self.args.sandbox: targets.append(self.exchange_name)

            for t in targets:
                kd = API_KEYS.get(t, {})
                if kd.get('api_key') or kd.get('private_key'):
                    api_key = kd.get('api_key')
                    secret = kd.get('secret')
                    private_key = kd.get('private_key')
                    break
            if api_key: display_message('warning', get_message("exchange.api_keys_note", exchange=self.exchange_name))

        config = {
            'enableRateLimit': True,
            'options': {'defaultType': 'swap' if self.exchange_name != 'binance' else getattr(self.args, 'market_type', 'spot')},
            'timeout': 20000,
        }
        if api_key: config['apiKey'] = api_key.strip()
        if secret: config['secret'] = secret.strip()
        if private_key: config['privateKey'] = private_key.strip()

        if self.exchange_name != 'simulated': config['verify'] = True
        if self.exchange_name == 'phemex': config['options']['defaultSettle'] = 'USDT'
        
        exchange_class = getattr(ccxt, getattr(self, 'exchange_class_override', self.exchange_name))
        if self.exchange_name == 'bybit' and self.args.sandbox: config['hostname'] = 'bybitglobal.com'
        exchange = exchange_class(config)

        # Risk Management: Security Check (Permissions)
        # Note: Some exchanges require load_markets or a private call to fetch permissions.
        # For now, we check what is available in the exchange info.
        if api_key:
            try:
                RiskManager.check_api_permissions(exchange)
            except Exception as e:
                if "SECURITY BREACH" in str(e):
                    display_message('error', str(e))
                    raise e

        if self.args.sandbox:
            if self.exchange_name == 'binance':
                market_type = getattr(self.args, 'market_type', 'spot')
                if market_type == 'futures':
                    exchange.options['fetchCurrencies'] = False
                    # Use 'linear' and 'inverse' for futures in CCXT to avoid margin sapi
                    exchange.options['fetchMarkets'] = ['linear', 'inverse']
                    exchange.options['defaultType'] = 'future' 
                    if 'demo' in exchange.urls:
                        exchange.urls['api'] = exchange.urls['demo'].copy()
                        # Add dummy sapi to prevent CCXT crash
                        if 'sapi' not in exchange.urls['api']:
                            exchange.urls['api']['sapi'] = 'https://api.binance.com/sapi/v1'
                    else:
                        demo_url = 'https://demo-fapi.binance.com/fapi/v1'
                        exchange.urls['api'] = {
                            'fapiPublic': demo_url, 'fapiPrivate': demo_url, 'fapiData': demo_url,
                            'public': demo_url, 'private': demo_url, 'sapi': 'https://api.binance.com/sapi/v1'
                        }
                else: exchange.set_sandbox_mode(True)
            elif self.exchange_name == 'bitfinex':
                exchange.urls['api'].update({'public': 'https://api-pub.bitfinex.com', 'private': 'https://api.bitfinex.com'})
            else:
                try: exchange.set_sandbox_mode(True)
                except: pass

        # FINAL credential checks and overrides (must be AFTER set_sandbox_mode)
        if self.exchange_name == 'binance':
            if private_key and not exchange.secret:
                exchange.secret = 'RSA_ACTIVE'
                exchange.requiredCredentials['secret'] = False
                display_message('debug', get_message("exchange.applied_rsa_override"))

        if hasattr(self.args, 'verbose') and self.args.verbose and not output_manager.json_mode:
            exchange.verbose = True
        return exchange

    def ensure_markets(self):
        """Loads markets if they haven't been loaded yet."""
        if self.exchange and (not self.exchange.markets or len(self.exchange.markets) == 0):
            self.exchange.load_markets()

    def _find_symbol_match(self, pair):
        """Attempts to find a matching CCXT symbol using fuzzy matching, prioritizing the requested market type."""
        if not self.exchange or not hasattr(self.exchange, 'symbols') or not self.exchange.symbols:
            return None
        
        pair_upper = pair.upper()
        target_market_type = getattr(self.args, 'market_type', 'futures') # Default to futures if not specified
        
        def get_type_score(symbol):
            """Returns a higher score if the symbol matches the requested market type."""
            if not self.exchange.markets or symbol not in self.exchange.markets:
                return 0
            m_type = self.exchange.markets[symbol].get('type')
            
            if target_market_type == 'spot':
                return 2 if m_type == 'spot' else 1
            else: # futures
                return 2 if m_type in ['swap', 'future'] else 1

        candidates = []

        # 1. Exact match
        if pair_upper in self.exchange.symbols:
            candidates.append(pair_upper)
            
        # 2. Slash replacement
        slash_pair = pair_upper.replace('-', '/')
        if slash_pair in self.exchange.symbols and slash_pair not in candidates:
            candidates.append(slash_pair)
            
        # 3. Fuzzy match (remove all separators)
        clean_input = pair_upper.replace('-', '').replace('/', '').replace(':', '').replace('_', '')
        for symbol in self.exchange.symbols:
            clean_symbol = symbol.upper().replace('-', '').replace('/', '').replace(':', '').replace('_', '')
            if clean_symbol == clean_input:
                if symbol not in candidates: candidates.append(symbol)
            elif clean_symbol in (clean_input + 'USDT', clean_input + 'USD', clean_input + 'USDC', clean_input + clean_input.split('USD')[0]):
                 if symbol not in candidates: candidates.append(symbol)
        
        # Special case for SOL/USD:SOL style fuzzy matching
        for symbol in self.exchange.symbols:
            clean_symbol = symbol.upper().replace('-', '').replace('/', '').replace(':', '').replace('_', '')
            if clean_symbol.startswith(clean_input) and len(clean_symbol) <= len(clean_input) + 4:
                 if symbol not in candidates: candidates.append(symbol)

        if not candidates:
            return None

        # Filter and Sort Candidates
        # Priority 1: Market Type Match (Swap/Future vs Spot)
        # Priority 2: Phemex Inverse preference (:BTC over :USD) if applicable
        # Priority 3: Standard Suffix (:USD/:USDT)
        
        scored_candidates = []
        for c in candidates:
            score = get_type_score(c) * 10 # Base score from type (20 or 10)
            
            # Boost for standard suffixes
            if c.upper().endswith(':USD') or c.upper().endswith(':USDT'):
                score += 2
            
            # Phemex Specific: Boost :BTC for Inverse if futures requested
            if self.exchange_name == 'phemex' and target_market_type != 'spot' and c.upper().endswith(':BTC'):
                score += 5 
                
            scored_candidates.append((score, c))
            
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        
        return scored_candidates[0][1]

    def _adapt_pair(self, pair):
        if not pair: return None
        
        # 1. Try to find a match in loaded markets (Universal Normalization)
        match = self._find_symbol_match(pair)
        if match:
            return match
            
        # 2. Fallback to hardcoded logic if no match found or markets not loaded
        market_type = getattr(self.args, 'market_type', 'futures')
        adapted = pair

        if market_type == 'futures':
            if self.exchange_name == 'bybit': 
                adapted = format_symbol(pair, format_type='slash') + ':USDT'
            elif self.exchange_name == 'phemex':
                formatted = format_symbol(pair, format_type='slash')
                # Phemex logic: USDT-margined ends in :USDT, Coin-margined (Inverse) ends in :BTC or :USD
                upair = pair.upper()
                if upair.endswith('-USDT') or upair.endswith('/USDT') or upair.endswith('USDT'):
                    adapted = formatted + ':USDT'
                elif upair.endswith('-USD') or upair.endswith('/USD') or upair.endswith('USD'):
                    # Default to :BTC for Inverse as it is more standard than :USD (uBTCUSD)
                    adapted = formatted + ':BTC'
                else:
                    adapted = formatted + ':USDT'
            elif self.exchange_name == 'bitget': 
                adapted = format_symbol(pair, format_type='slash') + ':USDT'
            elif self.exchange_name == 'okx': 
                adapted = format_symbol(pair, format_type='slash-colon-usdt')
            elif self.exchange_name == 'dydx': 
                adapted = format_symbol(pair, format_type='slash') + ':USDC'
            else:
                adapted = format_symbol(pair, format_type='slash')
        else:
            adapted = format_symbol(pair, format_type='slash')

        # 3. Final validation against markets
        if self.exchange and self.exchange.markets:
            if adapted in self.exchange.markets:
                return adapted
            
            # If not found, try to find a close match or warn the user
            display_message('warning', get_message("exchange.symbol_not_found", pair=pair, adapted=adapted, exchange=self.exchange_name))
            display_message('info', get_message("exchange.check_markets_tip", exchange=self.exchange_name))
            
        return adapted

    def _check_reliability(self):
        rate, count = get_health_status()
        if count < 5: return
        if rate >= 15.0: display_message('error', get_message("exchange.reliability_critical", rate=rate), icon="☢️")
        elif rate >= 5.0: display_message('warning', get_message("exchange.reliability_danger", rate=rate), icon="⚠️")

    def _request_with_retry(self, func, *args, **kwargs):
        max_retries, delay = 3, 1
        for i in range(max_retries):
            try:
                res = func(*args, **kwargs)
                record_operation(True)
                self._check_reliability()
                return res
            except (ccxt.NetworkError, ccxt.ExchangeError) as e:
                err_msg = get_message("exchange.request_attempt", current=i+1, max=max_retries)
                display_message('action_start', err_msg)
                if i == max_retries - 1:
                    record_operation(False)
                    self._check_reliability()
                    display_message('action_stop', err_msg, result_icon="❌")
                    raise e
                time.sleep(delay)
                display_message('action_stop', err_msg, result_icon="⏳")
                delay *= 2
            except Exception as e:
                err_str = str(e)
                if "429" in err_str:
                    msg = get_message("exchange.rate_limit_hit", current=i+1, max=max_retries)
                    display_message('action_start', msg)
                    time.sleep(delay * 3)
                    display_message('action_stop', msg, result_icon="🛑")
                    delay *= 2
                    continue
                record_operation(False)
                raise e
