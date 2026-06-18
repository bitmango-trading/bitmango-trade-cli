# Test Results for Mexc (Sandbox Environment)

## Summary

- Account Balance (mexc, sandbox): FAIL
- Account Positions (mexc, sandbox): FAIL
- Query Order Book (mexc, sandbox): FAIL
- Entry Limit Buy (mexc, sandbox): FAIL
- Cancel All Orders (mexc, sandbox): FAIL

## Detailed Output

```
Starting tests for mexc in sandbox environment...
--- Running Test: Account Balance (mexc, sandbox) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango --sandbox account --balance --exchange mexc
FAIL: Account Balance (mexc, sandbox)
Stdout: Attempting to import: bitmango.exchange.mexc.account_open_positions
sys.path: ['/home/trading/git/bitmango-bitmango', '/home/trading/git/bitmango-bitmango', '/usr/lib/python311.zip', '/usr/lib/python3.11', '/usr/lib/python3.11/lib-dynload', 'uv']
Loaded module: bitmango.exchange.mexc.account_open_positions
Error: API keys for mexc are not configured in api_keys.py.

Stderr: 
--- Running Test: Account Positions (mexc, sandbox) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango --sandbox account --positions --exchange mexc
FAIL: Account Positions (mexc, sandbox)
Stdout: Attempting to import: bitmango.exchange.mexc.account_open_positions
sys.path: ['/home/trading/git/bitmango-bitmango', '/home/trading/git/bitmango-bitmango', '/usr/lib/python311.zip', '/usr/lib/python3.11', '/usr/lib/python3.11/lib-dynload', 'uv']
Loaded module: bitmango.exchange.mexc.account_open_positions
Error: API keys for mexc are not configured in api_keys.py.

Stderr: 
--- Running Test: Query Order Book (mexc, sandbox) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango --sandbox query_order_book --pair BTC-USDT --exchange mexc
FAIL: Query Order Book (mexc, sandbox)
Stdout: Debug: Attempting to import module: bitmango.exchange.mexc.query_orderbook_mexc
Debug: Successfully imported module: bitmango.exchange.mexc.query_orderbook_mexc
Debug: Attempting to get class: MexcQueryOrderBook from module: bitmango.exchange.mexc.query_orderbook_mexc
Debug: Successfully got class: MexcQueryOrderBook
Error: API keys for mexc are not configured in api_keys.py.

Stderr: 
--- Running Test: Entry Limit Buy (mexc, sandbox) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango --sandbox entry --pair BTC-USDT --direction buy --size 0.0001 --price 10000 --order-type limit --exchange mexc --no-confirm
FAIL: Entry Limit Buy (mexc, sandbox)
Stdout: Error: API keys for mexc are not configured in api_keys.py.

Stderr: 
--- Running Test: Cancel All Orders (mexc, sandbox) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango --sandbox cancel all --pair BTC-USDT --exchange mexc --no-confirm
FAIL: Cancel All Orders (mexc, sandbox)
Stdout: Attempting to import: bitmango.exchange.mexc.account_open_positions
sys.path: ['/home/trading/git/bitmango-bitmango', '/home/trading/git/bitmango-bitmango', '/usr/lib/python311.zip', '/usr/lib/python3.11', '/usr/lib/python3.11/lib-dynload', 'uv']
Loaded module: bitmango.exchange.mexc.account_open_positions
Error: API keys for mexc are not configured in api_keys.py.

Stderr: 
--- Running Test: Exit Limit Sell (mexc, sandbox) ---
Error: API keys for mexc are not configured in api_keys.py.

```
