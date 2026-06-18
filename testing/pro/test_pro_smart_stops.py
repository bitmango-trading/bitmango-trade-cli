#!/usr/bin/env -S uv run python
import subprocess
import requests
import time
import sys
import os

# Ensure project root is in path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from testing.test_helper import skip_if_free, get_bitmango_executable

SIMULATOR_URL = "http://127.0.0.1:8080"

def set_price(price):
    print(f"\n[SIM] Setting Price to {price}")
    requests.post(f"{SIMULATOR_URL}/ticker/price", params={"symbol": "BTCUSDT", "price": price})

def run_bm(cmd_list):
    full_cmd = get_bitmango_executable() + cmd_list + ["--exchange", "simulated", "--market-type", "spot", "--no-confirm"]
    print(f"[BM] Running: {' '.join(full_cmd)}")
    env = os.environ.copy()
    env["BITMANGO_MAX_ORDER_USD"] = "10000"
    result = subprocess.Popen(full_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
    return result

def main():
    skip_if_free()
    os.environ["BITMANGO_MAX_ORDER_USD"] = "10000"
    print("🚀 Starting Pro Smart Stop Test")
    
    # Wait for simulator
    print("⏳ Waiting for simulator...")
    for i in range(10):
        try:
            requests.get(SIMULATOR_URL, timeout=1)
            print("✅ Simulator ready.")
            break
        except:
            time.sleep(1)
    
    # 1. Start with price at 70000
    set_price(70000.0)
    
    # 2. Start a Buy Position (0.1 BTC)
    subprocess.run(get_bitmango_executable() + ["entry", "--pair", "btc-usdt", "--direction", "buy", "--size", "0.1", "--order-type", "market", "--exchange", "simulated", "--market-type", "spot", "--no-confirm"])
    
    # 3. Start Trailing Stop (1% callback) in background
    # Initial Trigger should be 69300.
    ts_proc = run_bm(["stop", "--pair", "btc-usdt", "--direction", "sell", "--size", "0.1", "--stop-type", "trailing", "--callback-percentage", "0.01"])
    
    time.sleep(5)
    
    # 4. Move Price UP
    # Price 71000. New Trigger 70290.
    set_price(71000.0)
    time.sleep(15) # wait for polling
    
    # 5. Hit Trigger
    set_price(70000.0)
    print("\n[TEST] Price moved to 70000. Trigger is 70290. Waiting for execution...")
    time.sleep(10)
    
    # Wait for the process to finish
    stdout, stderr = ts_proc.communicate(timeout=30)
    print(f"\n--- BM OUTPUT ---")
    print(stdout)
    print(stderr)
    
    if "TRAILING STOP TRIGGERED" in stdout:
        print("\n✅ SUCCESS: Trailing stop triggered!")
    else:
        print("\n❌ FAIL: Trailing stop did not trigger.")
        print("\nFix this issue in a code branch, test, merge. repeat until 100% pass rate")
        sys.exit(1)

if __name__ == "__main__":
    main()
