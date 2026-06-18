#!/usr/bin/env -S uv run python
import subprocess
import os
import sys
import time
from bitmango_free.output import display_message

def run_bm(cmd_list):
    full_cmd = ["uv", "run", "./bitmango"] + cmd_list + ["--exchange", "phemex", "--sandbox", "--no-confirm", "--no-color"]
    return subprocess.run(full_cmd, capture_output=True, text=True)

def main():
    display_message('info', "🚀 Starting Automated Phemex Sandbox Suite")
    
    # 0. CLEANUP
    display_message('info', "Cleaning up Phemex Sandbox state...")
    subprocess.run([sys.executable, "testing/phemex_account_config.py"])
    
    # 1. ACCOUNT BALANCE
    display_message('info', "--- TEST 1: Account Balance ---")
    res = run_bm(["account", "--balance", "--market-type", "futures"])
    if res and res.returncode == 0:
        display_message('success', "Balance fetched successfully")
    else:
        display_message('error', "Failed to fetch balance")

    # 2. MARKET ORDER + POSITION CHECK
    display_message('info', "--- TEST 2: Market Order + Positions ---")
    # Phemex uses BTC-USDT for futures
    res = run_bm(["entry", "--pair", "btc-usdt", "--direction", "buy", "--size", "0.0001", "--order-type", "market", "--market-type", "futures"])
    if res and res.returncode == 0:
        display_message('success', "Market Buy Order executed")
    else:
        display_message('error', "Market Buy Order failed")

    time.sleep(2)
    res = run_bm(["account", "--positions", "--market-type", "futures"])
    if res and "BTCUSDT" in res.stdout:
        display_message('success', "Position found in account")
    else:
        display_message('error', "Position not found")

    # 3. LIMIT ORDER + CANCELLATION
    display_message('info', "--- TEST 3: Limit Order + Cancellation ---")
    # Get current price to place a far-away limit order
    # For now we'll just use a very low price
    res = run_bm(["entry", "--pair", "btc-usdt", "--direction", "buy", "--size", "0.001", "--order-type", "limit", "--price", "20000", "--market-type", "futures"])
    if res and "order executed" in res.stdout.lower():
        display_message('success', "Limit Buy Order placed")
    else:
        display_message('error', "Limit Buy Order failed")

    res = run_bm(["cancel", "all", "--pair", "btc-usdt", "--market-type", "futures"])
    if res and "order cancelled" in res.stdout.lower():
        display_message('success', "Limit Order cancelled")
    else:
        display_message('error', "Cancellation failed")

    # 4. STOP ORDER
    display_message('info', "--- TEST 4: Stop Order ---")
    res = run_bm(["stop", "--pair", "btc-usdt", "--direction", "buy", "--size", "0.001", "--stop-price", "80000", "--market-type", "futures"])
    if res and "order executed" in res.stdout.lower():
        display_message('success', "Stop Order placed")
    else:
        display_message('error', "Stop Order failed")

    # Final Cleanup
    display_message('info', "Final Cleanup...")
    subprocess.run([sys.executable, "testing/phemex_account_config.py"])
    
    display_message('success', "🚀 Phemex Sandbox Suite Complete")

if __name__ == "__main__":
    main()
