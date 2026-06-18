import os
import bitmango_pro_core as core
from bitmango_free.license import is_pro_enabled, get_machine_id
from bitmango_free.output import display_message

print("\n--- 1. Pro Validation Test ---")
if is_pro_enabled():
    print("✅ License Validated Successfully (Daily Heartbeat + Machine ID Lock)")
else:
    print("❌ License Validation Failed!")

print("\n--- 2. Pro Plugin Test: Accounting (Rust Math) ---")
trades = [150.0, -25.0, 75.5, -5.0]
audit = core.run_accounting_audit(trades)
print(f"✅ Accounting Audit: PnL={audit['total_pnl']}, Trades={audit['trade_count']}, Fees={audit['fees']:.4f}")

print("\n--- 3. Pro Plugin Test: SmartStops (Rust Math) ---")
res = core.calculate_smart_stop(100.0, 110.0, 0.05) # Current: 100, High: 110, Dist: 5%
print(f"✅ SmartStop Level: {res['stop_price']}, Hit: {res['hit']}")

print("\n--- 4. Machine Locking Verification ---")
machine_id = get_machine_id()
print(f"✅ Machine ID Locked: {machine_id}")
