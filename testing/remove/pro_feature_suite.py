#!/usr/bin/env -S uv run python
import subprocess
import requests
import time
import sys
import os
import csv

# Add project root to path for bitmango.output
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from bitmango_free.output import display_message

SIMULATOR_URL = "http://127.0.0.1:8000"

def run_bm(cmd_list):
    full_cmd = ["./bitmango"] + cmd_list + ["--exchange", "simulated", "--market-type", "spot", "--no-confirm"]
    display_message('info', f"Running: {' '.join(full_cmd)}")
    result = subprocess.run([sys.executable] + full_cmd, capture_output=True, text=True)
    if result.stdout: print(result.stdout.strip())
    if result.stderr: print(result.stderr.strip())
    return result

def main():
    display_message('info', "Starting Pro Features Unified Suite")
    
    # Reset Simulator State
    try:
        requests.post(f"{SIMULATOR_URL}/chaos", json={"dropout_rate": 0.0, "rate_limit_rate": 0.0})
    except:
        display_message('error', "Simulator not reachable")
        sys.exit(1)
    
    # 1. TEST ICEBERG ORDER
    display_message('info', "--- TEST 1: Iceberg Order ---")
    res = run_bm(["iceberg", "--pair", "btc-usdt", "--direction", "buy", "--total-size", "1.0", "--visible-size", "0.2"])
    if "Iceberg order complete" in res.stdout:
        display_message('success', "Iceberg Portions Executed")
    else:
        display_message('error', "Iceberg order failed")

    # 2. TEST TWAP ORDER
    display_message('info', "--- TEST 2: TWAP Order ---")
    res = run_bm(["twap", "--pair", "btc-usdt", "--direction", "buy", "--total-size", "0.5", "--duration", "1", "--chunks", "2"])
    if "TWAP order complete" in res.stdout:
        display_message('success', "TWAP Chunks Executed")
    else:
        display_message('error', "TWAP order failed")

    # 3. TEST ACCOUNTING REPORT
    display_message('info', "--- TEST 3: Accounting & CSV ---")
    filename = "test_pro_report.csv"
    if os.path.exists(filename): os.remove(filename)
    
    res = run_bm(["report", "--export", "csv", "--filename", filename])
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            display_message('success', f"CSV generated with {len(rows)-1} trade entries")
    else:
        display_message('error', "CSV was not generated")

    # 4. TEST KILL SWITCH
    display_message('info', "--- TEST 4: Kill Switch (Loss Protection) ---")
    run_bm(["kill-switch", "--reset"])
    run_bm(["kill-switch", "--max-loss", "5.0"])
    
    display_message('info', "Crashing market price to trigger Kill Switch")
    requests.post(f"{SIMULATOR_URL}/ticker/price", params={"symbol": "BTCUSDT", "price": 60000.0})
    
    res = run_bm(["account", "--balance"])
    
    if "EMERGENCY TRIGGER" in res.stdout and "TRADING PERMANENTLY SUSPENDED" in res.stdout:
        display_message('success', "Kill Switch triggered emergency liquidation")
    else:
        display_message('error', "Kill Switch did not trigger on loss")

    # 5. TEST LOCK PERSISTENCE
    display_message('info', "--- TEST 5: Lock Persistence ---")
    res = run_bm(["entry", "--pair", "btc-usdt", "--direction", "buy", "--size", "0.1", "--order-type", "market"])
    if "Action denied: Trading is suspended" in res.stdout:
        display_message('success', "Entry prevented while locked")
    else:
        display_message('error', "entry command allowed despite lock!")

    # Cleanup
    run_bm(["kill-switch", "--reset"])
    if os.path.exists(filename): os.remove(filename)
    display_message('success', "Pro Features Suite Complete")

if __name__ == "__main__":
    main()
