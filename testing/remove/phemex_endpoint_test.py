import ccxt
import os
import sys
import json
import time
from decimal import Decimal

# Add project root to sys.path to import API_KEYS
sys.path.insert(0, os.getcwd())
from api_keys import API_KEYS

def log_test(name, success, details=""):
    status = "PASS" if success else "FAIL"
    print(f"[{status}] {name}")
    if details:
        print(f"      {details}")
    return {"name": name, "status": status, "details": details}

def run_phemex_tests():
    api_key = API_KEYS.get('phemex', {}).get('api_key')
    secret = API_KEYS.get('phemex', {}).get('secret')
    
    if not api_key or not secret:
        print("Error: Phemex API keys not found in api_keys.py")
        return

    results = []
    
    # Initialize Exchange
    exchange = ccxt.phemex({
        'apiKey': api_key,
        'secret': secret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'swap',
        }
    })
    exchange.set_sandbox_mode(True)
    
    print("--- Starting Phemex Testnet Endpoint Verification ---")
    print(f"CCXT Version: {ccxt.__version__}")
    
    try:
        # 1. Public: Load Markets
        exchange.load_markets()
        results.append(log_test("Load Markets", True, f"Loaded {len(exchange.symbols)} symbols"))
        
        # 2. Public: Fetch Price
        symbol = 'BTC/USDT:USDT'
        ticker = exchange.fetch_ticker(symbol)
        current_price = ticker.get('last')
        if current_price is None:
            current_price = float(ticker['info'].get('markPriceRp', 0))
        if current_price == 0:
            ob = exchange.fetch_order_book(symbol)
            if ob['asks']:
                current_price = ob['asks'][0][0]
        
        if current_price and current_price > 0:
            results.append(log_test("Fetch Price", True, f"Price for {symbol}: {current_price}"))
        else:
            results.append(log_test("Fetch Price", False, "Could not determine current price"))
            return

        # 3. Private: Fetch Balance
        balance = exchange.fetch_balance()
        usdt_bal = balance['total'].get('USDT', 0)
        results.append(log_test("Fetch Balance", True, f"USDT Balance: {usdt_bal}"))
        
        # 4. Limit Order Test
        print("\nTesting Limit Order...")
        low_price = exchange.decimal_to_precision(current_price * 0.5, ccxt.ROUND, exchange.market(symbol)['precision']['price'], ccxt.TICK_SIZE)
        params = {'posSide': 'Long'}
        order = exchange.create_order(symbol, 'limit', 'buy', 0.001, low_price, params)
        order_id = order['id']
        results.append(log_test("Place Limit Order", True, f"ID: {order_id}"))
        
        time.sleep(2)
        # Fallback for fetch_order
        try:
            fetched = exchange.fetch_order(order_id, symbol)
            status = fetched.get('status', 'unknown')
        except:
            open_orders = exchange.fetch_open_orders(symbol)
            match = next((o for o in open_orders if o['id'] == order_id), None)
            status = match['status'] if match else 'not found'
        
        results.append(log_test("Order Status Check", status != 'not found', f"Status: {status}"))
        
        # 5. Cancel Test
        exchange.cancel_order(order_id, symbol, params=params)
        results.append(log_test("Cancel Order", True))

        # 6. Market Order Test (The Real Challenge)
        print("\nTesting Market Order...")
        try:
            market_order = exchange.create_order(symbol, 'market', 'buy', 0.001, params=params)
            mo_id = market_order['id']
            results.append(log_test("Place Market Order", True, f"ID: {mo_id}"))
            
            print("Waiting for matching engine...")
            time.sleep(5)
            
            # Use fetch_open_orders to see if it's still there
            open_orders = exchange.fetch_open_orders(symbol)
            is_open = any(o['id'] == mo_id for o in open_orders)
            
            if is_open:
                results.append(log_test("Market Order Fill", False, "Order STUCK in open orders"))
                print(f"Cleaning up stuck market order {mo_id}...")
                exchange.cancel_order(mo_id, symbol, params=params)
            else:
                # Check filled via fetch_order or fetch_balance
                try:
                    mo_check = exchange.fetch_order(mo_id, symbol)
                    filled = float(mo_check.get('filled', 0))
                except:
                    filled = 0 # Assume not filled if we can't find it and it's not open? 
                
                results.append(log_test("Market Order Fill", filled > 0, f"Filled: {filled}"))

        except Exception as e:
            results.append(log_test("Market Order Execution", False, str(e)))

        # 7. Positions
        positions = exchange.fetch_positions([symbol])
        active_pos = [p for p in positions if float(p.get('contracts', 0)) > 0]
        results.append(log_test("Fetch Positions", True, f"Active: {len(active_pos)}"))

    except Exception as e:
        results.append(log_test("Critical Failure", False, str(e)))
        import traceback
        traceback.print_exc()

    # Generate Report
    report_path = "testing/phemex_test_report.md"
    with open(report_path, "w") as f:
        f.write("# Phemex Testnet Detailed Verification Report\n\n")
        f.write(f"- **Time:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- **CCXT Version:** {ccxt.__version__}\n\n")
        f.write("| Test | Status | Details |\n|---|---|---|\n")
        for r in results:
            f.write(f"| {r['name']} | {r['status']} | {r['details']} |\n")
    
    print(f"Report: {report_path}")

if __name__ == "__main__":
    run_phemex_tests()
