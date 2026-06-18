#!/usr/bin/env -S uv run python
import subprocess
import sys
import json
import time
import argparse
import os
from datetime import datetime

# Set up project path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

SUPPORTED_EXCHANGES = [
    'binance', 'phemex', 'bybit', 'mexc', 'bitget', 'okx', 
    'hyperliquid', 'bitfinex', 'dydx', 'gateio', 'htx', 
    'kucoin', 'kraken', 'coinbase', 'lbank'
]

class ExchangeVerificationSuite:
    def __init__(self, exchanges=None, sandbox=True, pair="BTC-USDT"):
        self.exchanges = exchanges or SUPPORTED_EXCHANGES
        self.sandbox = sandbox
        self.pair = pair
        self.all_results = {} # {exchange: [results]}
        
    def log_result(self, exchange, feature, sub_feature, status, message="", error=""):
        if exchange not in self.all_results:
            self.all_results[exchange] = []
            
        self.all_results[exchange].append({
            "feature": feature,
            "sub_feature": sub_feature,
            "status": status, # PASS, FAIL, UNSUPPORTED, UNTESTED
            "message": message,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
        
        icons = {"PASS": "✅", "FAIL": "❌", "UNSUPPORTED": "⚠️", "UNTESTED": "⚪"}
        icon = icons.get(status, "❓")
        print(f"  {icon} {feature} > {sub_feature}: {status}")
        if error and status == "FAIL":
            print(f"     Error: {error}")

    def run_bm(self, exchange, cmd_list, market_type="futures", timeout=60):
        common_opts = ["--exchange", exchange, "--no-confirm", "--output", "json"]
        if self.sandbox:
            common_opts.append("--sandbox")
            
        full_cmd = ["./bitmango"] + cmd_list + common_opts + ["--market-type", market_type]
        
        # Check if we have keys for this exchange if it's a private command
        # This is a bit tricky without loading the vault here, but we can detect it from output
        
        try:
            result = subprocess.run([sys.executable] + full_cmd, capture_output=True, text=True, timeout=timeout)
            
            if result.returncode == 99:
                return "UNSUPPORTED", {}, result.stderr.strip()
            
            if result.returncode != 0:
                err_msg = result.stderr.strip() or result.stdout.strip()
                if "API keys for" in err_msg and "not configured" in err_msg:
                    return "UNTESTED", {}, "API keys not configured"
                return "FAIL", {}, err_msg
                
            try:
                out = result.stdout.strip()
                # Find the LAST JSON-like block to avoid interjected warnings at the start
                # We look for a line starting with [ or { and matching to the end
                import re
                json_match = re.search(r'(\[.*\]|\{.*\})', out, re.DOTALL)
                
                if json_match:
                    json_str = json_match.group(1)
                    data = json.loads(json_str)
                    
                    if isinstance(data, dict) and data.get('status') == 'error':
                        return "FAIL", data, data.get('message', 'Unknown Error')
                    
                    return "PASS", data, result.stderr
                return "PASS", {}, result.stderr
            except json.JSONDecodeError as je:
                return "FAIL", {}, f"JSON Decode Error: {je}. Output: {result.stdout[:200]}..."
        except subprocess.TimeoutExpired:
            return "FAIL", {}, "Command Timed Out"
        except Exception as e:
            return "FAIL", {}, str(e)

    def verify_exchange(self, exchange):
        print(f"\n>>> Verifying Exchange: {exchange.upper()} ({'Sandbox' if self.sandbox else 'Live'}) <<<")
        
        try:
            # 1. Market Data (Public)
            self.verify_market_data(exchange)
            
            # 2. Account (Private)
            self.verify_account(exchange)
            
            # 3. Trading (Private - High Risk)
            if self.sandbox:
                self.verify_trading(exchange)
            else:
                self.log_result(exchange, "Trading", "All Trading Features", "UNTESTED", "Skipping trading tests on Live")
        finally:
            self.cleanup(exchange)

    def cleanup(self, exchange):
        """Ensures all orders are cancelled and positions closed."""
        if not self.sandbox:
            return # Extra safety for live
            
        print(f"  Cleanup for {exchange}...")
        # Cancel all for the test pair
        self.run_bm(exchange, ["cancel", "all", "--pair", self.pair], timeout=30)
        # Close all positions
        self.run_bm(exchange, ["close-all"], timeout=30)

    def verify_market_data(self, exchange):
        feature = "Market Data"
        # Markets
        status, data, err = self.run_bm(exchange, ["markets"])
        self.log_result(exchange, feature, "Markets List", status, "Fetched markets", err)
        
        # Order Book
        status, data, err = self.run_bm(exchange, ["query_order_book", "--pair", self.pair])
        self.log_result(exchange, feature, "Order Book", status, "Fetched order book", err)

        # Ticker
        status, data, err = self.run_bm(exchange, ["ticker", "--pair", self.pair])
        self.log_result(exchange, feature, "Ticker", status, "Fetched ticker", err)

        # OHLCV
        status, data, err = self.run_bm(exchange, ["ohlcv", "--pair", self.pair, "--limit", "5"])
        self.log_result(exchange, feature, "OHLCV", status, "Fetched OHLCV", err)

        # Funding
        status, data, err = self.run_bm(exchange, ["funding", "--pair", self.pair])
        self.log_result(exchange, feature, "Funding", status, "Fetched funding rate", err)

    def verify_account(self, exchange):
        feature = "Account"
        # Balance
        status, data, err = self.run_bm(exchange, ["account", "--balance"])
        self.log_result(exchange, feature, "Balance", status, "Fetched balance", err)
        
        # Positions
        status, data, err = self.run_bm(exchange, ["account", "--positions"])
        self.log_result(exchange, feature, "Positions", status, "Fetched positions", err)

        # Ledger
        status, data, err = self.run_bm(exchange, ["ledger", "--currency", "USDT"])
        self.log_result(exchange, feature, "Ledger", status, "Fetched ledger", err)

        # Trades
        status, data, err = self.run_bm(exchange, ["trades", "--pair", self.pair])
        self.log_result(exchange, feature, "Trades", status, "Fetched trades", err)

        # Funding History
        status, data, err = self.run_bm(exchange, ["funding-history", "--pair", self.pair])
        self.log_result(exchange, feature, "Funding History", status, "Fetched funding history", err)

        # Order Status
        status, data, err = self.run_bm(exchange, ["order-status", "--order-id", "test-id", "--pair", self.pair])
        self.log_result(exchange, feature, "Order Status", status, "Fetched order status", err)

        # Closed Orders
        status, data, err = self.run_bm(exchange, ["closed-orders", "--pair", self.pair, "--limit", "5"])
        self.log_result(exchange, feature, "Closed Orders", status, "Fetched closed orders", err)

        # Deposits
        status, data, err = self.run_bm(exchange, ["deposits", "--currency", "USDT"])
        self.log_result(exchange, feature, "Deposits", status, "Fetched deposits", err)

        # Withdrawals
        status, data, err = self.run_bm(exchange, ["withdrawals", "--currency", "USDT"])
        self.log_result(exchange, feature, "Withdrawals", status, "Fetched withdrawals", err)

        # Position Risk
        status, data, err = self.run_bm(exchange, ["position-risk", "--pair", self.pair])
        self.log_result(exchange, feature, "Position Risk", status, "Fetched position risk", err)

        # Leverage
        status, data, err = self.run_bm(exchange, ["leverage", "--leverage", "5", "--pair", self.pair])
        self.log_result(exchange, feature, "Set Leverage", status, "Set leverage", err)

    def verify_trading(self, exchange):
        feature = "Trading"
        # Limit Entry
        status, data, err = self.run_bm(exchange, ["entry", "--pair", self.pair, "--direction", "buy", "--size", "0.001", "--order-type", "limit", "--price", "10000"])
        self.log_result(exchange, feature, "Limit Entry", status, "Placed limit buy", err)
        
        # Cancel All
        status, data, err = self.run_bm(exchange, ["cancel", "all", "--pair", self.pair])
        self.log_result(exchange, feature, "Cancel All", status, "Cancelled orders", err)

    def run_all(self):
        for ex in self.exchanges:
            self.verify_exchange(ex)
            
        # Save results to JSON - MERGE with existing
        output_file = os.path.join(PROJECT_ROOT, "testing", "verification_results.json")
        
        current_data = {"date": datetime.now().isoformat(), "results": {}}
        if os.path.exists(output_file):
            try:
                with open(output_file, "r") as f:
                    current_data = json.load(f)
            except: pass

        # Prepare new results structure if needed
        # Old format: "results": { "binance": [ {feature...} ] }
        # New format: "results": { "binance": { "sandbox": [...], "live": [...] } }
        
        env_key = "sandbox" if self.sandbox else "live"
        
        for exchange, entries in self.all_results.items():
            if exchange not in current_data["results"]:
                current_data["results"][exchange] = {"sandbox": [], "live": []}
            
            # If it's the old format, convert it
            if isinstance(current_data["results"][exchange], list):
                old_entries = current_data["results"][exchange]
                # Assuming old entries were sandbox by default in previous versions
                current_data["results"][exchange] = {"sandbox": old_entries, "live": []}
            
            current_data["results"][exchange][env_key] = entries

        current_data["date"] = datetime.now().isoformat()
        
        with open(output_file, "w") as f:
            json.dump(current_data, f, indent=2)
        print(f"\nVerification results saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Exchange Verification Suite")
    parser.add_argument('--live', action='store_true', help='Run against Live instead of Sandbox')
    parser.add_argument('--exchange', help='Specific exchange to test')
    parser.add_argument('--pair', default='BTC-USDT', help='Trading pair')
    args = parser.parse_args()
    
    exchanges = [args.exchange] if args.exchange else None
    suite = ExchangeVerificationSuite(exchanges=exchanges, sandbox=not args.live, pair=args.pair)
    suite.run_all()
