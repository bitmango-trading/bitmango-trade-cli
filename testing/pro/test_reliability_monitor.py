#!/usr/bin/env -S uv run python
import subprocess
import requests
import time
import sys
import os
import json

# Ensure project root is in path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from testing.test_helper import skip_if_free, get_bitmango_executable

SIMULATOR_URL = "http://127.0.0.1:8080"

def set_chaos(config):
    requests.post(f"{SIMULATOR_URL}/chaos", json=config)

def run_bm(cmd_list):
    full_cmd = get_bitmango_executable() + cmd_list + ["--exchange", "simulated", "--no-confirm"]
    result = subprocess.run(full_cmd, capture_output=True, text=True)
    return result

def main():
    skip_if_free()
    print("🚀 Verifying Reliability Health Monitor")
    
    # Reset health file
    if os.path.exists("exchange_health.json"):
        os.remove("exchange_health.json")
        
    # 1. Establish baseline (Successes)
    set_chaos({"error_rate": 0.0, "dropout_rate": 0.0, "latency_min": 0, "latency_max": 0})
    print("Priming baseline successes...")
    for _ in range(5):
        run_bm(["account", "--balance"])
        
    # 2. Induce "Danger Zone" (Approach 10-20% failure)
    # We want ~10% failure. 
    print("Inducing Danger Zone (High Errors)...")
    set_chaos({"error_rate": 1.0, "dropout_rate": 0.0}) # 100% error
    
    for i in range(5):
        print(f"Failed Op {i+1}...")
        run_bm(["entry", "--pair", "btc-usdt", "--direction", "buy", "--size", "0.001", "--order-type", "market"])

    # 3. Check for Warning in next command
    print("Checking for Reliability Warning...")
    # Lower error so the command itself might succeed but show the warning from history
    set_chaos({"error_rate": 0.0}) 
    run_bm(["account", "--balance"]) # This one populates the failure history
    res = run_bm(["account", "--balance"]) # This one should show the warning
    
    if "DANGER: Exchange Reliability dropping" in res.stderr or "DANGER: Exchange Reliability dropping" in res.stdout:
        print("✅ SUCCESS: Found 'DANGER' warning in output.")
    elif "CRITICAL: Exchange Reliability" in res.stderr or "CRITICAL: Exchange Reliability" in res.stdout:
        print("✅ SUCCESS: Found 'CRITICAL' warning in output.")
    else:
        print("❌ FAIL: Warning not found in output.")
        print("STDOUT:", res.stdout)
        print("STDERR:", res.stderr)
        print("\nFix this issue in a code branch, test, merge. repeat until 100% pass rate")
        sys.exit(1)

    # Clean up
    if os.path.exists("exchange_health.json"):
        os.remove("exchange_health.json")

if __name__ == "__main__":
    main()
