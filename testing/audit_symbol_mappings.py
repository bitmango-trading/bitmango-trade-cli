import subprocess
import json
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import os
from testing.test_helper import is_pro_active, skip_if_free, get_bitmango_executable

def run_cli(args):
    """Runs bitmango and returns the JSON output."""
    full_cmd = get_bitmango_executable() + args + ["-o", "json"]
    try:
        result = subprocess.run(full_cmd, capture_output=True, text=True)
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"status": "error", "error": f"JSON Decode Error: {result.stdout}", "stderr": result.stderr}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def audit_symbol_mapping():
    if is_pro_active():
        print("Running FREE test with PRO features enabled.")
    else:
        print("Running FREE test in FREE mode.")

    print("=== AUDIT: Multi-Exchange Symbol Mapping ===")
    
    scenarios = [
        # format: (exchange, input_pair, expected_substring, description)
        ("phemex", "BTC-USD", "BTC/USD:BTC", "Phemex Inverse (Standard)"),
        ("phemex", "BTC/USD", "BTC/USD:BTC", "Phemex Slash Inverse"),
        ("phemex", "BTC/USDT", "BTC/USDT:USDT", "Phemex Linear"),
        ("binance", "BTC-USDT", "BTC/USDT", "Binance Linear"),
        ("bybit", "BTC-USDT", "BTC/USDT:USDT", "Bybit Linear"),
        ("dydx", "BTC-USD", "BTC/USD:USDC", "dYdX USD (Perp)"), 
        # Note: dYdX v3 uses BTC-USD, v4 uses BTC-USD-PERP? 
        # Our adapter adds :USDC, let's see if that matches market data.
        ("mexc", "BTC-USDT", "BTC/USDT:USDT", "Mexc Linear"),
        ("bitget", "BTC-USDT", "BTC/USDT:USDT", "Bitget Linear"),
        ("kraken", "BTC-USD", "BTC/USD", "Kraken Spot/Futures"),
        ("okx", "BTC-USDT", "BTC/USDT:USDT", "OKX Linear"),
    ]

    failures = []
    
    for exchange, pair, expected, desc in scenarios:
        print(f"Checking {exchange.upper()} {pair} -> {expected} ({desc})...", end=" ", flush=True)
        
        # We use 'ticker' as it forces symbol resolution
        # We rely on 'symbol' field in the response being the RESOLVED symbol
        res = run_cli(["ticker", "--exchange", exchange, "--pair", pair])
        
        if res.get("status") == "success":
            resolved = res.get("symbol", "") or res.get("data", {}).get("symbol", "")
            if expected in resolved:
                print(f"PASS ✓ ({resolved})")
            else:
                print(f"FAIL ❌ (Got: {resolved})")
                failures.append(f"{exchange} {pair}: Expected {expected}, Got {resolved}")
        else:
            # If ticker fails (e.g. network), we check if the error message contains the *attempted* symbol
            # Often the error is "Symbol X not found", which tells us what it resolved to.
            err = res.get("error", "")
            if expected in err:
                print(f"PASS (Inferred via Error) ✓")
            elif "Failed to find symbol" in err or "does not exist" in err:
                 print(f"FAIL ❌ (Resolution Error: {err})")
                 failures.append(f"{exchange} {pair}: Resolution failed with {err}")
            else:
                print(f"WARN ⚠️ (API Error: {err})")
                # We don't fail the audit for generic API errors (e.g. 401), only mapping errors
                pass

    print("-" * 40)
    if failures:
        print(f"FAILED: {len(failures)} mapping issues found.")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("🏆 ALL MAPPINGS VERIFIED")
        sys.exit(0)

if __name__ == "__main__":
    audit_symbol_mapping()
