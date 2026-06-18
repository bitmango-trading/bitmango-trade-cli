#!/usr/bin/env -S uv run python
import requests
import time
import os
import sys
import subprocess

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from testing.test_helper import get_bitmango_executable

SIMULATOR_URL = "http://127.0.0.1:8000"

def main():
    print("🚀 Testing Simulator Proxy Mode")
    
    # 1. Enable Proxy for Binance
    print("\n[STEP 1] Enabling Binance Proxy...")
    res = requests.post(f"{SIMULATOR_URL}/chaos", json={"proxy": {"enabled": True, "exchange_id": "binance"}})
    res.raise_for_status()
    print("Proxy enabled ✓")

    # 2. Fetch live price for BTC/USDT
    print("\n[STEP 2] Fetching live price via proxy...")
    res = requests.get(f"{SIMULATOR_URL}/api/v3/ticker/price", params={"symbol": "BTCUSDT"})
    res.raise_for_status()
    data = res.json()
    price = data['price']
    print(f"Live BTC Price: {price} ✓")

    # 3. Fetch live price for ETH/USDT
    print("\n[STEP 3] Fetching live price for ETH...")
    res = requests.get(f"{SIMULATOR_URL}/api/v3/ticker/price", params={"symbol": "ETHUSDT"})
    res.raise_for_status()
    data = res.json()
    print(f"Live ETH Price: {data['price']} ✓")

    # 4. Place an order using live price
    print("\n[STEP 4] Placing order using live price context...")
    full_cmd = get_bitmango_executable() + ["entry", "--pair", "btc-usdt", "--direction", "buy", "--size", "0.01", "--order-type", "market", "--exchange", "simulated", "--market-type", "spot", "--no-confirm"]
    result = subprocess.run(full_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"FAILED (Code {result.returncode})")
        print(result.stdout)
        print(result.stderr)
        print("\nFix this issue in a code branch, test, merge. repeat until 100% pass rate")
        sys.exit(1)
    print(result.stdout)
    
    print("\n🏁 Proxy Mode Test Complete.")

if __name__ == "__main__":
    main()
