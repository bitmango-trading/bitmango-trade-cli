# Test Results for Phemex (Live Environment)

## Summary

- Account Balance (phemex, live): PASS
- Account Positions (phemex, live): PASS
- Query Order Book (phemex, live): PASS

## Detailed Output

```
Starting tests for phemex in live environment...
--- Running Test: Account Balance (phemex, live) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango account --balance --exchange phemex
PASS: Account Balance (phemex, live)
--- Running Test: Account Positions (phemex, live) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango account --positions --exchange phemex
PASS: Account Positions (phemex, live)
--- Running Test: Query Order Book (phemex, live) ---
Running command:  /home/trading/git/bitmango-bitmango/bitmango query_order_book --pair BTC-USDT --exchange phemex
PASS: Query Order Book (phemex, live)
--- Running Test: Entry Limit Buy (phemex, live) ---
SKIP: Entry Limit Buy (phemex, live) - Skipping live trading test.
--- Running Test: Cancel All Orders (phemex, live) ---
SKIP: Cancel All Orders (phemex, live) - Skipping live trading test.
--- Running Test: Exit Limit Sell (phemex, live) ---
SKIP: Exit Limit Sell (phemex, live) - Skipping live trading test.
--- Running Test: Stop Loss Order (phemex, live) ---
SKIP: Stop Loss Order (phemex, live) - Skipping live trading test.
--- Running Test: Smart Stop Phemex (phemex, live) ---
SKIP: Smart Stop Phemex (phemex, live) - Skipping live trading test.

--- Test Summary ---
test_account_balance: PASS
test_account_positions: PASS
test_query_order_book: PASS
test_entry_limit_buy: PASS
test_cancel_all_orders: PASS
test_exit_limit_sell: PASS
test_stop_loss_order: PASS
test_smart_stop_phemex: PASS

```
