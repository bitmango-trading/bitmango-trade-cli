#!/usr/bin/env -S uv run python
import subprocess
import os
import sys
import time
import requests
import argparse
import signal

# Ensure project root is in path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, BASE_DIR)

from testing.test_helper import is_pro_active, is_pro_enabled, get_bitmango_executable

# Suite Paths
FREE_DIR = "testing"
PRO_DIR = "testing/pro"
SIMULATOR_PATH = os.path.join(BASE_DIR, "testing/simulator/app.py")

def kill_process_on_port(port):
    try:
        if os.name == 'nt':
            # Windows: Find PID using netstat and kill with taskkill
            cmd = f'netstat -ano | findstr :{port} | findstr LISTENING'
            output = subprocess.check_output(cmd, shell=True).decode().strip()
            for line in output.split('\n'):
                if line:
                    pid = line.strip().split()[-1]
                    print(f"Killing PID {pid} on port {port} (Windows)...")
                    subprocess.run(["taskkill", "/F", "/PID", pid], stderr=subprocess.DEVNULL)
        else:
            # Linux/macOS: Use lsof
            cmd = ["lsof", "-t", "-i", f":{port}"]
            pids = subprocess.check_output(cmd).decode().strip().split('\n')
            for pid in pids:
                if pid:
                    print(f"Killing PID {pid} on port {port}...")
                    os.kill(int(pid), signal.SIGKILL)
    except Exception:
        pass

def start_simulator():
    print("🚀 Starting local simulator...")
    kill_process_on_port(8080)
    time.sleep(1)
    venv_python = os.path.join(BASE_DIR, ".venv/bin/python")
    if not os.path.exists(venv_python):
        venv_python = sys.executable # Fallback to current python
        
    proc = subprocess.Popen([venv_python, SIMULATOR_PATH])
    for i in range(10):
        try:
            res = requests.get("http://127.0.0.1:8080/", timeout=1)
            if res.status_code == 200:
                print("✅ Simulator is ready.")
                return proc
        except:
            time.sleep(1)
    print("❌ Error: Could not start simulator.")
    return proc

def reset_test_account(exchange, environment, pair):
    print(f"\n🔄 Exiting all active positions, resetting test account: {exchange.upper()} ({environment.upper()})")
    base_cmd = get_bitmango_executable()
    flags = ["--exchange", exchange, "--pair", pair, "--no-confirm", "--no-color"]
    if environment == "sandbox":
        flags.append("--sandbox")

    # Wipe both SPOT and FUTURES
    for mtype in ["spot", "futures"]:
        print(f"  - Resetting {mtype.upper()}...")
        # Cancel all orders
        subprocess.run(base_cmd + ["cancel", "all"] + flags + ["--market-type", mtype], capture_output=True)
        # Close all positions
        subprocess.run(base_cmd + ["close-all"] + flags + ["--market-type", mtype], capture_output=True)
    print("✅ Test account reset complete.")

def run_suite(suite_name, files, exchange, environment, pair):
    print(f"\n" + "="*60)
    print(f"RUNNING SUITE: {suite_name.upper()}")
    print(f"Exchange: {exchange.upper()} | Env: {environment.upper()}")
    print("="*60)

    for test_file in files:
        print(f"\n[RUN] {test_file}...")
        cmd = [sys.executable, test_file, "--exchange", exchange, "--pair", pair]
        if environment == "sandbox":
            cmd.append("--sandbox")
            
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"❌ TEST FAILED: {test_file}")
            return False
    return True

def main():
    parser = argparse.ArgumentParser(description="Master Test Runner (Free vs Pro)")
    parser.add_argument('--exchange', default='simulated', help='Exchange to test')
    parser.add_argument('--environment', choices=['sandbox', 'live'], default='sandbox', help='Environment')
    parser.add_argument('--pair', default='btc-usdt', help='Pair to use')
    parser.add_argument('--free-only', action='store_true', help='Force only free suite')
    args = parser.parse_args()

    if args.free_only:
        os.environ["BITMANGO_TEST_FREE_ONLY"] = "true"

    sim_proc = None
    try:
        if args.exchange == "simulated":
            sim_proc = start_simulator()

        # Initial Wipe
        reset_test_account(args.exchange, args.environment, args.pair)

        # --- PHASE 1: FREE CORE SUITE ---
        free_tests = [
            f"{FREE_DIR}/audit_technical_mandates.py",
            f"{FREE_DIR}/audit_symbol_mappings.py",
            f"{FREE_DIR}/audit_exchange_timeframes.py",
            f"{FREE_DIR}/test_json_errors.py",
            f"{FREE_DIR}/test_risk_manager.py",
            f"{FREE_DIR}/comprehensive_free.py"
        ]
        
        if not run_suite("Free Core", free_tests, args.exchange, args.environment, args.pair):
            sys.exit(1)

        # Wipe between suites
        reset_test_account(args.exchange, args.environment, args.pair)

        # --- PHASE 2: PRO EXTENSION SUITE ---
        if is_pro_active():
            pro_tests = [
                f"{PRO_DIR}/audit_ops_plugins.py",
                f"{PRO_DIR}/test_pro_smart_stops.py",
                f"{PRO_DIR}/audit_endpoint_coverage.py",
                f"{PRO_DIR}/comprehensive_pro.py"
            ]
            if not run_suite("Pro Extension", pro_tests, args.exchange, args.environment, args.pair):
                sys.exit(1)
        else:
            print("\n⏭️  SKIPPING PRO SUITE: No active Professional license detected or --free-only used.")

        print("\n🎉 ALL PHASES PASSED")

    finally:
        # Final Wipe before exit
        try:
            reset_test_account(args.exchange, args.environment, args.pair)
        except:
            pass

        if sim_proc:
            print("\n🛑 Shutting down simulator...")
            sim_proc.terminate()
            sim_proc.wait()

if __name__ == "__main__":
    main()
