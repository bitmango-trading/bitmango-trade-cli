# Test Results for Mexc (Live Environment)

## Summary

- Account Balance (mexc, live): FAIL
- Account Positions (mexc, live): FAIL
- Query Order Book (mexc, live): FAIL

## Detailed Output

```
Starting tests for mexc in live environment...
--- Running Test: Account Balance (mexc, live) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango account --balance --exchange mexc
FAIL: Account Balance (mexc, live)
Stdout: Attempting to import: bitmango.exchange.mexc.account_open_positions
sys.path: ['/home/trading/git/bitmango-bitmango', '/home/trading/git/bitmango-bitmango', '/usr/lib/python311.zip', '/usr/lib/python3.11', '/usr/lib/python3.11/lib-dynload', 'uv']
Loaded module: bitmango.exchange.mexc.account_open_positions
Error: API keys for mexc are not configured in api_keys.py.

Stderr: 
--- Running Test: Account Positions (mexc, live) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango account --positions --exchange mexc
FAIL: Account Positions (mexc, live)
Stdout: Attempting to import: bitmango.exchange.mexc.account_open_positions
sys.path: ['/home/trading/git/bitmango-bitmango', '/home/trading/git/bitmango-bitmango', '/usr/lib/python311.zip', '/usr/lib/python3.11', '/usr/lib/python3.11/lib-dynload', 'uv']
Loaded module: bitmango.exchange.mexc.account_open_positions
Error: API keys for mexc are not configured in api_keys.py.

Stderr: 
--- Running Test: Query Order Book (mexc, live) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango query_order_book --pair BTC-USDT --exchange mexc
FAIL: Query Order Book (mexc, live)
Stdout: Debug: Attempting to import module: bitmango.exchange.mexc.query_orderbook_mexc
Debug: Successfully imported module: bitmango.exchange.mexc.query_orderbook_mexc
Debug: Attempting to get class: MexcQueryOrderBook from module: bitmango.exchange.mexc.query_orderbook_mexc
Debug: Successfully got class: MexcQueryOrderBook
Error: API keys for mexc are not configured in api_keys.py.

Stderr: 
--- Running Test: Entry Limit Buy (mexc, live) ---
SKIP: Entry Limit Buy (mexc, live) - Skipping live trading test.
--- Running Test: Cancel All Orders (mexc, live) ---
SKIP: Cancel All Orders (mexc, live) - Skipping live trading test.
--- Running Test: Exit Limit Sell (mexc, live) ---
SKIP: Exit Limit Sell (mexc, live) - Skipping live trading test.
--- Running Test: Stop Loss Order (mexc, live) ---
SKIP: Stop Loss Order (mexc, live) - Skipping live trading test.
--- Running Test: Smart Stop Phemex (mexc, live) ---
SKIP: Smart Stop Phemex (mexc, live) - Skipping live trading test.

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
