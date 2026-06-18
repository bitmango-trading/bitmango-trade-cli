import pytest
import sqlite3
import os
from playwright.sync_api import Page, expect

DASHBOARD_URL = "http://127.0.0.1:8890"
DB_PATH = "/home/bitmango/git/bitmango-trade-cli-dev/data/pro_audit.db"

def test_index_loads(page: Page):
    print(f"🌍 Navigating to {DASHBOARD_URL}...")
    response = page.goto(DASHBOARD_URL)
    
    # Check HTTP Status
    assert response.status == 200, f"Expected 200 OK, got {response.status}"
    
    # Check Page Title to confirm index.html loaded
    expect(page).to_have_title("BitMango Pro Dashboard")
    
    # Check for critical UI element (Auth Overlay should be visible initially)
    expect(page.locator("#auth-overlay")).to_be_visible()
    
    print("✅ Dashboard index.html loaded successfully.")

def test_database_schema():
    print(f"🗄️ Checking database schema at {DB_PATH}...")
    
    assert os.path.exists(DB_PATH), "Database file not found!"
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check Users Table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    assert cursor.fetchone() is not None, "Table 'users' missing!"
    
    # Check Trades Table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trades';")
    assert cursor.fetchone() is not None, "Table 'trades' missing!"
    
    # Check Reviews Table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trade_reviews';")
    assert cursor.fetchone() is not None, "Table 'trade_reviews' missing!"
    
    conn.close()
    print("✅ Database schema verified.")
