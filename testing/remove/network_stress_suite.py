#!/usr/bin/env -S uv run python
import subprocess
import requests
import time
import sys

SIMULATOR_URL = "http://127.0.0.1:8000"

def set_chaos(latency_min=0.1, latency_max=0.5, error_rate=0.0, dropout_rate=0.0):
    config = {
        "latency_min": latency_min,
        "latency_max": latency_max,
        "error_rate": error_rate,
        "dropout_rate": dropout_rate
    }
    print(f"\n[STRESS] Setting chaos: {config}")
    res = requests.post(f"{SIMULATOR_URL}/chaos", json=config)
    res.raise_for_status()

def run_command(cmd):
    print(f"[STRESS] Executing: {' '.join(cmd)}")
    start = time.time()
    try:
        # Pass the python executable to run the command correctly
        result = subprocess.run(
            [sys.executable] + cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        duration = time.time() - start
        return result.returncode, result.stdout, result.stderr, duration
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT", 60.0

def test_case(name, config, cmd):
    print(f"\n--- TEST CASE: {name} ---")
    set_chaos(**config)
    ret, out, err, duration = run_command(cmd)
    
    print(f"Result (Exit {ret}) in {duration:.2f}s")
    if out:
        out_snippet = out.strip()[:200].replace('\n', ' ')
        print(f"STDOUT: {out_snippet}...")
    if err:
        err_snippet = err.strip()[:200].replace('\n', ' ')
        print(f"STDERR: {err_snippet}")
    
    return ret, out, err

def main():
    try:
        requests.get(SIMULATOR_URL)
    except:
        print("Error: Simulator is not running on 127.0.0.1:8000")
        sys.exit(1)

    test_case("Baseline", 
              {"error_rate": 0.0, "dropout_rate": 0.0},
              ["./bitmango", "account", "--balance", "--exchange", "simulated", "--market-type", "spot"])

    test_case("High Latency (2s-4s)", 
              {"latency_min": 2.0, "latency_max": 4.0},
              ["./bitmango", "account", "--balance", "--exchange", "simulated", "--market-type", "spot"])

    test_case("Intermittent 5xx Errors (50%)", 
              {"error_rate": 0.5, "latency_min": 0.1, "latency_max": 0.2},
              ["./bitmango", "account", "--balance", "--exchange", "simulated", "--market-type", "spot"])

    test_case("Random Dropouts (30%)", 
              {"dropout_rate": 0.3},
              ["./bitmango", "entry", "--pair", "btc-usdt", "--direction", "buy", "--size", "0.1", "--order-type", "market", "--exchange", "simulated", "--market-type", "spot", "--no-confirm"])

    set_chaos(error_rate=0.0, dropout_rate=0.0)

if __name__ == "__main__":
    main()
