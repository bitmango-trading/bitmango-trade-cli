import os
import sqlite3
import subprocess
import time
import requests
import signal
import sys

# Configuration
TEST_DB = "/home/bitmango/git/bitmango-trade-cli-dev/data/test_blank.db"
TEST_PORT = "8895"
DASHBOARD_BINARY = "/usr/local/bin/bitmango-dev-dashboard"
PROJECT_ROOT = "/home/bitmango/git/bitmango-trade-cli-dev"

# Global process variable for cleanup
proc = None

def setup_blank_db():
    print(f"🧹 Creating blank test database: {TEST_DB}")
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    
    conn = sqlite3.connect(TEST_DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    github_id TEXT PRIMARY KEY, 
                    username TEXT NOT NULL, 
                    approved INTEGER DEFAULT 0, 
                    hwid TEXT)''')
    c.execute("INSERT INTO users (github_id, username, approved, hwid) VALUES (?, ?, ?, ?)", 
              ("12345", "testuser", 1, None))
    conn.commit()
    conn.close()

def start_dashboard():
    print(f"🚀 Starting Dashboard on port {TEST_PORT}...")
    env = os.environ.copy()
    env["DATABASE_URL"] = f"sqlite:{TEST_DB}"
    env["IS_DEV"] = "true"
    env["PORT"] = TEST_PORT
    env["BIND_ADDR"] = "127.0.0.1"
    env["GITHUB_CLIENT_ID"] = "dummy_id"
    env["GITHUB_CLIENT_SECRET"] = "dummy_secret"
    env["GITHUB_REDIRECT_URL"] = "http://localhost:8895/auth/callback"
    
    with open("dashboard_test.log", "w") as log:
        process = subprocess.Popen(
            [DASHBOARD_BINARY, "dev"],
            env=env,
            cwd=os.path.join(PROJECT_ROOT, "bitmango-dashboard"),
            stdout=log,
            stderr=log,
            preexec_fn=os.setsid
        )
    return process

def run_tests():
    global proc
    base_url = f"http://127.0.0.1:{TEST_PORT}"
    
    print("🧪 Running Smoke Tests...")
    
    # 1. Check if Index.html is served
    try:
        res = requests.get(base_url, timeout=5)
        if res.status_code == 200:
            print("✅ TEST 1: Index.html served correctly.")
        else:
            print(f"❌ TEST 1: Index.html failed (Status: {res.status_code})")
            return False
    except Exception as e:
        print(f"❌ TEST 1: Connection failed: {e}")
        return False

    return True

if __name__ == "__main__":
    setup_blank_db()
    proc = start_dashboard()
    
    success = False
    try:
        time.sleep(5)
        if proc.poll() is not None:
            print(f"❌ Dashboard exited prematurely with code {proc.poll()}")
            with open("dashboard_test.log", "r") as f:
                print(f.read())
            sys.exit(1)
        success = run_tests()
    finally:
        print("🛑 Shutting down test server...")
        if proc.poll() is None:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        
    if success:
        print("\n🏆 ALL DASHBOARD SMOKE TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n❌ DASHBOARD SMOKE TESTS FAILED!")
        sys.exit(1)
