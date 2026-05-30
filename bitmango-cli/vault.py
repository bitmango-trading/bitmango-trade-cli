import os
import sys
import json
import base64
import time
import machineid
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from bitmango.output import display_message
from bitmango.config import get_config_path

VAULT_FILE = get_config_path(".bitmango_vault")
SESSION_DIR = "/tmp/bitmango_sessions" if os.name != 'nt' else os.path.join(os.environ.get('TEMP', r'C:\Temp'), 'bitmango_sessions')

def get_machine_key():
    """Generates a hardware-bound encryption key."""
    try:
        # machineid.id() provides a cross-platform unique ID
        m_id = machineid.id()
        
        # Use PBKDF2 to derive a stable 32-byte key from the machine ID
        salt = b'bitmango_salt_v1' # Stable salt for hardware binding
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(m_id.encode()))
        return key
    except Exception as e:
        display_message('error', f"Vault: Failed to generate machine key: {e}")
        raise RuntimeError(f"Vault: Failed to generate machine key: {e}")

def encrypt_data(data, key):
    f = Fernet(key)
    return f.encrypt(json.dumps(data).encode()).decode()

def decrypt_data(encrypted_data, key):
    f = Fernet(key)
    try:
        return json.loads(f.decrypt(encrypted_data.encode()).decode())
    except Exception:
        return None

def _save_atomic(file_path, content, is_json=False):
    """
    Saves content to a file atomically using a temporary file.
    """
    import tempfile
    
    dir_name = os.path.dirname(os.path.abspath(file_path))
    prefix = os.path.basename(file_path) + "."
    
    # Create temp file in the same directory to ensure it's on the same filesystem
    fd, temp_path = tempfile.mkstemp(dir=dir_name, prefix=prefix)
    try:
        with os.fdopen(fd, 'w') as f:
            if is_json:
                json.dump(content, f)
            else:
                f.write(content)
            f.flush()
            os.fsync(f.fileno()) # Ensure it hits disk
        
        # Set strict permissions BEFORE replacing the original
        os.chmod(temp_path, 0o600)
        
        # Atomic replacement
        os.replace(temp_path, file_path)
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e

def save_vault(data):
    key = get_machine_key()
    encrypted = encrypt_data(data, key)
    _save_atomic(VAULT_FILE, encrypted)

def load_vault():
    if not os.path.exists(VAULT_FILE):
        return None
    
    key = get_machine_key()
    with open(VAULT_FILE, 'r') as f:
        encrypted = f.read()
    
    data = decrypt_data(encrypted, key)
    if data is None:
        display_message('debug', "Vault: Decryption failed (Machine mismatch). Falling back to other key sources.")
        return None
    return data

def get_session_file():
    """Returns a user-specific session file path."""
    if not os.path.exists(SESSION_DIR):
        try:
            os.makedirs(SESSION_DIR, mode=0o700, exist_ok=True)
        except:
            pass
    
    import getpass
    username = getpass.getuser()
    return os.path.join(SESSION_DIR, f"session_{username}")

def create_session(ttl_minutes):
    """
    Creates a temporary session token.
    ttl_minutes: -1 for 'until reboot', 0 for 'disabled', >0 for minutes
    """
    session_file = get_session_file()
    expiry = -1
    if ttl_minutes > 0:
        expiry = int(time.time()) + (ttl_minutes * 60)
    elif ttl_minutes == 0:
        return # No session needed if disabled
        
    session_data = {
        "expiry": expiry,
        "created_at": int(time.time())
    }
    
    _save_atomic(session_file, session_data, is_json=True)

def is_session_valid():
    """Checks if the current TOTP session is still active."""
    vault = load_vault()
    if not vault:
        return False
        
    ttl = vault.get("config", {}).get("session_ttl", 10)
    if ttl == 0:
        return True # TOTP disabled
        
    session_file = get_session_file()
    if not os.path.exists(session_file):
        return False
        
    try:
        with open(session_file, 'r') as f:
            session = json.load(f)
            
        expiry = session.get("expiry", -1)
        if expiry == -1:
            # 'Until reboot' logic: on Linux /tmp is often cleared on reboot
            # or we check uptime. For simplicity we treat -1 as persistent 
            # until manual deletion or /tmp wipe.
            return True
            
        if int(time.time()) < expiry:
            return True
    except:
        pass
        
    return False
