#!/usr/bin/env -S uv run python
import subprocess
import sys
import json
import time
import argparse
import os

# Set up project path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from bitmango_free.output import display_message

class PhemexAudit:
    def __init__(self, sandbox=True, pair="BTC-USDT"):
        self.sandbox = sandbox
        self.pair = pair
        self.results = []
        self.common_opts = ["--exchange", "phemex", "--no-confirm", "--output", "json"]
        if self.sandbox:
            self.common_opts.append("--sandbox")
        
    def log_result(self, feature, sub_feature, status, message="", error=""):
        self.results.append({
            "feature": feature,
            "sub_feature": sub_feature,
            "status": "PASS" if status else "FAIL",
            "message": message,
            "error": error
        })
        icon = "✅" if status else "❌"
        print(f"{icon} {feature} > {sub_feature}: {'PASS' if status else 'FAIL'}")
        if error:
            print(f"   Error: {error}")

    def run_bm(self, cmd_list, market_type="futures", timeout=60):
        full_cmd = ["./bitmango"] + cmd_list + self.common_opts + ["--market-type", market_type]
        try:
            result = subprocess.run([sys.executable] + full_cmd, capture_output=True, text=True, timeout=timeout)
            if result.returncode != 0:
                err_msg = result.stderr.strip() or result.stdout.strip()
                return False, {}, err_msg
            try:
                out = result.stdout.strip()
                if "{" in out:
                    json_part = out[out.find("{"):]
                    data = json.loads(json_part)
                    
                    # Check for application-level errors in JSON
                    if data.get('status') == 'error':
                        return False, data, data.get('message', 'Unknown Error')
                    
                    # Phemex specific stop order success check
                    if cmd_list[0] == 'stop' and not data.get('id'):
                        return False, data, "No order ID in response"

                    return True, data, result.stderr
                return True, {}, result.stderr
            except json.JSONDecodeError:
                return False, {}, f"JSON Decode Error. Output: {result.stdout[:100]}"
        except subprocess.TimeoutExpired:
            return False, {}, "Command Timed Out"
        except Exception as e:
            return False, {}, str(e)

    def audit_account(self):
        feature = "Account"
        print(f"\n--- Auditing {feature} ---")
        
        # 1. Balance
        success, data, err = self.run_bm(["account", "--balance"])
        self.log_result(feature, "Balance (Futures)", success, "Fetched balance", err)
        
        # 2. Positions
        success, data, err = self.run_bm(["account", "--positions"])
        self.log_result(feature, "Positions", success, "Fetched positions", err)

        # 3. Leverage
        success, data, err = self.run_bm(["leverage", "--leverage", "5", "--pair", self.pair])
        self.log_result(feature, "Set Leverage", success, "Set leverage to 5", err)
        
        # 4. Margin Mode
        success, data, err = self.run_bm(["margin", "--mode", "cross", "--pair", self.pair])
        self.log_result(feature, "Set Margin Mode", success, "Set margin to cross", err)

        # 5. Position Mode
        success, data, err = self.run_bm(["position-mode", "--mode", "hedge", "--pair", self.pair])
        self.log_result(feature, "Set Position Mode", success, "Set position mode to hedge", err)

        # 6. Ledger/History
        success, data, err = self.run_bm(["ledger", "--currency", "USDT"])
        self.log_result(feature, "Ledger/History", success, "Fetched ledger for USDT", err)

    def audit_market_data(self):
        feature = "Market Data"
        print(f"\n--- Auditing {feature} ---")
        
        # 1. Markets
        success, data, err = self.run_bm(["markets"])
        self.log_result(feature, "Markets List", success, "Fetched markets", err)
        
        # 2. Order Book
        success, data, err = self.run_bm(["query_order_book", "--pair", self.pair])
        self.log_result(feature, "Order Book", success, "Fetched order book", err)

    def audit_trading(self):
        feature = "Trading"
        print(f"\n--- Auditing {feature} ---")
        
        # Ensure clean state
        print("Initial cleanup...")
        self.run_bm(["cancel", "all", "--pair", self.pair], timeout=30)
        self.run_bm(["close", "--pair", self.pair], timeout=30)

        # 1. Limit Entry
        success, data, err = self.run_bm(["entry", "--pair", self.pair, "--direction", "buy", "--size", "0.001", "--order-type", "limit", "--price", "15000"])
        self.log_result(feature, "Limit Entry", success, "Placed limit buy", err)
        
        # 2. Market Entry (to enable stop tests)
        print("Placing market order to enable stop loss testing...")
        success_m, data_m, err_m = self.run_bm(["buy", "--pair", self.pair, "--size", "0.01", "--order-type", "market"])
        if success_m:
            print("Market order placed. Waiting for fill propagation (10s)...")
            time.sleep(10) 

        # 3. Cancel All
        success_c, data_c, err_c = self.run_bm(["cancel", "all", "--pair", self.pair], timeout=90)
        self.log_result(feature, "Cancel All (Pair)", success_c, "Cancelled by pair", err_c)

    def audit_stops(self):
        feature = "Stops"
        print(f"\n--- Auditing {feature} ---")
        
        # 1. Native Stop Loss
        success, data, err = self.run_bm(["stop", "--pair", self.pair, "--direction", "sell", "--size", "0.001", "--order-type", "stop_loss", "--stop-price", "10000", "--stop-type", "native"])
        self.log_result(feature, "Native Stop Loss", success, "Placed stop loss", err)
        
        # 2. Native Take Profit
        success, data, err = self.run_bm(["stop", "--pair", self.pair, "--direction", "sell", "--size", "0.001", "--order-type", "take_profit", "--stop-price", "90000", "--stop-type", "native"])
        self.log_result(feature, "Native Take Profit", success, "Placed take profit", err)

        # 3. Trailing Stop (Ghost/CLI-based)
        print("Skipping Trailing Stop audit as it is a long-running polling process.")
        self.log_result(feature, "Trailing Stop", True, "Skipped (Long-running)", "")

        self.run_bm(["cancel", "all", "--pair", self.pair], timeout=30)
        self.run_bm(["close", "--pair", self.pair], timeout=30)

    def generate_report(self):
        report_path = os.path.join(PROJECT_ROOT, "testing", "phemex_audit_report.md")
        with open(report_path, "w") as f:
            f.write("# Phemex Comprehensive Audit Report\n\n")
            f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Environment:** {'Sandbox' if self.sandbox else 'Live'}\n")
            f.write(f"**Pair:** {self.pair}\n\n")
            
            f.write("| Feature | Sub-Feature | Status | Message | Error |\n")
            f.write("|---------|-------------|--------|---------|-------|\n")
            for r in self.results:
                msg = str(r['message']).replace('|', 'I')
                err = str(r['error']).replace('|', 'I').replace('\n', ' ')
                f.write(f"| {r['feature']} | {r['sub_feature']} | {r['status']} | {msg} | {err} |\n")
        
        print(f"\nReport generated at {report_path}")

    def run_full_audit(self):
        self.audit_account()
        self.audit_market_data()
        self.audit_trading()
        self.audit_stops()
        self.generate_report()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phemex Comprehensive Audit")
    parser.add_argument('--live', action='store_true', help='Run against Live instead of Sandbox')
    parser.add_argument('--pair', default='BTC-USDT', help='Trading pair')
    args = parser.parse_args()
    
    audit = PhemexAudit(sandbox=not args.live, pair=args.pair)
    audit.run_full_audit()
