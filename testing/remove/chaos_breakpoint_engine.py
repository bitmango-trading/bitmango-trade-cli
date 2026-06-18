#!/usr/bin/env -S uv run python
import requests
import time
import sys
import os
import random
import json
import csv
import concurrent.futures
from datetime import datetime
from argparse import Namespace

# Project root for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import bitmango_free.output
bitmango.output.display_message = lambda *args, **kwargs: None

from bitmango_free.exchange.simulated.account_open_positions import SimulatedExchange

SIMULATOR_URL = "http://127.0.0.1:8000"
CSV_FILE = "testing/chaos_results.csv"

class FastFuzzer:
    def __init__(self, worker_id):
        self.worker_id = f"worker_{worker_id}"
        self.args = Namespace(exchange="simulated", sandbox=False, market_type="spot", verbose=False)
        self.exchange = SimulatedExchange(self.args)
        self._original_request = self.exchange._request
        self.exchange._request = self.patched_request

    def patched_request(self, method, path, **kwargs):
        params = kwargs.get('params', {})
        params['uid'] = self.worker_id
        kwargs['params'] = params
        return self._original_request(method, path, **kwargs)

    def setup_worker(self):
        setup_args = Namespace(pair="BTC-USDT", direction="buy", size=1.0, order_type="market")
        self.exchange.entry(setup_args)
        # Snapshot current equity
        try:
            res = requests.get(f"{SIMULATOR_URL}/debug", params={"uid": self.worker_id}, timeout=1).json()
            self.initial_equity = res["balance"].get("USDT", 0) + (res["balance"].get("BTC", 0) * 70000.0)
        except:
            self.initial_equity = 100000.0

    def run_test(self, feature_type, config):
        success = False
        if feature_type == "Polling":
            exit_args = Namespace(pair="BTC-USDT", direction="sell", size=1.0, order_type="market")
            try:
                self.exchange.entry(exit_args)
                success = True
            except: success = False
        else:
            stop_args = Namespace(pair="BTC-USDT", direction="buy", size=1.0, stop_price=60000, order_type="stop_market")
            try:
                self.exchange.stop_market(stop_args)
                success = True
            except: success = False
        
        try:
            res = requests.get(f"{SIMULATOR_URL}/debug", params={"uid": self.worker_id}, timeout=1).json()
            final_equity = res["balance"].get("USDT", 0) + (res["balance"].get("BTC", 0) * 10000.0)
            loss_pct = ((self.initial_equity - final_equity) / self.initial_equity) * 100 if self.initial_equity > 0 else 0
        except:
            loss_pct = 100.0

        return {
            "feature": feature_type,
            "latency_max": config["latency_max"],
            "error_rate": config["error_rate"],
            "dropout_rate": config["dropout_rate"],
            "loss_pct": loss_pct,
            "success": success,
            "is_breakage": loss_pct > 15.0
        }

def main():
    num_workers = 10
    num_rounds = 100 
    
    print(f"🚀 Fuzzing: {num_rounds} rounds x {num_workers} workers...")
    fuzzers = [FastFuzzer(i) for i in range(num_workers)]
    all_results = []
    start_time = time.time()
    
    with open(CSV_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["feature", "latency_max", "error_rate", "dropout_rate", "loss_pct", "success", "is_breakage"])

        requests.post(f"{SIMULATOR_URL}/chaos", json={"dropout_rate": 0, "error_rate": 0, "latency_min": 0, "latency_max": 0})
        requests.post(f"{SIMULATOR_URL}/ticker/price", params={"symbol": "BTCUSDT", "price": 70000.0})

        for r in range(num_rounds):
            for fuzzer in fuzzers: fuzzer.setup_worker()
            
            config = {
                "latency_min": 0.01,
                "latency_max": random.uniform(0.02, 0.2),
                "error_rate": random.uniform(0.0, 0.05),
                "dropout_rate": random.uniform(0.0, 0.02)
            }
            requests.post(f"{SIMULATOR_URL}/chaos", json=config)
            
            feature = random.choice(["Polling", "Native"])
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
                futures = [executor.submit(fuzzer.run_test, feature, config) for fuzzer in fuzzers]
                requests.post(f"{SIMULATOR_URL}/ticker/price", params={"symbol": "BTCUSDT", "price": 10000.0})
                time.sleep(1.0) # Increased from 0.1 to 1.0

                for future in concurrent.futures.as_completed(futures):
                    res = future.result()
                    all_results.append(res)
                    writer.writerow([res["feature"], res["latency_max"], res["error_rate"], res["dropout_rate"], f"{res['loss_pct']:.4f}", res["success"], res["is_breakage"]])
            
            requests.post(f"{SIMULATOR_URL}/chaos", json={"dropout_rate": 0, "error_rate": 0, "latency_min": 0, "latency_max": 0})
            requests.post(f"{SIMULATOR_URL}/ticker/price", params={"symbol": "BTCUSDT", "price": 70000.0})
            
            if (r+1) % 10 == 0:
                print(f"Round {r+1}/{num_rounds} complete...")

    duration = time.time() - start_time
    print(f"✅ Complete: {len(all_results)} iterations in {duration:.2f}s")

if __name__ == "__main__":
    main()
