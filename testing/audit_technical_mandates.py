import subprocess
import json
import sys
import os
import time
import requests
from pathlib import Path

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from test_helper import is_pro_active, skip_if_free, get_bitmango_executable

# Constants

SIMULATOR_URL = "http://127.0.0.1:8080"
LOCK_FILE = Path.home() / ".config" / "bitmango" / "trading_suspended.lock"

def run_cli(args):
    """Runs bitmango and returns (stdout, stderr, returncode)."""
    full_cmd = get_bitmango_executable() + args + ["-o", "json"]
    result = subprocess.run(full_cmd, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode

def set_sim_chaos(config):
    try:
        requests.post(f"{SIMULATOR_URL}/chaos", json=config, timeout=1)
    except:
        pass

def cleanup():
    if LOCK_FILE.exists():
        LOCK_FILE.unlink()
    set_sim_chaos({"stale_timestamp": None})

def audit_json_purity():
    print("--- 1. JSON Purity Audit ---")
    commands = [
        ["ticker", "--pair", "BTC-USDT", "--exchange", "simulated"],
        ["account", "--exchange", "simulated"],
        ["markets", "--exchange", "simulated"],
        ["help"], # Should output JSON help if -o json passed? Or maybe help ignores it? Let's see.
    ]
    
    for cmd in commands:
        print(f"Testing {' '.join(cmd)}...", end=" ", flush=True)
        stdout, stderr, code = run_cli(cmd)
        
        # Help command might not return JSON, that's acceptable if documented, 
        # but for data commands it MUST be JSON.
        if cmd[0] == 'help':
            # Help usually prints to stdout. If -o json is respected, it should be JSON string of help text?
            # Current implementation of help might not support JSON. 
            # If so, we skip help for purity check or expect specific behavior.
            # Let's skip help for now as it's often special.
            print("SKIPPED (Help command special case)")
            continue

        try:
            data = json.loads(stdout)
            print("PASS ✓")
        except json.JSONDecodeError:
            print(f"FAIL ❌ (Invalid JSON)")
            print(f"Stdout: {stdout[:200]}...")
            return False
            
        if not isinstance(data, (dict, list)):
            print(f"FAIL ❌ (JSON root is not object/list)")
            return False

    return True

def audit_risk_breach():
    print("\n--- 2. Risk Breach & Stale Data Audit ---")
    
    # A. Stale Data
    print("Scenario: Stale Data (15s delay)...", end=" ", flush=True)
    stale_ts = int((time.time() - 15) * 1000)
    set_sim_chaos({"stale_timestamp": stale_ts})
    
    stdout, stderr, code = run_cli(["ticker", "--pair", "BTC-USDT", "--exchange", "simulated"])
    set_sim_chaos({"stale_timestamp": None}) # Reset immediately
    
    try:
        res = json.loads(stdout)
        if code != 0 and ("stale" in res.get('error', '').lower() or "risk breach" in res.get('error', '').lower()):
             print("PASS ✓")
        else:
             print(f"FAIL ❌ (Code: {code}, Error: {res.get('error')})")
             return False
    except:
        print(f"FAIL ❌ (Invalid JSON response)")
        return False

    # B. Excessive Size
    print("Scenario: Excessive Order Size ($500k)...", end=" ", flush=True)
    # Ensure price is normal
    requests.post(f"{SIMULATOR_URL}/ticker/price", params={"symbol": "BTCUSDT", "price": 50000.0})
    
    stdout, stderr, code = run_cli(["buy", "--pair", "BTC-USDT", "--size", "10", "--exchange", "simulated", "--no-confirm"])
    
    try:
        res = json.loads(stdout)
        # We expect a RISK BREACH status or error
        if code != 0 and (res.get('status') == 'risk_breach' or "risk breach" in res.get('error', '').lower()):
            print("PASS ✓")
        else:
            print(f"FAIL ❌ (Code: {code}, Status: {res.get('status')}, Error: {res.get('error')})")
            return False
    except:
        print(f"FAIL ❌ (Invalid JSON response)")
        return False
        
    return True

def audit_lock_file():
    print("\n--- 3. Lock File Concurrency Audit ---")
    print("Scenario: Existing Lock File...", end=" ", flush=True)
    
    # Create lock file
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOCK_FILE, 'w') as f:
        f.write("MANUAL_LOCK")
        
    stdout, stderr, code = run_cli(["buy", "--pair", "BTC-USDT", "--size", "0.001", "--exchange", "simulated", "--no-confirm"])
    
    cleanup() # Remove lock
    
    # We expect immediate failure
    # The error message for lock file usually goes to stderr if it's a pre-check, 
    # but if -o json is on, it should hopefully be in JSON error?
    # If the lock check happens BEFORE argument parsing or renderer setup, it might be raw text.
    # Let's check both.
    
    if "TRADING PERMANENTLY SUSPENDED" in stdout or "TRADING PERMANENTLY SUSPENDED" in stderr:
         print("PASS ✓")
    else:
         print(f"FAIL ❌ (Lock file ignored?)")
         print(f"Stdout: {stdout}")
         print(f"Stderr: {stderr}")
         return False
         
    return True

def main():
    if is_pro_active():
        print("Running FREE test with PRO features enabled.")
    else:
        print("Running FREE test in FREE mode.")

    print("=== AUDIT: Technical Mandates (JSON Purity, Risk, Safety) ===")
    cleanup()
    
    # Ensure simulator is running (helper)
    print(f"Checking simulator at {SIMULATOR_URL}...")
    connected = False
    for i in range(5):
        try:
            requests.get(SIMULATOR_URL, timeout=2)
            connected = True
            break
        except Exception as e:
            print(f"  Attempt {i+1} failed: {e}")
            time.sleep(1)
            
    if not connected:
        print(f"❌ Simulator not running at {SIMULATOR_URL}. Please start it first.")
        sys.exit(1)

    success = True
    success &= audit_json_purity()
    success &= audit_risk_breach()
    success &= audit_lock_file()
    
    cleanup()
    
    if success:
        print("\n🏆 ALL TECHNICAL MANDATES VERIFIED")
        sys.exit(0)
    else:
        print("\n❌ MANDATE FAILURE")
        sys.exit(1)

if __name__ == "__main__":
    main()
