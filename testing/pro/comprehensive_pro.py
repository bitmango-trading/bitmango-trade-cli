#!/usr/bin/env -S uv run python
import subprocess
import os
import sys
import argparse
import json
import atexit

# Ensure project root is in path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from testing.test_helper import skip_if_free, get_bitmango_executable

def main():
    skip_if_free()
    parser = argparse.ArgumentParser(description="Comprehensive PRO Test Suite for bitmango")
    parser.add_argument('--exchange', required=True, help='Exchange to test')
    parser.add_argument('--sandbox', action='store_true', help='Use sandbox mode')
    parser.add_argument('--pair', default='btc-usdt', help='Pair to use for testing')
    parser.add_argument('--force-live', action='store_true', help='Force live execution (CAUTION)')
    args = parser.parse_args()

    common_opts = ["--exchange", args.exchange, "--no-color"]
    if args.sandbox:
        common_opts.append("--sandbox")
    
    # Pro features often involve futures
    mtype = "futures"
    common_opts.extend(["--market-type", mtype])

    all_passed = True

    def run_cmd(cmd, critical=True):
        nonlocal all_passed
        print(f"\n[PRO-TEST] Running: {' '.join(cmd)}")
        env = os.environ.copy()
        env["BITMANGO_MAX_ORDER_USD"] = "10000"
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        print(f"Exit Code: {result.returncode}")
        
        if result.returncode != 0 and critical:
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            sys.exit(1)
        else:
            lines = result.stdout.strip().split('\n')
            for line in lines[-5:]:
                print(f"  {line}")
        return result

    def run_test(cmd_list, is_safe=True, extra_opts=None, critical=True):
        full_cmd = get_bitmango_executable() + [cmd_list[0]] + cmd_list[1:] + common_opts
        if extra_opts:
            full_cmd += extra_opts
        
        if not is_safe and not args.sandbox and not args.force_live:
            print(f"⏩ SKIPPING (LIVE PROTECTION): {' '.join(full_cmd)}")
            return None
            
        return run_cmd(full_cmd, critical=critical)

    def cleanup():
        print("\n🔄 Exiting all active positions, resetting test account...")
        run_test(["cancel", "all", "--pair", args.pair, "--no-confirm"], is_safe=False, critical=False)
        run_test(["close-all", "--no-confirm"], is_safe=False, critical=False)
        # Also clean spot just in case
        run_test(["cancel", "all", "--pair", args.pair, "--no-confirm"], is_safe=False, critical=False, extra_opts=["--market-type", "spot"])
        run_test(["close-all", "--no-confirm"], is_safe=False, critical=False, extra_opts=["--market-type", "spot"])

    atexit.register(cleanup)
    cleanup()

    print(f"=== Starting Comprehensive PRO Test Suite on {args.exchange.upper()} ===")

    # 1. Advanced Futures Configuration
    print("\n--- 1. Advanced Futures Configuration ---")
    run_test(["leverage", "--leverage", "10", "--pair", args.pair], is_safe=False)
    run_test(["margin", "--mode", "isolated", "--pair", args.pair], is_safe=False)
    run_test(["position-mode", "--mode", "oneway", "--pair", args.pair], is_safe=False)

    # 2. Risk & Analytics
    print("\n--- 2. Risk & Analytics ---")
    run_test(["position-risk"])
    
    # 3. Execution Algorithms (PRO)
    print("\n--- 3. Execution Algorithms (PRO) ---")
    run_test(["iceberg", "--pair", args.pair, "--direction", "buy", "--total-size", "0.01", "--visible-size", "0.005", "--no-confirm"], is_safe=False)
    run_test(["twap", "--pair", args.pair, "--direction", "buy", "--total-size", "0.01", "--duration", "2", "--chunks", "2", "--no-confirm"], is_safe=False)

    # 4. Smart Order Routing (Logic check)
    print("\n--- 4. Order History & Audit (PRO Integration) ---")
    run_test(["trades", "--pair", args.pair])

    print(f"\n=== Comprehensive PRO Suite Completed ({'SUCCESS' if all_passed else 'FAILED'}) ===")
    if not all_passed:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
