#!/usr/bin/env -S uv run python
import subprocess
import requests
import time
import sys
import os
import csv
import re
import json

# Add project root to path for bitmango.output
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from bitmango_free.output import display_message

SIMULATOR_URL = "http://127.0.0.1:8000"

def set_chaos(config):
    requests.post(f"{SIMULATOR_URL}/chaos", json=config)

def set_price(price):
    requests.post(f"{SIMULATOR_URL}/ticker/price", params={"symbol": "BTCUSDT", "price": price})

def run_bm(cmd_list, timeout=60):
    full_cmd = ["./bitmango"] + cmd_list + ["--exchange", "simulated", "--market-type", "spot", "--no-confirm", "--debug"]
    display_message('info', f"Running: {' '.join(full_cmd)}")
    try:
        result = subprocess.run([sys.executable] + full_cmd, capture_output=True, text=True, timeout=timeout)
        # We don't print full output here to keep logs clean, but we return it
        return result
    except subprocess.TimeoutExpired:
        display_message('error', f"Command timed out: {' '.join(full_cmd)}")
        return None

def main():
    display_message('info', "🚀 Starting Unified Pro Chaos Suite (v2)")
    
    # 0. RESET EVERYTHING
    set_chaos({"dropout_rate": 0.0, "error_rate": 0.0, "latency_min": 0.0, "latency_max": 0.0})
    set_price(70000.0)
    run_bm(["kill-switch", "--reset"])
    
    # 1. SMART STOP WITH 50% ERROR RATE
    display_message('info', "\n--- TEST 1: Smart Stop + Network Errors (50%) ---")
    set_chaos({"error_rate": 0.5})
    res = run_bm(["stop", "--pair", "btc-usdt", "--direction", "sell", "--size", "0.1", "--stop-price", "69000"])
    if res and re.search(r"(order placed|order executed)", res.stdout, re.IGNORECASE):
        display_message('success', "Smart Stop placed despite 50% error rate")
    else:
        display_message('error', "Smart Stop placement failed")
        if res: print(res.stdout)

    # 2. KILL SWITCH + HIGH LATENCY
    display_message('info', "\n--- TEST 2: Kill Switch + High Latency (1s-2s) ---")
    set_chaos({"latency_min": 0.0, "latency_max": 0.0}) # No latency for setup
    set_price(70000.0)
    run_bm(["kill-switch", "--reset"])
    run_bm(["kill-switch", "--max-loss", "50.0"])
    
    # Buy 1 BTC so crash affects us
    display_message('info', "Buying 1 BTC for equity valuation...")
    run_bm(["entry", "--pair", "btc-usdt", "--direction", "buy", "--size", "1.0", "--order-type", "market"])
    
    # Manually inject initial balance to config to be 100% sure it's higher than crash
    display_message('info', "Manually setting initial_balance to 100000.0...")
    with open("kill_switch_config.json", 'w') as f:
        json.dump({"max_loss": 50.0, "initial_balance": 100000.0}, f)
    
    set_chaos({"latency_min": 1.0, "latency_max": 2.0})
    display_message('info', "Crashing price to 10000.0 to trigger Kill Switch...")
    set_price(10000.0)
    
    # Check balance - this should trigger the check and subsequent liquidation
    triggered = False
    for i in range(5):
        display_message('info', f"Polling for Kill Switch trigger (Attempt {i+1})...")
        res = run_bm(["account", "--balance"], timeout=60)
        if res and "EMERGENCY TRIGGER" in res.stdout:
            triggered = True
            break
        time.sleep(5)

    if triggered:
        display_message('success', "Kill Switch triggered under high latency")
    else:
        display_message('error', "Kill Switch failed to trigger")
        # Debug: show current config
        with open("kill_switch_config.json", 'r') as f:
            print(f"Config: {f.read()}")

    run_bm(["kill-switch", "--reset"])
    set_chaos({"latency_min": 0.0, "latency_max": 0.0})

    # 3. TRAILING STOP + PRICE VOLATILITY + DROPOUTS
    display_message('info', "\n--- TEST 3: Trailing Stop + Dropouts (20%) ---")
    set_price(70000.0)
    run_bm(["entry", "--pair", "btc-usdt", "--direction", "buy", "--size", "0.1", "--order-type", "market"])
    
    set_chaos({"dropout_rate": 0.2})
    display_message('info', "Starting Trailing Stop background process...")
    ts_proc = subprocess.Popen([sys.executable, "./bitmango", "trailing-stop", "--pair", "btc-usdt", "--direction", "buy", "--size", "0.1", "--callback-percentage", "0.01", "--exchange", "simulated", "--market-type", "spot", "--no-confirm", "--debug"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    time.sleep(5)
    set_price(75000.0)
    time.sleep(15)
    set_price(70000.0)
    
    try:
        stdout, stderr = ts_proc.communicate(timeout=120)
        if re.search(r"TRAILING STOP TRIGGERED", stdout, re.IGNORECASE):
            display_message('success', "Trailing Stop executed correctly despite dropouts")
        else:
            display_message('error', "Trailing Stop failed to trigger")
            print(stdout)
    except subprocess.TimeoutExpired:
        ts_proc.kill()
        display_message('error', "Trailing Stop process timed out")

    # 4. TWAP + INTERMITTENT DROP-OUTS
    display_message('info', "\n--- TEST 4: TWAP + Dropouts (30%) ---")
    set_chaos({"dropout_rate": 0.3})
    res = run_bm(["twap", "--pair", "btc-usdt", "--direction", "buy", "--total-size", "0.3", "--duration", "1", "--chunks", "3"])
    if res and re.search(r"TWAP Order Complete", res.stdout, re.IGNORECASE):
        display_message('success', "TWAP completed all chunks with connection dropouts")
    else:
        display_message('error', "TWAP failed with dropouts")
        if res: print(res.stdout)

    # CLEANUP
    set_chaos({"dropout_rate": 0.0, "error_rate": 0.0})
    display_message('success', "\n🚀 Unified Pro Chaos Suite Complete")

if __name__ == "__main__":
    main()
