import os
import subprocess
import time
import sys

# Ensure project root is in path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from testing.test_helper import skip_if_free, get_bitmango_executable

TARGET_FILE = os.path.join(project_root, "bitmango/exchange/simulated/account_open_positions.py")

def main():
    skip_if_free()
    print("=== PRO-TEST: Ledger Fallback Verification ===")
    
    # 1. Disable fetchLedger in SimulatedExchange
    if not os.path.exists(TARGET_FILE):
        print(f"❌ Target file {TARGET_FILE} not found.")
        sys.exit(1)

    with open(TARGET_FILE, 'r') as f:
        original_content = f.read()
        
    try:
        modified_content = original_content.replace("'fetchLedger': True", "'fetchLedger': False")
        with open(TARGET_FILE, 'w') as f:
            f.write(modified_content)
        print("Disabled fetchLedger in SimulatedExchange.")
        
        # 2. Run Ledger Command
        print("Running ledger command (expecting fallback results)...")
        cmd = get_bitmango_executable() + ["ledger", "--currency", "USDT", "--exchange", "simulated", "--sandbox", "--no-color", "-o", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print("STDOUT:", result.stdout)
        
        # 3. Verify Output
        # Fallback entries are constructed manually in AccountMixin.
        expected_strings = [
            "1000.0", # Deposit
            "500.0"   # Withdrawal
        ]
        
        failed = False
        for s in expected_strings:
            if s not in result.stdout:
                print(f"FAILED: Missing expected value '{s}' in ledger output")
                failed = True
        
        if not failed:
            print("✅ SUCCESS: Ledger fallback verified.")
            sys.exit(0)
        else:
            sys.exit(1)
            
    finally:
        # 4. Restore File
        with open(TARGET_FILE, 'w') as f:
            f.write(original_content)
        print("Restored SimulatedExchange configuration.")

if __name__ == "__main__":
    main()
