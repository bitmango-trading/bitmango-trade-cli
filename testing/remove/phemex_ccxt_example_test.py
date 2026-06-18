import sys
import os
import ccxt
# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
from api_keys import API_KEYS

# Initialize the Phemex exchange object
phemex = ccxt.phemex({
    'apiKey': API_KEYS['phemex']['api_key'],
    'secret': API_KEYS['phemex']['secret'],
})
phemex.set_sandbox_mode(True)


# Set the symbol and the amount for the order
symbol = 'BTC/USDT'  # Example: Bitcoin/Tether trading pair
amount = 0.001       # The amount of BTC to buy

# --- Create a market buy order ---
try:
    print(f"Attempting to create a market buy order for {amount} {symbol} on Phemex testnet...")
    buy_order = phemex.create_market_buy_order(symbol, amount)
    print("Market buy order created successfully:")
    print(buy_order)
except ccxt.NetworkError as e:
    print(f"Network error: {e}")
except ccxt.ExchangeError as e:
    print(f"Exchange error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
