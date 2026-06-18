#!/usr/bin/env -S uv run python
import subprocess
import requests
import time
import sys

SIMULATOR_URL = "http://127.0.0.1:8000"

def set_chaos(config):
    print(f"\n[ATTACK] Injecting Chaos: {config}")
    res = requests.post(f"{SIMULATOR_URL}/chaos", json=config)
    res.raise_for_status()

def run_bm(cmd_list, no_confirm=True):
    # Only append --no-confirm if it's a command that supports it
    supports_confirm = ["entry", "exit", "cancel", "stop", "close", "close-all"]
    full_cmd = ["./bitmango"] + cmd_list + ["--exchange", "simulated", "--market-type", "spot"]
    if no_confirm and cmd_list[0] in supports_confirm:
        full_cmd.append("--no-confirm")
        
    print(f"[BM] Running: {' '.join(full_cmd)}")
    start = time.time()
    result = subprocess.run([sys.executable] + full_cmd, capture_output=True, text=True)
    duration = time.time() - start
    print(f"[BM] Exit {result.returncode} in {duration:.2f}s")
    if result.stdout:
        print(f"STDOUT Snip: {result.stdout.strip()[:300].replace(chr(10), ' ')}")
    if result.stderr:
        print(f"STDERR Snip: {result.stderr.strip()[:300].replace(chr(10), ' ')}")
    return result

def check_balance():
    res = requests.get(f"{SIMULATOR_URL}/account")
    return res.json()["balances"]

def main():
    # 1. THE GHOST FILL ATTACK
    print("\n--- ATTACK 1: Ghost Fill (Idempotency Check) ---")
    set_chaos({"ghost_fill_rate": 1.0, "latency_min": 0.1, "latency_max": 0.2})
    
    initial_btc = next(b["free"] for b in check_balance() if b["asset"] == "BTC")
    
    # This will hit a dropout, but the tool should RECONCILE and return success
    run_bm(["entry", "--pair", "btc-usdt", "--direction", "buy", "--size", "0.1", "--order-type", "market"])
    
    final_btc = next(b["free"] for b in check_balance() if b["asset"] == "BTC")
    diff = final_btc - initial_btc
    print(f"BTC Change on server: {diff}")
    
    if abs(diff - 0.1) < 0.0001:
        print("✅ SUCCESS: Idempotency Reconciled Ghost Fill!")
    else:
        print(f"❌ FAIL: Idempotency failed. Diff: {diff}")

    # 2. THE RATE LIMIT SIEGE
    print("\n--- ATTACK 2: Rate Limit Siege ---")
    set_chaos({"rate_limit_rate": 0.5, "latency_min": 0.01, "latency_max": 0.05})
    
    # Tool should retry and eventually succeed
    run_bm(["account", "--balance"])

    # 3. PARTIAL FILL RECONCILE
    print("\n--- ATTACK 3: Partial Fill Reconcile ---")
    set_chaos({"partial_fill_rate": 1.0, "ghost_fill_rate": 1.0})
    
    # Order fills 10-50%, then connection drops. 
    # Tool must detect it partially filled and NOT retry the full amount.
    run_bm(["entry", "--pair", "btc-usdt", "--direction", "buy", "--size", "1.0", "--order-type", "market"])
    
    final_btc_last = next(b["free"] for b in check_balance() if b["asset"] == "BTC")
    print(f"Final BTC Balance after Partial Ghost: {final_btc_last}")

    # Reset
    set_chaos({"ghost_fill_rate": 0.0, "rate_limit_rate": 0.0, "partial_fill_rate": 0.0, "error_rate": 0.0, "dropout_rate": 0.0})

if __name__ == "__main__":
    main()
