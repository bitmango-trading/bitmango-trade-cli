# Test Results for Bybit (Sandbox Environment)

## Summary

- Account Balance (bybit, sandbox): FAIL
- Account Positions (bybit, sandbox): FAIL
- Query Order Book (bybit, sandbox): FAIL
- Entry Limit Buy (bybit, sandbox): FAIL
- Cancel All Orders (bybit, sandbox): FAIL
- Exit Limit Sell (bybit, sandbox) - Could not fetch current price for BTC/USDT:USDT: FAIL
- Stop Loss Order (bybit, sandbox) - Could not fetch current price for BTC/USDT:USDT: FAIL

## Detailed Output

```
Starting tests for bybit in sandbox environment...
--- Running Test: Account Balance (bybit, sandbox) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango --sandbox account --balance --exchange bybit
FAIL: Account Balance (bybit, sandbox)
Stdout: Attempting to import: bitmango.exchange.bybit.account_open_positions
sys.path: ['/home/trading/git/bitmango-bitmango', '/home/trading/git/bitmango-bitmango', '/usr/lib/python311.zip', '/usr/lib/python3.11', '/usr/lib/python3.11/lib-dynload', 'uv']
Loaded module: bitmango.exchange.bybit.account_open_positions
Using Bybit Testnet
Error fetching balance: bybit {"retCode":10003,"retMsg":"API key is invalid.","result":{},"retExtInfo":{},"time":1757176739589}

Stderr: 
--- Running Test: Account Positions (bybit, sandbox) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango --sandbox account --positions --exchange bybit
FAIL: Account Positions (bybit, sandbox)
Stdout: Attempting to import: bitmango.exchange.bybit.account_open_positions
sys.path: ['/home/trading/git/bitmango-bitmango', '/home/trading/git/bitmango-bitmango', '/usr/lib/python311.zip', '/usr/lib/python3.11', '/usr/lib/python3.11/lib-dynload', 'uv']
Loaded module: bitmango.exchange.bybit.account_open_positions
Using Bybit Testnet
Error fetching positions: bybit {"retCode":10003,"retMsg":"API key is invalid.","result":{},"retExtInfo":{},"time":1757176740470}

Stderr: 
--- Running Test: Query Order Book (bybit, sandbox) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango --sandbox query_order_book --pair BTC-USDT --exchange bybit
FAIL: Query Order Book (bybit, sandbox)
Stdout: Debug: Attempting to import module: bitmango.exchange.bybit.query_orderbook_bybit
Debug: Successfully imported module: bitmango.exchange.bybit.query_orderbook_bybit
Debug: Attempting to get class: BybitQueryOrderBook from module: bitmango.exchange.bybit.query_orderbook_bybit
Debug: Successfully got class: BybitQueryOrderBook
Using Bybit Testnet
Error querying order book: bybit {"retCode":10003,"retMsg":"API key is invalid.","result":{},"retExtInfo":{},"time":1757176741302}

Stderr: 
--- Running Test: Entry Limit Buy (bybit, sandbox) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango --sandbox entry --pair BTC-USDT --direction buy --size 0.0001 --price 10000 --order-type limit --exchange bybit --no-confirm
FAIL: Entry Limit Buy (bybit, sandbox)
Stdout: Using Bybit Testnet
Placing limit buy order for 0.0001 BTC/USDT:USDT at 10000.0
Error placing order: bybit {"retCode":10003,"retMsg":"API key is invalid.","result":{},"retExtInfo":{},"time":1757176742125}

Stderr: 
--- Running Test: Cancel All Orders (bybit, sandbox) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango --sandbox cancel all --pair BTC-USDT --exchange bybit --no-confirm
FAIL: Cancel All Orders (bybit, sandbox)
Stdout: Attempting to import: bitmango.exchange.bybit.account_open_positions
sys.path: ['/home/trading/git/bitmango-bitmango', '/home/trading/git/bitmango-bitmango', '/usr/lib/python311.zip', '/usr/lib/python3.11', '/usr/lib/python3.11/lib-dynload', 'uv']
Loaded module: bitmango.exchange.bybit.account_open_positions
Using Bybit Testnet
Unexpected error: 'BybitAccountPositions' object has no attribute 'cancel_all_orders'

Stderr: 
--- Running Test: Exit Limit Sell (bybit, sandbox) ---
Using Bybit Testnet
Error fetching current price for BTC/USDT:USDT: bybit {"retCode":10003,"retMsg":"API key is invalid.","result":{},"retExtInfo":{},"time":1757176743040}
FAIL: Exit Limit Sell (bybit, sandbox) - Could not fetch current price for BTC/USDT:USDT
--- Running Test: Stop Loss Order (bybit, sandbox) ---
--- Pre-test Cleanup for Stop Loss Order (bybit, sandbox) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango --sandbox cancel all --pair BTC-USDT --exchange bybit --no-confirm
WARNING: Pre-test cleanup failed for Stop Loss Order (bybit, sandbox). Stderr: 
Using Bybit Testnet
Error fetching current price for BTC/USDT:USDT: bybit {"retCode":10003,"retMsg":"API key is invalid.","result":{},"retExtInfo":{},"time":1757176743907}
FAIL: Stop Loss Order (bybit, sandbox) - Could not fetch current price for BTC/USDT:USDT
--- Running Test: Smart Stop Phemex (bybit, sandbox) ---
SKIP: Smart Stop Phemex (bybit, sandbox) - Smart Stop test is Phemex-specific.

--- Test Summary ---
test_account_balance: FAIL
test_account_positions: FAIL
test_query_order_book: FAIL
test_entry_limit_buy: FAIL
test_cancel_all_orders: FAIL
test_exit_limit_sell: FAIL
test_stop_loss_order: FAIL
test_smart_stop_phemex: PASS

```
