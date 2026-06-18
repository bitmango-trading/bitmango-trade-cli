import subprocess
import json
import os
import sys
import time
import requests
from pathlib import Path

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from testing.test_helper import is_pro_active, get_bitmango_executable

SIMULATOR_URL = "http://127.0.0.1:8080"

def run_cli(args):
    """Runs the CLI with given args and returns (stdout, stderr, returncode)."""
    env = os.environ.copy()
    env["BITMANGO_MAX_ORDER_USD"] = "10000"
    full_cmd = get_bitmango_executable() + args + ["-o", "json", "--exchange", "simulated", "--no-confirm"]
    result = subprocess.run(full_cmd, capture_output=True, text=True, env=env)
    return result.stdout, result.stderr, result.returncode

def set_sim_price(symbol, price):
    requests.post(f"{SIMULATOR_URL}/ticker/price", params={"symbol": symbol, "price": price})

def set_sim_chaos(config):
    requests.post(f"{SIMULATOR_URL}/chaos", json=config)

def cleanup_lock():
    lock_file = Path.home() / ".config" / "bitmango" / "trading_suspended.lock"
    if lock_file.exists(): lock_file.unlink()

def test_phase_1_order_size():
    print("Testing Phase 1: MAX_ORDER_USD ($10,000)...")
    cleanup_lock()
    set_sim_price("BTCUSDT", 70000.0)
    print("  Scenario: $7,000 Order (PASS)...", end=" ", flush=True)
    stdout, _, code = run_cli(["buy", "--pair", "BTC-USDT", "--size", "0.1", "--order-type", "market"])
    if code == 0: print("✓")
    else: 
        print(f"FAILED (Result: {stdout})")
        sys.exit(1)

def test_phase_2_multi_currency():
    print("\nTesting Phase 2: Multi-Currency Notional Calculation...")
    cleanup_lock()
    set_sim_price("ETHUSDT", 2500.0)
    print("  Scenario: 10 ETH Order ($25,000) (FAIL)...", end=" ", flush=True)
    stdout, _, code = run_cli(["buy", "--pair", "ETH-USDT", "--size", "10", "--order-type", "market"])
    try:
        data = json.loads(stdout.strip())
        if code != 0 and "RISK BREACH" in data.get('error', ''): print("✓")
        else: 
            print(f"FAILED (Code {code}, Result: {data})")
            sys.exit(1)
    except:
        print(f"FAILED (Invalid JSON: {stdout})")
        sys.exit(1)

def test_phase_3_time_chaos():
    print("\nTesting Phase 3: Stale Data & Clock Drift...")
    cleanup_lock()
    stale_ts = int((time.time() - 600) * 1000)
    set_sim_chaos({"stale_timestamp": stale_ts})
    print("  Scenario: Stale Ticker (FAIL)...", end=" ", flush=True)
    stdout, _, code = run_cli(["ticker", "--pair", "BTC-USDT"])
    try:
        data = json.loads(stdout.strip())
        if code != 0 and "stale" in data.get('error', '').lower(): print("✓")
        else: 
            print(f"FAILED (Result: {data})")
            sys.exit(1)
    except:
        print(f"FAILED (Invalid JSON: {stdout})")
        sys.exit(1)
    set_sim_chaos({"stale_timestamp": None})

def test_phase_5_kill_switch_integration():
    print("\nTesting Phase 5: Kill Switch Integration...")
    cleanup_lock()
    print("  Scenario: Triggering Proactive Lock...", end=" ", flush=True)
    stdout, stderr, code = run_cli(["buy", "--pair", "BTC-USDT", "--size", "1.0", "--order-type", "market"])
    if "PROACTIVE LOCK" in stderr or "PROACTIVE LOCK" in stdout: print("✓")
    else: 
        print(f"FAILED (Stdout: {stdout}, Stderr: {stderr})")
        sys.exit(1)
    cleanup_lock()

def main():
    print("=== TEST: Risk Manager (Free Core) ===")
    # Note: Simulator should already be running via run_all_tests.py
    test_phase_1_order_size()
    test_phase_2_multi_currency()
    test_phase_3_time_chaos()
    test_phase_5_kill_switch_integration()
    print("\n🏆 RISK MANAGER VERIFIED")

if __name__ == "__main__":
    main()
