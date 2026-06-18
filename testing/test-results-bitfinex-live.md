# Test Results for Bitfinex (Live Environment)

## Summary

- Account Balance (bitfinex, live): FAIL
- Account Positions (bitfinex, live): FAIL
- Query Order Book (bitfinex, live): FAIL

## Detailed Output

```
Starting tests for bitfinex in live environment...
--- Running Test: Account Balance (bitfinex, live) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango account --balance --exchange bitfinex
FAIL: Account Balance (bitfinex, live)
Stdout: Attempting to import: bitmango.exchange.bitfinex.account_open_positions
sys.path: ['/home/trading/git/bitmango-bitmango', '/home/trading/git/bitmango-bitmango', '/usr/lib/python311.zip', '/usr/lib/python3.11', '/usr/lib/python3.11/lib-dynload', 'uv']
Loaded module: bitmango.exchange.bitfinex.account_open_positions
Error: API keys for bitfinex are not configured in api_keys.py.

Stderr: 
--- Running Test: Account Positions (bitfinex, live) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango account --positions --exchange bitfinex
FAIL: Account Positions (bitfinex, live)
Stdout: Attempting to import: bitmango.exchange.bitfinex.account_open_positions
sys.path: ['/home/trading/git/bitmango-bitmango', '/home/trading/git/bitmango-bitmango', '/usr/lib/python311.zip', '/usr/lib/python3.11', '/usr/lib/python3.11/lib-dynload', 'uv']
Loaded module: bitmango.exchange.bitfinex.account_open_positions
Error: API keys for bitfinex are not configured in api_keys.py.

Stderr: 
--- Running Test: Query Order Book (bitfinex, live) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango query_order_book --pair BTC-USDT --exchange bitfinex
FAIL: Query Order Book (bitfinex, live)
Stdout: Debug: Attempting to import module: bitmango.exchange.bitfinex.query_orderbook_bitfinex
Debug: Successfully imported module: bitmango.exchange.bitfinex.query_orderbook_bitfinex
Debug: Attempting to get class: BitfinexQueryOrderBook from module: bitmango.exchange.bitfinex.query_orderbook_bitfinex
Debug: Successfully got class: BitfinexQueryOrderBook
Error: API keys for bitfinex are not configured in api_keys.py.

Stderr: 
--- Running Test: Entry Limit Buy (bitfinex, live) ---
SKIP: Entry Limit Buy (bitfinex, live) - Skipping live trading test.
--- Running Test: Cancel All Orders (bitfinex, live) ---
SKIP: Cancel All Orders (bitfinex, live) - Skipping live trading test.
--- Running Test: Exit Limit Sell (bitfinex, live) ---
SKIP: Exit Limit Sell (bitfinex, live) - Skipping live trading test.
--- Running Test: Stop Loss Order (bitfinex, live) ---
SKIP: Stop Loss Order (bitfinex, live) - Skipping live trading test.
--- Running Test: Smart Stop Phemex (bitfinex, live) ---
SKIP: Smart Stop Phemex (bitfinex, live) - Skipping live trading test.

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
