import subprocess
import json
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from testing.test_helper import skip_if_free, get_bitmango_executable

# Constants
LOCK_FILE = Path.home() / ".config" / "bitmango" / "trading_suspended.lock"

def run_cli(args):
    """Runs bitmango and returns (stdout, stderr, returncode)."""
    full_cmd = get_bitmango_executable() + args + ["-o", "json"]
    result = subprocess.run(full_cmd, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode

def audit_kill_switch_panic():
    print("--- 1. Kill-Switch Panic Audit ---")
    if LOCK_FILE.exists(): LOCK_FILE.unlink()
    
    print("Triggering Panic...", end=" ", flush=True)
    stdout, stderr, code = run_cli(["kill-switch", "panic", "--no-confirm"])
    
    if LOCK_FILE.exists():
        print("PASS ✓ (Lock Created)")
    else:
        print(f"FAIL ❌ (Lock NOT Created)")
        print(f"Stdout: {stdout}")
        print(f"Stderr: {stderr}")
        return False
        
    print("Verifying Command Blockade...", end=" ", flush=True)
    stdout, stderr, code = run_cli(["account", "--exchange", "simulated"])
    if code != 0 and "PERMANENTLY SUSPENDED" in stdout:
        print("PASS ✓")
    else:
        print("FAIL ❌ (Command not blocked)")
        if LOCK_FILE.exists(): LOCK_FILE.unlink()
        return False
        
    if LOCK_FILE.exists(): LOCK_FILE.unlink()
    return True

def audit_detailed_history():
    print("\n--- 2. Detailed History Audit ---")
    commands = [
        ["trades", "--exchange", "simulated", "--pair", "BTC-USDT"],
        ["closed-orders", "--exchange", "simulated", "--pair", "BTC-USDT"],
        ["order-status", "--exchange", "simulated", "--order-id", "sim-123"]
    ]
    
    for cmd in commands:
        print(f"Testing {' '.join(cmd)}...", end=" ", flush=True)
        stdout, stderr, code = run_cli(cmd)
        if code == 0:
            print("PASS ✓")
        else:
            print(f"FAIL ❌ (Code: {code})")
            return False
    return True

def audit_funding_ops():
    print("\n--- 3. Funding Operations Audit ---")
    commands = [
        ["deposits", "--exchange", "simulated"],
        ["withdrawals", "--exchange", "simulated"],
        ["funding-history", "--exchange", "simulated"]
    ]
    
    for cmd in commands:
        print(f"Testing {' '.join(cmd)}...", end=" ", flush=True)
        stdout, stderr, code = run_cli(cmd)
        if code == 0:
            print("PASS ✓")
        else:
            print(f"FAIL ❌ (Code: {code})")
            return False
    return True

def audit_reporting():
    print("\n--- 4. Reporting Plugin Audit ---")
    
    # Test CSV Export
    print("Generating CSV Report...", end=" ", flush=True)
    stdout, stderr, code = run_cli(["report", "--export", "csv", "--exchange", "simulated", "--filename", "test_report.csv"])
    if code == 0:
        if os.path.exists("test_report.csv"):
            print("PASS ✓")
            os.remove("test_report.csv")
        else:
            print("FAIL ❌ (File not created)")
            print(f"Stdout: {stdout}")
            print(f"Stderr: {stderr}")
            return False
    else:
        if "No trade data" in stdout or "No trade data" in stderr:
            print("PASS (No Data) ✓")
        else:
            print(f"FAIL ❌ (Code: {code})")
            return False
            
    # Test JSON Output (standard -o json)
    print("Generating JSON Output...", end=" ", flush=True)
    stdout, stderr, code = run_cli(["report", "--exchange", "simulated"])
    if code == 0:
        try:
            json.loads(stdout)
            print("PASS ✓")
        except:
            print("FAIL ❌ (Invalid JSON output)")
            return False
    else:
        if "No trade data" in stdout or "No trade data" in stderr:
            print("PASS (No Data) ✓")
        else:
            print(f"FAIL ❌ (Code: {code})")
            return False
            
    return True

def main():
    skip_if_free()
    print("=== AUDIT: Operational Commands & Plugins ===")
    
    success = True
    success &= audit_kill_switch_panic()
    success &= audit_detailed_history()
    success &= audit_funding_ops()
    success &= audit_reporting()
    
    if success:
        print("\n🏆 ALL OPS & PLUGINS VERIFIED")
        sys.exit(0)
    else:
        print("\n❌ OPS AUDIT FAILURE")
        sys.exit(1)

if __name__ == "__main__":
    main()
