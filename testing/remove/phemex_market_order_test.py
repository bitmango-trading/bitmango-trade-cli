import sys
import os
import time
import argparse
from types import SimpleNamespace

# Add the project root to sys.path to enable importing library modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__name__), '..')))

from bitmango_free.exchange.phemex.order_spot_phemex import PhemexSpotOrder

def run_spot_market_buy_test(exchange_name, environment):
    print(f"\n=== Running Phemex Spot Market Buy Test ({environment.capitalize()}) ===")

    # Initialize PhemexSpotOrder
    args = SimpleNamespace(exchange=exchange_name, sandbox=(environment=='sandbox'))
    phemex_order = PhemexSpotOrder(args)

    pair = "BTC/USDT" # Use CCXT format for symbol
    size = 0.0001 # Small size for testing

    # 1. Place a market buy order (will use FOK internally)
    print("\nStep 1: Placing a market buy order (FOK)... ")
    entry_args = SimpleNamespace(
        pair=pair,
        direction='buy',
        size=size,
        order_type='market',
        market_type='spot'
    )
    
    # Capture stdout to check for success message and order details
    original_stdout = sys.stdout
    sys.stdout = open('temp_stdout.txt', 'w')
    
    order_id = None
    try:
        phemex_order.entry(entry_args)
        sys.stdout.close()
        sys.stdout = original_stdout # Restore stdout
        
        with open('temp_stdout.txt', 'r') as f:
            output = f.read()
        
        if "✅ Aggressive Limit Order (simulating market) executed:" not in output and \
           "✅ Order executed:" not in output:
            print("❌ Order placement failed. Check output for details.")
            print(output)
            return False
        
        # Extract order_id (this is a brittle way, ideally the method would return it)
        for line in output.splitlines():
            if "'id':" in line:
                try:
                    order_id = line.split("'id': '")[1].split("'")[0]
                    break
                except IndexError:
                    pass
        
        if not order_id:
            print("❌ Could not extract order ID from output.")
            print(output)
            return False
        
        print(f"Order placed successfully. Order ID: {order_id}")

        # 2. Verify order status
        print("\nStep 2: Verifying order status...")
        max_retries = 10
        retry_delay = 3 # seconds
        order_status = 'unknown'

        for i in range(max_retries):
            order_status = phemex_order.get_order_status(order_id, pair)
            print(f"Attempt {i+1}/{max_retries}: Order status: {order_status}")
            if order_status in ['closed', 'filled', 'partially_filled', 'canceled']:
                break
            time.sleep(retry_delay)
        
        if order_status == 'closed' or order_status == 'filled' or order_status == 'partially_filled':
            print(f"✅ Order status verified: {order_status}")
            return True
        else:
            print(f"❌ Order did not reach expected status. Final status: {order_status}")
            return False

    except Exception as e:
        sys.stdout.close()
        sys.stdout = original_stdout # Restore stdout
        with open('temp_stdout.txt', 'r') as f:
            captured_output = f.read()
        print(f"An error occurred during the test: {e}")
        print("Captured output:")
        print(captured_output)
        return False
    finally:
        if 'temp_stdout.txt' in locals() and not sys.stdout.closed:
            sys.stdout.close()
        sys.stdout = original_stdout # Ensure stdout is restored
        if os.path.exists('temp_stdout.txt'):
            os.remove('temp_stdout.txt')

def main():
    parser = argparse.ArgumentParser(description="Run Phemex market order tests.")
    parser.add_argument("--exchange", required=True, help="The exchange to test (e.g., phemex).")
    parser.add_argument("--environment", choices=["live", "sandbox"], default="sandbox", help="The environment to test (live or sandbox).")
    
    args = parser.parse_args()

    if run_spot_market_buy_test(args.exchange.lower(), args.environment.lower()):
        print("\n=== Phemex Spot Market Buy Test PASSED ===")
        sys.exit(0)
    else:
        print("\n=== Phemex Spot Market Buy Test FAILED ===")
        sys.exit(1)

if __name__ == "__main__":
    main()