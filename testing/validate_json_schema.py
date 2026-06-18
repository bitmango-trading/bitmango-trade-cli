import subprocess
import json
import os
import sys
import time
from jsonschema import validate, ValidationError

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from testing.test_helper import get_bitmango_executable

# --- FORMAL JSON SCHEMAS (Draft 7) ---

ORDER_DATA_SCHEMA = {
    "type": "object",
    "required": ["id", "symbol", "side", "type", "amount", "status", "filled", "remaining"],
    "properties": {
        "id": {"type": "string"},
        "symbol": {"type": "string"},
        "side": {"enum": ["buy", "sell", "long", "short"]},
        "type": {"enum": ["market", "limit", "stop", "stop_loss", "take_profit"]},
        "amount": {"type": "number", "minimum": 0},
        "status": {"type": "string"},
        "filled": {"type": "number", "minimum": 0},
        "remaining": {"type": "number", "minimum": 0},
        "price": {"type": ["number", "null"]},
        "average": {"type": ["number", "null"]},
        "fee": {"type": ["object", "null"]}
    }
}

CANDLE_SCHEMA = {
    "type": "object",
    "required": ["timestamp", "open", "high", "low", "close", "volume", "indicators"],
    "properties": {
        "timestamp": {"type": "integer"},
        "open": {"type": "number"},
        "high": {"type": "number"},
        "low": {"type": "number"},
        "close": {"type": "number"},
        "volume": {"type": "number"},
        "indicators": {
            "type": "object",
            "properties": {
                "rsi": {"type": ["number", "null"]},
                "ema": {"type": ["number", "null"]}
            }
        }
    }
}

SCHEMAS = {
    "ticker": {
        "type": "object",
        "required": ["type", "exchange", "symbol", "data", "status"],
        "properties": {
            "type": {"const": "ticker"},
            "exchange": {"type": "string"},
            "symbol": {"type": "string"},
            "status": {"const": "success"},
            "data": {
                "type": "object",
                "required": ["symbol", "last", "bid", "ask"],
                "properties": {
                    "symbol": {"type": "string"},
                    "last": {"type": "number", "exclusiveMinimum": 0},
                    "bid": {"type": ["number", "null"]},
                    "ask": {"type": ["number", "null"]}
                }
            }
        }
    },
    "ohlcv": {
        "type": "object",
        "required": ["type", "exchange", "symbol", "timeframe", "data", "status"],
        "properties": {
            "type": {"const": "ohlcv"},
            "exchange": {"type": "string"},
            "symbol": {"type": "string"},
            "timeframe": {"type": "string"},
            "status": {"const": "success"},
            "data": {"type": "array", "items": CANDLE_SCHEMA}
        }
    },
    "order": {
        "type": "object",
        "required": ["type", "exchange", "order", "status"],
        "properties": {
            "type": {"const": "order"},
            "exchange": {"type": "string"},
            "status": {"const": "success"},
            "order": ORDER_DATA_SCHEMA
        }
    },
    "error": {
        "type": "object",
        "required": ["error", "status", "exit_code"],
        "properties": {
            "error": {"type": "string"},
            "status": {"const": "error"},
            "exit_code": {"type": "integer"}
        }
    },
    "balance": {
        "type": "object",
        "required": ["type", "exchange", "market_type", "data", "status"],
        "properties": {
            "type": {"const": "balance"},
            "exchange": {"type": "string"},
            "market_type": {"type": "string"},
            "status": {"const": "success"},
            "data": {"type": "object"}
        }
    }
}

def run_cli(args):
    """Runs the CLI with given args and returns (stdout, stderr, returncode, latency)."""
    full_cmd = get_bitmango_executable() + args + ["-o", "json", "--exchange", "simulated", "--no-confirm"]
    start_time = time.time()
    result = subprocess.run(full_cmd, capture_output=True, text=True)
    latency = (time.time() - start_time) * 1000 # ms
    return result.stdout, result.stderr, result.returncode, latency

def main():
    print("🚀 Starting Simulator for Formal Verification & Risk Checks...")
    sim_proc = subprocess.Popen([os.path.join(project_root, "testing/simulator/run.sh")], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(5)
    
    test_scenarios = [
        ("Ticker", ["ticker", "--pair", "BTC-USDT"], "ticker"),
        ("OHLCV w/ RSI", ["ohlcv", "--pair", "BTC-USDT", "--rsi", "14"], "ohlcv"),
        ("Market Buy", ["buy", "--pair", "BTC-USDT", "--size", "0.1", "--order-type", "market"], "order"),
        ("Balance", ["account", "--balance"], "balance"),
        ("Error: Invalid Pair", ["ticker", "--pair", "NONEXISTENT"], "error"),
        ("Risk: Oversized Order", ["buy", "--pair", "BTC-USDT", "--size", "1000"], "error"),
    ]

    passed = 0
    latencies = []
    
    try:
        for name, args, r_type in test_scenarios:
            print(f"Testing {name:25}...", end=" ", flush=True)
            stdout, stderr, code, latency = run_cli(args)
            latencies.append(latency)
            
            try:
                data = json.loads(stdout.strip())
                validate(instance=data, schema=SCHEMAS[r_type])
                
                # Check for risk-specific message if needed
                if name == "Risk: Oversized Order":
                    if "RISK BREACH" not in data.get('error', ''):
                        print(f"FAILED (Error message mismatch: {data.get('error')})")
                        print("\nFix this issue in a code branch, test, merge. repeat until 100% pass rate")
                        sys.exit(1)

                # Purity check
                if not stdout.strip().startswith(("{", "[")):
                    print(f"FAILED (Stdout pollution)")
                    print("\nFix this issue in a code branch, test, merge. repeat until 100% pass rate")
                    sys.exit(1)
                else:
                    print(f"PASS ✓ ({latency:.1f}ms)")
                    passed += 1
            except json.JSONDecodeError:
                print("FAILED (Invalid JSON)")
                print("\nFix this issue in a code branch, test, merge. repeat until 100% pass rate")
                sys.exit(1)
            except ValidationError as e:
                print(f"FAILED (Schema error: {e.message})")
                print("\nFix this issue in a code branch, test, merge. repeat until 100% pass rate")
                sys.exit(1)
            except Exception as e:
                print(f"FAILED (Error: {e})")
                print("\nFix this issue in a code branch, test, merge. repeat until 100% pass rate")
                sys.exit(1)
                
    finally:
        print("\n🛑 Shutting down simulator...")
        sim_proc.terminate()
        sim_proc.wait()
        
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    print(f"\nPhase 7 Result: {passed}/{len(test_scenarios)} tests passed.")
    print(f"Average Latency: {avg_latency:.1f}ms")
    
    if passed < len(test_scenarios):
        sys.exit(1)

if __name__ == "__main__":
    main()
