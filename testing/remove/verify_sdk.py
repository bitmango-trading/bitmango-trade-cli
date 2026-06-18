import os
import sys
import time
import subprocess

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bitmango import BitMango

def main():
    # 1. Start Simulator
    print("🚀 Starting Simulator for SDK verification...")
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sim_proc = subprocess.Popen([os.path.join(project_root, "testing/simulator/run.sh")], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(5)

    try:
        # 2. Initialize SDK
        print("Initializing SDK for 'simulated' exchange...")
        bm = BitMango(exchange='simulated', market_type='spot')

        # 3. Test Ticker
        print("Testing .ticker()...", end=" ", flush=True)
        res = bm.ticker('BTC-USDT')
        if res.get('status') == 'success' and res['data']['last'] > 0:
            print("PASS ✓")
        else:
            print(f"FAILED ({res})")

        # 4. Test Balance
        print("Testing .balance()...", end=" ", flush=True)
        res = bm.balance()
        if res.get('status') == 'success' and 'USDT' in res['data']['total']:
            print("PASS ✓")
        else:
            print(f"FAILED ({res})")

        # 5. Test Buy Order
        print("Testing .buy()...", end=" ", flush=True)
        res = bm.buy('BTC-USDT', 0.1, order_type='market')
        if res.get('status') == 'success' and res['order']['id']:
            print("PASS ✓")
        else:
            print(f"FAILED ({res})")

    finally:
        print("\n🛑 Shutting down simulator...")
        sim_proc.terminate()
        sim_proc.wait()

if __name__ == "__main__":
    main()
