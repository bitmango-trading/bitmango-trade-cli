import ccxt
from library.exchange.api_keys import API_KEYS  # Import the API keys storage

def set_sandbox_mode(exchange, sandbox_mode):
    """
    Set sandbox mode on the exchange if supported.
    """
    if hasattr(exchange, 'sandbox') and sandbox_mode is not None:
        if sandbox_mode:
            print("Setting sandbox mode...")
            exchange.sandbox = True
            exchange.verbose = True
        else:
            print("Using live environment...")
            exchange.sandbox = False
            exchange.verbose = False
    else:
        if sandbox_mode:
            raise RuntimeError(f"Error: {exchange.id} does not support sandbox mode.")
        else:
            print(f"Live mode selected for {exchange.id}. No sandbox mode available.")
    print(f"Connecting to {exchange.id.upper()} {'[SANDBOX]' if sandbox_mode else '[LIVE]'}...")

def initialize_exchange(exchange_name, sandbox_mode=False):
    """
    Initialize the exchange and optionally enable sandbox mode.
    """
    if exchange_name not in API_KEYS:
        raise ValueError(f"API keys for {exchange_name} are not available.")
    
    api_key = API_KEYS[exchange_name]["api_key"]
    secret_key = API_KEYS[exchange_name]["secret_key"]

    exchange_class = getattr(ccxt, exchange_name)
    exchange = exchange_class({
        "enableRateLimit": True,
        "apiKey": api_key,
        "secret": secret_key,
    })

    print("CCXT Version:", ccxt.__version__)
    set_sandbox_mode(exchange, sandbox_mode)
    return exchange
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
    else:
        raise ValueError(f"Unsupported symbol format_type: {format_type}")