import os
import time
import json
import requests
from bitmango.output import display_message

# Path to local validation cache (Hidden in user's vault)
CACHE_FILE = ".bitmango_vault/.license_cache"
API_URL = "http://127.0.0.1:8888/validate"

def get_machine_id():
    """Generates a hardware-locked unique ID via the Rust Core."""
    try:
        import bitmango_pro_core
        return bitmango_pro_core.get_machine_id()
    except ImportError:
        # Fallback for Free version (or if binary is missing)
        import uuid
        import hashlib
        return hashlib.sha256(str(uuid.getnode()).encode()).hexdigest()

def get_pro_token():
    """Returns the current valid Pro token if it exists."""
    cache = _load_cache()
    if cache and (time.time() - cache.get("last_sync", 0)) < 172800: # 48h validity
        return cache.get("token")
    return None

def get_public_key():
    """Returns the server public key for JWT validation."""
    # In production, this would be a hardcoded RSA public key
    # For Alpha, we use a shared secret for HS256 validation
    return os.environ.get("BITMANGO_PUBLIC_KEY", "bitmango-alpha-secret")

def is_pro_enabled():
    """
    Checks if Professional features are enabled.
    Supports daily heartbeats with a 24-hour grace period.
    """
    # 1. Check for Manual override (Dev only)
    if os.environ.get("BITMANGO_PRO_ENABLED") == "true":
        return True

    # 2. Try to load local cache
    cache = _load_cache()
    now = time.time()

    if cache:
        last_sync = cache.get("last_sync", 0)
        
        # 3. If synced within 24 hours, we are good
        if (now - last_sync) < 86400: # 24 Hours
            return True

        # 4. If older than 24h, attempt a refresh
        if _perform_online_validation():
            return True

        # 5. If refresh fails (offline/server down), allow 24h Grace Period
        if (now - last_sync) < 172800: # 48 Hours Total (24h + 24h Grace)
            display_message('warning', "⚠️ Validation server offline. 24h grace period active.")
            return True

    # 6. No cache or Grace period expired: Revert to Free
    return False

def _load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return None

def _perform_online_validation():
    """Performs daily heartbeat with validation server."""
    license_key = os.environ.get("BITMANGO_LICENSE_KEY")
    if not license_key:
        return False

    machine_id = get_machine_id()

    try:
        response = requests.post(API_URL, json={
            "license_key": license_key,
            "machine_id": machine_id
        }, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'active':
                # Update Cache
                with open(CACHE_FILE, 'w') as f:
                    json.dump({
                        "last_sync": time.time(),
                        "token": data['token'],
                        "tier": data['tier']
                    }, f)
                return True
    except:
        pass
    return False

def require_pro(feature_name):
    """Enforces Pro tier for specific commands."""
    if not is_pro_enabled():
        msg = f"Feature '{feature_name}' is exclusive to BitMango Professional Tier."
        display_message('error', msg, icon="🛑")
        raise PermissionError(msg)
