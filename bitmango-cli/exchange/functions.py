import ccxt
import json
import os
import inspect
import re
try:
    from api_keys import API_KEYS
except ImportError:
    API_KEYS = {}
import importlib
from bitmango.config import get_config_path
from bitmango.messages import get_message

HEALTH_STATE_FILE = get_config_path("exchange_health.json")

# Security: Whitelist of supported exchanges to prevent module hijacking
SUPPORTED_EXCHANGES = [
    'binance', 'phemex', 'bybit', 'mexc', 'bitget', 'okx', 
    'hyperliquid', 'bitfinex', 'dydx', 'gateio', 'htx', 
    'kucoin', 'kraken', 'coinbase', 'lbank', 'simulated'
]

def sanitize_exchange_name(name):
    """
    Strictly validates exchange name to prevent path traversal or hijacking.
    Only allows lowercase alphanumeric characters.
    """
    if not name:
        return None
    sanitized = name.lower().strip()
    if not re.match(r'^[a-z0-9]+$', sanitized):
        raise ValueError(get_message("errors.security_invalid_format", name=name))
    if sanitized not in SUPPORTED_EXCHANGES:
        raise ValueError(get_message("errors.security_unauthorized", name=name))
    return sanitized

def _save_atomic(file_path, content, is_json=False):
    """
    Saves content to a file atomically using a temporary file.
    """
    import tempfile
    
    dir_name = os.path.dirname(os.path.abspath(file_path))
    prefix = os.path.basename(file_path) + "."
    
    # Create temp file in the same directory to ensure it's on the same filesystem
    fd, temp_path = tempfile.mkstemp(dir=dir_name, prefix=prefix)
    try:
        with os.fdopen(fd, 'w') as f:
            if is_json:
                json.dump(content, f)
            else:
                f.write(content)
            f.flush()
            os.fsync(f.fileno()) # Ensure it hits disk
        
        # Atomic replacement
        os.replace(temp_path, file_path)
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e

def record_operation(success):
    """
    Records the outcome of an operation in a sliding window.
    """
    try:
        if os.path.exists(HEALTH_STATE_FILE):
            with open(HEALTH_STATE_FILE, 'r') as f:
                state = json.load(f)
        else:
            state = []
        
        state.append(1 if success else 0)
        # Keep last 50 operations
        if len(state) > 50:
            state = state[-50:]
            
        _save_atomic(HEALTH_STATE_FILE, state, is_json=True)
    except Exception as e:
        from bitmango.output import display_message
        display_message('debug', get_message("exchange.failed_record_health", error=e))
        pass

def get_health_status():
    """
    Calculates the current failure rate.
    Returns (failure_rate_pct, count)
    """
    try:
        if not os.path.exists(HEALTH_STATE_FILE):
            return 0.0, 0
            
        with open(HEALTH_STATE_FILE, 'r') as f:
            state = json.load(f)
            
        if not state:
            return 0.0, 0
            
        failures = state.count(0)
        rate = (failures / len(state)) * 100
        return rate, len(state)
    except:
        return 0.0, 0

def format_symbol(symbol, format_type='underscore'):
    """
    Formats the symbol to match the required format for the exchange.
    
    Parameters:
    - symbol (str): The symbol to be formatted, e.g., 'btc-usd'
    - format_type (str): The format to convert to. Can be 'underscore' or 'slash'.
    
    Returns:
    - str: The formatted symbol.
    """
    # Replace '-' with the appropriate separator based on format_type
    if format_type == 'underscore': # BTC_USDT
        return symbol.replace('-', '_').upper()
    elif format_type == 'slash': # BTC/USDT
        return symbol.replace('-', '/').upper()
    elif format_type == 'dash': # BTC-USDT
        return symbol.upper()
    elif format_type == 'slash-colon': # BTC/USDT:USD
        return (symbol.replace('-', '/') + ':USD').upper()
    elif format_type == 'slash-colon-usdt': # BTC/USDT:USDT
        return (symbol.replace('-', '/') + ':USDT').upper()
    elif format_type == 'slash-colon-usd': # BTC/USD:USD
        return (symbol.replace('-', '/') + ':USD').upper()
    else:
        raise ValueError(get_message("errors.unsupported_symbol_format", type=format_type))

def display_balance(exchange_name, args):
    try:
        # Dynamically import the exchange-specific account_open_positions module
        module_path = f"bitmango.exchange.{exchange_name}.account_open_positions"
        module = importlib.import_module(module_path)
        ExchangeClass = getattr(module, f"{exchange_name.capitalize()}AccountPositions")
        
        # Instantiate the exchange-specific class with args
        exchange_instance = ExchangeClass(args)
        
        # Call the balance method
        exchange_instance.balance(args)
    except Exception as e:
        from bitmango.output import display_message
        display_message('error', get_message("exchange.fetch_error", item="balance", exchange=exchange_name, error=e))

def get_exchange_class(exchange_name, command=None):
    """
    Returns the appropriate exchange-specific class.
    """
    # Security: Sanitize and validate exchange name before processing
    try:
        exchange_name = sanitize_exchange_name(exchange_name)
    except ValueError as e:
        from bitmango.output import display_message
        display_message('error', str(e))
        return None

    if not exchange_name:
        return None

    # 1. Try to find a unified exchange class first
    try:
        module_path = f"bitmango.exchange.{exchange_name}.account_open_positions"
        module = importlib.import_module(module_path)
        
        # Try both Capitalized and UPPERCASE class names for robustness
        # e.g. MexcAccountPositions or MEXCAccountPositions
        class_names = [f"{exchange_name.capitalize()}AccountPositions", f"{exchange_name.upper()}AccountPositions"]
        
        ExchangeClass = None
        for class_name in class_names:
            if hasattr(module, class_name):
                ExchangeClass = getattr(module, class_name)
                break
        
        if ExchangeClass and command:
            method_name = command.replace('-', '_')
            if hasattr(ExchangeClass, method_name):
                return ExchangeClass
        elif ExchangeClass:
            return ExchangeClass
    except:
        pass

    # 2. Handle specialized classes for orders if command is provided
    if command in ('entry', 'exit', 'close', 'close-all', 'markets', 'history'):
        try:
            # We assume futures for now as per current project focus, but could check args.market_type
            module_path = f"bitmango.exchange.{exchange_name}.order_futures_{exchange_name}"
            module = importlib.import_module(module_path)
            # Find the class that ends with 'FuturesOrder' or similar
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if name.lower().startswith(exchange_name) and 'order' in name.lower():
                    return obj
        except:
            pass

    # 3. Hardcoded fallback for Phemex (backward compatibility)
    if exchange_name == 'phemex':
        from bitmango.exchange.phemex.account_open_positions import PhemexAccountPositions
        return PhemexAccountPositions
    elif exchange_name == 'simulated':
        from bitmango.exchange.simulated.account_open_positions import SimulatedExchange
        return SimulatedExchange
    
    # 4. Generic dynamic loader for AccountPositions
    try:
        module_path = f"bitmango.exchange.{exchange_name}.account_open_positions"
        module = importlib.import_module(module_path)
        ExchangeClass = getattr(module, f"{exchange_name.capitalize()}AccountPositions")
        return ExchangeClass
    except:
        return None
