# Test Results for Bitfinex (Sandbox Environment)

## Summary

- Account Balance (bitfinex, sandbox): FAIL
- Account Positions (bitfinex, sandbox): FAIL
- Query Order Book (bitfinex, sandbox): FAIL
- Entry Limit Buy (bitfinex, sandbox): FAIL
- Cancel All Orders (bitfinex, sandbox): FAIL

## Detailed Output

```
Starting tests for bitfinex in sandbox environment...
--- Running Test: Account Balance (bitfinex, sandbox) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango --sandbox account --balance --exchange bitfinex
FAIL: Account Balance (bitfinex, sandbox)
Stdout: Attempting to import: bitmango.exchange.bitfinex.account_open_positions
sys.path: ['/home/trading/git/bitmango-bitmango', '/home/trading/git/bitmango-bitmango', '/usr/lib/python311.zip', '/usr/lib/python3.11', '/usr/lib/python3.11/lib-dynload', 'uv']
Loaded module: bitmango.exchange.bitfinex.account_open_positions
Error: API keys for bitfinex are not configured in api_keys.py.

Stderr: 
--- Running Test: Account Positions (bitfinex, sandbox) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango --sandbox account --positions --exchange bitfinex
FAIL: Account Positions (bitfinex, sandbox)
Stdout: Attempting to import: bitmango.exchange.bitfinex.account_open_positions
sys.path: ['/home/trading/git/bitmango-bitmango', '/home/trading/git/bitmango-bitmango', '/usr/lib/python311.zip', '/usr/lib/python3.11', '/usr/lib/python3.11/lib-dynload', 'uv']
Loaded module: bitmango.exchange.bitfinex.account_open_positions
Error: API keys for bitfinex are not configured in api_keys.py.

Stderr: 
--- Running Test: Query Order Book (bitfinex, sandbox) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango --sandbox query_order_book --pair BTC-USDT --exchange bitfinex
FAIL: Query Order Book (bitfinex, sandbox)
Stdout: Debug: Attempting to import module: bitmango.exchange.bitfinex.query_orderbook_bitfinex
Debug: Successfully imported module: bitmango.exchange.bitfinex.query_orderbook_bitfinex
Debug: Attempting to get class: BitfinexQueryOrderBook from module: bitmango.exchange.bitfinex.query_orderbook_bitfinex
Debug: Successfully got class: BitfinexQueryOrderBook
Error: API keys for bitfinex are not configured in api_keys.py.

Stderr: 
--- Running Test: Entry Limit Buy (bitfinex, sandbox) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango --sandbox entry --pair BTC-USDT --direction buy --size 0.0001 --price 10000 --order-type limit --exchange bitfinex --no-confirm
FAIL: Entry Limit Buy (bitfinex, sandbox)
Stdout: Error: API keys for bitfinex are not configured in api_keys.py.

Stderr: 
--- Running Test: Cancel All Orders (bitfinex, sandbox) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango --sandbox cancel all --pair BTC-USDT --exchange bitfinex --no-confirm
FAIL: Cancel All Orders (bitfinex, sandbox)
Stdout: Attempting to import: bitmango.exchange.bitfinex.account_open_positions
sys.path: ['/home/trading/git/bitmango-bitmango', '/home/trading/git/bitmango-bitmango', '/usr/lib/python311.zip', '/usr/lib/python3.11', '/usr/lib/python3.11/lib-dynload', 'uv']
Loaded module: bitmango.exchange.bitfinex.account_open_positions
Error: API keys for bitfinex are not configured in api_keys.py.

Stderr: 
--- Running Test: Exit Limit Sell (bitfinex, sandbox) ---
Error: API keys for bitfinex are not configured in api_keys.py.

```
