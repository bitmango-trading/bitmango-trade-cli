# Test Results for Binance (Sandbox Environment)

## Summary

- Account Balance (binance, sandbox): FAIL
- Account Positions (binance, sandbox): FAIL
- Query Order Book (binance, sandbox): FAIL
- Entry Limit Buy (binance, sandbox): FAIL
- Cancel All Orders (binance, sandbox): FAIL

## Detailed Output

```
Starting tests for binance in sandbox environment...
--- Running Test: Account Balance (binance, sandbox) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango --sandbox account --balance --exchange binance
FAIL: Account Balance (binance, sandbox)
Stdout: Attempting to import: bitmango.exchange.binance.account_open_positions
sys.path: ['/home/trading/git/bitmango-bitmango', '/home/trading/git/bitmango-bitmango', '/usr/lib/python311.zip', '/usr/lib/python3.11', '/usr/lib/python3.11/lib-dynload', 'uv']
Loaded module: bitmango.exchange.binance.account_open_positions
Error: API keys for binance are not configured in api_keys.py.

Stderr: 
--- Running Test: Account Positions (binance, sandbox) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango --sandbox account --positions --exchange binance
FAIL: Account Positions (binance, sandbox)
Stdout: Attempting to import: bitmango.exchange.binance.account_open_positions
sys.path: ['/home/trading/git/bitmango-bitmango', '/home/trading/git/bitmango-bitmango', '/usr/lib/python311.zip', '/usr/lib/python3.11', '/usr/lib/python3.11/lib-dynload', 'uv']
Loaded module: bitmango.exchange.binance.account_open_positions
Error: API keys for binance are not configured in api_keys.py.

Stderr: 
--- Running Test: Query Order Book (binance, sandbox) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango --sandbox query_order_book --pair BTC-USDT --exchange binance
FAIL: Query Order Book (binance, sandbox)
Stdout: Debug: Attempting to import module: bitmango.exchange.binance.query_orderbook_binance
Debug: Successfully imported module: bitmango.exchange.binance.query_orderbook_binance
Debug: Attempting to get class: BinanceQueryOrderBook from module: bitmango.exchange.binance.query_orderbook_binance
Debug: Successfully got class: BinanceQueryOrderBook
Error: API keys for binance are not configured in api_keys.py.

Stderr: 
--- Running Test: Entry Limit Buy (binance, sandbox) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango --sandbox entry --pair BTC-USDT --direction buy --size 0.0001 --price 10000 --order-type limit --exchange binance --no-confirm
FAIL: Entry Limit Buy (binance, sandbox)
Stdout: Error: API keys for binance are not configured in api_keys.py.

Stderr: 
--- Running Test: Cancel All Orders (binance, sandbox) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango --sandbox cancel all --pair BTC-USDT --exchange binance --no-confirm
FAIL: Cancel All Orders (binance, sandbox)
Stdout: Attempting to import: bitmango.exchange.binance.account_open_positions
sys.path: ['/home/trading/git/bitmango-bitmango', '/home/trading/git/bitmango-bitmango', '/usr/lib/python311.zip', '/usr/lib/python3.11', '/usr/lib/python3.11/lib-dynload', 'uv']
Loaded module: bitmango.exchange.binance.account_open_positions
Error: API keys for binance are not configured in api_keys.py.

Stderr: 
--- Running Test: Exit Limit Sell (binance, sandbox) ---
Error: API keys for binance are not configured in api_keys.py.

```
