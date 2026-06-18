import sys
import os
import ccxt

# Add the parent directory to the Python path to allow imports from library
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import config

# This is a simplified test script. In a real scenario, you'd pass args from bitmango_free.
# For direct testing, you can simulate args.
class MockArgs:
    def __init__(self, sandbox=False):
        self.sandbox = sandbox

def main():
    # Simulate args for mainnet and testnet
    args_mainnet = MockArgs(sandbox=False)
    args_testnet = MockArgs(sandbox=True)

    print("\n--- Testing dYdX Mainnet ---")
    try:
        # Instantiate DydxFuturesOrder (even if we only fetch balance for now)
        # This will use BaseExchange to initialize the ccxt object
        from bitmango_free.exchange.dydx.order_futures_dydx import DydxFuturesOrder
        dydx_mainnet_instance = DydxFuturesOrder(args_mainnet)
        
        print("Attempting to fetch dYdX Mainnet account summary...")
        balances_mainnet = dydx_mainnet_instance.exchange.fetch_balance()
        print("Successfully fetched account summary from dYdX Mainnet:")
        print("Total Balances:", balances_mainnet['total'])
        print("Free Balances:", balances_mainnet['free'])
        print("Used Balances:", balances_mainnet['used'])

    except Exception as e:
        print(f"Error fetching account summary from dYdX Mainnet: {e}")

    print("\n--- Testing dYdX Testnet ---")
    try:
        dydx_testnet_instance = DydxFuturesOrder(args_testnet)

        print("Attempting to fetch dYdX Testnet account summary...")
        balances_testnet = dydx_testnet_instance.exchange.fetch_balance()
        print("Successfully fetched account summary from dYdX Testnet:")
        print("Total Balances:", balances_testnet['total'])
        print("Free Balances:", balances_testnet['free'])
        print("Used Balances:", balances_testnet['used'])

    except Exception as e:
        print(f"Error fetching account summary from dYdX Testnet: {e}")

if __name__ == "__main__":
    main()
