# Test Results for Binance (Live Environment)

## Summary

- Account Balance (binance, live): FAIL
- Account Positions (binance, live): FAIL
- Query Order Book (binance, live): FAIL

## Detailed Output

```
Starting tests for binance in live environment...
--- Running Test: Account Balance (binance, live) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango account --balance --exchange binance
FAIL: Account Balance (binance, live)
Stdout: Attempting to import: bitmango.exchange.binance.account_open_positions
sys.path: ['/home/trading/git/bitmango-bitmango', '/home/trading/git/bitmango-bitmango', '/usr/lib/python311.zip', '/usr/lib/python3.11', '/usr/lib/python3.11/lib-dynload', 'uv']
Loaded module: bitmango.exchange.binance.account_open_positions
Error: API keys for binance are not configured in api_keys.py.

Stderr: 
--- Running Test: Account Positions (binance, live) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango account --positions --exchange binance
FAIL: Account Positions (binance, live)
Stdout: Attempting to import: bitmango.exchange.binance.account_open_positions
sys.path: ['/home/trading/git/bitmango-bitmango', '/home/trading/git/bitmango-bitmango', '/usr/lib/python311.zip', '/usr/lib/python3.11', '/usr/lib/python3.11/lib-dynload', 'uv']
Loaded module: bitmango.exchange.binance.account_open_positions
Error: API keys for binance are not configured in api_keys.py.

Stderr: 
--- Running Test: Query Order Book (binance, live) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango query_order_book --pair BTC-USDT --exchange binance
FAIL: Query Order Book (binance, live)
Stdout: Debug: Attempting to import module: bitmango.exchange.binance.query_orderbook_binance
Debug: Successfully imported module: bitmango.exchange.binance.query_orderbook_binance
Debug: Attempting to get class: BinanceQueryOrderBook from module: bitmango.exchange.binance.query_orderbook_binance
Debug: Successfully got class: BinanceQueryOrderBook
Error: API keys for binance are not configured in api_keys.py.

Stderr: 
--- Running Test: Entry Limit Buy (binance, live) ---
SKIP: Entry Limit Buy (binance, live) - Skipping live trading test.
--- Running Test: Cancel All Orders (binance, live) ---
SKIP: Cancel All Orders (binance, live) - Skipping live trading test.
--- Running Test: Exit Limit Sell (binance, live) ---
SKIP: Exit Limit Sell (binance, live) - Skipping live trading test.
--- Running Test: Stop Loss Order (binance, live) ---
SKIP: Stop Loss Order (binance, live) - Skipping live trading test.
--- Running Test: Smart Stop Phemex (binance, live) ---
SKIP: Smart Stop Phemex (binance, live) - Skipping live trading test.

--- Test Summary ---
test_account_balance: FAIL
test_account_positions: FAIL
test_query_order_book: FAIL
test_entry_limit_buy: PASS
test_cancel_all_orders: PASS
test_exit_limit_sell: PASS
test_stop_loss_order: PASS
test_smart_stop_phemex: PASS

```
