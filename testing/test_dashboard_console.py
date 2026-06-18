import pytest
from playwright.sync_api import Page, expect

DASHBOARD_URL = "http://127.0.0.1:8890"

def test_console_errors(page: Page):
    error_logs = []
    page.on("console", lambda msg: error_logs.append(msg.text) if msg.type == "error" else None)
    
    print(f"🌍 Navigating to {DASHBOARD_URL}...")
    page.goto(DASHBOARD_URL)
    
    # Check for specific MIME type errors known to occur
    mime_errors = [log for log in error_logs if "Refused to apply style" in log and "MIME type" in log]
    
    if mime_errors:
        print("\n❌ Console Errors Detected:")
        for err in mime_errors:
            print(f"  - {err}")
        pytest.fail(f"Found {len(mime_errors)} MIME type errors in console.")
    else:
        print("✅ No MIME type errors found in console.")

    # Also check for other critical errors
    critical_errors = [log for log in error_logs if "SECURITY_BLOCK" in log or "Exception" in log]
    if critical_errors:
        print("\n❌ Critical Security/JS Errors Detected:")
        for err in critical_errors:
            print(f"  - {err}")
        pytest.fail(f"Found {len(critical_errors)} critical errors in console.")

