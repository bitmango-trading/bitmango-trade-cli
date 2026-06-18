import os
import sys

# Ensure project root is in path so we can import bitmango_free
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from bitmango_free.license import is_pro_enabled
except ImportError:
    # Fallback if bitmango is not installed in the path
    def is_pro_enabled():
        return False

def is_pro_active():
    """
    Determines if Pro features should be tested.
    Returns False if BITMANGO_TEST_FREE_ONLY is set, 
    otherwise returns the actual state from the license module.
    """
    if os.environ.get("BITMANGO_TEST_FREE_ONLY") == "true":
        return False
    return is_pro_enabled()

def get_bitmango_executable():
    """Returns the executable command for bitmango as a list."""
    custom = os.environ.get("BITMANGO_EXECUTABLE")
    if custom:
        return [custom]
    # Default to running the source script with current python
    return [sys.executable, "./bitmango"]

def get_help_executable():
    """Returns the executable command for bitmango-help as a list."""
    custom = os.environ.get("BITMANGO_HELP_EXECUTABLE")
    if custom:
        return [custom]
    # Default to running the source script with current python
    return [sys.executable, "./bitmango-help"]

def skip_if_free():
    """Helper to exit a test script early if Pro is not active."""
    if not is_pro_active():
        print("⏩ SKIPPING: This test requires BitMango Professional tier.")
        sys.exit(0)
