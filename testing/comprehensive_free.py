#!/usr/bin/env -S uv run python
import subprocess
import os
import sys
import argparse
import json
import atexit

# Ensure project root is in path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from testing.test_helper import get_bitmango_executable

def main():
    parser = argparse.ArgumentParser(description="Comprehensive Test Suite for bitmango")
    parser.add_argument('--exchange', required=True, help='Exchange to test')
    parser.add_argument('--sandbox', action='store_true', help='Use sandbox mode')
    parser.add_argument('--pair', default='btc-usdt', help='Pair to use for testing')
    parser.add_argument('--force-live', action='store_true', help='Force live execution (CAUTION)')
    args = parser.parse_args()

    common_opts = ["--exchange", args.exchange, "--no-color"]
    if args.sandbox:
        common_opts.append("--sandbox")
    
    # Force market-type spot for generic tests unless it's a futures-only exchange
    mtype = "spot"
    common_opts.extend(["--market-type", mtype])

    all_passed = True

    def run_cmd(cmd, critical=True):
        nonlocal all_passed
        print(f"\n[TEST] Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(f"Exit Code: {result.returncode}")
        
        # Special case: ohlcv can fail with PRO license error, we allow this for baseline test
        is_license_err = "exclusive to BitMango Professional" in result.stdout or "exclusive to BitMango Professional" in result.stderr
        
        if result.returncode != 0 and not is_license_err and critical:
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            print("\nFix this issue in a code branch, test, merge. repeat until 100% pass rate")
            sys.exit(1)
        else:
            if is_license_err:
                print("  (Skipping Pro feature validation in baseline)")
            # Show snippet of output on success
            lines = result.stdout.strip().split('\n')
            for line in lines[-5:]: # Show last 5 lines
                print(f"  {line}")
        return result

    def run_test(cmd_list, is_safe=True, extra_opts=None, critical=True):
        full_cmd = get_bitmango_executable() + [cmd_list[0]] + cmd_list[1:] + common_opts
        if extra_opts:
            # If extra_opts has --market-type, it overrides the default spot in common_opts
            if "--market-type" in extra_opts:
                # Remove the default market-type from full_cmd if present
                full_cmd = [arg for i, arg in enumerate(full_cmd) if not (full_cmd[i-1] == "--market-type" or arg == "--market-type")]
            full_cmd += extra_opts
        
        if not is_safe and not args.sandbox and not args.force_live:
            print(f"⏩ SKIPPING (LIVE PROTECTION): {' '.join(full_cmd)}")
            return None
            
        return run_cmd(full_cmd, critical=critical)

    def cleanup():
        print("\n🔄 Exiting all active positions, resetting test account...")
        # We run these as non-critical so if they fail (e.g. no orders) we don't crash
        run_test(["cancel", "all", "--pair", args.pair, "--no-confirm"], is_safe=False, critical=False)
        run_test(["close-all", "--no-confirm"], is_safe=False, critical=False)
        # Repeat for futures just in case
        run_test(["cancel", "all", "--pair", args.pair, "--no-confirm"], is_safe=False, critical=False, extra_opts=["--market-type", "futures"])
        run_test(["close-all", "--no-confirm"], is_safe=False, critical=False, extra_opts=["--market-type", "futures"])

    # Register cleanup for exit
    atexit.register(cleanup)

    # Pre-test cleanup
    cleanup()

    print(f"=== Starting Comprehensive Test Suite on {args.exchange.upper()} ===")

    # 1. Informational Commands
    print("\n--- 1. Informational Commands ---")
    run_test(["markets"])
    run_test(["ticker", "--pair", args.pair])
    run_test(["ohlcv", "--pair", args.pair, "--limit", "5"])
    run_test(["funding", "--pair", args.pair])
    run_test(["history", "--pair", args.pair])
    run_test(["ledger", "--currency", "usdt"])
    run_test(["query_order_book", "--pair", args.pair])

    # 2. Account Management
    print("\n--- 2. Account Management ---")
    run_test(["account", "--balance"])
    run_test(["account", "--positions"])
    run_test(["transfer", "--currency", "usdt", "--amount", "1", "--from-account", "spot", "--to-account", "futures"], is_safe=False)
    
    # 3. Trading Commands (Requires careful handling)
    print("\n--- 3. Trading Operations ---")
    
    # Fetch current price to avoid deviation breaches
    ticker_res = run_test(["ticker", "--pair", args.pair, "-o", "json"])
    current_price = 70000.0
    if ticker_res and ticker_res.returncode == 0:
        try:
            ticker_data = json.loads(ticker_res.stdout)
            # Ticker data is nested under 'data' key in JSON mode
            current_price = float(ticker_data.get('data', {}).get('last', ticker_data.get('last', 70000.0)))
            print(f"  [DEBUG] Parsed Price: {current_price}")
        except Exception as e:
            print(f"  [DEBUG] Price parse failed: {e}")
            pass
    
    limit_price = str(current_price * 0.98) # 2% below market for a safe buy limit
    
    # Limit Order
    run_test(["entry", "--pair", args.pair, "--direction", "buy", "--size", "0.001", "--order-type", "limit", "--price", limit_price, "--no-confirm"], is_safe=False)
    run_test(["open_orders", "--pair", args.pair])
    
    # Cancel All
    run_test(["cancel", "all", "--pair", args.pair, "--no-confirm"], is_safe=False)
    
    # Market Order
    run_test(["entry", "--pair", args.pair, "--direction", "buy", "--size", "0.0001", "--order-type", "market", "--no-confirm"], is_safe=False)
    
    # Stop Order
    run_test(["stop", "--pair", args.pair, "--direction", "sell", "--size", "0.0001", "--order-type", "stop_loss", "--current-price", str(current_price), "--stop-loss-percentage", "0.01", "--no-confirm"], is_safe=False)

    # 4. Position Closure
    print("\n--- 4. Position Closure ---")
    run_test(["close", "--pair", args.pair, "--no-confirm"], is_safe=False)
    run_test(["close-all", "--no-confirm"], is_safe=False)

    print(f"\n=== Comprehensive FREE Suite Completed ({'SUCCESS' if all_passed else 'FAILED'}) ===")
    if not all_passed:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
