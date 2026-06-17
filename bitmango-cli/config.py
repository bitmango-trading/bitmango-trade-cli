import os
import sys
from pathlib import Path

def get_default_config_dir():
    """
    Returns the default configuration directory based on the OS.
    """
    if os.name == 'nt': # Windows
        base = os.environ.get('APPDATA')
        if not base:
            base = Path.home() / 'AppData' / 'Roaming'
        return Path(base) / 'bitmango'
    elif sys.platform == 'darwin': # macOS
        return Path.home() / 'Library' / 'Application Support' / 'bitmango'
    else: # Linux and others
        base = os.environ.get('XDG_CONFIG_HOME')
        if not base:
            base = Path.home() / '.config'
        return Path(base) / 'bitmango'

def get_config_dir():
    """
    Returns the configuration directory to use.
    Prioritizes BITMANGO_CONFIG_DIR environment variable.
    If the current directory contains a .bitmango_vault, it assumes 'portable/dev mode'.
    """
    env_dir = os.environ.get('BITMANGO_CONFIG_DIR')
    if env_dir:
        return Path(env_dir)

    # If we are running from a git repo or have a local vault, use local dir for dev convenience
    # BUT if specifically installed, we should probably prefer the global one.
    # Let's check for a marker file or if it's installed in a standard 'bin' path.
    
    local_vault = Path('.bitmango_vault')
    if local_vault.exists():
        return Path('.')

    # Default to system-standard path
    return get_default_config_dir()

def get_config_path(filename):
    """
    Returns the full path for a configuration file.
    Ensures the directory exists.
    """
    config_dir = get_config_dir()
    if config_dir != Path('.'):
        config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / filename
