# Test Results for Bybit (Live Environment)

## Summary

- Account Balance (bybit, live): FAIL
- Account Positions (bybit, live): FAIL
- Query Order Book (bybit, live): FAIL

## Detailed Output

```
Starting tests for bybit in live environment...
--- Running Test: Account Balance (bybit, live) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango account --balance --exchange bybit
FAIL: Account Balance (bybit, live)
Stdout: Attempting to import: bitmango.exchange.bybit.account_open_positions
sys.path: ['/home/trading/git/bitmango-bitmango', '/home/trading/git/bitmango-bitmango', '/usr/lib/python311.zip', '/usr/lib/python3.11', '/usr/lib/python3.11/lib-dynload', 'uv']
Loaded module: bitmango.exchange.bybit.account_open_positions
Using Bybit Mainnet
Error fetching balance: bybit {"retCode":10003,"retMsg":"API key is invalid.","result":{},"retExtInfo":{},"time":1757176745207}

Stderr: 
--- Running Test: Account Positions (bybit, live) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango account --positions --exchange bybit
FAIL: Account Positions (bybit, live)
Stdout: Attempting to import: bitmango.exchange.bybit.account_open_positions
sys.path: ['/home/trading/git/bitmango-bitmango', '/home/trading/git/bitmango-bitmango', '/usr/lib/python311.zip', '/usr/lib/python3.11', '/usr/lib/python3.11/lib-dynload', 'uv']
Loaded module: bitmango.exchange.bybit.account_open_positions
Using Bybit Mainnet
Error fetching positions: bybit {"retCode":10003,"retMsg":"API key is invalid.","result":{},"retExtInfo":{},"time":1757176746085}

Stderr: 
--- Running Test: Query Order Book (bybit, live) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango query_order_book --pair BTC-USDT --exchange bybit
FAIL: Query Order Book (bybit, live)
Stdout: Debug: Attempting to import module: bitmango.exchange.bybit.query_orderbook_bybit
Debug: Successfully imported module: bitmango.exchange.bybit.query_orderbook_bybit
Debug: Attempting to get class: BybitQueryOrderBook from module: bitmango.exchange.bybit.query_orderbook_bybit
Debug: Successfully got class: BybitQueryOrderBook
Using Bybit Mainnet
Error querying order book: bybit {"retCode":10003,"retMsg":"API key is invalid.","result":{},"retExtInfo":{},"time":1757176746895}

Stderr: 
--- Running Test: Entry Limit Buy (bybit, live) ---
SKIP: Entry Limit Buy (bybit, live) - Skipping live trading test.
--- Running Test: Cancel All Orders (bybit, live) ---
SKIP: Cancel All Orders (bybit, live) - Skipping live trading test.
--- Running Test: Exit Limit Sell (bybit, live) ---
SKIP: Exit Limit Sell (bybit, live) - Skipping live trading test.
--- Running Test: Stop Loss Order (bybit, live) ---
SKIP: Stop Loss Order (bybit, live) - Skipping live trading test.
--- Running Test: Smart Stop Phemex (bybit, live) ---
SKIP: Smart Stop Phemex (bybit, live) - Skipping live trading test.

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
