import sys
import os

# Add the parent directory to the Python path to allow imports from library
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from bitmango_free.exchange.binance.account_portfolio_binance import get_account_summary
import config

# Ensure you have BINANCE_TESTNET_API_KEY and BINANCE_TESTNET_SECRET_KEY in your config.py
# For testing, you might temporarily hardcode them here or use environment variables

# Replace with your actual testnet API keys from config.py or environment variables
api_key = config.BINANCE_TESTNET_API_KEY
api_secret = config.BINANCE_TESTNET_SECRET_KEY

def main():
    print("Attempting to fetch Binance Testnet account summary...")
    try:
        account_summary = get_account_summary(api_key, api_secret, is_testnet=True)
        print("Successfully fetched account summary from Binance Testnet:")
        print("Spot Balances:", account_summary['spot']['total'])
        print("Margin Balances:", account_summary['margin']['total'])
        print("Positions:", account_summary['positions'])
    except Exception as e:
        print(f"Error fetching account summary from Binance Testnet: {e}")

if __name__ == "__main__":
    main()
