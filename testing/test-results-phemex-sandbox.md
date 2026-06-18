# Test Results for Phemex (Sandbox Environment)

## Summary

- Account Balance (phemex, sandbox): PASS
- Account Positions (phemex, sandbox): PASS
- Query Order Book (phemex, sandbox): PASS
- Entry Limit Buy (phemex, sandbox): FAIL
- Cancel All Orders (phemex, sandbox): PASS
- Exit Limit Sell (phemex, sandbox): PASS
- Smart Stop Phemex (phemex, sandbox): PASS

## Detailed Output

```
Starting tests for phemex in sandbox environment...
--- Running Test: Account Balance (phemex, sandbox) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango --sandbox account --balance --exchange phemex
PASS: Account Balance (phemex, sandbox)
--- Running Test: Account Positions (phemex, sandbox) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango --sandbox account --positions --exchange phemex
PASS: Account Positions (phemex, sandbox)
--- Running Test: Query Order Book (phemex, sandbox) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango --sandbox query_order_book --pair BTC-USDT --exchange phemex
PASS: Query Order Book (phemex, sandbox)
--- Running Test: Entry Limit Buy (phemex, sandbox) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango --sandbox entry --pair BTC-USDT --direction buy --size 0.000001 --price 10000 --order-type limit --exchange phemex --no-confirm
FAIL: Entry Limit Buy (phemex, sandbox)
Stdout: Using Phemex Testnet
❌ Order failed: phemex {"msg":"Min order Value check failed, symbol sBTCUSDT, min order value 1","code":39100}

Stderr: 
--- Running Test: Cancel All Orders (phemex, sandbox) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango --sandbox cancel all --pair BTC-USDT --exchange phemex --no-confirm
PASS: Cancel All Orders (phemex, sandbox)
--- Running Test: Exit Limit Sell (phemex, sandbox) ---
Using Phemex Testnet
Debug: Order book for BTC/USDT (timestamp: 1757214901361, datetime: 2025-09-07T03:15:01.361Z)
Current price: 110525.16, Setting limit price for sell: 111630.41 (adjusted for tick size 0.01)
Running command:  /home/trading/git/bitmango-bitmango/bitmango --sandbox exit --pair BTC-USDT --size 0.0001 --price 111630.41 --order-type limit --exchange phemex --no-confirm
PASS: Exit Limit Sell (phemex, sandbox)
--- Running Test: Stop Loss Order (phemex, sandbox) ---
SKIP: Stop Loss Order (phemex, sandbox) - Skipping for Phemex due to 'TE_SO_NUM_EXCEEDS' error on testnet.
--- Running Test: Smart Stop Phemex (phemex, sandbox) ---
Testing close_position...
DEBUG: Entering close_position for BTC/USDT
DEBUG: Current position size: 0.001, Absolute size: 0.001, Side: sell
INFO: Attempting to close 0.001 contracts of BTC/USDT with a sell order.
DEBUG: Current market price for BTC/USDT: 110000
DEBUG: Calling create_order with symbol=BTC/USDT, type='market', side=sell, amount=0.001, price=110000, params={'reduceOnly': True}
MockCcxtExchange: create_order called with: BTC/USDT, market, sell, 0.001, 110000, {'reduceOnly': True}
SUCCESS: Close order placed: {'id': 'mock_order_id', 'status': 'closed'}
close_position test passed.
Testing open_position...
DEBUG: Entering open_position for BTC/USDT with USD amount: 100, side: buy
DEBUG: Current market price for BTC/USDT: 110000
DEBUG: Calculating contract size for USD amount: 100 at price: 110000
DEBUG: Calculated quantity: 0.0009090909090909091
DEBUG: Converted USD amount 100 to base asset quantity: 0.0009090909090909091
DEBUG: Calling create_order with symbol=BTC/USDT, type='market', side=buy, amount=0.0009090909090909091, price=110000, params={}
MockCcxtExchange: create_order called with: BTC/USDT, market, buy, 0.0009090909090909091, 110000, {}
SUCCESS: Open order placed: {'id': 'mock_order_id', 'status': 'closed'}
open_position test passed.
PASS: Smart Stop Phemex (phemex, sandbox)

--- Test Summary ---
test_account_balance: PASS
test_account_positions: PASS
test_query_order_book: PASS
test_entry_limit_buy: FAIL
test_cancel_all_orders: PASS
test_exit_limit_sell: PASS
test_stop_loss_order: PASS
test_smart_stop_phemex: PASS

```
