import os
import sys

import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Base directory setup
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, base_dir)

from bitmango.vault import save_vault

# Create a mock vault for UI testing
vault_data = {
    "keys": {
        "binance": {"api_key": "test_key", "secret": "test_secret"},
        "phemex_testnet": {"api_key": "test_sandbox", "secret": "test_sandbox_secret"}
    },
    "config": {
        "session_ttl": 15,
        "totp_secret": "JBSWY3DPEHPK3PXP"
    }
}
save_vault(vault_data)
print("✅ Mock vault created for UI testing.")
