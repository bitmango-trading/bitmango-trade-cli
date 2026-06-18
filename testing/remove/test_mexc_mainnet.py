import sys
import os
import ccxt

# Add the parent directory to the Python path to allow imports from library
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import config

# Ensure you have MEXC_API_KEY and MEXC_SECRET_KEY in your config.py
# For testing, you might temporarily hardcode them here or use environment variables

# Replace with your actual MEXC API keys from config.py or environment variables
api_key = config.MEXC_API_KEY
api_secret = config.MEXC_SECRET_KEY

def main():
    print("Attempting to fetch MEXC Mainnet account summary...")
    try:
        exchange = ccxt.mexc({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
        })

        # Fetch account balances
        balances = exchange.fetch_balance()
        print("Successfully fetched account summary from MEXC Mainnet:")
        print("Total Balances:", balances['total'])
        print("Free Balances:", balances['free'])
        print("Used Balances:", balances['used'])

    except Exception as e:
        print(f"Error fetching account summary from MEXC Mainnet: {e}")

if __name__ == "__main__":
    main()
